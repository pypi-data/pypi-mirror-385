# coding: utf-8

# modified copy of Project Nayuki's qrcodegen (MIT-licensed);
# https://github.com/nayuki/QR-Code-generator/blob/daa3114/python/qrcodegen.py
# the original ^ is extremely well commented so refer to that for explanations

# hacks: binary-only, auto-ecc, py2-compat

from __future__ import print_function, unicode_literals

import collections
import itertools

try:
    range = xrange
except:
    pass


def num_char_count_bits(ver )  :
    return 16 if (ver + 7) // 17 else 8


class Ecc(object):
    #ordinal: int
    #formatbits: int

    def __init__(self, i , fb )  :
        self.ordinal = i
        self.formatbits = fb

    #LOW: "Ecc"
    #MEDIUM: "Ecc"
    #QUARTILE: "Ecc"
    #HIGH: "Ecc"


Ecc.LOW = Ecc(0, 1)
Ecc.MEDIUM = Ecc(1, 0)
Ecc.QUARTILE = Ecc(2, 3)
Ecc.HIGH = Ecc(3, 2)


class QrSegment(object):
    @staticmethod
    def make_seg(data  )  :
        bb = _BitBuffer()
        for b in data:
            bb.append_bits(b, 8)
        return QrSegment(len(data), bb)

    #numchars: int  # num bytes, not the same as the data's bit length
    #bitdata: List[int]  # The data bits of this segment

    def __init__(self, numch , bitdata )  :
        if numch < 0:
            raise ValueError()
        self.numchars = numch
        self.bitdata = list(bitdata)

    @staticmethod
    def get_total_bits(segs , ver )  :
        result = 0
        for seg in segs:
            ccbits  = num_char_count_bits(ver)
            if seg.numchars >= (1 << ccbits):
                return None  # segment length doesn't fit the field's bit width
            result += 4 + ccbits + len(seg.bitdata)
        return result


