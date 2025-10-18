# coding: utf-8
from __future__ import print_function, unicode_literals

import argparse
import base64
import hashlib
import json
import os
import re
import stat
import sys
import threading
import time
from datetime import datetime

from .__init__ import ANYWIN, MACOS, PY2, TYPE_CHECKING, WINDOWS, E
from .bos import bos
from .cfg import flagdescs, permdescs, vf_bmap, vf_cmap, vf_vmap
from .pwhash import PWHash
from .util import (
    DEF_MTE,
    DEF_MTH,
    EXTS,
    FAVICON_MIMES,
    HAVE_SQLITE3,
    IMPLICATIONS,
    META_NOBOTS,
    MIMES,
    SQLITE_VER,
    UNPLICATIONS,
    UTC,
    ODict,
    Pebkac,
    absreal,
    afsenc,
    get_df,
    humansize,
    json_hesc,
    min_ex,
    odfusion,
    read_utf8,
    relchk,
    statdir,
    ub64enc,
    uncyg,
    undot,
    unhumanize,
    vjoin,
    vsplit,
)

if HAVE_SQLITE3:
    import sqlite3

if TYPE_CHECKING:
    from .broker_mp import BrokerMp
    from .broker_thr import BrokerThr
    from .broker_util import BrokerCli

    # Vflags: TypeAlias = dict[str, str | bool | float | list[str]]
    # Vflags: TypeAlias = dict[str, Any]
    # Mflags: TypeAlias = dict[str, Vflags]

if PY2:
    range = xrange  # type: ignore


LEELOO_DALLAS = "leeloo_dallas"
##
## you might be curious what Leeloo Dallas is doing here, so let me explain:
##
## certain daemonic tasks, namely:
##  * deletion of expired files, running on a timer
##  * deletion of sidecar files, initiated by plugins
## need to skip the usual permission-checks to do their thing,
## so we let Leeloo handle these
##
## and also, the smb-server has really shitty support for user-accounts
## so one popular way to avoid issues is by running copyparty without users;
## this makes all smb-clients identify as LD to gain unrestricted access
##
## Leeloo, being a fictional character from The Fifth Element,
## obviously does not exist and will never be able to access any copyparty
## instances from the outside (the username is rejected at every entrypoint)
##
## thanks for coming to my ted talk


SEE_LOG = "see log for details"
SEESLOG = " (see serverlog for details)"
SSEELOG = " ({})".format(SEE_LOG)
BAD_CFG = "invalid config; {}".format(SEE_LOG)
SBADCFG = " ({})".format(BAD_CFG)

PTN_U_GRP = re.compile(r"\$\{u(%[+-][^}]+)\}")
PTN_G_GRP = re.compile(r"\$\{g(%[+-][^}]+)\}")
PTN_U_ANY = re.compile(r"(\${[u][}%])")
PTN_G_ANY = re.compile(r"(\${[g][}%])")
PTN_SIGIL = re.compile(r"(\${[ug][}%])")


class CfgEx(Exception):
    pass


class AXS(object):
    def __init__(
        self,
        uread   = None,
        uwrite   = None,
        umove   = None,
        udel   = None,
        uget   = None,
        upget   = None,
        uhtml   = None,
        uadmin   = None,
        udot   = None,
    )  :
        self.uread  = set(uread or [])
        self.uwrite  = set(uwrite or [])
        self.umove  = set(umove or [])
        self.udel  = set(udel or [])
        self.uget  = set(uget or [])
        self.upget  = set(upget or [])
        self.uhtml  = set(uhtml or [])
        self.uadmin  = set(uadmin or [])
        self.udot  = set(udot or [])

    def __repr__(self)  :
        ks = "uread uwrite umove udel uget upget uhtml uadmin udot".split()
        return "AXS(%s)" % (", ".join("%s=%r" % (k, self.__dict__[k]) for k in ks),)


class Lim(object):
    def __init__(self, log_func )  :
        self.log_func = log_func

        self.reg    = None  # up2k registry

        self.chmod_d = 0o755
        self.uid = self.gid = -1
        self.chown = False

        self.nups   = {}  # num tracker
        self.bups    = {}  # byte tracker list
        self.bupc   = {}  # byte tracker cache

        self.nosub = False  # disallow subdirectories

        self.dfl = 0  # free disk space limit
        self.dft = 0  # last-measured time
        self.dfv = 0  # currently free
        self.vbmax = 0  # volume bytes max
        self.vnmax = 0  # volume max num files

        self.smin = 0  # filesize min
        self.smax = 0  # filesize max

        self.bwin = 0  # bytes window
        self.bmax = 0  # bytes max
        self.nwin = 0  # num window
        self.nmax = 0  # num max

        self.rotn = 0  # rot num files
        self.rotl = 0  # rot depth
        self.rotf = ""  # rot datefmt
        self.rotf_tz = UTC  # rot timezone
        self.rot_re = re.compile("")  # rotf check

    def log(self, msg , c   = 0)  :
        if self.log_func:
            self.log_func("up-lim", msg, c)

    def set_rotf(self, fmt , tz )  :
        self.rotf = fmt
        if tz != "UTC":
            from zoneinfo import ZoneInfo

            self.rotf_tz = ZoneInfo(tz)
        r = re.escape(fmt).replace("%Y", "[0-9]{4}").replace("%j", "[0-9]{3}")
        r = re.sub("%[mdHMSWU]", "[0-9]{2}", r)
        self.rot_re = re.compile("(^|/)" + r + "$")

    def all(
        self,
        ip ,
        rem ,
        sz ,
        ptop ,
        abspath ,
        broker    = None,
        reg    = None,
        volgetter  = "up2k.get_volsize",
    )   :
        if reg is not None and self.reg is None:
            self.reg = reg
            self.dft = 0

        self.chk_nup(ip)
        self.chk_bup(ip)
        self.chk_rem(rem)
        if sz != -1:
            self.chk_sz(sz)
        else:
            sz = 0

        self.chk_vsz(broker, ptop, sz, volgetter)
        self.chk_df(abspath, sz)  # side effects; keep last-ish

        ap2, vp2 = self.rot(abspath)
        if abspath == ap2:
            return ap2, rem

        return ap2, ("{}/{}".format(rem, vp2) if rem else vp2)

    def chk_sz(self, sz )  :
        if sz < self.smin:
            raise Pebkac(400, "file too small")

        if self.smax and sz > self.smax:
            raise Pebkac(400, "file too big")

    def chk_vsz(
        self,
        broker   ,
        ptop ,
        sz ,
        volgetter  = "up2k.get_volsize",
    )  :
        if not broker or not self.vbmax + self.vnmax:
            return

        x = broker.ask(volgetter, ptop)
        nbytes, nfiles = x.get()

        if self.vbmax and self.vbmax < nbytes + sz:
            raise Pebkac(400, "volume has exceeded max size")

        if self.vnmax and self.vnmax < nfiles + 1:
            raise Pebkac(400, "volume has exceeded max num.files")

    def chk_df(self, abspath , sz , already_written  = False)  :
        if not self.dfl:
            return

        if self.dft < time.time():
            self.dft = int(time.time()) + 300

            df, du, err = get_df(abspath, True)
            if err:
                t = "failed to read disk space usage for %r: %s"
                self.log(t % (abspath, err), 3)
                self.dfv = 0xAAAAAAAAA  # 42.6 GiB
            else:
                self.dfv = df or 0

            for j in list(self.reg.values()) if self.reg else []:
                self.dfv -= int(j["size"] / (len(j["hash"]) or 999) * len(j["need"]))

            if already_written:
                sz = 0

        if self.dfv - sz < self.dfl:
            self.dft = min(self.dft, int(time.time()) + 10)
            t = "server HDD is full; {} free, need {}"
            raise Pebkac(500, t.format(humansize(self.dfv - self.dfl), humansize(sz)))

        self.dfv -= int(sz)

    def chk_rem(self, rem )  :
        if self.nosub and rem:
            raise Pebkac(500, "no subdirectories allowed")

    def rot(self, path )   :
        if not self.rotf and not self.rotn:
            return path, ""

        if self.rotf:
            path = path.rstrip("/\\")
            if self.rot_re.search(path.replace("\\", "/")):
                return path, ""

            suf = datetime.now(self.rotf_tz).strftime(self.rotf)
            if path:
                path += "/"

            return path + suf, suf

        ret = self.dive(path, self.rotl)
        if not ret:
            raise Pebkac(500, "no available slots in volume")

        d = ret[len(path) :].strip("/\\").replace("\\", "/")
        return ret, d

    def dive(self, path , lvs )  :
        items = bos.listdir(path)

        if not lvs:
            # at leaf level
            return None if len(items) >= self.rotn else ""

        dirs = [int(x) for x in items if x and all(y in "1234567890" for y in x)]
        dirs.sort()

        if not dirs:
            # no branches yet; make one
            sub = os.path.join(path, "0")
            bos.mkdir(sub, self.chmod_d)
            if self.chown:
                os.chown(sub, self.uid, self.gid)
        else:
            # try newest branch only
            sub = os.path.join(path, str(dirs[-1]))

        ret = self.dive(sub, lvs - 1)
        if ret is not None:
            return os.path.join(sub, ret)

        if len(dirs) >= self.rotn:
            # full branch or root
            return None

        # make a branch
        sub = os.path.join(path, str(dirs[-1] + 1))
        bos.mkdir(sub, self.chmod_d)
        if self.chown:
            os.chown(sub, self.uid, self.gid)
        ret = self.dive(sub, lvs - 1)
        if ret is None:
            raise Pebkac(500, "rotation bug")

        return os.path.join(sub, ret)

    def nup(self, ip )  :
        try:
            self.nups[ip].append(time.time())
        except:
            self.nups[ip] = [time.time()]

    def bup(self, ip , nbytes )  :
        v = (time.time(), nbytes)
        try:
            self.bups[ip].append(v)
            self.bupc[ip] += nbytes
        except:
            self.bups[ip] = [v]
            self.bupc[ip] = nbytes

    def chk_nup(self, ip )  :
        if not self.nmax or ip not in self.nups:
            return

        nups = self.nups[ip]
        cutoff = time.time() - self.nwin
        while nups and nups[0] < cutoff:
            nups.pop(0)

        if len(nups) >= self.nmax:
            raise Pebkac(429, "too many uploads")

    def chk_bup(self, ip )  :
        if not self.bmax or ip not in self.bups:
            return

        bups = self.bups[ip]
        cutoff = time.time() - self.bwin
        mark = self.bupc[ip]
        while bups and bups[0][0] < cutoff:
            mark -= bups.pop(0)[1]

        self.bupc[ip] = mark
        if mark >= self.bmax:
            raise Pebkac(429, "upload size limit exceeded")


