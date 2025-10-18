# coding: utf-8
from __future__ import print_function, unicode_literals

import argparse  # typechk
import copy
import errno
import hashlib
import itertools
import json
import os
import random
import re
import socket
import stat
import sys
import threading  # typechk
import time
import uuid
from datetime import datetime
from operator import itemgetter

import jinja2  # typechk
from ipaddress import IPv6Network

try:
    if os.environ.get("PRTY_NO_LZMA"):
        raise Exception()

    import lzma
except:
    pass

from .__init__ import ANYWIN, RES, TYPE_CHECKING, EnvParams, unicode
from .__version__ import S_VERSION
from .authsrv import LEELOO_DALLAS, VFS  # typechk
from .bos import bos
from .qrkode import QrCode, qr2svg, qrgen
from .star import StreamTar
from .sutil import StreamArc, gfilter
from .szip import StreamZip
from .up2k import up2k_chunksize
from .util import unquote  # type: ignore
from .util import (
    APPLESAN_RE,
    BITNESS,
    DAV_ALLPROPS,
    E_SCK_WR,
    FN_EMB,
    HAVE_SQLITE3,
    HTTPCODE,
    UTC,
    Garda,
    MultipartParser,
    ODict,
    Pebkac,
    UnrecvEOF,
    WrongPostKey,
    absreal,
    afsenc,
    alltrace,
    atomic_move,
    b64dec,
    eol_conv,
    exclude_dotfiles,
    formatdate,
    fsenc,
    gen_content_disposition,
    gen_filekey,
    gen_filekey_dbg,
    gencookie,
    get_df,
    get_spd,
    guess_mime,
    gzip,
    gzip_file_orig_sz,
    gzip_orig_sz,
    has_resource,
    hashcopy,
    hidedir,
    html_bescape,
    html_escape,
    html_sh_esc,
    humansize,
    ipnorm,
    json_hesc,
    justcopy,
    load_resource,
    loadpy,
    log_reloc,
    min_ex,
    pathmod,
    quotep,
    rand_name,
    read_header,
    read_socket,
    read_socket_chunked,
    read_socket_unbounded,
    read_utf8,
    relchk,
    ren_open,
    runhook,
    s2hms,
    s3enc,
    sanitize_fn,
    sanitize_vpath,
    sendfile_kern,
    sendfile_py,
    set_fperms,
    stat_resource,
    str_anchor,
    ub64dec,
    ub64enc,
    ujoin,
    undot,
    unescape_cookie,
    unquotep,
    vjoin,
    vol_san,
    vroots,
    vsplit,
    wunlink,
    yieldfile,
)

if TYPE_CHECKING:
    from .httpconn import HttpConn

if not hasattr(socket, "AF_UNIX"):
    setattr(socket, "AF_UNIX", -9001)

_ = (argparse, threading)

USED4SEC = {"usedforsecurity": False} if sys.version_info > (3, 9) else {}

NO_CACHE = {"Cache-Control": "no-cache"}

ALL_COOKIES = "k304 no304 js idxh dots cppwd cppws".split()

BADXFF = " due to dangerous misconfiguration (the http-header specified by --xff-hdr was received from an untrusted reverse-proxy)"

H_CONN_KEEPALIVE = "Connection: Keep-Alive"
H_CONN_CLOSE = "Connection: Close"

LOGUES = [[0, ".prologue.html"], [1, ".epilogue.html"]]

READMES = [[0, ["preadme.md", "PREADME.md"]], [1, ["readme.md", "README.md"]]]

RSS_SORT = {"m": "mt", "u": "at", "n": "fn", "s": "sz"}

A_FILE = os.stat_result(
    (0o644, -1, -1, 1, 1000, 1000, 8, 0x39230101, 0x39230101, 0x39230101)
)

RE_CC = re.compile(r"[\x00-\x1f]")  # search always faster
RE_HSAFE = re.compile(r"[\x00-\x1f<>\"'&]")  # search always much faster
RE_HOST = re.compile(r"[^][0-9a-zA-Z.:_-]")  # search faster <=17ch
RE_MHOST = re.compile(r"^[][0-9a-zA-Z.:_-]+$")  # match faster >=18ch
RE_K = re.compile(r"[^0-9a-zA-Z_-]")  # search faster <=17ch
RE_HR = re.compile(r"[<>\"'&]")
RE_MDV = re.compile(r"(.*)\.([0-9]+\.[0-9]{3})(\.[Mm][Dd])$")

UPARAM_CC_OK = set("doc move tree".split())