class QrCode(object):
    @staticmethod
    def encode_binary(data  )  :
        return QrCode.encode_segments([QrSegment.make_seg(data)])

    @staticmethod
    def encode_segments(
        segs ,
        ecl  = Ecc.LOW,
        minver  = 2,
        maxver  = 40,
        mask  = -1,
    )  :
        for ver in range(minver, maxver + 1):
            datacapacitybits  = QrCode._get_num_data_codewords(ver, ecl) * 8
            datausedbits  = QrSegment.get_total_bits(segs, ver)
            if (datausedbits is not None) and (datausedbits <= datacapacitybits):
                break

        assert datausedbits

        for newecl in (
            Ecc.MEDIUM,
            Ecc.QUARTILE,
            Ecc.HIGH,
        ):
            if datausedbits <= QrCode._get_num_data_codewords(ver, newecl) * 8:
                ecl = newecl

        # Concatenate all segments to create the data bit string
        bb = _BitBuffer()
        for seg in segs:
            bb.append_bits(4, 4)
            bb.append_bits(seg.numchars, num_char_count_bits(ver))
            bb.extend(seg.bitdata)
        assert len(bb) == datausedbits

        # Add terminator and pad up to a byte if applicable
        datacapacitybits = QrCode._get_num_data_codewords(ver, ecl) * 8
        assert len(bb) <= datacapacitybits
        bb.append_bits(0, min(4, datacapacitybits - len(bb)))
        bb.append_bits(0, -len(bb) % 8)
        assert len(bb) % 8 == 0

        # Pad with alternating bytes until data capacity is reached
        for padbyte in itertools.cycle((0xEC, 0x11)):
            if len(bb) >= datacapacitybits:
                break
            bb.append_bits(padbyte, 8)

        # Pack bits into bytes in big endian
        datacodewords = bytearray([0] * (len(bb) // 8))
        for (i, bit) in enumerate(bb):
            datacodewords[i >> 3] |= bit << (7 - (i & 7))

        return QrCode(ver, ecl, datacodewords, mask)

    #ver: int
    #size: int  # w/h; 21..177 (ver * 4 + 17)
    #ecclvl: Ecc
    #mask: int  # 0..7
    #modules: List[List[bool]]
    #unmaskable: List[List[bool]]

    def __init__(
        self,
        ver ,
        ecclvl ,
        datacodewords  ,
        msk ,
    )  :
        self.ver = ver
        self.size = ver * 4 + 17
        self.ecclvl = ecclvl

        self.modules = [[False] * self.size for _ in range(self.size)]
        self.unmaskable = [[False] * self.size for _ in range(self.size)]

        # Compute ECC, draw modules
        self._draw_function_patterns()
        allcodewords  = self._add_ecc_and_interleave(bytearray(datacodewords))
        self._draw_codewords(allcodewords)

        if msk == -1:  # automask
            minpenalty  = 1 << 32
            for i in range(8):
                self._apply_mask(i)
                self._draw_format_bits(i)
                penalty = self._get_penalty_score()
                if penalty < minpenalty:
                    msk = i
                    minpenalty = penalty
                self._apply_mask(i)  # xor/undo

        assert 0 <= msk <= 7
        self.mask = msk
        self._apply_mask(msk)  # Apply the final choice of mask
        self._draw_format_bits(msk)  # Overwrite old format bits

    def _draw_function_patterns(self)  :
        # Draw horizontal and vertical timing patterns
        for i in range(self.size):
            self._set_function_module(6, i, i % 2 == 0)
            self._set_function_module(i, 6, i % 2 == 0)

        # Draw 3 finder patterns (all corners except bottom right; overwrites some timing modules)
        self._draw_finder_pattern(3, 3)
        self._draw_finder_pattern(self.size - 4, 3)
        self._draw_finder_pattern(3, self.size - 4)

        # Draw numerous alignment patterns
        alignpatpos  = self._get_alignment_pattern_positions()
        numalign  = len(alignpatpos)
        skips   = (
            (0, 0),
            (0, numalign - 1),
            (numalign - 1, 0),
        )
        for i in range(numalign):
            for j in range(numalign):
                if (i, j) not in skips:  # avoid finder corners
                    self._draw_alignment_pattern(alignpatpos[i], alignpatpos[j])

        # draw config data with dummy mask value; ctor overwrites it
        self._draw_format_bits(0)
        self._draw_ver()

    def _draw_format_bits(self, mask )  :
        # Calculate error correction code and pack bits; ecclvl is uint2, mask is uint3
        data  = self.ecclvl.formatbits << 3 | mask
        rem  = data
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        bits  = (data << 10 | rem) ^ 0x5412  # uint15
        assert bits >> 15 == 0

        # first copy
        for i in range(0, 6):
            self._set_function_module(8, i, _get_bit(bits, i))
        self._set_function_module(8, 7, _get_bit(bits, 6))
        self._set_function_module(8, 8, _get_bit(bits, 7))
        self._set_function_module(7, 8, _get_bit(bits, 8))
        for i in range(9, 15):
            self._set_function_module(14 - i, 8, _get_bit(bits, i))

        # second copy
        for i in range(0, 8):
            self._set_function_module(self.size - 1 - i, 8, _get_bit(bits, i))
        for i in range(8, 15):
            self._set_function_module(8, self.size - 15 + i, _get_bit(bits, i))
        self._set_function_module(8, self.size - 8, True)  # Always dark

    def _draw_ver(self)  :
        if self.ver < 7:
            return

        # Calculate error correction code and pack bits
        rem  = self.ver  # ver is uint6, 7..40
        for _ in range(12):
            rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
        bits  = self.ver << 12 | rem  # uint18
        assert bits >> 18 == 0

        # Draw two copies
        for i in range(18):
            bit  = _get_bit(bits, i)
            a  = self.size - 11 + i % 3
            b  = i // 3
            self._set_function_module(a, b, bit)
            self._set_function_module(b, a, bit)

    def _draw_finder_pattern(self, x , y )  :
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                xx, yy = x + dx, y + dy
                if (0 <= xx < self.size) and (0 <= yy < self.size):
                    # Chebyshev/infinity norm
                    self._set_function_module(
                        xx, yy, max(abs(dx), abs(dy)) not in (2, 4)
                    )

    def _draw_alignment_pattern(self, x , y )  :
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                self._set_function_module(x + dx, y + dy, max(abs(dx), abs(dy)) != 1)

    def _set_function_module(self, x , y , isdark )  :
        self.modules[y][x] = isdark
        self.unmaskable[y][x] = True

    def _add_ecc_and_interleave(self, data )  :
        ver  = self.ver
        assert len(data) == QrCode._get_num_data_codewords(ver, self.ecclvl)

        # Calculate parameter numbers
        numblocks  = QrCode._NUM_ERROR_CORRECTION_BLOCKS[self.ecclvl.ordinal][ver]
        blockecclen  = QrCode._ECC_CODEWORDS_PER_BLOCK[self.ecclvl.ordinal][ver]
        rawcodewords  = QrCode._get_num_raw_data_modules(ver) // 8
        numshortblocks  = numblocks - rawcodewords % numblocks
        shortblocklen  = rawcodewords // numblocks

        # Split data into blocks and append ECC to each block
        blocks  = []
        rsdiv  = QrCode._reed_solomon_compute_divisor(blockecclen)
        k  = 0
        for i in range(numblocks):
            dat  = data[
                k : k + shortblocklen - blockecclen + (0 if i < numshortblocks else 1)
            ]
            k += len(dat)
            ecc  = QrCode._reed_solomon_compute_remainder(dat, rsdiv)
            if i < numshortblocks:
                dat.append(0)
            blocks.append(dat + ecc)
        assert k == len(data)

        # Interleave (not concatenate) the bytes from every block into a single sequence
        result = bytearray()
        for i in range(len(blocks[0])):
            for (j, blk) in enumerate(blocks):
                # Skip the padding byte in short blocks
                if (i != shortblocklen - blockecclen) or (j >= numshortblocks):
                    result.append(blk[i])
        assert len(result) == rawcodewords
        return result

    def _draw_codewords(self, data )  :
        assert len(data) == QrCode._get_num_raw_data_modules(self.ver) // 8

        i  = 0  # Bit index into the data
        for right in range(self.size - 1, 0, -2):
            # idx of right column in each column pair
            if right <= 6:
                right -= 1
            for vert in range(self.size):  # Vertical counter
                for j in range(2):
                    x  = right - j
                    upward  = (right + 1) & 2 == 0
                    y  = (self.size - 1 - vert) if upward else vert
                    if (not self.unmaskable[y][x]) and (i < len(data) * 8):
                        self.modules[y][x] = _get_bit(data[i >> 3], 7 - (i & 7))
                        i += 1
                    # any remainder bits (0..7) were set 0/false/light by ctor

        assert i == len(data) * 8

    def _apply_mask(self, mask )  :
        masker    = QrCode._MASK_PATTERNS[mask]
        for y in range(self.size):
            for x in range(self.size):
                self.modules[y][x] ^= (masker(x, y) == 0) and (
                    not self.unmaskable[y][x]
                )

    def _get_penalty_score(self)  :
        result  = 0
        size  = self.size
        modules  = self.modules

        # Adjacent modules in row having same color, and finder-like patterns
        for y in range(size):
            runcolor  = False
            runx  = 0
            runhistory = collections.deque([0] * 7, 7)
            for x in range(size):
                if modules[y][x] == runcolor:
                    runx += 1
                    if runx == 5:
                        result += QrCode._PENALTY_N1
                    elif runx > 5:
                        result += 1
                else:
                    self._finder_penalty_add_history(runx, runhistory)
                    if not runcolor:
                        result += (
                            self._finder_penalty_count_patterns(runhistory)
                            * QrCode._PENALTY_N3
                        )
                    runcolor = modules[y][x]
                    runx = 1
            result += (
                self._finder_penalty_terminate_and_count(runcolor, runx, runhistory)
                * QrCode._PENALTY_N3
            )

        # Adjacent modules in column having same color, and finder-like patterns
        for x in range(size):
            runcolor = False
            runy = 0
            runhistory = collections.deque([0] * 7, 7)
            for y in range(size):
                if modules[y][x] == runcolor:
                    runy += 1
                    if runy == 5:
                        result += QrCode._PENALTY_N1
                    elif runy > 5:
                        result += 1
                else:
                    self._finder_penalty_add_history(runy, runhistory)
                    if not runcolor:
                        result += (
                            self._finder_penalty_count_patterns(runhistory)
                            * QrCode._PENALTY_N3
                        )
                    runcolor = modules[y][x]
                    runy = 1
            result += (
                self._finder_penalty_terminate_and_count(runcolor, runy, runhistory)
                * QrCode._PENALTY_N3
            )

        # 2*2 blocks of modules having same color
        for y in range(size - 1):
            for x in range(size - 1):
                if (
                    modules[y][x]
                    == modules[y][x + 1]
                    == modules[y + 1][x]
                    == modules[y + 1][x + 1]
                ):
                    result += QrCode._PENALTY_N2

        # Balance of dark and light modules
        dark  = sum((1 if cell else 0) for row in modules for cell in row)
        total  = size ** 2  # Note that size is odd, so dark/total != 1/2

        # Compute the smallest integer k >= 0 such that (45-5k)% <= dark/total <= (55+5k)%
        k  = (abs(dark * 20 - total * 10) + total - 1) // total - 1
        assert 0 <= k <= 9
        result += k * QrCode._PENALTY_N4
        assert 0 <= result <= 2568888
        # ^ Non-tight upper bound based on default values of PENALTY_N1, ..., N4

        return result

    def _get_alignment_pattern_positions(self)  :
        ver  = self.ver
        if ver == 1:
            return []

        numalign  = ver // 7 + 2
        step  = (
            26
            if (ver == 32)
            else (ver * 4 + numalign * 2 + 1) // (numalign * 2 - 2) * 2
        )
        result  = [
            (self.size - 7 - i * step) for i in range(numalign - 1)
        ] + [6]
        return list(reversed(result))

    @staticmethod
    def _get_num_raw_data_modules(ver )  :
        result  = (16 * ver + 128) * ver + 64
        if ver >= 2:
            numalign  = ver // 7 + 2
            result -= (25 * numalign - 10) * numalign - 55
            if ver >= 7:
                result -= 36
        assert 208 <= result <= 29648
        return result

    @staticmethod
    def _get_num_data_codewords(ver , ecl )  :
        return (
            QrCode._get_num_raw_data_modules(ver) // 8
            - QrCode._ECC_CODEWORDS_PER_BLOCK[ecl.ordinal][ver]
            * QrCode._NUM_ERROR_CORRECTION_BLOCKS[ecl.ordinal][ver]
        )

    @staticmethod
    def _reed_solomon_compute_divisor(degree )  :
        if not (1 <= degree <= 255):
            raise ValueError("Degree out of range")

        # Polynomial coefficients are stored from highest to lowest power, excluding the leading term which is always 1.
        # For example the polynomial x^3 + 255x^2 + 8x + 93 is stored as the uint8 array [255, 8, 93].
        result = bytearray([0] * (degree - 1) + [1])  # start with monomial x^0

        # Compute the product polynomial (x - r^0) * (x - r^1) * (x - r^2) * ... * (x - r^{degree-1}),
        # and drop the highest monomial term which is always 1x^degree.
        # Note that r = 0x02, which is a generator element of this field GF(2^8/0x11D).
        root  = 1
        for _ in range(degree):
            # Multiply the current product by (x - r^i)
            for j in range(degree):
                result[j] = QrCode._reed_solomon_multiply(result[j], root)
                if j + 1 < degree:
                    result[j] ^= result[j + 1]
            root = QrCode._reed_solomon_multiply(root, 0x02)

        return result

    @staticmethod
    def _reed_solomon_compute_remainder(data , divisor )  :
        result = bytearray([0] * len(divisor))
        for b in data:  # Polynomial division
            factor  = b ^ result.pop(0)
            result.append(0)
            for (i, coef) in enumerate(divisor):
                result[i] ^= QrCode._reed_solomon_multiply(coef, factor)

        return result

    @staticmethod
    def _reed_solomon_multiply(x , y )  :
        if (x >> 8 != 0) or (y >> 8 != 0):
            raise ValueError("Byte out of range")
        z  = 0  # Russian peasant multiplication
        for i in reversed(range(8)):
            z = (z << 1) ^ ((z >> 7) * 0x11D)
            z ^= ((y >> i) & 1) * x
        assert z >> 8 == 0
        return z

    def _finder_penalty_count_patterns(self, runhistory )  :
        n  = runhistory[1]
        assert n <= self.size * 3
        core  = (
            n > 0
            and (runhistory[2] == runhistory[4] == runhistory[5] == n)
            and runhistory[3] == n * 3
        )
        return (
            1 if (core and runhistory[0] >= n * 4 and runhistory[6] >= n) else 0
        ) + (1 if (core and runhistory[6] >= n * 4 and runhistory[0] >= n) else 0)

    def _finder_penalty_terminate_and_count(
        self,
        currentruncolor ,
        currentrunlength ,
        runhistory ,
    )  :
        if currentruncolor:  # Terminate dark run
            self._finder_penalty_add_history(currentrunlength, runhistory)
            currentrunlength = 0
        currentrunlength += self.size  # Add light border to final run
        self._finder_penalty_add_history(currentrunlength, runhistory)
        return self._finder_penalty_count_patterns(runhistory)

    def _finder_penalty_add_history(
        self, currentrunlength , runhistory 
    )  :
        if runhistory[0] == 0:
            currentrunlength += self.size  # Add light border to initial run

        runhistory.appendleft(currentrunlength)

    _PENALTY_N1  = 3
    _PENALTY_N2  = 3
    _PENALTY_N3  = 40
    _PENALTY_N4  = 10

    # fmt: off
    _ECC_CODEWORDS_PER_BLOCK  = (
        (-1,  7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28, 30, 28, 28, 28, 28, 30, 30, 26, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),  # noqa: E241  # L
        (-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28),  # noqa: E241  # M
        (-1, 13, 22, 18, 26, 18, 24, 18, 22, 20, 24, 28, 26, 24, 20, 30, 24, 28, 28, 26, 30, 28, 30, 30, 30, 30, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),  # noqa: E241  # Q
        (-1, 17, 28, 22, 16, 22, 28, 26, 26, 24, 28, 24, 28, 22, 24, 24, 30, 28, 28, 26, 28, 30, 24, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30))  # noqa: E241  # H

    _NUM_ERROR_CORRECTION_BLOCKS  = (
        (-1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4,  4,  4,  4,  4,  6,  6,  6,  6,  7,  8,  8,  9,  9, 10, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 19, 20, 21, 22, 24, 25),  # noqa: E241  # L
        (-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5,  5,  8,  9,  9, 10, 10, 11, 13, 14, 16, 17, 17, 18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49),  # noqa: E241  # M
        (-1, 1, 1, 2, 2, 4, 4, 6, 6, 8, 8,  8, 10, 12, 16, 12, 17, 16, 18, 21, 20, 23, 23, 25, 27, 29, 34, 34, 35, 38, 40, 43, 45, 48, 51, 53, 56, 59, 62, 65, 68),  # noqa: E241  # Q
        (-1, 1, 1, 2, 4, 4, 4, 5, 6, 8, 8, 11, 11, 16, 16, 18, 16, 19, 21, 25, 25, 25, 34, 30, 32, 35, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 70, 74, 77, 81))  # noqa: E241  # H
    # fmt: on

    _MASK_PATTERNS    = (
        (lambda x, y: (x + y) % 2),
        (lambda x, y: y % 2),
        (lambda x, y: x % 3),
        (lambda x, y: (x + y) % 3),
        (lambda x, y: (x // 3 + y // 2) % 2),
        (lambda x, y: x * y % 2 + x * y % 3),
        (lambda x, y: (x * y % 2 + x * y % 3) % 2),
        (lambda x, y: ((x + y) % 2 + x * y % 3) % 2),
    )


class _BitBuffer(list):  # type: ignore
    def append_bits(self, val , n )  :
        if (n < 0) or (val >> n != 0):
            raise ValueError("Value out of range")

        self.extend(((val >> i) & 1) for i in reversed(range(n)))


def _get_bit(x , i )  :
    return (x >> i) & 1 != 0


class DataTooLongError(ValueError):
    pass
