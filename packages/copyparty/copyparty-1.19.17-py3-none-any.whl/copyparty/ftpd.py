# coding: utf-8
from __future__ import print_function, unicode_literals

import argparse
import errno
import logging
import os
import stat
import sys
import time

from pyftpdlib.authorizers import AuthenticationFailed, DummyAuthorizer
from pyftpdlib.filesystems import AbstractedFS, FilesystemError
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.ioloop import IOLoop
from pyftpdlib.servers import FTPServer

from .__init__ import PY2, TYPE_CHECKING
from .authsrv import VFS
from .bos import bos
from .util import (
    FN_EMB,
    VF_CAREFUL,
    Daemon,
    ODict,
    Pebkac,
    exclude_dotfiles,
    fsenc,
    ipnorm,
    pybin,
    relchk,
    runhook,
    sanitize_fn,
    set_fperms,
    vjoin,
    wunlink,
)

if TYPE_CHECKING:
    from .svchub import SvcHub

if PY2:
    range = xrange  # type: ignore


class FSE(FilesystemError):
    def __init__(self, msg , severity  = 0)  :
        super(FilesystemError, self).__init__(msg)
        self.severity = severity


class FtpAuth(DummyAuthorizer):
    def __init__(self, hub )  :
        super(FtpAuth, self).__init__()
        self.hub = hub

    def validate_authentication(
        self, username , password , handler 
    )  :
        handler.username = "{}:{}".format(username, password)
        handler.uname = "*"

        ip = handler.addr[0]
        if ip.startswith("::ffff:"):
            ip = ip[7:]

        ipn = ipnorm(ip)
        bans = self.hub.bans
        if ipn in bans:
            rt = bans[ipn] - time.time()
            if rt < 0:
                logging.info("client unbanned")
                del bans[ipn]
            else:
                raise AuthenticationFailed("banned")

        args = self.hub.args
        asrv = self.hub.asrv
        uname = "*"
        if username != "anonymous":
            uname = ""
            if args.usernames:
                alts = ["%s:%s" % (username, password)]
            else:
                alts = password, username

            for zs in alts:
                zs = asrv.iacct.get(asrv.ah.hash(zs), "")
                if zs:
                    uname = zs
                    break

        if args.ipu and uname == "*":
            uname = args.ipu_iu[args.ipu_nm.map(ip)]
        if args.ipr and uname in args.ipr_u:
            if not args.ipr_u[uname].map(ip):
                logging.warning("username [%s] rejected by --ipr", uname)
                uname = "*"

        if not uname or not (asrv.vfs.aread.get(uname) or asrv.vfs.awrite.get(uname)):
            g = self.hub.gpwd
            if g.lim:
                bonk, ip = g.bonk(ip, handler.username)
                if bonk:
                    logging.warning("client banned: invalid passwords")
                    bans[ip] = bonk
                    try:
                        # only possible if multiprocessing disabled
                        self.hub.broker.httpsrv.bans[ip] = bonk  # type: ignore
                        self.hub.broker.httpsrv.nban += 1  # type: ignore
                    except:
                        pass

            raise AuthenticationFailed("Authentication failed.")

        handler.uname = handler.username = uname

    def get_home_dir(self, username )  :
        return "/"

    def has_user(self, username )  :
        asrv = self.hub.asrv
        return username in asrv.acct or username in asrv.iacct

    def has_perm(self, username , perm , path  = None)  :
        return True  # handled at filesystem layer

    def get_perms(self, username )  :
        return "elradfmwMT"

    def get_msg_login(self, username )  :
        return "sup {}".format(username)

    def get_msg_quit(self, username )  :
        return "cya"


