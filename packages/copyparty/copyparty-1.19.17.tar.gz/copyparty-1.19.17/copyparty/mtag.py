# coding: utf-8
from __future__ import print_function, unicode_literals

import argparse
import json
import os
import re
import shutil
import subprocess as sp
import sys
import tempfile

from .__init__ import ANYWIN, EXE, PY2, WINDOWS, E, unicode
from .authsrv import VFS
from .bos import bos
from .util import (
    FFMPEG_URL,
    REKOBO_LKEY,
    VF_CAREFUL,
    fsenc,
    gzip,
    min_ex,
    pybin,
    retchk,
    runcmd,
    sfsenc,
    uncyg,
    wunlink,
)

try:
    if os.environ.get("PRTY_NO_MUTAGEN"):
        raise Exception()

    from mutagen import version  # noqa: F401

    HAVE_MUTAGEN = True
except:
    HAVE_MUTAGEN = False


def have_ff(scmd )  :
    if ANYWIN:
        scmd += ".exe"

    if PY2:
        print("# checking {}".format(scmd))
        acmd = (scmd + " -version").encode("ascii").split(b" ")
        try:
            sp.Popen(acmd, stdout=sp.PIPE, stderr=sp.PIPE).communicate()
            return True
        except:
            return False
    else:
        return bool(shutil.which(scmd))


HAVE_FFMPEG = not os.environ.get("PRTY_NO_FFMPEG") and have_ff("ffmpeg")
HAVE_FFPROBE = not os.environ.get("PRTY_NO_FFPROBE") and have_ff("ffprobe")

CBZ_PICS = set("png jpg jpeg gif bmp tga tif tiff webp avif".split())
CBZ_01 = re.compile(r"(^|[^0-9v])0+[01]\b")

FMT_AU = set("mp3 ogg flac wav".split())


class MParser(object):
    def __init__(self, cmdline )  :
        self.tag, args = cmdline.split("=", 1)
        self.tags = self.tag.split(",")

        self.timeout = 60
        self.force = False
        self.kill = "t"  # tree; all children recursively
        self.capture = 3  # outputs to consume
        self.audio = "y"
        self.pri = 0  # priority; higher = later
        self.ext = []

        while True:
            try:
                bp = os.path.expanduser(args)
                if WINDOWS:
                    bp = uncyg(bp)

                if bos.path.exists(bp):
                    self.bin = bp
                    return
            except:
                pass

            arg, args = args.split(",", 1)
            arg = arg.lower()

            if arg.startswith("a"):
                self.audio = arg[1:]  # [r]equire [n]ot [d]ontcare
                continue

            if arg.startswith("k"):
                self.kill = arg[1:]  # [t]ree [m]ain [n]one
                continue

            if arg.startswith("c"):
                self.capture = int(arg[1:])  # 0=none 1=stdout 2=stderr 3=both
                continue

            if arg == "f":
                self.force = True
                continue

            if arg.startswith("t"):
                self.timeout = int(arg[1:])
                continue

            if arg.startswith("e"):
                self.ext.append(arg[1:])
                continue

            if arg.startswith("p"):
                self.pri = int(arg[1:] or "1")
                continue

            raise Exception()


def au_unpk(
    log , fmt_map  , abspath , vn  = None
)  :
    ret = ""
    maxsz = 1024 * 1024 * 64
    try:
        ext = abspath.split(".")[-1].lower()
        au, pk = fmt_map[ext].split(".")

        fd, ret = tempfile.mkstemp("." + au)

        if pk == "gz":
            fi = gzip.GzipFile(abspath, mode="rb")

        elif pk == "xz":
            import lzma

            fi = lzma.open(abspath, "rb")

        elif pk == "zip":
            import zipfile

            zf = zipfile.ZipFile(abspath, "r")
            zil = zf.infolist()
            zil = [x for x in zil if x.filename.lower().split(".")[-1] == au]
            if not zil:
                raise Exception("no audio inside zip")
            fi = zf.open(zil[0])

        elif pk == "cbz":
            import zipfile

            zf = zipfile.ZipFile(abspath, "r")
            znil = [(x.filename.lower(), x) for x in zf.infolist()]
            nf = len(znil)
            znil = [x for x in znil if x[0].split(".")[-1] in CBZ_PICS]
            znil = [x for x in znil if "cover" in x[0]] or znil
            znil = [x for x in znil if CBZ_01.search(x[0])] or znil
            t = "cbz: %d files, %d hits" % (nf, len(znil))
            if not znil:
                raise Exception("no images inside cbz")
            using = sorted(znil)[0][1].filename
            if znil:
                t += ", using " + using
            log(t)
            fi = zf.open(using)

        elif pk == "epub":
            fi = get_cover_from_epub(log, abspath)

        else:
            raise Exception("unknown compression %s" % (pk,))

        fsz = 0
        with os.fdopen(fd, "wb") as fo:
            while True:
                buf = fi.read(32768)
                if not buf:
                    break

                fsz += len(buf)
                if fsz > maxsz:
                    raise Exception("zipbomb defused")

                fo.write(buf)

        return ret

    except Exception as ex:
        if ret:
            t = "failed to decompress file %r: %r"
            log(t % (abspath, ex))
            wunlink(log, ret, vn.flags if vn else VF_CAREFUL)
            return ""

        return abspath