class VFS(object):
    """single level in the virtual fs"""

    def __init__(
        self,
        log ,
        realpath ,
        vpath ,
        vpath0 ,
        axs ,
        flags  ,
    )  :
        self.log = log
        self.realpath = realpath  # absolute path on host filesystem
        self.vpath = vpath  # absolute path in the virtual filesystem
        self.vpath0 = vpath0  # original vpath (before idp expansion)
        self.axs = axs
        self.flags = flags  # config options
        self.root = self
        self.dev = 0  # st_dev
        self.nodes   = {}  # child nodes
        self.histtab   = {}  # all realpath->histpath
        self.dbpaths   = {}  # all realpath->dbpath
        self.dbv  = None  # closest full/non-jump parent
        self.lim  = None  # upload limits; only set for dbv
        self.shr_src   = None  # source vfs+rem of a share
        self.shr_files  = set()  # filenames to include from shr_src
        self.shr_owner  = ""  # uname
        self.shr_all_aps   = []
        self.aread   = {}
        self.awrite   = {}
        self.amove   = {}
        self.adel   = {}
        self.aget   = {}
        self.apget   = {}
        self.ahtml   = {}
        self.aadmin   = {}
        self.adot   = {}
        self.js_ls = {}
        self.js_htm = ""
        self.all_vols   = {}  # flattened recursive
        self.all_nodes   = {}  # also jumpvols/shares

        if realpath:
            rp = realpath + ("" if realpath.endswith(os.sep) else os.sep)
            vp = vpath + ("/" if vpath else "")
            self.histpath = os.path.join(realpath, ".hist")  # db / thumbcache
            self.dbpath = self.histpath
            self.all_vols[vpath] = self
            self.all_nodes[vpath] = self
            self.all_aps = [(rp, [self])]
            self.all_vps = [(vp, self)]
            self.canonical = self._canonical
            self.dcanonical = self._dcanonical
        else:
            self.histpath = self.dbpath = ""
            self.all_aps = []
            self.all_vps = []
            self.canonical = self._canonical_null
            self.dcanonical = self._dcanonical_null

        self.get_dbv = self._get_dbv
        self.ls = self._ls

    def __repr__(self)  :
        return "VFS(%s)" % (
            ", ".join(
                "%s=%r" % (k, self.__dict__[k])
                for k in "realpath vpath axs flags".split()
            )
        )

    def get_all_vols(
        self,
        vols  ,
        nodes  ,
        aps  ,
        vps  ,
    )  :
        nodes[self.vpath] = self
        if self.realpath:
            vols[self.vpath] = self
            rp = self.realpath
            rp += "" if rp.endswith(os.sep) else os.sep
            vp = self.vpath + ("/" if self.vpath else "")
            hit = next((x[1] for x in aps if x[0] == rp), None)
            if hit:
                hit.append(self)
            else:
                aps.append((rp, [self]))
            vps.append((vp, self))

        for v in self.nodes.values():
            v.get_all_vols(vols, nodes, aps, vps)

    def add(self, src , dst , dst0 )  :
        """get existing, or add new path to the vfs"""
        assert src == "/" or not src.endswith("/")  # nosec
        assert not dst.endswith("/")  # nosec

        if "/" in dst:
            # requires breadth-first population (permissions trickle down)
            name, dst = dst.split("/", 1)
            name0, dst0 = dst0.split("/", 1)
            if name in self.nodes:
                # exists; do not manipulate permissions
                return self.nodes[name].add(src, dst, dst0)

            vn = VFS(
                self.log,
                os.path.join(self.realpath, name) if self.realpath else "",
                "{}/{}".format(self.vpath, name).lstrip("/"),
                "{}/{}".format(self.vpath0, name0).lstrip("/"),
                self.axs,
                self._copy_flags(name),
            )
            vn.dbv = self.dbv or self
            self.nodes[name] = vn
            return vn.add(src, dst, dst0)

        if dst in self.nodes:
            # leaf exists; return as-is
            return self.nodes[dst]

        # leaf does not exist; create and keep permissions blank
        vp = "{}/{}".format(self.vpath, dst).lstrip("/")
        vp0 = "{}/{}".format(self.vpath0, dst0).lstrip("/")
        vn = VFS(self.log, src, vp, vp0, AXS(), {})
        vn.dbv = self.dbv or self
        self.nodes[dst] = vn
        return vn

    def _copy_flags(self, name )   :
        flags = {k: v for k, v in self.flags.items()}

        hist = flags.get("hist")
        if hist and hist != "-":
            zs = "{}/{}".format(hist.rstrip("/"), name)
            flags["hist"] = os.path.expandvars(os.path.expanduser(zs))

        dbp = flags.get("dbpath")
        if dbp and dbp != "-":
            zs = "{}/{}".format(dbp.rstrip("/"), name)
            flags["dbpath"] = os.path.expandvars(os.path.expanduser(zs))

        return flags

    def bubble_flags(self)  :
        if self.dbv:
            for k, v in self.dbv.flags.items():
                if k not in ("hist", "dbpath"):
                    self.flags[k] = v

        for n in self.nodes.values():
            n.bubble_flags()

    def _find(self, vpath )   :
        """return [vfs,remainder]"""
        if not vpath:
            return self, ""

        if "/" in vpath:
            name, rem = vpath.split("/", 1)
        else:
            name = vpath
            rem = ""

        if name in self.nodes:
            return self.nodes[name]._find(rem)

        return self, vpath

    def can_access(
        self, vpath , uname 
    )         :
        """can Read,Write,Move,Delete,Get,Upget,Admin,Dot"""
        if vpath:
            vn, _ = self._find(undot(vpath))
        else:
            vn = self

        c = vn.axs
        return (
            uname in c.uread,
            uname in c.uwrite,
            uname in c.umove,
            uname in c.udel,
            uname in c.uget,
            uname in c.upget,
            uname in c.uadmin,
            uname in c.udot,
        )
        # skip uhtml because it's rarely needed

    def get_perms(self, vpath , uname )  :
        zbl = self.can_access(vpath, uname)
        ret = "".join(ch for ch, ok in zip("rwmdgGa.", zbl) if ok)
        if "rwmd" in ret and "a." in ret:
            ret += "A"
        return ret

    def get(
        self,
        vpath ,
        uname ,
        will_read ,
        will_write ,
        will_move  = False,
        will_del  = False,
        will_get  = False,
        err  = 403,
    )   :
        """returns [vfsnode,fs_remainder] if user has the requested permissions"""
        if relchk(vpath):
            if self.log:
                self.log("vfs", "invalid relpath %r @%s" % (vpath, uname))
            raise Pebkac(422)

        cvpath = undot(vpath)
        vn, rem = self._find(cvpath)
        c  = vn.axs

        for req, d, msg in [
            (will_read, c.uread, "read"),
            (will_write, c.uwrite, "write"),
            (will_move, c.umove, "move"),
            (will_del, c.udel, "delete"),
            (will_get, c.uget, "get"),
        ]:
            if req and uname not in d and uname != LEELOO_DALLAS:
                if vpath != cvpath and vpath != "." and self.log:
                    ap = vn.canonical(rem)
                    t = "%s has no %s in %r => %r => %r"
                    self.log("vfs", t % (uname, msg, vpath, cvpath, ap), 6)

                t = "you don't have %s-access in %r or below %r"
                raise Pebkac(err, t % (msg, "/" + cvpath, "/" + vn.vpath))

        return vn, rem

    def _get_share_src(self, vrem )   :
        src = self.shr_src
        if not src:
            return self._get_dbv(vrem)

        shv, srem = src
        return shv._get_dbv(vjoin(srem, vrem))

    def _get_dbv(self, vrem )   :
        dbv = self.dbv
        if not dbv:
            return self, vrem

        vrem = vjoin(self.vpath[len(dbv.vpath) :].lstrip("/"), vrem)
        return dbv, vrem

    def casechk(self, rem , do_stat )  :
        ap = self.canonical(rem, False)
        if do_stat and not bos.path.exists(ap):
            return True  # doesn't exist at all; good to go
        dp, fn = os.path.split(ap)
        if not fn:
            return True  # filesystem root
        try:
            fns = os.listdir(dp)
        except:
            return True  # maybe chmod 111; assume ok
        if fn in fns:
            return True
        hit = "<?>"
        lfn = fn.lower()
        for zs in fns:
            if lfn == zs.lower():
                hit = zs
                break
        if not hit:
            return True  # NFC/NFD or something, can't be helped either way
        if self.log:
            t = "returning 404 due to underlying case-insensitive filesystem:\n  http-req: %r\n  local-fs: %r"
            self.log("vfs", t % (fn, hit))
        return False

    def _canonical_null(self, rem , resolve  = True)  :
        return ""

    def _dcanonical_null(self, rem )  :
        return ""

    def _canonical(self, rem , resolve  = True)  :
        """returns the canonical path (fully-resolved absolute fs path)"""
        ap = self.realpath
        if rem:
            ap += "/" + rem

        return absreal(ap) if resolve else ap

    def _dcanonical(self, rem )  :
        """resolves until the final component (filename)"""
        ap = self.realpath
        if rem:
            ap += "/" + rem

        ad, fn = os.path.split(ap)
        return os.path.join(absreal(ad), fn)

    def _canonical_shr(self, rem , resolve  = True)  :
        """returns the canonical path (fully-resolved absolute fs path)"""
        ap = self.realpath
        if rem:
            ap += "/" + rem

        rap = absreal(ap)
        if self.shr_files:
            vn, rem = self.shr_src
            chk = absreal(os.path.join(vn.realpath, rem))
            if chk != rap:
                # not the dir itself; assert file allowed
                ad, fn = os.path.split(rap)
                if chk != ad or fn not in self.shr_files:
                    return "\n\n"

        return rap if resolve else ap

    def _dcanonical_shr(self, rem )  :
        """resolves until the final component (filename)"""
        ap = self.realpath
        if rem:
            ap += "/" + rem

        ad, fn = os.path.split(ap)
        ad = absreal(ad)
        if self.shr_files:
            vn, rem = self.shr_src
            chk = absreal(os.path.join(vn.realpath, rem))
            if chk != absreal(ap):
                # not the dir itself; assert file allowed
                if ad != chk or fn not in self.shr_files:
                    return "\n\n"

        return os.path.join(ad, fn)

    def _ls_nope(
        self, *a, **ka
    )      :
        raise Pebkac(500, "nope.avi")

    def _ls_shr(
        self,
        rem ,
        uname ,
        scandir ,
        permsets ,
        lstat  = False,
        throw  = False,
    )      :
        """replaces _ls for certain shares (single-file, or file selection)"""
        vn, rem = self.shr_src  # type: ignore
        abspath, real, _ = vn.ls(rem, "\n", scandir, permsets, lstat, throw)
        real = [x for x in real if os.path.basename(x[0]) in self.shr_files]
        return abspath, real, {}

    def _ls(
        self,
        rem ,
        uname ,
        scandir ,
        permsets ,
        lstat  = False,
        throw  = False,
    )      :
        """return user-readable [fsdir,real,virt] items at vpath"""
        virt_vis = {}  # nodes readable by user
        abspath = self.canonical(rem)
        if abspath:
            real = list(statdir(self.log, scandir, lstat, abspath, throw))
            real.sort()
        else:
            real = []

        if not rem:
            # no vfs nodes in the list of real inodes
            real = [x for x in real if x[0] not in self.nodes]

            dbv = self.dbv or self
            for name, vn2 in sorted(self.nodes.items()):
                if vn2.dbv == dbv and self.flags.get("dk"):
                    virt_vis[name] = vn2
                    continue

                ok = False
                zx = vn2.axs
                axs = [zx.uread, zx.uwrite, zx.umove, zx.udel, zx.uget]
                for pset in permsets:
                    ok = True
                    for req, lst in zip(pset, axs):
                        if req and uname not in lst:
                            ok = False
                    if ok:
                        break

                if ok:
                    virt_vis[name] = vn2

        if ".hist" in abspath:
            p = abspath.replace("\\", "/") if WINDOWS else abspath
            if p.endswith("/.hist"):
                real = [x for x in real if not x[0].startswith("up2k.")]
            elif "/.hist/th/" in p:
                real = [x for x in real if not x[0].endswith("dir.txt")]

        return abspath, real, virt_vis

    def walk(
        self,
        rel ,
        rem ,
        seen ,
        uname ,
        permsets ,
        wantdots ,
        scandir ,
        lstat ,
        subvols  = True,
    ):  
        
            
            
            
            
             
             
             
        
        
        
    
        """
        recursively yields from ./rem;
        rel is a unix-style user-defined vpath (not vfs-related)

        NOTE: don't invoke this function from a dbv; subvols are only
          descended into if rem is blank due to the _ls `if not rem:`
          which intention is to prevent unintended access to subvols
        """

        fsroot, vfs_ls, vfs_virt = self.ls(rem, uname, scandir, permsets, lstat=lstat)
        dbv, vrem = self.get_dbv(rem)

        if (
            seen
            and (not fsroot.startswith(seen[-1]) or fsroot == seen[-1])
            and fsroot in seen
        ):
            if self.log:
                t = "bailing from symlink loop,\n  prev: %r\n  curr: %r\n  from: %r / %r"
                self.log("vfs.walk", t % (seen[-1], fsroot, self.vpath, rem), 3)
            return

        if "xdev" in self.flags or "xvol" in self.flags:
            rm1 = []
            for le in vfs_ls:
                ap = absreal(os.path.join(fsroot, le[0]))
                vn2 = self.chk_ap(ap)
                if not vn2 or not vn2.get("", uname, True, False):
                    rm1.append(le)
            _ = [vfs_ls.remove(x) for x in rm1]  # type: ignore

        dots_ok = wantdots and (wantdots == 2 or uname in dbv.axs.udot)
        if not dots_ok:
            vfs_ls = [x for x in vfs_ls if "/." not in "/" + x[0]]

        seen = seen[:] + [fsroot]
        rfiles = [x for x in vfs_ls if not stat.S_ISDIR(x[1].st_mode)]
        rdirs = [x for x in vfs_ls if stat.S_ISDIR(x[1].st_mode)]
        # if lstat: ignore folder symlinks since copyparty will never make those
        #            (and we definitely don't want to descend into them)

        rfiles.sort()
        rdirs.sort()

        yield dbv, vrem, rel, fsroot, rfiles, rdirs, vfs_virt

        for rdir, _ in rdirs:
            if not dots_ok and rdir.startswith("."):
                continue

            wrel = (rel + "/" + rdir).lstrip("/")
            wrem = (rem + "/" + rdir).lstrip("/")
            for x in self.walk(
                wrel, wrem, seen, uname, permsets, wantdots, scandir, lstat, subvols
            ):
                yield x

        if not subvols:
            return

        for n, vfs in sorted(vfs_virt.items()):
            if not dots_ok and n.startswith("."):
                continue

            wrel = (rel + "/" + n).lstrip("/")
            for x in vfs.walk(
                wrel, "", seen, uname, permsets, wantdots, scandir, lstat
            ):
                yield x

    def zipgen(
        self,
        vpath ,
        vrem ,
        flt ,
        uname ,
        dirs ,
        scandir ,
        wrap  = True,
    )     :

        # if multiselect: add all items to archive root
        # if single folder: the folder itself is the top-level item
        folder = "" if flt or not wrap else (vpath.split("/")[-1].lstrip(".") or "top")

        g = self.walk(folder, vrem, [], uname, [[True, False]], 1, scandir, False)
        for _, _, vpath, apath, files, rd, vd in g:
            if flt:
                files = [x for x in files if x[0] in flt]

                rm1 = [x for x in rd if x[0] not in flt]
                _ = [rd.remove(x) for x in rm1]  # type: ignore

                rm2 = [x for x in vd.keys() if x not in flt]
                _ = [vd.pop(x) for x in rm2]

                flt = set()

            # print(repr([vpath, apath, [x[0] for x in files]]))
            fnames = [n[0] for n in files]
            vpaths = [vpath + "/" + n for n in fnames] if vpath else fnames
            apaths = [os.path.join(apath, n) for n in fnames]
            ret = list(zip(vpaths, apaths, files))

            for f in [{"vp": v, "ap": a, "st": n[1]} for v, a, n in ret]:
                yield f

            if not dirs:
                continue

            ts = int(time.time())
            st = os.stat_result((16877, -1, -1, 1, 1000, 1000, 8, ts, ts, ts))
            dnames = [n[0] for n in rd]
            dstats = [n[1] for n in rd]
            dnames += list(vd.keys())
            dstats += [st] * len(vd)
            vpaths = [vpath + "/" + n for n in dnames] if vpath else dnames
            apaths = [os.path.join(apath, n) for n in dnames]
            ret2 = list(zip(vpaths, apaths, dstats))
            for d in [{"vp": v, "ap": a, "st": n} for v, a, n in ret2]:
                yield d

    def chk_ap(self, ap , st  = None)  :
        aps = ap + os.sep
        if "xdev" in self.flags and not ANYWIN:
            if not st:
                ap2 = ap.replace("\\", "/") if ANYWIN else ap
                while ap2:
                    try:
                        st = bos.stat(ap2)
                        break
                    except:
                        if "/" not in ap2:
                            raise
                        ap2 = ap2.rsplit("/", 1)[0]
                assert st

            vdev = self.dev
            if not vdev:
                vdev = self.dev = bos.stat(self.realpath).st_dev

            if vdev != st.st_dev:
                if self.log:
                    t = "xdev: %s[%r] => %s[%r]"
                    self.log("vfs", t % (vdev, self.realpath, st.st_dev, ap), 3)

                return None

        if "xvol" in self.flags:
            self_ap = self.realpath + os.sep
            if aps.startswith(self_ap):
                vp = aps[len(self_ap) :]
                if ANYWIN:
                    vp = vp.replace(os.sep, "/")
                vn2, _ = self._find(vp)
                if self == vn2:
                    return self

            all_aps = self.shr_all_aps or self.root.all_aps

            for vap, vns in all_aps:
                if aps.startswith(vap):
                    return self if self in vns else vns[0]

            if self.log:
                self.log("vfs", "xvol: %r" % (ap,), 3)

            return None

        return self

    def check_landmarks(self)  :
        if self.dbv:
            return True

        vps = self.flags.get("landmark") or []
        if not vps:
            return True

        failed = ""
        for vp in vps:
            if "^=" in vp:
                vp, zs = vp.split("^=", 1)
                expect = zs.encode("utf-8")
            else:
                expect = b""

            if self.log:
                t = "checking [/%s] landmark [%s]"
                self.log("vfs", t % (self.vpath, vp), 6)

            ap = "?"
            try:
                ap = self.canonical(vp)
                with open(ap, "rb") as f:
                    buf = f.read(4096)
                    if not buf.startswith(expect):
                        t = "file [%s] does not start with the expected bytes %s"
                        failed = t % (ap, expect)
                        break
            except Exception as ex:
                t = "%r while trying to read [%s] => [%s]"
                failed = t % (ex, vp, ap)
                break

        if not failed:
            return True

        if self.log:
            t = "WARNING: landmark verification failed; %s; will now disable up2k database for volume [/%s]"
            self.log("vfs", t % (failed, self.vpath), 3)

        for rm in "e2d e2t e2v".split():
            self.flags = {k: v for k, v in self.flags.items() if not k.startswith(rm)}
        self.flags["d2d"] = True
        self.flags["d2t"] = True
        return False


if WINDOWS:
    re_vol = re.compile(r"^([a-zA-Z]:[\\/][^:]*|[^:]*):([^:]*):(.*)$")
else:
    re_vol = re.compile(r"^([^:]*):([^:]*):(.*)$")