class FtpFs(AbstractedFS):
    def __init__(
        self, root , cmd_channel 
    )  :  # pylint: disable=super-init-not-called
        self.h = cmd_channel  # type: FTPHandler
        self.cmd_channel = cmd_channel  # type: FTPHandler
        self.hub  = cmd_channel.hub
        self.args = cmd_channel.args
        self.uname = cmd_channel.uname

        self.cwd = "/"  # pyftpdlib convention of leading slash
        self.root = "/var/lib/empty"

        self.listdirinfo = self.listdir
        self.chdir(".")

    def log(self, msg , c   = 0)  :
        self.hub.log("ftpd", msg, c)

    def v2a(
        self,
        vpath ,
        r  = False,
        w  = False,
        m  = False,
        d  = False,
    )    :
        try:
            vpath = vpath.replace("\\", "/").strip("/")
            rd, fn = os.path.split(vpath)
            if relchk(rd):
                logging.warning("malicious vpath: %s", vpath)
                t = "Unsupported characters in [{}]"
                raise FSE(t.format(vpath), 1)

            fn = sanitize_fn(fn or "", "")
            vpath = vjoin(rd, fn)
            vfs, rem = self.hub.asrv.vfs.get(vpath, self.uname, r, w, m, d)
            if (
                w
                and fn.lower() in FN_EMB
                and self.h.uname not in vfs.axs.uread
                and "wo_up_readme" not in vfs.flags
            ):
                fn = "_wo_" + fn
                vpath = vjoin(rd, fn)
                vfs, rem = self.hub.asrv.vfs.get(vpath, self.uname, r, w, m, d)

            if not vfs.realpath:
                t = "No filesystem mounted at [{}]"
                raise FSE(t.format(vpath))

            if "xdev" in vfs.flags or "xvol" in vfs.flags:
                ap = vfs.canonical(rem)
                avfs = vfs.chk_ap(ap)
                t = "Permission denied in [{}]"
                if not avfs:
                    raise FSE(t.format(vpath), 1)

                cr, cw, cm, cd, _, _, _, _ = avfs.can_access("", self.h.uname)
                if r and not cr or w and not cw or m and not cm or d and not cd:
                    raise FSE(t.format(vpath), 1)

            if "bcasechk" in vfs.flags and not vfs.casechk(rem, True):
                raise FSE("No such file or directory", 1)

            return os.path.join(vfs.realpath, rem), vfs, rem
        except Pebkac as ex:
            raise FSE(str(ex))

    def rv2a(
        self,
        vpath ,
        r  = False,
        w  = False,
        m  = False,
        d  = False,
    )    :
        return self.v2a(join(self.cwd, vpath), r, w, m, d)

    def ftp2fs(self, ftppath )  :
        # return self.v2a(ftppath)
        return ftppath  # self.cwd must be vpath

    def fs2ftp(self, fspath )  :
        # raise NotImplementedError()
        return fspath

    def validpath(self, path )  :
        if "/.hist/" in path:
            if "/up2k." in path or path.endswith("/dir.txt"):
                raise FSE("Access to this file is forbidden", 1)

        return True

    def open(self, filename , mode )  :
        r = "r" in mode
        w = "w" in mode or "a" in mode or "+" in mode

        ap, vfs, _ = self.rv2a(filename, r, w)
        self.validpath(ap)
        if w:
            try:
                st = bos.stat(ap)
                td = time.time() - st.st_mtime
                need_unlink = True
            except:
                need_unlink = False
                td = 0

        if w and need_unlink:
            if td >= -1 and td <= self.args.ftp_wt:
                # within permitted timeframe; allow overwrite or resume
                do_it = True
            elif self.args.no_del or self.args.ftp_no_ow:
                # file too old, or overwrite not allowed; reject
                do_it = False
            else:
                # allow overwrite if user has delete permission
                # (avoids win2000 freaking out and deleting the server copy without uploading its own)
                try:
                    self.rv2a(filename, False, True, False, True)
                    do_it = True
                except:
                    do_it = False

            if not do_it:
                raise FSE("File already exists")

            # Don't unlink file for append mode
            elif "a" not in mode:
                wunlink(self.log, ap, VF_CAREFUL)

        ret = open(fsenc(ap), mode, self.args.iobuf)
        if w and "fperms" in vfs.flags:
            set_fperms(ret, vfs.flags)

        return ret

    def chdir(self, path )  :
        nwd = join(self.cwd, path)
        vfs, rem = self.hub.asrv.vfs.get(nwd, self.uname, False, False)
        if not vfs.realpath:
            self.cwd = nwd
            return

        ap = vfs.canonical(rem)
        try:
            st = bos.stat(ap)
            if not stat.S_ISDIR(st.st_mode):
                raise Exception()
        except:
            # returning 550 is library-default and suitable
            raise FSE("No such file or directory")

        avfs = vfs.chk_ap(ap, st)
        if not avfs:
            raise FSE("Permission denied", 1)

        self.cwd = nwd

    def mkdir(self, path )  :
        ap, vfs, _ = self.rv2a(path, w=True)
        bos.makedirs(ap, vf=vfs.flags)  # filezilla expects this

    def listdir(self, path )  :
        vpath = join(self.cwd, path)
        try:
            ap, vfs, rem = self.v2a(vpath, True, False)
            if not bos.path.isdir(ap):
                raise FSE("No such file or directory", 1)

            fsroot, vfs_ls1, vfs_virt = vfs.ls(
                rem,
                self.uname,
                not self.args.no_scandir,
                [[True, False], [False, True]],
                throw=True,
            )
            vfs_ls = [x[0] for x in vfs_ls1]
            vfs_ls.extend(vfs_virt.keys())

            if self.uname not in vfs.axs.udot:
                vfs_ls = exclude_dotfiles(vfs_ls)

            vfs_ls.sort()
            return vfs_ls
        except Exception as ex:
            # panic on malicious names
            if getattr(ex, "severity", 0):
                raise

            if vpath.strip("/"):
                # display write-only folders as empty
                return []

            # return list of accessible volumes
            ret = []
            for vn in self.hub.asrv.vfs.all_vols.values():
                if "/" in vn.vpath or not vn.vpath:
                    continue  # only include toplevel-mounted vols

                try:
                    self.hub.asrv.vfs.get(vn.vpath, self.uname, True, False)
                    ret.append(vn.vpath)
                except:
                    pass

            ret.sort()
            return ret

    def rmdir(self, path )  :
        ap = self.rv2a(path, d=True)[0]
        try:
            bos.rmdir(ap)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def remove(self, path )  :
        if self.args.no_del:
            raise FSE("The delete feature is disabled in server config")

        vp = join(self.cwd, path).lstrip("/")
        try:
            self.hub.up2k.handle_rm(self.uname, self.h.cli_ip, [vp], [], False, False)
        except Exception as ex:
            raise FSE(str(ex))

    def rename(self, src , dst )  :
        if self.args.no_mv:
            raise FSE("The rename/move feature is disabled in server config")

        svp = join(self.cwd, src).lstrip("/")
        dvp = join(self.cwd, dst).lstrip("/")
        try:
            self.hub.up2k.handle_mv("", self.uname, self.h.cli_ip, svp, dvp)
        except Exception as ex:
            raise FSE(str(ex))

    def chmod(self, path , mode )  :
        pass

    def stat(self, path )  :
        try:
            ap = self.rv2a(path, r=True)[0]
            return bos.stat(ap)
        except FSE as ex:
            if ex.severity:
                raise

            ap = self.rv2a(path)[0]
            st = bos.stat(ap)
            if not stat.S_ISDIR(st.st_mode):
                raise

            return st

    def utime(self, path , timeval )  :
        ap = self.rv2a(path, w=True)[0]
        bos.utime_c(logging.warning, ap, int(timeval), False)

    def lstat(self, path )  :
        ap = self.rv2a(path)[0]
        return bos.stat(ap)

    def isfile(self, path )  :
        try:
            st = self.stat(path)
            return stat.S_ISREG(st.st_mode)
        except Exception as ex:
            if getattr(ex, "severity", 0):
                raise

            return False  # expected for mojibake in ftp_SIZE()

    def islink(self, path )  :
        ap = self.rv2a(path)[0]
        return bos.path.islink(ap)

    def isdir(self, path )  :
        try:
            st = self.stat(path)
            return stat.S_ISDIR(st.st_mode)
        except Exception as ex:
            if getattr(ex, "severity", 0):
                raise

            return True

    def getsize(self, path )  :
        ap = self.rv2a(path)[0]
        return bos.path.getsize(ap)

    def getmtime(self, path )  :
        ap = self.rv2a(path)[0]
        return bos.path.getmtime(ap)

    def realpath(self, path )  :
        return path

    def lexists(self, path )  :
        ap = self.rv2a(path)[0]
        return bos.path.lexists(ap)

    def get_user_by_uid(self, uid )  :
        return "root"

    def get_group_by_uid(self, gid )  :
        return "root"


