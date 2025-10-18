"""
**AveyTense Constants** \n
@lifetime >= 0.3.26rc3 \\
© 2024-Present John "Aveyzan" Mammoth // License: MIT \\
https://aveyzan.xyz/aveytense#aveytense.constants

Constants wrapper for AveyTense. Extracted from former `tense.tcs` module
"""
from __future__ import annotations
from decimal import Decimal

from ._ᴧv_collection._constants import (
    AbroadHexMode as _AbroadHexMode,
    BisectMode as _BisectMode,
    InsortMode as _InsortMode,
    ProbabilityLength as _ProbabilityLength,
    ModeSelection as _ModeSelection
)

#################################### ENUM CONSTANTS ####################################

ABROAD_HEX_INCLUDE = _AbroadHexMode.INCLUDE # 0.3.35
ABROAD_HEX_HASH = _AbroadHexMode.HASH # 0.3.35
ABROAD_HEX_EXCLUDE = _AbroadHexMode.EXCLUDE # 0.3.35

BISECT_LEFT = _BisectMode.LEFT # 0.3.35
BISECT_RIGHT = _BisectMode.RIGHT # 0.3.35

INSORT_LEFT = _InsortMode.LEFT # 0.3.35
INSORT_RIGHT = _InsortMode.RIGHT # 0.3.35

PROBABILITY_MIN = _ProbabilityLength.MIN # 0.3.35
PROBABILITY_MAX = _ProbabilityLength.MAX # 0.3.35
PROBABILITY_COMPUTE = _ProbabilityLength.COMPUTE # 0.3.35
PROBABILITY_DEFAULT = _ProbabilityLength.DEFAULT # 0.3.35

MODE_AND = _ModeSelection.AND # 0.3.36
MODE_OR = _ModeSelection.OR # 0.3.36

STRING_LOWER = "abcdefghijklmnopqrstuvwxyz" # 0.3.36
STRING_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" # 0.3.36
STRING_LETTERS = STRING_LOWER + STRING_UPPER # 0.3.36
STRING_HEXADECIMAL = "0123456789abcdefABCDEF" # 0.3.36
STRING_DIGITS = "0123456789" # 0.3.36
STRING_OCTAL = "01234567" # 0.3.36
STRING_BINARY = "01" # 0.3.36
STRING_SPECIAL = r"""`~!@#$%^&*()-_=+[]{};:'"\|,.<>/?""" # 0.3.36
STRING_WHITESPACE = "\n\t\r\v\f" # 0.3.57

RGB_MIN = 0 # 0.3.37
RGB_MAX = (1 << 24) - 1 # 0.3.37

#################################### NUMBER CONSTANTS ####################################

# JavaScript
# >= 0.3.26b3; < 0.3.53; >= 0.3.57
# NOTE: 'JS_MIN_VALUE' constant value won't be displayed exactly as-is as a float object, it
# will comply with JavaScript's approximate value 5e-324 (from formula 2 ** -1074), so using
# 'decimal.Decimal' in this case.
JS_MIN_SAFE_INTEGER = -((1 << 53) - 1) 
JS_MAX_SAFE_INTEGER = ((1 << 53) - 1)
JS_MIN_VALUE = Decimal(4.940656458412465441765687928682213723650598026143247644255856825006755072702087518652998363616359923797965646954457177309266567103559397963987747960107818781263007131903114045278458171678489821036887186360569987307230500063874091535649843873124733972731696151400317153853980741262385655911710266585566867681870395603106249319452715914924553293054565444011274801297099995419319894090804165633245247571478690147267801593552386115501348035264934720193790268107107491703332226844753335720832431936092382893458368060106011506169809753078342277318329247904982524730776375927247874656084778203734469699533647017972677717585125660551199131504891101451037862738167250955837389733598993664809941164205702637090279242767544565229087538682506419718265533447265625e-324)
JS_MAX_VALUE = (1 << 1024) - (1 << 971)

# Borrowed from C/C++ (8-128 bits). 128-bit integer is compiler specific.
# Going above 14287 bits ('(1 << N) - 1' where N > 14287) will require
# exceeding the 4300 digit display limit with 'sys.set_int_max_str_digits'.
# This is set to 0 by default in AveyTense (see __init__.py file) whether
# this function is defined, but may not work on older versions of Python
# preceding 3.11. In this case hasattr() is used.
UINT8_MIN = UINT16_MIN = UINT32_MIN = UINT64_MIN = UINT128_MIN = UINT256_MIN = \
UINT512_MIN = UINT1024_MIN = UINT2048_MIN = UINT4096_MIN = UINT8192_MIN = 0 # 0.3.57 (all)
UINT8_MAX = (1 << (1 << 3)) - 1 # 0.3.57
UINT16_MAX = (1 << (1 << 4)) - 1 # 0.3.57
UINT32_MAX = (1 << (1 << 5)) - 1 # 0.3.57
UINT64_MAX = (1 << (1 << 6)) - 1 # 0.3.57
UINT128_MAX = (1 << (1 << 7)) - 1 # 0.3.57
UINT256_MAX = (1 << (1 << 8)) - 1 # 0.3.57
UINT512_MAX = (1 << (1 << 9)) - 1 # 0.3.57
UINT1024_MAX = (1 << (1 << 10)) - 1 # 0.3.57
UINT2048_MAX = (1 << (1 << 11)) - 1 # 0.3.57
UINT4096_MAX = (1 << (1 << 12)) - 1 # 0.3.57
UINT8192_MAX = (1 << (1 << 13)) - 1 # 0.3.57

INT8_MIN = -(1 << 7) # 0.3.57
INT8_MAX = (1 << 7) - 1 # 0.3.57
INT16_MIN = -(1 << 15) # 0.3.57
INT16_MAX = (1 << 15) - 1 # 0.3.57
INT32_MIN = -(1 << 31) # 0.3.57
INT32_MAX = (1 << 31) - 1 # 0.3.57
INT64_MIN = -(1 << 63) # 0.3.57
INT64_MAX = (1 << 63) - 1 # 0.3.57
INT128_MIN = -(1 << 127) # 0.3.57
INT128_MAX = (1 << 127) - 1 # 0.3.57
INT256_MIN = -(1 << 255) # 0.3.57
INT256_MAX = (1 << 255) - 1 # 0.3.57
INT512_MIN = -(1 << 511) # 0.3.57
INT512_MAX = (1 << 511) - 1 # 0.3.57
INT1024_MIN = -(1 << 1023) # 0.3.57
INT1024_MAX = (1 << 1023) - 1 # 0.3.57
INT2048_MIN = -(1 << 2047) # 0.3.57
INT2048_MAX = (1 << 2047) - 1 # 0.3.57
INT4096_MIN = -(1 << 4095) # 0.3.57
INT4096_MAX = (1 << 4095) - 1 # 0.3.57
INT8192_MIN = -(1 << 8191) # 0.3.57
INT8192_MAX = (1 << 8191) - 1 # 0.3.57

SIZE_MAX = (PROBABILITY_MAX.value + 1) * 2 - 1 # 0.3.57
SSIZE_MAX = PROBABILITY_MAX.value # 0.3.57; sys.maxsize

del Decimal # not for export

__all__ = [k for k in globals() if not k.startswith("_")]
"""
@lifetime >= 0.3.41
"""
__all_deprecated__ = sorted([n for n in globals() if hasattr(globals()[n], "__deprecated__")])
"""
@lifetime >= 0.3.41

Returns all deprecated declarations within this module.
"""

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error