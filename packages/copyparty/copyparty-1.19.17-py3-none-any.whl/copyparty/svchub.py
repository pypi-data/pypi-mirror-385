# coding: utf-8
from __future__ import print_function, unicode_literals

import argparse
import atexit
import errno
import logging
import os
import re
import shlex
import signal
import socket
import string
import sys
import threading
import time
from datetime import datetime

# from inspect import currentframe
# print(currentframe().f_lineno)


from .__init__ import ANYWIN, EXE, MACOS, PY2, TYPE_CHECKING, E, EnvParams, unicode
from .authsrv import BAD_CFG, AuthSrv, derive_args, n_du_who, n_ver_who
from .bos import bos
from .cert import ensure_cert
from .fsutil import ramdisk_chk
from .mtag import HAVE_FFMPEG, HAVE_FFPROBE, HAVE_MUTAGEN
from .pwhash import HAVE_ARGON2
from .tcpsrv import TcpSrv
from .th_srv import (
    HAVE_AVIF,
    HAVE_FFMPEG,
    HAVE_FFPROBE,
    HAVE_HEIF,
    HAVE_PIL,
    HAVE_RAW,
    HAVE_VIPS,
    HAVE_WEBP,
    ThumbSrv,
)
from .up2k import Up2k
from .util import (
    DEF_EXP,
    DEF_MTE,
    DEF_MTH,
    FFMPEG_URL,
    HAVE_PSUTIL,
    HAVE_SQLITE3,
    HAVE_ZMQ,
    RE_ANSI,
    URL_BUG,
    UTC,
    VERSIONS,
    Daemon,
    Garda,
    HLog,
    HMaccas,
    ODict,
    alltrace,
    build_netmap,
    expat_ver,
    gzip,
    html_escape,
    load_ipr,
    load_ipu,
    lock_file,
    min_ex,
    mp,
    odfusion,
    pybin,
    start_log_thrs,
    start_stackmon,
    termsize,
    ub64enc,
)

if HAVE_SQLITE3:
    import sqlite3

if TYPE_CHECKING:
    try:
        from .mdns import MDNS
        from .ssdp import SSDPd
    except:
        pass

if PY2:
    range = xrange  # type: ignore


VER_IDP_DB = 1
VER_SESSION_DB = 1
VER_SHARES_DB = 2