class FtpHandler(FTPHandler):
    abstracted_fs = FtpFs
    #hub: "SvcHub"
    #args: argparse.Namespace
    #uname: str

    def __init__(self, conn , server , ioloop  = None)  :
        self.hub  = FtpHandler.hub
        self.args  = FtpHandler.args
        self.uname = "*"

        if PY2:
            FTPHandler.__init__(self, conn, server, ioloop)
        else:
            super(FtpHandler, self).__init__(conn, server, ioloop)

        cip = self.remote_ip
        if cip.startswith("::ffff:"):
            cip = cip[7:]

        if self.args.ftp_ipa_nm and not self.args.ftp_ipa_nm.map(cip):
            logging.warning("client rejected (--ftp-ipa): %s", cip)
            self.connected = False
            conn.close()
            return

        self.cli_ip = cip

        # abspath->vpath mapping to resolve log_transfer paths
        self.vfs_map   = {}

        # reduce non-debug logging
        self.log_cmds_list = [x for x in self.log_cmds_list if x not in ("CWD", "XCWD")]

    def ftp_STOR(self, file , mode  = "w")  :
        # Optional[str]
        vp = join(self.fs.cwd, file).lstrip("/")
        try:
            ap, vfs, rem = self.fs.v2a(vp, w=True)
        except Exception as ex:
            self.respond("550 %s" % (ex,), logging.info)
            return
        self.vfs_map[ap] = vp
        xbu = vfs.flags.get("xbu")
        if xbu:
            hr = runhook(
                None,
                None,
                self.hub.up2k,
                "xbu.ftpd",
                xbu,
                ap,
                vp,
                "",
                self.uname,
                self.hub.asrv.vfs.get_perms(vp, self.uname),
                0,
                0,
                self.cli_ip,
                time.time(),
                None,
            )
            t = hr.get("rejectmsg") or ""
            if t or not hr:
                if not t:
                    t = "Upload blocked by xbu server config: %r" % (vp,)
                self.respond("550 %s" % (t,), logging.info)
                return

        # print("ftp_STOR: {} {} => {}".format(vp, mode, ap))
        ret = FTPHandler.ftp_STOR(self, file, mode)
        # print("ftp_STOR: {} {} OK".format(vp, mode))
        return ret

    def log_transfer(
        self,
        cmd ,
        filename ,
        receive ,
        completed ,
        elapsed ,
        bytes ,
    )  :
        # None
        ap = filename.decode("utf-8", "replace")
        vp = self.vfs_map.pop(ap, None)
        # print("xfer_end: {} => {}".format(ap, vp))
        if vp:
            vp, fn = os.path.split(vp)
            vfs, rem = self.hub.asrv.vfs.get(vp, self.uname, False, True)
            vfs, rem = vfs.get_dbv(rem)
            self.hub.up2k.hash_file(
                vfs.realpath,
                vfs.vpath,
                vfs.flags,
                rem,
                fn,
                self.cli_ip,
                time.time(),
                self.uname,
            )

        return FTPHandler.log_transfer(
            self, cmd, filename, receive, completed, elapsed, bytes
        )