class AuthSrv(object):
    """verifies users against given paths"""

    def __init__(
        self,
        args ,
        log_func ,
        warn_anonwrite  = True,
        dargs  = None,
    )  :
        self.ah = PWHash(args)
        self.args = args
        self.dargs = dargs or args
        self.log_func = log_func
        self.warn_anonwrite = warn_anonwrite
        self.line_ctr = 0
        self.indent = ""
        self.is_lxc = args.c == ["/z/initcfg"]

        self._vf0b = {
            "tcolor": self.args.tcolor,
            "du_iwho": self.args.du_iwho,
            "shr_who": self.args.shr_who if self.args.shr else "no",
        }
        self._vf0 = self._vf0b.copy()
        self._vf0["d2d"] = True

        # fwd-decl
        self.vfs = VFS(log_func, "", "", "", AXS(), {})
        self.acct   = {}  # uname->pw
        self.iacct   = {}  # pw->uname
        self.ases   = {}  # uname->session
        self.sesa   = {}  # session->uname
        self.defpw   = {}
        self.grps   = {}
        self.re_pwd  = None
        self.cfg_files_loaded  = []
        self.badcfg1 = False

        # all volumes observed since last restart
        self.idp_vols   = {}  # vpath->abspath

        # all users/groups observed since last restart
        self.idp_accs   = {}  # username->groupnames
        self.idp_usr_gh   = {}  # username->group-header-value (cache)

        self.hid_cache   = {}
        self.mutex = threading.Lock()
        self.reload()

    def log(self, msg , c   = 0)  :
        if self.log_func:
            self.log_func("auth", msg, c)

    def laggy_iter(self, iterable )    :
        """returns [value,isFinalValue]"""
        it = iter(iterable)
        prev = next(it)
        for x in it:
            yield prev, False
            prev = x

        yield prev, True

    def vf0(self):
        return self._vf0.copy()

    def vf0b(self):
        return self._vf0b.copy()

    def idp_checkin(
        self, broker , uname , gname 
    )  :
        if uname in self.acct:
            return False

        if self.idp_usr_gh.get(uname) == gname:
            return False

        gnames = [x.strip() for x in self.args.idp_gsep.split(gname)]
        gnames.sort()

        with self.mutex:
            self.idp_usr_gh[uname] = gname
            if self.idp_accs.get(uname) == gnames:
                return False

            self.idp_accs[uname] = gnames
            try:
                self._update_idp_db(uname, gname)
            except:
                self.log("failed to update the --idp-db:\n%s" % (min_ex(),), 3)

            t = "reinitializing due to new user from IdP: [%r:%r]"
            self.log(t % (uname, gnames), 3)

            if not broker:
                # only true for tests
                self._reload()
                return True

        broker.ask("reload", False, True).get()
        return True

    def _update_idp_db(self, uname , gname )  :
        if not self.args.idp_store:
            return


        db = sqlite3.connect(self.args.idp_db)
        cur = db.cursor()

        cur.execute("delete from us where un = ?", (uname,))
        cur.execute("insert into us values (?,?)", (uname, gname))

        db.commit()
        cur.close()
        db.close()

    def _map_volume_idp(
        self,
        src ,
        dst ,
        mount   ,
        daxs  ,
        mflags   ,
        un_gns  ,
    )     :
        ret     = []
        visited = set()
        src0 = src  # abspath
        dst0 = dst  # vpath

        zsl = []
        for ptn, sigil in ((PTN_U_ANY, "${u}"), (PTN_G_ANY, "${g}")):
            if bool(ptn.search(src)) != bool(ptn.search(dst)):
                zsl.append(sigil)
        if zsl:
            t = "ERROR: if %s is mentioned in a volume definition, it must be included in both the filesystem-path [%s] and the volume-url [/%s]"
            t = "\n".join([t % (x, src, dst) for x in zsl])
            self.log(t, 1)
            raise Exception(t)

        un_gn = [(un, gn) for un, gns in un_gns.items() for gn in gns]
        if not un_gn:
            # ensure volume creation if there's no users
            un_gn = [("", "")]

        for un, gn in un_gn:
            rejected = False
            for ptn in [PTN_U_GRP, PTN_G_GRP]:
                m = ptn.search(dst0)
                if not m:
                    continue
                zs = m.group(1)
                zs = zs.replace(",%+", "\n%+")
                zs = zs.replace(",%-", "\n%-")
                for rule in zs.split("\n"):
                    gnc = rule[2:]
                    if ptn == PTN_U_GRP:
                        # is user member of group?
                        hit = gnc in (un_gns.get(un) or [])
                    else:
                        # is it this specific group?
                        hit = gn == gnc

                    if rule.startswith("%+") != hit:
                        rejected = True
            if rejected:
                continue

            if gn == self.args.grp_all:
                gn = ""

            # if ap/vp has a user/group placeholder, make sure to keep
            # track so the same user/group is mapped when setting perms;
            # otherwise clear un/gn to indicate it's a regular volume

            src1 = src0.replace("${u}", un or "\n")
            dst1 = dst0.replace("${u}", un or "\n")
            src1 = PTN_U_GRP.sub(un or "\n", src1)
            dst1 = PTN_U_GRP.sub(un or "\n", dst1)
            if src0 == src1 and dst0 == dst1:
                un = ""

            src = src1.replace("${g}", gn or "\n")
            dst = dst1.replace("${g}", gn or "\n")
            src = PTN_G_GRP.sub(gn or "\n", src)
            dst = PTN_G_GRP.sub(gn or "\n", dst)
            if src == src1 and dst == dst1:
                gn = ""

            if "\n" in (src + dst):
                continue

            label = "%s\n%s" % (src, dst)
            if label in visited:
                continue
            visited.add(label)

            src, dst = self._map_volume(src, dst, dst0, mount, daxs, mflags)
            if src:
                ret.append((src, dst, un, gn))
                if un or gn:
                    self.idp_vols[dst] = src

        return ret

    def _map_volume(
        self,
        src ,
        dst ,
        dst0 ,
        mount   ,
        daxs  ,
        mflags   ,
    )   :
        src = os.path.expandvars(os.path.expanduser(src))
        src = absreal(src)
        dst = dst.strip("/")

        if dst in mount:
            t = "multiple filesystem-paths mounted at [/{}]:\n  [{}]\n  [{}]"
            self.log(t.format(dst, mount[dst][0], src), c=1)
            raise Exception(BAD_CFG)

        if src in mount.values():
            t = "filesystem-path [{}] mounted in multiple locations:"
            t = t.format(src)
            for v in [k for k, v in mount.items() if v[0] == src] + [dst]:
                t += "\n  /{}".format(v)

            self.log(t, c=3)
            raise Exception(BAD_CFG)

        if not bos.path.exists(src):
            self.log("warning: filesystem-path did not exist: %r" % (src,), 3)

        mount[dst] = (src, dst0)
        daxs[dst] = AXS()
        mflags[dst] = {}
        return (src, dst)

    def _e(self, desc  = None)  :
        if not self.args.vc or not self.line_ctr:
            return

        if not desc and not self.indent:
            self.log("")
            return

        desc = desc or ""
        desc = desc.replace("[", "[\033[0m").replace("]", "\033[90m]")
        self.log(" >>> {}{}".format(self.indent, desc), "90")

    def _l(self, ln , c , desc )  :
        if not self.args.vc or not self.line_ctr:
            return

        if c < 10:
            c += 30

        t = "\033[97m{:4} \033[{}m{}{}"
        if desc:
            t += "  \033[0;90m# {}\033[0m"
            desc = desc.replace("[", "[\033[0m").replace("]", "\033[90m]")

        self.log(t.format(self.line_ctr, c, self.indent, ln, desc))

    def _all_un_gn(
        self,
        acct  ,
        grps  ,
    )   :
        """
        generate list of all confirmed pairs of username/groupname seen since last restart;
        in case of conflicting group memberships then it is selected as follows:
         * any non-zero value from IdP group header
         * otherwise take --grps / [groups]
        """
        self.load_idp_db(bool(self.idp_accs))
        ret = {un: gns[:] for un, gns in self.idp_accs.items()}
        ret.update({zs: [""] for zs in acct if zs not in ret})
        grps[self.args.grp_all] = list(ret.keys())
        for gn, uns in grps.items():
            for un in uns:
                try:
                    ret[un].append(gn)
                except:
                    ret[un] = [gn]

        return ret

    def _parse_config_file(
        self,
        fp ,
        cfg_lines ,
        acct  ,
        grps  ,
        daxs  ,
        mflags   ,
        mount   ,
    )  :
        self.line_ctr = 0

        expand_config_file(self.log, cfg_lines, fp, "")
        if self.args.vc:
            lns = ["{:4}: {}".format(n, s) for n, s in enumerate(cfg_lines, 1)]
            self.log("expanded config file (unprocessed):\n" + "\n".join(lns))

        cfg_lines = upgrade_cfg_fmt(self.log, self.args, cfg_lines, fp)

        # due to IdP, volumes must be parsed after users and groups;
        # do volumes in a 2nd pass to allow arbitrary order in config files
        for npass in range(1, 3):
            if self.args.vc:
                self.log("parsing config files; pass %d/%d" % (npass, 2))
            self._parse_config_file_2(cfg_lines, acct, grps, daxs, mflags, mount, npass)

    def _parse_config_file_2(
        self,
        cfg_lines ,
        acct  ,
        grps  ,
        daxs  ,
        mflags   ,
        mount   ,
        npass ,
    )  :
        self.line_ctr = 0
        all_un_gn = self._all_un_gn(acct, grps)

        cat = ""
        catg = "[global]"
        cata = "[accounts]"
        catgrp = "[groups]"
        catx = "accs:"
        catf = "flags:"
        ap  = None
        vp  = None
        vols     = []
        for ln in cfg_lines:
            self.line_ctr += 1
            ln = ln.split("  #")[0].strip()
            if not ln.split("#")[0].strip():
                continue

            if re.match(r"^\[.*\]:$", ln):
                ln = ln[:-1]

            subsection = ln in (catx, catf)
            if ln.startswith("[") or subsection:
                self._e()
                if npass > 1 and ap is None and vp is not None:
                    t = "the first line after [/{}] must be a filesystem path to share on that volume"
                    raise Exception(t.format(vp))

                cat = ln
                if not subsection:
                    ap = vp = None
                    self.indent = ""
                else:
                    self.indent = "  "

                if ln == catg:
                    t = "begin commandline-arguments (anything from --help; dashes are optional)"
                    self._l(ln, 6, t)
                elif ln == cata:
                    self._l(ln, 5, "begin user-accounts section")
                elif ln == catgrp:
                    self._l(ln, 5, "begin user-groups section")
                elif ln.startswith("[/"):
                    vp = ln[1:-1].strip("/")
                    self._l(ln, 2, "define volume at URL [/{}]".format(vp))
                elif subsection:
                    if ln == catx:
                        self._l(ln, 5, "volume access config:")
                    else:
                        t = "volume-specific config (anything from --help-flags)"
                        self._l(ln, 6, t)
                else:
                    raise Exception("invalid section header" + SBADCFG)

                self.indent = "    " if subsection else "  "
                continue

            if cat == catg:
                self._l(ln, 6, "")
                zt = split_cfg_ln(ln)
                for zs, za in zt.items():
                    zs = zs.lstrip("-")
                    if "=" in zs:
                        t = "WARNING: found an option named [%s] in your [global] config; did you mean to say [%s: %s] instead?"
                        zs1, zs2 = zs.split("=", 1)
                        self.log(t % (zs, zs1, zs2), 3)
                    if za is True:
                        self._e("└─argument [{}]".format(zs))
                    else:
                        self._e("└─argument [{}] with value [{}]".format(zs, za))
                continue

            if cat == cata:
                try:
                    u, p = [zs.strip() for zs in ln.split(":", 1)]
                    if "=" in u and not p:
                        t = "WARNING: found username [%s] in your [accounts] config; did you mean to say [%s: %s] instead?"
                        zs1, zs2 = u.split("=", 1)
                        self.log(t % (u, zs1, zs2), 3)
                    self._l(ln, 5, "account [{}], password [{}]".format(u, p))
                    acct[u] = p
                except:
                    t = 'lines inside the [accounts] section must be "username: password"'
                    raise Exception(t + SBADCFG)
                continue

            if cat == catgrp:
                try:
                    gn, zs1 = [zs.strip() for zs in ln.split(":", 1)]
                    uns = [zs.strip() for zs in zs1.split(",")]
                    t = "group [%s] = " % (gn,)
                    t += ", ".join("user [%s]" % (x,) for x in uns)
                    self._l(ln, 5, t)
                    grps[gn] = uns
                except:
                    t = 'lines inside the [groups] section must be "groupname: user1, user2, user..."'
                    raise Exception(t + SBADCFG)
                continue

            if vp is not None and ap is None:
                if npass != 2:
                    continue

                ap = ln
                self._l(ln, 2, "bound to filesystem-path [{}]".format(ap))
                vols = self._map_volume_idp(ap, vp, mount, daxs, mflags, all_un_gn)
                if not vols:
                    ap = vp = None
                    self._l(ln, 2, "└─no users/groups known; was not mapped")
                elif len(vols) > 1:
                    for vol in vols:
                        self._l(ln, 2, "└─mapping: [%s] => [%s]" % (vol[1], vol[0]))
                continue

            if cat == catx:
                if npass != 2 or not ap:
                    # not stage2, or unmapped ${u}/${g}
                    continue

                err = ""
                try:
                    self._l(ln, 5, "volume access config:")
                    sk, sv = ln.split(":")
                    if re.sub("[rwmdgGhaA.]", "", sk) or not sk:
                        err = "invalid accs permissions list; "
                        raise Exception(err)
                    if " " in re.sub(", *", "", sv).strip():
                        err = "list of users is not comma-separated; "
                        raise Exception(err)
                    sv = sv.replace(" ", "")
                    self._read_vol_str_idp(sk, sv, vols, all_un_gn, daxs, mflags)
                    continue
                except CfgEx:
                    raise
                except:
                    err += "accs entries must be 'rwmdgGhaA.: user1, user2, ...'"
                    raise CfgEx(err + SBADCFG)

            if cat == catf:
                if npass != 2 or not ap:
                    # not stage2, or unmapped ${u}/${g}
                    continue

                err = ""
                try:
                    self._l(ln, 6, "volume-specific config:")
                    zd = split_cfg_ln(ln)
                    fstr = ""
                    for sk, sv in zd.items():
                        if "=" in sk:
                            t = "WARNING: found a volflag named [%s] in your config; did you mean to say [%s: %s] instead?"
                            zs1, zs2 = sk.split("=", 1)
                            self.log(t % (sk, zs1, zs2), 3)
                        bad = re.sub(r"[a-z0-9_-]", "", sk).lstrip("-")
                        if bad:
                            err = "bad characters [{}] in volflag name [{}]; "
                            err = err.format(bad, sk)
                            raise Exception(err + SBADCFG)
                        if sv is True:
                            fstr += "," + sk
                        else:
                            fstr += ",{}={}".format(sk, sv)
                            assert vp is not None
                            self._read_vol_str_idp(
                                "c", fstr[1:], vols, all_un_gn, daxs, mflags
                            )
                            fstr = ""
                    if fstr:
                        self._read_vol_str_idp(
                            "c", fstr[1:], vols, all_un_gn, daxs, mflags
                        )
                    continue
                except:
                    err += "flags entries (volflags) must be one of the following:\n  'flag1, flag2, ...'\n  'key: value'\n  'flag1, flag2, key: value'"
                    raise Exception(err + SBADCFG)

            raise Exception("unprocessable line in config" + SBADCFG)

        self._e()
        self.line_ctr = 0

    def _read_vol_str_idp(
        self,
        lvl ,
        uname ,
        vols    ,
        un_gns  ,
        axs  ,
        flags   ,
    )  :
        if lvl.strip("crwmdgGhaA."):
            t = "%s,%s" % (lvl, uname) if uname else lvl
            raise CfgEx("invalid config value (volume or volflag): %s" % (t,))

        if lvl == "c":
            # here, 'uname' is not a username; it is a volflag name... sorry
            cval   = True
            try:
                # volflag with arguments, possibly with a preceding list of bools
                uname, cval = uname.split("=", 1)
            except:
                # just one or more bools
                pass

            while "," in uname:
                # one or more bools before the final flag; eat them
                n1, uname = uname.split(",", 1)
                for _, vp, _, _ in vols:
                    self._read_volflag(vp, flags[vp], n1, True, False)

            for _, vp, _, _ in vols:
                self._read_volflag(vp, flags[vp], uname, cval, False)

            return

        if uname == "":
            uname = "*"

        unames = []
        for un in uname.replace(",", " ").strip().split():
            if un.startswith("@"):
                grp = un[1:]
                uns = [x[0] for x in un_gns.items() if grp in x[1]]
                if grp == "${g}":
                    unames.append(un)
                elif not uns and not self.args.idp_h_grp:
                    t = "group [%s] must be defined with --grp argument (or in a [groups] config section)"
                    raise CfgEx(t % (grp,))

                unames.extend(uns)
            else:
                unames.append(un)

        # unames may still contain ${u} and ${g} so now expand those;
        un_gn = [(un, gn) for un, gns in un_gns.items() for gn in gns]

        for src, dst, vu, vg in vols:
            unames2 = set(unames)

            if "${u}" in unames:
                if not vu:
                    t = "cannot use ${u} in accs of volume [%s] because the volume url does not contain ${u}"
                    raise CfgEx(t % (src,))
                unames2.add(vu)

            if "@${g}" in unames:
                if not vg:
                    t = "cannot use @${g} in accs of volume [%s] because the volume url does not contain @${g}"
                    raise CfgEx(t % (src,))
                unames2.update([un for un, gn in un_gn if gn == vg])

            if "${g}" in unames:
                t = 'the accs of volume [%s] contains "${g}" but the only supported way of specifying that is "@${g}"'
                raise CfgEx(t % (src,))

            unames2.discard("${u}")
            unames2.discard("@${g}")

            self._read_vol_str(lvl, list(unames2), axs[dst])

    def _read_vol_str(self, lvl , unames , axs )  :
        junkset = set()
        for un in unames:
            for alias, mapping in [
                ("h", "gh"),
                ("G", "gG"),
                ("A", "rwmda.A"),
            ]:
                expanded = ""
                for ch in mapping:
                    if ch not in lvl:
                        expanded += ch
                    lvl = lvl.replace(alias, expanded + alias)

            for ch, al in [
                ("r", axs.uread),
                ("w", axs.uwrite),
                ("m", axs.umove),
                ("d", axs.udel),
                (".", axs.udot),
                ("a", axs.uadmin),
                ("A", junkset),
                ("g", axs.uget),
                ("G", axs.upget),
                ("h", axs.uhtml),
            ]:
                if ch in lvl:
                    if un == "*":
                        t = "└─add permission [{0}] for [everyone] -- {2}"
                    else:
                        t = "└─add permission [{0}] for user [{1}] -- {2}"

                    desc = permdescs.get(ch, "?")
                    self._e(t.format(ch, un, desc))
                    al.add(un)

    def _read_volflag(
        self,
        vpath ,
        flags  ,
        name ,
        value   ,
        is_list ,
    )  :
        if name not in flagdescs:
            name = name.lower()

            # volflags are snake_case, but a leading dash is the removal operator
            stripped = name.lstrip("-")
            zi = len(name) - len(stripped)
            if zi > 1:
                t = "WARNING: the config for volume [/%s] specified a volflag with multiple leading hyphens (%s); use one hyphen to remove, or zero hyphens to add a flag. Will now enable flag [%s]"
                self.log(t % (vpath, name, stripped), 3)
                name = stripped
                zi = 0

            if stripped not in flagdescs and "-" in stripped:
                name = ("-" * zi) + stripped.replace("-", "_")

        desc = flagdescs.get(name.lstrip("-"), "?").replace("\n", " ")

        if not name:
            self._e("└─unreadable-line")
            t = "WARNING: the config for volume [/%s] indicated that a volflag was to be defined, but the volflag name was blank"
            self.log(t % (vpath,), 3)
            return

        if re.match("^-[^-]+$", name):
            t = "└─unset volflag [{}]  ({})"
            self._e(t.format(name[1:], desc))
            flags[name] = True
            return

        zs = "ext_th landmark mtp on403 on404 xbu xau xiu xbc xac xbr xar xbd xad xm xban"
        if name not in zs.split():
            if value is True:
                t = "└─add volflag [{}] = {}  ({})"
            else:
                t = "└─add volflag [{}] = [{}]  ({})"
            self._e(t.format(name, value, desc))
            flags[name] = value
            return

        vals = flags.get(name, [])
        if not value:
            return
        elif is_list:
            vals += value
        else:
            vals += [value]

        flags[name] = vals
        self._e("volflag [{}] += {}  ({})".format(name, vals, desc))

    def reload(self, verbosity  = 9)  :
        """
        construct a flat list of mountpoints and usernames
        first from the commandline arguments
        then supplementing with config files
        before finally building the VFS
        """
        with self.mutex:
            self._reload(verbosity)

    def _reload(self, verbosity  = 9)  :
        acct   = {}  # username:password
        grps   = {}  # groupname:usernames
        daxs   = {}
        mflags    = {}  # vpath:flags
        mount    = {}  # dst:src (vp:(ap,vp0))
        cfg_files_loaded  = []

        self.idp_vols = {}  # yolo
        self.badcfg1 = False

        if self.args.a:
            # list of username:password
            for x in self.args.a:
                try:
                    u, p = x.split(":", 1)
                    acct[u] = p
                except:
                    t = '\n  invalid value "{}" for argument -a, must be username:password'
                    raise Exception(t.format(x))

        if self.args.grp:
            # list of groupname:username,username,...
            for x in self.args.grp:
                try:
                    # accept both = and : as separator between groupname and usernames,
                    # accept both , and : as separators between usernames
                    zs1, zs2 = x.replace("=", ":").split(":", 1)
                    grps[zs1] = zs2.replace(":", ",").split(",")
                    grps[zs1] = [x.strip() for x in grps[zs1]]
                except:
                    t = '\n  invalid value "{}" for argument --grp, must be groupname:username1,username2,...'
                    raise Exception(t.format(x))

        if self.args.v:
            # list of src:dst:permset:permset:...
            # permset is <rwmdgGhaA.>[,username][,username] or <c>,<flag>[=args]
            all_un_gn = self._all_un_gn(acct, grps)
            for v_str in self.args.v:
                m = re_vol.match(v_str)
                if not m:
                    raise Exception("invalid -v argument: [{}]".format(v_str))

                src, dst, perms = m.groups()
                if WINDOWS:
                    src = uncyg(src)

                vols = self._map_volume_idp(src, dst, mount, daxs, mflags, all_un_gn)

                for x in perms.split(":"):
                    lvl, uname = x.split(",", 1) if "," in x else [x, ""]
                    self._read_vol_str_idp(lvl, uname, vols, all_un_gn, daxs, mflags)

        if self.args.c:
            for cfg_fn in self.args.c:
                lns  = []
                try:
                    self._parse_config_file(
                        cfg_fn, lns, acct, grps, daxs, mflags, mount
                    )

                    zs = "#\033[36m cfg files in "
                    zst = [x[len(zs) :] for x in lns if x.startswith(zs)]
                    for zs in list(set(zst)):
                        self.log("discovered config files in " + zs, 6)

                    zs = "#\033[36m opening cfg file"
                    zstt = [x.split(" -> ") for x in lns if x.startswith(zs)]
                    zst = [(max(0, len(x) - 2) * " ") + "└" + x[-1] for x in zstt]
                    t = "loaded {} config files:\n{}"
                    self.log(t.format(len(zst), "\n".join(zst)))
                    cfg_files_loaded = zst

                except:
                    lns = lns[: self.line_ctr]
                    slns = ["{:4}: {}".format(n, s) for n, s in enumerate(lns, 1)]
                    t = "\033[1;31m\nerror @ line {}, included from {}\033[0m"
                    t = t.format(self.line_ctr, cfg_fn)
                    self.log("\n{0}\n{1}{0}".format(t, "\n".join(slns)))
                    raise

        derive_args(self.args)
        self.setup_auth_ord()

        self.setup_pwhash(acct)
        defpw = acct.copy()
        self.setup_chpw(acct)

        # case-insensitive; normalize
        if WINDOWS:
            cased = {}
            for vp, (ap, vp0) in mount.items():
                cased[vp] = (absreal(ap), vp0)

            mount = cased

        if not mount and not self.args.have_idp_hdrs:
            # -h says our defaults are CWD at root and read/write for everyone
            axs = AXS(["*"], ["*"], None, None)
            ehint = ""
            if self.is_lxc:
                t = "Read-access has been disabled due to failsafe: Docker detected, but %s. This failsafe is to prevent unintended access if this is due to accidental loss of config. You can override this safeguard and allow read/write to all of /w/ by adding the following arguments to the docker container:  -v .::rw"
                if len(cfg_files_loaded) == 1:
                    self.log(t % ("no config-file was provided",), 1)
                    t = "it is strongly recommended to add a config-file instead, for example based on https://github.com/9001/copyparty/blob/hovudstraum/docs/examples/docker/basic-docker-compose/copyparty.conf"
                    self.log(t, 3)
                else:
                    self.log(t % ("the config does not define any volumes",), 1)
                axs = AXS()
                ehint = "; please try moving them up one level, into the parent folder:"
            elif self.args.c:
                t = "Read-access has been disabled due to failsafe: No volumes were defined by the config-file. This failsafe is to prevent unintended access if this is due to accidental loss of config. You can override this safeguard and allow read/write to the working-directory by adding the following arguments:  -v .::rw"
                self.log(t, 1)
                axs = AXS()
                ehint = ":"
            if ehint:
                try:
                    files = os.listdir(E.cfg)
                except:
                    files = []
                hits = [
                    x
                    for x in files
                    if x.lower().endswith(".conf") and not x.startswith(".")
                ]
                if hits:
                    t = "Hint: Found some config files in [%s], but these were not automatically loaded because they are in the wrong place%s %s\n"
                    self.log(t % (E.cfg, ehint, ", ".join(hits)), 3)
            vfs = VFS(self.log_func, absreal("."), "", "", axs, self.vf0b())
            if not axs.uread:
                self.badcfg1 = True
        elif "" not in mount:
            # there's volumes but no root; make root inaccessible
            vfs = VFS(self.log_func, "", "", "", AXS(), self.vf0())

        maxdepth = 0
        for dst in sorted(mount.keys(), key=lambda x: (x.count("/"), len(x))):
            depth = dst.count("/")
            assert maxdepth <= depth  # nosec
            maxdepth = depth
            src, dst0 = mount[dst]

            if dst == "":
                # rootfs was mapped; fully replaces the default CWD vfs
                vfs = VFS(self.log_func, src, dst, dst0, daxs[dst], mflags[dst])
                continue

            assert vfs  # type: ignore
            zv = vfs.add(src, dst, dst0)
            zv.axs = daxs[dst]
            zv.flags = mflags[dst]
            zv.dbv = None

        assert vfs  # type: ignore
        vfs.all_vols = {}
        vfs.all_nodes = {}
        vfs.all_aps = []
        vfs.all_vps = []
        vfs.get_all_vols(vfs.all_vols, vfs.all_nodes, vfs.all_aps, vfs.all_vps)
        for vol in vfs.all_nodes.values():
            vol.all_aps.sort(key=lambda x: len(x[0]), reverse=True)
            vol.all_vps.sort(key=lambda x: len(x[0]), reverse=True)
            vol.root = vfs

        zs = "neversymlink du_iwho"
        k_ign = set(zs.split())
        for vol in vfs.all_vols.values():
            unknown_flags = set()
            for k, v in vol.flags.items():
                ks = k.lstrip("-")
                if ks not in flagdescs and ks not in k_ign:
                    unknown_flags.add(k)
            if unknown_flags:
                t = "WARNING: the config for volume [/%s] has unrecognized volflags; will ignore: '%s'"
                self.log(t % (vol.vpath, "', '".join(unknown_flags)), 3)

        enshare = self.args.shr
        shr = enshare[1:-1]
        shrs = enshare[1:]
        if enshare:

            shv = VFS(self.log_func, "", shr, shr, AXS(), self.vf0())

            db_path = self.args.shr_db
            db = sqlite3.connect(db_path)
            cur = db.cursor()
            cur2 = db.cursor()
            now = time.time()
            for row in cur.execute("select * from sh"):
                s_k, s_pw, s_vp, s_pr, s_nf, s_un, s_t0, s_t1 = row
                if s_t1 and s_t1 < now:
                    continue

                if self.args.shr_v:
                    t = "loading %s share %r by %r => %r"
                    self.log(t % (s_pr, s_k, s_un, s_vp))

                if s_pw:
                    # gotta reuse the "account" for all shares with this pw,
                    # so do a light scramble as this appears in the web-ui
                    zb = hashlib.sha512(s_pw.encode("utf-8")).digest()
                    sun = "s_%s" % (ub64enc(zb)[4:16].decode("ascii"),)
                    acct[sun] = s_pw
                else:
                    sun = "*"

                s_axs = AXS(
                    [sun] if "r" in s_pr else [],
                    [sun] if "w" in s_pr else [],
                    [sun] if "m" in s_pr else [],
                    [sun] if "d" in s_pr else [],
                )

                # don't know the abspath yet + wanna ensure the user
                # still has the privs they granted, so nullmap it
                vp = "%s/%s" % (shr, s_k)
                shv.nodes[s_k] = VFS(self.log_func, "", vp, vp, s_axs, shv.flags.copy())

            vfs.nodes[shr] = vfs.all_vols[shr] = shv
            for vol in shv.nodes.values():
                vfs.all_vols[vol.vpath] = vfs.all_nodes[vol.vpath] = vol
                vol.get_dbv = vol._get_share_src
                vol.ls = vol._ls_nope

        zss = set(acct)
        zss.update(self.idp_accs)
        zss.discard("*")
        unames = ["*"] + list(sorted(zss))

        for perm in "read write move del get pget html admin dot".split():
            axs_key = "u" + perm
            for vp, vol in vfs.all_vols.items():
                zx = getattr(vol.axs, axs_key)
                if "*" in zx and "-@acct" not in zx:
                    for usr in unames:
                        zx.add(usr)
                for zs in list(zx):
                    if zs.startswith("-"):
                        zx.discard(zs)
                        zs = zs[1:]
                        zx.discard(zs)
                        if zs.startswith("@"):
                            zs = zs[1:]
                            for zs in grps.get(zs) or []:
                                zx.discard(zs)

            # aread,... = dict[uname, list[volnames] or []]
            umap   = {x: [] for x in unames}
            for usr in unames:
                for vp, vol in vfs.all_vols.items():
                    zx = getattr(vol.axs, axs_key)
                    if usr in zx and (not enshare or not vp.startswith(shrs)):
                        umap[usr].append(vp)
                umap[usr].sort()
            setattr(vfs, "a" + perm, umap)

        all_users = {}
        missing_users = {}
        associated_users = {}
        for axs in daxs.values():
            for d in [
                axs.uread,
                axs.uwrite,
                axs.umove,
                axs.udel,
                axs.uget,
                axs.upget,
                axs.uhtml,
                axs.uadmin,
                axs.udot,
            ]:
                for usr in d:
                    all_users[usr] = 1
                    if usr != "*" and usr not in acct and usr not in self.idp_accs:
                        missing_users[usr] = 1
                    if "*" not in d:
                        associated_users[usr] = 1

        if missing_users:
            zs = ", ".join(k for k in sorted(missing_users))
            if self.args.have_idp_hdrs:
                t = "the following users are unknown, and assumed to come from IdP: "
                self.log(t + zs, c=6)
            else:
                t = "you must -a the following users: "
                self.log(t + zs, c=1)
                raise Exception(BAD_CFG)

        if LEELOO_DALLAS in all_users:
            raise Exception("sorry, reserved username: " + LEELOO_DALLAS)

        zsl = []
        for usr in list(acct)[:]:
            zs = acct[usr].strip()
            if not zs:
                zs = ub64enc(os.urandom(48)).decode("ascii")
                zsl.append(usr)
            acct[usr] = zs
        if zsl:
            self.log("generated random passwords for users %r" % (zsl,), 6)

        seenpwds = {}
        for usr, pwd in acct.items():
            if pwd in seenpwds:
                t = "accounts [{}] and [{}] have the same password; this is not supported"
                self.log(t.format(seenpwds[pwd], usr), 1)
                raise Exception(BAD_CFG)
            seenpwds[pwd] = usr

        for usr in acct:
            if usr not in associated_users:
                if enshare and usr.startswith("s_"):
                    continue
                if len(vfs.all_vols) > 1:
                    # user probably familiar enough that the verbose message is not necessary
                    t = "account [%s] is not mentioned in any volume definitions; see --help-accounts"
                    self.log(t % (usr,), 1)
                else:
                    t = "WARNING: the account [%s] is not mentioned in any volume definitions and thus has the same access-level and privileges that guests have; please see --help-accounts for details.  For example, if you intended to give that user full access to the current directory, you could do this:  -v .::A,%s"
                    self.log(t % (usr, usr), 1)

        promote = []
        demote = []
        for vol in vfs.all_vols.values():
            if not vol.realpath:
                continue
            hid = self.hid_cache.get(vol.realpath)
            if not hid:
                zb = hashlib.sha512(afsenc(vol.realpath)).digest()
                hid = base64.b32encode(zb).decode("ascii").lower()
                self.hid_cache[vol.realpath] = hid

            vflag = vol.flags.get("hist")
            if vflag == "-":
                pass
            elif vflag:
                vflag = os.path.expandvars(os.path.expanduser(vflag))
                vol.histpath = vol.dbpath = uncyg(vflag) if WINDOWS else vflag
            elif self.args.hist:
                for nch in range(len(hid)):
                    hpath = os.path.join(self.args.hist, hid[: nch + 1])
                    bos.makedirs(hpath)

                    powner = os.path.join(hpath, "owner.txt")
                    try:
                        with open(powner, "rb") as f:
                            owner = f.read().rstrip()
                    except:
                        owner = None

                    me = afsenc(vol.realpath).rstrip()
                    if owner not in [None, me]:
                        continue

                    if owner is None:
                        with open(powner, "wb") as f:
                            f.write(me)

                    vol.histpath = vol.dbpath = hpath
                    break

            vol.histpath = absreal(vol.histpath)

        for vol in vfs.all_vols.values():
            if not vol.realpath:
                continue
            hid = self.hid_cache[vol.realpath]
            vflag = vol.flags.get("dbpath")
            if vflag == "-":
                pass
            elif vflag:
                vflag = os.path.expandvars(os.path.expanduser(vflag))
                vol.dbpath = uncyg(vflag) if WINDOWS else vflag
            elif self.args.dbpath:
                for nch in range(len(hid)):
                    hpath = os.path.join(self.args.dbpath, hid[: nch + 1])
                    bos.makedirs(hpath)

                    powner = os.path.join(hpath, "owner.txt")
                    try:
                        with open(powner, "rb") as f:
                            owner = f.read().rstrip()
                    except:
                        owner = None

                    me = afsenc(vol.realpath).rstrip()
                    if owner not in [None, me]:
                        continue

                    if owner is None:
                        with open(powner, "wb") as f:
                            f.write(me)

                    vol.dbpath = hpath
                    break

            vol.dbpath = absreal(vol.dbpath)
            if vol.dbv:
                if bos.path.exists(os.path.join(vol.dbpath, "up2k.db")):
                    promote.append(vol)
                    vol.dbv = None
                else:
                    demote.append(vol)

        # discard jump-vols
        for zv in demote:
            vfs.all_vols.pop(zv.vpath)

        if promote:
            ta = [
                "\n  the following jump-volumes were generated to assist the vfs.\n  As they contain a database (probably from v0.11.11 or older),\n  they are promoted to full volumes:"
            ]
            for vol in promote:
                ta.append("  /%s  (%s)  (%s)" % (vol.vpath, vol.realpath, vol.dbpath))

            self.log("\n\n".join(ta) + "\n", c=3)

        rhisttab = {}
        vfs.histtab = {}
        for zv in vfs.all_vols.values():
            histp = zv.histpath
            is_shr = shr and zv.vpath.split("/")[0] == shr
            if histp and not is_shr and histp in rhisttab:
                zv2 = rhisttab[histp]
                t = "invalid config; multiple volumes share the same histpath (database+thumbnails location):\n  histpath: %s\n  volume 1: /%s  [%s]\n  volume 2: /%s  [%s]"
                t = t % (histp, zv2.vpath, zv2.realpath, zv.vpath, zv.realpath)
                self.log(t, 1)
                raise Exception(t)
            rhisttab[histp] = zv
            vfs.histtab[zv.realpath] = histp

        rdbpaths = {}
        vfs.dbpaths = {}
        for zv in vfs.all_vols.values():
            dbp = zv.dbpath
            is_shr = shr and zv.vpath.split("/")[0] == shr
            if dbp and not is_shr and dbp in rdbpaths:
                zv2 = rdbpaths[dbp]
                t = "invalid config; multiple volumes share the same dbpath (database location):\n  dbpath: %s\n  volume 1: /%s  [%s]\n  volume 2: /%s  [%s]"
                t = t % (dbp, zv2.vpath, zv2.realpath, zv.vpath, zv.realpath)
                self.log(t, 1)
                raise Exception(t)
            rdbpaths[dbp] = zv
            vfs.dbpaths[zv.realpath] = dbp

        for vol in vfs.all_vols.values():
            use = False
            for k in ["zipmaxn", "zipmaxs"]:
                try:
                    zs = vol.flags[k]
                except:
                    zs = getattr(self.args, k)
                if zs in ("", "0"):
                    vol.flags[k] = 0
                    continue

                zf = unhumanize(zs)
                vol.flags[k + "_v"] = zf
                if zf:
                    use = True
            if use:
                vol.flags["zipmax"] = True

        for vol in vfs.all_vols.values():
            lim = Lim(self.log_func)
            use = False

            if vol.flags.get("nosub"):
                use = True
                lim.nosub = True

            zs = vol.flags.get("df") or self.args.df or ""
            if zs not in ("", "0"):
                use = True
                try:
                    _ = float(zs)
                    zs = "%sg" % (zs,)
                except:
                    pass
                lim.dfl = unhumanize(zs)

            zs = vol.flags.get("sz")
            if zs:
                use = True
                lim.smin, lim.smax = [unhumanize(x) for x in zs.split("-")]

            zs = vol.flags.get("rotn")
            if zs:
                use = True
                lim.rotn, lim.rotl = [int(x) for x in zs.split(",")]

            zs = vol.flags.get("rotf")
            if zs:
                use = True
                lim.set_rotf(zs, vol.flags.get("rotf_tz") or "UTC")

            zs = vol.flags.get("maxn")
            if zs:
                use = True
                lim.nmax, lim.nwin = [int(x) for x in zs.split(",")]

            zs = vol.flags.get("maxb")
            if zs:
                use = True
                lim.bmax, lim.bwin = [unhumanize(x) for x in zs.split(",")]

            zs = vol.flags.get("vmaxb")
            if zs:
                use = True
                lim.vbmax = unhumanize(zs)

            zs = vol.flags.get("vmaxn")
            if zs:
                use = True
                lim.vnmax = unhumanize(zs)

            if use:
                vol.lim = lim

        if self.args.no_robots:
            for vol in vfs.all_nodes.values():
                # volflag "robots" overrides global "norobots", allowing indexing by search engines for this vol
                if not vol.flags.get("robots"):
                    vol.flags["norobots"] = True

        for vol in vfs.all_nodes.values():
            if self.args.no_vthumb:
                vol.flags["dvthumb"] = True
            if self.args.no_athumb:
                vol.flags["dathumb"] = True
            if self.args.no_thumb or vol.flags.get("dthumb", False):
                vol.flags["dthumb"] = True
                vol.flags["dvthumb"] = True
                vol.flags["dathumb"] = True
                vol.flags["dithumb"] = True

        have_fk = False
        for vol in vfs.all_nodes.values():
            fk = vol.flags.get("fk")
            fka = vol.flags.get("fka")
            if fka and not fk:
                fk = fka
            if fk:
                fk = 8 if fk is True else int(fk)
                if fk > 72:
                    t = "max filekey-length is 72; volume /%s specified %d (anything higher than 16 is pointless btw)"
                    raise Exception(t % (vol.vpath, fk))
                vol.flags["fk"] = fk
                have_fk = True

            dk = vol.flags.get("dk")
            dks = vol.flags.get("dks")
            dky = vol.flags.get("dky")
            if dks is not None and dky is not None:
                t = "WARNING: volume /%s has both dks and dky enabled; this is too yolo and not permitted"
                raise Exception(t % (vol.vpath,))

            if dks and not dk:
                dk = dks
            if dky and not dk:
                dk = dky
            if dk:
                vol.flags["dk"] = int(dk) if dk is not True else 8

        if have_fk and re.match(r"^[0-9\.]+$", self.args.fk_salt):
            self.log("filekey salt: {}".format(self.args.fk_salt))

        fk_len = len(self.args.fk_salt)
        if have_fk and fk_len < 14:
            t = "WARNING: filekeys are enabled, but the salt is only %d chars long; %d or longer is recommended. Either specify a stronger salt using --fk-salt or delete this file and restart copyparty: %s"
            zs = os.path.join(E.cfg, "fk-salt.txt")
            self.log(t % (fk_len, 16, zs), 3)

        for vol in vfs.all_nodes.values():
            if "pk" in vol.flags and "gz" not in vol.flags and "xz" not in vol.flags:
                vol.flags["gz"] = False  # def.pk

            if "scan" in vol.flags:
                vol.flags["scan"] = int(vol.flags["scan"])
            elif self.args.re_maxage:
                vol.flags["scan"] = self.args.re_maxage

        self.args.have_unlistc = False

        all_mte = {}
        errors = False
        free_umask = False
        have_reflink = False
        for vol in vfs.all_nodes.values():
            if (self.args.e2ds and vol.axs.uwrite) or self.args.e2dsa:
                vol.flags["e2ds"] = True

            if self.args.e2d or "e2ds" in vol.flags:
                vol.flags["e2d"] = True

            for ga, vf in [
                ["no_hash", "nohash"],
                ["no_idx", "noidx"],
                ["og_ua", "og_ua"],
                ["srch_excl", "srch_excl"],
            ]:
                if vf in vol.flags:
                    ptn = re.compile(vol.flags.pop(vf))
                else:
                    ptn = getattr(self.args, ga)

                if ptn:
                    vol.flags[vf] = ptn

            for ga, vf in vf_bmap().items():
                if getattr(self.args, ga):
                    vol.flags[vf] = True

            for ve, vd in (
                ("nodotsrch", "dotsrch"),
                ("sb_lg", "no_sb_lg"),
                ("sb_md", "no_sb_md"),
            ):
                if ve in vol.flags:
                    vol.flags.pop(vd, None)

            for ga, vf in vf_vmap().items():
                if vf not in vol.flags:
                    vol.flags[vf] = getattr(self.args, ga)

            zs = "forget_ip gid nrand tail_who th_spec_p u2abort u2ow uid unp_who ups_who zip_who"
            for k in zs.split():
                if k in vol.flags:
                    vol.flags[k] = int(vol.flags[k])

            zs = "aconvt convt tail_fd tail_rate tail_tmax"
            for k in zs.split():
                if k in vol.flags:
                    vol.flags[k] = float(vol.flags[k])

            for k in ("mv_re", "rm_re"):
                try:
                    zs1, zs2 = vol.flags[k + "try"].split("/")
                    vol.flags[k + "_t"] = float(zs1)
                    vol.flags[k + "_r"] = float(zs2)
                except:
                    t = 'volume "/%s" has invalid %stry [%s]'
                    raise Exception(t % (vol.vpath, k, vol.flags.get(k + "try")))

            for k in ("chmod_d", "chmod_f"):
                is_d = k == "chmod_d"
                zs = vol.flags.get(k, "")
                if not zs and is_d:
                    zs = "755"
                if not zs:
                    vol.flags.pop(k, None)
                    continue
                if not re.match("^[0-7]{3}$", zs):
                    t = "config-option '%s' must be a three-digit octal value such as [755] or [644] but the value was [%s]"
                    t = t % (k, zs)
                    self.log(t, 1)
                    raise Exception(t)
                zi = int(zs, 8)
                vol.flags[k] = zi
                if (is_d and zi != 0o755) or not is_d:
                    free_umask = True

            vol.flags.pop("chown", None)
            if vol.flags["uid"] != -1 or vol.flags["gid"] != -1:
                vol.flags["chown"] = True
            vol.flags.pop("fperms", None)
            if "chown" in vol.flags or vol.flags.get("chmod_f"):
                vol.flags["fperms"] = True
            if vol.lim:
                vol.lim.chmod_d = vol.flags["chmod_d"]
                vol.lim.chown = "chown" in vol.flags
                vol.lim.uid = vol.flags["uid"]
                vol.lim.gid = vol.flags["gid"]

            vol.flags["du_iwho"] = n_du_who(vol.flags["du_who"])

            if not enshare:
                vol.flags["shr_who"] = self.args.shr_who = "no"

            if vol.flags.get("og"):
                self.args.uqe = True

            if "unlistcr" in vol.flags or "unlistcw" in vol.flags:
                self.args.have_unlistc = True

            if "reflink" in vol.flags:
                have_reflink = True

            zs = str(vol.flags.get("tcolor", "")).lstrip("#")
            if len(zs) == 3:  # fc5 => ffcc55
                vol.flags["tcolor"] = "".join([x * 2 for x in zs])

            # volflag syntax currently doesn't allow for ':' in value
            zs = vol.flags["put_name"]
            vol.flags["put_name2"] = zs.replace("{now.", "{now:.")

            if vol.flags.get("neversymlink"):
                vol.flags["hardlinkonly"] = True  # was renamed
            if vol.flags.get("hardlinkonly"):
                vol.flags["hardlink"] = True

            for k1, k2 in IMPLICATIONS:
                if k1 in vol.flags:
                    vol.flags[k2] = True

            for k1, k2 in UNPLICATIONS:
                if k1 in vol.flags:
                    vol.flags[k2] = False

            dbds = "acid|swal|wal|yolo"
            vol.flags["dbd"] = dbd = vol.flags.get("dbd") or self.args.dbd
            if dbd not in dbds.split("|"):
                t = 'volume "/%s" has invalid dbd [%s]; must be one of [%s]'
                raise Exception(t % (vol.vpath, dbd, dbds))

            # default tag cfgs if unset
            for k in ("mte", "mth", "exp_md", "exp_lg"):
                if k not in vol.flags:
                    vol.flags[k] = getattr(self.args, k).copy()
                else:
                    vol.flags[k] = odfusion(getattr(self.args, k), vol.flags[k])

            # append additive args from argv to volflags
            hooks = "xbu xau xiu xbc xac xbr xar xbd xad xm xban".split()
            for name in "ext_th mtp on404 on403".split() + hooks:
                self._read_volflag(
                    vol.vpath, vol.flags, name, getattr(self.args, name), True
                )

            for hn in hooks:
                cmds = vol.flags.get(hn)
                if not cmds:
                    continue

                ncmds = []
                for cmd in cmds:
                    hfs = []
                    ocmd = cmd
                    while "," in cmd[:6]:
                        zs, cmd = cmd.split(",", 1)
                        hfs.append(zs)

                    if "c" in hfs and "f" in hfs:
                        t = "cannot combine flags c and f; removing f from eventhook [{}]"
                        self.log(t.format(ocmd), 1)
                        hfs = [x for x in hfs if x != "f"]
                        ocmd = ",".join(hfs + [cmd])

                    if "c" not in hfs and "f" not in hfs and hn == "xban":
                        hfs = ["c"] + hfs
                        ocmd = ",".join(hfs + [cmd])

                    ncmds.append(ocmd)
                vol.flags[hn] = ncmds

            ext_th = vol.flags["ext_th_d"] = {}
            etv = "(?)"
            try:
                for etv in vol.flags.get("ext_th") or []:
                    k, v = etv.split("=")
                    ext_th[k] = v
            except:
                t = "WARNING: volume [/%s]: invalid value specified for ext-th: %s"
                self.log(t % (vol.vpath, etv), 3)

            zs = str(vol.flags.get("html_head") or "")
            if zs and zs[:1] in "%@":
                vol.flags["html_head_d"] = zs
                head_s = str(vol.flags.get("html_head_s") or "")
            else:
                zs2 = str(vol.flags.get("html_head_s") or "")
                if zs2 and zs:
                    head_s = "%s\n%s\n" % (zs2.strip(), zs.strip())
                else:
                    head_s = zs2 or zs

            if head_s and not head_s.endswith("\n"):
                head_s += "\n"

            if "norobots" in vol.flags:
                head_s += META_NOBOTS

            ico_url = vol.flags.get("ufavico")
            if ico_url:
                ico_h = ""
                ico_ext = ico_url.split("?")[0].split(".")[-1].lower()
                if ico_ext in FAVICON_MIMES:
                    zs = '<link rel="icon" type="%s" href="%s">\n'
                    ico_h = zs % (FAVICON_MIMES[ico_ext], ico_url)
                elif ico_ext == "ico":
                    zs = '<link rel="shortcut icon" href="%s">\n'
                    ico_h = zs % (ico_url,)
                if ico_h:
                    vol.flags["ufavico_h"] = ico_h
                    head_s += ico_h

            if head_s:
                vol.flags["html_head_s"] = head_s
            else:
                vol.flags.pop("html_head_s", None)

            if not vol.flags.get("html_head_d"):
                vol.flags.pop("html_head_d", None)

            vol.check_landmarks()

            # d2d drops all database features for a volume
            for grp, rm in [["d2d", "e2d"], ["d2t", "e2t"], ["d2d", "e2v"]]:
                if not vol.flags.get(grp, False):
                    continue

                vol.flags["d2t"] = True
                vol.flags = {k: v for k, v in vol.flags.items() if not k.startswith(rm)}

            # d2ds drops all onboot scans for a volume
            for grp, rm in [["d2ds", "e2ds"], ["d2ts", "e2ts"]]:
                if not vol.flags.get(grp, False):
                    continue

                vol.flags["d2ts"] = True
                vol.flags = {k: v for k, v in vol.flags.items() if not k.startswith(rm)}

            # mt* needs e2t so drop those too
            for grp, rm in [["e2t", "mt"]]:
                if vol.flags.get(grp, False):
                    continue

                vol.flags = {
                    k: v
                    for k, v in vol.flags.items()
                    if not k.startswith(rm) or k == "mte"
                }

            for grp, rm in [["d2v", "e2v"]]:
                if not vol.flags.get(grp, False):
                    continue

                vol.flags = {k: v for k, v in vol.flags.items() if not k.startswith(rm)}

            ints = ["lifetime"]
            for k in list(vol.flags):
                if k in ints:
                    vol.flags[k] = int(vol.flags[k])

            if "e2d" not in vol.flags:
                if "lifetime" in vol.flags:
                    t = 'removing lifetime config from volume "/{}" because e2d is disabled'
                    self.log(t.format(vol.vpath), 1)
                    del vol.flags["lifetime"]

                needs_e2d = [x for x in hooks if x in ("xau", "xiu")]
                drop = [x for x in needs_e2d if vol.flags.get(x)]
                if drop:
                    t = 'removing [{}] from volume "/{}" because e2d is disabled'
                    self.log(t.format(", ".join(drop), vol.vpath), 1)
                    for x in drop:
                        vol.flags.pop(x)

            zi = vol.flags.get("lifetime") or 0
            zi2 = time.time() // (86400 * 365)
            zi3 = zi2 * 86400 * 365
            if zi < 0 or zi > zi3:
                t = "the lifetime of volume [/%s] (%d) exceeds max value (%d years; %d)"
                t = t % (vol.vpath, zi, zi2, zi3)
                self.log(t, 1)
                raise Exception(t)

            # verify tags mentioned by -mt[mp] are used by -mte
            local_mtp = {}
            local_only_mtp = {}
            tags = vol.flags.get("mtp", []) + vol.flags.get("mtm", [])
            tags = [x.split("=")[0] for x in tags]
            tags = [y for x in tags for y in x.split(",")]
            for a in tags:
                local_mtp[a] = True
                local = True
                for b in self.args.mtp or []:
                    b = b.split("=")[0]
                    if a == b:
                        local = False

                if local:
                    local_only_mtp[a] = True

            local_mte = ODict()
            for a in vol.flags.get("mte", {}).keys():
                local = True
                all_mte[a] = True
                local_mte[a] = True
                for b in self.args.mte.keys():
                    if not a or not b:
                        continue

                    if a == b:
                        local = False

            for mtp in local_only_mtp:
                if mtp not in local_mte:
                    t = 'volume "/{}" defines metadata tag "{}", but doesnt use it in "-mte" (or with "cmte" in its volflags)'
                    self.log(t.format(vol.vpath, mtp), 1)
                    errors = True

        for vol in vfs.all_nodes.values():
            if not vol.realpath or os.path.isfile(vol.realpath):
                continue
            ccs = vol.flags["casechk"][:1].lower()
            if ccs in ("y", "n"):
                if ccs == "y":
                    vol.flags["bcasechk"] = True
                continue
            try:
                bos.makedirs(vol.realpath, vf=vol.flags)
                files = os.listdir(vol.realpath)
                for fn in files:
                    fn2 = fn.lower()
                    if fn == fn2:
                        fn2 = fn.upper()
                    if fn == fn2 or fn2 in files:
                        continue
                    is_ci = os.path.exists(os.path.join(vol.realpath, fn2))
                    ccs = "y" if is_ci else "n"
                    break
                if ccs not in ("y", "n"):
                    ap = os.path.join(vol.realpath, "casechk")
                    open(ap, "wb").close()
                    ccs = "y" if os.path.exists(ap[:-1] + "K") else "n"
                    os.unlink(ap)
            except Exception as ex:
                if ANYWIN:
                    zs = "Windows"
                    ccs = "y"
                elif MACOS:
                    zs = "Macos"
                    ccs = "y"
                else:
                    zs = "Linux"
                    ccs = "n"
                t = "unable to determine if filesystem at %r is case-insensitive due to %r; assuming casechk=%s due to %s"
                self.log(t % (vol.realpath, ex, ccs, zs), 3)
            vol.flags["casechk"] = ccs
            if ccs == "y":
                vol.flags["bcasechk"] = True

        tags = self.args.mtp or []
        tags = [x.split("=")[0] for x in tags]
        tags = [y for x in tags for y in x.split(",")]
        for mtp in tags:
            if mtp not in all_mte:
                t = 'metadata tag "{}" is defined by "-mtm" or "-mtp", but is not used by "-mte" (or by any "cmte" volflag)'
                self.log(t.format(mtp), 1)
                errors = True

        for vol in vfs.all_vols.values():
            re1  = vol.flags.get("srch_excl")
            excl = [re1.pattern] if re1 else []

            vpaths = []
            vtop = vol.vpath
            for vp2 in vfs.all_vols.keys():
                if vp2.startswith((vtop + "/").lstrip("/")) and vtop != vp2:
                    vpaths.append(re.escape(vp2[len(vtop) :].lstrip("/")))
            if vpaths:
                excl.append("^(%s)/" % ("|".join(vpaths),))

            vol.flags["srch_re_dots"] = re.compile("|".join(excl or ["^$"]))
            excl.extend([r"^\.", r"/\."])
            vol.flags["srch_re_nodot"] = re.compile("|".join(excl))

        have_daw = False
        for vol in vfs.all_nodes.values():
            daw = vol.flags.get("daw") or self.args.daw
            if daw:
                vol.flags["daw"] = True
                have_daw = True

        if have_daw and self.args.no_dav:
            t = 'volume "/{}" has volflag "daw" (webdav write-access), but --no-dav is set'
            self.log(t, 1)
            errors = True

        if self.args.smb and self.ah.on and acct:
            self.log("--smb can only be used when --ah-alg is none", 1)
            errors = True

        for vol in vfs.all_nodes.values():
            for k in list(vol.flags.keys()):
                if re.match("^-[^-]+$", k):
                    vol.flags.pop(k)
                    zs = k[1:]
                    if zs in vol.flags:
                        vol.flags.pop(k[1:])
                    else:
                        t = "WARNING: the config for volume [/%s] tried to remove volflag [%s] by specifying [%s] but that volflag was not already set"
                        self.log(t % (vol.vpath, zs, k), 3)

            if vol.flags.get("dots"):
                for name in vol.axs.uread:
                    vol.axs.udot.add(name)

        if errors:
            sys.exit(1)

        setattr(self.args, "free_umask", free_umask)
        if free_umask:
            os.umask(0)

        vfs.bubble_flags()

        have_e2d = False
        have_e2t = False
        have_dedup = False
        unsafe_dedup = []
        t = "volumes and permissions:\n"
        for zv in vfs.all_vols.values():
            if not self.warn_anonwrite or verbosity < 5:
                break

            if enshare and (zv.vpath == shr or zv.vpath.startswith(shrs)):
                continue

            t += '\n\033[36m"/{}"  \033[33m{}\033[0m'.format(zv.vpath, zv.realpath)
            for txt, attr in [
                ["  read", "uread"],
                [" write", "uwrite"],
                ["  move", "umove"],
                ["delete", "udel"],
                ["  dots", "udot"],
                ["   get", "uget"],
                [" upGet", "upget"],
                ["  html", "uhtml"],
                ["uadmin", "uadmin"],
            ]:
                u = list(sorted(getattr(zv.axs, attr)))
                if u == ["*"] and acct:
                    u = ["\033[35monly-anonymous\033[0m"]
                elif "*" in u:
                    u = ["\033[35meverybody\033[0m"]
                if not u:
                    u = ["\033[36m--none--\033[0m"]
                u = ", ".join(u)
                t += "\n|  {}:  {}".format(txt, u)

            if "e2d" in zv.flags:
                have_e2d = True

            if "e2t" in zv.flags:
                have_e2t = True

            if "dedup" in zv.flags:
                have_dedup = True
                if (
                    "e2d" not in zv.flags
                    and "hardlink" not in zv.flags
                    and "reflink" not in zv.flags
                ):
                    unsafe_dedup.append("/" + zv.vpath)

            t += "\n"

        if self.warn_anonwrite and verbosity > 4:
            if not self.args.no_voldump:
                self.log(t)

            if have_e2d or self.args.have_idp_hdrs:
                t = self.chk_sqlite_threadsafe()
                if t:
                    self.log("\n\033[{}\033[0m\n".format(t))
            if have_e2d:
                if not have_e2t:
                    t = "hint: enable multimedia indexing (artist/title/...) with argument -e2ts"
                    self.log(t, 6)
            else:
                t = "hint: enable searching and upload-undo with argument -e2dsa"
                self.log(t, 6)

            if unsafe_dedup:
                t = "WARNING: symlink-based deduplication is enabled for some volumes, but without indexing. Please enable -e2dsa and/or --hardlink to avoid problems when moving/renaming files. Affected volumes: %s"
                self.log(t % (", ".join(unsafe_dedup)), 3)
            elif not have_dedup:
                t = "hint: enable upload deduplication with --dedup (but see readme for consequences)"
                self.log(t, 6)

            zv, _ = vfs.get("/", "*", False, False)
            zs = zv.realpath.lower()
            if zs in ("/", "c:\\") or zs.startswith(r"c:\windows"):
                t = "you are sharing a system directory: {}\n"
                self.log(t.format(zv.realpath), c=1)

        try:
            zv, _ = vfs.get("", "*", False, True, err=999)
            if self.warn_anonwrite and verbosity > 4 and os.getcwd() == zv.realpath:
                t = "anyone can write to the current directory: {}\n"
                self.log(t.format(zv.realpath), c=1)

            self.warn_anonwrite = False
        except Pebkac:
            self.warn_anonwrite = True

        self.idp_warn = []
        self.idp_err = []
        for idp_vp in self.idp_vols:
            idp_vn, _ = vfs.get(idp_vp, "*", False, False)
            idp_vp0 = idp_vn.vpath0

            sigils = set(PTN_SIGIL.findall(idp_vp0))
            if len(sigils) > 1:
                t = '\nWARNING: IdP-volume "/%s" created by "/%s" has multiple IdP placeholders: %s'
                self.idp_warn.append(t % (idp_vp, idp_vp0, list(sigils)))
                continue

            sigil = sigils.pop()
            par_vp = idp_vp
            while par_vp:
                par_vp = vsplit(par_vp)[0]
                par_vn, _ = vfs.get(par_vp, "*", False, False)
                if sigil in par_vn.vpath0:
                    continue  # parent was spawned for and by same user

                oth_read = []
                oth_write = []
                for usr in par_vn.axs.uread:
                    if usr not in idp_vn.axs.uread:
                        oth_read.append(usr)
                for usr in par_vn.axs.uwrite:
                    if usr not in idp_vn.axs.uwrite:
                        oth_write.append(usr)

                if "*" in oth_read:
                    taxs = "WORLD-READABLE"
                elif "*" in oth_write:
                    taxs = "WORLD-WRITABLE"
                elif oth_read:
                    taxs = "READABLE BY %r" % (oth_read,)
                elif oth_write:
                    taxs = "WRITABLE BY %r" % (oth_write,)
                else:
                    break  # no sigil; not idp; safe to stop

                t = '\nWARNING: IdP-volume "/%s" created by "/%s" has parent/grandparent "/%s" and would be %s'
                self.idp_err.append(t % (idp_vp, idp_vp0, par_vn.vpath, taxs))

        if self.idp_warn:
            t = "WARNING! Some IdP volumes include multiple IdP placeholders; this is too complex to automatically determine if safe or not. To ensure that no users gain unintended access, please use only a single placeholder for each IdP volume."
            self.log(t + "".join(self.idp_warn), 1)

        if self.idp_err:
            t = "WARNING! The following IdP volumes are mounted below another volume where other users can read and/or write files. This is a SECURITY HAZARD!! When copyparty is restarted, it will not know about these IdP volumes yet. These volumes will then be accessible by an unexpected set of permissions UNTIL one of the users associated with their volume sends a request to the server. RECOMMENDATION: You should create a restricted volume where nobody can read/write files, and make sure that all IdP volumes are configured to appear somewhere below that volume."
            self.log(t + "".join(self.idp_err), 1)

        if have_reflink:
            t = "WARNING: Reflink-based dedup was requested, but %s. This will not work; files will be full copies instead."
            if not sys.platform.startswith("linux"):
                self.log(t % "your OS is not Linux", 1)

        self.vfs = vfs
        self.acct = acct
        self.defpw = defpw
        self.grps = grps
        self.iacct = {v: k for k, v in acct.items()}
        self.cfg_files_loaded = cfg_files_loaded

        self.load_sessions()

        self.re_pwd = None
        pwds = [re.escape(x) for x in self.iacct.keys()]
        pwds.extend(list(self.sesa))
        if self.args.usernames:
            pwds.extend([x.split(":", 1)[1] for x in pwds if ":" in x])
        if pwds:
            if self.ah.on:
                zs = r"(\[H\] pw:.*|[?&]pw=)([^&]+)"
            else:
                zs = r"(\[H\] pw:.*|=)(" + "|".join(pwds) + r")([]&; ]|$)"

            self.re_pwd = re.compile(zs)

        # to ensure it propagates into tcpsrv with mp on
        if self.args.mime:
            for zs in self.args.mime:
                ext, mime = zs.split("=", 1)
                MIMES[ext] = mime
            EXTS.update({v: k for k, v in MIMES.items()})

        if enshare:
            # hide shares from controlpanel
            vfs.all_vols = {
                x: y
                for x, y in vfs.all_vols.items()
                if x != shr and not x.startswith(shrs)
            }

            assert db and cur and cur2 and shv  # type: ignore
            for row in cur.execute("select * from sh"):
                s_k, s_pw, s_vp, s_pr, s_nf, s_un, s_t0, s_t1 = row
                shn = shv.nodes.get(s_k, None)
                if not shn:
                    continue

                try:
                    s_vfs, s_rem = vfs.get(
                        s_vp, s_un, "r" in s_pr, "w" in s_pr, "m" in s_pr, "d" in s_pr
                    )
                except Exception as ex:
                    t = "removing share [%s] by [%s] to [%s] due to %r"
                    self.log(t % (s_k, s_un, s_vp, ex), 3)
                    shv.nodes.pop(s_k)
                    continue

                fns = []
                if s_nf:
                    q = "select vp from sf where k = ?"
                    for (s_fn,) in cur2.execute(q, (s_k,)):
                        fns.append(s_fn)

                    shn.shr_files = set(fns)
                    shn.ls = shn._ls_shr
                    shn.canonical = shn._canonical_shr
                    shn.dcanonical = shn._dcanonical_shr
                else:
                    shn.ls = shn._ls
                    shn.canonical = shn._canonical
                    shn.dcanonical = shn._dcanonical

                shn.shr_owner = s_un
                shn.shr_src = (s_vfs, s_rem)
                shn.realpath = s_vfs.canonical(s_rem)

                o_vn, _ = shn._get_share_src("")
                shn.flags = o_vn.flags.copy()
                shn.dbpath = o_vn.dbpath
                shn.histpath = o_vn.histpath

                # root.all_aps doesn't include any shares, so make a copy where the
                # share appears in all abspaths it can provide (for example for chk_ap)
                ap = shn.realpath
                if not ap.endswith(os.sep):
                    ap += os.sep
                shn.shr_all_aps = [(x, y[:]) for x, y in vfs.all_aps]
                exact = False
                for ap2, vns in shn.shr_all_aps:
                    if ap == ap2:
                        exact = True
                    if ap2.startswith(ap):
                        try:
                            vp2 = vjoin(s_rem, ap2[len(ap) :])
                            vn2, _ = s_vfs.get(vp2, "*", False, False)
                            if vn2 == s_vfs or vn2.dbv == s_vfs:
                                vns.append(shn)
                        except:
                            pass
                if not exact:
                    shn.shr_all_aps.append((ap, [shn]))
                shn.shr_all_aps.sort(key=lambda x: len(x[0]), reverse=True)

                if self.args.shr_v:
                    t = "mapped %s share [%s] by [%s] => [%s] => [%s]"
                    self.log(t % (s_pr, s_k, s_un, s_vp, shn.realpath))

            # transplant shadowing into shares
            for vn in shv.nodes.values():
                svn, srem = vn.shr_src  # type: ignore
                if srem:
                    continue  # free branch, safe
                ap = svn.canonical(srem)
                if bos.path.isfile(ap):
                    continue  # also fine
                for zs in svn.nodes.keys():
                    # hide subvolume
                    vn.nodes[zs] = VFS(self.log_func, "", "", "", AXS(), self.vf0())

            cur2.close()
            cur.close()
            db.close()

        self.js_ls = {}
        self.js_htm = {}
        for vp, vn in self.vfs.all_nodes.items():
            if enshare and vp.startswith(shrs):
                continue  # propagates later in this func
            vf = vn.flags
            vn.js_ls = {
                "idx": "e2d" in vf,
                "itag": "e2t" in vf,
                "dnsort": "nsort" in vf,
                "dhsortn": vf["hsortn"],
                "dsort": vf["sort"],
                "dcrop": vf["crop"],
                "dth3x": vf["th3x"],
                "u2ts": vf["u2ts"],
                "shr_who": vf["shr_who"],
                "frand": bool(vf.get("rand")),
                "lifetime": vf.get("lifetime") or 0,
                "unlist": vf.get("unlist") or "",
                "sb_lg": "" if "no_sb_lg" in vf else (vf.get("lg_sbf") or "y"),
            }
            if "ufavico_h" in vf:
                vn.js_ls["ufavico"] = vf["ufavico_h"]
            js_htm = {
                "SPINNER": self.args.spinner,
                "s_name": self.args.bname,
                "idp_login": self.args.idp_login,
                "have_up2k_idx": "e2d" in vf,
                "have_acode": not self.args.no_acode,
                "have_c2flac": self.args.allow_flac,
                "have_c2wav": self.args.allow_wav,
                "have_shr": self.args.shr,
                "shr_who": vf["shr_who"],
                "have_zip": not self.args.no_zip,
                "have_zls": not self.args.no_zls,
                "have_mv": not self.args.no_mv,
                "have_del": not self.args.no_del,
                "have_unpost": int(self.args.unpost),
                "have_emp": int(self.args.emp),
                "md_no_br": int(vf.get("md_no_br") or 0),
                "ext_th": vf.get("ext_th_d") or {},
                "sb_md": "" if "no_sb_md" in vf else (vf.get("md_sbf") or "y"),
                "sba_md": vf.get("md_sba") or "",
                "sba_lg": vf.get("lg_sba") or "",
                "txt_ext": self.args.textfiles.replace(",", " "),
                "def_hcols": list(vf.get("mth") or []),
                "unlist0": vf.get("unlist") or "",
                "see_dots": self.args.see_dots,
                "dqdel": self.args.qdel,
                "dgrid": "grid" in vf,
                "dgsel": "gsel" in vf,
                "dnsort": "nsort" in vf,
                "dhsortn": vf["hsortn"],
                "dsort": vf["sort"],
                "dcrop": vf["crop"],
                "dth3x": vf["th3x"],
                "dvol": self.args.au_vol,
                "idxh": int(self.args.ih),
                "dutc": not self.args.localtime,
                "dfszf": self.args.ui_filesz.strip("-"),
                "themes": self.args.themes,
                "turbolvl": self.args.turbo,
                "nosubtle": self.args.nosubtle,
                "u2j": self.args.u2j,
                "u2sz": self.args.u2sz,
                "u2ts": vf["u2ts"],
                "u2ow": vf["u2ow"],
                "frand": bool(vf.get("rand")),
                "lifetime": vn.js_ls["lifetime"],
                "u2sort": self.args.u2sort,
            }
            zs = "ui_noacci ui_nocpla ui_noctxb ui_nolbar ui_nombar ui_nonav ui_notree ui_norepl ui_nosrvi"
            for zs in zs.split():
                if vf.get(zs):
                    js_htm[zs] = 1
            vn.js_htm = json_hesc(json.dumps(js_htm))

        vols = list(vfs.all_nodes.values())
        if enshare:
            for vol in shv.nodes.values():
                if vol.vpath not in vfs.all_nodes:
                    self.log("BUG: /%s not in all_nodes" % (vol.vpath,), 1)
                    vols.append(vol)
            if shr in vfs.all_nodes:
                self.log("BUG: %s found in all_nodes" % (shr,), 1)

        for vol in vols:
            dbv = vol.get_dbv("")[0]
            vol.js_ls = vol.js_ls or dbv.js_ls or {}
            vol.js_htm = vol.js_htm or dbv.js_htm or "{}"

            zs = str(vol.flags.get("tcolor") or self.args.tcolor)
            vol.flags["tcolor"] = zs.lstrip("#")

    def setup_auth_ord(self)  :
        ao = [x.strip() for x in self.args.auth_ord.split(",")]
        if "idp" in ao:
            zi = ao.index("idp")
            ao = ao[:zi] + ["idp-hm", "idp-h"] + ao[zi:]
        zsl = "pw idp-h idp-hm ipu".split()
        pw, h, hm, ipu = [ao.index(x) if x in ao else 99 for x in zsl]
        self.args.ao_idp_before_pw = min(h, hm) < pw
        self.args.ao_h_before_hm = h < hm
        self.args.ao_ipu_wins = ipu == 0
        self.args.ao_have_pw = pw < 99 or not self.args.have_idp_hdrs

    def load_idp_db(self, quiet=False)  :
        # mutex me
        level = self.args.idp_store
        if level < 2 or not self.args.have_idp_hdrs:
            return


        db = sqlite3.connect(self.args.idp_db)
        cur = db.cursor()
        from_cache = cur.execute("select un, gs from us").fetchall()
        cur.close()
        db.close()

        self.idp_accs.clear()
        self.idp_usr_gh.clear()

        gsep = self.args.idp_gsep
        n = []
        for uname, gname in from_cache:
            if level < 3:
                if uname in self.idp_accs:
                    continue
                gname = ""
            gnames = [x.strip() for x in gsep.split(gname)]
            gnames.sort()

            # self.idp_usr_gh[uname] = gname
            self.idp_accs[uname] = gnames
            n.append(uname)

        if n and not quiet:
            t = ", ".join(n[:9])
            if len(n) > 9:
                t += "..."
            self.log("found %d IdP users in db (%s)" % (len(n), t))

    def load_sessions(self, quiet=False)  :
        # mutex me
        if self.args.no_ses:
            self.ases = {}
            self.sesa = {}
            return


        ases = {}
        blen = (self.args.ses_len // 4) * 4  # 3 bytes in 4 chars
        blen = (blen * 3) // 4  # bytes needed for ses_len chars

        db = sqlite3.connect(self.args.ses_db)
        cur = db.cursor()

        for uname, sid in cur.execute("select un, si from us"):
            if uname in self.acct:
                ases[uname] = sid

        n = []
        q = "insert into us values (?,?,?)"
        accs = list(self.acct)
        if self.args.have_idp_hdrs and self.args.idp_cookie:
            accs.extend(self.idp_accs.keys())
        for uname in accs:
            if uname not in ases:
                sid = ub64enc(os.urandom(blen)).decode("ascii")
                cur.execute(q, (uname, sid, int(time.time())))
                ases[uname] = sid
                n.append(uname)

        if n:
            db.commit()

        cur.close()
        db.close()

        self.ases = ases
        self.sesa = {v: k for k, v in ases.items()}
        if n and not quiet:
            t = ", ".join(n[:3])
            if len(n) > 3:
                t += "..."
            self.log("added %d new sessions (%s)" % (len(n), t))

    def forget_session(self, broker , uname )  :
        with self.mutex:
            self._forget_session(uname)

        if broker:
            broker.ask("_reload_sessions").get()

    def _forget_session(self, uname )  :
        if self.args.no_ses:
            return


        db = sqlite3.connect(self.args.ses_db)
        cur = db.cursor()
        cur.execute("delete from us where un = ?", (uname,))
        db.commit()
        cur.close()
        db.close()

        self.sesa.pop(self.ases.get(uname, ""), "")
        self.ases.pop(uname, "")

    def chpw(self, broker , uname, pw)   :
        if not self.args.chpw:
            return False, "feature disabled in server config"

        if uname == "*" or uname not in self.defpw:
            return False, "not logged in"

        if uname in self.args.chpw_no:
            return False, "not allowed for this account"

        if len(pw) < self.args.chpw_len:
            t = "minimum password length: %d characters"
            return False, t % (self.args.chpw_len,)

        if self.args.usernames:
            pw = "%s:%s" % (uname, pw)

        hpw = self.ah.hash(pw) if self.ah.on else pw

        if hpw == self.acct[uname]:
            return False, "that's already your password my dude"

        if hpw in self.iacct or hpw in self.sesa:
            return False, "password is taken"

        with self.mutex:
            ap = self.args.chpw_db
            if not bos.path.exists(ap):
                pwdb = {}
            else:
                jtxt = read_utf8(self.log, ap, True)
                pwdb = json.loads(jtxt)

            pwdb = [x for x in pwdb if x[0] != uname]
            pwdb.append((uname, self.defpw[uname], hpw))

            with open(ap, "w", encoding="utf-8") as f:
                json.dump(pwdb, f, separators=(",\n", ": "))

            self.log("reinitializing due to password-change for user [%s]" % (uname,))

            if not broker:
                # only true for tests
                self._reload()
                return True, "new password OK"

        broker.ask("reload", False, False).get()
        return True, "new password OK"

    def setup_chpw(self, acct  )  :
        ap = self.args.chpw_db
        if not self.args.chpw or not bos.path.exists(ap):
            return

        jtxt = read_utf8(self.log, ap, True)
        pwdb = json.loads(jtxt)

        useen = set()
        urst = set()
        uok = set()
        for usr, orig, mod in pwdb:
            useen.add(usr)
            if usr not in acct:
                # previous user, no longer known
                continue
            if acct[usr] != orig:
                urst.add(usr)
                continue
            uok.add(usr)
            acct[usr] = mod

        if not self.args.chpw_v:
            return

        for usr in acct:
            if usr not in useen:
                urst.add(usr)

        for zs in uok:
            urst.discard(zs)

        if self.args.chpw_v == 1 or (self.args.chpw_v == 2 and not urst):
            t = "chpw: %d changed, %d unchanged"
            self.log(t % (len(uok), len(urst)))
            return

        elif self.args.chpw_v == 2:
            t = "chpw: %d changed" % (len(uok),)
            if urst:
                t += ", \033[0munchanged:\033[35m %s" % (", ".join(list(urst)))

            self.log(t, 6)
            return

        msg = ""
        if uok:
            t = "\033[0mchanged: \033[32m%s"
            msg += t % (", ".join(list(uok)),)
        if urst:
            t = "%s\033[0munchanged: \033[35m%s"
            msg += t % (
                ", " if msg else "",
                ", ".join(list(urst)),
            )

        self.log("chpw: " + msg, 6)

    def setup_pwhash(self, acct  )  :
        if self.args.usernames:
            for uname, pw in list(acct.items())[:]:
                if pw.startswith("+") and len(pw) == 33:
                    continue
                acct[uname] = "%s:%s" % (uname, pw)

        self.ah = PWHash(self.args)
        if not self.ah.on:
            if self.args.ah_cli or self.args.ah_gen:
                t = "\n  BAD CONFIG:\n    cannot --ah-cli or --ah-gen without --ah-alg"
                raise Exception(t)
            return

        if self.args.ah_cli:
            self.ah.cli()
            sys.exit()
        elif self.args.ah_gen == "-":
            self.ah.stdin()
            sys.exit()
        elif self.args.ah_gen:
            print(self.ah.hash(self.args.ah_gen))
            sys.exit()

        if not acct:
            return

        changed = False
        for uname, pw in list(acct.items())[:]:
            if pw.startswith("+") and len(pw) == 33:
                continue

            changed = True
            hpw = self.ah.hash(pw)
            acct[uname] = hpw
            t = "hashed password for account {}: {}"
            self.log(t.format(uname, hpw), 3)

        if not changed:
            return

        lns = []
        for uname, pw in acct.items():
            lns.append("  {}: {}".format(uname, pw))

        t = "please use the following hashed passwords in your config:\n{}"
        self.log(t.format("\n".join(lns)), 3)

    def chk_sqlite_threadsafe(self)  :
        v = SQLITE_VER[-1:]

        if v == "1":
            # threadsafe (linux, windows)
            return ""

        if v == "2":
            # module safe, connections unsafe (macos)
            return "33m  your sqlite3 was compiled with reduced thread-safety;\n   database features (-e2d, -e2t) SHOULD be fine\n    but MAY cause database-corruption and crashes"

        if v == "0":
            # everything unsafe
            return "31m  your sqlite3 was compiled WITHOUT thread-safety!\n   database features (-e2d, -e2t) will PROBABLY cause crashes!"

        return "36m  cannot verify sqlite3 thread-safety; strange but probably fine"

    def dbg_ls(self)  :
        users = self.args.ls
        vol = "*"
        flags  = []

        try:
            users, vol = users.split(",", 1)
        except:
            pass

        try:
            vol, zf = vol.split(",", 1)
            flags = zf.split(",")
        except:
            pass

        if users == "**":
            users = list(self.acct.keys()) + ["*"]
        else:
            users = [users]

        for u in users:
            if u not in self.acct and u != "*":
                raise Exception("user not found: " + u)

        if vol == "*":
            vols = ["/" + x for x in self.vfs.all_vols]
        else:
            vols = [vol]

        for zs in vols:
            if not zs.startswith("/"):
                raise Exception("volumes must start with /")

            if zs[1:] not in self.vfs.all_vols:
                raise Exception("volume not found: " + zs)

        self.log(str({"users": users, "vols": vols, "flags": flags}))
        t = "/{}: read({}) write({}) move({}) del({}) dots({}) get({}) upGet({}) uadmin({})"
        for k, zv in self.vfs.all_vols.items():
            vc = zv.axs
            vs = [
                k,
                vc.uread,
                vc.uwrite,
                vc.umove,
                vc.udel,
                vc.udot,
                vc.uget,
                vc.upget,
                vc.uhtml,
                vc.uadmin,
            ]
            self.log(t.format(*vs))

        flag_v = "v" in flags
        flag_ln = "ln" in flags
        flag_p = "p" in flags
        flag_r = "r" in flags

        bads = []
        for v in vols:
            v = v[1:]
            vtop = "/{}/".format(v) if v else "/"
            for u in users:
                self.log("checking /{} as {}".format(v, u))
                try:
                    vn, _ = self.vfs.get(v, u, True, False, False, False, False)
                except:
                    continue

                atop = vn.realpath
                safeabs = atop + os.sep
                g = vn.walk(
                    vn.vpath,
                    "",
                    [],
                    u,
                    [[True, False]],
                    1,
                    not self.args.no_scandir,
                    False,
                    False,
                )
                for _, _, vpath, apath, files1, dirs, _ in g:
                    fnames = [n[0] for n in files1]
                    zsl = [vpath + "/" + n for n in fnames] if vpath else fnames
                    vpaths = [vtop + x for x in zsl]
                    apaths = [os.path.join(apath, n) for n in fnames]
                    files = [(vpath + "/", apath + os.sep)] + list(
                        [(zs1, zs2) for zs1, zs2 in zip(vpaths, apaths)]
                    )

                    if flag_ln:
                        files = [x for x in files if not x[1].startswith(safeabs)]
                        if files:
                            dirs[:] = []  # stop recursion
                            bads.append(files[0][0])

                    if not files:
                        continue
                    elif flag_v:
                        ta = [""] + [
                            '# user "{}", vpath "{}"\n{}'.format(u, vp, ap)
                            for vp, ap in files
                        ]
                    else:
                        ta = ["user {}, vol {}: {} =>".format(u, vtop, files[0][0])]
                        ta += [x[1] for x in files]

                    self.log("\n".join(ta))

                if bads:
                    self.log("\n  ".join(["found symlinks leaving volume:"] + bads))

                if bads and flag_p:
                    raise Exception(
                        "\033[31m\n  [--ls] found a safety issue and prevented startup:\n    found symlinks leaving volume, and strict is set\n\033[0m"
                    )

        if not flag_r:
            sys.exit(0)

    def cgen(self)  :
        ret = [
            "## WARNING:",
            "##  there will probably be mistakes in",
            "##  commandline-args (and maybe volflags)",
            "",
        ]

        csv = set("i p th_covers zm_on zm_off zs_on zs_off".split())
        zs = "c ihead ohead mtm mtp on403 on404 xac xad xar xau xiu xban xbc xbd xbr xbu xm"
        lst = set(zs.split())
        askip = set("a v c vc cgen exp_lg exp_md theme".split())

        t = "exp_lg exp_md ext_th_d mv_re_r mv_re_t rm_re_r rm_re_t srch_re_dots srch_re_nodot"
        fskip = set(t.split())

        # keymap from argv to vflag
        amap = vf_bmap()
        amap.update(vf_vmap())
        amap.update(vf_cmap())
        vmap = {v: k for k, v in amap.items()}

        args = {k: v for k, v in vars(self.args).items()}
        pops = []
        for k1, k2 in IMPLICATIONS:
            if args.get(k1):
                pops.append(k2)
        for pop in pops:
            args.pop(pop, None)

        if args:
            ret.append("[global]")
            for k, v in args.items():
                if k in askip:
                    continue

                try:
                    v = v.pattern
                    if k in ("idp_gsep", "tftp_lsf"):
                        v = v[1:-1]  # close enough
                except:
                    pass

                skip = False
                for k2, defstr in (("mte", DEF_MTE), ("mth", DEF_MTH)):
                    if k != k2:
                        continue
                    s1 = list(sorted(list(v)))
                    s2 = list(sorted(defstr.split(",")))
                    if s1 == s2:
                        skip = True
                        break
                    v = ",".join(s1)

                if skip:
                    continue

                if k in csv:
                    v = ", ".join([str(za) for za in v])
                try:
                    v2 = getattr(self.dargs, k)
                    if k == "tcolor" and len(v2) == 3:
                        v2 = "".join([x * 2 for x in v2])
                    if v == v2 or v.replace(", ", ",") == v2:
                        continue
                except:
                    continue

                dk = "  " + k.replace("_", "-")
                if k in lst:
                    for ve in v:
                        ret.append("{}: {}".format(dk, ve))
                else:
                    if v is True:
                        ret.append(dk)
                    elif v not in (False, None, ""):
                        ret.append("{}: {}".format(dk, v))
            ret.append("")

        if self.acct:
            ret.append("[accounts]")
            for u, p in self.acct.items():
                ret.append("  {}: {}".format(u, p))
            ret.append("")

        if self.grps:
            ret.append("[groups]")
            for gn, uns in self.grps.items():
                ret.append("  %s: %s" % (gn, ", ".join(uns)))
            ret.append("")

        for vol in self.vfs.all_vols.values():
            ret.append("[/{}]".format(vol.vpath))
            ret.append("  " + vol.realpath)
            ret.append("  accs:")
            perms = {
                "r": "uread",
                "w": "uwrite",
                "m": "umove",
                "d": "udel",
                ".": "udot",
                "g": "uget",
                "G": "upget",
                "h": "uhtml",
                "a": "uadmin",
            }
            users = {}
            for pkey in perms.values():
                for uname in getattr(vol.axs, pkey):
                    try:
                        users[uname] += 1
                    except:
                        users[uname] = 1
            lusers = [(v, k) for k, v in users.items()]
            vperms = {}
            for _, uname in sorted(lusers):
                pstr = ""
                for pchar, pkey in perms.items():
                    if uname in getattr(vol.axs, pkey):
                        pstr += pchar
                if "g" in pstr and "G" in pstr:
                    pstr = pstr.replace("g", "")
                pstr = pstr.replace("rwmd.a", "A")
                try:
                    vperms[pstr].append(uname)
                except:
                    vperms[pstr] = [uname]
            for pstr, uname in vperms.items():
                ret.append("    {}: {}".format(pstr, ", ".join(uname)))
            trues = []
            vals = []
            for k, v in sorted(vol.flags.items()):
                if k in fskip:
                    continue

                try:
                    v = v.pattern
                except:
                    pass

                try:
                    ak = vmap[k]
                    v2 = getattr(self.args, ak)

                    try:
                        v2 = v2.pattern
                    except:
                        pass

                    if v2 is v:
                        continue
                except:
                    pass

                skip = False
                for k2, defstr in (("mte", DEF_MTE), ("mth", DEF_MTH)):
                    if k != k2:
                        continue
                    s1 = list(sorted(list(v)))
                    s2 = list(sorted(defstr.split(",")))
                    if s1 == s2:
                        skip = True
                        break
                    v = ",".join(s1)

                if skip:
                    continue

                if k in lst:
                    for ve in v:
                        vals.append("{}: {}".format(k, ve))
                elif v is True:
                    trues.append(k)
                elif v is not False:
                    vals.append("{}: {}".format(k, v))
            pops = []
            for k1, k2 in IMPLICATIONS:
                if k1 in trues:
                    pops.append(k2)
            trues = [x for x in trues if x not in pops]
            if trues:
                vals.append(", ".join(trues))
            if vals:
                ret.append("  flags:")
                for zs in vals:
                    ret.append("    " + zs)
            ret.append("")

        self.log("generated config:\n\n" + "\n".join(ret))


def derive_args(args )  :
    args.have_idp_hdrs = bool(args.idp_h_usr or args.idp_hm_usr)
    args.have_ipu_or_ipr = bool(args.ipu or args.ipr)


def n_du_who(s )  :
    if s == "all":
        return 9
    if s == "auth":
        return 7
    if s == "w":
        return 5
    if s == "rw":
        return 4
    if s == "a":
        return 3
    return 0


def n_ver_who(s )  :
    if s == "all":
        return 9
    if s == "auth":
        return 6
    if s == "a":
        return 3
    return 0


def split_cfg_ln(ln )   :
    # "a, b, c: 3" => {a:true, b:true, c:3}
    ret = {}
    while True:
        ln = ln.strip()
        if not ln:
            break
        ofs_sep = ln.find(",") + 1
        ofs_var = ln.find(":") + 1
        if not ofs_sep and not ofs_var:
            ret[ln] = True
            break
        if ofs_sep and (ofs_sep < ofs_var or not ofs_var):
            k, ln = ln.split(",", 1)
            ret[k.strip()] = True
        else:
            k, ln = ln.split(":", 1)
            ret[k.strip()] = ln.strip()
            break
    return ret


def expand_config_file(
    log , ret , fp , ipath 
)  :
    """expand all % file includes"""
    fp = absreal(fp)
    if len(ipath.split(" -> ")) > 64:
        raise Exception("hit max depth of 64 includes")

    if os.path.isdir(fp):
        names = list(sorted(os.listdir(fp)))
        cnames = [
            x for x in names if x.lower().endswith(".conf") and not x.startswith(".")
        ]
        if not cnames:
            t = "warning: tried to read config-files from folder '%s' but it does not contain any "
            if names:
                t += ".conf files; the following files/subfolders were ignored: %s"
                t = t % (fp, ", ".join(names[:8]))
            else:
                t += "files at all"
                t = t % (fp,)

            if log:
                log(t, 3)

            ret.append("#\033[33m %s\033[0m" % (t,))
        else:
            zs = "#\033[36m cfg files in %s => %s\033[0m" % (fp, cnames)
            ret.append(zs)

        for fn in cnames:
            fp2 = os.path.join(fp, fn)
            if fp2 in ipath:
                continue

            expand_config_file(log, ret, fp2, ipath)

        return

    if not os.path.exists(fp):
        t = "warning: tried to read config from '%s' but the file/folder does not exist"
        t = t % (fp,)
        if log:
            log(t, 3)

        ret.append("#\033[31m %s\033[0m" % (t,))
        return

    ipath += " -> " + fp
    ret.append("#\033[36m opening cfg file{}\033[0m".format(ipath))

    cfg_lines = read_utf8(log, fp, True).replace("\t", " ").split("\n")
    if True:  # diff-golf
        for oln in [x.rstrip() for x in cfg_lines]:
            ln = oln.split("  #")[0].strip()
            if ln.startswith("% "):
                pad = " " * len(oln.split("%")[0])
                fp2 = ln[1:].strip()
                fp2 = os.path.join(os.path.dirname(fp), fp2)
                ofs = len(ret)
                expand_config_file(log, ret, fp2, ipath)
                for n in range(ofs, len(ret)):
                    ret[n] = pad + ret[n]
                continue

            ret.append(oln)

    ret.append("#\033[36m closed{}\033[0m".format(ipath))

    zsl = []
    for ln in ret:
        zs = ln.split("  #")[0]
        if " #" in zs and zs.split("#")[0].strip():
            zsl.append(ln)
    if zsl and "no-cfg-cmt-warn" not in "\n".join(ret):
        t = "\033[33mWARNING: there is less than two spaces before the # in the following config lines, so instead of assuming that this is a comment, the whole line will become part of the config value:\n\n>>> %s\n\nif you are familiar with this and would like to mute this warning, specify the global-option no-cfg-cmt-warn\n\033[0m"
        t = t % ("\n>>> ".join(zsl),)
        if log:
            log(t)
        else:
            print(t, file=sys.stderr)


def upgrade_cfg_fmt(
    log , args , orig , cfg_fp 
)  :
    """convert from v1 to v2 format"""
    zst = [x.split("#")[0].strip() for x in orig]
    zst = [x for x in zst if x]
    if (
        "[global]" in zst
        or "[accounts]" in zst
        or "accs:" in zst
        or "flags:" in zst
        or [x for x in zst if x.startswith("[/")]
        or len(zst) == len([x for x in zst if x.startswith("%")])
    ):
        return orig

    zst = [x for x in orig if "#\033[36m opening cfg file" not in x]
    incl = len(zst) != len(orig) - 1

    t = "upgrading config file [{}] from v1 to v2"
    if not args.vc:
        t += ". Run with argument '--vc' to see the converted config if you want to upgrade"
    if incl:
        t += ". Please don't include v1 configs from v2 files or vice versa! Upgrade all of them at the same time."
    if log:
        log(t.format(cfg_fp), 3)

    ret = []
    vp = ""
    ap = ""
    cat = ""
    catg = "[global]"
    cata = "[accounts]"
    catx = "  accs:"
    catf = "  flags:"
    for ln in orig:
        sn = ln.strip()
        if not sn:
            cat = vp = ap = ""
        if not sn.split("#")[0]:
            ret.append(ln)
        elif sn.startswith("-") and cat in ("", catg):
            if cat != catg:
                cat = catg
                ret.append(cat)
            sn = sn.lstrip("-")
            zst = sn.split(" ", 1)
            if len(zst) > 1:
                sn = "{}: {}".format(zst[0], zst[1].strip())
            ret.append("  " + sn)
        elif sn.startswith("u ") and cat in ("", catg, cata):
            if cat != cata:
                cat = cata
                ret.append(cat)
            s1, s2 = sn[1:].split(":", 1)
            ret.append("  {}: {}".format(s1.strip(), s2.strip()))
        elif not ap:
            ap = sn
        elif not vp:
            vp = "/" + sn.strip("/")
            cat = "[{}]".format(vp)
            ret.append(cat)
            ret.append("  " + ap)
        elif sn.startswith("c "):
            if cat != catf:
                cat = catf
                ret.append(cat)
            sn = sn[1:].strip()
            if "=" in sn:
                zst = sn.split("=", 1)
                sn = zst[0].replace(",", ", ")
                sn += ": " + zst[1]
            else:
                sn = sn.replace(",", ", ")
            ret.append("    " + sn)
        elif sn[:1] in "rwmdgGhaA.":
            if cat != catx:
                cat = catx
                ret.append(cat)
            zst = sn.split(" ")
            zst = [x for x in zst if x]
            if len(zst) == 1:
                zst.append("*")
            ret.append("    {}: {}".format(zst[0], ", ".join(zst[1:])))
        else:
            t = "did not understand line {} in the config"
            t1 = t
            n = 0
            for ln in orig:
                n += 1
                t += "\n{:4} {}".format(n, ln)
            if log:
                log(t, 1)
            else:
                print("\033[31m" + t)
            raise Exception(t1)

    if args.vc and log:
        t = "new config syntax (copy/paste this to upgrade your config):\n"
        t += "\n# ======================[ begin upgraded config ]======================\n\n"
        for ln in ret:
            t += ln + "\n"
        t += "\n# ======================[ end of upgraded config ]======================\n"
        log(t)

    return ret