class HttpCli(object):
    """
    Spawned by HttpConn to process one http transaction
    """

    def __init__(self, conn )  :

        empty_stringlist  = []

        self.t0 = time.time()
        self.conn = conn
        self.u2mutex = conn.u2mutex  # mypy404
        self.s = conn.s
        self.sr = conn.sr
        self.ip = conn.addr[0]
        self.addr   = conn.addr
        self.args = conn.args  # mypy404
        self.E  = self.args.E
        self.asrv = conn.asrv  # mypy404
        self.ico = conn.ico  # mypy404
        self.thumbcli = conn.thumbcli  # mypy404
        self.u2fh = conn.u2fh  # mypy404
        self.pipes = conn.pipes  # mypy404
        self.log_func = conn.log_func  # mypy404
        self.log_src = conn.log_src  # mypy404
        self.gen_fk = self._gen_fk if self.args.log_fk else gen_filekey
        self.tls  = hasattr(self.s, "cipher")
        self.is_vproxied = bool(self.args.R)

        # placeholders; assigned by run()
        self.keepalive = False
        self.is_https = False
        self.in_hdr_recv = True
        self.headers   = {}
        self.mode = " "  # http verb
        self.req = " "
        self.http_ver = ""
        self.hint = ""
        self.host = " "
        self.ua = " "
        self.is_rclone = False
        self.ouparam   = {}
        self.uparam   = {}
        self.cookies   = {}
        self.avn  = None
        self.vn = self.asrv.vfs
        self.rem = " "
        self.vpath = " "
        self.vpaths = " "
        self.dl_id = ""
        self.gctx = " "  # additional context for garda
        self.trailing_slash = True
        self.uname = " "
        self.pw = " "
        self.rvol = self.wvol = self.avol = empty_stringlist
        self.do_log = True
        self.can_read = False
        self.can_write = False
        self.can_move = False
        self.can_delete = False
        self.can_get = False
        self.can_upget = False
        self.can_admin = False
        self.can_dot = False
        self.out_headerlist   = []
        self.out_headers   = {}
        # post
        self.parser  = None
        # end placeholders

        self.html_head = ""

    def log(self, msg , c   = 0)  :
        ptn = self.asrv.re_pwd
        if ptn and ptn.search(msg):
            if self.asrv.ah.on:
                msg = ptn.sub("\033[7m pw \033[27m", msg)
            else:
                msg = ptn.sub(self.unpwd, msg)

        self.log_func(self.log_src, msg, c)

    def unpwd(self, m )  :
        a, b, c = m.groups()
        uname = self.asrv.iacct.get(b) or self.asrv.sesa.get(b)
        return "%s\033[7m %s \033[27m%s" % (a, uname, c)

    def _check_nonfatal(self, ex , post )  :
        if post:
            return ex.code < 300

        return ex.code < 400 or ex.code in [404, 429]

    def _assert_safe_rem(self, rem )  :
        # sanity check to prevent any disasters
        # (this function hopefully serves no purpose; validation has already happened at this point, this only exists as a last-ditch effort just in case)
        if rem.startswith(("/", "../")) or "/../" in rem:
            raise Exception("that was close")

    def _gen_fk(self, alg , salt , fspath , fsize , inode )  :
        return gen_filekey_dbg(
            alg, salt, fspath, fsize, inode, self.log, self.args.log_fk
        )

    def j2s(self, name , **ka )  :
        tpl = self.conn.hsrv.j2[name]
        ka["r"] = self.args.SR if self.is_vproxied else ""
        ka["ts"] = self.conn.hsrv.cachebuster()
        ka["lang"] = self.cookies.get("cplng") or self.args.lang
        ka["favico"] = self.args.favico
        ka["s_doctitle"] = self.args.doctitle
        ka["tcolor"] = self.vn.flags["tcolor"]

        if self.args.js_other and "js" not in ka:
            zs = self.args.js_other
            zs += "&" if "?" in zs else "?"
            ka["js"] = zs

        if "html_head_d" in self.vn.flags:
            ka["this"] = self
            self._build_html_head(ka)

        ka["html_head"] = self.html_head
        return tpl.render(**ka)  # type: ignore

    def j2j(self, name )  :
        return self.conn.hsrv.j2[name]

    def run(self)  :
        """returns true if connection can be reused"""
        self.out_headers = {
            "Vary": "Origin, PW, Cookie",
            "Cache-Control": "no-store, max-age=0",
        }

        if self.args.early_ban and self.is_banned():
            return False

        if self.conn.ipa_nm and not self.conn.ipa_nm.map(self.conn.addr[0]):
            self.log("client rejected (--ipa)", 3)
            self.terse_reply(b"", 500)
            return False

        try:
            self.s.settimeout(2)
            headerlines = read_header(self.sr, self.args.s_thead, self.args.s_thead)
            self.in_hdr_recv = False
            if not headerlines:
                return False

            if not headerlines[0]:
                # seen after login with IE6.0.2900.5512.xpsp.080413-2111 (xp-sp3)
                self.log("BUG: trailing newline from previous request", c="1;31")
                headerlines.pop(0)

            try:
                self.mode, self.req, self.http_ver = headerlines[0].split(" ")

                # normalize incoming headers to lowercase;
                # outgoing headers however are Correct-Case
                for header_line in headerlines[1:]:
                    k, zs = header_line.split(":", 1)
                    self.headers[k.lower()] = zs.strip()
            except:
                headerlines = [repr(x) for x in headerlines]
                msg = "#[ " + " ]\n#[ ".join(headerlines) + " ]"
                raise Pebkac(400, "bad headers", log=msg)

        except Pebkac as ex:
            self.mode = "GET"
            self.req = "[junk]"
            self.http_ver = "HTTP/1.1"
            # self.log("pebkac at httpcli.run #1: " + repr(ex))
            self.keepalive = False
            h = {"WWW-Authenticate": 'Basic realm="a"'} if ex.code == 401 else {}
            try:
                self.loud_reply(unicode(ex), status=ex.code, headers=h, volsan=True)
            except:
                pass

            if ex.log:
                self.log("additional error context:\n" + ex.log, 6)

            return False

        self.conn.hsrv.nreq += 1

        self.ua = self.headers.get("user-agent", "")
        self.is_rclone = self.ua.startswith("rclone/")

        zs = self.headers.get("connection", "").lower()
        self.keepalive = "close" not in zs and (
            self.http_ver != "HTTP/1.0" or zs == "keep-alive"
        )
        self.is_https = (
            self.headers.get("x-forwarded-proto", "").lower() == "https" or self.tls
        )
        self.host = self.headers.get("host") or ""
        if not self.host:
            if self.s.family == socket.AF_UNIX:
                self.host = self.args.name
            else:
                zs = "%s:%s" % self.s.getsockname()[:2]
                self.host = zs[7:] if zs.startswith("::ffff:") else zs

        trusted_xff = False
        n = self.args.rproxy
        if n:
            zso = self.headers.get(self.args.xff_hdr)
            if zso:
                if n > 0:
                    n -= 1

                zsl = zso.split(",")
                try:
                    cli_ip = zsl[n].strip()
                except:
                    cli_ip = self.ip
                    self.bad_xff = True
                    if self.args.rproxy != 9999999:
                        t = "global-option --rproxy %d could not be used (out-of-bounds) for the received header [%s]"
                        self.log(t % (self.args.rproxy, zso), c=3)
                    else:
                        zsl = [
                            "  rproxy: %d   if this client's IP-address is [%s]"
                            % (-1 - zd, zs.strip())
                            for zd, zs in enumerate(zsl[::-1])
                        ]
                        t = 'could not determine the client\'s IP-address because the global-option --rproxy has not been configured, so the request-header [%s] specified by global-option --xff-hdr cannot be used safely! The raw header value was [%s]. Please see the "reverse-proxy" section in the readme. The best approach is to configure your reverse-proxy to give copyparty the exact IP-address to assume (perhaps in another header), but you may also try the following:'
                        t = t % (self.args.xff_hdr, zso)
                        self.log("%s\n\n%s\n" % (t, "\n".join(zsl)), 3)

                pip = self.conn.addr[0]
                xffs = self.conn.xff_nm
                if xffs and not xffs.map(pip):
                    t = 'got header "%s" from untrusted source "%s" claiming the true client ip is "%s" (raw value: "%s");  if you trust this, you must allowlist this proxy with "--xff-src=%s"%s'
                    if self.headers.get("cf-connecting-ip"):
                        t += '  Note: if you are behind cloudflare, then this default header is not a good choice; please first make sure your local reverse-proxy (if any) does not allow non-cloudflare IPs from providing cf-* headers, and then add this additional global setting: "--xff-hdr=cf-connecting-ip"'
                    else:
                        t += '  Note: depending on your reverse-proxy, and/or WAF, and/or other intermediates, you may want to read the true client IP from another header by also specifying "--xff-hdr=SomeOtherHeader"'

                    if "." in pip:
                        zs = ".".join(pip.split(".")[:2]) + ".0.0/16"
                    else:
                        zs = IPv6Network(pip + "/64", False).compressed

                    zs2 = ' or "--xff-src=lan"' if self.conn.xff_lan.map(pip) else ""
                    self.log(t % (self.args.xff_hdr, pip, cli_ip, zso, zs, zs2), 3)
                    self.bad_xff = True
                else:
                    self.ip = cli_ip
                    self.log_src = self.conn.set_rproxy(self.ip)
                    self.host = self.headers.get("x-forwarded-host") or self.host
                    trusted_xff = True

        m = RE_HOST.search(self.host)
        if m and self.host != self.args.name:
            zs = self.host
            t = "malicious user; illegal Host header; req(%r) host(%r) => %r"
            self.log(t % (self.req, zs, zs[m.span()[0] :]), 1)
            self.cbonk(self.conn.hsrv.gmal, zs, "bad_host", "illegal Host header")
            self.terse_reply(b"illegal Host header", 400)
            return False

        if self.is_banned():
            return False

        if self.conn.aclose:
            nka = self.conn.aclose
            ip = ipnorm(self.ip)
            if ip in nka:
                rt = nka[ip] - time.time()
                if rt < 0:
                    self.log("client uncapped", 3)
                    del nka[ip]
                else:
                    self.keepalive = False

        ptn  = self.conn.lf_url  # mypy404
        self.do_log = not ptn or not ptn.search(self.req)

        if self.args.ihead and self.do_log:
            keys = self.args.ihead
            if "*" in keys:
                keys = list(sorted(self.headers.keys()))

            for k in keys:
                zso = self.headers.get(k)
                if zso is not None:
                    self.log("[H] {}: \033[33m[{}]".format(k, zso), 6)

        if "&" in self.req and "?" not in self.req:
            self.hint = "did you mean '?' instead of '&'"

        if self.args.uqe and "/.uqe/" in self.req:
            try:
                vpath, query = self.req.split("?")[0].split("/.uqe/")
                query = query.split("/")[0]  # discard trailing junk
                # (usually a "filename" to trick discord into behaving)
                query = ub64dec(query.encode("utf-8")).decode("utf-8", "replace")
                if query.startswith("/"):
                    self.req = "%s/?%s" % (vpath, query[1:])
                else:
                    self.req = "%s?%s" % (vpath, query)
            except Exception as ex:
                t = "bad uqe in request [%s]: %r" % (self.req, ex)
                self.loud_reply(t, status=400)
                return False

        ptn_cc = RE_CC
        m = ptn_cc.search(self.req)
        if m:
            zs = self.req
            t = "malicious user; Cc in req0 %r => %r"
            self.log(t % (zs, zs[m.span()[0] :]), 1)
            self.cbonk(self.conn.hsrv.gmal, zs, "cc_r0", "Cc in req0")
            self.terse_reply(b"", 500)
            return False

        # split req into vpath + uparam
        uparam = {}
        if "?" not in self.req:
            vpath = unquotep(self.req)  # not query, so + means +
            self.trailing_slash = vpath.endswith("/")
            vpath = undot(vpath)
        else:
            vpath, arglist = self.req.split("?", 1)
            vpath = unquotep(vpath)
            self.trailing_slash = vpath.endswith("/")
            vpath = undot(vpath)

            re_k = RE_K
            k_safe = UPARAM_CC_OK
            for k in arglist.split("&"):
                if "=" in k:
                    k, zs = k.split("=", 1)
                    # x-www-form-urlencoded (url query part) uses
                    # either + or %20 for 0x20 so handle both
                    sv = unquotep(zs.strip().replace("+", " "))
                else:
                    sv = ""

                m = re_k.search(k)
                if m:
                    t = "malicious user; bad char in query key; req(%r) qk(%r) => %r"
                    self.log(t % (self.req, k, k[m.span()[0] :]), 1)
                    self.cbonk(self.conn.hsrv.gmal, self.req, "bc_q", "illegal qkey")
                    self.terse_reply(b"", 500)
                    return False

                k = k.lower()
                uparam[k] = sv

                if k in k_safe:
                    continue

                zs = "%s=%s" % (k, sv)
                m = ptn_cc.search(zs)
                if not m:
                    continue

                t = "malicious user; Cc in query; req(%r) qp(%r) => %r"
                self.log(t % (self.req, zs, zs[m.span()[0] :]), 1)
                self.cbonk(self.conn.hsrv.gmal, self.req, "cc_q", "Cc in query")
                self.terse_reply(b"", 500)
                return False

            if "k" in uparam:
                m = re_k.search(uparam["k"])
                if m:
                    zs = uparam["k"]
                    t = "malicious user; illegal filekey; req(%r) k(%r) => %r"
                    self.log(t % (self.req, zs, zs[m.span()[0] :]), 1)
                    self.cbonk(self.conn.hsrv.gmal, zs, "bad_k", "illegal filekey")
                    self.terse_reply(b"illegal filekey", 400)
                    return False

        if self.is_vproxied:
            if vpath.startswith(self.args.R):
                vpath = vpath[len(self.args.R) + 1 :]
            else:
                t = "incorrect --rp-loc or webserver config; expected vpath starting with %r but got %r"
                self.log(t % (self.args.R, vpath), 1)
                self.is_vproxied = False

        self.ouparam = uparam.copy()

        if self.args.rsp_slp:
            time.sleep(self.args.rsp_slp)
            if self.args.rsp_jtr:
                time.sleep(random.random() * self.args.rsp_jtr)

        zso = self.headers.get("cookie")
        if zso:
            if len(zso) > self.args.cookie_cmax:
                self.loud_reply("cookie header too big", status=400)
                return False
            zsll = [x.split("=", 1) for x in zso.split(";") if "=" in x]
            cookies = {k.strip(): unescape_cookie(zs) for k, zs in zsll}
            cookie_pw = cookies.get("cppws" if self.is_https else "cppwd") or ""
            if "b" in cookies and "b" not in uparam:
                uparam["b"] = cookies["b"]
            if len(cookies) > self.args.cookie_nmax:
                self.loud_reply("too many cookies", status=400)
        else:
            cookies = {}
            cookie_pw = ""

        if len(uparam) > 12:
            t = "http-request rejected; num.params: %d %r"
            self.log(t % (len(uparam), self.req), 3)
            self.loud_reply("u wot m8", status=400)
            return False

        self.uparam = uparam
        self.cookies = cookies
        self.vpath = vpath
        self.vpaths = (
            self.vpath + "/" if self.trailing_slash and self.vpath else self.vpath
        )

        if "qr" in uparam:
            return self.tx_qr()

        if relchk(self.vpath) and (self.vpath != "*" or self.mode != "OPTIONS"):
            self.log("illegal relpath; req(%r) => %r" % (self.req, "/" + self.vpath))
            self.cbonk(self.conn.hsrv.gmal, self.req, "bad_vp", "invalid relpaths")
            return self.tx_404() and self.keepalive

        zso = self.headers.get("authorization")
        bauth = ""
        if (
            zso
            and not self.args.no_bauth
            and (not cookie_pw or not self.args.bauth_last)
        ):
            try:
                zb = zso.split(" ")[1].encode("ascii")
                zs = b64dec(zb).decode("utf-8")
                # try "pwd", "x:pwd", "pwd:x"
                for bauth in [zs] + zs.split(":", 1)[::-1]:
                    if bauth in self.asrv.sesa:
                        break
                    hpw = self.asrv.ah.hash(bauth)
                    if self.asrv.iacct.get(hpw):
                        break
            except:
                pass

        self.pw = uparam.get("pw") or self.headers.get("pw") or bauth or cookie_pw
        self.uname = (
            self.asrv.sesa.get(self.pw)
            or self.asrv.iacct.get(self.asrv.ah.hash(self.pw))
            or "*"
        )

        if self.args.have_idp_hdrs and (
            self.uname == "*" or self.args.ao_idp_before_pw
        ):
            idp_usr = ""
            if self.args.idp_hm_usr:
                for hn, hmv in self.args.idp_hm_usr_p.items():
                    zs = self.headers.get(hn)
                    if zs:
                        for zs1, zs2 in hmv.items():
                            if zs == zs1:
                                idp_usr = zs2
                                break
                    if idp_usr:
                        break
            for hn in self.args.idp_h_usr:
                if idp_usr and not self.args.ao_h_before_hm:
                    break
                idp_usr = self.headers.get(hn) or idp_usr
            if idp_usr:
                idp_grp = (
                    self.headers.get(self.args.idp_h_grp) or ""
                    if self.args.idp_h_grp
                    else ""
                )

                if not trusted_xff:
                    pip = self.conn.addr[0]
                    xffs = self.conn.xff_nm
                    trusted_xff = xffs and xffs.map(pip)

                trusted_key = (
                    not self.args.idp_h_key
                ) or self.args.idp_h_key in self.headers

                if trusted_key and trusted_xff:
                    if idp_usr.lower() == LEELOO_DALLAS:
                        self.loud_reply("send her back", status=403)
                        return False
                    self.asrv.idp_checkin(self.conn.hsrv.broker, idp_usr, idp_grp)
                else:
                    if not trusted_key:
                        t = 'the idp-h-key header ("%s") is not present in the request; will NOT trust the other headers saying that the client\'s username is "%s" and group is "%s"'
                        self.log(t % (self.args.idp_h_key, idp_usr, idp_grp), 3)

                    if not trusted_xff:
                        t = 'got IdP headers from untrusted source "%s" claiming the client\'s username is "%s" and group is "%s";  if you trust this, you must allowlist this proxy with "--xff-src=%s"%s'
                        if not self.args.idp_h_key:
                            t += "  Note: you probably also want to specify --idp-h-key <SECRET-HEADER-NAME> for additional security"

                        pip = self.conn.addr[0]
                        zs = (
                            ".".join(pip.split(".")[:2]) + "."
                            if "." in pip
                            else ":".join(pip.split(":")[:4]) + ":"
                        ) + "0.0/16"
                        zs2 = (
                            ' or "--xff-src=lan"' if self.conn.xff_lan.map(pip) else ""
                        )
                        self.log(t % (pip, idp_usr, idp_grp, zs, zs2), 3)

                    idp_usr = "*"
                    idp_grp = ""

                if idp_usr in self.asrv.vfs.aread:
                    self.pw = ""
                    self.uname = idp_usr
                    if self.args.ao_have_pw or self.args.idp_logout:
                        self.html_head += "<script>var is_idp=1</script>\n"
                    else:
                        self.html_head += "<script>var is_idp=2</script>\n"
                    zs = self.asrv.ases.get(idp_usr)
                    if zs:
                        self.set_idp_cookie(zs)
                else:
                    self.log("unknown username: %r" % (idp_usr,), 1)

        if self.args.have_ipu_or_ipr:
            if self.args.ipu and (self.uname == "*" or self.args.ao_ipu_wins):
                self.uname = self.conn.ipu_iu[self.conn.ipu_nm.map(self.ip)]
            ipr = self.conn.hsrv.ipr
            if ipr and self.uname in ipr:
                if not ipr[self.uname].map(self.ip):
                    self.log("username [%s] rejected by --ipr" % (self.uname,), 3)
                    self.uname = "*"

        self.rvol = self.asrv.vfs.aread[self.uname]
        self.wvol = self.asrv.vfs.awrite[self.uname]
        self.avol = self.asrv.vfs.aadmin[self.uname]

        if self.pw and (
            self.pw != cookie_pw or self.conn.freshen_pwd + 30 < time.time()
        ):
            self.conn.freshen_pwd = time.time()
            self.get_pwd_cookie(self.pw)

        if self.is_rclone:
            # dots: always include dotfiles if permitted
            # lt: probably more important showing the correct timestamps of any dupes it just uploaded rather than the lastmod time of any non-copyparty-managed symlinks
            # b: basic-browser if it tries to parse the html listing
            uparam["dots"] = ""
            uparam["lt"] = ""
            uparam["b"] = ""
            cookies["b"] = ""

        vn, rem = self.asrv.vfs.get(self.vpath, self.uname, False, False)
        if vn.realpath and ("xdev" in vn.flags or "xvol" in vn.flags):
            ap = vn.canonical(rem)
            avn = vn.chk_ap(ap)
        else:
            avn = vn

        if "bcasechk" in vn.flags and not vn.casechk(rem, True):
            return self.tx_404() and False

        (
            self.can_read,
            self.can_write,
            self.can_move,
            self.can_delete,
            self.can_get,
            self.can_upget,
            self.can_admin,
            self.can_dot,
        ) = (
            avn.can_access("", self.uname) if avn else [False] * 8
        )
        self.avn = avn
        self.vn = vn  # note: do not dbv due to walk/zipgen
        self.rem = rem

        self.s.settimeout(self.args.s_tbody or None)

        if "norobots" in vn.flags:
            self.out_headers["X-Robots-Tag"] = "noindex, nofollow"

        if "html_head_s" in vn.flags:
            self.html_head += vn.flags["html_head_s"]

        try:
            cors_k = self._cors()
            if self.mode in ("GET", "HEAD"):
                return self.handle_get() and self.keepalive
            if self.mode == "OPTIONS":
                return self.handle_options() and self.keepalive

            if not cors_k:
                host = self.headers.get("host", "<?>")
                origin = self.headers.get("origin", "<?>")
                proto = "https://" if self.is_https else "http://"
                guess = "modifying" if (origin and host) else "stripping"
                t = "cors-reject %s because request-header Origin=%r does not match request-protocol %r and host %r based on request-header Host=%r (note: if this request is not malicious, check if your reverse-proxy is accidentally %s request headers, in particular 'Origin', for example by running copyparty with --ihead='*' to show all request headers)"
                self.log(t % (self.mode, origin, proto, self.host, host, guess), 3)
                raise Pebkac(403, "rejected by cors-check")

            # getattr(self.mode) is not yet faster than this
            if self.mode == "POST":
                return self.handle_post() and self.keepalive
            elif self.mode == "PUT":
                return self.handle_put() and self.keepalive
            elif self.mode == "PROPFIND":
                return self.handle_propfind() and self.keepalive
            elif self.mode == "DELETE":
                return self.handle_delete() and self.keepalive
            elif self.mode == "PROPPATCH":
                return self.handle_proppatch() and self.keepalive
            elif self.mode == "LOCK":
                return self.handle_lock() and self.keepalive
            elif self.mode == "UNLOCK":
                return self.handle_unlock() and self.keepalive
            elif self.mode == "MKCOL":
                return self.handle_mkcol() and self.keepalive
            elif self.mode in ("MOVE", "COPY"):
                return self.handle_cpmv() and self.keepalive
            else:
                raise Pebkac(400, "invalid HTTP verb %r" % (self.mode,))

        except Exception as ex:
            if not isinstance(ex, Pebkac):
                pex = Pebkac(500)
            else:
                pex  = ex  # type: ignore

            try:
                if pex.code == 999:
                    self.terse_reply(b"", 500)
                    return False

                post = self.mode in ["POST", "PUT"] or "content-length" in self.headers
                if not self._check_nonfatal(pex, post):
                    self.keepalive = False

                em = str(ex)
                msg = em if pex is ex else min_ex()

                if pex.code != 404 or self.do_log:
                    self.log(
                        "http%d: %s\033[0m, %r" % (pex.code, msg, "/" + self.vpath),
                        6 if em.startswith("client d/c ") else 3,
                    )

                if self.hint and self.hint.startswith("<xml> "):
                    if self.args.log_badxml:
                        t = "invalid XML received from client: %r"
                        self.log(t % (self.hint[6:],), 6)
                    else:
                        t = "received invalid XML from client; enable --log-badxml to see the whole XML in the log"
                        self.log(t, 6)
                    self.hint = ""

                msg = "%s\r\nURL: %s\r\n" % (em, self.vpath)
                if self.hint:
                    msg += "hint: %s\r\n" % (self.hint,)

                if "database is locked" in em:
                    self.conn.hsrv.broker.say("log_stacks")
                    msg += "hint: important info in the server log\r\n"

                zb = b"<pre>" + html_escape(msg).encode("utf-8", "replace")
                h = {"WWW-Authenticate": 'Basic realm="a"'} if pex.code == 401 else {}
                self.reply(zb, status=pex.code, headers=h, volsan=True)
                if pex.log:
                    self.log("additional error context:\n" + pex.log, 6)

                return self.keepalive
            except Pebkac:
                return False

        finally:
            if self.dl_id:
                self.conn.hsrv.dli.pop(self.dl_id, None)
                self.conn.hsrv.dls.pop(self.dl_id, None)

    def dip(self)  :
        if self.args.plain_ip:
            return self.ip.replace(":", ".")
        else:
            return self.conn.iphash.s(self.ip)

    def cbonk(self, g , v , reason , descr )  :
        cond = self.args.dont_ban
        if (
            cond == "any"
            or (cond == "auth" and self.uname != "*")
            or (cond == "aa" and self.avol)
            or (cond == "av" and self.can_admin)
            or (cond == "rw" and self.can_read and self.can_write)
        ):
            return False

        self.conn.hsrv.nsus += 1
        if not g.lim:
            return False

        bonk, ip = g.bonk(self.ip, v + self.gctx)
        if not bonk:
            return False

        xban = self.vn.flags.get("xban")
        if not xban or not runhook(
            self.log,
            self.conn.hsrv.broker,
            None,
            "xban",
            xban,
            self.vn.canonical(self.rem),
            self.vpath,
            self.host,
            self.uname,
            "",
            time.time(),
            0,
            self.ip,
            time.time(),
            [reason, reason],
        ):
            self.log("client banned: %s" % (descr,), 1)
            self.conn.hsrv.bans[ip] = bonk
            self.conn.hsrv.nban += 1
            return True

        return False

    def is_banned(self)  :
        if not self.conn.bans:
            return False

        bans = self.conn.bans
        ip = ipnorm(self.ip)
        if ip not in bans:
            return False

        rt = bans[ip] - time.time()
        if rt < 0:
            self.log("client unbanned", 3)
            del bans[ip]
            return False

        self.log("banned for {:.0f} sec".format(rt), 6)
        self.terse_reply(b"thank you for playing", 403)
        return True

    def permit_caching(self)  :
        cache = self.uparam.get("cache")
        if cache is None:
            self.out_headers.update(NO_CACHE)
            return

        n = 69 if not cache else 604869 if cache == "i" else int(cache)
        self.out_headers["Cache-Control"] = "max-age=" + str(n)

    def k304(self)  :
        k304 = self.cookies.get("k304")
        return k304 == "y" or (self.args.k304 == 2 and k304 != "n")

    def no304(self)  :
        no304 = self.cookies.get("no304")
        return no304 == "y" or (self.args.no304 == 2 and no304 != "n")

    def _build_html_head(self, kv  )  :
        html = str(self.vn.flags["html_head_d"])
        is_jinja = html[:2] in "%@%"
        if is_jinja:
            html = html.replace("%", "", 1)

        if html.startswith("@"):
            html = read_utf8(self.log, html[1:], True)

        if html.startswith("%"):
            html = html[1:]
            is_jinja = True

        if is_jinja:
            with self.conn.hsrv.mutex:
                if html not in self.conn.hsrv.j2:
                    j2env = jinja2.Environment()
                    tpl = j2env.from_string(html)
                    self.conn.hsrv.j2[html] = tpl
                html = self.conn.hsrv.j2[html].render(**kv)

        self.html_head += html + "\n"

    def send_headers(
        self,
        length ,
        status  = 200,
        mime  = None,
        headers   = None,
    )  :
        response = ["%s %s %s" % (self.http_ver, status, HTTPCODE[status])]

        # headers{} overrides anything set previously
        if headers:
            self.out_headers.update(headers)

        if status == 304:
            self.out_headers.pop("Content-Length", None)
            self.out_headers.pop("Content-Type", None)
            self.out_headerlist[:] = []
            if self.k304():
                self.keepalive = False
        else:
            if length is not None:
                response.append("Content-Length: " + unicode(length))

            if mime:
                self.out_headers["Content-Type"] = mime
            elif "Content-Type" not in self.out_headers:
                self.out_headers["Content-Type"] = "text/html; charset=utf-8"

        # close if unknown length, otherwise take client's preference
        response.append(H_CONN_KEEPALIVE if self.keepalive else H_CONN_CLOSE)
        response.append("Date: " + formatdate())

        for k, zs in list(self.out_headers.items()) + self.out_headerlist:
            response.append("%s: %s" % (k, zs))

        ptn_cc = RE_CC
        for zs in response:
            m = ptn_cc.search(zs)
            if m:
                t = "malicious user; Cc in out-hdr; req(%r) hdr(%r) => %r"
                self.log(t % (self.req, zs, zs[m.span()[0] :]), 1)
                self.cbonk(self.conn.hsrv.gmal, zs, "cc_hdr", "Cc in out-hdr")
                raise Pebkac(999)

        if self.args.ohead and self.do_log:
            keys = self.args.ohead
            if "*" in keys:
                lines = response[1:]
            else:
                lines = []
                for zs in response[1:]:
                    if zs.split(":")[0].lower() in keys:
                        lines.append(zs)
            for zs in lines:
                hk, hv = zs.split(": ")
                self.log("[O] {}: \033[33m[{}]".format(hk, hv), 5)

        response.append("\r\n")
        try:
            self.s.sendall("\r\n".join(response).encode("utf-8"))
        except:
            raise Pebkac(400, "client d/c while replying headers")

    def reply(
        self,
        body ,
        status  = 200,
        mime  = None,
        headers   = None,
        volsan  = False,
    )  :
        if (
            status > 400
            and status in (403, 404, 422)
            and (
                status != 422
                or (
                    not body.startswith(b"<pre>partial upload exists")
                    and not body.startswith(b"<pre>source file busy")
                )
            )
            and (status != 404 or (self.can_get and not self.can_read))
        ):
            if status == 404:
                g = self.conn.hsrv.g404
            elif status == 403:
                g = self.conn.hsrv.g403
            else:
                g = self.conn.hsrv.g422

            gurl = self.conn.hsrv.gurl
            if (
                gurl.lim
                and (not g.lim or gurl.lim < g.lim)
                and self.args.sus_urls.search(self.vpath)
            ):
                g = self.conn.hsrv.gurl

            if g.lim and (
                g == self.conn.hsrv.g422
                or not self.args.nonsus_urls
                or not self.args.nonsus_urls.search(self.vpath)
            ):
                self.cbonk(g, self.vpath, str(status), "%ss" % (status,))

        if volsan:
            vols = list(self.asrv.vfs.all_vols.values())
            body = vol_san(vols, body)
            try:
                zs = absreal(__file__).rsplit(os.path.sep, 2)[0]
                body = body.replace(zs.encode("utf-8"), b"PP")
            except:
                pass

        self.send_headers(len(body), status, mime, headers)

        try:
            if self.mode != "HEAD":
                self.s.sendall(body)
        except:
            raise Pebkac(400, "client d/c while replying body")

        return body

    def loud_reply(self, body , *args , **kwargs )  :
        if not kwargs.get("mime"):
            kwargs["mime"] = "text/plain; charset=utf-8"

        self.log(body.rstrip())
        self.reply(body.encode("utf-8") + b"\r\n", *list(args), **kwargs)

    def terse_reply(self, body , status  = 200)  :
        self.keepalive = False

        lines = [
            "%s %s %s" % (self.http_ver or "HTTP/1.1", status, HTTPCODE[status]),
            H_CONN_CLOSE,
        ]

        if body:
            lines.append("Content-Length: " + unicode(len(body)))

        lines.append("\r\n")
        self.s.sendall("\r\n".join(lines).encode("utf-8") + body)

    def urlq(self, add  , rm )  :
        """
        generates url query based on uparam (b, pw, all others)
        removing anything in rm, adding pairs in add

        also list faster than set until ~20 items
        """

        if self.is_rclone:
            return ""

        kv = {k: zs for k, zs in self.uparam.items() if k not in rm}
        if "pw" in kv:
            pw = self.cookies.get("cppws") or self.cookies.get("cppwd")
            if kv["pw"] == pw:
                del kv["pw"]

        kv.update(add)
        if not kv:
            return ""

        r = ["%s=%s" % (quotep(k), quotep(zs)) if zs else k for k, zs in kv.items()]
        return "?" + "&amp;".join(r)

    def ourlq(self)  :
        skip = ("pw", "h", "k")
        ret = []
        for k, v in self.ouparam.items():
            if k in skip:
                continue

            t = "%s=%s" % (quotep(k), quotep(v))
            ret.append(t.replace(" ", "+").rstrip("="))

        if not ret:
            return ""

        return "?" + "&".join(ret)

    def redirect(
        self,
        vpath ,
        suf  = "",
        msg  = "aight",
        flavor  = "go to",
        click  = True,
        status  = 200,
        use302  = False,
    )  :
        vp = self.args.SRS + vpath
        html = self.j2s(
            "msg",
            h2='<a href="{}">{} {}</a>'.format(
                quotep(vp) + suf, flavor, html_escape(vp, crlf=True) + suf
            ),
            pre=msg,
            click=click,
        ).encode("utf-8", "replace")

        if use302:
            self.reply(html, status=302, headers={"Location": vp})
        else:
            self.reply(html, status=status)

        return True

    def _cors(self)  :
        ih = self.headers
        origin = ih.get("origin")
        if not origin:
            sfsite = ih.get("sec-fetch-site")
            if sfsite and sfsite.lower().startswith("cross"):
                origin = ":|"  # sandboxed iframe
            else:
                return True

        host = self.host.lower()
        if host.startswith("["):
            if "]:" in host:
                host = host.split("]:")[0] + "]"
        else:
            host = host.split(":")[0]

        oh = self.out_headers
        origin = origin.lower()
        proto = "https" if self.is_https else "http"
        good_origins = self.args.acao + ["%s://%s" % (proto, host)]

        if "pw" in ih or re.sub(r"(:[0-9]{1,5})?/?$", "", origin) in good_origins:
            good_origin = True
            bad_hdrs = ("",)
        else:
            good_origin = False
            bad_hdrs = ("", "pw")

        # '*' blocks auth through cookies / WWW-Authenticate;
        # exact-match for Origin is necessary to unlock those,
        # but the ?pw= param and PW: header are always allowed
        acah = ih.get("access-control-request-headers", "")
        acao = (origin if good_origin else None) or (
            "*" if "*" in good_origins else None
        )
        if self.args.allow_csrf:
            acao = origin or acao or "*"  # explicitly permit impersonation
            acam = ", ".join(self.conn.hsrv.mallow)  # and all methods + headers
            oh["Access-Control-Allow-Credentials"] = "true"
            good_origin = True
        else:
            acam = ", ".join(self.args.acam)
            # wash client-requested headers and roll with that
            if "range" not in acah.lower():
                acah += ",Range"  # firefox
            req_h = acah.split(",")
            req_h = [x.strip() for x in req_h]
            req_h = [x for x in req_h if x.lower() not in bad_hdrs]
            acah = ", ".join(req_h)

        if not acao:
            return False

        oh["Access-Control-Allow-Origin"] = acao
        oh["Access-Control-Allow-Methods"] = acam.upper()
        if acah:
            oh["Access-Control-Allow-Headers"] = acah

        return good_origin

    def handle_get(self)  :
        if self.do_log:
            logmsg = "%-4s %s @%s" % (self.mode, self.req, self.uname)

            if "range" in self.headers:
                try:
                    rval = self.headers["range"].split("=", 1)[1]
                except:
                    rval = self.headers["range"]

                logmsg += " [\033[36m" + rval + "\033[0m]"

            self.log(logmsg)
            if "%" in self.req:
                self.log(" `-- %r" % (self.vpath,))

        # "embedded" resources
        if self.vpath.startswith(".cpr"):
            if self.vpath.startswith(".cpr/ico/"):
                return self.tx_ico(self.vpath.split("/")[-1], exact=True)

            if self.vpath.startswith(".cpr/ssdp"):
                if self.conn.hsrv.ssdp:
                    return self.conn.hsrv.ssdp.reply(self)
                else:
                    self.reply(b"ssdp is disabled in server config", 404)
                    return False

            if self.vpath == ".cpr/metrics":
                return self.conn.hsrv.metrics.tx(self)

            res_path = "web/" + self.vpath[5:]
            if res_path in RES:
                ap = self.E.mod_ + res_path
                if bos.path.exists(ap) or bos.path.exists(ap + ".gz"):
                    return self.tx_file(ap)
                else:
                    return self.tx_res(res_path)

            self.tx_404()
            return False

        if "cf_challenge" in self.uparam:
            self.reply(self.j2s("cf").encode("utf-8", "replace"))
            return True

        if not self.can_read and not self.can_write and not self.can_get:
            t = "@%s has no access to %r"

            if self.vn.realpath and "on403" in self.vn.flags:
                t += " (on403)"
                self.log(t % (self.uname, "/" + self.vpath))
                ret = self.on40x(self.vn.flags["on403"], self.vn, self.rem)
                if ret == "true":
                    return True
                elif ret == "false":
                    return False
                elif ret == "home":
                    self.uparam["h"] = ""
                elif ret == "allow":
                    self.log("plugin override; access permitted")
                    self.can_read = self.can_write = self.can_move = True
                    self.can_delete = self.can_get = self.can_upget = True
                    self.can_admin = True
                else:
                    return self.tx_404(True)
            else:
                if (
                    self.asrv.badcfg1
                    and "h" not in self.ouparam
                    and "hc" not in self.ouparam
                ):
                    zs1 = "copyparty refused to start due to a failsafe: invalid server config; check server log"
                    zs2 = 'you may <a href="/?h">access the controlpanel</a> but nothing will work until you shutdown the copyparty container and %s config-file (or provide the configuration as command-line arguments)'
                    if self.asrv.is_lxc and len(self.asrv.cfg_files_loaded) == 1:
                        zs2 = zs2 % ("add a",)
                    else:
                        zs2 = zs2 % ("fix the",)

                    html = self.j2s("msg", h1=zs1, h2=zs2)
                    self.reply(html.encode("utf-8", "replace"), 500)
                    return True

                if "ls" in self.uparam:
                    return self.tx_ls_vols()

                if self.vpath:
                    ptn = self.args.nonsus_urls
                    if not ptn or not ptn.search(self.vpath):
                        self.log(t % (self.uname, "/" + self.vpath))

                    return self.tx_404(True)

                self.uparam["h"] = ""

        if "tree" in self.uparam:
            return self.tx_tree()

        if "scan" in self.uparam:
            return self.scanvol()

        if self.args.getmod:
            if "delete" in self.uparam:
                return self.handle_rm([])

            if "move" in self.uparam:
                return self.handle_mv()

            if "copy" in self.uparam:
                return self.handle_cp()

        if not self.vpath and self.ouparam:
            if "reload" in self.uparam:
                return self.handle_reload()

            if "stack" in self.uparam:
                return self.tx_stack()

            if "setck" in self.uparam:
                return self.setck()

            if "reset" in self.uparam:
                return self.set_cfg_reset()

            if "hc" in self.uparam:
                return self.tx_svcs()

            if "shares" in self.uparam:
                return self.tx_shares()

            if "dls" in self.uparam:
                return self.tx_dls()

            if "ru" in self.uparam:
                return self.tx_rups()

            if "idp" in self.uparam:
                return self.tx_idp()

        if "h" in self.uparam:
            return self.tx_mounts()

        if "ups" in self.uparam:
            # vpath is used for share translation
            return self.tx_ups()

        if "rss" in self.uparam:
            return self.tx_rss()

        return self.tx_browser()

    def tx_rss(self)  :
        if self.do_log:
            self.log("RSS  %s @%s" % (self.req, self.uname))

        if not self.can_read:
            return self.tx_404(True)

        vn = self.vn
        if not vn.flags.get("rss"):
            raise Pebkac(405, "RSS is disabled in server config")

        rem = self.rem
        idx = self.conn.get_u2idx()
        if not idx or not hasattr(idx, "p_end"):
            if not HAVE_SQLITE3:
                raise Pebkac(500, "sqlite3 not found on server; rss is disabled")
            raise Pebkac(500, "server busy, cannot generate rss; please retry in a bit")

        uv = [rem]
        if "recursive" in self.uparam:
            uq = "up.rd like ?||'%'"
        else:
            uq = "up.rd == ?"

        zs = str(self.uparam.get("fext", self.args.rss_fext))
        if zs in ("True", "False"):
            zs = ""
        if zs:
            zsl = []
            for ext in zs.split(","):
                zsl.append("+up.fn like '%.'||?")
                uv.append(ext)
            uq += " and ( %s )" % (" or ".join(zsl),)

        zs1 = self.uparam.get("sort", self.args.rss_sort)
        zs2 = zs1.lower()
        zs = RSS_SORT.get(zs2)
        if not zs:
            raise Pebkac(400, "invalid sort key; must be m/u/n/s")

        uq += " order by up." + zs
        if zs1 == zs2:
            uq += " desc"

        nmax = int(self.uparam.get("nf") or self.args.rss_nf)

        hits = idx.run_query(self.uname, [self.vn], uq, uv, False, False, nmax)[0]

        if "pw" in self.ouparam and "nopw" not in self.ouparam:
            zs = self.ouparam["pw"]
            q_pw = "?pw=%s" % (quotep(zs),)
            a_pw = "&pw=%s" % (quotep(zs),)
            for i in hits:
                i["rp"] += a_pw if "?" in i["rp"] else q_pw
        else:
            q_pw = a_pw = ""

        title = self.uparam.get("title") or self.vpath.split("/")[-1]
        etitle = html_escape(title, True, True)

        baseurl = "%s://%s/" % (
            "https" if self.is_https else "http",
            self.host,
        )
        feed = baseurl + self.req[1:]
        if "pw" in self.ouparam and self.ouparam.get("nopw") == "a":
            feed = re.sub(r"&pw=[^&]*", "", feed)
        if self.is_vproxied:
            baseurl += self.args.RS
        efeed = html_escape(feed, True, True)
        edirlink = efeed.split("?")[0] + q_pw

        ret = [
            """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:content="http://purl.org/rss/1.0/modules/content/">
\t<channel>
\t\t<atom:link href="%s" rel="self" type="application/rss+xml" />
\t\t<title>%s</title>
\t\t<description></description>
\t\t<link>%s</link>
\t\t<generator>copyparty-2</generator>
"""
            % (efeed, etitle, edirlink)
        ]

        q = "select fn from cv where rd=? and dn=?"
        crd, cdn = rem.rsplit("/", 1) if "/" in rem else ("", rem)
        try:
            cfn = idx.cur[self.vn.realpath].execute(q, (crd, cdn)).fetchone()[0]
            bos.stat(os.path.join(vn.canonical(rem), cfn))
            cv_url = "%s%s?th=jf%s" % (baseurl, vjoin(self.vpath, cfn), a_pw)
            cv_url = html_escape(cv_url, True, True)
            zs = """\
\t\t<image>
\t\t\t<url>%s</url>
\t\t\t<title>%s</title>
\t\t\t<link>%s</link>
\t\t</image>
"""
            ret.append(zs % (cv_url, etitle, edirlink))
        except:
            pass

        ap = ""
        use_magic = "rmagic" in self.vn.flags

        for i in hits:
            if use_magic:
                ap = os.path.join(self.vn.realpath, i["rp"])

            iurl = html_escape("%s%s" % (baseurl, i["rp"]), True, True)
            title = unquotep(i["rp"].split("?")[0].split("/")[-1])
            title = html_escape(title, True, True)
            tag_t = str(i["tags"].get("title") or "")
            tag_a = str(i["tags"].get("artist") or "")
            desc = "%s - %s" % (tag_a, tag_t) if tag_t and tag_a else (tag_t or tag_a)
            desc = html_escape(desc, True, True) if desc else title
            mime = html_escape(guess_mime(title, ap))
            lmod = formatdate(max(0, i["ts"]))
            zsa = (iurl, iurl, title, desc, lmod, iurl, mime, i["sz"])
            zs = (
                """\
\t\t<item>
\t\t\t<guid>%s</guid>
\t\t\t<link>%s</link>
\t\t\t<title>%s</title>
\t\t\t<description>%s</description>
\t\t\t<pubDate>%s</pubDate>
\t\t\t<enclosure url="%s" type="%s" length="%d"/>
"""
                % zsa
            )
            dur = i["tags"].get(".dur")
            if dur:
                zs += "\t\t\t<itunes:duration>%d</itunes:duration>\n" % (dur,)
            ret.append(zs + "\t\t</item>\n")

        ret.append("\t</channel>\n</rss>\n")
        bret = "".join(ret).encode("utf-8", "replace")
        self.reply(bret, 200, "text/xml; charset=utf-8")
        self.log("rss: %d hits, %d bytes" % (len(hits), len(bret)))
        return True

    def tx_zls(self, abspath)  :
        if self.do_log:
            self.log("zls %s @%s" % (self.req, self.uname))
        if self.args.no_zls:
            raise Pebkac(405, "zip browsing is disabled in server config")

        import zipfile

        try:
            with zipfile.ZipFile(abspath, "r") as zf:
                filelist = [{"fn": f.filename} for f in zf.infolist()]
                ret = json.dumps(filelist).encode("utf-8", "replace")
                self.reply(ret, mime="application/json")
                return True
        except (zipfile.BadZipfile, RuntimeError):
            raise Pebkac(404, "requested file is not a valid zip file")

    def tx_zget(self, abspath)  :
        maxsz = 1024 * 1024 * 64

        inner_path = self.uparam.get("zget")
        if not inner_path:
            raise Pebkac(405, "inner path is required")
        if self.do_log:
            self.log(
                "zget %s \033[35m%s\033[0m @%s" % (self.req, inner_path, self.uname)
            )
        if self.args.no_zls:
            raise Pebkac(405, "zip browsing is disabled in server config")

        import zipfile

        try:
            with zipfile.ZipFile(abspath, "r") as zf:
                zi = zf.getinfo(inner_path)
                if zi.file_size >= maxsz:
                    raise Pebkac(404, "zip bomb defused")
                with zf.open(zi, "r") as fi:
                    self.send_headers(length=zi.file_size, mime=guess_mime(inner_path))

                    sendfile_py(
                        self.log,
                        0,
                        zi.file_size,
                        fi,
                        self.s,
                        self.args.s_wr_sz,
                        self.args.s_wr_slp,
                        not self.args.no_poll,
                        {},
                        "",
                    )
        except KeyError:
            raise Pebkac(404, "no such file in archive")
        except (zipfile.BadZipfile, RuntimeError):
            raise Pebkac(404, "requested file is not a valid zip file")
        return True

    def handle_propfind(self)  :
        if self.do_log:
            self.log("PFIND %s @%s" % (self.req, self.uname))
            if "%" in self.req:
                self.log("  `-- %r" % (self.vpath,))

        if self.args.no_dav:
            raise Pebkac(405, "WebDAV is disabled in server config")

        vn = self.vn
        rem = self.rem
        tap = vn.canonical(rem)

        if "davauth" in vn.flags and self.uname == "*":
            raise Pebkac(401, "authenticate")

        from .dxml import parse_xml

        # enc = "windows-31j"
        # enc = "shift_jis"
        enc = "utf-8"
        uenc = enc.upper()
        props = DAV_ALLPROPS

        clen = int(self.headers.get("content-length", 0))
        if clen:
            buf = b""
            for rbuf in self.get_body_reader()[0]:
                buf += rbuf
                if not rbuf or len(buf) >= 32768:
                    break

            sbuf = buf.decode(enc, "replace")
            self.hint = "<xml> " + sbuf
            xroot = parse_xml(sbuf)
            xtag = next((x for x in xroot if x.tag.split("}")[-1] == "prop"), None)
            if xtag is not None:
                props = set([y.tag.split("}")[-1] for y in xtag])
            # assume <allprop/> otherwise; nobody ever gonna <propname/>
            self.hint = ""

        zi = int(time.time())
        vst = os.stat_result((16877, -1, -1, 1, 1000, 1000, 8, zi, zi, zi))

        try:
            st = bos.stat(tap)
        except OSError as ex:
            if ex.errno not in (errno.ENOENT, errno.ENOTDIR):
                raise
            if tap:
                raise Pebkac(404)
            st = vst

        topdir = {"vp": "", "st": st}
        fgen   = []

        depth = self.headers.get("depth", "infinity").lower()
        if depth == "infinity":
            # allow depth:0 from unmapped root, but require read-axs otherwise
            if not self.can_read and (self.vpath or self.asrv.vfs.realpath):
                t = "depth:infinity requires read-access in %r"
                t = t % ("/" + self.vpath,)
                self.log(t, 3)
                raise Pebkac(401, t)

            if not stat.S_ISDIR(topdir["st"].st_mode):
                t = "depth:infinity can only be used on folders; %r is 0o%o"
                t = t % ("/" + self.vpath, topdir["st"])
                self.log(t, 3)
                raise Pebkac(400, t)

            if not self.args.dav_inf:
                self.log("client wants --dav-inf", 3)
                zb = b'<?xml version="1.0" encoding="utf-8"?>\n<D:error xmlns:D="DAV:"><D:propfind-finite-depth/></D:error>'
                self.reply(zb, 403, "application/xml; charset=utf-8")
                return True

            # this will return symlink-target timestamps
            # because lstat=true would not recurse into subfolders
            # and this is a rare case where we actually want that
            fgen = vn.zipgen(
                rem,
                rem,
                set(),
                self.uname,
                True,
                not self.args.no_scandir,
                wrap=False,
            )

        elif depth == "0" or not stat.S_ISDIR(st.st_mode):
            if depth == "0" and not self.vpath and not vn.realpath:
                # rootless server; give dummy listing
                self.can_read = True
            # propfind on a file; return as topdir
            if not self.can_read and not self.can_get:
                self.log("inaccessible: %r" % ("/" + self.vpath,))
                raise Pebkac(401, "authenticate")

        elif depth == "1":
            _, vfs_ls, vfs_virt = vn.ls(
                rem,
                self.uname,
                not self.args.no_scandir,
                [[True, False]],
                lstat="davrt" not in vn.flags,
                throw=True,
            )
            if not self.can_read:
                vfs_ls = []
            if not self.can_dot:
                names = set(exclude_dotfiles([x[0] for x in vfs_ls]))
                vfs_ls = [x for x in vfs_ls if x[0] in names]

            fgen = [{"vp": vp, "st": st} for vp, st in vfs_ls]
            fgen += [{"vp": v, "st": vst} for v in vfs_virt]

        else:
            t = "invalid depth value '{}' (must be either '0' or '1'{})"
            t2 = " or 'infinity'" if self.args.dav_inf else ""
            raise Pebkac(412, t.format(depth, t2))

        if not self.can_read and not self.can_write and not fgen:
            self.log("inaccessible: %r" % ("/" + self.vpath,))
            raise Pebkac(401, "authenticate")

        zi = (
            vn.flags["du_iwho"]
            if vn.realpath and "quota-available-bytes" in props
            else 0
        )
        if zi and (
            zi == 9
            or (zi == 7 and self.uname != "*")
            or (zi == 5 and self.can_write)
            or (zi == 4 and self.can_write and self.can_read)
            or (zi == 3 and self.can_admin)
        ):
            bfree, btot, _ = get_df(vn.realpath, False)
            if btot:
                df = {
                    "quota-available-bytes": str(bfree),
                    "quota-used-bytes": str(btot - bfree),
                }
                if "quotaused" in props:  # macos finder crazytalk
                    df["quotaused"] = df["quota-used-bytes"]
                    if "quota" in props:
                        df["quota"] = df["quota-available-bytes"]  # idk, makes it happy
            else:
                df = {}
        else:
            df = {}

        fgen = itertools.chain([topdir], fgen)
        vtop = vjoin(self.args.R, vjoin(vn.vpath, rem))

        chunksz = 0x7FF8  # preferred by nginx or cf (dunno which)

        self.send_headers(
            None, 207, "text/xml; charset=" + enc, {"Transfer-Encoding": "chunked"}
        )

        ap = ""
        use_magic = "rmagic" in vn.flags

        ret = '<?xml version="1.0" encoding="{}"?>\n<D:multistatus xmlns:D="DAV:">'
        ret = ret.format(uenc)
        for x in fgen:
            rp = vjoin(vtop, x["vp"])
            st  = x["st"]
            mtime = max(0, st.st_mtime)
            if stat.S_ISLNK(st.st_mode):
                try:
                    st = bos.stat(os.path.join(tap, x["vp"]))
                except:
                    continue

            isdir = stat.S_ISDIR(st.st_mode)

            ret += "<D:response><D:href>/%s%s</D:href><D:propstat><D:prop>" % (
                quotep(rp),
                "/" if isdir and rp else "",
            )

            pvs   = {
                "displayname": html_escape(rp.split("/")[-1]),
                "getlastmodified": formatdate(mtime),
                "resourcetype": '<D:collection xmlns:D="DAV:"/>' if isdir else "",
                "supportedlock": '<D:lockentry xmlns:D="DAV:"><D:lockscope><D:exclusive/></D:lockscope><D:locktype><D:write/></D:locktype></D:lockentry>',
            }
            if not isdir:
                if use_magic:
                    ap = os.path.join(tap, x["vp"])
                pvs["getcontenttype"] = html_escape(guess_mime(rp, ap))
                pvs["getcontentlength"] = str(st.st_size)
            elif df:
                pvs.update(df)
                df = {}

            for k, v in pvs.items():
                if k not in props:
                    continue
                elif v:
                    ret += "<D:%s>%s</D:%s>" % (k, v, k)
                else:
                    ret += "<D:%s/>" % (k,)

            ret += "</D:prop><D:status>HTTP/1.1 200 OK</D:status></D:propstat>"

            missing = ["<D:%s/>" % (x,) for x in props if x not in pvs]
            if missing and clen:
                t = "<D:propstat><D:prop>{}</D:prop><D:status>HTTP/1.1 404 Not Found</D:status></D:propstat>"
                ret += t.format("".join(missing))

            ret += "</D:response>"
            while len(ret) >= chunksz:
                ret = self.send_chunk(ret, enc, chunksz)

        ret += "</D:multistatus>"
        while ret:
            ret = self.send_chunk(ret, enc, chunksz)

        self.send_chunk("", enc, chunksz)
        # self.reply(ret.encode(enc, "replace"),207, "text/xml; charset=" + enc)
        return True

    def handle_proppatch(self)  :
        if self.do_log:
            self.log("PPATCH %s @%s" % (self.req, self.uname))
            if "%" in self.req:
                self.log("   `-- %r" % (self.vpath,))

        if self.args.no_dav:
            raise Pebkac(405, "WebDAV is disabled in server config")

        if not self.can_write:
            self.log("%s tried to proppatch %r" % (self.uname, "/" + self.vpath))
            raise Pebkac(401, "authenticate")

        from xml.etree import ElementTree as ET

        from .dxml import mkenod, mktnod, parse_xml

        buf = b""
        for rbuf in self.get_body_reader()[0]:
            buf += rbuf
            if not rbuf or len(buf) >= 128 * 1024:
                break

        if self._applesan():
            return True

        txt = buf.decode("ascii", "replace").lower()
        enc = self.get_xml_enc(txt)
        uenc = enc.upper()

        txt = buf.decode(enc, "replace")
        self.hint = "<xml> " + txt
        ET.register_namespace("D", "DAV:")
        xroot = mkenod("D:orz")
        xroot.insert(0, parse_xml(txt))
        xprop = xroot.find(r"./{DAV:}propertyupdate/{DAV:}set/{DAV:}prop")
        for ze in xprop:
            ze.clear()
        self.hint = ""

        txt = """<multistatus xmlns="DAV:"><response><propstat><status>HTTP/1.1 403 Forbidden</status></propstat></response></multistatus>"""
        xroot = parse_xml(txt)

        el = xroot.find(r"./{DAV:}response")
        e2 = mktnod("D:href", quotep(self.args.SRS + self.vpath))
        el.insert(0, e2)

        el = xroot.find(r"./{DAV:}response/{DAV:}propstat")
        el.insert(0, xprop)

        ret = '<?xml version="1.0" encoding="{}"?>\n'.format(uenc)
        ret += ET.tostring(xroot).decode("utf-8")

        self.reply(ret.encode(enc, "replace"), 207, "text/xml; charset=" + enc)
        return True

    def handle_lock(self)  :
        if self.do_log:
            self.log("LOCK %s @%s" % (self.req, self.uname))
            if "%" in self.req:
                self.log(" `-- %r" % (self.vpath,))

        if self.args.no_dav:
            raise Pebkac(405, "WebDAV is disabled in server config")

        # win7+ deadlocks if we say no; just smile and nod
        if not self.can_write and "Microsoft-WebDAV" not in self.ua:
            self.log("%s tried to lock %r" % (self.uname, "/" + self.vpath))
            raise Pebkac(401, "authenticate")

        from xml.etree import ElementTree as ET

        from .dxml import mkenod, mktnod, parse_xml

        abspath = self.vn.dcanonical(self.rem)

        buf = b""
        for rbuf in self.get_body_reader()[0]:
            buf += rbuf
            if not rbuf or len(buf) >= 128 * 1024:
                break

        if self._applesan():
            return True

        txt = buf.decode("ascii", "replace").lower()
        enc = self.get_xml_enc(txt)
        uenc = enc.upper()

        txt = buf.decode(enc, "replace")
        self.hint = "<xml> " + txt
        ET.register_namespace("D", "DAV:")
        lk = parse_xml(txt)
        assert lk.tag == "{DAV:}lockinfo"
        self.hint = ""

        token = str(uuid.uuid4())

        if lk.find(r"./{DAV:}depth") is None:
            depth = self.headers.get("depth", "infinity")
            lk.append(mktnod("D:depth", depth))

        lk.append(mktnod("D:timeout", "Second-3310"))
        lk.append(mkenod("D:locktoken", mktnod("D:href", token)))
        lk.append(
            mkenod("D:lockroot", mktnod("D:href", quotep(self.args.SRS + self.vpath)))
        )

        lk2 = mkenod("D:activelock")
        xroot = mkenod("D:prop", mkenod("D:lockdiscovery", lk2))
        for a in lk:
            lk2.append(a)

        ret = '<?xml version="1.0" encoding="{}"?>\n'.format(uenc)
        ret += ET.tostring(xroot).decode("utf-8")

        rc = 200
        if self.can_write and not bos.path.isfile(abspath):
            with open(fsenc(abspath), "wb") as _:
                rc = 201

        self.out_headers["Lock-Token"] = "<{}>".format(token)
        self.reply(ret.encode(enc, "replace"), rc, "text/xml; charset=" + enc)
        return True

    def handle_unlock(self)  :
        if self.do_log:
            self.log("UNLOCK %s @%s" % (self.req, self.uname))
            if "%" in self.req:
                self.log("   `-- %r" % (self.vpath,))

        if self.args.no_dav:
            raise Pebkac(405, "WebDAV is disabled in server config")

        if not self.can_write and "Microsoft-WebDAV" not in self.ua:
            self.log("%s tried to lock %r" % (self.uname, "/" + self.vpath))
            raise Pebkac(401, "authenticate")

        self.send_headers(None, 204)
        return True

    def handle_mkcol(self)  :
        if self._applesan():
            return True

        if self.do_log:
            self.log("MKCOL %s @%s" % (self.req, self.uname))
            if "%" in self.req:
                self.log("  `-- %r" % (self.vpath,))

        if self.args.no_dav:
            raise Pebkac(405, "WebDAV is disabled in server config")

        if not self.can_write:
            raise Pebkac(401, "authenticate")

        try:
            return self._mkdir(self.vpath, True)
        except Pebkac as ex:
            if ex.code >= 500:
                raise

            self.reply(b"", ex.code)
            return True

    def handle_cpmv(self)  :
        dst = self.headers["destination"]

        # dolphin (kioworker/6.10) "webdav://127.0.0.1:3923/a/b.txt"
        dst = re.sub("^[a-zA-Z]+://[^/]+", "", dst).lstrip()

        if self.is_vproxied and dst.startswith(self.args.SRS):
            dst = dst[len(self.args.RS) :]

        if self.do_log:
            self.log("%s %s  --//>  %s @%s" % (self.mode, self.req, dst, self.uname))
            if "%" in self.req:
                self.log("  `-- %r" % (self.vpath,))

        if self.args.no_dav:
            raise Pebkac(405, "WebDAV is disabled in server config")

        dst = unquotep(dst)

        # overwrite=True is default; rfc4918 9.8.4
        zs = self.headers.get("overwrite", "").lower()
        overwrite = zs not in ["f", "false"]

        try:
            fun = self._cp if self.mode == "COPY" else self._mv
            return fun(self.vpath, dst.lstrip("/"), overwrite)
        except Pebkac as ex:
            if ex.code == 403:
                ex.code = 401
            raise

    def _applesan(self)  :
        if self.args.dav_mac or "Darwin/" not in self.ua:
            return False

        vp = "/" + self.vpath
        if re.search(APPLESAN_RE, vp):
            zt = '<?xml version="1.0" encoding="utf-8"?>\n<D:error xmlns:D="DAV:"><D:lock-token-submitted><D:href>{}</D:href></D:lock-token-submitted></D:error>'
            zb = zt.format(vp).encode("utf-8", "replace")
            self.reply(zb, 423, "text/xml; charset=utf-8")
            return True

        return False

    def send_chunk(self, txt , enc , bmax )  :
        orig_len = len(txt)
        buf = txt[:bmax].encode(enc, "replace")[:bmax]
        try:
            _ = buf.decode(enc)
        except UnicodeDecodeError as ude:
            buf = buf[: ude.start]

        txt = txt[len(buf.decode(enc)) :]
        if txt and len(txt) == orig_len:
            raise Pebkac(500, "chunk slicing failed")

        buf = ("%x\r\n" % (len(buf),)).encode(enc) + buf
        self.s.sendall(buf + b"\r\n")
        return txt

    def handle_options(self)  :
        if self.do_log:
            self.log("OPTIONS %s @%s" % (self.req, self.uname))
            if "%" in self.req:
                self.log("    `-- %r" % (self.vpath,))

        oh = self.out_headers
        oh["Allow"] = ", ".join(self.conn.hsrv.mallow)

        if not self.args.no_dav:
            # PROPPATCH, LOCK, UNLOCK, COPY: noop (spec-must)
            oh["Dav"] = "1, 2"
            oh["Ms-Author-Via"] = "DAV"

        # winxp-webdav doesnt know what 204 is
        self.send_headers(0, 200)
        return True

    def handle_delete(self)  :
        self.log("DELETE %s @%s" % (self.req, self.uname))
        if "%" in self.req:
            self.log("   `-- %r" % (self.vpath,))
        return self.handle_rm([])

    def handle_put(self)  :
        self.log("PUT  %s @%s" % (self.req, self.uname))
        if "%" in self.req:
            self.log(" `-- %r" % (self.vpath,))

        if not self.can_write:
            t = "user %s does not have write-access under /%s"
            raise Pebkac(403 if self.pw else 401, t % (self.uname, self.vn.vpath))

        if not self.args.no_dav and self._applesan():
            return self.headers.get("content-length") == "0"

        if self.headers.get("expect", "").lower() == "100-continue":
            try:
                self.s.sendall(b"HTTP/1.1 100 Continue\r\n\r\n")
            except:
                raise Pebkac(400, "client d/c before 100 continue")

        return self.handle_stash(True)

    def handle_post(self)  :
        self.log("POST %s @%s" % (self.req, self.uname))
        if "%" in self.req:
            self.log(" `-- %r" % (self.vpath,))

        if self.headers.get("expect", "").lower() == "100-continue":
            try:
                self.s.sendall(b"HTTP/1.1 100 Continue\r\n\r\n")
            except:
                raise Pebkac(400, "client d/c before 100 continue")

        if "raw" in self.uparam:
            return self.handle_stash(False)

        ctype = self.headers.get("content-type", "").lower()

        if "multipart/form-data" in ctype:
            return self.handle_post_multipart()

        if (
            "application/json" in ctype
            or "text/plain" in ctype
            or "application/xml" in ctype
        ):
            return self.handle_post_json()

        if "move" in self.uparam:
            return self.handle_mv()

        if "copy" in self.uparam:
            return self.handle_cp()

        if "delete" in self.uparam:
            return self.handle_rm([])

        if "eshare" in self.uparam:
            return self.handle_eshare()

        if "fs_abrt" in self.uparam:
            return self.handle_fs_abrt()

        if "application/octet-stream" in ctype:
            return self.handle_post_binary()

        if "application/x-www-form-urlencoded" in ctype:
            opt = self.args.urlform
            if "stash" in opt:
                return self.handle_stash(False)

            xm = []
            xm_rsp = {}

            if "save" in opt:
                post_sz, _, _, _, _, path, _ = self.dump_to_file(False)
                self.log("urlform: %d bytes, %r" % (post_sz, path))
            elif "print" in opt:
                reader, _ = self.get_body_reader()
                buf = b""
                for rbuf in reader:
                    buf += rbuf
                    if not rbuf or len(buf) >= 32768:
                        break

                if buf:
                    orig = buf.decode("utf-8", "replace")
                    t = "urlform_raw %d @ %r\n  %r\n"
                    self.log(t % (len(orig), "/" + self.vpath, orig))
                    try:
                        zb = unquote(buf.replace(b"+", b" ").replace(b"&", b"\n"))
                        plain = zb.decode("utf-8", "replace")
                        if buf.startswith(b"msg="):
                            plain = plain[4:]
                            xm = self.vn.flags.get("xm")
                            if xm:
                                xm_rsp = runhook(
                                    self.log,
                                    self.conn.hsrv.broker,
                                    None,
                                    "xm",
                                    xm,
                                    self.vn.canonical(self.rem),
                                    self.vpath,
                                    self.host,
                                    self.uname,
                                    self.asrv.vfs.get_perms(self.vpath, self.uname),
                                    time.time(),
                                    len(buf),
                                    self.ip,
                                    time.time(),
                                    [plain, orig],
                                )

                        t = "urlform_dec %d @ %r\n  %r\n"
                        self.log(t % (len(plain), "/" + self.vpath, plain))

                    except Exception as ex:
                        self.log(repr(ex))

            if "xm" in opt:
                if xm:
                    self.loud_reply(xm_rsp.get("stdout") or "", status=202)
                    return True
                else:
                    return self.handle_get()

            if "get" in opt:
                return self.handle_get()

            raise Pebkac(405, "POST(%r) is disabled in server config" % (ctype,))

        raise Pebkac(405, "don't know how to handle POST(%r)" % (ctype,))

    def get_xml_enc(self, txt )  :
        ofs = txt[:512].find(' encoding="')
        enc = ""
        if ofs + 1:
            enc = txt[ofs + 6 :].split('"')[1]
        else:
            enc = self.headers.get("content-type", "").lower()
            ofs = enc.find("charset=")
            if ofs + 1:
                enc = enc[ofs + 4].split("=")[1].split(";")[0].strip("\"'")
            else:
                enc = ""

        return enc or "utf-8"

    def get_body_reader(self)     :
        bufsz = self.args.s_rd_sz
        if "chunked" in self.headers.get("transfer-encoding", "").lower():
            return read_socket_chunked(self.sr, bufsz), -1

        remains = int(self.headers.get("content-length", -1))
        if remains == -1:
            self.keepalive = False
            self.in_hdr_recv = True
            self.s.settimeout(max(self.args.s_tbody // 20, 1))
            return read_socket_unbounded(self.sr, bufsz), remains
        else:
            return read_socket(self.sr, bufsz, remains), remains

    def dump_to_file(self, is_put )        :
        # post_sz, halg, sha_hex, sha_b64, remains, path, url
        reader, remains = self.get_body_reader()
        vfs, rem = self.asrv.vfs.get(self.vpath, self.uname, False, True)
        rnd, lifetime, xbu, xau = self.upload_flags(vfs)
        lim = vfs.get_dbv(rem)[0].lim
        fdir = vfs.canonical(rem)
        fn = None
        if rem and not self.trailing_slash and not bos.path.isdir(fdir):
            fdir, fn = os.path.split(fdir)
            rem, _ = vsplit(rem)

        if lim:
            fdir, rem = lim.all(
                self.ip, rem, remains, vfs.realpath, fdir, self.conn.hsrv.broker
            )

        bos.makedirs(fdir, vf=vfs.flags)

        open_ka   = {"fun": open}
        open_a = ["wb", self.args.iobuf]

        # user-request || config-force
        if ("gz" in vfs.flags or "xz" in vfs.flags) and (
            "pk" in vfs.flags
            or "pk" in self.uparam
            or "gz" in self.uparam
            or "xz" in self.uparam
        ):
            fb = {"gz": 9, "xz": 0}  # default/fallback level
            lv = {}  # selected level
            alg = ""  # selected algo (gz=preferred)

            # user-prefs first
            if "gz" in self.uparam or "pk" in self.uparam:  # def.pk
                alg = "gz"
            if "xz" in self.uparam:
                alg = "xz"
            if alg:
                zso = self.uparam.get(alg)
                lv[alg] = fb[alg] if zso is None else int(zso)

            if alg not in vfs.flags:
                alg = "gz" if "gz" in vfs.flags else "xz"

            # then server overrides
            pk = vfs.flags.get("pk")
            if pk is not None:
                # config-forced on
                alg = alg or "gz"  # def.pk
                try:
                    # config-forced opts
                    alg, nlv = pk.split(",")
                    lv[alg] = int(nlv)
                except:
                    pass

            lv[alg] = lv.get(alg) or fb.get(alg) or 0

            self.log("compressing with {} level {}".format(alg, lv.get(alg)))
            if alg == "gz":
                open_ka["fun"] = gzip.GzipFile
                open_a = ["wb", lv[alg], None, 0x5FEE6600]  # 2021-01-01
            elif alg == "xz":
                open_ka = {"fun": lzma.open, "preset": lv[alg]}
                open_a = ["wb"]
            else:
                self.log("fallthrough? thats a bug", 1)

        suffix = "-{:.6f}-{}".format(time.time(), self.dip())
        nameless = not fn
        if nameless:
            fn = vfs.flags["put_name2"].format(now=time.time(), cip=self.dip())

        params = {"suffix": suffix, "fdir": fdir, "vf": vfs.flags}
        if self.args.nw:
            params = {}
            fn = os.devnull

        params.update(open_ka)

        if not self.args.nw:
            if rnd:
                fn = rand_name(fdir, fn, rnd)

            fn = sanitize_fn(fn or "", "")

        path = os.path.join(fdir, fn)

        if xbu:
            at = time.time() - lifetime
            vp = vjoin(self.vpath, fn) if nameless else self.vpath
            hr = runhook(
                self.log,
                self.conn.hsrv.broker,
                None,
                "xbu.http.dump",
                xbu,
                path,
                vp,
                self.host,
                self.uname,
                self.asrv.vfs.get_perms(self.vpath, self.uname),
                at,
                remains,
                self.ip,
                at,
                None,
            )
            t = hr.get("rejectmsg") or ""
            if t or not hr:
                if not t:
                    t = "upload blocked by xbu server config: %r" % (vp,)
                self.log(t, 1)
                raise Pebkac(403, t)
            if hr.get("reloc"):
                x = pathmod(self.asrv.vfs, path, vp, hr["reloc"])
                if x:
                    if self.args.hook_v:
                        log_reloc(self.log, hr["reloc"], x, path, vp, fn, vfs, rem)
                    fdir, self.vpath, fn, (vfs, rem) = x
                    if self.args.nw:
                        fn = os.devnull
                    else:
                        bos.makedirs(fdir, vf=vfs.flags)
                        path = os.path.join(fdir, fn)
                        if not nameless:
                            self.vpath = vjoin(self.vpath, fn)
                        params["fdir"] = fdir

        if is_put and not (self.args.no_dav or self.args.nw) and bos.path.exists(path):
            # allow overwrite if...
            #  * volflag 'daw' is set, or client is definitely webdav
            #  * and account has delete-access
            # or...
            #  * file exists, is empty, sufficiently new
            #  * and there is no .PARTIAL

            tnam = fn + ".PARTIAL"
            if self.args.dotpart:
                tnam = "." + tnam

            if (
                self.can_delete
                and (
                    vfs.flags.get("daw")
                    or "replace" in self.headers
                    or "x-oc-mtime" in self.headers
                )
            ) or (
                not bos.path.exists(os.path.join(fdir, tnam))
                and not bos.path.getsize(path)
                and bos.path.getmtime(path) >= time.time() - self.args.blank_wt
            ):
                # small toctou, but better than clobbering a hardlink
                wunlink(self.log, path, vfs.flags)

        hasher = None
        copier = hashcopy
        halg = self.ouparam.get("ck") or self.headers.get("ck") or vfs.flags["put_ck"]
        if halg == "sha512":
            pass
        elif halg == "no":
            copier = justcopy
            halg = ""
        elif halg == "md5":
            hasher = hashlib.md5(**USED4SEC)
        elif halg == "sha1":
            hasher = hashlib.sha1(**USED4SEC)
        elif halg == "sha256":
            hasher = hashlib.sha256(**USED4SEC)
        elif halg in ("blake2", "b2"):
            hasher = hashlib.blake2b(**USED4SEC)
        elif halg in ("blake2s", "b2s"):
            hasher = hashlib.blake2s(**USED4SEC)
        else:
            raise Pebkac(500, "unknown hash alg")

        f, fn = ren_open(fn, *open_a, **params)
        try:
            path = os.path.join(fdir, fn)
            post_sz, sha_hex, sha_b64 = copier(reader, f, hasher, 0, self.args.s_wr_slp)
        finally:
            f.close()

        if lim:
            lim.nup(self.ip)
            lim.bup(self.ip, post_sz)
            try:
                lim.chk_sz(post_sz)
                lim.chk_vsz(self.conn.hsrv.broker, vfs.realpath, post_sz)
            except:
                wunlink(self.log, path, vfs.flags)
                raise

        if self.args.nw:
            return post_sz, halg, sha_hex, sha_b64, remains, path, ""

        at = mt = time.time() - lifetime
        cli_mt = self.headers.get("x-oc-mtime")
        if cli_mt:
            bos.utime_c(self.log, path, int(cli_mt), False)

        if nameless and "magic" in vfs.flags:
            try:
                ext = self.conn.hsrv.magician.ext(path)
            except Exception as ex:
                self.log("filetype detection failed for %r: %s" % (path, ex), 6)
                ext = None

            if ext:
                if rnd:
                    fn2 = rand_name(fdir, "a." + ext, rnd)
                else:
                    fn2 = fn.rsplit(".", 1)[0] + "." + ext

                params["suffix"] = suffix[:-4]
                f, fn2 = ren_open(fn2, *open_a, **params)
                f.close()

                path2 = os.path.join(fdir, fn2)
                atomic_move(self.log, path, path2, vfs.flags)
                fn = fn2
                path = path2

        if xau:
            vp = vjoin(self.vpath, fn) if nameless else self.vpath
            hr = runhook(
                self.log,
                self.conn.hsrv.broker,
                None,
                "xau.http.dump",
                xau,
                path,
                vp,
                self.host,
                self.uname,
                self.asrv.vfs.get_perms(self.vpath, self.uname),
                mt,
                post_sz,
                self.ip,
                at,
                None,
            )
            t = hr.get("rejectmsg") or ""
            if t or not hr:
                if not t:
                    t = "upload blocked by xau server config: %r" % (vp,)
                self.log(t, 1)
                wunlink(self.log, path, vfs.flags)
                raise Pebkac(403, t)
            if hr.get("reloc"):
                x = pathmod(self.asrv.vfs, path, vp, hr["reloc"])
                if x:
                    if self.args.hook_v:
                        log_reloc(self.log, hr["reloc"], x, path, vp, fn, vfs, rem)
                    fdir, self.vpath, fn, (vfs, rem) = x
                    bos.makedirs(fdir, vf=vfs.flags)
                    path2 = os.path.join(fdir, fn)
                    atomic_move(self.log, path, path2, vfs.flags)
                    path = path2
                    if not nameless:
                        self.vpath = vjoin(self.vpath, fn)
            sz = bos.path.getsize(path)
        else:
            sz = post_sz

        vfs, rem = vfs.get_dbv(rem)
        self.conn.hsrv.broker.say(
            "up2k.hash_file",
            vfs.realpath,
            vfs.vpath,
            vfs.flags,
            rem,
            fn,
            self.ip,
            at,
            self.uname,
            True,
        )

        vsuf = ""
        if (self.can_read or self.can_upget) and "fk" in vfs.flags:
            alg = 2 if "fka" in vfs.flags else 1
            vsuf = "?k=" + self.gen_fk(
                alg,
                self.args.fk_salt,
                path,
                sz,
                0 if ANYWIN else bos.stat(path).st_ino,
            )[: vfs.flags["fk"]]

        if "media" in self.uparam or "medialinks" in vfs.flags:
            vsuf += "&v" if vsuf else "?v"

        vpath = "/".join([x for x in [vfs.vpath, rem, fn] if x])
        vpath = quotep(vpath)

        url = "{}://{}/{}".format(
            "https" if self.is_https else "http",
            self.host,
            self.args.RS + vpath + vsuf,
        )

        return post_sz, halg, sha_hex, sha_b64, remains, path, url

    def handle_stash(self, is_put )  :
        post_sz, halg, sha_hex, sha_b64, remains, path, url = self.dump_to_file(is_put)
        spd = self._spd(post_sz)
        t = "%s wrote %d/%d bytes to %r  # %s"
        self.log(t % (spd, post_sz, remains, path, sha_b64[:28]))  # 21

        mime = "text/plain; charset=utf-8"
        ac = self.uparam.get("want") or self.headers.get("accept") or ""
        if ac:
            ac = ac.split(";", 1)[0].lower()
            if ac == "application/json":
                ac = "json"
        if ac == "url":
            t = url
        elif ac == "json" or "j" in self.uparam:
            jmsg = {"fileurl": url, "filesz": post_sz}
            if halg:
                jmsg[halg] = sha_hex[:56]
                jmsg["sha_b64"] = sha_b64

            mime = "application/json"
            t = json.dumps(jmsg, indent=2, sort_keys=True)
        else:
            t = "{}\n{}\n{}\n{}\n".format(post_sz, sha_b64, sha_hex[:56], url)

        h = {"Location": url} if is_put and url else {}

        if "x-oc-mtime" in self.headers:
            h["X-OC-MTime"] = "accepted"
            t = ""  # some webdav clients expect/prefer this

        self.reply(t.encode("utf-8", "replace"), 201, mime=mime, headers=h)
        return True

    def bakflip(
        self,
        f ,
        ap ,
        ofs ,
        sz ,
        good_sha ,
        bad_sha ,
        flags  ,
    )  :
        now = time.time()
        t = "bad-chunk:  %.3f  %s  %s  %d  %s  %s  %r"
        t = t % (now, bad_sha, good_sha, ofs, self.ip, self.uname, ap)
        self.log(t, 5)

        if self.args.bf_log:
            try:
                with open(self.args.bf_log, "ab+") as f2:
                    f2.write((t + "\n").encode("utf-8", "replace"))
            except Exception as ex:
                self.log("append %s failed: %r" % (self.args.bf_log, ex))

        if not self.args.bak_flips or self.args.nw:
            return

        sdir = self.args.bf_dir
        fp = os.path.join(sdir, bad_sha)
        if bos.path.exists(fp):
            return self.log("no bakflip; have it", 6)

        if not bos.path.isdir(sdir):
            bos.makedirs(sdir)

        if len(bos.listdir(sdir)) >= self.args.bf_nc:
            return self.log("no bakflip; too many", 3)

        nrem = sz
        f.seek(ofs)
        with open(fp, "wb") as fo:
            while nrem:
                buf = f.read(min(nrem, self.args.iobuf))
                if not buf:
                    break

                nrem -= len(buf)
                fo.write(buf)

        if nrem:
            self.log("bakflip truncated; {} remains".format(nrem), 1)
            atomic_move(self.log, fp, fp + ".trunc", flags)
        else:
            self.log("bakflip ok", 2)

    def _spd(self, nbytes , add  = True)  :
        if add:
            self.conn.nbyte += nbytes

        spd1 = get_spd(nbytes, self.t0)
        spd2 = get_spd(self.conn.nbyte, self.conn.t0)
        return "%s %s n%s" % (spd1, spd2, self.conn.nreq)

    def handle_post_multipart(self)  :
        self.parser = MultipartParser(self.log, self.args, self.sr, self.headers)
        self.parser.parse()

        file0      = []
        try:
            act = self.parser.require("act", 64)
        except WrongPostKey as ex:
            if ex.got == "f" and ex.fname:
                self.log("missing 'act', but looks like an upload so assuming that")
                file0 = [(ex.got, ex.fname, ex.datagen)]
                act = "bput"
            else:
                raise

        if act == "login":
            return self.handle_login()

        if act == "mkdir":
            return self.handle_mkdir()

        if act == "new_md":
            # kinda silly but has the least side effects
            return self.handle_new_md()

        if act in ("bput", "uput"):
            return self.handle_plain_upload(file0, act == "uput")

        if act == "tput":
            return self.handle_text_upload()

        if act == "zip":
            return self.handle_zip_post()

        if act == "chpw":
            return self.handle_chpw()

        if act == "logout":
            return self.handle_logout()

        raise Pebkac(422, "invalid action %r" % (act,))

    def handle_zip_post(self)  :
        try:
            k = next(x for x in self.uparam if x in ("zip", "tar"))
        except:
            raise Pebkac(422, "need zip or tar keyword")

        v = self.uparam[k]

        if self._use_dirkey(self.vn, ""):
            vn = self.vn
            rem = self.rem
        else:
            vn, rem = self.asrv.vfs.get(self.vpath, self.uname, True, False)

        zs = self.parser.require("files", 1024 * 1024)
        if not zs:
            raise Pebkac(422, "need files list")

        items = zs.replace("\r", "").split("\n")
        items = [unquotep(x) for x in items if items]

        self.parser.drop()
        return self.tx_zip(k, v, "", vn, rem, items)

    def handle_post_json(self)  :
        try:
            remains = int(self.headers["content-length"])
        except:
            raise Pebkac(411)

        if remains > 1024 * 1024:
            raise Pebkac(413, "json 2big")

        enc = "utf-8"
        ctype = self.headers.get("content-type", "").lower()
        if "charset" in ctype:
            enc = ctype.split("charset")[1].strip(" =").split(";")[0].strip()

        try:
            json_buf = self.sr.recv_ex(remains)
        except UnrecvEOF:
            raise Pebkac(422, "client disconnected while posting JSON")

        try:
            body = json.loads(json_buf.decode(enc, "replace"))
            try:
                zds = {k: v for k, v in body.items()}
                zds["hash"] = "%d chunks" % (len(body["hash"]),)
            except:
                zds = body
            t = "POST len=%d type=%s ip=%s user=%s req=%r json=%s"
            self.log(t % (len(json_buf), enc, self.ip, self.uname, self.req, zds))
        except:
            raise Pebkac(422, "you POSTed %d bytes of invalid json" % (len(json_buf),))

        # self.reply(b"cloudflare", 503)
        # return True

        if "srch" in self.uparam or "srch" in body:
            return self.handle_search(body)

        if "share" in self.uparam:
            return self.handle_share(body)

        if "delete" in self.uparam:
            return self.handle_rm(body)

        name = undot(body["name"])
        if "/" in name:
            raise Pebkac(400, "your client is old; press CTRL-SHIFT-R and try again")

        vfs, rem = self.asrv.vfs.get(self.vpath, self.uname, False, True)
        dbv, vrem = vfs.get_dbv(rem)

        name = sanitize_fn(name, "")
        if (
            not self.can_read
            and self.can_write
            and name.lower() in FN_EMB
            and "wo_up_readme" not in dbv.flags
        ):
            name = "_wo_" + name

        body["name"] = name
        body["vtop"] = dbv.vpath
        body["ptop"] = dbv.realpath
        body["prel"] = vrem
        body["host"] = self.host
        body["user"] = self.uname
        body["addr"] = self.ip
        body["vcfg"] = dbv.flags

        if not self.can_delete:
            body.pop("replace", None)

        if rem:
            dst = vfs.canonical(rem)
            try:
                if not bos.path.isdir(dst):
                    bos.makedirs(dst, vf=vfs.flags)
            except OSError as ex:
                self.log("makedirs failed %r" % (dst,))
                if not bos.path.isdir(dst):
                    if ex.errno == errno.EACCES:
                        raise Pebkac(500, "the server OS denied write-access")

                    if ex.errno == errno.EEXIST:
                        raise Pebkac(400, "some file got your folder name")

                    raise Pebkac(500, min_ex())
            except:
                raise Pebkac(500, min_ex())

        # not to protect u2fh, but to prevent handshakes while files are closing
        with self.u2mutex:
            x = self.conn.hsrv.broker.ask("up2k.handle_json", body, self.u2fh.aps)
            ret = x.get()

        if self.args.shr and self.vpath.startswith(self.args.shr1):
            # strip common suffix (uploader's folder structure)
            vp_req, vp_vfs = vroots(self.vpath, vjoin(dbv.vpath, vrem))
            if not ret["purl"].startswith(vp_vfs):
                t = "share-mapping failed; req=%r dbv=%r vrem=%r n1=%r n2=%r purl=%r"
                zt = (self.vpath, dbv.vpath, vrem, vp_req, vp_vfs, ret["purl"])
                raise Pebkac(500, t % zt)
            ret["purl"] = vp_req + ret["purl"][len(vp_vfs) :]

        if self.is_vproxied:
            if "purl" in ret:
                ret["purl"] = self.args.SR + ret["purl"]

        ret = json.dumps(ret)
        self.log(ret)
        self.reply(ret.encode("utf-8"), mime="application/json")
        return True

    def handle_search(self, body  )  :
        idx = self.conn.get_u2idx()
        if not idx or not hasattr(idx, "p_end"):
            if not HAVE_SQLITE3:
                raise Pebkac(500, "sqlite3 not found on server; search is disabled")
            raise Pebkac(500, "server busy, cannot search; please retry in a bit")

        vols  = []
        seen   = {}
        for vtop in self.rvol:
            vfs, _ = self.asrv.vfs.get(vtop, self.uname, True, False)
            vfs = vfs.dbv or vfs
            if vfs in seen:
                continue

            seen[vfs] = True
            vols.append(vfs)

        t0 = time.time()
        if idx.p_end:
            penalty = 0.7
            t_idle = t0 - idx.p_end
            if idx.p_dur > 0.7 and t_idle < penalty:
                t = "rate-limit {:.1f} sec, cost {:.2f}, idle {:.2f}"
                raise Pebkac(429, t.format(penalty, idx.p_dur, t_idle))

        if "srch" in body:
            # search by up2k hashlist
            vbody = copy.deepcopy(body)
            vbody["hash"] = len(vbody["hash"])
            self.log("qj: " + repr(vbody))
            hits = idx.fsearch(self.uname, vols, body)
            msg  = repr(hits)
            taglist  = []
            trunc = False
        else:
            # search by query params
            q = body["q"]
            n = body.get("n", self.args.srch_hits)
            self.log("qj: %r |%d|" % (q, n))
            hits, taglist, trunc = idx.search(self.uname, vols, q, n)
            msg = len(hits)

        idx.p_end = time.time()
        idx.p_dur = idx.p_end - t0
        self.log("q#: %r (%.2fs)" % (msg, idx.p_dur))

        order = []
        for t in self.args.mte:
            if t in taglist:
                order.append(t)
        for t in taglist:
            if t not in order:
                order.append(t)

        if self.is_vproxied:
            for hit in hits:
                hit["rp"] = self.args.RS + hit["rp"]

        rj = {"hits": hits, "tag_order": order, "trunc": trunc}
        r = json.dumps(rj).encode("utf-8")
        self.reply(r, mime="application/json")
        return True

    def handle_post_binary(self)  :
        try:
            postsize = remains = int(self.headers["content-length"])
        except:
            raise Pebkac(400, "you must supply a content-length for binary POST")

        try:
            chashes = self.headers["x-up2k-hash"].split(",")
            wark = self.headers["x-up2k-wark"]
        except KeyError:
            raise Pebkac(400, "need hash and wark headers for binary POST")

        chashes = [x.strip() for x in chashes]
        if len(chashes) == 3 and len(chashes[1]) == 1:
            # the first hash, then length of consecutive hashes,
            # then a list of stitched hashes as one long string
            clen = int(chashes[1])
            siblings = chashes[2]
            chashes = [chashes[0]]
            for n in range(0, len(siblings), clen):
                chashes.append(siblings[n : n + clen])

        vfs, _ = self.asrv.vfs.get(self.vpath, self.uname, False, True)
        ptop = vfs.get_dbv("")[0].realpath
        # if this is a share, then get_dbv has been overridden to return
        # the dbv (which does not exist as a property). And its realpath
        # could point into the middle of its origin vfs node, meaning it
        # is not necessarily registered with up2k, so get_dbv is crucial

        broker = self.conn.hsrv.broker
        x = broker.ask("up2k.handle_chunks", ptop, wark, chashes)
        response = x.get()
        chashes, chunksize, cstarts, path, lastmod, fsize, sprs = response
        maxsize = chunksize * len(chashes)
        cstart0 = cstarts[0]
        locked = chashes  # remaining chunks to be received in this request
        written = []  # chunks written to disk, but not yet released by up2k
        num_left = -1  # num chunks left according to most recent up2k release
        bail1 = False  # used in sad path to avoid contradicting error-text
        treport = time.time()  # ratelimit up2k reporting to reduce overhead

        try:
            if "x-up2k-subc" in self.headers:
                sc_ofs = int(self.headers["x-up2k-subc"])
                chash = chashes[0]

                u2sc = self.conn.hsrv.u2sc
                try:
                    sc_pofs, hasher = u2sc[chash]
                    if not sc_ofs:
                        t = "client restarted the chunk; forgetting subchunk offset %d"
                        self.log(t % (sc_pofs,))
                        raise Exception()
                except:
                    sc_pofs = 0
                    hasher = hashlib.sha512()

                et = "subchunk protocol error; resetting chunk "
                if sc_pofs != sc_ofs:
                    u2sc.pop(chash, None)
                    t = "%s[%s]: the expected resume-point was %d, not %d"
                    raise Pebkac(400, t % (et, chash, sc_pofs, sc_ofs))
                if len(cstarts) > 1:
                    u2sc.pop(chash, None)
                    t = "%s[%s]: only a single subchunk can be uploaded in one request; you are sending %d chunks"
                    raise Pebkac(400, t % (et, chash, len(cstarts)))
                csize = min(chunksize, fsize - cstart0[0])
                cstart0[0] += sc_ofs  # also sets cstarts[0][0]
                sc_next_ofs = sc_ofs + postsize
                if sc_next_ofs > csize:
                    u2sc.pop(chash, None)
                    t = "%s[%s]: subchunk offset (%d) plus postsize (%d) exceeds chunksize (%d)"
                    raise Pebkac(400, t % (et, chash, sc_ofs, postsize, csize))
                else:
                    final_subchunk = sc_next_ofs == csize
                    t = "subchunk %s %d:%d/%d %s"
                    zs = "END" if final_subchunk else ""
                    self.log(t % (chash[:15], sc_ofs, sc_next_ofs, csize, zs), 6)
                    if final_subchunk:
                        u2sc.pop(chash, None)
                    else:
                        u2sc[chash] = (sc_next_ofs, hasher)
            else:
                hasher = None
                final_subchunk = True

            if self.args.nw:
                path = os.devnull

            if remains > maxsize:
                t = "your client is sending %d bytes which is too much (server expected %d bytes at most)"
                raise Pebkac(400, t % (remains, maxsize))

            t = "writing %r %s+%d #%d+%d %s"
            chunkno = cstart0[0] // chunksize
            zs = " ".join([chashes[0][:15]] + [x[:9] for x in chashes[1:]])
            self.log(t % (path, cstart0, remains, chunkno, len(chashes), zs))

            f = None
            fpool = not self.args.no_fpool and sprs
            if fpool:
                with self.u2mutex:
                    try:
                        f = self.u2fh.pop(path)
                    except:
                        pass

            f = f or open(fsenc(path), "rb+", self.args.iobuf)

            try:
                for chash, cstart in zip(chashes, cstarts):
                    f.seek(cstart[0])
                    reader = read_socket(
                        self.sr, self.args.s_rd_sz, min(remains, chunksize)
                    )
                    post_sz, _, sha_b64 = hashcopy(
                        reader, f, hasher, 0, self.args.s_wr_slp
                    )

                    if sha_b64 != chash and final_subchunk:
                        try:
                            self.bakflip(
                                f, path, cstart[0], post_sz, chash, sha_b64, vfs.flags
                            )
                        except:
                            self.log("bakflip failed: " + min_ex())

                        t = "your chunk got corrupted somehow (received {} bytes); expected vs received hash:\n{}\n{}"
                        raise Pebkac(400, t.format(post_sz, chash, sha_b64))

                    remains -= chunksize

                    if len(cstart) > 1 and path != os.devnull:
                        t = " & ".join(unicode(x) for x in cstart[1:])
                        self.log("clone %s to %s" % (cstart[0], t))
                        ofs = 0
                        while ofs < chunksize:
                            bufsz = max(4 * 1024 * 1024, self.args.iobuf)
                            bufsz = min(chunksize - ofs, bufsz)
                            f.seek(cstart[0] + ofs)
                            buf = f.read(bufsz)
                            for wofs in cstart[1:]:
                                f.seek(wofs + ofs)
                                f.write(buf)

                            ofs += len(buf)

                        self.log("clone {} done".format(cstart[0]))

                    # be quick to keep the tcp winsize scale;
                    # if we can't confirm rn then that's fine
                    if final_subchunk:
                        written.append(chash)
                    now = time.time()
                    if now - treport < 1:
                        continue
                    treport = now
                    x = broker.ask(
                        "up2k.fast_confirm_chunks", ptop, wark, written, locked
                    )
                    num_left, t = x.get()
                    if num_left < -1:
                        self.loud_reply(t, status=500)
                        locked = written = []
                        return False
                    elif num_left >= 0:
                        t = "got %d more chunks, %d left"
                        self.log(t % (len(written), num_left), 6)
                        locked = locked[len(written) :]
                        written = []

                if not fpool:
                    f.close()
                else:
                    with self.u2mutex:
                        self.u2fh.put(path, f)
            except:
                # maybe busted handle (eg. disk went full)
                f.close()
                raise
        finally:
            if locked:
                # now block until all chunks released+confirmed
                x = broker.ask("up2k.confirm_chunks", ptop, wark, written, locked)
                num_left, t = x.get()
                if num_left < 0:
                    self.loud_reply(t, status=500)
                    bail1 = True
                else:
                    t = "got %d more chunks, %d left"
                    self.log(t % (len(written), num_left), 6)

        if num_left < 0:
            if bail1:
                return False
            raise Pebkac(500, "unconfirmed; see serverlog")

        if not num_left and fpool:
            with self.u2mutex:
                self.u2fh.close(path)

        if not num_left and not self.args.nw:
            broker.ask("up2k.finish_upload", ptop, wark, self.u2fh.aps).get()

        cinf = self.headers.get("x-up2k-stat", "")

        spd = self._spd(postsize)
        self.log("%70s thank %r" % (spd, cinf))
        self.reply(b"thank")
        return True

    def handle_chpw(self)  :
        if self.args.usernames:
            self.parser.require("uname", 64)
        pwd = self.parser.require("pw", 64)
        self.parser.drop()

        ok, msg = self.asrv.chpw(self.conn.hsrv.broker, self.uname, pwd)
        if ok:
            self.cbonk(self.conn.hsrv.gpwc, pwd, "pw", "too many password changes")
            if self.args.usernames:
                pwd = "%s:%s" % (self.uname, pwd)
            ok, msg = self.get_pwd_cookie(pwd)
            if ok:
                msg = "new password OK"

        redir = (self.args.SRS + "?h") if ok else ""
        h2 = '<a href="' + self.args.SRS + '?h">continue</a>'
        html = self.j2s("msg", h1=msg, h2=h2, redir=redir)
        self.reply(html.encode("utf-8"))
        return True

    def handle_login(self)  :
        if self.args.usernames and not (
            self.args.shr and self.vpath.startswith(self.args.shr1)
        ):
            try:
                un = self.parser.require("uname", 64)
            except:
                un = ""
        else:
            un = ""
        pwd = self.parser.require("cppwd", 64)
        try:
            uhash = self.parser.require("uhash", 256)
        except:
            uhash = ""
        self.parser.drop()

        if not pwd:
            raise Pebkac(422, "password cannot be blank")

        if un:
            pwd = "%s:%s" % (un, pwd)

        dst = self.args.SRS
        if self.vpath:
            dst += quotep(self.vpaths)

        dst += self.ourlq()

        uhash = uhash.lstrip("#")
        if uhash not in ("", "-"):
            dst += "&" if "?" in dst else "?"
            dst += "_=1#" + html_escape(uhash, True, True)

        _, msg = self.get_pwd_cookie(pwd)
        h2 = '<a href="' + dst + '">continue</a>'
        html = self.j2s("msg", h1=msg, h2=h2, redir=dst)
        self.reply(html.encode("utf-8"))
        return True

    def handle_logout(self)  :
        self.parser.drop()

        self.log("logout " + self.uname)
        if not self.uname.startswith("s_"):
            self.asrv.forget_session(self.conn.hsrv.broker, self.uname)
        self.get_pwd_cookie("x")

        dst = self.args.idp_logout or (self.args.SRS + "?h")
        h2 = '<a href="' + dst + '">continue</a>'
        html = self.j2s("msg", h1="ok bye", h2=h2, redir=dst)
        self.reply(html.encode("utf-8"))
        return True

    def get_pwd_cookie(self, pwd )   :
        uname = self.asrv.sesa.get(pwd)
        if not uname:
            hpwd = self.asrv.ah.hash(pwd)
            uname = self.asrv.iacct.get(hpwd)
            if uname:
                pwd = self.asrv.ases.get(uname) or pwd
        if uname and self.conn.hsrv.ipr:
            znm = self.conn.hsrv.ipr.get(uname)
            if znm and not znm.map(self.ip):
                self.log("username [%s] rejected by --ipr" % (self.uname,), 3)
                uname = ""
        if uname:
            msg = "hi " + uname
            dur = int(60 * 60 * self.args.logout)
        else:
            logpwd = pwd
            if self.args.log_badpwd == 0:
                logpwd = ""
            elif self.args.log_badpwd == 2:
                zb = hashlib.sha512(pwd.encode("utf-8", "replace")).digest()
                logpwd = "%" + ub64enc(zb[:12]).decode("ascii")

            if pwd != "x":
                self.log("invalid password: %r" % (logpwd,), 3)
                self.cbonk(self.conn.hsrv.gpwd, pwd, "pw", "invalid passwords")

            msg = "naw dude"
            pwd = "x"  # nosec
            dur = 0

        if pwd == "x":
            # reset both plaintext and tls
            # (only affects active tls cookies when tls)
            for k in ("cppwd", "cppws") if self.is_https else ("cppwd",):
                ck = gencookie(k, pwd, self.args.R, self.args.cookie_lax, False)
                self.out_headerlist.append(("Set-Cookie", ck))
            self.out_headers.pop("Set-Cookie", None)  # drop keepalive
        else:
            k = "cppws" if self.is_https else "cppwd"
            ck = gencookie(
                k,
                pwd,
                self.args.R,
                self.args.cookie_lax,
                self.is_https,
                dur,
                "; HttpOnly",
            )
            self.out_headers["Set-Cookie"] = ck

        return dur > 0, msg

    def set_idp_cookie(self, ases)  :
        k = "cppws" if self.is_https else "cppwd"
        ck = gencookie(
            k,
            ases,
            self.args.R,
            self.args.cookie_lax,
            self.is_https,
            self.args.idp_cookie,
            "; HttpOnly",
        )
        self.out_headers["Set-Cookie"] = ck

    def handle_mkdir(self)  :
        new_dir = self.parser.require("name", 512)
        self.parser.drop()

        return self._mkdir(vjoin(self.vpath, new_dir))

    def _mkdir(self, vpath , dav  = False)  :
        nullwrite = self.args.nw
        self.gctx = vpath
        vpath = undot(vpath)
        vfs, rem = self.asrv.vfs.get(vpath, self.uname, False, True)
        if "nosub" in vfs.flags:
            raise Pebkac(403, "mkdir is forbidden below this folder")

        rem = sanitize_vpath(rem, "/")
        fn = vfs.canonical(rem)

        if not nullwrite:
            fdir = os.path.dirname(fn)

            if dav and not bos.path.isdir(fdir):
                raise Pebkac(409, "parent folder does not exist")

            if bos.path.isdir(fn):
                raise Pebkac(405, 'folder "/%s" already exists' % (vpath,))

            try:
                bos.makedirs(fn, vf=vfs.flags)
            except OSError as ex:
                if ex.errno == errno.EACCES:
                    raise Pebkac(500, "the server OS denied write-access")

                raise Pebkac(500, "mkdir failed:\n" + min_ex())
            except:
                raise Pebkac(500, min_ex())

        self.out_headers["X-New-Dir"] = quotep(self.args.RS + vpath)

        if dav:
            self.reply(b"", 201)
        else:
            self.redirect(vpath, status=201)

        return True

    def handle_new_md(self)  :
        new_file = self.parser.require("name", 512)
        self.parser.drop()

        nullwrite = self.args.nw
        vfs, rem = self.asrv.vfs.get(self.vpath, self.uname, False, True)
        self._assert_safe_rem(rem)

        ext = "" if "." not in new_file else new_file.split(".")[-1]
        if not ext or len(ext) > 5 or not self.can_delete:
            new_file += ".md"

        sanitized = sanitize_fn(new_file, "")
        fdir = vfs.canonical(rem)
        fn = os.path.join(fdir, sanitized)

        for hn in ("xbu", "xau"):
            xxu = vfs.flags.get(hn)
            if xxu:
                hr = runhook(
                    self.log,
                    self.conn.hsrv.broker,
                    None,
                    "%s.http.new-md" % (hn,),
                    xxu,
                    fn,
                    vjoin(self.vpath, sanitized),
                    self.host,
                    self.uname,
                    self.asrv.vfs.get_perms(self.vpath, self.uname),
                    time.time(),
                    0,
                    self.ip,
                    time.time(),
                    None,
                )
                t = hr.get("rejectmsg") or ""
                if t or not hr:
                    if not t:
                        t = "new-md blocked by " + hn + " server config: %r"
                        t = t % (vjoin(vfs.vpath, rem),)
                    self.log(t, 1)
                    raise Pebkac(403, t)

        if not nullwrite:
            if bos.path.exists(fn):
                raise Pebkac(500, "that file exists already")

            with open(fsenc(fn), "wb") as f:
                f.write(b"`GRUNNUR`\n")
                if "fperms" in vfs.flags:
                    set_fperms(f, vfs.flags)

            dbv, vrem = vfs.get_dbv(rem)
            self.conn.hsrv.broker.say(
                "up2k.hash_file",
                dbv.realpath,
                dbv.vpath,
                dbv.flags,
                vrem,
                sanitized,
                self.ip,
                bos.stat(fn).st_mtime,
                self.uname,
                True,
            )

        vpath = "{}/{}".format(self.vpath, sanitized).lstrip("/")
        self.redirect(vpath, "?edit")
        return True

    def upload_flags(self, vfs )     :
        if self.args.nw:
            rnd = 0
        else:
            rnd = int(self.uparam.get("rand") or self.headers.get("rand") or 0)
            if vfs.flags.get("rand"):  # force-enable
                rnd = max(rnd, vfs.flags["nrand"])

        zs = self.uparam.get("life", self.headers.get("life", ""))
        if zs:
            vlife = vfs.flags.get("lifetime") or 0
            lifetime = max(0, int(vlife - int(zs)))
        else:
            lifetime = 0

        return (
            rnd,
            lifetime,
            vfs.flags.get("xbu") or [],
            vfs.flags.get("xau") or [],
        )

    def handle_plain_upload(
        self,
        file0     ,
        nohash ,
    )  :
        assert self.parser
        nullwrite = self.args.nw
        vfs, rem = self.asrv.vfs.get(self.vpath, self.uname, False, True)
        self._assert_safe_rem(rem)

        hasher = None
        if nohash:
            halg = ""
            copier = justcopy
        else:
            copier = hashcopy
            halg = (
                self.ouparam.get("ck") or self.headers.get("ck") or vfs.flags["bup_ck"]
            )
            if halg == "sha512":
                pass
            elif halg == "no":
                copier = justcopy
                halg = ""
            elif halg == "md5":
                hasher = hashlib.md5(**USED4SEC)
            elif halg == "sha1":
                hasher = hashlib.sha1(**USED4SEC)
            elif halg == "sha256":
                hasher = hashlib.sha256(**USED4SEC)
            elif halg in ("blake2", "b2"):
                hasher = hashlib.blake2b(**USED4SEC)
            elif halg in ("blake2s", "b2s"):
                hasher = hashlib.blake2s(**USED4SEC)
            else:
                raise Pebkac(500, "unknown hash alg")

        upload_vpath = self.vpath
        lim = vfs.get_dbv(rem)[0].lim
        fdir_base = vfs.canonical(rem)
        if lim:
            fdir_base, rem = lim.all(
                self.ip, rem, -1, vfs.realpath, fdir_base, self.conn.hsrv.broker
            )
            upload_vpath = "{}/{}".format(vfs.vpath, rem).strip("/")
            if not nullwrite:
                bos.makedirs(fdir_base, vf=vfs.flags)

        rnd, lifetime, xbu, xau = self.upload_flags(vfs)
        zs = self.uparam.get("want") or self.headers.get("accept") or ""
        if zs:
            zs = zs.split(";", 1)[0].lower()
            if zs == "application/json":
                zs = "json"
        want_url = zs == "url"
        want_json = zs == "json" or "j" in self.uparam

        files       = []
        # sz, sha_hex, sha_b64, p_file, fname, abspath
        errmsg = ""
        tabspath = ""
        dip = self.dip()
        t0 = time.time()
        try:
            assert self.parser.gen
            gens = itertools.chain(file0, self.parser.gen)
            for nfile, (p_field, p_file, p_data) in enumerate(gens):
                if not p_file:
                    self.log("discarding incoming file without filename")
                    # fallthrough

                fdir = fdir_base
                fname = sanitize_fn(p_file or "", "")
                abspath = os.path.join(fdir, fname)
                suffix = "-%.6f-%s" % (time.time(), dip)
                if p_file and not nullwrite:
                    if rnd:
                        fname = rand_name(fdir, fname, rnd)

                    open_args = {"fdir": fdir, "suffix": suffix, "vf": vfs.flags}

                    if "replace" in self.uparam or "replace" in self.headers:
                        if not self.can_delete:
                            self.log("user not allowed to overwrite with ?replace")
                        elif bos.path.exists(abspath):
                            try:
                                wunlink(self.log, abspath, vfs.flags)
                                t = "overwriting file with new upload: %r"
                            except:
                                t = "toctou while deleting for ?replace: %r"
                            self.log(t % (abspath,))
                else:
                    open_args = {}
                    tnam = fname = os.devnull
                    fdir = abspath = ""

                if xbu:
                    at = time.time() - lifetime
                    hr = runhook(
                        self.log,
                        self.conn.hsrv.broker,
                        None,
                        "xbu.http.bup",
                        xbu,
                        abspath,
                        vjoin(upload_vpath, fname),
                        self.host,
                        self.uname,
                        self.asrv.vfs.get_perms(upload_vpath, self.uname),
                        at,
                        0,
                        self.ip,
                        at,
                        None,
                    )
                    t = hr.get("rejectmsg") or ""
                    if t or not hr:
                        if not t:
                            t = "upload blocked by xbu server config: %r"
                            t = t % (vjoin(upload_vpath, fname),)
                        self.log(t, 1)
                        raise Pebkac(403, t)
                    if hr.get("reloc"):
                        zs = vjoin(upload_vpath, fname)
                        x = pathmod(self.asrv.vfs, abspath, zs, hr["reloc"])
                        if x:
                            if self.args.hook_v:
                                log_reloc(
                                    self.log,
                                    hr["reloc"],
                                    x,
                                    abspath,
                                    zs,
                                    fname,
                                    vfs,
                                    rem,
                                )
                            fdir, upload_vpath, fname, (vfs, rem) = x
                            abspath = os.path.join(fdir, fname)
                            if nullwrite:
                                fdir = abspath = ""
                            else:
                                open_args["fdir"] = fdir

                if p_file and not nullwrite:
                    bos.makedirs(fdir, vf=vfs.flags)

                    # reserve destination filename
                    f, fname = ren_open(fname, "wb", fdir=fdir, suffix=suffix)
                    f.close()

                    tnam = fname + ".PARTIAL"
                    if self.args.dotpart:
                        tnam = "." + tnam

                    abspath = os.path.join(fdir, fname)
                else:
                    open_args = {}
                    tnam = fname = os.devnull
                    fdir = abspath = ""

                if lim:
                    lim.chk_bup(self.ip)
                    lim.chk_nup(self.ip)

                try:
                    max_sz = 0
                    if lim:
                        v1 = lim.smax
                        v2 = lim.dfv - lim.dfl
                        max_sz = min(v1, v2) if v1 and v2 else v1 or v2

                    f, tnam = ren_open(tnam, "wb", self.args.iobuf, **open_args)
                    try:
                        tabspath = os.path.join(fdir, tnam)
                        self.log("writing to %r" % (tabspath,))
                        sz, sha_hex, sha_b64 = copier(
                            p_data, f, hasher, max_sz, self.args.s_wr_slp
                        )
                    finally:
                        f.close()

                    if lim:
                        lim.nup(self.ip)
                        lim.bup(self.ip, sz)
                        try:
                            lim.chk_df(tabspath, sz, True)
                            lim.chk_sz(sz)
                            lim.chk_vsz(self.conn.hsrv.broker, vfs.realpath, sz)
                            lim.chk_bup(self.ip)
                            lim.chk_nup(self.ip)
                        except:
                            if not nullwrite:
                                wunlink(self.log, tabspath, vfs.flags)
                                wunlink(self.log, abspath, vfs.flags)
                            fname = os.devnull
                            raise

                    if not nullwrite:
                        atomic_move(self.log, tabspath, abspath, vfs.flags)

                    tabspath = ""

                    at = time.time() - lifetime
                    if xau:
                        hr = runhook(
                            self.log,
                            self.conn.hsrv.broker,
                            None,
                            "xau.http.bup",
                            xau,
                            abspath,
                            vjoin(upload_vpath, fname),
                            self.host,
                            self.uname,
                            self.asrv.vfs.get_perms(upload_vpath, self.uname),
                            at,
                            sz,
                            self.ip,
                            at,
                            None,
                        )
                        t = hr.get("rejectmsg") or ""
                        if t or not hr:
                            if not t:
                                t = "upload blocked by xau server config: %r"
                                t = t % (vjoin(upload_vpath, fname),)
                            self.log(t, 1)
                            wunlink(self.log, abspath, vfs.flags)
                            raise Pebkac(403, t)
                        if hr.get("reloc"):
                            zs = vjoin(upload_vpath, fname)
                            x = pathmod(self.asrv.vfs, abspath, zs, hr["reloc"])
                            if x:
                                if self.args.hook_v:
                                    log_reloc(
                                        self.log,
                                        hr["reloc"],
                                        x,
                                        abspath,
                                        zs,
                                        fname,
                                        vfs,
                                        rem,
                                    )
                                fdir, upload_vpath, fname, (vfs, rem) = x
                                ap2 = os.path.join(fdir, fname)
                                if nullwrite:
                                    fdir = ap2 = ""
                                else:
                                    bos.makedirs(fdir, vf=vfs.flags)
                                    atomic_move(self.log, abspath, ap2, vfs.flags)
                                abspath = ap2
                        sz = bos.path.getsize(abspath)

                    files.append(
                        (sz, sha_hex, sha_b64, p_file or "(discarded)", fname, abspath)
                    )
                    dbv, vrem = vfs.get_dbv(rem)
                    self.conn.hsrv.broker.say(
                        "up2k.hash_file",
                        dbv.realpath,
                        vfs.vpath,
                        dbv.flags,
                        vrem,
                        fname,
                        self.ip,
                        at,
                        self.uname,
                        True,
                    )
                    self.conn.nbyte += sz

                except Pebkac:
                    self.parser.drop()
                    raise

        except Pebkac as ex:
            errmsg = vol_san(
                list(self.asrv.vfs.all_vols.values()), unicode(ex).encode("utf-8")
            ).decode("utf-8")
            try:
                got = bos.path.getsize(tabspath)
                t = "connection lost after receiving %s of the file"
                self.log(t % (humansize(got),), 3)
            except:
                pass

        td = max(0.1, time.time() - t0)
        sz_total = sum(x[0] for x in files)
        spd = (sz_total / td) / (1024 * 1024)

        status = "OK"
        if errmsg:
            self.log(errmsg, 3)
            status = "ERROR"

        msg = "{} // {} bytes // {:.3f} MiB/s\n".format(status, sz_total, spd)
        jmsg   = {
            "status": status,
            "sz": sz_total,
            "mbps": round(spd, 3),
            "files": [],
        }

        if errmsg:
            msg += errmsg + "\n"
            jmsg["error"] = errmsg
            errmsg = "ERROR: " + errmsg

        if halg:
            file_fmt = '{0}: {1} // {2} // {3} bytes // <a href="/{4}">{5}</a> {6}\n'
        else:
            file_fmt = '{3} bytes // <a href="/{4}">{5}</a> {6}\n'

        for sz, sha_hex, sha_b64, ofn, lfn, ap in files:
            vsuf = ""
            if (self.can_read or self.can_upget) and "fk" in vfs.flags:
                st = A_FILE if nullwrite else bos.stat(ap)
                alg = 2 if "fka" in vfs.flags else 1
                vsuf = "?k=" + self.gen_fk(
                    alg,
                    self.args.fk_salt,
                    ap,
                    st.st_size,
                    0 if ANYWIN or not ap else st.st_ino,
                )[: vfs.flags["fk"]]

            if "media" in self.uparam or "medialinks" in vfs.flags:
                vsuf += "&v" if vsuf else "?v"

            vpath = "{}/{}".format(upload_vpath, lfn).strip("/")
            rel_url = quotep(self.args.RS + vpath) + vsuf
            msg += file_fmt.format(
                halg,
                sha_hex[:56],
                sha_b64,
                sz,
                rel_url,
                html_escape(ofn, crlf=True),
                vsuf,
            )
            # truncated SHA-512 prevents length extension attacks;
            # using SHA-512/224, optionally SHA-512/256 = :64
            jpart = {
                "url": "{}://{}/{}".format(
                    "https" if self.is_https else "http",
                    self.host,
                    rel_url,
                ),
                "sz": sz,
                "fn": lfn,
                "fn_orig": ofn,
                "path": rel_url,
            }
            if halg:
                jpart[halg] = sha_hex[:56]
                jpart["sha_b64"] = sha_b64
            jmsg["files"].append(jpart)

        vspd = self._spd(sz_total, False)
        self.log("%s %r" % (vspd, msg))

        suf = ""
        if not nullwrite and self.args.write_uplog:
            try:
                log_fn = "up.{:.6f}.txt".format(t0)
                with open(log_fn, "wb") as f:
                    ft = "{}:{}".format(self.ip, self.addr[1])
                    ft = "{}\n{}\n{}\n".format(ft, msg.rstrip(), errmsg)
                    f.write(ft.encode("utf-8"))
                    if "fperms" in vfs.flags:
                        set_fperms(f, vfs.flags)
            except Exception as ex:
                suf = "\nfailed to write the upload report: {}".format(ex)

        sc = 400 if errmsg else 201
        if want_url:
            msg = "\n".join([x["url"] for x in jmsg["files"]])
            if errmsg:
                msg += "\n" + errmsg

            self.reply(msg.encode("utf-8", "replace"), status=sc)
        elif want_json:
            if len(jmsg["files"]) == 1:
                jmsg["fileurl"] = jmsg["files"][0]["url"]
            jtxt = json.dumps(jmsg, indent=2, sort_keys=True).encode("utf-8", "replace")
            self.reply(jtxt, mime="application/json", status=sc)
        else:
            self.redirect(
                self.vpath,
                msg=msg + suf,
                flavor="return to",
                click=False,
                status=sc,
            )

        if errmsg:
            return False

        self.parser.drop()
        return True

    def handle_text_upload(self)  :
        try:
            cli_lastmod3 = int(self.parser.require("lastmod", 16))
        except:
            raise Pebkac(400, "could not read lastmod from request")

        nullwrite = self.args.nw
        vfs, rem = self.asrv.vfs.get(self.vpath, self.uname, True, True)
        self._assert_safe_rem(rem)

        clen = int(self.headers.get("content-length", -1))
        if clen == -1:
            raise Pebkac(411)

        rp, fn = vsplit(rem)
        fp = vfs.canonical(rp)
        lim = vfs.get_dbv(rem)[0].lim
        if lim:
            fp, rp = lim.all(self.ip, rp, clen, vfs.realpath, fp, self.conn.hsrv.broker)
            bos.makedirs(fp, vf=vfs.flags)

        fp = os.path.join(fp, fn)
        rem = "{}/{}".format(rp, fn).strip("/")
        dbv, vrem = vfs.get_dbv(rem)

        if not rem.lower().endswith(".md") and not self.can_delete:
            raise Pebkac(400, "only markdown pls")

        if nullwrite:
            response = json.dumps({"ok": True, "lastmod": 0})
            self.log(response)
            # TODO reply should parser.drop()
            self.parser.drop()
            self.reply(response.encode("utf-8"))
            return True

        srv_lastmod = -1.0
        srv_lastmod3 = -1
        try:
            st = bos.stat(fp)
            srv_lastmod = st.st_mtime
            srv_lastmod3 = int(srv_lastmod * 1000)
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                raise

        # if file exists, check that timestamp matches the client's
        if srv_lastmod >= 0:
            same_lastmod = cli_lastmod3 in [-1, srv_lastmod3]
            if not same_lastmod:
                # some filesystems/transports limit precision to 1sec, hopefully floored
                same_lastmod = (
                    srv_lastmod == int(cli_lastmod3 / 1000)
                    and cli_lastmod3 > srv_lastmod3
                    and cli_lastmod3 - srv_lastmod3 < 1000
                )

            if not same_lastmod:
                response = json.dumps(
                    {
                        "ok": False,
                        "lastmod": srv_lastmod3,
                        "now": int(time.time() * 1000),
                    }
                )
                self.log(
                    "{} - {} = {}".format(
                        srv_lastmod3, cli_lastmod3, srv_lastmod3 - cli_lastmod3
                    )
                )
                self.log(response)
                self.parser.drop()
                self.reply(response.encode("utf-8"))
                return True

            mdir, mfile = os.path.split(fp)
            fname, fext = mfile.rsplit(".", 1) if "." in mfile else (mfile, "md")
            mfile2 = "{}.{:.3f}.{}".format(fname, srv_lastmod, fext)

            dp = ""
            hist_cfg = dbv.flags["md_hist"]
            if hist_cfg == "v":
                vrd = vsplit(vrem)[0]
                zb = hashlib.sha512(afsenc(vrd)).digest()
                zs = ub64enc(zb).decode("ascii")[:24].lower()
                dp = "%s/md/%s/%s/%s" % (dbv.histpath, zs[:2], zs[2:4], zs)
                self.log("moving old version to %s/%s" % (dp, mfile2))
                if bos.makedirs(dp, vf=vfs.flags):
                    with open(os.path.join(dp, "dir.txt"), "wb") as f:
                        f.write(afsenc(vrd))
                        if "fperms" in vfs.flags:
                            set_fperms(f, vfs.flags)
            elif hist_cfg == "s":
                dp = os.path.join(mdir, ".hist")
                try:
                    bos.mkdir(dp, vfs.flags["chmod_d"])
                    if "chown" in vfs.flags:
                        bos.chown(dp, vfs.flags["uid"], vfs.flags["gid"])
                    hidedir(dp)
                except:
                    pass
            if dp:
                atomic_move(self.log, fp, os.path.join(dp, mfile2), vfs.flags)

        p_field, _, p_data = next(self.parser.gen)
        if p_field != "body":
            raise Pebkac(400, "expected body, got %r" % (p_field,))

        if "txt_eol" in vfs.flags:
            p_data = eol_conv(p_data, vfs.flags["txt_eol"])

        xbu = vfs.flags.get("xbu")
        if xbu:
            hr = runhook(
                self.log,
                self.conn.hsrv.broker,
                None,
                "xbu.http.txt",
                xbu,
                fp,
                self.vpath,
                self.host,
                self.uname,
                self.asrv.vfs.get_perms(self.vpath, self.uname),
                time.time(),
                0,
                self.ip,
                time.time(),
                None,
            )
            t = hr.get("rejectmsg") or ""
            if t or not hr:
                if not t:
                    t = "save blocked by xbu server config"
                self.log(t, 1)
                raise Pebkac(403, t)

        if bos.path.exists(fp):
            wunlink(self.log, fp, vfs.flags)

        with open(fsenc(fp), "wb", self.args.iobuf) as f:
            if "fperms" in vfs.flags:
                set_fperms(f, vfs.flags)
            sz, sha512, _ = hashcopy(p_data, f, None, 0, self.args.s_wr_slp)

        if lim:
            lim.nup(self.ip)
            lim.bup(self.ip, sz)
            try:
                lim.chk_sz(sz)
                lim.chk_vsz(self.conn.hsrv.broker, vfs.realpath, sz)
            except:
                wunlink(self.log, fp, vfs.flags)
                raise

        new_lastmod = bos.stat(fp).st_mtime
        new_lastmod3 = int(new_lastmod * 1000)
        sha512 = sha512[:56]

        xau = vfs.flags.get("xau")
        if xau:
            hr = runhook(
                self.log,
                self.conn.hsrv.broker,
                None,
                "xau.http.txt",
                xau,
                fp,
                self.vpath,
                self.host,
                self.uname,
                self.asrv.vfs.get_perms(self.vpath, self.uname),
                new_lastmod,
                sz,
                self.ip,
                new_lastmod,
                None,
            )
            t = hr.get("rejectmsg") or ""
            if t or not hr:
                if not t:
                    t = "save blocked by xau server config"
                self.log(t, 1)
                wunlink(self.log, fp, vfs.flags)
                raise Pebkac(403, t)

        self.conn.hsrv.broker.say(
            "up2k.hash_file",
            dbv.realpath,
            dbv.vpath,
            dbv.flags,
            vsplit(vrem)[0],
            fn,
            self.ip,
            new_lastmod,
            self.uname,
            True,
        )

        response = json.dumps(
            {"ok": True, "lastmod": new_lastmod3, "size": sz, "sha512": sha512}
        )
        self.log(response)
        self.parser.drop()
        self.reply(response.encode("utf-8"))
        return True

    def _chk_lastmod(self, file_ts )    :
        # ret: lastmod, do_send, can_range
        file_lastmod = formatdate(file_ts)
        c_ifrange = self.headers.get("if-range")
        c_lastmod = self.headers.get("if-modified-since")

        if not c_ifrange and not c_lastmod:
            return file_lastmod, True, True

        if c_ifrange and c_ifrange != file_lastmod:
            t = "sending entire file due to If-Range; cli(%s) file(%s)"
            self.log(t % (c_ifrange, file_lastmod), 6)
            return file_lastmod, True, False

        do_send = c_lastmod != file_lastmod
        if do_send and c_lastmod:
            t = "sending body due to If-Modified-Since cli(%s) file(%s)"
            self.log(t % (c_lastmod, file_lastmod), 6)
        elif not do_send and self.no304():
            do_send = True
            self.log("sending body due to no304")

        return file_lastmod, do_send, True

    def _use_dirkey(self, vn , ap )  :
        if self.can_read or not self.can_get:
            return False

        if vn.flags.get("dky"):
            return True

        req = self.uparam.get("k") or ""
        if not req:
            return False

        dk_len = vn.flags.get("dk")
        if not dk_len:
            return False

        if not ap:
            ap = vn.canonical(self.rem)

        zs = self.gen_fk(2, self.args.dk_salt, ap, 0, 0)[:dk_len]
        if req == zs:
            return True

        t = "wrong dirkey, want %s, got %s\n  vp: %r\n  ap: %r"
        self.log(t % (zs, req, self.req, ap), 6)
        return False

    def _use_filekey(self, vn , ap , st )  :
        if self.can_read or not self.can_get:
            return False

        req = self.uparam.get("k") or ""
        if not req:
            return False

        fk_len = vn.flags.get("fk")
        if not fk_len:
            return False

        if not ap:
            ap = self.vn.canonical(self.rem)

        alg = 2 if "fka" in vn.flags else 1

        zs = self.gen_fk(
            alg, self.args.fk_salt, ap, st.st_size, 0 if ANYWIN else st.st_ino
        )[:fk_len]

        if req == zs:
            return True

        t = "wrong filekey, want %s, got %s\n  vp: %r\n  ap: %r"
        self.log(t % (zs, req, self.req, ap), 6)
        return False

    def _add_logues(
        self, vn , abspath , lnames  
    )   :
        logues = ["", ""]
        if not self.args.no_logues:
            for n, fn in LOGUES:
                if lnames is not None and fn not in lnames:
                    continue
                fn = "%s/%s" % (abspath, fn)
                if bos.path.isfile(fn):
                    logues[n] = read_utf8(self.log, fsenc(fn), False)
                    if "exp" in vn.flags:
                        logues[n] = self._expand(
                            logues[n], vn.flags.get("exp_lg") or []
                        )

        readmes = ["", ""]
        for n, fns in [] if self.args.no_readme else READMES:
            if logues[n]:
                continue
            elif lnames is None:
                pass
            elif fns[0] in lnames:
                fns = [lnames[fns[0]]]
            else:
                fns = []

            txt = ""
            for fn in fns:
                fn = "%s/%s" % (abspath, fn)
                if bos.path.isfile(fn):
                    txt = read_utf8(self.log, fsenc(fn), False)
                    break

            if txt and "exp" in vn.flags:
                txt = self._expand(txt, vn.flags.get("exp_md") or [])

            readmes[n] = txt

        return logues, readmes

    def _expand(self, txt , phs )  :
        ptn_hsafe = RE_HSAFE
        for ph in phs:
            if ph.startswith("hdr."):
                sv = str(self.headers.get(ph[4:], ""))
            elif ph.startswith("self."):
                sv = str(getattr(self, ph[5:], ""))
            elif ph.startswith("cfg."):
                sv = str(getattr(self.args, ph[4:], ""))
            elif ph.startswith("vf."):
                sv = str(self.vn.flags.get(ph[3:]) or "")
            elif ph == "srv.itime":
                sv = str(int(time.time()))
            elif ph == "srv.htime":
                sv = datetime.now(UTC).strftime("%Y-%m-%d, %H:%M:%S")
            else:
                self.log("unknown placeholder in server config: [%s]" % (ph,), 3)
                continue

            sv = ptn_hsafe.sub("_", sv)
            txt = txt.replace("{{%s}}" % (ph,), sv)

        return txt

    def _can_tail(self, volflags  )  :
        zp = self.args.ua_nodoc
        if zp and zp.search(self.ua):
            t = "this URL contains no valuable information for bots/crawlers"
            raise Pebkac(403, t)
        lvl = volflags["tail_who"]
        if "notail" in volflags or not lvl:
            raise Pebkac(400, "tail is disabled in server config")
        elif lvl <= 1 and not self.can_admin:
            raise Pebkac(400, "tail is admin-only on this server")
        elif lvl <= 2 and self.uname in ("", "*"):
            raise Pebkac(400, "you must be authenticated to use ?tail on this server")
        return True

    def _can_zip(self, volflags  )  :
        lvl = volflags["zip_who"]
        if self.args.no_zip or not lvl:
            return "download-as-zip/tar is disabled in server config"
        elif lvl <= 1 and not self.can_admin:
            return "download-as-zip/tar is admin-only on this server"
        elif lvl <= 2 and self.uname in ("", "*"):
            return "you must be authenticated to download-as-zip/tar on this server"
        elif self.args.ua_nozip and self.args.ua_nozip.search(self.ua):
            t = "this URL contains no valuable information for bots/crawlers"
            raise Pebkac(403, t)
        return ""

    def tx_res(self, req_path )  :
        status = 200
        logmsg = "{:4} {} ".format("", self.req)
        logtail = ""

        editions = {}
        file_ts = 0

        if has_resource(self.E, req_path):
            st = stat_resource(self.E, req_path)
            if st:
                file_ts = max(file_ts, st.st_mtime)
            editions["plain"] = req_path

        if has_resource(self.E, req_path + ".gz"):
            st = stat_resource(self.E, req_path + ".gz")
            if st:
                file_ts = max(file_ts, st.st_mtime)
            if not st or st.st_mtime > file_ts:
                editions[".gz"] = req_path + ".gz"

        if not editions:
            return self.tx_404()

        #
        # force download

        if "dl" in self.ouparam:
            cdis = gen_content_disposition(os.path.basename(req_path))
            self.out_headers["Content-Disposition"] = cdis

        #
        # if-modified

        if file_ts > 0:
            file_lastmod, do_send, _ = self._chk_lastmod(int(file_ts))
            self.out_headers["Last-Modified"] = file_lastmod
            if not do_send:
                status = 304

            if self.can_write:
                self.out_headers["X-Lastmod3"] = str(int(file_ts * 1000))
        else:
            do_send = True

        #
        # Accept-Encoding and UA decides which edition to send

        decompress = False
        supported_editions = [
            x.strip()
            for x in self.headers.get("accept-encoding", "").lower().split(",")
        ]
        if ".gz" in editions:
            is_compressed = True
            selected_edition = ".gz"

            if "gzip" not in supported_editions:
                decompress = True
            else:
                if re.match(r"MSIE [4-6]\.", self.ua) and " SV1" not in self.ua:
                    decompress = True

            if not decompress:
                self.out_headers["Content-Encoding"] = "gzip"
        else:
            is_compressed = False
            selected_edition = "plain"

        res_path = editions[selected_edition]
        logmsg += "{} ".format(selected_edition.lstrip("."))

        res = load_resource(self.E, res_path)

        if decompress:
            file_sz = gzip_file_orig_sz(res)
            res = gzip.open(res)
        else:
            res.seek(0, os.SEEK_END)
            file_sz = res.tell()
            res.seek(0, os.SEEK_SET)

        #
        # send reply

        if is_compressed:
            self.out_headers["Cache-Control"] = "max-age=604869"
        else:
            self.permit_caching()

        if "txt" in self.uparam:
            mime = "text/plain; charset={}".format(self.uparam["txt"] or "utf-8")
        elif "mime" in self.uparam:
            mime = str(self.uparam.get("mime"))
        else:
            mime = guess_mime(req_path)

        logmsg += unicode(status) + logtail

        if self.mode == "HEAD" or not do_send:
            res.close()
            if self.do_log:
                self.log(logmsg)

            self.send_headers(length=file_sz, status=status, mime=mime)
            return True

        ret = True
        self.send_headers(length=file_sz, status=status, mime=mime)
        remains = sendfile_py(
            self.log,
            0,
            file_sz,
            res,
            self.s,
            self.args.s_wr_sz,
            self.args.s_wr_slp,
            not self.args.no_poll,
            {},
            "",
        )
        res.close()

        if remains > 0:
            logmsg += " \033[31m" + unicode(file_sz - remains) + "\033[0m"
            ret = False

        spd = self._spd(file_sz - remains)
        if self.do_log:
            self.log("{},  {}".format(logmsg, spd))

        return ret

    def tx_file(self, req_path , ptop  = None)  :
        status = 200
        logmsg = "{:4} {} ".format("", self.req)
        logtail = ""

        is_tail = "tail" in self.uparam and self._can_tail(self.vn.flags)

        if ptop is not None:
            ap_data = "<%s>" % (req_path,)
            try:
                dp, fn = os.path.split(req_path)
                tnam = fn + ".PARTIAL"
                if self.args.dotpart:
                    tnam = "." + tnam
                ap_data = os.path.join(dp, tnam)
                st_data = bos.stat(ap_data)
                if not st_data.st_size:
                    raise Exception("partial is empty")
                x = self.conn.hsrv.broker.ask("up2k.find_job_by_ap", ptop, req_path)
                job = json.loads(x.get())
                if not job:
                    raise Exception("not found in registry")
                self.pipes.set(req_path, job)
            except Exception as ex:
                if getattr(ex, "errno", 0) != errno.ENOENT:
                    self.log("will not pipe %r; %s" % (ap_data, ex), 6)
                ptop = None

        #
        # if request is for foo.js, check if we have foo.js.gz

        file_ts = 0.0
        editions    = {}
        for ext in ("", ".gz"):
            if ptop is not None:
                sz = job["size"]
                file_ts = max(0, job["lmod"])
                editions["plain"] = (ap_data, sz)
                break

            try:
                fs_path = req_path + ext
                st = bos.stat(fs_path)
                if stat.S_ISDIR(st.st_mode):
                    continue

                if stat.S_ISBLK(st.st_mode):
                    fd = bos.open(fs_path, os.O_RDONLY)
                    try:
                        sz = os.lseek(fd, 0, os.SEEK_END)
                    finally:
                        os.close(fd)
                else:
                    sz = st.st_size

                file_ts = max(file_ts, st.st_mtime)
                editions[ext or "plain"] = (fs_path, sz)
            except:
                pass
            if not self.vpath.startswith(".cpr/"):
                break

        if not editions:
            return self.tx_404()

        #
        # force download

        if "dl" in self.ouparam:
            cdis = gen_content_disposition(os.path.basename(req_path))
            self.out_headers["Content-Disposition"] = cdis

        #
        # if-modified

        file_lastmod, do_send, can_range = self._chk_lastmod(int(file_ts))
        self.out_headers["Last-Modified"] = file_lastmod
        if not do_send:
            status = 304

        if self.can_write:
            self.out_headers["X-Lastmod3"] = str(int(file_ts * 1000))

        #
        # Accept-Encoding and UA decides which edition to send

        decompress = False
        supported_editions = [
            x.strip()
            for x in self.headers.get("accept-encoding", "").lower().split(",")
        ]
        if ".gz" in editions:
            is_compressed = True
            selected_edition = ".gz"
            fs_path, file_sz = editions[".gz"]
            if "gzip" not in supported_editions:
                decompress = True
            else:
                if re.match(r"MSIE [4-6]\.", self.ua) and " SV1" not in self.ua:
                    decompress = True

            if not decompress:
                self.out_headers["Content-Encoding"] = "gzip"
        else:
            is_compressed = False
            selected_edition = "plain"

        fs_path, file_sz = editions[selected_edition]
        logmsg += "{} ".format(selected_edition.lstrip("."))

        #
        # partial

        lower = 0
        upper = file_sz
        hrange = self.headers.get("range")

        # let's not support 206 with compression
        # and multirange / multipart is also not-impl (mostly because calculating contentlength is a pain)
        if (
            do_send
            and not is_compressed
            and hrange
            and can_range
            and file_sz
            and "," not in hrange
            and not is_tail
        ):
            try:
                if not hrange.lower().startswith("bytes"):
                    raise Exception()

                a, b = hrange.split("=", 1)[1].split("-")

                if a.strip():
                    lower = int(a.strip())
                else:
                    lower = 0

                if b.strip():
                    upper = int(b.strip()) + 1
                else:
                    upper = file_sz

                if upper > file_sz:
                    upper = file_sz

                if lower < 0 or lower >= upper:
                    raise Exception()

            except:
                err = "invalid range ({}), size={}".format(hrange, file_sz)
                self.loud_reply(
                    err,
                    status=416,
                    headers={"Content-Range": "bytes */{}".format(file_sz)},
                )
                return True

            status = 206
            self.out_headers["Content-Range"] = "bytes {}-{}/{}".format(
                lower, upper - 1, file_sz
            )

            logtail += " [\033[36m{}-{}\033[0m]".format(lower, upper)

        use_sendfile = False
        if decompress:
            open_func  = gzip.open
            open_args  = [fsenc(fs_path), "rb"]
            # Content-Length := original file size
            upper = gzip_orig_sz(fs_path)
        else:
            open_func = open
            open_args = [fsenc(fs_path), "rb", self.args.iobuf]
            use_sendfile = (
                # fmt: off
                not self.tls
                and not self.args.no_sendfile
                and (BITNESS > 32 or file_sz < 0x7fffFFFF)
                # fmt: on
            )

        #
        # send reply

        if is_compressed:
            self.out_headers["Cache-Control"] = "max-age=604869"
        else:
            self.permit_caching()

        if "txt" in self.uparam:
            mime = "text/plain; charset={}".format(self.uparam["txt"] or "utf-8")
        elif "mime" in self.uparam:
            mime = str(self.uparam.get("mime"))
        elif "rmagic" in self.vn.flags:
            mime = guess_mime(req_path, fs_path)
        else:
            mime = guess_mime(req_path)

        if "nohtml" in self.vn.flags and "html" in mime:
            mime = "text/plain; charset=utf-8"

        self.out_headers["Accept-Ranges"] = "bytes"
        logmsg += unicode(status) + logtail

        if self.mode == "HEAD" or not do_send:
            if self.do_log:
                self.log(logmsg)

            self.send_headers(length=upper - lower, status=status, mime=mime)
            return True

        dls = self.conn.hsrv.dls
        if is_tail:
            upper = 1 << 30
            if len(dls) > self.args.tail_cmax:
                raise Pebkac(400, "too many active downloads to start a new tail")

        if upper - lower > 0x400000:  # 4m
            now = time.time()
            self.dl_id = "%s:%s" % (self.ip, self.addr[1])
            dls[self.dl_id] = (now, 0)
            self.conn.hsrv.dli[self.dl_id] = (
                now,
                0 if is_tail else upper - lower,
                self.vn,
                self.vpath,
                self.uname,
            )

        if ptop is not None:
            return self.tx_pipe(
                ptop, req_path, ap_data, job, lower, upper, status, mime, logmsg
            )
        elif is_tail:
            self.tx_tail(open_args, status, mime)
            return False

        ret = True
        with open_func(*open_args) as f:
            self.send_headers(length=upper - lower, status=status, mime=mime)

            sendfun = sendfile_kern if use_sendfile else sendfile_py
            remains = sendfun(
                self.log,
                lower,
                upper,
                f,
                self.s,
                self.args.s_wr_sz,
                self.args.s_wr_slp,
                not self.args.no_poll,
                dls,
                self.dl_id,
            )

        if remains > 0:
            logmsg += " \033[31m" + unicode(upper - remains) + "\033[0m"
            ret = False

        spd = self._spd((upper - lower) - remains)
        if self.do_log:
            self.log("{},  {}".format(logmsg, spd))

        return ret

    def tx_tail(
        self,
        open_args ,
        status ,
        mime ,
    )  :
        vf = self.vn.flags
        self.send_headers(length=None, status=status, mime=mime)
        abspath  = open_args[0]
        sec_rate = vf["tail_rate"]
        sec_max = vf["tail_tmax"]
        sec_fd = vf["tail_fd"]
        sec_ka = self.args.tail_ka
        wr_slp = self.args.s_wr_slp
        wr_sz = self.args.s_wr_sz
        dls = self.conn.hsrv.dls
        dl_id = self.dl_id

        # non-numeric = full file from start
        # positive = absolute offset from start
        # negative = start that many bytes from eof
        try:
            ofs = int(self.uparam["tail"])
        except:
            ofs = 0

        t0 = time.time()
        ofs0 = ofs
        f = None
        try:
            st = os.stat(abspath)
            f = open(*open_args)
            f.seek(0, os.SEEK_END)
            eof = f.tell()
            f.seek(0)
            if ofs < 0:
                ofs = max(0, ofs + eof)

            self.log("tailing from byte %d: %r" % (ofs, abspath), 6)

            # send initial data asap
            remains = sendfile_py(
                self.log,  # d/c
                ofs,
                eof,
                f,
                self.s,
                wr_sz,
                wr_slp,
                False,  # d/c
                dls,
                dl_id,
            )
            sent = (eof - ofs) - remains
            ofs = eof - remains
            f.seek(ofs)

            try:
                st2 = os.stat(open_args[0])
                if st.st_ino == st2.st_ino:
                    st = st2  # for filesize
            except:
                pass

            gone = 0
            t_fd = t_ka = time.time()
            while True:
                buf = f.read(4096)
                now = time.time()

                if sec_max and now - t0 >= sec_max:
                    self.log("max duration exceeded; kicking client", 6)
                    zb = b"\n\n*** max duration exceeded; disconnecting ***\n"
                    self.s.sendall(zb)
                    break

                if buf:
                    t_fd = t_ka = now
                    self.s.sendall(buf)
                    sent += len(buf)
                    dls[dl_id] = (time.time(), sent)
                    continue

                time.sleep(sec_rate)
                if t_ka < now - sec_ka:
                    t_ka = now
                    self.s.send(b"\x00")
                if t_fd < now - sec_fd:
                    try:
                        st2 = os.stat(open_args[0])
                        if (
                            st2.st_ino != st.st_ino
                            or st2.st_size < sent
                            or st2.st_size < st.st_size
                        ):
                            # open new file before closing previous to avoid toctous (open may fail; cannot null f before)
                            f2 = open(*open_args)
                            f.close()
                            f = f2
                            f.seek(0, os.SEEK_END)
                            eof = f.tell()
                            if eof < sent:
                                ofs = sent = 0  # shrunk; send from start
                                zb = b"\n\n*** file size decreased -- rewinding to the start of the file ***\n\n"
                                self.s.sendall(zb)
                                if ofs0 < 0 and eof > -ofs0:
                                    ofs = eof + ofs0
                            else:
                                ofs = sent  # just new fd? resume from same ofs
                            f.seek(ofs)
                            self.log("reopened at byte %d: %r" % (ofs, abspath), 6)
                            gone = 0
                        st = st2
                    except:
                        gone += 1
                        if gone > 3:
                            self.log("file deleted; disconnecting")
                            break
        except IOError as ex:
            if ex.errno not in E_SCK_WR:
                raise
        finally:
            if f:
                f.close()

    def tx_pipe(
        self,
        ptop ,
        req_path ,
        ap_data ,
        job  ,
        lower ,
        upper ,
        status ,
        mime ,
        logmsg ,
    )  :
        M = 1048576
        self.send_headers(length=upper - lower, status=status, mime=mime)
        wr_slp = self.args.s_wr_slp
        wr_sz = self.args.s_wr_sz
        file_size = job["size"]
        chunk_size = up2k_chunksize(file_size)
        num_need = -1
        data_end = 0
        remains = upper - lower
        broken = False
        spins = 0
        tier = 0
        tiers = ["uncapped", "reduced speed", "one byte per sec"]

        while lower < upper and not broken:
            with self.u2mutex:
                job = self.pipes.get(req_path)
                if not job:
                    x = self.conn.hsrv.broker.ask("up2k.find_job_by_ap", ptop, req_path)
                    job = json.loads(x.get())
                    if job:
                        self.pipes.set(req_path, job)

            if not job:
                t = "pipe: OK, upload has finished; yeeting remainder"
                self.log(t, 2)
                data_end = file_size
                break

            if num_need != len(job["need"]) and data_end - lower < 8 * M:
                num_need = len(job["need"])
                data_end = 0
                for cid in job["hash"]:
                    if cid in job["need"]:
                        break
                    data_end += chunk_size
                t = "pipe: can stream %.2f MiB; requested range is %.2f to %.2f"
                self.log(t % (data_end / M, lower / M, upper / M), 6)
                with self.u2mutex:
                    if data_end > self.u2fh.aps.get(ap_data, data_end):
                        fhs  = None
                        try:
                            fhs = self.u2fh.cache[ap_data].all_fhs
                            for fh in fhs:
                                fh.flush()
                            self.u2fh.aps[ap_data] = data_end
                            self.log("pipe: flushed %d up2k-FDs" % (len(fhs),))
                        except Exception as ex:
                            if fhs is None:
                                err = "file is not being written to right now"
                            else:
                                err = repr(ex)
                            self.log("pipe: u2fh flush failed: " + err)

            if lower >= data_end:
                if data_end:
                    t = "pipe: uploader is too slow; aborting download at %.2f MiB"
                    self.log(t % (data_end / M,))
                    raise Pebkac(416, "uploader is too slow")

                raise Pebkac(416, "no data available yet; please retry in a bit")

            slack = data_end - lower
            if slack >= 8 * M:
                ntier = 0
                winsz = M
                bufsz = wr_sz
                slp = wr_slp
            else:
                winsz = max(40, int(M * (slack / (12 * M))))
                base_rate = M if not wr_slp else wr_sz / wr_slp
                if winsz > base_rate:
                    ntier = 0
                    bufsz = wr_sz
                    slp = wr_slp
                elif winsz > 300:
                    ntier = 1
                    bufsz = winsz // 5
                    slp = 0.2
                else:
                    ntier = 2
                    bufsz = winsz = slp = 1

            if tier != ntier:
                tier = ntier
                self.log("moved to tier %d (%s)" % (tier, tiers[tier]))

            try:
                with open(ap_data, "rb", self.args.iobuf) as f:
                    f.seek(lower)
                    page = f.read(min(winsz, data_end - lower, upper - lower))
                if not page:
                    raise Exception("got 0 bytes (EOF?)")
            except Exception as ex:
                self.log("pipe: read failed at %.2f MiB: %s" % (lower / M, ex), 3)
                with self.u2mutex:
                    self.pipes.c.pop(req_path, None)
                spins += 1
                if spins > 3:
                    raise Pebkac(500, "file became unreadable")
                time.sleep(2)
                continue

            spins = 0
            pofs = 0
            while pofs < len(page):
                if slp:
                    time.sleep(slp)

                try:
                    buf = page[pofs : pofs + bufsz]
                    self.s.sendall(buf)
                    zi = len(buf)
                    remains -= zi
                    lower += zi
                    pofs += zi
                except:
                    broken = True
                    break

        if lower < upper and not broken:
            with open(req_path, "rb") as f:
                remains = sendfile_py(
                    self.log,
                    lower,
                    upper,
                    f,
                    self.s,
                    wr_sz,
                    wr_slp,
                    not self.args.no_poll,
                    self.conn.hsrv.dls,
                    self.dl_id,
                )

        spd = self._spd((upper - lower) - remains)
        if self.do_log:
            self.log("{},  {}".format(logmsg, spd))

        return not broken

    def tx_zip(
        self,
        fmt ,
        uarg ,
        vpath ,
        vn ,
        rem ,
        items ,
    )  :
        t = self._can_zip(vn.flags)
        if t:
            raise Pebkac(400, t)

        logmsg = "{:4} {} ".format("", self.req)
        self.keepalive = False

        cancmp = not self.args.no_tarcmp

        if fmt == "tar":
            packer  = StreamTar
            if cancmp and "gz" in uarg:
                mime = "application/gzip"
                ext = "tar.gz"
            elif cancmp and "bz2" in uarg:
                mime = "application/x-bzip"
                ext = "tar.bz2"
            elif cancmp and "xz" in uarg:
                mime = "application/x-xz"
                ext = "tar.xz"
            else:
                mime = "application/x-tar"
                ext = "tar"
        else:
            mime = "application/zip"
            packer = StreamZip
            ext = "zip"

        fn = self.vpath.split("/")[-1] or self.host.split(":")[0]
        if items:
            fn = "sel-" + fn

        if vn.flags.get("zipmax") and not (
            vn.flags.get("zipmaxu") and self.uname != "*"
        ):
            maxs = vn.flags.get("zipmaxs_v") or 0
            maxn = vn.flags.get("zipmaxn_v") or 0
            nf = 0
            nb = 0
            fgen = vn.zipgen(
                vpath, rem, set(items), self.uname, False, not self.args.no_scandir
            )
            t = "total size exceeds a limit specified in server config"
            t = vn.flags.get("zipmaxt") or t
            if maxs and maxn:
                for zd in fgen:
                    nf += 1
                    nb += zd["st"].st_size
                    if maxs < nb or maxn < nf:
                        raise Pebkac(400, t)
            elif maxs:
                for zd in fgen:
                    nb += zd["st"].st_size
                    if maxs < nb:
                        raise Pebkac(400, t)
            elif maxn:
                for zd in fgen:
                    nf += 1
                    if maxn < nf:
                        raise Pebkac(400, t)

        cdis = gen_content_disposition("%s.%s" % (fn, ext))
        self.log(repr(cdis))
        self.send_headers(None, mime=mime, headers={"Content-Disposition": cdis})

        fgen = vn.zipgen(
            vpath, rem, set(items), self.uname, False, not self.args.no_scandir
        )
        # for f in fgen: print(repr({k: f[k] for k in ["vp", "ap"]}))
        cfmt = ""
        if self.thumbcli and not self.args.no_bacode:
            for zs in ("opus", "mp3", "flac", "wav", "w", "j", "p"):
                if zs in self.ouparam or uarg == zs:
                    cfmt = zs

            if cfmt:
                self.log("transcoding to [{}]".format(cfmt))
                fgen = gfilter(fgen, self.thumbcli, self.uname, vpath, cfmt)

        now = time.time()
        self.dl_id = "%s:%s" % (self.ip, self.addr[1])
        self.conn.hsrv.dli[self.dl_id] = (
            now,
            0,
            self.vn,
            "%s :%s" % (self.vpath, ext),
            self.uname,
        )
        dls = self.conn.hsrv.dls
        dls[self.dl_id] = (time.time(), 0)

        bgen = packer(
            self.log,
            self.asrv,
            fgen,
            utf8="utf" in uarg or not uarg,
            pre_crc="crc" in uarg,
            cmp=uarg if cancmp or uarg == "pax" else "",
        )
        n = 0
        bsent = 0
        for buf in bgen.gen():
            if not buf:
                break

            try:
                self.s.sendall(buf)
                bsent += len(buf)
            except:
                logmsg += " \033[31m" + unicode(bsent) + "\033[0m"
                bgen.stop()
                break

            n += 1
            if n >= 4:
                n = 0
                dls[self.dl_id] = (time.time(), bsent)

        spd = self._spd(bsent)
        self.log("{},  {}".format(logmsg, spd))
        return True

    def tx_ico(self, ext , exact  = False)  :
        self.permit_caching()
        if ext.endswith("/"):
            ext = "folder"
            exact = True

        bad = re.compile(r"[](){}/ []|^[0-9_-]*$")
        n = ext.split(".")[::-1]
        if not exact:
            n = n[:-1]

        ext = ""
        for v in n:
            if len(v) > 7 or bad.search(v):
                break

            ext = "{}.{}".format(v, ext)

        ext = ext.rstrip(".") or "unk"
        if len(ext) > 11:
            ext = "~" + ext[-9:]

        return self.tx_svg(ext, exact)

    def tx_svg(self, txt , small  = False)  :
        # chrome cannot handle more than ~2000 unique SVGs
        # so url-param "raster" returns a png/webp instead
        # (useragent-sniffing kinshi due to caching proxies)
        mime, ico = self.ico.get(txt, not small, "raster" in self.uparam)

        lm = formatdate(self.E.t0)
        self.reply(ico, mime=mime, headers={"Last-Modified": lm})
        return True

    def tx_qr(self):
        url = "%s://%s%s%s" % (
            "https" if self.is_https else "http",
            self.host,
            self.args.SRS,
            self.vpaths,
        )
        uhash = ""
        uparams = []
        if self.ouparam:
            for k, v in self.ouparam.items():
                if k == "qr":
                    continue
                if k == "uhash":
                    uhash = v
                    continue
                uparams.append(k if v == "" else "%s=%s" % (k, v))
        if uparams:
            url += "?" + "&".join(uparams)
        if uhash:
            url += "#" + uhash

        self.log("qrcode(%r)" % (url,))
        ret = qr2svg(qrgen(url.encode("utf-8")), 2)
        self.reply(ret.encode("utf-8"), mime="image/svg+xml")
        return True

    def tx_md(self, vn , fs_path )  :
        logmsg = "     %s @%s " % (self.req, self.uname)

        if not self.can_write:
            if "edit" in self.uparam or "edit2" in self.uparam:
                return self.tx_404(True)

        tpl = "mde" if "edit2" in self.uparam else "md"
        template = self.j2j(tpl)

        st = bos.stat(fs_path)
        ts_md = st.st_mtime

        max_sz = 1024 * self.args.txt_max
        sz_md = 0
        lead = b""
        fullfile = b""
        for buf in yieldfile(fs_path, self.args.iobuf):
            if sz_md < max_sz:
                fullfile += buf
            else:
                fullfile = b""

            if not sz_md and buf.startswith((b"\n", b"\r\n")):
                lead = b"\n" if buf.startswith(b"\n") else b"\r\n"
                sz_md += len(lead)

            sz_md += len(buf)
            for c, v in [(b"&", 4), (b"<", 3), (b">", 3)]:
                sz_md += (len(buf) - len(buf.replace(c, b""))) * v

        if (
            fullfile
            and "exp" in vn.flags
            and "edit" not in self.uparam
            and "edit2" not in self.uparam
            and vn.flags.get("exp_md")
        ):
            fulltxt = fullfile.decode("utf-8", "replace")
            fulltxt = self._expand(fulltxt, vn.flags.get("exp_md") or [])
            fullfile = fulltxt.encode("utf-8", "replace")

        if fullfile:
            fullfile = html_bescape(fullfile)
            sz_md = len(lead) + len(fullfile)

        file_ts = int(max(ts_md, self.E.t0))
        file_lastmod, do_send, _ = self._chk_lastmod(file_ts)
        self.out_headers["Last-Modified"] = file_lastmod
        self.out_headers.update(NO_CACHE)
        status = 200 if do_send else 304

        arg_base = "?"
        if "k" in self.uparam:
            arg_base = "?k={}&".format(self.uparam["k"])

        boundary = "\roll\tide"
        targs = {
            "r": self.args.SR if self.is_vproxied else "",
            "ts": self.conn.hsrv.cachebuster(),
            "edit": "edit" in self.uparam,
            "title": html_escape(self.vpath, crlf=True),
            "lastmod": int(ts_md * 1000),
            "lang": self.cookies.get("cplng") or self.args.lang,
            "favico": self.args.favico,
            "have_emp": int(self.args.emp),
            "md_no_br": int(vn.flags.get("md_no_br") or 0),
            "md_chk_rate": self.args.mcr,
            "md": boundary,
            "arg_base": arg_base,
        }

        if self.args.js_other and "js" not in targs:
            zs = self.args.js_other
            zs += "&" if "?" in zs else "?"
            targs["js"] = zs

        if "html_head_d" in self.vn.flags:
            targs["this"] = self
            self._build_html_head(targs)

        targs["html_head"] = self.html_head
        zs = template.render(**targs).encode("utf-8", "replace")
        html = zs.split(boundary.encode("utf-8"))
        if len(html) != 2:
            raise Exception("boundary appears in " + tpl)

        self.send_headers(sz_md + len(html[0]) + len(html[1]), status)

        logmsg += unicode(status)
        if self.mode == "HEAD" or not do_send:
            if self.do_log:
                self.log(logmsg)

            return True

        try:
            self.s.sendall(html[0] + lead)
            if fullfile:
                self.s.sendall(fullfile)
            else:
                for buf in yieldfile(fs_path, self.args.iobuf):
                    self.s.sendall(html_bescape(buf))

            self.s.sendall(html[1])

        except:
            self.log(logmsg + " \033[31md/c\033[0m")
            return False

        if self.do_log:
            self.log(logmsg + " " + unicode(len(html)))

        return True

    def tx_svcs(self)  :
        aname = re.sub("[^0-9a-zA-Z]+", "", self.args.vname) or "a"
        ep = self.host
        sep = "]:" if "]" in ep else ":"
        if sep in ep:
            host, hport = ep.rsplit(":", 1)
            hport = ":" + hport
        else:
            host = ep
            hport = ""

        if host.endswith(".local") and self.args.zm and not self.args.rclone_mdns:
            rip = self.conn.hsrv.nm.map(self.ip) or host
            if ":" in rip and "[" not in rip:
                rip = "[%s]" % (rip,)
        else:
            rip = host

        defpw = "dave:hunter2" if self.args.usernames else "hunter2"

        vp = (self.uparam["hc"] or "").lstrip("/")
        pw = self.ouparam.get("pw") or defpw
        if pw in self.asrv.sesa:
            pw = defpw

        unpw = pw
        try:
            un, pw = unpw.split(":")
        except:
            un = ""
            if self.args.usernames:
                un = "dave"

        html = self.j2s(
            "svcs",
            args=self.args,
            accs=bool(self.asrv.acct),
            s="s" if self.is_https else "",
            rip=html_sh_esc(rip),
            ep=html_sh_esc(ep),
            vp=html_sh_esc(vp),
            rvp=html_sh_esc(vjoin(self.args.R, vp)),
            host=html_sh_esc(host),
            hport=html_sh_esc(hport),
            aname=aname,
            b_un=("<b>%s</b>" % (html_sh_esc(un),)) if un else "k",
            un=html_sh_esc(un),
            pw=html_sh_esc(pw),
            unpw=html_sh_esc(unpw),
        )
        self.reply(html.encode("utf-8"))
        return True

    def tx_mounts(self)  :
        suf = self.urlq({}, ["h"])
        rvol, wvol, avol = [
            [("/" + x).rstrip("/") + "/" for x in y]
            for y in [self.rvol, self.wvol, self.avol]
        ]

        ups = []
        now = time.time()
        get_vst = self.avol and not self.args.no_rescan
        get_ups = self.rvol and not self.args.no_up_list and self.uname or ""
        if get_vst or get_ups:
            x = self.conn.hsrv.broker.ask("up2k.get_state", get_vst, get_ups)
            vs = json.loads(x.get())
            vstate = {("/" + k).rstrip("/") + "/": v for k, v in vs["volstate"].items()}
            try:
                for rem, sz, t0, poke, vp in vs["ups"]:
                    fdone = max(0.001, 1 - rem)
                    td = max(0.1, now - t0)
                    rd, fn = vsplit(vp.replace(os.sep, "/"))
                    if not rd:
                        rd = "/"
                    erd = quotep(rd)
                    rds = rd.replace("/", " / ")
                    spd = humansize(sz * fdone / td, True) + "/s"
                    eta = s2hms((td / fdone) - td, True) if rem < 1 else "--"
                    idle = s2hms(now - poke, True)
                    ups.append((int(100 * fdone), spd, eta, idle, erd, rds, fn))
            except Exception as ex:
                self.log("failed to list upload progress: %r" % (ex,), 1)
        if not get_vst:
            vstate = {}
            vs = {
                "scanning": None,
                "hashq": None,
                "tagq": None,
                "mtpq": None,
                "dbwt": None,
            }


        dls = dl_list = []
        if self.conn.hsrv.tdls:
            zi = self.args.dl_list
            if zi == 2 or (zi == 1 and self.avol):
                dl_list = self.get_dls()
        for t0, t1, sent, sz, vp, dl_id, uname in dl_list:
            td = max(0.1, now - t0)
            rd, fn = vsplit(vp)
            if not rd:
                rd = "/"
            erd = quotep(rd)
            rds = rd.replace("/", " / ")
            spd = humansize(sent / td, True) + "/s"
            hsent = humansize(sent, True)
            idle = s2hms(now - t1, True)
            usr = "%s @%s" % (dl_id, uname) if dl_id else uname
            if sz and sent and td:
                eta = s2hms((sz - sent) / (sent / td), True)
                perc = int(100 * sent / sz)
            else:
                eta = perc = "--"

            fn = html_escape(fn) if fn else self.conn.hsrv.iiam
            dls.append((perc, hsent, spd, eta, idle, usr, erd, rds, fn))

        if self.args.have_unlistc:
            allvols = self.asrv.vfs.all_vols
            rvol = [x for x in rvol if "unlistcr" not in allvols[x[1:-1]].flags]
            wvol = [x for x in wvol if "unlistcw" not in allvols[x[1:-1]].flags]

        fmt = self.uparam.get("ls", "")
        if not fmt and self.ua.startswith(("curl/", "fetch")):
            fmt = "v"

        if fmt in ["v", "t", "txt"]:
            if self.uname == "*":
                txt = "howdy stranger (you're not logged in)"
            else:
                txt = "welcome back {}".format(self.uname)

            if vstate:
                txt += "\nstatus:"
                for k in ["scanning", "hashq", "tagq", "mtpq", "dbwt"]:
                    txt += " {}({})".format(k, vs[k])

            if ups:
                txt += "\n\nincoming files:"
                for zt in ups:
                    txt += "\n%s" % (", ".join((str(x) for x in zt)),)
                txt += "\n"

            if dls:
                txt += "\n\nactive downloads:"
                for zt in dls:
                    txt += "\n%s" % (", ".join((str(x) for x in zt)),)
                txt += "\n"

            if rvol:
                txt += "\nyou can browse:"
                for v in rvol:
                    txt += "\n  " + v

            if wvol:
                txt += "\nyou can upload to:"
                for v in wvol:
                    txt += "\n  " + v

            zb = txt.encode("utf-8", "replace") + b"\n"
            self.reply(zb, mime="text/plain; charset=utf-8")
            return True

        re_btn = ""
        nre = self.args.ctl_re
        if "re" in self.uparam:
            self.out_headers["Refresh"] = str(nre)
        elif nre:
            re_btn = "&re=%s" % (nre,)

        zi = self.args.ver_iwho
        show_ver = zi and (
            zi == 9 or (zi == 6 and self.uname != "*") or (zi == 3 and avol)
        )

        html = self.j2s(
            "splash",
            this=self,
            qvpath=quotep(self.vpaths) + self.ourlq(),
            rvol=rvol,
            wvol=wvol,
            avol=avol,
            in_shr=self.args.shr and self.vpath.startswith(self.args.shr1),
            vstate=vstate,
            dls=dls,
            ups=ups,
            scanning=vs["scanning"],
            hashq=vs["hashq"],
            tagq=vs["tagq"],
            mtpq=vs["mtpq"],
            dbwt=vs["dbwt"],
            url_suf=suf,
            re=re_btn,
            k304=self.k304(),
            no304=self.no304(),
            k304vis=self.args.k304 > 0,
            no304vis=self.args.no304 > 0,
            ver=S_VERSION if show_ver else "",
            chpw=self.args.chpw and self.uname != "*",
            ahttps="" if self.is_https else "https://" + self.host + self.req,
        )
        self.reply(html.encode("utf-8"))
        return True

    def setck(self)  :
        k, v = self.uparam["setck"].split("=", 1)
        t = 0 if v in ("", "x") else 86400 * 299
        ck = gencookie(k, v, self.args.R, self.args.cookie_lax, False, t)
        self.out_headerlist.append(("Set-Cookie", ck))
        if "cc" in self.ouparam:
            self.redirect("", "?h#cc")
        else:
            self.reply(b"o7\n")
        return True

    def set_cfg_reset(self)  :
        for k in ALL_COOKIES:
            if k not in self.cookies:
                continue
            cookie = gencookie(k, "x", self.args.R, self.args.cookie_lax, False)
            self.out_headerlist.append(("Set-Cookie", cookie))

        self.redirect("", "?h#cc")
        return True

    def tx_404(self, is_403  = False)  :
        rc = 404
        if self.args.vague_403:
            t = '<h1 id="n">404 not found &nbsp;┐( ´ -`)┌</h1><p id="o">or maybe you don\'t have access -- try a password or <a href="{}/?h">go home</a></p>'
            pt = "404 not found  ┐( ´ -`)┌   (or maybe you don't have access -- try a password)"
        elif is_403:
            t = '<h1 id="p">403 forbiddena &nbsp;~┻━┻</h1><p id="q">use a password or <a href="{}/?h">go home</a></p>'
            pt = "403 forbiddena ~┻━┻   (you'll have to log in)"
            rc = 403
        else:
            t = '<h1 id="n">404 not found &nbsp;┐( ´ -`)┌</h1><p><a id="r" href="{}/?h">go home</a></p>'
            pt = "404 not found  ┐( ´ -`)┌"

        if self.ua.startswith(("curl/", "fetch")):
            pt = "# acct: %s\n%s\n" % (self.uname, pt)
            self.reply(pt.encode("utf-8"), status=rc)
            return True

        if "th" in self.ouparam and str(self.ouparam["th"])[:1] in "jw":
            return self.tx_svg("e" + pt[:3])

        # most webdav clients will not send credentials until they
        # get 401'd, so send a challenge if we're Absolutely Sure
        # that the client is not a graphical browser
        if (
            rc == 403
            and self.uname == "*"
            and "sec-fetch-site" not in self.headers
            and (
                not self.ua.startswith("Mozilla/")
                or (self.args.dav_ua1 and self.args.dav_ua1.search(self.ua))
            )
        ):
            rc = 401
            self.out_headers["WWW-Authenticate"] = 'Basic realm="a"'

        t = t.format(self.args.SR)
        qv = quotep(self.vpaths) + self.ourlq()
        html = self.j2s(
            "splash",
            this=self,
            qvpath=qv,
            msg=t,
            in_shr=self.args.shr and self.vpath.startswith(self.args.shr1),
            ahttps="" if self.is_https else "https://" + self.host + self.req,
        )
        self.reply(html.encode("utf-8"), status=rc)
        return True

    def on40x(self, mods , vn , rem )  :
        for mpath in mods:
            try:
                mod = loadpy(mpath, self.args.hot_handlers)
            except Exception as ex:
                self.log("import failed: {!r}".format(ex))
                continue

            ret = mod.main(self, vn, rem)
            if ret:
                return ret.lower()

        return ""  # unhandled / fallthrough

    def scanvol(self)  :
        if self.args.no_rescan:
            raise Pebkac(403, "the rescan feature is disabled in server config")

        vpaths = self.uparam["scan"].split(",/")
        if vpaths == [""]:
            vpaths = [self.vpath]

        vols = []
        for vpath in vpaths:
            vn, _ = self.asrv.vfs.get(vpath, self.uname, True, True)
            vols.append(vn.vpath)
            if self.uname not in vn.axs.uadmin:
                self.log("rejected scanning [%s] => [%s];" % (vpath, vn.vpath), 3)
                raise Pebkac(403, "'scanvol' not allowed for user " + self.uname)

        self.log("trying to rescan %d volumes: %r" % (len(vols), vols))

        args = [self.asrv.vfs.all_vols, vols, False, True]

        x = self.conn.hsrv.broker.ask("up2k.rescan", *args)
        err = x.get()
        if not err:
            self.redirect("", "?h")
            return True

        raise Pebkac(500, err)

    def handle_reload(self)  :
        act = self.uparam.get("reload")
        if act != "cfg":
            raise Pebkac(400, "only config files ('cfg') can be reloaded rn")

        if not self.avol:
            raise Pebkac(403, "'reload' not allowed for user " + self.uname)

        if self.args.no_reload:
            raise Pebkac(403, "the reload feature is disabled in server config")

        x = self.conn.hsrv.broker.ask("reload", True, True)
        return self.redirect("", "?h", x.get(), "return to", False)

    def tx_stack(self)  :
        zs = self.args.stack_who
        if zs == "all" or (
            (zs == "a" and self.avol)
            or (zs == "rw" and [x for x in self.wvol if x in self.rvol])
        ):
            pass
        else:
            raise Pebkac(403, "'stack' not allowed for user " + self.uname)

        ret = html_escape(alltrace(self.args.stack_v))
        if self.args.stack_v:
            ret = "<pre>%s\n%s" % (time.time(), ret)
        else:
            ret = "<pre>%s" % (ret,)
        self.reply(ret.encode("utf-8"))
        return True

    def tx_tree(self)  :
        top = self.uparam["tree"] or ""
        dst = self.vpath
        if top in [".", ".."]:
            top = undot(self.vpath + "/" + top)

        if top == dst:
            dst = ""
        elif top:
            if not dst.startswith(top + "/"):
                raise Pebkac(422, "arg funk")

            dst = dst[len(top) + 1 :]

        ret = self.gen_tree(top, dst, self.uparam.get("k", ""))
        if self.is_vproxied and not self.uparam["tree"]:
            # uparam is '' on initial load, which is
            # the only time we gotta fill in the blanks
            parents = self.args.R.split("/")
            for parent in reversed(parents):
                ret = {"k%s" % (parent,): ret, "a": []}

        zs = json.dumps(ret)
        self.reply(zs.encode("utf-8"), mime="application/json")
        return True

    def gen_tree(self, top , target , dk )   :
        ret   = {}
        excl = None
        if target:
            excl, target = (target.split("/", 1) + [""])[:2]
            sub = self.gen_tree("/".join([top, excl]).strip("/"), target, dk)
            ret["k" + quotep(excl)] = sub

        vfs = self.asrv.vfs
        dk_sz = False
        if dk:
            vn, rem = vfs.get(top, self.uname, False, False)
            if vn.flags.get("dks") and self._use_dirkey(vn, vn.canonical(rem)):
                dk_sz = vn.flags.get("dk")

        dots = False
        fsroot = ""
        try:
            vn, rem = vfs.get(top, self.uname, not dk_sz, False)
            fsroot, vfs_ls, vfs_virt = vn.ls(
                rem,
                self.uname,
                not self.args.no_scandir,
                [[True, False], [False, True]],
            )
            dots = self.uname in vn.axs.udot
            dk_sz = vn.flags.get("dk")
        except:
            dk_sz = None
            vfs_ls = []
            vfs_virt = {}
            for v in self.rvol:
                d1, d2 = v.rsplit("/", 1) if "/" in v else ["", v]
                if d1 == top:
                    vfs_virt[d2] = vfs  # typechk, value never read

        dirs = [x[0] for x in vfs_ls if stat.S_ISDIR(x[1].st_mode)]

        if not dots or "dots" not in self.uparam:
            dirs = exclude_dotfiles(dirs)

        dirs = [quotep(x) for x in dirs if x != excl]

        if dk_sz and fsroot:
            kdirs = []
            fsroot_ = os.path.join(fsroot, "")
            for dn in dirs:
                ap = fsroot_ + dn
                zs = self.gen_fk(2, self.args.dk_salt, ap, 0, 0)[:dk_sz]
                kdirs.append(dn + "?k=" + zs)
            dirs = kdirs

        for x in vfs_virt:
            if x != excl:
                try:
                    dvn, drem = vfs.get(vjoin(top, x), self.uname, True, False)
                    bos.stat(dvn.canonical(drem, False))
                except:
                    x += "\n"
                dirs.append(x)

        ret["a"] = dirs
        return ret

    def get_dls(self)  :
        ret = []
        dls = self.conn.hsrv.tdls
        enshare = self.args.shr
        shrs = enshare[1:]
        for dl_id, (t0, sz, vn, vp, uname) in self.conn.hsrv.tdli.items():
            t1, sent = dls[dl_id]
            if sent > 0x100000:  # 1m; buffers 2~4
                sent -= 0x100000
            if self.uname not in vn.axs.uread:
                vp = ""
            elif self.uname not in vn.axs.udot and (vp.startswith(".") or "/." in vp):
                vp = ""
            elif (
                enshare
                and vp.startswith(shrs)
                and self.uname != vn.shr_owner
                and self.uname not in vn.axs.uadmin
                and self.uname not in self.args.shr_adm
                and not dl_id.startswith(self.ip + ":")
            ):
                vp = ""
            if self.uname not in vn.axs.uadmin:
                dl_id = uname = ""

            ret.append([t0, t1, sent, sz, vp, dl_id, uname])
        return ret

    def tx_dls(self)  :
        ret = [
            {
                "t0": x[0],
                "t1": x[1],
                "sent": x[2],
                "size": x[3],
                "path": x[4],
                "conn": x[5],
                "uname": x[6],
            }
            for x in self.get_dls()
        ]
        zs = json.dumps(ret, separators=(",\n", ": "))
        self.reply(zs.encode("utf-8", "replace"), mime="application/json")
        return True

    def tx_ups(self)  :
        idx = self.conn.get_u2idx()
        if not idx or not hasattr(idx, "p_end"):
            if not HAVE_SQLITE3:
                raise Pebkac(500, "sqlite3 not found on server; unpost is disabled")
            raise Pebkac(500, "server busy, cannot unpost; please retry in a bit")

        sfilt = self.uparam.get("filter") or ""
        nfi, vfi = str_anchor(sfilt)
        lm = "ups %d%r" % (nfi, sfilt)

        if self.args.shr and self.vpath.startswith(self.args.shr1):
            shr_dbv, shr_vrem = self.vn.get_dbv(self.rem)
        else:
            shr_dbv = None

        wret   = {}
        ret   = []
        t0 = time.time()
        lim = time.time() - self.args.unpost
        fk_vols = {
            vol: (vol.flags["fk"], 2 if "fka" in vol.flags else 1)
            for vp, vol in self.asrv.vfs.all_vols.items()
            if "fk" in vol.flags
            and (self.uname in vol.axs.uread or self.uname in vol.axs.upget)
        }

        bad_xff = hasattr(self, "bad_xff")
        if bad_xff:
            allvols = []
            t = "will not return list of recent uploads" + BADXFF
            self.log(t, 1)
            if self.avol:
                raise Pebkac(500, t)

        x = self.conn.hsrv.broker.ask(
            "up2k.get_unfinished_by_user", self.uname, "" if bad_xff else self.ip
        )
        zdsa   = x.get()
        uret   = []
        if "timeout" in zdsa:
            wret["nou"] = 1
        else:
            uret = zdsa["f"]
        nu = len(uret)

        if not self.args.unpost:
            allvols = []
        else:
            allvols = list(self.asrv.vfs.all_vols.values())

        allvols = [
            x
            for x in allvols
            if "e2d" in x.flags
            and ("*" in x.axs.uwrite or self.uname in x.axs.uwrite or x == shr_dbv)
        ]

        q = ""
        qp = (0,)
        q_c = -1

        for vol in allvols:
            cur = idx.get_cur(vol)
            if not cur:
                continue

            nfk, fk_alg = fk_vols.get(vol) or (0, 0)

            zi = vol.flags["unp_who"]
            if q_c != zi:
                q_c = zi
                q = "select sz, rd, fn, at from up where "
                if zi == 1:
                    q += "ip=? and un=?"
                    qp = (self.ip, self.uname, lim)
                elif zi == 2:
                    q += "ip=?"
                    qp = (self.ip, lim)
                if zi == 3:
                    q += "un=?"
                    qp = (self.uname, lim)
                q += " and at>? order by at desc"

            n = 2000
            for sz, rd, fn, at in cur.execute(q, qp):
                vp = "/" + "/".join(x for x in [vol.vpath, rd, fn] if x)
                if nfi == 0 or (nfi == 1 and vfi in vp.lower()):
                    pass
                elif nfi == 2:
                    if not vp.lower().startswith(vfi):
                        continue
                elif nfi == 3:
                    if not vp.lower().endswith(vfi):
                        continue
                else:
                    continue

                n -= 1
                if not n:
                    break

                rv = {"vp": vp, "sz": sz, "at": at, "nfk": nfk}
                if nfk:
                    rv["ap"] = vol.canonical(vjoin(rd, fn))
                    rv["fk_alg"] = fk_alg

                ret.append(rv)
                if len(ret) > 3000:
                    ret.sort(key=lambda x: x["at"], reverse=True)  # type: ignore
                    ret = ret[:2000]

        ret.sort(key=lambda x: x["at"], reverse=True)  # type: ignore

        if len(ret) > 2000:
            ret = ret[:2000]
        if len(ret) >= 2000:
            wret["oc"] = 1

        for rv in ret:
            rv["vp"] = quotep(rv["vp"])
            nfk = rv.pop("nfk")
            if not nfk:
                continue

            alg = rv.pop("fk_alg")
            ap = rv.pop("ap")
            try:
                st = bos.stat(ap)
            except:
                continue

            fk = self.gen_fk(
                alg, self.args.fk_salt, ap, st.st_size, 0 if ANYWIN else st.st_ino
            )
            rv["vp"] += "?k=" + fk[:nfk]

        if not allvols:
            wret["noc"] = 1
            ret = []

        nc = len(ret)
        ret = uret + ret

        if shr_dbv:
            # translate vpaths from share-target to share-url
            # to satisfy access checks
            vp_shr, vp_vfs = vroots(self.vpath, vjoin(shr_dbv.vpath, shr_vrem))
            for v in ret:
                vp = v["vp"]
                if vp.startswith(vp_vfs):
                    v["vp"] = vp_shr + vp[len(vp_vfs) :]

        if self.is_vproxied:
            for v in ret:
                v["vp"] = self.args.SR + v["vp"]

        wret["f"] = ret
        wret["nu"] = nu
        wret["nc"] = nc
        jtxt = json.dumps(wret, separators=(",\n", ": "))
        self.log("%s #%d+%d %.2fsec" % (lm, nu, nc, time.time() - t0))
        self.reply(jtxt.encode("utf-8", "replace"), mime="application/json")
        return True

    def tx_rups(self)  :
        if self.args.no_ups_page:
            raise Pebkac(500, "listing of recent uploads is disabled in server config")

        idx = self.conn.get_u2idx()
        if not idx or not hasattr(idx, "p_end"):
            if not HAVE_SQLITE3:
                raise Pebkac(500, "sqlite3 not found on server; recent-uploads n/a")
            raise Pebkac(500, "server busy, cannot list recent uploads; please retry")

        sfilt = self.uparam.get("filter") or ""
        nfi, vfi = str_anchor(sfilt)
        lm = "ru %d%r" % (nfi, sfilt)
        self.log(lm)

        ret   = []
        t0 = time.time()
        allvols = [
            x
            for x in self.asrv.vfs.all_vols.values()
            if "e2d" in x.flags and ("*" in x.axs.uread or self.uname in x.axs.uread)
        ]
        fk_vols = {
            vol: (vol.flags["fk"], 2 if "fka" in vol.flags else 1)
            for vol in allvols
            if "fk" in vol.flags and "*" not in vol.axs.uread
        }

        for vol in allvols:
            cur = idx.get_cur(vol)
            if not cur:
                continue

            nfk, fk_alg = fk_vols.get(vol) or (0, 0)
            adm = "*" in vol.axs.uadmin or self.uname in vol.axs.uadmin
            dots = "*" in vol.axs.udot or self.uname in vol.axs.udot

            lvl = vol.flags["ups_who"]
            if not lvl:
                continue
            elif lvl == 1 and not adm:
                continue

            n = 1000
            q = "select sz, rd, fn, ip, at, un from up where at>0 order by at desc"
            for sz, rd, fn, ip, at, un in cur.execute(q):
                vp = "/" + "/".join(x for x in [vol.vpath, rd, fn] if x)
                if nfi == 0 or (nfi == 1 and vfi in vp.lower()):
                    pass
                elif nfi == 2:
                    if not vp.lower().startswith(vfi):
                        continue
                elif nfi == 3:
                    if not vp.lower().endswith(vfi):
                        continue
                else:
                    continue

                if not dots and "/." in vp:
                    continue

                rv = {
                    "vp": vp,
                    "sz": sz,
                    "ip": ip,
                    "at": at,
                    "un": un,
                    "nfk": nfk,
                    "adm": adm,
                }
                if nfk:
                    rv["ap"] = vol.canonical(vjoin(rd, fn))
                    rv["fk_alg"] = fk_alg

                ret.append(rv)
                if len(ret) > 2000:
                    ret.sort(key=lambda x: x["at"], reverse=True)  # type: ignore
                    ret = ret[:1000]

                n -= 1
                if not n:
                    break

        ret.sort(key=lambda x: x["at"], reverse=True)  # type: ignore

        if len(ret) > 1000:
            ret = ret[:1000]

        for rv in ret:
            rv["vp"] = quotep(rv["vp"])
            nfk = rv.pop("nfk")
            if not nfk:
                continue

            alg = rv.pop("fk_alg")
            ap = rv.pop("ap")
            try:
                st = bos.stat(ap)
            except:
                continue

            fk = self.gen_fk(
                alg, self.args.fk_salt, ap, st.st_size, 0 if ANYWIN else st.st_ino
            )
            rv["vp"] += "?k=" + fk[:nfk]

        if self.args.ups_when:
            for rv in ret:
                adm = rv.pop("adm")
                if not adm:
                    rv["ip"] = "(You)" if rv["ip"] == self.ip else "(?)"
                    if rv["un"] not in ("*", self.uname):
                        rv["un"] = "(?)"
        else:
            for rv in ret:
                adm = rv.pop("adm")
                if not adm:
                    rv["ip"] = "(You)" if rv["ip"] == self.ip else "(?)"
                    rv["at"] = 0
                    if rv["un"] not in ("*", self.uname):
                        rv["un"] = "(?)"

        if self.is_vproxied:
            for v in ret:
                v["vp"] = self.args.SR + v["vp"]

        now = time.time()
        self.log("%s #%d %.2fsec" % (lm, len(ret), now - t0))

        ret2 = {"now": int(now), "filter": sfilt, "ups": ret}
        jtxt = json.dumps(ret2, separators=(",\n", ": "))
        if "j" in self.ouparam:
            self.reply(jtxt.encode("utf-8", "replace"), mime="application/json")
            return True

        html = self.j2s("rups", this=self, v=json_hesc(jtxt))
        self.reply(html.encode("utf-8"), status=200)
        return True

    def tx_idp(self)  :
        if self.uname.lower() not in self.args.idp_adm_set:
            raise Pebkac(403, "'idp' not allowed for user " + self.uname)

        cmd = self.uparam["idp"]
        if cmd.startswith("rm="):
            import sqlite3

            db = sqlite3.connect(self.args.idp_db)
            db.execute("delete from us where un=?", (cmd[3:],))
            db.commit()
            db.close()

            self.conn.hsrv.broker.ask("reload", False, True).get()

            self.redirect("", "?idp")
            return True

        rows = [
            [k, "[%s]" % ("], [".join(v))]
            for k, v in sorted(self.asrv.idp_accs.items())
        ]
        html = self.j2s("idp", this=self, rows=rows, now=int(time.time()))
        self.reply(html.encode("utf-8"), status=200)
        return True

    def tx_shares(self)  :
        if self.uname == "*":
            self.loud_reply("you're not logged in")
            return True

        idx = self.conn.get_u2idx()
        if not idx or not hasattr(idx, "p_end"):
            if not HAVE_SQLITE3:
                raise Pebkac(500, "sqlite3 not found on server; sharing is disabled")
            raise Pebkac(500, "server busy, cannot list shares; please retry in a bit")

        cur = idx.get_shr()
        if not cur:
            raise Pebkac(400, "huh, sharing must be disabled in the server config...")

        rows = cur.execute("select * from sh").fetchall()
        rows = [list(x) for x in rows]

        if self.uname != self.args.shr_adm:
            rows = [x for x in rows if x[5] == self.uname]

        html = self.j2s(
            "shares", this=self, shr=self.args.shr, rows=rows, now=int(time.time())
        )
        self.reply(html.encode("utf-8"), status=200)
        return True

    def handle_eshare(self)  :
        idx = self.conn.get_u2idx()
        if not idx or not hasattr(idx, "p_end"):
            if not HAVE_SQLITE3:
                raise Pebkac(500, "sqlite3 not found on server; sharing is disabled")
            raise Pebkac(500, "server busy, cannot create share; please retry in a bit")

        skey = self.uparam.get("skey") or self.vpath.split("/")[-1]

        if self.args.shr_v:
            self.log("handle_eshare: " + skey)

        cur = idx.get_shr()
        if not cur:
            raise Pebkac(400, "huh, sharing must be disabled in the server config...")

        rows = cur.execute("select un, t1 from sh where k = ?", (skey,)).fetchall()
        un = rows[0][0] if rows and rows[0] else ""

        if not un:
            raise Pebkac(400, "that sharekey didn't match anything")

        expiry = rows[0][1]

        if un != self.uname and self.uname != self.args.shr_adm:
            t = "your username (%r) does not match the sharekey's owner (%r) and you're not admin"
            raise Pebkac(400, t % (self.uname, un))

        reload = False
        act = self.uparam["eshare"]
        if act == "rm":
            cur.execute("delete from sh where k = ?", (skey,))
            if skey in self.asrv.vfs.nodes[self.args.shr.strip("/")].nodes:
                reload = True
        else:
            now = time.time()
            if expiry < now:
                expiry = now
                reload = True
            expiry += int(act) * 60
            cur.execute("update sh set t1 = ? where k = ?", (expiry, skey))

        cur.connection.commit()
        if reload:
            self.conn.hsrv.broker.ask("reload", False, True).get()
            self.conn.hsrv.broker.ask("up2k.wake_rescanner").get()

        self.redirect("", "?shares")
        return True

    def handle_share(self, req  )  :
        idx = self.conn.get_u2idx()
        if not idx or not hasattr(idx, "p_end"):
            if not HAVE_SQLITE3:
                raise Pebkac(500, "sqlite3 not found on server; sharing is disabled")
            raise Pebkac(500, "server busy, cannot create share; please retry in a bit")

        if self.args.shr_v:
            self.log("handle_share: " + json.dumps(req, indent=4))

        skey = req["k"]
        vps = req["vp"]
        fns = []
        if len(vps) == 1:
            vp = vps[0]
            if not vp.endswith("/"):
                vp, zs = vp.rsplit("/", 1)
                fns = [zs]
        else:
            for zs in vps:
                if zs.endswith("/"):
                    t = "you cannot select more than one folder, or mix files and folders in one selection"
                    raise Pebkac(400, t)
            vp = vps[0].rsplit("/", 1)[0]
            for zs in vps:
                vp2, fn = zs.rsplit("/", 1)
                fns.append(fn)
                if vp != vp2:
                    t = "mismatching base paths in selection:\n  %r\n  %r"
                    raise Pebkac(400, t % (vp, vp2))

        vp = vp.strip("/")
        if self.is_vproxied and (vp == self.args.R or vp.startswith(self.args.RS)):
            vp = vp[len(self.args.RS) :]

        m = re.search(r"([^0-9a-zA-Z_-])", skey)
        if m:
            raise Pebkac(400, "sharekey has illegal character %r" % (m[1],))

        if vp.startswith(self.args.shr1):
            raise Pebkac(400, "yo dawg...")

        cur = idx.get_shr()
        if not cur:
            raise Pebkac(400, "huh, sharing must be disabled in the server config...")

        q = "select * from sh where k = ?"
        qr = cur.execute(q, (skey,)).fetchall()
        if qr and qr[0]:
            self.log("sharekey taken by %r" % (qr,))
            raise Pebkac(400, "sharekey %r is already in use" % (skey,))

        # ensure user has requested perms
        s_rd = "read" in req["perms"]
        s_wr = "write" in req["perms"]
        s_mv = "move" in req["perms"]
        s_del = "delete" in req["perms"]
        try:
            vfs, rem = self.asrv.vfs.get(vp, self.uname, s_rd, s_wr, s_mv, s_del)
        except:
            raise Pebkac(400, "you dont have all the perms you tried to grant")

        zs = vfs.flags["shr_who"]
        if zs == "auth" and self.uname != "*":
            pass
        elif zs == "a" and self.uname in vfs.axs.uadmin:
            pass
        else:
            raise Pebkac(400, "you dont have perms to create shares from this volume")

        ap, reals, _ = vfs.ls(
            rem, self.uname, not self.args.no_scandir, [[s_rd, s_wr, s_mv, s_del]]
        )
        rfns = set([x[0] for x in reals])
        for fn in fns:
            if fn not in rfns:
                raise Pebkac(400, "selected file not found on disk: %r" % (fn,))

        pw = req.get("pw") or ""
        pw = self.asrv.ah.hash(pw)
        now = int(time.time())
        sexp = req["exp"]
        exp = int(sexp) if sexp else 0
        exp = now + exp * 60 if exp else 0
        pr = "".join(zc for zc, zb in zip("rwmd", (s_rd, s_wr, s_mv, s_del)) if zb)

        q = "insert into sh values (?,?,?,?,?,?,?,?)"
        cur.execute(q, (skey, pw, vp, pr, len(fns), self.uname, now, exp))

        q = "insert into sf values (?,?)"
        for fn in fns:
            cur.execute(q, (skey, fn))

        cur.connection.commit()
        self.conn.hsrv.broker.ask("reload", False, True).get()
        self.conn.hsrv.broker.ask("up2k.wake_rescanner").get()

        fn = quotep(fns[0]) if len(fns) == 1 else ""

        surl = "created share: %s://%s%s%s%s/%s" % (
            "https" if self.is_https else "http",
            self.host,
            self.args.SR,
            self.args.shr,
            skey,
            fn,
        )
        self.loud_reply(surl, status=201)
        return True

    def handle_rm(self, req )  :
        if not req and not self.can_delete:
            if self.mode == "DELETE" and self.uname == "*":
                raise Pebkac(401, "authenticate")  # webdav
            raise Pebkac(403, "'delete' not allowed for user " + self.uname)

        if self.args.no_del:
            raise Pebkac(403, "the delete feature is disabled in server config")

        unpost = "unpost" in self.uparam
        if unpost and hasattr(self, "bad_xff"):
            self.log("unpost was denied" + BADXFF, 1)
            raise Pebkac(403, "the delete feature is disabled in server config")

        if not req:
            req = [self.vpath]
        elif self.is_vproxied:
            req = [x[len(self.args.SR) :] for x in req]

        nlim = int(self.uparam.get("lim") or 0)
        lim = [nlim, nlim] if nlim else []

        x = self.conn.hsrv.broker.ask(
            "up2k.handle_rm", self.uname, self.ip, req, lim, False, unpost
        )
        self.loud_reply(x.get())
        return True

    def handle_mv(self)  :
        # full path of new loc (incl filename)
        dst = self.uparam.get("move")

        if self.is_vproxied and dst and dst.startswith(self.args.SR):
            dst = dst[len(self.args.RS) :]

        if not dst:
            raise Pebkac(400, "need dst vpath")

        return self._mv(self.vpath, dst.lstrip("/"), False)

    def _mv(self, vsrc , vdst , overwrite )  :
        if self.args.no_mv:
            raise Pebkac(403, "the rename/move feature is disabled in server config")

        # `handle_cpmv` will catch 403 from these and raise 401
        svn, srem = self.asrv.vfs.get(vsrc, self.uname, True, False, True)
        dvn, drem = self.asrv.vfs.get(vdst, self.uname, False, True)

        if overwrite:
            dabs = dvn.canonical(drem)
            if bos.path.exists(dabs):
                self.log("overwriting %s" % (dabs,))
                self.asrv.vfs.get(vdst, self.uname, False, True, False, True)
                wunlink(self.log, dabs, dvn.flags)

        x = self.conn.hsrv.broker.ask(
            "up2k.handle_mv", self.ouparam.get("akey"), self.uname, self.ip, vsrc, vdst
        )
        self.loud_reply(x.get(), status=201)
        return True

    def handle_cp(self)  :
        # full path of new loc (incl filename)
        dst = self.uparam.get("copy")

        if self.is_vproxied and dst and dst.startswith(self.args.SR):
            dst = dst[len(self.args.RS) :]

        if not dst:
            raise Pebkac(400, "need dst vpath")

        return self._cp(self.vpath, dst.lstrip("/"), False)

    def _cp(self, vsrc , vdst , overwrite )  :
        if self.args.no_cp:
            raise Pebkac(403, "the copy feature is disabled in server config")

        svn, srem = self.asrv.vfs.get(vsrc, self.uname, True, False)
        dvn, drem = self.asrv.vfs.get(vdst, self.uname, False, True)

        if overwrite:
            dabs = dvn.canonical(drem)
            if bos.path.exists(dabs):
                self.log("overwriting %s" % (dabs,))
                self.asrv.vfs.get(vdst, self.uname, False, True, False, True)
                wunlink(self.log, dabs, dvn.flags)

        x = self.conn.hsrv.broker.ask(
            "up2k.handle_cp", self.ouparam.get("akey"), self.uname, self.ip, vsrc, vdst
        )
        self.loud_reply(x.get(), status=201)
        return True

    def handle_fs_abrt(self):
        if self.args.no_fs_abrt:
            t = "aborting an ongoing copy/move is disabled in server config"
            raise Pebkac(403, t)

        self.conn.hsrv.broker.say("up2k.handle_fs_abrt", self.uparam["fs_abrt"])
        self.loud_reply("aborting", status=200)
        return True

    def tx_ls_vols(self)  :
        e_d = {}
        eses = ["", ""]
        rvol = self.rvol
        wvol = self.wvol
        if self.args.have_unlistc:
            allvols = self.asrv.vfs.all_vols
            rvol = [x for x in rvol if "unlistcr" not in allvols[x[1:-1]].flags]
            wvol = [x for x in wvol if "unlistcw" not in allvols[x[1:-1]].flags]
        vols = list(set(rvol + wvol))
        if self.vpath:
            zs = "%s/" % (self.vpath,)
            vols = [x[len(zs) :] for x in vols if x.startswith(zs)]
        vols = [x.split("/", 1)[0] for x in vols if x]
        if not vols and self.vpath:
            return self.tx_404(True)
        dirs = [
            {
                "lead": "",
                "href": "%s/" % (x,),
                "ext": "---",
                "sz": 0,
                "ts": 0,
                "tags": e_d,
                "dt": 0,
                "name": 0,
            }
            for x in sorted(vols)
        ]
        ls = {
            "dirs": dirs,
            "files": [],
            "acct": self.uname,
            "perms": [],
            "taglist": [],
            "logues": eses,
            "readmes": eses,
            "srvinf": "" if self.args.nih else self.args.name,
        }
        return self.tx_ls(ls)

    def tx_ls(self, ls  )  :
        dirs = ls["dirs"]
        files = ls["files"]
        arg = self.uparam["ls"]
        if arg in ["v", "t", "txt"]:
            try:
                biggest = max(ls["files"] + ls["dirs"], key=itemgetter("sz"))["sz"]
            except:
                biggest = 0

            if arg == "v":
                fmt = "\033[0;7;36m{{}}{{:>{}}}\033[0m {{}}"
                nfmt = "{}"
                biggest = 0
                f2 = "".join(
                    "{}{{}}".format(x)
                    for x in [
                        "\033[7m",
                        "\033[27m",
                        "",
                        "\033[0;1m",
                        "\033[0;36m",
                        "\033[0m",
                    ]
                )
                ctab = {"B": 6, "K": 5, "M": 1, "G": 3}
                for lst in [dirs, files]:
                    for x in lst:
                        a = x["dt"].replace("-", " ").replace(":", " ").split(" ")
                        x["dt"] = f2.format(*list(a))
                        sz = humansize(x["sz"], True)
                        x["sz"] = "\033[0;3{}m {:>5}".format(ctab.get(sz[-1:], 0), sz)
            else:
                fmt = "{{}}  {{:{},}}  {{}}"
                nfmt = "{:,}"

            for x in dirs:
                n = x["name"] + "/"
                if arg == "v":
                    n = "\033[94m" + n

                x["name"] = n

            fmt = fmt.format(len(nfmt.format(biggest)))
            retl = [
                ("# %s: %s" % (x, ls[x])).replace(r"</span> // <span>", " // ")
                for x in ["acct", "perms", "srvinf"]
                if x in ls
            ]
            retl += [
                fmt.format(x["dt"], x["sz"], x["name"])
                for y in [dirs, files]
                for x in y
            ]
            ret = "\n".join(retl)
            mime = "text/plain; charset=utf-8"
        else:
            [x.pop(k) for k in ["name", "dt"] for y in [dirs, files] for x in y]

            # nonce (tlnote: norwegian for flake as in snowflake)
            if self.args.no_fnugg:
                ls["fnugg"] = "nei"
            elif "fnugg" in self.headers:
                ls["fnugg"] = self.headers["fnugg"]

            ret = json.dumps(ls)
            mime = "application/json"

        ret += "\n\033[0m" if arg == "v" else "\n"
        self.reply(ret.encode("utf-8", "replace"), mime=mime)
        return True

    def tx_browser(self)  :
        vpath = ""
        vpnodes = [["", "/"]]
        if self.vpath:
            for node in self.vpath.split("/"):
                if not vpath:
                    vpath = node
                else:
                    vpath += "/" + node

                vpnodes.append([quotep(vpath) + "/", html_escape(node, crlf=True)])

        vn = self.vn
        rem = self.rem
        abspath = vn.dcanonical(rem)
        dbv, vrem = vn.get_dbv(rem)

        try:
            st = bos.stat(abspath)
        except:
            if "on404" not in vn.flags:
                return self.tx_404(not self.can_read)

            ret = self.on40x(vn.flags["on404"], vn, rem)
            if ret == "true":
                return True
            elif ret == "false":
                return False
            elif ret == "retry":
                try:
                    st = bos.stat(abspath)
                except:
                    return self.tx_404(not self.can_read)
            else:
                return self.tx_404(not self.can_read)

        if rem.startswith(".hist/up2k.") or (
            rem.endswith("/dir.txt") and rem.startswith(".hist/th/")
        ):
            raise Pebkac(403)

        e2d = "e2d" in vn.flags
        e2t = "e2t" in vn.flags

        add_og = "og" in vn.flags
        if add_og:
            if "th" in self.uparam or "raw" in self.uparam or "opds" in self.uparam:
                add_og = False
            elif vn.flags["og_ua"]:
                add_og = vn.flags["og_ua"].search(self.ua)
            og_fn = ""

        if "v" in self.uparam:
            add_og = True
            og_fn = ""

        if "b" in self.uparam:
            self.out_headers["X-Robots-Tag"] = "noindex, nofollow"

        is_dir = stat.S_ISDIR(st.st_mode)
        is_dk = False
        fk_pass = False
        icur = None
        if (e2t or e2d) and (is_dir or add_og):
            idx = self.conn.get_u2idx()
            if idx and hasattr(idx, "p_end"):
                icur = idx.get_cur(dbv)

        if "k" in self.uparam or "dky" in vn.flags:
            if is_dir:
                use_dirkey = self._use_dirkey(vn, abspath)
                use_filekey = False
            else:
                use_filekey = self._use_filekey(vn, abspath, st)
                use_dirkey = False
        else:
            use_dirkey = use_filekey = False

        th_fmt = self.uparam.get("th")
        if self.can_read or (
            self.can_get
            and (use_filekey or use_dirkey or (not is_dir and "fk" not in vn.flags))
        ):
            if th_fmt is not None:
                nothumb = "dthumb" in dbv.flags
                if is_dir:
                    vrem = vrem.rstrip("/")
                    if nothumb:
                        pass
                    elif icur and vrem:
                        q = "select fn from cv where rd=? and dn=?"
                        crd, cdn = vrem.rsplit("/", 1) if "/" in vrem else ("", vrem)
                        # no mojibake support:
                        try:
                            cfn = icur.execute(q, (crd, cdn)).fetchone()
                            if cfn:
                                fn = cfn[0]
                                fp = os.path.join(abspath, fn)
                                st = bos.stat(fp)
                                vrem = "{}/{}".format(vrem, fn).strip("/")
                                is_dir = False
                        except:
                            pass
                    else:
                        for fn in self.args.th_covers:
                            fp = os.path.join(abspath, fn)
                            try:
                                st = bos.stat(fp)
                                vrem = "{}/{}".format(vrem, fn).strip("/")
                                is_dir = False
                                break
                            except:
                                pass

                    if is_dir:
                        return self.tx_svg("folder")

                thp = None
                if self.thumbcli and not nothumb:
                    try:
                        thp = self.thumbcli.get(dbv, vrem, int(st.st_mtime), th_fmt)
                    except Pebkac as ex:
                        if ex.code == 500 and th_fmt[:1] in "jw":
                            self.log("failed to convert [%s]:\n%s" % (abspath, ex), 3)
                            return self.tx_svg("--error--\ncheck\nserver\nlog")
                        raise

                if thp:
                    return self.tx_file(thp)

                if th_fmt == "p":
                    raise Pebkac(404)

                return self.tx_ico(rem)

        elif self.can_write and th_fmt is not None:
            return self.tx_svg("upload\nonly")

        if not self.can_read and self.can_get and self.avn:
            axs = self.avn.axs
            if self.uname not in axs.uhtml:
                pass
            elif is_dir:
                for fn in ("index.htm", "index.html"):
                    ap2 = os.path.join(abspath, fn)
                    try:
                        st2 = bos.stat(ap2)
                    except:
                        continue

                    # might as well be extra careful
                    if not stat.S_ISREG(st2.st_mode):
                        continue

                    if not self.trailing_slash:
                        return self.redirect(
                            self.vpath + "/", flavor="redirecting to", use302=True
                        )

                    fk_pass = True
                    is_dir = False
                    rem = vjoin(rem, fn)
                    vrem = vjoin(vrem, fn)
                    abspath = ap2
                    break
            elif self.vpath.rsplit("/", 1)[-1] in ("index.htm", "index.html"):
                fk_pass = True

        if not is_dir and (self.can_read or self.can_get):
            if not self.can_read and not fk_pass and "fk" in vn.flags:
                if not use_filekey:
                    return self.tx_404(True)

            is_md = abspath.lower().endswith(".md")
            if add_og and not is_md:
                if self.host not in self.headers.get("referer", ""):
                    self.vpath, og_fn = vsplit(self.vpath)
                    vpath = self.vpath
                    vn, rem = self.asrv.vfs.get(self.vpath, self.uname, False, False)
                    abspath = vn.dcanonical(rem)
                    dbv, vrem = vn.get_dbv(rem)
                    is_dir = stat.S_ISDIR(st.st_mode)
                    is_dk = True
                    vpnodes.pop()

            if (
                (is_md or self.can_delete)
                and "nohtml" not in vn.flags
                and (
                    (is_md and "v" in self.uparam)
                    or "edit" in self.uparam
                    or "edit2" in self.uparam
                )
            ):
                return self.tx_md(vn, abspath)

            if "zls" in self.uparam:
                return self.tx_zls(abspath)
            if "zget" in self.uparam:
                return self.tx_zget(abspath)

            if not add_og or not og_fn:
                if st.st_size or "nopipe" in vn.flags:
                    return self.tx_file(abspath, None)
                else:
                    return self.tx_file(abspath, vn.get_dbv("")[0].realpath)

        elif is_dir and not self.can_read:
            if use_dirkey:
                is_dk = True
            elif self.can_get and "doc" in self.uparam:
                zs = vjoin(self.vpath, self.uparam["doc"]) + "?v"
                return self.redirect(zs, flavor="redirecting to", use302=True)
            elif not self.can_write:
                return self.tx_404(True)

        srv_info = []

        try:
            if not self.args.nih:
                srv_info.append(self.args.name_html)
        except:
            self.log("#wow #whoa")

        zi = vn.flags["du_iwho"]
        if zi and (
            zi == 9
            or (zi == 7 and self.uname != "*")
            or (zi == 5 and self.can_write)
            or (zi == 4 and self.can_write and self.can_read)
            or (zi == 3 and self.can_admin)
        ):
            free, total, zs = get_df(abspath, False)
            if total:
                h1 = humansize(free or 0)
                h2 = humansize(total)
                srv_info.append("{} free of {}".format(h1, h2))
            elif zs:
                self.log("diskfree(%r): %s" % (abspath, zs), 3)

        srv_infot = "</span> // <span>".join(srv_info)

        perms = []
        if self.can_read or is_dk:
            perms.append("read")
        if self.can_write:
            perms.append("write")
        if self.can_move:
            perms.append("move")
        if self.can_delete:
            perms.append("delete")
        if self.can_get:
            perms.append("get")
        if self.can_upget:
            perms.append("upget")
        if self.can_admin:
            perms.append("admin")

        url_suf = self.urlq({}, ["k"])
        is_ls = "ls" in self.uparam
        is_opds = "opds" in self.uparam
        is_js = self.args.force_js or self.cookies.get("js") == "y"

        if not is_ls and not add_og and self.ua.startswith(("curl/", "fetch")):
            self.uparam["ls"] = "v"
            is_ls = True

        tpl = "browser"
        if "b" in self.uparam:
            tpl = "browser2"
            is_js = False
        elif is_opds:
            # Display directory listing as OPDS v1.2 catalog feed
            if not (self.args.opds or "opds" in self.vn.flags):
                raise Pebkac(405, "OPDS is disabled in server config")
            if not self.can_read:
                raise Pebkac(401, "OPDS requires read permission")
            is_js = is_ls = False

        vf = vn.flags
        ls_ret = {
            "dirs": [],
            "files": [],
            "taglist": [],
            "srvinf": srv_infot,
            "acct": self.uname,
            "perms": perms,
            "cfg": vn.js_ls,
        }
        cgv = {
            "ls0": None,
            "acct": self.uname,
            "perms": perms,
        }
        # also see `js_htm` in authsrv.py
        j2a = {
            "cgv1": vn.js_htm,
            "cgv": cgv,
            "vpnodes": vpnodes,
            "files": [],
            "ls0": None,
            "taglist": [],
            "have_tags_idx": int(e2t),
            "have_b_u": (self.can_write and self.uparam.get("b") == "u"),
            "sb_lg": vn.js_ls["sb_lg"],
            "url_suf": url_suf,
            "title": html_escape("%s %s" % (self.args.bname, self.vpath), crlf=True),
            "srv_info": srv_infot,
            "dtheme": self.args.theme,
        }

        if self.args.js_browser:
            zs = self.args.js_browser
            zs += "&" if "?" in zs else "?"
            j2a["js"] = zs

        if self.args.css_browser:
            zs = self.args.css_browser
            zs += "&" if "?" in zs else "?"
            j2a["css"] = zs

        if not self.conn.hsrv.prism:
            j2a["no_prism"] = True

        if not self.can_read and not is_dk:
            logues, readmes = self._add_logues(vn, abspath, None)
            ls_ret["logues"] = j2a["logues"] = logues
            ls_ret["readmes"] = cgv["readmes"] = readmes

            if is_ls:
                return self.tx_ls(ls_ret)

            if not stat.S_ISDIR(st.st_mode):
                return self.tx_404(True)

            if "zip" in self.uparam or "tar" in self.uparam:
                raise Pebkac(403)

            html = self.j2s(tpl, **j2a)
            self.reply(html.encode("utf-8", "replace"))
            return True

        for k in ["zip", "tar"]:
            v = self.uparam.get(k)
            if v is not None and (not add_og or not og_fn):
                if is_dk and "dks" not in vn.flags:
                    t = "server config does not allow download-as-zip/tar; only dk is specified, need dks too"
                    raise Pebkac(403, t)
                return self.tx_zip(k, v, self.vpath, vn, rem, [])

        fsroot, vfs_ls, vfs_virt = vn.ls(
            rem,
            self.uname,
            not self.args.no_scandir,
            [[True, False], [False, True]],
            lstat="lt" in self.uparam,
            throw=True,
        )
        stats = {k: v for k, v in vfs_ls}
        ls_names = [x[0] for x in vfs_ls]
        ls_names.extend(list(vfs_virt.keys()))

        if add_og and og_fn and not self.can_read:
            ls_names = [og_fn]
            is_js = True

        # check for old versions of files,
        # [num-backups, most-recent, hist-path]
        hist     = {}
        try:
            if vf["md_hist"] != "s":
                raise Exception()
            histdir = os.path.join(fsroot, ".hist")
            ptn = RE_MDV
            for hfn in bos.listdir(histdir):
                m = ptn.match(hfn)
                if not m:
                    continue

                fn = m.group(1) + m.group(3)
                n, ts, _ = hist.get(fn, (0, 0, ""))
                hist[fn] = (n + 1, max(ts, float(m.group(2))), hfn)
        except:
            pass

        lnames = {x.lower(): x for x in ls_names}

        # show dotfiles if permitted and requested
        if not self.can_dot or (
            "dots" not in self.uparam and (is_ls or "dots" not in self.cookies)
        ):
            ls_names = exclude_dotfiles(ls_names)

        add_dk = vf.get("dk")
        add_fk = vf.get("fk")
        fk_alg = 2 if "fka" in vf else 1
        if add_dk:
            if vf.get("dky"):
                add_dk = False
            else:
                zs = self.gen_fk(2, self.args.dk_salt, abspath, 0, 0)[:add_dk]
                ls_ret["dk"] = cgv["dk"] = zs

        no_zip = bool(self._can_zip(vf))

        dirs = []
        files = []
        ptn_hr = RE_HR
        use_abs_url = (
            not is_opds
            and not is_ls
            and not is_js
            and not self.trailing_slash
            and vpath
        )
        for fn in ls_names:
            base = ""
            href = fn
            if use_abs_url:
                base = "/" + vpath + "/"
                href = base + fn

            if fn in vfs_virt:
                fspath = vfs_virt[fn].realpath
            else:
                fspath = fsroot + "/" + fn

            try:
                linf = stats.get(fn) or bos.lstat(fspath)
                inf = bos.stat(fspath) if stat.S_ISLNK(linf.st_mode) else linf
            except:
                self.log("broken symlink: %r" % (fspath,))
                continue

            is_dir = stat.S_ISDIR(inf.st_mode)
            if is_dir:
                href += "/"
                if no_zip:
                    margin = "DIR"
                elif add_dk:
                    zs = absreal(fspath)
                    margin = '<a href="%s?k=%s&zip=crc" rel="nofollow">zip</a>' % (
                        quotep(href),
                        self.gen_fk(2, self.args.dk_salt, zs, 0, 0)[:add_dk],
                    )
                else:
                    margin = '<a href="%s?zip=crc" rel="nofollow">zip</a>' % (
                        quotep(href),
                    )
            elif fn in hist:
                margin = '<a href="%s.hist/%s" rel="nofollow">#%s</a>' % (
                    base,
                    html_escape(hist[fn][2], quot=True, crlf=True),
                    hist[fn][0],
                )
            else:
                margin = "-"

            sz = inf.st_size
            zd = datetime.fromtimestamp(max(0, linf.st_mtime), UTC)
            dt = "%04d-%02d-%02d %02d:%02d:%02d" % (
                zd.year,
                zd.month,
                zd.day,
                zd.hour,
                zd.minute,
                zd.second,
            )

            if is_dir:
                ext = "---"
            elif "." in fn:
                ext = ptn_hr.sub("@", fn.rsplit(".", 1)[1])
                if len(ext) > 16:
                    ext = ext[:16]
            else:
                ext = "%"

            if add_fk and not is_dir:
                href = "%s?k=%s" % (
                    quotep(href),
                    self.gen_fk(
                        fk_alg,
                        self.args.fk_salt,
                        fspath,
                        sz,
                        0 if ANYWIN else inf.st_ino,
                    )[:add_fk],
                )
            elif add_dk and is_dir:
                href = "%s?k=%s" % (
                    quotep(href),
                    self.gen_fk(2, self.args.dk_salt, fspath, 0, 0)[:add_dk],
                )
            else:
                href = quotep(href)

            item = {
                "lead": margin,
                "href": href,
                "name": fn,
                "sz": sz,
                "ext": ext,
                "dt": dt,
                "ts": int(linf.st_mtime),
            }
            if is_dir:
                dirs.append(item)
            else:
                files.append(item)

        if is_dk and not vf.get("dks"):
            dirs = []

        if (
            self.cookies.get("idxh") == "y"
            and "ls" not in self.uparam
            and "v" not in self.uparam
            and not is_opds
        ):
            idx_html = set(["index.htm", "index.html"])
            for item in files:
                if item["name"] in idx_html:
                    # do full resolve in case of shadowed file
                    vp = vjoin(self.vpath.split("?")[0], item["name"])
                    vn, rem = self.asrv.vfs.get(vp, self.uname, True, False)
                    ap = vn.canonical(rem)
                    return self.tx_file(ap)  # is no-cache

        if icur:
            mte = vn.flags.get("mte") or {}
            tagset  = set()
            rd = vrem
            if self.can_admin:
                up_q = "select substr(w,1,16), ip, at, un from up where rd=? and fn=?"
                up_m = ["w", "up_ip", ".up_at", "up_by"]
            elif ".up_at" in mte:
                if "w" in mte:
                    up_q = "select substr(w,1,16), at from up where rd=? and fn=?"
                    up_m = ["w", ".up_at"]
                else:
                    up_q = "select at from up where rd=? and fn=?"
                    up_m = [".up_at"]
            elif "w" in mte:
                up_q = "select substr(w,1,16) from up where rd=? and fn=?"
                up_m = ["w"]
            else:
                up_q = ""

            mt_q = "select mt.k, mt.v from up inner join mt on mt.w = substr(up.w,1,16) where up.rd = ? and up.fn = ? and +mt.k != 'x'"
            for fe in files:
                fn = fe["name"]
                erd_efn = (rd, fn)
                try:
                    r = icur.execute(mt_q, erd_efn)
                except Exception as ex:
                    if "database is locked" in str(ex):
                        break

                    try:
                        erd_efn = s3enc(idx.mem_cur, rd, fn)
                        r = icur.execute(mt_q, erd_efn)
                    except:
                        self.log("tag read error, %r / %r\n%s" % (rd, fn, min_ex()))
                        break

                tags = {k: v for k, v in r}

                if up_q:
                    try:
                        up_v = icur.execute(up_q, erd_efn).fetchone()
                        for zs1, zs2 in zip(up_m, up_v):
                            if zs2:
                                tags[zs1] = zs2
                    except:
                        pass

                _ = [tagset.add(k) for k in tags]
                fe["tags"] = tags

            for fe in dirs:
                fe["tags"] = ODict()

            lmte = list(mte)
            if self.can_admin:
                lmte.extend(("w", "up_by", "up_ip", ".up_at"))

            if "nodirsz" not in vf:
                tagset.add(".files")
                vdir = "%s/" % (rd,) if rd else ""
                q = "select sz, nf from ds where rd=? limit 1"
                for fe in dirs:
                    try:
                        hit = icur.execute(q, (vdir + fe["name"],)).fetchone()
                        (fe["sz"], fe["tags"][".files"]) = hit
                    except:
                        pass  # 404 or mojibake

            taglist = [k for k in lmte if k in tagset]
        else:
            taglist = []

        logues, readmes = self._add_logues(vn, abspath, lnames)
        ls_ret["logues"] = j2a["logues"] = logues
        ls_ret["readmes"] = cgv["readmes"] = readmes

        if (
            not files
            and not dirs
            and not readmes[0]
            and not readmes[1]
            and not logues[0]
            and not logues[1]
        ):
            logues[1] = "this folder is empty"

        if "descript.ion" in lnames and os.path.isfile(
            os.path.join(abspath, lnames["descript.ion"])
        ):
            rem = []
            with open(os.path.join(abspath, lnames["descript.ion"]), "rb") as f:
                for bln in [x.strip() for x in f]:
                    try:
                        if bln.endswith(b"\x04\xc2"):
                            # multiline comment; replace literal r"\n" with " // "
                            bln = bln.replace(br"\\n", b" // ")[:-2]
                        ln = bln.decode("utf-8", "replace")
                        if ln.startswith('"'):
                            fn, desc = ln.split('" ', 1)
                            fn = fn[1:]
                        else:
                            fn, desc = ln.split(" ", 1)
                        fe = next(
                            (x for x in files if x["name"].lower() == fn.lower()), None
                        )
                        if fe:
                            fe["tags"]["descript.ion"] = desc
                        else:
                            t = "<li><code>%s</code> %s</li>"
                            rem.append(t % (html_escape(fn), html_escape(desc)))
                    except:
                        pass
            if "descript.ion" not in taglist:
                taglist.insert(0, "descript.ion")
            if rem and not logues[1]:
                t = "<h3>descript.ion</h3><ul>\n"
                logues[1] = t + "\n".join(rem) + "</ul>"

        if is_ls:
            ls_ret["dirs"] = dirs
            ls_ret["files"] = files
            ls_ret["taglist"] = taglist
            return self.tx_ls(ls_ret)

        doc = self.uparam.get("doc") if self.can_read else None
        if doc:
            zp = self.args.ua_nodoc
            if zp and zp.search(self.ua):
                t = "this URL contains no valuable information for bots/crawlers"
                raise Pebkac(403, t)
            j2a["docname"] = doc
            doctxt = None
            dfn = lnames.get(doc.lower())
            if dfn and dfn != doc:
                # found Foo but want FOO
                dfn = next((x for x in files if x["name"] == doc), None)
            if dfn:
                docpath = os.path.join(abspath, doc)
                sz = bos.path.getsize(docpath)
                if sz < 1024 * self.args.txt_max:
                    doctxt = read_utf8(self.log, fsenc(docpath), False)
                    if doc.lower().endswith(".md") and "exp" in vn.flags:
                        doctxt = self._expand(doctxt, vn.flags.get("exp_md") or [])
                else:
                    self.log("doc 2big: %r" % (doc,), 6)
                    doctxt = "( size of textfile exceeds serverside limit )"
            else:
                self.log("doc 404: %r" % (doc,), 6)
                doctxt = "( textfile not found )"

            if doctxt is not None:
                j2a["doc"] = doctxt

        for d in dirs:
            d["name"] += "/"

        dirs.sort(key=itemgetter("name"))

        if is_opds:
            # exclude files which don't match --opds-exts
            allowed_exts = vf.get("opds_exts") or self.args.opds_exts
            if allowed_exts:
                files = [
                    x for x in files if x["name"].rsplit(".", 1)[-1] in allowed_exts
                ]
            for item in dirs:
                href = item["href"]
                href += ("&" if "?" in href else "?") + "opds"
                item["href"] = href
                item["iso8601"] = "%sZ" % (item["dt"].replace(" ", "T"),)

            for item in files:
                href = item["href"]
                href += ("&" if "?" in href else "?") + "dl"
                item["href"] = href
                item["iso8601"] = "%sZ" % (item["dt"].replace(" ", "T"),)

                if "rmagic" in self.vn.flags:
                    ap = "%s/%s" % (fsroot, item["name"])
                    item["mime"] = guess_mime(item["name"], ap)
                else:
                    item["mime"] = guess_mime(item["name"])

                # Make sure we can actually generate JPEG thumbnails
                if (
                    not self.args.th_no_jpg
                    and self.thumbcli
                    and "dthumb" not in dbv.flags
                    and "dithumb" not in dbv.flags
                ):
                    item["jpeg_thumb_href"] = href + "&th=jf"
                    item["jpeg_thumb_href_hires"] = item["jpeg_thumb_href"] + "3"

            j2a["files"] = files
            j2a["dirs"] = dirs
            html = self.j2s("opds", **j2a)
            mime = "application/atom+xml;profile=opds-catalog"
            self.reply(html.encode("utf-8", "replace"), mime=mime)
            return True

        if is_js:
            j2a["ls0"] = cgv["ls0"] = {
                "dirs": dirs,
                "files": files,
                "taglist": taglist,
            }
            j2a["files"] = []
        else:
            j2a["files"] = dirs + files

        j2a["taglist"] = taglist

        if add_og and "raw" not in self.uparam:
            j2a["this"] = self
            cgv["og_fn"] = og_fn
            if og_fn and vn.flags.get("og_tpl"):
                tpl = vn.flags["og_tpl"]
                if "EXT" in tpl:
                    zs = og_fn.split(".")[-1].lower()
                    tpl2 = tpl.replace("EXT", zs)
                    if os.path.exists(tpl2):
                        tpl = tpl2
                with self.conn.hsrv.mutex:
                    if tpl not in self.conn.hsrv.j2:
                        tdir, tname = os.path.split(tpl)
                        j2env = jinja2.Environment()
                        j2env.loader = jinja2.FileSystemLoader(tdir)
                        self.conn.hsrv.j2[tpl] = j2env.get_template(tname)
            thumb = ""
            is_pic = is_vid = is_au = False
            for fn in self.args.th_coversd:
                if fn in lnames:
                    thumb = lnames[fn]
                    break
            if og_fn:
                ext = og_fn.split(".")[-1].lower()
                if self.thumbcli and ext in self.thumbcli.thumbable:
                    is_pic = (
                        ext in self.thumbcli.fmt_pil
                        or ext in self.thumbcli.fmt_vips
                        or ext in self.thumbcli.fmt_ffi
                    )
                    is_vid = ext in self.thumbcli.fmt_ffv
                    is_au = ext in self.thumbcli.fmt_ffa
                    if not thumb or not is_au:
                        thumb = og_fn
                file = next((x for x in files if x["name"] == og_fn), None)
            else:
                file = None

            url_base = "%s://%s/%s" % (
                "https" if self.is_https else "http",
                self.host,
                self.args.RS + quotep(vpath),
            )
            j2a["og_is_pic"] = is_pic
            j2a["og_is_vid"] = is_vid
            j2a["og_is_au"] = is_au
            if thumb:
                fmt = vn.flags.get("og_th", "j")
                th_base = ujoin(url_base, quotep(thumb))
                query = "th=%s&cache" % (fmt,)
                if use_filekey:
                    query += "&k=" + self.uparam["k"]
                query = ub64enc(query.encode("utf-8")).decode("ascii")
                # discord looks at file extension, not content-type...
                query += "/th.jpg" if "j" in fmt else "/th.webp"
                j2a["og_thumb"] = "%s/.uqe/%s" % (th_base, query)

            j2a["og_fn"] = og_fn
            j2a["og_file"] = file
            if og_fn:
                og_fn_q = quotep(og_fn)
                query = "raw"
                if use_filekey:
                    query += "&k=" + self.uparam["k"]
                query = ub64enc(query.encode("utf-8")).decode("ascii")
                query += "/%s" % (og_fn_q,)
                j2a["og_url"] = ujoin(url_base, og_fn_q)
                j2a["og_raw"] = j2a["og_url"] + "/.uqe/" + query
            else:
                j2a["og_url"] = j2a["og_raw"] = url_base

            if not vn.flags.get("og_no_head"):
                ogh = {"twitter:card": "summary"}

                title = str(vn.flags.get("og_title") or "")

                if thumb:
                    ogh["og:image"] = j2a["og_thumb"]

                zso = vn.flags.get("og_desc") or ""
                if zso != "-":
                    ogh["og:description"] = str(zso)

                zs = vn.flags.get("og_site") or self.args.name
                if zs not in ("", "-"):
                    ogh["og:site_name"] = zs

                try:
                    zs1, zs2 = file["tags"]["res"].split("x")
                    file["tags"][".resw"] = zs1
                    file["tags"][".resh"] = zs2
                except:
                    pass

                tagmap = {}

                if is_au:
                    title = str(vn.flags.get("og_title_a") or "")
                    ogh["og:type"] = "music.song"
                    ogh["og:audio"] = j2a["og_raw"]
                    tagmap = {
                        "artist": "og:music:musician",
                        "album": "og:music:album",
                        ".dur": "og:music:duration",
                    }
                elif is_vid:
                    title = str(vn.flags.get("og_title_v") or "")
                    ogh["og:type"] = "video.other"
                    ogh["og:video"] = j2a["og_raw"]

                    tagmap = {
                        "title": "og:title",
                        ".dur": "og:video:duration",
                        ".resw": "og:video:width",
                        ".resh": "og:video:height",
                    }
                elif is_pic:
                    title = str(vn.flags.get("og_title_i") or "")
                    ogh["twitter:card"] = "summary_large_image"
                    ogh["twitter:image"] = ogh["og:image"] = j2a["og_raw"]

                    tagmap = {
                        ".resw": "og:image:width",
                        ".resh": "og:image:height",
                    }

                try:
                    for k, v in file["tags"].items():
                        zs = "{{ %s }}" % (k,)
                        title = title.replace(zs, str(v))
                except:
                    pass
                title = re.sub(r"\{\{ [^}]+ \}\}", "", title)
                while title.startswith(" - "):
                    title = title[3:]
                while title.endswith(" - "):
                    title = title[:3]

                if vn.flags.get("og_s_title") or not title:
                    title = str(vn.flags.get("og_title") or "")

                for tag, hname in tagmap.items():
                    try:
                        v = file["tags"][tag]
                        if not v:
                            continue
                        ogh[hname] = int(v) if tag == ".dur" else v
                    except:
                        pass

                ogh["og:title"] = title

                oghs = [
                    '\t<meta property="%s" content="%s">'
                    % (k, html_escape(str(v), True, True))
                    for k, v in ogh.items()
                ]
                zs = self.html_head + "\n%s\n" % ("\n".join(oghs),)
                self.html_head = zs.replace("\n\n", "\n")

        html = self.j2s(tpl, **j2a)
        self.reply(html.encode("utf-8", "replace"))
        return True