class SvcHub(object):
    """
    Hosts all services which cannot be parallelized due to reliance on monolithic resources.
    Creates a Broker which does most of the heavy stuff; hosted services can use this to perform work:
        hub.broker.<say|ask>(destination, args_list).

    Either BrokerThr (plain threads) or BrokerMP (multiprocessing) is used depending on configuration.
    Nothing is returned synchronously; if you want any value returned from the call,
    put() can return a queue (if want_reply=True) which has a blocking get() with the response.
    """

    def __init__(
        self,
        args ,
        dargs ,
        argv ,
        printed ,
    )  :
        self.args = args
        self.dargs = dargs
        self.argv = argv
        self.E  = args.E
        self.no_ansi = args.no_ansi
        self.tz = UTC if args.log_utc else None
        self.logf  = None
        self.logf_base_fn = ""
        self.is_dut = False  # running in unittest; always False
        self.stop_req = False
        self.stopping = False
        self.stopped = False
        self.reload_req = False
        self.reload_mutex = threading.Lock()
        self.stop_cond = threading.Condition()
        self.nsigs = 3
        self.retcode = 0
        self.httpsrv_up = 0
        self.qr_tsz = None

        self.log_mutex = threading.Lock()
        self.cday = 0
        self.cmon = 0
        self.tstack = 0.0

        self.iphash = HMaccas(os.path.join(self.E.cfg, "iphash"), 8)

        if args.sss or args.s >= 3:
            args.ss = True
            args.no_dav = True
            args.no_logues = True
            args.no_readme = True
            args.lo = args.lo or "cpp-%Y-%m%d-%H%M%S.txt.xz"
            args.ls = args.ls or "**,*,ln,p,r"

        if args.ss or args.s >= 2:
            args.s = True
            args.unpost = 0
            args.no_del = True
            args.no_mv = True
            args.reflink = True
            args.dav_auth = True
            args.vague_403 = True
            args.nih = True

        if args.s:
            args.dotpart = True
            args.no_thumb = True
            args.no_mtag_ff = True
            args.no_robots = True
            args.force_js = True

        if not self._process_config():
            raise Exception(BAD_CFG)

        # for non-http clients (ftp, tftp)
        self.bans   = {}
        self.gpwd = Garda(self.args.ban_pw)
        self.gpwc = Garda(self.args.ban_pwc)
        self.g404 = Garda(self.args.ban_404)
        self.g403 = Garda(self.args.ban_403)
        self.g422 = Garda(self.args.ban_422, False)
        self.gmal = Garda(self.args.ban_422)
        self.gurl = Garda(self.args.ban_url)

        self.log_div = 10 ** (6 - args.log_tdec)
        self.log_efmt = "%02d:%02d:%02d.%0{}d".format(args.log_tdec)
        self.log_dfmt = "%04d-%04d-%06d.%0{}d".format(args.log_tdec)
        self.log = self._log_disabled if args.q else self._log_enabled
        if args.lo:
            self._setup_logfile(printed)

        lg = logging.getLogger()
        lh = HLog(self.log)
        lg.handlers = [lh]
        lg.setLevel(logging.DEBUG)

        self._check_env()

        if args.stackmon:
            start_stackmon(args.stackmon, 0)

        if args.log_thrs:
            start_log_thrs(self.log, args.log_thrs, 0)

        if not args.use_fpool and args.j != 1:
            args.no_fpool = True
            t = "multithreading enabled with -j {}, so disabling fpool -- this can reduce upload performance on some filesystems, and make some antivirus-softwares "
            c = 0
            if ANYWIN:
                t += "(especially Microsoft Defender) stress your CPU and HDD severely during big uploads"
                c = 3
            else:
                t += "consume more resources (CPU/HDD) than normal"
            self.log("root", t.format(args.j), c)

        if not args.no_fpool and args.j != 1:
            t = "WARNING: ignoring --use-fpool because multithreading (-j{}) is enabled"
            self.log("root", t.format(args.j), c=3)
            args.no_fpool = True

        for name, arg in (
            ("iobuf", "iobuf"),
            ("s-rd-sz", "s_rd_sz"),
            ("s-wr-sz", "s_wr_sz"),
        ):
            zi = getattr(args, arg)
            if zi < 32768:
                t = "WARNING: expect very poor performance because you specified a very low value (%d) for --%s"
                self.log("root", t % (zi, name), 3)
                zi = 2
            zi2 = 2 ** (zi - 1).bit_length()
            if zi != zi2:
                zi3 = 2 ** ((zi - 1).bit_length() - 1)
                t = "WARNING: expect poor performance because --%s is not a power-of-two; consider using %d or %d instead of %d"
                self.log("root", t % (name, zi2, zi3, zi), 3)

        if args.s_rd_sz > args.iobuf:
            t = "WARNING: --s-rd-sz (%d) is larger than --iobuf (%d); this may lead to reduced performance"
            self.log("root", t % (args.s_rd_sz, args.iobuf), 3)

        zs = ""
        if args.th_ram_max < 0.22:
            zs = "generate thumbnails"
        elif args.th_ram_max < 1:
            zs = "generate audio waveforms or spectrograms"
        if zs:
            t = "WARNING: --th-ram-max is very small (%.2f GiB); will not be able to %s"
            self.log("root", t % (args.th_ram_max, zs), 3)

        if args.chpw and args.have_idp_hdrs and "pw" not in args.auth_ord.split(","):
            t = "ERROR: user-changeable passwords is not compatible with your current configuration. Choose one of these options to fix it:\n option1: disable --chpw\n option2: remove all use of IdP features; --idp-*\n option3: change --auth-ord to something like pw,idp,ipu"
            self.log("root", t, 1)
            raise Exception(t)

        noch = set()
        for zs in args.chpw_no or []:
            zsl = [x.strip() for x in zs.split(",")]
            noch.update([x for x in zsl if x])
        args.chpw_no = noch

        if args.ipu:
            iu, nm = load_ipu(self.log, args.ipu, True)
            setattr(args, "ipu_iu", iu)
            setattr(args, "ipu_nm", nm)

        if args.ipr:
            ipr = load_ipr(self.log, args.ipr, True)
            setattr(args, "ipr_u", ipr)

        for zs in "ah_salt fk_salt dk_salt".split():
            if getattr(args, "show_%s" % (zs,)):
                self.log("root", "effective %s is %s" % (zs, getattr(args, zs)))

        if args.ah_cli or args.ah_gen:
            args.idp_store = 0
            args.no_ses = True
            args.shr = ""

        if args.idp_store and args.have_idp_hdrs:
            self.setup_db("idp")

        if not self.args.no_ses:
            self.setup_db("ses")

        args.shr1 = ""
        if args.shr:
            self.setup_share_db()

        bri = "zy"[args.theme % 2 :][:1]
        ch = "abcdefghijklmnopqrstuvwx"[int(args.theme / 2)]
        args.theme = "{0}{1} {0} {1}".format(ch, bri)

        if args.no_stack:
            args.stack_who = "no"

        if args.nid:
            args.du_who = "no"
        args.du_iwho = n_du_who(args.du_who)

        if args.ver and args.ver_who == "no":
            args.ver_who = "all"
        args.ver_iwho = n_ver_who(args.ver_who)

        if args.nih:
            args.vname = ""
            args.doctitle = args.doctitle.replace(" @ --name", "")
        else:
            args.vname = args.name
        args.doctitle = args.doctitle.replace("--name", args.vname)
        args.bname = args.bname.replace("--name", args.vname) or args.vname

        if args.log_fk:
            args.log_fk = re.compile(args.log_fk)

        # initiate all services to manage
        self.asrv = AuthSrv(self.args, self.log, dargs=self.dargs)
        ramdisk_chk(self.asrv)

        if args.cgen:
            self.asrv.cgen()

        if args.exit == "cfg":
            sys.exit(0)

        if args.ls:
            self.asrv.dbg_ls()

        if not ANYWIN:
            self._setlimits()

        self.log("root", "max clients: {}".format(self.args.nc))

        self.tcpsrv = TcpSrv(self)

        if not self.tcpsrv.srv and self.args.ign_ebind_all:
            self.args.no_fastboot = True

        self.up2k = Up2k(self)

        self._feature_test()

        decs = {k.strip(): 1 for k in self.args.th_dec.split(",")}
        if not HAVE_VIPS:
            decs.pop("vips", None)
        if not HAVE_PIL:
            decs.pop("pil", None)
        if not HAVE_RAW:
            decs.pop("raw", None)
        if not HAVE_FFMPEG or not HAVE_FFPROBE:
            decs.pop("ff", None)

        # compressed formats; "s3z=s3m.zip, s3gz=s3m.gz, ..."
        zlss = [x.strip().lower().split("=", 1) for x in args.au_unpk.split(",")]
        args.au_unpk = {x[0]: x[1] for x in zlss}

        self.args.th_dec = list(decs.keys())
        self.thumbsrv = None
        want_ff = False
        if not args.no_thumb:
            t = ", ".join(self.args.th_dec) or "(None available)"
            self.log("thumb", "decoder preference: {}".format(t))

            if "pil" in self.args.th_dec and not HAVE_WEBP:
                msg = "disabling webp thumbnails because either libwebp is not available or your Pillow is too old"
                self.log("thumb", msg, c=3)

            if self.args.th_dec:
                self.thumbsrv = ThumbSrv(self)
            else:
                want_ff = True
                msg = "need either Pillow, pyvips, or FFmpeg to create thumbnails; for example:\n{0}{1} -m pip install --user Pillow\n{0}{1} -m pip install --user pyvips\n{0}apt install ffmpeg"
                msg = msg.format(" " * 37, os.path.basename(pybin))
                if EXE:
                    msg = "copyparty.exe cannot use Pillow or pyvips; need ffprobe.exe and ffmpeg.exe to create thumbnails"

                self.log("thumb", msg, c=3)

        if not args.no_acode and args.no_thumb:
            msg = "setting --no-acode because --no-thumb (sorry)"
            self.log("thumb", msg, c=6)
            args.no_acode = True

        if not args.no_acode and (not HAVE_FFMPEG or not HAVE_FFPROBE):
            msg = "setting --no-acode because either FFmpeg or FFprobe is not available"
            self.log("thumb", msg, c=6)
            args.no_acode = True
            want_ff = True

        if want_ff and ANYWIN:
            self.log("thumb", "download FFmpeg to fix it:\033[0m " + FFMPEG_URL, 3)

        if not args.no_acode:
            if not re.match("^(0|[qv][0-9]|[0-9]{2,3}k)$", args.q_mp3.lower()):
                t = "invalid mp3 transcoding quality [%s] specified; only supports [0] to disable, a CBR value such as [192k], or a CQ/CRF value such as [v2]"
                raise Exception(t % (args.q_mp3,))
        else:
            zss = set(args.th_r_ffa.split(",") + args.th_r_ffv.split(","))
            args.au_unpk = {
                k: v for k, v in args.au_unpk.items() if v.split(".")[0] not in zss
            }

        args.th_poke = min(args.th_poke, args.th_maxage, args.ac_maxage)

        zms = ""
        if not args.https_only:
            zms += "d"
        if not args.http_only:
            zms += "D"

        if args.ftp or args.ftps:
            from .ftpd import Ftpd

            self.ftpd  = None
            zms += "f" if args.ftp else "F"

        if args.tftp:
            from .tftpd import Tftpd

            self.tftpd  = None

        if args.ftp or args.ftps or args.tftp:
            Daemon(self.start_ftpd, "start_tftpd")

        if args.smb:
            # impacket.dcerpc is noisy about listen timeouts
            sto = socket.getdefaulttimeout()
            socket.setdefaulttimeout(None)

            from .smbd import SMB

            self.smbd = SMB(self)
            socket.setdefaulttimeout(sto)
            self.smbd.start()
            zms += "s"

        if not args.zms:
            args.zms = zms

        self.zc_ngen = 0
        self.mdns  = None
        self.ssdp  = None

        # decide which worker impl to use
        if self.check_mp_enable():
            from .broker_mp import BrokerMp as Broker
        else:
            from .broker_thr import BrokerThr as Broker  # type: ignore

        self.broker = Broker(self)

        # create netmaps early to avoid firewall gaps,
        # but the mutex blocks multiprocessing startup
        for zs in "ipu_nm ftp_ipa_nm tftp_ipa_nm".split():
            try:
                getattr(args, zs).mutex = threading.Lock()
            except:
                pass
        if args.ipr:
            for nm in args.ipr_u.values():
                nm.mutex = threading.Lock()

    def _db_onfail_ses(self)  :
        self.args.no_ses = True

    def _db_onfail_idp(self)  :
        self.args.idp_store = 0

    def setup_db(self, which )  :
        """
        the "non-mission-critical" databases; if something looks broken then just nuke it
        """
        if which == "ses":
            native_ver = VER_SESSION_DB
            db_path = self.args.ses_db
            desc = "sessions-db"
            pathopt = "ses-db"
            sanchk_q = "select count(*) from us"
            createfun = self._create_session_db
            failfun = self._db_onfail_ses
        elif which == "idp":
            native_ver = VER_IDP_DB
            db_path = self.args.idp_db
            desc = "idp-db"
            pathopt = "idp-db"
            sanchk_q = "select count(*) from us"
            createfun = self._create_idp_db
            failfun = self._db_onfail_idp
        else:
            raise Exception("unknown cachetype")

        if not db_path.endswith(".db"):
            zs = "config option --%s (the %s) was configured to [%s] which is invalid; must be a filepath ending with .db"
            self.log("root", zs % (pathopt, desc, db_path), 1)
            raise Exception(BAD_CFG)

        if not HAVE_SQLITE3:
            failfun()
            if which == "ses":
                zs = "disabling sessions, will use plaintext passwords in cookies"
            elif which == "idp":
                zs = "disabling idp-db, will be unable to remember IdP-volumes after a restart"
            self.log("root", "WARNING: sqlite3 not available; %s" % (zs,), 3)
            return


        db_lock = db_path + ".lock"
        try:
            create = not os.path.getsize(db_path)
        except:
            create = True
        zs = "creating new" if create else "opening"
        self.log("root", "%s %s %s" % (zs, desc, db_path))

        for tries in range(2):
            sver = 0
            try:
                db = sqlite3.connect(db_path)
                cur = db.cursor()
                try:
                    zs = "select v from kv where k='sver'"
                    sver = cur.execute(zs).fetchall()[0][0]
                    if sver > native_ver:
                        zs = "this version of copyparty only understands %s v%d and older; the db is v%d"
                        raise Exception(zs % (desc, native_ver, sver))

                    cur.execute(sanchk_q).fetchone()
                except:
                    if sver:
                        raise
                    sver = createfun(cur)

                err = self._verify_db(
                    cur, which, pathopt, db_path, desc, sver, native_ver
                )
                if err:
                    tries = 99
                    self.args.no_ses = True
                    self.log("root", err, 3)
                break

            except Exception as ex:
                if tries or sver > native_ver:
                    raise
                t = "%s is unusable; deleting and recreating: %r"
                self.log("root", t % (desc, ex), 3)
                try:
                    cur.close()  # type: ignore
                except:
                    pass
                try:
                    db.close()  # type: ignore
                except:
                    pass
                try:
                    os.unlink(db_lock)
                except:
                    pass
                os.unlink(db_path)

    def _create_session_db(self, cur )  :
        sch = [
            r"create table kv (k text, v int)",
            r"create table us (un text, si text, t0 int)",
            # username, session-id, creation-time
            r"create index us_un on us(un)",
            r"create index us_si on us(si)",
            r"create index us_t0 on us(t0)",
            r"insert into kv values ('sver', 1)",
        ]
        for cmd in sch:
            cur.execute(cmd)
        self.log("root", "created new sessions-db")
        return 1

    def _create_idp_db(self, cur )  :
        sch = [
            r"create table kv (k text, v int)",
            r"create table us (un text, gs text)",
            # username, groups
            r"create index us_un on us(un)",
            r"insert into kv values ('sver', 1)",
        ]
        for cmd in sch:
            cur.execute(cmd)
        self.log("root", "created new idp-db")
        return 1

    def _verify_db(
        self,
        cur ,
        which ,
        pathopt ,
        db_path ,
        desc ,
        sver ,
        native_ver ,
    )  :
        # ensure writable (maybe owned by other user)
        db = cur.connection

        try:
            zil = cur.execute("select v from kv where k='pid'").fetchall()
            if len(zil) > 1:
                raise Exception()
            owner = zil[0][0]
        except:
            owner = 0

        if which == "ses":
            cons = "Will now disable sessions and instead use plaintext passwords in cookies."
        elif which == "idp":
            cons = "Each IdP-volume will not become available until its associated user sends their first request."
        else:
            raise Exception()

        if not lock_file(db_path + ".lock"):
            t = "the %s [%s] is already in use by another copyparty instance (pid:%d). This is not supported; please provide another database with --%s or give this copyparty-instance its entirely separate config-folder by setting another path in the XDG_CONFIG_HOME env-var. You can also disable this safeguard by setting env-var PRTY_NO_DB_LOCK=1. %s"
            return t % (desc, db_path, owner, pathopt, cons)

        vars = (("pid", os.getpid()), ("ts", int(time.time() * 1000)))
        if owner:
            # wear-estimate: 2 cells; offsets 0x10, 0x50, 0x19720
            for k, v in vars:
                cur.execute("update kv set v=? where k=?", (v, k))
        else:
            # wear-estimate: 3~4 cells; offsets 0x10, 0x50, 0x19180, 0x19710, 0x36000, 0x360b0, 0x36b90
            for k, v in vars:
                cur.execute("insert into kv values(?, ?)", (k, v))

        if sver < native_ver:
            cur.execute("delete from kv where k='sver'")
            cur.execute("insert into kv values('sver',?)", (native_ver,))

        db.commit()
        cur.close()
        db.close()
        return ""

    def setup_share_db(self)  :
        al = self.args
        if not HAVE_SQLITE3:
            self.log("root", "sqlite3 not available; disabling --shr", 1)
            al.shr = ""
            return


        al.shr = al.shr.strip("/")
        if "/" in al.shr or not al.shr:
            t = "config error: --shr must be the name of a virtual toplevel directory to put shares inside"
            self.log("root", t, 1)
            raise Exception(t)

        al.shr = "/%s/" % (al.shr,)
        al.shr1 = al.shr[1:]

        # policy:
        # the shares-db is important, so panic if something is wrong

        db_path = self.args.shr_db
        db_lock = db_path + ".lock"
        try:
            create = not os.path.getsize(db_path)
        except:
            create = True
        zs = "creating new" if create else "opening"
        self.log("root", "%s shares-db %s" % (zs, db_path))

        sver = 0
        try:
            db = sqlite3.connect(db_path)
            cur = db.cursor()
            if not create:
                zs = "select v from kv where k='sver'"
                sver = cur.execute(zs).fetchall()[0][0]
                if sver > VER_SHARES_DB:
                    zs = "this version of copyparty only understands shares-db v%d and older; the db is v%d"
                    raise Exception(zs % (VER_SHARES_DB, sver))

                cur.execute("select count(*) from sh").fetchone()
        except Exception as ex:
            t = "could not open shares-db; will now panic...\nthe following database must be repaired or deleted before you can launch copyparty:\n%s\n\nERROR: %s\n\nadditional details:\n%s\n"
            self.log("root", t % (db_path, ex, min_ex()), 1)
            raise

        try:
            zil = cur.execute("select v from kv where k='pid'").fetchall()
            if len(zil) > 1:
                raise Exception()
            owner = zil[0][0]
        except:
            owner = 0

        if not lock_file(db_lock):
            t = "the shares-db [%s] is already in use by another copyparty instance (pid:%d). This is not supported; please provide another database with --shr-db or give this copyparty-instance its entirely separate config-folder by setting another path in the XDG_CONFIG_HOME env-var. You can also disable this safeguard by setting env-var PRTY_NO_DB_LOCK=1. Will now panic."
            t = t % (db_path, owner)
            self.log("root", t, 1)
            raise Exception(t)

        sch1 = [
            r"create table kv (k text, v int)",
            r"create table sh (k text, pw text, vp text, pr text, st int, un text, t0 int, t1 int)",
            # sharekey, password, src, perms, numFiles, owner, created, expires
        ]
        sch2 = [
            r"create table sf (k text, vp text)",
            r"create index sf_k on sf(k)",
            r"create index sh_k on sh(k)",
            r"create index sh_t1 on sh(t1)",
            r"insert into kv values ('sver', 2)",
        ]

        if not sver:
            sver = VER_SHARES_DB
            for cmd in sch1 + sch2:
                cur.execute(cmd)
            self.log("root", "created new shares-db")

        if sver == 1:
            for cmd in sch2:
                cur.execute(cmd)
            cur.execute("update sh set st = 0")
            self.log("root", "shares-db schema upgrade ok")

        if sver < VER_SHARES_DB:
            cur.execute("delete from kv where k='sver'")
            cur.execute("insert into kv values('sver',?)", (VER_SHARES_DB,))

        vars = (("pid", os.getpid()), ("ts", int(time.time() * 1000)))
        if owner:
            # wear-estimate: same as sessions-db
            for k, v in vars:
                cur.execute("update kv set v=? where k=?", (v, k))
        else:
            for k, v in vars:
                cur.execute("insert into kv values(?, ?)", (k, v))

        db.commit()
        cur.close()
        db.close()

    def start_ftpd(self)  :
        time.sleep(30)

        if hasattr(self, "ftpd") and not self.ftpd:
            self.restart_ftpd()

        if hasattr(self, "tftpd") and not self.tftpd:
            self.restart_tftpd()

    def restart_ftpd(self)  :
        if not hasattr(self, "ftpd"):
            return

        from .ftpd import Ftpd

        if self.ftpd:
            return  # todo

        if not os.path.exists(self.args.cert):
            ensure_cert(self.log, self.args)

        self.ftpd = Ftpd(self)
        self.log("root", "started FTPd")

    def restart_tftpd(self)  :
        if not hasattr(self, "tftpd"):
            return

        from .tftpd import Tftpd

        if self.tftpd:
            return  # todo

        self.tftpd = Tftpd(self)

    def thr_httpsrv_up(self)  :
        time.sleep(1 if self.args.ign_ebind_all else 5)
        expected = self.broker.num_workers * self.tcpsrv.nsrv
        failed = expected - self.httpsrv_up
        if not failed:
            return

        if self.args.ign_ebind_all:
            if not self.tcpsrv.srv:
                for _ in range(self.broker.num_workers):
                    self.broker.say("cb_httpsrv_up")
            return

        if self.args.ign_ebind and self.tcpsrv.srv:
            return

        t = "{}/{} workers failed to start"
        t = t.format(failed, expected)
        self.log("root", t, 1)

        self.retcode = 1
        self.sigterm()

    def sigterm(self)  :
        self.signal_handler(signal.SIGTERM, None)

    def sticky_qr(self)  :
        self._sticky_qr()

    def _unsticky_qr(self, flush=True)  :
        print("\033[s\033[J\033[r\033[u", file=sys.stderr, end="")
        if flush:
            sys.stderr.flush()

    def _sticky_qr(self, force  = False)  :
        sz = termsize()
        if self.qr_tsz == sz:
            if not force:
                return
        else:
            force = False

        if self.qr_tsz:
            self._unsticky_qr(False)
        else:
            atexit.register(self._unsticky_qr)

        tw, th = self.qr_tsz = sz
        zs1, qr = self.tcpsrv.qr.split("\n", 1)
        url, colr = zs1.split(" ", 1)
        nl = len(qr.split("\n"))  # numlines
        lp = 3 if nl * 2 + 4 < tw else 0  # leftpad
        lp0 = lp
        if self.args.qr_pin == 2:
            url = ""
        else:
            while lp and (nl + lp) * 2 + len(url) + 1 > tw:
                lp -= 1
            if (nl + lp) * 2 + len(url) + 1 > tw:
                qr = url + "\n" + qr
                url = ""
                nl += 1
                lp = lp0
        sh = 1 + th - nl
        if lp:
            zs = " " * lp
            qr = zs + qr.replace("\n", "\n" + zs)
        if url:
            url = "%s\033[%d;%dH%s\033[0m" % (colr, sh + 1, (nl + lp) * 2, url)
        qr = colr + qr

        t = "%s\033[%dA" % ("\n" * nl, nl)
        t = "%s\033[s\033[1;%dr\033[%dH%s%s\033[u" % (t, sh - 1, sh, qr, url)
        if not force:
            self.log("qr", "sticky-qrcode %sx%s,%s" % (tw, th, sh), 6)
        self.pr(t, file=sys.stderr, end="")

    def _qr_thr(self):
        qr = self.tcpsrv.qr
        w8 = self.args.qr_wait
        if w8:
            time.sleep(w8)
            self.log("qr-code", qr)
        if self.args.qr_stdout:
            self.pr(self.tcpsrv.qr)
        if self.args.qr_stderr:
            self.pr(self.tcpsrv.qr, file=sys.stderr)
        w8 = self.args.qr_every
        msg = "%s\033[%dA" % (qr, len(qr.split("\n")))
        while w8:
            time.sleep(w8)
            if self.stopping:
                break
            if self.args.qr_pin:
                self._sticky_qr(True)
            else:
                self.log("qr-code", msg)
        w8 = self.args.qr_winch
        while w8:
            time.sleep(w8)
            if self.stopping:
                break
            self._sticky_qr()

    def cb_httpsrv_up(self)  :
        self.httpsrv_up += 1
        if self.httpsrv_up != self.broker.num_workers:
            return

        ar = self.args
        for _ in range(10 if ar.ftp or ar.ftps else 0):
            time.sleep(0.03)
            if self.ftpd:
                break

        if self.tcpsrv.qr:
            if self.args.qr_pin:
                self.sticky_qr()
            if self.args.qr_wait or self.args.qr_every or self.args.qr_winch:
                Daemon(self._qr_thr, "qr")
            else:
                if not self.args.qr_pin:
                    self.log("qr-code", self.tcpsrv.qr)
                if self.args.qr_stdout:
                    self.pr(self.tcpsrv.qr)
                if self.args.qr_stderr:
                    self.pr(self.tcpsrv.qr, file=sys.stderr)
        else:
            self.log("root", "workers OK\n")

        self.after_httpsrv_up()

    def after_httpsrv_up(self)  :
        self.up2k.init_vols()

        Daemon(self.sd_notify, "sd-notify")

    def _feature_test(self)  :
        fok = []
        fng = []
        t_ff = "transcode audio, create spectrograms, video thumbnails"
        to_check = [
            (HAVE_SQLITE3, "sqlite", "sessions and file/media indexing"),
            (HAVE_PIL, "pillow", "image thumbnails (plenty fast)"),
            (HAVE_VIPS, "vips", "image thumbnails (faster, eats more ram)"),
            (HAVE_WEBP, "pillow-webp", "create thumbnails as webp files"),
            (HAVE_FFMPEG, "ffmpeg", t_ff + ", good-but-slow image thumbnails"),
            (HAVE_FFPROBE, "ffprobe", t_ff + ", read audio/media tags"),
            (HAVE_MUTAGEN, "mutagen", "read audio tags (ffprobe is better but slower)"),
            (HAVE_ARGON2, "argon2", "secure password hashing (advanced users only)"),
            (HAVE_ZMQ, "pyzmq", "send zeromq messages from event-hooks"),
            (HAVE_HEIF, "pillow-heif", "read .heif images with pillow (rarely useful)"),
            (HAVE_AVIF, "pillow-avif", "read .avif images with pillow (rarely useful)"),
            (HAVE_RAW, "rawpy", "read RAW images"),
        ]
        if ANYWIN:
            to_check += [
                (HAVE_PSUTIL, "psutil", "improved plugin cleanup  (rarely useful)")
            ]

        verbose = self.args.deps
        if verbose:
            self.log("dependencies", "")

        for have, feat, what in to_check:
            lst = fok if have else fng
            lst.append((feat, what))
            if verbose:
                zi = 2 if have else 5
                sgot = "found" if have else "missing"
                t = "%7s: %s \033[36m(%s)"
                self.log("dependencies", t % (sgot, feat, what), zi)

        if verbose:
            self.log("dependencies", "")
            return

        sok = ", ".join(x[0] for x in fok)
        sng = ", ".join(x[0] for x in fng)

        t = ""
        if sok:
            t += "OK: \033[32m" + sok
        if sng:
            if t:
                t += ", "
            t += "\033[0mNG: \033[35m" + sng

        t += "\033[0m, see --deps (this is fine btw)"
        self.log("optional-dependencies", t, 6)

    def _check_env(self)  :
        al = self.args

        if self.args.no_bauth:
            t = "WARNING: --no-bauth disables support for the Android app; you may want to use --bauth-last instead"
            self.log("root", t, 3)
            if self.args.bauth_last:
                self.log("root", "WARNING: ignoring --bauth-last due to --no-bauth", 3)

        have_tcp = False
        for zs in al.i:
            if not zs.startswith(("unix:", "fd:")):
                have_tcp = True
        if not have_tcp:
            zb = False
            zs = "z zm zm4 zm6 zmv zmvv zs zsv zv"
            for zs in zs.split():
                if getattr(al, zs, False):
                    setattr(al, zs, False)
                    zb = True
            if zb:
                t = "not listening on any ip-addresses (only unix-sockets and/or FDs); cannot enable zeroconf/mdns/ssdp as requested"
                self.log("root", t, 3)

        if not self.args.no_dav:
            from .dxml import DXML_OK

            if not DXML_OK:
                if not self.args.no_dav:
                    self.args.no_dav = True
                    t = "WARNING:\nDisabling WebDAV support because dxml selftest failed. Please report this bug;\n%s\n...and include the following information in the bug-report:\n%s | expat %s\n"
                    self.log("root", t % (URL_BUG, VERSIONS, expat_ver()), 1)

        if not E.scfg and not al.unsafe_state and not os.getenv("PRTY_UNSAFE_STATE"):
            t = "because runtime config is currently being stored in an untrusted emergency-fallback location. Please fix your environment so either XDG_CONFIG_HOME or ~/.config can be used instead, or disable this safeguard with --unsafe-state or env-var PRTY_UNSAFE_STATE=1."
            if not al.no_ses:
                al.no_ses = True
                t2 = "A consequence of this misconfiguration is that passwords will now be sent in the HTTP-header of every request!"
                self.log("root", "WARNING:\nWill disable sessions %s %s" % (t, t2), 1)
            if al.idp_store == 1:
                al.idp_store = 0
                self.log("root", "WARNING:\nDisabling --idp-store %s" % (t,), 3)
            if al.idp_store:
                t2 = "ERROR: Cannot enable --idp-store %s" % (t,)
                self.log("root", t2, 1)
                raise Exception(t2)
            if al.shr:
                t2 = "ERROR: Cannot enable shares %s" % (t,)
                self.log("root", t2, 1)
                raise Exception(t2)

    def _process_config(self)  :
        al = self.args

        al.zm_on = al.zm_on or al.z_on
        al.zs_on = al.zs_on or al.z_on
        al.zm_off = al.zm_off or al.z_off
        al.zs_off = al.zs_off or al.z_off
        ns = "zm_on zm_off zs_on zs_off acao acam"
        for n in ns.split(" "):
            vs = getattr(al, n).split(",")
            vs = [x.strip() for x in vs]
            vs = [x for x in vs if x]
            setattr(al, n, vs)

        ns = "acao acam"
        for n in ns.split(" "):
            vs = getattr(al, n)
            vd = {zs: 1 for zs in vs}
            setattr(al, n, vd)

        ns = "acao"
        for n in ns.split(" "):
            vs = getattr(al, n)
            vs = [x.lower() for x in vs]
            setattr(al, n, vs)

        R = al.rp_loc
        if "//" in R or ":" in R:
            t = "found URL in --rp-loc; it should be just the location, for example /foo/bar"
            raise Exception(t)

        al.R = R = R.strip("/")
        al.SR = "/" + R if R else ""
        al.RS = R + "/" if R else ""
        al.SRS = "/" + R + "/" if R else "/"

        if al.rsp_jtr:
            al.rsp_slp = 0.000001

        zsl = al.th_covers.split(",")
        zsl = [x.strip() for x in zsl]
        zsl = [x for x in zsl if x]
        al.th_covers = zsl
        al.th_coversd = zsl + ["." + x for x in zsl]
        al.th_covers_set = set(al.th_covers)
        al.th_coversd_set = set(al.th_coversd)

        for k in "c".split(" "):
            vl = getattr(al, k)
            if not vl:
                continue

            vl = [os.path.expandvars(os.path.expanduser(x)) for x in vl]
            setattr(al, k, vl)

        for k in "lo hist dbpath ssl_log".split(" "):
            vs = getattr(al, k)
            if vs:
                vs = os.path.expandvars(os.path.expanduser(vs))
                setattr(al, k, vs)

        for k in "idp_adm".split(" "):
            vs = getattr(al, k)
            vsa = [x.strip() for x in vs.split(",")]
            vsa = [x.lower() for x in vsa if x]
            setattr(al, k + "_set", set(vsa))

        zs = "dav_ua1 sus_urls nonsus_urls ua_nodoc ua_nozip"
        for k in zs.split(" "):
            vs = getattr(al, k)
            if not vs or vs == "no":
                setattr(al, k, None)
            else:
                setattr(al, k, re.compile(vs))

        for k in "tftp_lsf".split(" "):
            vs = getattr(al, k)
            if not vs or vs == "no":
                setattr(al, k, None)
            else:
                setattr(al, k, re.compile("^" + vs + "$"))

        if not al.sus_urls:
            al.ban_url = "no"
        elif al.ban_url == "no":
            al.sus_urls = None

        al.xff_hdr = al.xff_hdr.lower()
        al.idp_h_usr = [x.lower() for x in al.idp_h_usr or []]
        al.idp_h_grp = al.idp_h_grp.lower()
        al.idp_h_key = al.idp_h_key.lower()

        al.idp_hm_usr_p = {}
        for zs0 in al.idp_hm_usr or []:
            try:
                sep = zs0[:1]
                hn, zs1, zs2 = zs0[1:].split(sep)
                hn = hn.lower()
                if hn in al.idp_hm_usr_p:
                    al.idp_hm_usr_p[hn][zs1] = zs2
                else:
                    al.idp_hm_usr_p[hn] = {zs1: zs2}
            except:
                raise Exception("invalid --idp-hm-usr [%s]" % (zs0,))

        al.ftp_ipa_nm = build_netmap(al.ftp_ipa or al.ipa, True)
        al.tftp_ipa_nm = build_netmap(al.tftp_ipa or al.ipa, True)

        mte = ODict.fromkeys(DEF_MTE.split(","), True)
        al.mte = odfusion(mte, al.mte)

        mth = ODict.fromkeys(DEF_MTH.split(","), True)
        al.mth = odfusion(mth, al.mth)

        exp = ODict.fromkeys(DEF_EXP.split(" "), True)
        al.exp_md = odfusion(exp, al.exp_md.replace(" ", ","))
        al.exp_lg = odfusion(exp, al.exp_lg.replace(" ", ","))

        for k in ["no_hash", "no_idx", "og_ua", "srch_excl"]:
            ptn = getattr(self.args, k)
            if ptn:
                setattr(self.args, k, re.compile(ptn))

        for k in ["idp_gsep"]:
            ptn = getattr(self.args, k)
            if "]" in ptn:
                ptn = "]" + ptn.replace("]", "")
            if "[" in ptn:
                ptn = ptn.replace("[", "") + "["
            if "-" in ptn:
                ptn = ptn.replace("-", "") + "-"

            ptn = ptn.replace("\\", "\\\\").replace("^", "\\^")
            setattr(self.args, k, re.compile("[%s]" % (ptn,)))

        try:
            zf1, zf2 = self.args.rm_retry.split("/")
            self.args.rm_re_t = float(zf1)
            self.args.rm_re_r = float(zf2)
        except:
            raise Exception("invalid --rm-retry [%s]" % (self.args.rm_retry,))

        try:
            zf1, zf2 = self.args.mv_retry.split("/")
            self.args.mv_re_t = float(zf1)
            self.args.mv_re_r = float(zf2)
        except:
            raise Exception("invalid --mv-retry [%s]" % (self.args.mv_retry,))

        al.js_utc = "false" if al.localtime else "true"

        al.tcolor = al.tcolor.lstrip("#")
        if len(al.tcolor) == 3:  # fc5 => ffcc55
            al.tcolor = "".join([x * 2 for x in al.tcolor])

        if self.args.name_url:
            zs = html_escape(self.args.name_url, True, True)
            zs = '<a href="%s">%s</a>' % (zs, self.args.name)
        else:
            zs = self.args.name
        self.args.name_html = zs

        zs = al.u2sz
        zsl = [x.strip() for x in zs.split(",")]
        if len(zsl) not in (1, 3):
            t = "invalid --u2sz; must be either one number, or a comma-separated list of three numbers (min,default,max)"
            raise Exception(t)
        if len(zsl) < 3:
            zsl = ["1", zs, zs]
        zi2 = 1
        for zs in zsl:
            zi = int(zs)
            # arbitrary constraint (anything above 2 GiB is probably unintended)
            if zi < 1 or zi > 2047:
                raise Exception("invalid --u2sz; minimum is 1, max is 2047")
            if zi < zi2:
                raise Exception("invalid --u2sz; values must be equal or ascending")
            zi2 = zi
        al.u2sz = ",".join(zsl)

        derive_args(al)
        return True

    def _ipa2re(self, txt)  :
        if txt in ("any", "0", ""):
            return None

        zs = txt.replace(" ", "").replace(".", "\\.").replace(",", "|")
        return re.compile("^(?:" + zs + ")")

    def _setlimits(self)  :
        try:
            import resource

            soft, hard = [
                int(x) if x > 0 else 1024 * 1024
                for x in list(resource.getrlimit(resource.RLIMIT_NOFILE))
            ]
        except:
            self.log("root", "failed to read rlimits from os", 6)
            return

        if not soft or not hard:
            t = "got bogus rlimits from os ({}, {})"
            self.log("root", t.format(soft, hard), 6)
            return

        want = self.args.nc * 4
        new_soft = min(hard, want)
        if new_soft < soft:
            return

        # t = "requesting rlimit_nofile({}), have {}"
        # self.log("root", t.format(new_soft, soft), 6)

        try:
            import resource

            resource.setrlimit(resource.RLIMIT_NOFILE, (new_soft, hard))
            soft = new_soft
        except:
            t = "rlimit denied; max open files: {}"
            self.log("root", t.format(soft), 3)
            return

        if soft < want:
            t = "max open files: {} (wanted {} for -nc {})"
            self.log("root", t.format(soft, want, self.args.nc), 3)
            self.args.nc = min(self.args.nc, soft // 2)

    def _logname(self)  :
        dt = datetime.now(self.tz)
        fn = str(self.args.lo)
        for fs in "YmdHMS":
            fs = "%" + fs
            if fs in fn:
                fn = fn.replace(fs, dt.strftime(fs))

        return fn

    def _setup_logfile(self, printed )  :
        base_fn = fn = sel_fn = self._logname()
        do_xz = fn.lower().endswith(".xz")
        if fn != self.args.lo:
            ctr = 0
            # yup this is a race; if started sufficiently concurrently, two
            # copyparties can grab the same logfile (considered and ignored)
            while os.path.exists(sel_fn):
                ctr += 1
                sel_fn = "{}.{}".format(fn, ctr)

        fn = sel_fn
        try:
            bos.makedirs(os.path.dirname(fn))
        except:
            pass

        try:
            if do_xz:
                import lzma

                lh = lzma.open(fn, "wt", encoding="utf-8", errors="replace", preset=0)
                self.args.no_logflush = True
            else:
                lh = open(fn, "wt", encoding="utf-8", errors="replace")
        except:
            import codecs

            lh = codecs.open(fn, "w", encoding="utf-8", errors="replace")

        if getattr(self.args, "free_umask", False):
            os.fchmod(lh.fileno(), 0o644)

        argv = [pybin] + self.argv
        if hasattr(shlex, "quote"):
            argv = [shlex.quote(x) for x in argv]
        else:
            argv = ['"{}"'.format(x) for x in argv]

        msg = "[+] opened logfile [{}]\n".format(fn)
        printed += msg
        t = "t0: {:.3f}\nargv: {}\n\n{}"
        lh.write(t.format(self.E.t0, " ".join(argv), printed))
        self.logf = lh
        self.logf_base_fn = base_fn
        print(msg, end="")

    def run(self)  :
        self.tcpsrv.run()
        if getattr(self.args, "z_chk", 0) and (
            getattr(self.args, "zm", False) or getattr(self.args, "zs", False)
        ):
            Daemon(self.tcpsrv.netmon, "netmon")

        Daemon(self.thr_httpsrv_up, "sig-hsrv-up2")

        sigs = [signal.SIGINT, signal.SIGTERM]
        if not ANYWIN:
            sigs.append(signal.SIGUSR1)

        for sig in sigs:
            signal.signal(sig, self.signal_handler)

        # macos hangs after shutdown on sigterm with while-sleep,
        # windows cannot ^c stop_cond (and win10 does the macos thing but winxp is fine??)
        # linux is fine with both,
        # never lucky
        if ANYWIN:
            # msys-python probably fine but >msys-python
            Daemon(self.stop_thr, "svchub-sig")

            try:
                while not self.stop_req:
                    time.sleep(1)
            except:
                pass

            self.shutdown()
            # cant join; eats signals on win10
            while not self.stopped:
                time.sleep(0.1)
        else:
            self.stop_thr()

    def start_zeroconf(self)  :
        self.zc_ngen += 1

        if getattr(self.args, "zm", False):
            try:
                from .mdns import MDNS

                if self.mdns:
                    self.mdns.stop(True)

                self.mdns = MDNS(self, self.zc_ngen)
                Daemon(self.mdns.run, "mdns")
            except:
                self.log("root", "mdns startup failed;\n" + min_ex(), 3)

        if getattr(self.args, "zs", False):
            try:
                from .ssdp import SSDPd

                if self.ssdp:
                    self.ssdp.stop()

                self.ssdp = SSDPd(self, self.zc_ngen)
                Daemon(self.ssdp.run, "ssdp")
            except:
                self.log("root", "ssdp startup failed;\n" + min_ex(), 3)

    def reload(self, rescan_all_vols , up2k )  :
        t = "config has been reloaded"
        with self.reload_mutex:
            self.log("root", "reloading config")
            self.asrv.reload(9 if up2k else 4)
            ramdisk_chk(self.asrv)
            if up2k:
                self.up2k.reload(rescan_all_vols)
                t += "; volumes are now reinitializing"
            else:
                self.log("root", "reload done")
            self.broker.reload()
        return t

    def _reload_sessions(self)  :
        with self.asrv.mutex:
            self.asrv.load_sessions(True)
        self.broker.reload_sessions()

    def stop_thr(self)  :
        while not self.stop_req:
            with self.stop_cond:
                self.stop_cond.wait(9001)

            if self.reload_req:
                self.reload_req = False
                self.reload(True, True)

        self.shutdown()

    def kill9(self, delay  = 0.0)  :
        if delay > 0.01:
            time.sleep(delay)
            print("component stuck; issuing sigkill")
            time.sleep(0.1)

        if ANYWIN:
            os.system("taskkill /f /pid {}".format(os.getpid()))
        else:
            os.kill(os.getpid(), signal.SIGKILL)

    def signal_handler(self, sig , frame )  :
        if self.stopping:
            if self.nsigs <= 0:
                try:
                    threading.Thread(target=self.pr, args=("OMBO BREAKER",)).start()
                    time.sleep(0.1)
                except:
                    pass

                self.kill9()
            else:
                self.nsigs -= 1
                return

        if not ANYWIN and sig == signal.SIGUSR1:
            self.reload_req = True
        else:
            self.stop_req = True

        with self.stop_cond:
            self.stop_cond.notify_all()

    def shutdown(self)  :
        if self.stopping:
            return

        # start_log_thrs(print, 0.1, 1)

        self.stopping = True
        self.stop_req = True
        with self.stop_cond:
            self.stop_cond.notify_all()

        ret = 1
        try:
            self.pr("OPYTHAT")
            tasks = []
            slp = 0.0

            if self.mdns:
                tasks.append(Daemon(self.mdns.stop, "mdns"))
                slp = time.time() + 0.5

            if self.ssdp:
                tasks.append(Daemon(self.ssdp.stop, "ssdp"))
                slp = time.time() + 0.5

            self.broker.shutdown()
            self.tcpsrv.shutdown()
            self.up2k.shutdown()

            if hasattr(self, "smbd"):
                slp = max(slp, time.time() + 0.5)
                tasks.append(Daemon(self.smbd.stop, "smbd"))

            if self.thumbsrv:
                self.thumbsrv.shutdown()

                for n in range(200):  # 10s
                    time.sleep(0.05)
                    if self.thumbsrv.stopped():
                        break

                    if n == 3:
                        self.log("root", "waiting for thumbsrv (10sec)...")

            if hasattr(self, "smbd"):
                zf = max(time.time() - slp, 0)
                Daemon(self.kill9, a=(zf + 0.5,))

            while time.time() < slp:
                if not next((x for x in tasks if x.is_alive), None):
                    break

                time.sleep(0.05)

            self.log("root", "nailed it")
            ret = self.retcode
        except:
            self.pr("\033[31m[ error during shutdown ]\n{}\033[0m".format(min_ex()))
            raise
        finally:
            if self.args.wintitle:
                print("\033]0;\033\\", file=sys.stderr, end="")
                sys.stderr.flush()

            self.pr("\033[0m", end="")
            if self.logf:
                self.logf.close()

            self.stopped = True
            sys.exit(ret)

    def _log_disabled(self, src , msg , c   = 0)  :
        if not self.logf:
            return

        with self.log_mutex:
            dt = datetime.now(self.tz)
            ts = self.log_dfmt % (
                dt.year,
                dt.month * 100 + dt.day,
                (dt.hour * 100 + dt.minute) * 100 + dt.second,
                dt.microsecond // self.log_div,
            )

            if c and not self.args.no_ansi:
                if isinstance(c, int):
                    msg = "\033[3%sm%s\033[0m" % (c, msg)
                elif "\033" not in c:
                    msg = "\033[%sm%s\033[0m" % (c, msg)
                else:
                    msg = "%s%s\033[0m" % (c, msg)

            if "\033" in src:
                src += "\033[0m"

            if "\033" in msg:
                msg += "\033[0m"

            self.logf.write("@%s [%-21s] %s\n" % (ts, src, msg))
            if not self.args.no_logflush:
                self.logf.flush()

            if dt.day != self.cday or dt.month != self.cmon:
                self._set_next_day(dt)

    def _set_next_day(self, dt )  :
        if self.cday and self.logf and self.logf_base_fn != self._logname():
            self.logf.close()
            self._setup_logfile("")

        self.cday = dt.day
        self.cmon = dt.month

    def _log_enabled(self, src , msg , c   = 0)  :
        """handles logging from all components"""
        with self.log_mutex:
            dt = datetime.now(self.tz)
            if dt.day != self.cday or dt.month != self.cmon:
                zs = "{}\n" if self.no_ansi else "\033[36m{}\033[0m\n"
                zs = zs.format(dt.strftime("%Y-%m-%d"))
                print(zs, end="")
                self._set_next_day(dt)
                if self.logf:
                    self.logf.write(zs)

            fmt = "\033[36m%s \033[33m%-21s \033[0m%s\n"
            if self.no_ansi:
                if c == 1:
                    fmt = "%s %-21s CRIT: %s\n"
                elif c == 3:
                    fmt = "%s %-21s WARN: %s\n"
                elif c == 6:
                    fmt = "%s %-21s  BTW: %s\n"
                else:
                    fmt = "%s %-21s  LOG: %s\n"
                if "\033" in msg:
                    msg = RE_ANSI.sub("", msg)
                if "\033" in src:
                    src = RE_ANSI.sub("", src)
            elif c:
                if isinstance(c, int):
                    msg = "\033[3%sm%s\033[0m" % (c, msg)
                elif "\033" not in c:
                    msg = "\033[%sm%s\033[0m" % (c, msg)
                else:
                    msg = "%s%s\033[0m" % (c, msg)

            ts = self.log_efmt % (
                dt.hour,
                dt.minute,
                dt.second,
                dt.microsecond // self.log_div,
            )
            msg = fmt % (ts, src, msg)
            try:
                print(msg, end="")
            except UnicodeEncodeError:
                try:
                    print(msg.encode("utf-8", "replace").decode(), end="")
                except:
                    print(msg.encode("ascii", "replace").decode(), end="")
            except OSError as ex:
                if ex.errno != errno.EPIPE:
                    raise

            if self.logf:
                self.logf.write(msg)
                if not self.args.no_logflush:
                    self.logf.flush()

    def pr(self, *a , **ka )  :
        try:
            with self.log_mutex:
                print(*a, **ka)
        except OSError as ex:
            if ex.errno != errno.EPIPE:
                raise

    def check_mp_support(self)  :
        if MACOS and not os.environ.get("PRTY_FORCE_MP"):
            return "multiprocessing is wonky on mac osx;"
        elif sys.version_info < (3, 3):
            return "need python 3.3 or newer for multiprocessing;"

        try:
            x   = mp.Queue(1)
            x.put(("foo", "bar"))
            if x.get()[0] != "foo":
                raise Exception()
        except:
            return "multiprocessing is not supported on your platform;"

        return ""

    def check_mp_enable(self)  :
        if self.args.j == 1:
            return False

        try:
            if mp.cpu_count() <= 1 and not os.environ.get("PRTY_FORCE_MP"):
                raise Exception()
        except:
            self.log("svchub", "only one CPU detected; multiprocessing disabled")
            return False

        try:
            # support vscode debugger (bonus: same behavior as on windows)
            mp.set_start_method("spawn", True)
        except AttributeError:
            # py2.7 probably, anyways dontcare
            pass

        err = self.check_mp_support()
        if not err:
            return True
        else:
            self.log("svchub", err)
            self.log("svchub", "cannot efficiently use multiple CPU cores")
            return False

    def sd_notify(self)  :
        try:
            zb = os.getenv("NOTIFY_SOCKET")
            if not zb:
                return

            addr = unicode(zb)
            if addr.startswith("@"):
                addr = "\0" + addr[1:]

            t = "".join(x for x in addr if x in string.printable)
            self.log("sd_notify", t)

            sck = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            sck.connect(addr)
            sck.sendall(b"READY=1")
        except:
            self.log("sd_notify", min_ex())

    def log_stacks(self)  :
        td = time.time() - self.tstack
        if td < 300:
            self.log("stacks", "cooldown {}".format(td))
            return

        self.tstack = time.time()
        zs = "{}\n{}".format(VERSIONS, alltrace())
        zb = zs.encode("utf-8", "replace")
        zb = gzip.compress(zb)
        zs = ub64enc(zb).decode("ascii")
        self.log("stacks", zs)