def ffprobe(
    abspath , timeout  = 60
)         :
    cmd = [
        b"ffprobe",
        b"-hide_banner",
        b"-show_streams",
        b"-show_format",
        b"--",
        fsenc(abspath),
    ]
    rc, so, se = runcmd(cmd, timeout=timeout, nice=True, oom=200)
    retchk(rc, cmd, se)
    return parse_ffprobe(so)


def parse_ffprobe(
    txt ,
)         :
    """
    txt: output from ffprobe -show_format -show_streams
    returns:
     * normalized tags
     * original/raw tags
     * list of streams
     * format props
    """
    streams = []
    fmt = {}
    g = {}
    for ln in [x.rstrip("\r") for x in txt.split("\n")]:
        try:
            sk, sv = ln.split("=", 1)
            g[sk] = sv
            continue
        except:
            pass

        if ln == "[STREAM]":
            g = {}
            streams.append(g)

        if ln == "[FORMAT]":
            g = {"codec_type": "format"}  # heh
            fmt = g

    streams = [fmt] + streams
    ret   = {}  # processed
    md   = {}  # raw tags

    is_audio = fmt.get("format_name") in FMT_AU
    if fmt.get("filename", "").split(".")[-1].lower() in ["m4a", "aac"]:
        is_audio = True

    # if audio file, ensure audio stream appears first
    if (
        is_audio
        and len(streams) > 2
        and streams[1].get("codec_type") != "audio"
        and streams[2].get("codec_type") == "audio"
    ):
        streams = [fmt, streams[2], streams[1]] + streams[3:]

    have = {}
    for strm in streams:
        typ = strm.get("codec_type")
        if typ in have:
            continue

        have[typ] = True
        kvm = []

        if typ == "audio":
            kvm = [
                ["codec_name", "ac"],
                ["channel_layout", "chs"],
                ["sample_rate", ".hz"],
                ["bit_rate", ".aq"],
                ["bits_per_sample", ".bps"],
                ["bits_per_raw_sample", ".bprs"],
                ["duration", ".dur"],
            ]

        if typ == "video":
            if strm.get("DISPOSITION:attached_pic") == "1" or is_audio:
                continue

            kvm = [
                ["codec_name", "vc"],
                ["pix_fmt", "pixfmt"],
                ["r_frame_rate", ".fps"],
                ["bit_rate", ".vq"],
                ["width", ".resw"],
                ["height", ".resh"],
                ["duration", ".dur"],
            ]

        if typ == "format":
            kvm = [["duration", ".dur"], ["bit_rate", ".q"], ["format_name", "fmt"]]

        for sk, rk in kvm:
            v1 = strm.get(sk)
            if v1 is None:
                continue

            if rk.startswith("."):
                try:
                    zf = float(v1)
                    v2 = ret.get(rk)
                    if v2 is None or zf > v2:
                        ret[rk] = zf
                except:
                    # sqlite doesnt care but the code below does
                    if v1 not in ["N/A"]:
                        ret[rk] = v1
            else:
                ret[rk] = v1

    if ret.get("vc") == "ansi":  # shellscript
        return {}, {}, [], {}

    for strm in streams:
        for sk, sv in strm.items():
            if not sk.startswith("TAG:"):
                continue

            sk = sk[4:].strip()
            sv = sv.strip()
            if sk and sv and sk not in md:
                md[sk] = [sv]

    for sk in [".q", ".vq", ".aq"]:
        if sk in ret:
            ret[sk] /= 1000  # bit_rate=320000

    for sk in [".q", ".vq", ".aq", ".resw", ".resh"]:
        if sk in ret:
            ret[sk] = int(ret[sk])

    if ".fps" in ret:
        fps = ret[".fps"]
        if "/" in fps:
            fa, fb = fps.split("/")
            try:
                fps = float(fa) / float(fb)
            except:
                fps = 9001

        if fps < 1000 and fmt.get("format_name") not in ["image2", "png_pipe"]:
            ret[".fps"] = round(fps, 3)
        else:
            del ret[".fps"]

    if ".dur" in ret:
        if ret[".dur"] < 0.1:
            del ret[".dur"]
            if ".q" in ret:
                del ret[".q"]

    if "fmt" in ret:
        ret["fmt"] = ret["fmt"].split(",")[0]

    if ".resw" in ret and ".resh" in ret:
        ret["res"] = "{}x{}".format(ret[".resw"], ret[".resh"])

    zero = int("0")
    zd = {k: (zero, v) for k, v in ret.items()}

    return zd, md, streams, fmt