try:
    from pyftpdlib.handlers import TLS_FTPHandler

    class SftpHandler(FtpHandler, TLS_FTPHandler):
        pass

except:
    pass


class Ftpd(object):
    def __init__(self, hub )  :
        self.hub = hub
        self.args = hub.args

        hs = []
        if self.args.ftp:
            hs.append([FtpHandler, self.args.ftp])
        if self.args.ftps:
            try:
                h1 = SftpHandler
            except:
                t = "\nftps requires pyopenssl;\nplease run the following:\n\n  {} -m pip install --user pyopenssl\n"
                print(t.format(pybin))
                sys.exit(1)

            h1.certfile = self.args.cert
            h1.tls_control_required = True
            h1.tls_data_required = True

            hs.append([h1, self.args.ftps])

        for h_lp in hs:
            h2, lp = h_lp
            FtpHandler.hub = h2.hub = hub
            FtpHandler.args = h2.args = hub.args
            FtpHandler.authorizer = h2.authorizer = FtpAuth(hub)

            if self.args.ftp_pr:
                p1, p2 = [int(x) for x in self.args.ftp_pr.split("-")]
                if self.args.ftp and self.args.ftps:
                    # divide port range in half
                    d = int((p2 - p1) / 2)
                    if lp == self.args.ftp:
                        p2 = p1 + d
                    else:
                        p1 += d + 1

                h2.passive_ports = list(range(p1, p2 + 1))

            if self.args.ftp_nat:
                h2.masquerade_address = self.args.ftp_nat

        lgr = logging.getLogger("pyftpdlib")
        lgr.setLevel(logging.DEBUG if self.args.ftpv else logging.INFO)

        ips = self.args.i
        if "::" in ips:
            ips.append("0.0.0.0")

        ips = [x for x in ips if not x.startswith(("unix:", "fd:"))]

        if self.args.ftp4:
            ips = [x for x in ips if ":" not in x]

        if not ips:
            lgr.fatal("cannot start ftp-server; no compatible IPs in -i")
            return

        ips = list(ODict.fromkeys(ips))  # dedup

        ioloop = IOLoop()
        for ip in ips:
            for h, lp in hs:
                try:
                    FTPServer((ip, int(lp)), h, ioloop)
                except:
                    if ip != "0.0.0.0" or "::" not in ips:
                        raise

        Daemon(ioloop.loop, "ftp")


def join(p1 , p2 )  :
    w = os.path.join(p1, p2.replace("\\", "/"))
    return os.path.normpath(w).replace("\\", "/")