def get_cover_from_epub(log , abspath )  :
    import zipfile

    from .dxml import parse_xml

    try:
        from urlparse import urljoin  # Python2
    except ImportError:
        from urllib.parse import urljoin  # Python3

    with zipfile.ZipFile(abspath, "r") as z:
        # First open the container file to find the package document (.opf file)
        try:
            container_root = parse_xml(z.read("META-INF/container.xml").decode())
        except KeyError:
            log("epub: no container file found in %s" % (abspath,))
            return None

        # https://www.w3.org/TR/epub-33/#sec-container.xml-rootfile-elem
        container_ns = {"": "urn:oasis:names:tc:opendocument:xmlns:container"}
        # One file could contain multiple package documents, default to the first one
        rootfile_path = container_root.find("./rootfiles/rootfile", container_ns).get(
            "full-path"
        )

        # Then open the first package document to find the path of the cover image
        try:
            package_root = parse_xml(z.read(rootfile_path).decode())
        except KeyError:
            log("epub: no package document found in %s" % (abspath,))
            return None

        # https://www.w3.org/TR/epub-33/#sec-package-doc
        package_ns = {"": "http://www.idpf.org/2007/opf"}
        # https://www.w3.org/TR/epub-33/#sec-cover-image
        coverimage_path_node = package_root.find(
            "./manifest/item[@properties='cover-image']", package_ns
        )
        if coverimage_path_node is not None:
            coverimage_path = coverimage_path_node.get("href")
        else:
            # This might be an EPUB2 file, try the legacy way of specifying covers
            coverimage_path = _get_cover_from_epub2(log, package_root, package_ns)

        if not coverimage_path:
            raise Exception("no cover inside epub")

        # This url is either absolute (in the .epub) or relative to the package document
        adjusted_cover_path = urljoin(rootfile_path, coverimage_path)

        try:
            return z.open(adjusted_cover_path)
        except KeyError:
            t = "epub: cover specified in package document, but doesn't exist: %s"
            log(t % (adjusted_cover_path,))


def _get_cover_from_epub2(
    log , package_root, package_ns
)  :
    # <meta name="cover" content="id-to-cover-image"> in <metadata>, then
    # <item> in <manifest>
    xn = package_root.find("./metadata/meta[@name='cover']", package_ns)
    cover_id = xn.get("content") if xn is not None else None

    if not cover_id:
        return None

    for node in package_root.iterfind("./manifest/item", package_ns):
        if node.get("id") == cover_id:
            cover_path = node.get("href")
            return cover_path

    return None


class MTag(object):
    def __init__(self, log_func , args )  :
        self.log_func = log_func
        self.args = args
        self.usable = True
        self.prefer_mt = not args.no_mtag_ff
        self.backend = (
            "ffprobe" if args.no_mutagen or (HAVE_FFPROBE and EXE) else "mutagen"
        )
        self.can_ffprobe = HAVE_FFPROBE and not args.no_mtag_ff
        mappings = args.mtm
        or_ffprobe = " or FFprobe"

        if self.backend == "mutagen":
            self._get = self.get_mutagen
            if not HAVE_MUTAGEN:
                self.log("could not load Mutagen, trying FFprobe instead", c=3)
                self.backend = "ffprobe"

        if self.backend == "ffprobe":
            self.usable = self.can_ffprobe
            self._get = self.get_ffprobe
            self.prefer_mt = True

            if not HAVE_FFPROBE:
                pass

            elif args.no_mtag_ff:
                msg = "found FFprobe but it was disabled by --no-mtag-ff"
                self.log(msg, c=3)

        if not self.usable:
            if EXE:
                t = "copyparty.exe cannot use mutagen; need ffprobe.exe to read media tags: "
                self.log(t + FFMPEG_URL)
                return

            msg = "need Mutagen{} to read media tags so please run this:\n{}{} -m pip install --user mutagen\n"
            pyname = os.path.basename(pybin)
            self.log(msg.format(or_ffprobe, " " * 37, pyname), c=1)
            return

        # https://picard-docs.musicbrainz.org/downloads/MusicBrainz_Picard_Tag_Map.html
        tagmap = {
            "album": ["album", "talb", "\u00a9alb", "original-album", "toal"],
            "artist": [
                "artist",
                "tpe1",
                "\u00a9art",
                "composer",
                "performer",
                "arranger",
                "\u00a9wrt",
                "tcom",
                "tpe3",
                "original-artist",
                "tope",
            ],
            "title": ["title", "tit2", "\u00a9nam"],
            "circle": [
                "album-artist",
                "tpe2",
                "aart",
                "organization",
                "band",
            ],
            ".tn": ["tracknumber", "trck", "trkn", "track"],
            "genre": ["genre", "tcon", "\u00a9gen"],
            "date": [
                "original-release-date",
                "release-date",
                "date",
                "tdrc",
                "\u00a9day",
                "original-date",
                "original-year",
                "tyer",
                "tdor",
                "tory",
                "year",
                "creation-time",
            ],
            ".bpm": ["bpm", "tbpm", "tmpo", "tbp"],
            "key": ["initial-key", "tkey", "key"],
            "comment": ["comment", "comm", "\u00a9cmt", "comments", "description"],
        }

        if mappings:
            for k, v in [x.split("=") for x in mappings]:
                tagmap[k] = v.split(",")

        self.tagmap = {}
        for k, vs in tagmap.items():
            vs2 = []
            for v in vs:
                if "-" not in v:
                    vs2.append(v)
                    continue

                vs2.append(v.replace("-", " "))
                vs2.append(v.replace("-", "_"))
                vs2.append(v.replace("-", ""))

            self.tagmap[k] = vs2

        self.rmap = {
            v: [n, k] for k, vs in self.tagmap.items() for n, v in enumerate(vs)
        }
        # self.get = self.compare

    def log(self, msg , c   = 0)  :
        self.log_func("mtag", msg, c)

    def normalize_tags(
        self, parser_output   , md  
    )    :
        for sk, tv in dict(md).items():
            if not tv:
                continue

            sk = sk.lower().split("::")[0].strip()
            key_mapping = self.rmap.get(sk)
            if not key_mapping:
                continue

            priority, alias = key_mapping
            if alias not in parser_output or parser_output[alias][0] > priority:
                parser_output[alias] = (priority, tv[0])

        # take first value (lowest priority / most preferred)
        ret    = {
            sk: unicode(tv[1]).strip() for sk, tv in parser_output.items()
        }

        # track 3/7 => track 3
        for sk, zv in ret.items():
            if sk[0] == ".":
                sv = str(zv).split("/")[0].strip().lstrip("0")
                ret[sk] = sv or 0

        # normalize key notation to rekobo
        okey = ret.get("key")
        if okey:
            key = str(okey).replace(" ", "").replace("maj", "").replace("min", "m")
            ret["key"] = REKOBO_LKEY.get(key.lower(), okey)

        if self.args.mtag_vv:
            zl = " ".join("\033[36m{} \033[33m{}".format(k, v) for k, v in ret.items())
            self.log("norm: {}\033[0m".format(zl), "90")

        return ret

    def compare(self, abspath )    :
        if abspath.endswith(".au"):
            return {}

        print("\n" + abspath)
        r1 = self.get_mutagen(abspath)
        r2 = self.get_ffprobe(abspath)

        keys = {}
        for d in [r1, r2]:
            for k in d.keys():
                keys[k] = True

        diffs = []
        l1 = []
        l2 = []
        for k in sorted(keys.keys()):
            if k in [".q", ".dur"]:
                continue  # lenient

            v1 = r1.get(k)
            v2 = r2.get(k)
            if v1 == v2:
                print("  ", k, v1)
            elif v1 != "0000":  # FFprobe date=0
                diffs.append(k)
                print(" 1", k, v1)
                print(" 2", k, v2)
                if v1:
                    l1.append(k)
                if v2:
                    l2.append(k)

        if diffs:
            raise Exception()

        return r1

    def get(self, abspath )    :
        ext = abspath.split(".")[-1].lower()
        if ext not in self.args.au_unpk:
            return self._get(abspath)

        ap = au_unpk(self.log, self.args.au_unpk, abspath)
        if not ap:
            return {}

        ret = self._get(ap)
        if ap != abspath:
            wunlink(self.log, ap, VF_CAREFUL)
        return ret

    def get_mutagen(self, abspath )    :
        ret    = {}

        if not bos.path.isfile(abspath):
            return {}

        from mutagen import File

        try:
            md = File(fsenc(abspath), easy=True)
            assert md
            if self.args.mtag_vv:
                for zd in (md.info.__dict__, dict(md.tags)):
                    zl = ["\033[36m{} \033[33m{}".format(k, v) for k, v in zd.items()]
                    self.log("mutagen: {}\033[0m".format(" ".join(zl)), "90")
            if not md.info.length and not md.info.codec:
                raise Exception()
        except Exception as ex:
            if self.args.mtag_v:
                self.log("mutagen-err [%s] @ %r" % (ex, abspath), "90")

            return self.get_ffprobe(abspath) if self.can_ffprobe else {}

        sz = bos.path.getsize(abspath)
        try:
            ret[".q"] = (0, int((sz / md.info.length) / 128))
        except:
            pass

        for attr, k, norm in [
            ["codec", "ac", unicode],
            ["channels", "chs", int],
            ["sample_rate", ".hz", int],
            ["bitrate", ".aq", int],
            ["length", ".dur", int],
        ]:
            try:
                v = getattr(md.info, attr)
            except:
                if k != "ac":
                    continue

                try:
                    v = str(md.info).split(".")[1]
                    if v.startswith("ogg"):
                        v = v[3:]
                except:
                    continue

            if not v:
                continue

            if k == ".aq":
                v /= 1000  # type: ignore

            if k == "ac" and v.startswith("mp4a.40."):
                v = "aac"

            ret[k] = (0, norm(v))

        return self.normalize_tags(ret, md)

    def get_ffprobe(self, abspath )    :
        if not bos.path.isfile(abspath):
            return {}

        ret, md, _, _ = ffprobe(abspath, self.args.mtag_to)

        if self.args.mtag_vv:
            for zd in (ret, dict(md)):
                zl = ["\033[36m{} \033[33m{}".format(k, v) for k, v in zd.items()]
                self.log("ffprobe: {}\033[0m".format(" ".join(zl)), "90")

        return self.normalize_tags(ret, md)

    def get_bin(
        self, parsers  , abspath , oth_tags  
    )   :
        if not bos.path.isfile(abspath):
            return {}

        env = os.environ.copy()
        try:
            if EXE:
                raise Exception()

            pypath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            zsl = [str(pypath)] + [str(x) for x in sys.path if x]
            pypath = str(os.pathsep.join(zsl))
            env["PYTHONPATH"] = pypath
        except:
            raise  # might be expected outside cpython

        ext = abspath.split(".")[-1].lower()
        if ext in self.args.au_unpk:
            ap = au_unpk(self.log, self.args.au_unpk, abspath)
        else:
            ap = abspath

        ret   = {}
        if not ap:
            return ret

        for tagname, parser in sorted(parsers.items(), key=lambda x: (x[1].pri, x[0])):
            try:
                cmd = [parser.bin, ap]
                if parser.bin.endswith(".py"):
                    cmd = [pybin] + cmd

                args = {
                    "env": env,
                    "nice": True,
                    "oom": 300,
                    "timeout": parser.timeout,
                    "kill": parser.kill,
                    "capture": parser.capture,
                }

                if parser.pri:
                    zd = oth_tags.copy()
                    zd.update(ret)
                    args["sin"] = json.dumps(zd).encode("utf-8", "replace")

                bcmd = [sfsenc(x) for x in cmd[:-1]] + [fsenc(cmd[-1])]
                rc, v, err = runcmd(bcmd, **args)  # type: ignore
                retchk(rc, bcmd, err, self.log, 5, self.args.mtag_v)
                v = v.strip()
                if not v:
                    continue

                if "," not in tagname:
                    ret[tagname] = v
                else:
                    zj = json.loads(v)
                    for tag in tagname.split(","):
                        if tag and tag in zj:
                            ret[tag] = zj[tag]
            except:
                if self.args.mtag_v:
                    t = "mtag error: tagname %r, parser %r, file %r => %r"
                    self.log(t % (tagname, parser.bin, abspath, min_ex()), 6)

        if ap != abspath:
            wunlink(self.log, ap, VF_CAREFUL)

        return ret
