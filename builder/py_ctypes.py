import sys


class PrimitiveType(object):
    decl = ''
    depends = None
    _registered_types = set()
    _used_types = []

    def __init__(self):
        self._registered_types.add(self.__class__)

    def get_decl(self):
        if self.__class__ not in self._used_types:
            self._used_types.append(self.__class__)
            res = []
            if self.depends is not None:
                depends = self.depends().get_decl()
            else:
                depends = ''

            if depends:
                res.append(depends)

            res.append(self.decl)

            return '\n'.join(res)

        return ''

    def __str__(self):
        return self.__class__.__name__


class short_t(PrimitiveType):
    decl = '''
class short_t(_ctypes.c_short, __IntMixin, __PyObjectStore):
    pass


_type_short_t = Union[short_t, int]
'''


class ushort_t(PrimitiveType):
    decl = ''' 
class ushort_t(_ctypes.c_ushort, __IntMixin, __PyObjectStore):
    pass


_type_ushort_t = Union[ushort_t, int]
'''


class long_t(PrimitiveType):
    decl = '''
class long_t(_ctypes.c_long, __IntMixin, __PyObjectStore):
    pass
    

_type_long_t = Union[long_t, int]
'''


class ulong_t(PrimitiveType):
    decl = '''
class ulong_t(_ctypes.c_ulong, __IntMixin, __PyObjectStore):
    pass


_type_ulong_t = Union[ulong_t, int]
'''


class int_t(PrimitiveType):
    decl = '''
class int_t(_ctypes.c_int, __IntMixin, __PyObjectStore):
    pass


_type_int_t = Union[int_t, int]
'''


class uint_t(PrimitiveType):
    decl = '''
class uint_t(_ctypes.c_uint, __IntMixin, __PyObjectStore):
    pass


_type_uint_t = Union[uint_t, int]
'''


class float_t(PrimitiveType):
    decl = '''
class float_t(_ctypes.c_float, __PyObjectStore):
    pass
    

_type_float_t = Union[float_t, float]
'''


class double_t(PrimitiveType):
    decl = '''
class double_t(_ctypes.c_double, __PyObjectStore):
    pass


_type_double_t = Union[double_t, float]
'''


class longdouble_t(PrimitiveType):
    decl = '''
class longdouble_t(_ctypes.c_longdouble, __PyObjectStore):
    pass


_type_longdouble_t = Union[longdouble_t, float]
'''


class longlong_t(PrimitiveType):
    decl = '''
class longlong_t(_ctypes.c_longlong, __IntMixin, __PyObjectStore):
    pass


_type_longlong_t = Union[longlong_t, int]
'''


class ulonglong_t(PrimitiveType):
    decl = '''
class ulonglong_t(_ctypes.c_ulonglong, __IntMixin, __PyObjectStore):
    pass


_type_ulonglong_t = Union[ulonglong_t, int]
'''


class ubyte_t(PrimitiveType):
    decl = '''
class ubyte_t(_ctypes.c_ubyte, __IntMixin, __PyObjectStore):
    pass


_type_ubyte_t = Union[ubyte_t, int]
'''


class byte_t(PrimitiveType):
    decl = '''
class byte_t(_ctypes.c_byte, __IntMixin, __PyObjectStore):
    pass


_type_byte_t = Union[byte_t, int]
'''


class char_t(PrimitiveType):
    decl = '''
class char_t(_ctypes.c_char, __PyObjectStore):
    pass
    

_type_char_t = Union[char_t, str, bytearray, bytes]
'''


class schar_t(PrimitiveType):
    depends = char_t
    decl = '''
class schar_t(char_t, __PyObjectStore):
    pass


_type_schar_t = Union[schar_t, str, bytearray, bytes]
'''


class void_t(PrimitiveType):
    decl = '''
class void_t(_ctypes.c_void_p, __PyObjectStore):
    pass
    

_type_void_t = Any
'''


class bool_t(PrimitiveType):
    decl = '''
class bool_t(_ctypes.c_bool, __PyObjectStore):
    pass


_type_bool_t = Union[bool_t, bool, int]
'''


class wchar_t(PrimitiveType):
    decl = '''
class wchar_t(_ctypes.c_wchar, __PyObjectStore):
    pass


_type_wchar_t = Union[wchar_t, bytearray, bytes]
'''


class size_t(PrimitiveType):
    decl = '''
class size_t(_ctypes.c_size_t, __IntMixin, __PyObjectStore):
    pass


_type_size_t = Union[size_t, int]
'''


class ssize_t(PrimitiveType):
    decl = '''
class ssize_t(_ctypes.c_ssize_t, __IntMixin, __PyObjectStore):
    pass


_type_ssize_t = Union[ssize_t, int]
'''


class int8_t(PrimitiveType):
    decl = '''
class int8_t(_ctypes.c_int8, __IntMixin, __PyObjectStore):
    pass


_type_int8_t = Union[int8_t, int]
'''


class int16_t(PrimitiveType):
    decl = '''
class int16_t(_ctypes.c_int16, __IntMixin, __PyObjectStore):
    pass


_type_int16_t = Union[int16_t, int]
'''


class int32_t(PrimitiveType):
    decl = '''
class int32_t(_ctypes.c_int32, __IntMixin, __PyObjectStore):
    pass


_type_int32_t = Union[int32_t, int]
'''


class int64_t(PrimitiveType):
    decl = '''
class int64_t(_ctypes.c_int64, __IntMixin, __PyObjectStore):
    pass


_type_int64_t = Union[int64_t, int] 
'''


class uint8_t(PrimitiveType):
    decl = '''
class uint8_t(_ctypes.c_uint8, __IntMixin, __PyObjectStore):
    pass


_type_uint8_t = Union[uint8_t, int]
'''


class uint16_t(PrimitiveType):
    decl = '''
class uint16_t(_ctypes.c_uint16, __IntMixin, __PyObjectStore):
    pass


_type_uint16_t = Union[uint16_t, int]
'''


class uint32_t(PrimitiveType):
    decl = '''
class uint32_t(_ctypes.c_uint32, __IntMixin, __PyObjectStore):
    pass


_type_uint32_t = Union[uint32_t, int]
'''


class uint64_t(PrimitiveType):
    decl = '''
class uint64_t(_ctypes.c_uint64, __IntMixin, __PyObjectStore):
    pass


_type_uint64_t = Union[uint64_t, int]
'''


if sys.maxsize > 2 ** 32:

    class intptr_t(PrimitiveType):
        depends = longlong_t
        decl = '''
class intptr_t(longlong_t):
    pass


_type_intptr_t = Union[intptr_t, int]
'''


    class uintptr_t(PrimitiveType):
        depends = ulonglong_t
        decl = '''
class uintptr_t(ulonglong_t):
    pass


_type_uintptr_t = Union[uintptr_t, int]
'''
else:

    class intptr_t(PrimitiveType):
        depends = long_t
        decl = '''
class intptr_t(long_t):
    pass


_type_intptr_t = Union[intptr_t, int]
'''

    class uintptr_t(PrimitiveType):
        depends = ulong_t
        decl = '''
class uintptr_t(ulong_t):
    pass


_type_uintptr_t = Union[uintptr_t, int]
'''


class int_least8_t(PrimitiveType):
    depends = int8_t
    decl = '''
class int_least8_t(int8_t):
    pass
    

_type_int_least8_t = Union[int_least8_t, int]
'''


class uint_least8_t(PrimitiveType):
    depends = uint8_t
    decl = '''
class uint_least8_t(uint8_t):
    pass


_type_uint_least8_t = Union[uint_least8_t, int]
'''


class int_least16_t(PrimitiveType):
    depends = int16_t
    decl = '''
class int_least16_t(int16_t):
    pass


_type_int_least16_t = Union[int_least16_t, int]
'''


class uint_least16_t(PrimitiveType):
    depends = uint16_t
    decl = '''
class uint_least16_t(uint16_t):
    pass


_type_uint_least16_t = Union[uint_least16_t, int]
'''


class int_least32_t(PrimitiveType):
    depends = int32_t
    decl = '''
class int_least32_t(int32_t):
    pass


_type_int_least32_t = Union[int_least32_t, int]
'''


class uint_least32_t(PrimitiveType):
    depends = uint32_t
    decl = '''
class uint_least32_t(uint32_t):
    pass


_type_uint_least32_t = Union[uint_least32_t, int]
'''


class int_least64_t(PrimitiveType):
    depends = int64_t
    decl = '''
class int_least64_t(int64_t):
    pass


_type_int_least64_t = Union[int_least64_t, int]
'''


class uint_least64_t(PrimitiveType):
    depends = uint64_t
    decl = '''
class uint_least64_t(uint64_t):
    pass


_type_uint_least64_t = Union[uint_least64_t, int]
'''


class int_fast8_t(PrimitiveType):
    depends = int8_t
    decl = '''
class int_fast8_t(int8_t):
    pass


_type_int_fast8_t = Union[int_fast8_t, int]
'''


class uint_fast8_t(PrimitiveType):
    depends = uint8_t
    decl = '''
class uint_fast8_t(uint8_t):
    pass


_type_uint_fast8_t = Union[uint_fast8_t, int]
'''


class int_fast16_t(PrimitiveType):
    depends = int16_t
    decl = '''
class int_fast16_t(int16_t):
    pass


_type_int_fast16_t = Union[int_fast16_t, int]
'''


class uint_fast16_t(PrimitiveType):
    depends = uint16_t
    decl = '''
class uint_fast16_t(uint16_t):
    pass


_type_uint_fast16_t = Union[uint_fast16_t, int]
'''


class int_fast32_t(PrimitiveType):
    depends = int32_t
    decl = '''
class int_fast32_t(int32_t):
    pass


_type_int_fast32_t = Union[int_fast32_t, int]
'''


class uint_fast32_t(PrimitiveType):
    depends = uint32_t
    decl = '''
class uint_fast32_t(uint32_t):
    pass


_type_uint_fast32_t = Union[uint_fast32_t, int]
'''


class int_fast64_t(PrimitiveType):
    depends = int64_t
    decl = '''
class int_fast64_t(int64_t):
    pass


_type_int_fast64_t = Union[int_fast64_t, int]
'''


class uint_fast64_t(PrimitiveType):
    depends = uint64_t
    decl = '''
class uint_fast64_t(uint64_t):
    pass


_type_uint_fast64_t = Union[uint_fast64_t, int]
'''


class atomic_bool_t(PrimitiveType):
    depends = bool_t
    decl = '''
class atomic_bool_t(bool_t):
    pass


_type_atomic_bool_t = Union[atomic_bool_t, bool, int]
'''


class atomic_char_t(PrimitiveType):
    depends = char_t
    decl = '''
class atomic_char_t(char_t):
    pass


_type_atomic_char_t = Union[atomic_char_t, str, bytearray, bytes]
'''


class atomic_schar_t(PrimitiveType):
    depends = schar_t
    decl = '''
class atomic_schar_t(schar_t):
    pass


_type_atomic_schar_t = Union[atomic_schar_t, str, bytearray, bytes]
'''


class uchar_t(PrimitiveType):
    depends = ubyte_t
    decl = '''
class uchar_t(ubyte_t):
    pass


_type_uchar_t = Union[uchar_t, str, bytearray, bytes]
'''


class atomic_uchar_t(PrimitiveType):
    depends = uchar_t
    decl = '''
class atomic_uchar_t(uchar_t):
    pass


_type_atomic_uchar_t = Union[atomic_uchar_t, str, bytearray, bytes]
'''


class atomic_short_t(PrimitiveType):
    depends = short_t
    decl = '''
class atomic_short_t(short_t):
    pass


_type_atomic_short_t = Union[atomic_short_t, int]
'''


class atomic_ushort_t(PrimitiveType):
    depends = ushort_t
    decl = '''
class atomic_ushort_t(ushort_t):
    pass


_type_atomic_ushort_t = Union[atomic_ushort_t, int]
'''


class atomic_int_t(PrimitiveType):
    depends = int_t
    decl = '''
class atomic_int_t(int_t):
    pass


_type_atomic_int_t = Union[atomic_int_t, int]
'''


class atomic_uint_t(PrimitiveType):
    depends = uint_t
    decl = '''
class atomic_uint_t(uint_t):
    pass


_type_atomic_uint_t = Union[atomic_uint_t, int]
'''


class atomic_long_t(PrimitiveType):
    depends = long_t
    decl = '''
class atomic_long_t(long_t):
    pass


_type_atomic_long_t = Union[atomic_long_t, int]
'''


class atomic_ulong_t(PrimitiveType):
    depends = ulong_t
    decl = '''
class atomic_ulong_t(ulong_t):
    pass


_type_atomic_ulong_t = Union[atomic_ulong_t, int]
'''


class llong_t(PrimitiveType):
    depends = longlong_t
    decl = '''
class llong_t(longlong_t):
    pass


_type_llong_t = Union[llong_t, int]
'''


class atomic_llong_t(PrimitiveType):
    depends = llong_t
    decl = '''
class atomic_llong_t(llong_t):
    pass


_type_atomic_llong_t = Union[atomic_llong_t, int]
'''


class ullong_t(PrimitiveType):
    depends = ulonglong_t
    decl = '''
class ullong_t(ulonglong_t):
    pass


_type_ullong_t = Union[ullong_t, int]
'''


class atomic_ullong_t(PrimitiveType):
    depends = ullong_t
    decl = '''
class atomic_ullong_t(ullong_t):
    pass


_type_atomic_ullong_t = Union[atomic_ullong_t, int]
'''


class char16_t(PrimitiveType):
    depends = short_t
    decl = '''
class char16_t(short_t):
    pass


_type_char16_t = Union[char16_t, int]
'''


class atomic_char16_t(PrimitiveType):
    depends = char16_t
    decl = '''
class atomic_char16_t(char16_t):
    pass


_type_atomic_char16_t = Union[atomic_char16_t, int]
'''


class char32_t(PrimitiveType):
    depends = long_t
    decl = '''
class char32_t(long_t):
    pass


_type_char32_t = Union[char32_t, int]
'''


class atomic_char32_t(PrimitiveType):
    depends = char32_t
    decl = '''
class atomic_char32_t(char32_t):
    pass


_type_atomic_char32_t = Union[atomic_char32_t, int]
'''


class atomic_wchar_t(PrimitiveType):
    depends = wchar_t
    decl = '''
class atomic_wchar_t(wchar_t):
    pass


_type_atomic_wchar_t = Union[atomic_wchar_t, bytes, bytearray]
'''


class atomic_int_least8_t(PrimitiveType):
    depends = int_least8_t
    decl = '''
class atomic_int_least8_t(int_least8_t):
    pass


_type_atomic_int_least8_t = Union[atomic_int_least8_t, int]
'''


class atomic_uint_least8_t(PrimitiveType):
    depends = uint_least8_t
    decl = '''
class atomic_uint_least8_t(uint_least8_t):
    pass


_type_atomic_uint_least8_t = Union[atomic_uint_least8_t, int]
'''


class atomic_int_least16_t(PrimitiveType):
    depends = int_least16_t
    decl = '''
class atomic_int_least16_t(int_least16_t):
    pass


_type_atomic_int_least16_t = Union[atomic_int_least16_t, int]
'''


class atomic_uint_least16_t(PrimitiveType):
    depends = uint_least16_t
    decl = '''
class atomic_uint_least16_t(uint_least16_t):
    pass


_type_atomic_uint_least16_t = Union[atomic_uint_least16_t, int]
'''


class atomic_int_least32_t(PrimitiveType):
    depends = int_least32_t
    decl = '''
class atomic_int_least32_t(int_least32_t):
    pass


_type_atomic_int_least32_t = Union[atomic_int_least32_t, int]
'''


class atomic_uint_least32_t(PrimitiveType):
    depends = uint_least32_t
    decl = '''
class atomic_uint_least32_t(uint_least32_t):
    pass


_type_atomic_uint_least32_t = Union[atomic_uint_least32_t, int]
'''


class atomic_int_least64_t(PrimitiveType):
    depends = int_least64_t
    decl = '''
class atomic_int_least64_t(int_least64_t):
    pass


_type_atomic_int_least64_t = Union[atomic_int_least64_t, int]
'''


class atomic_uint_least64_t(PrimitiveType):
    depends = uint_least64_t
    decl = '''
class atomic_uint_least64_t(uint_least64_t):
    pass


_type_atomic_uint_least64_t = Union[atomic_uint_least64_t, int]
'''


class atomic_int_fast8_t(PrimitiveType):
    depends = int_fast8_t
    decl = '''
class atomic_int_fast8_t(int_fast8_t):
    pass


_type_atomic_int_fast8_t = Union[atomic_int_fast8_t, int]
'''


class atomic_uint_fast8_t(PrimitiveType):
    depends = uint_fast8_t
    decl = '''
class atomic_uint_fast8_t(uint_fast8_t):
    pass


_type_atomic_uint_fast8_t = Union[atomic_uint_fast8_t, int]
'''


class atomic_int_fast16_t(PrimitiveType):
    depends = int_fast16_t
    decl = '''
class atomic_int_fast16_t(int_fast16_t):
    pass


_type_atomic_int_fast16_t = Union[atomic_int_fast16_t, int]
'''


class atomic_uint_fast16_t(PrimitiveType):
    depends = uint_fast16_t
    decl = '''
class atomic_uint_fast16_t(uint_fast16_t):
    pass


_type_atomic_uint_fast16_t = Union[atomic_uint_fast16_t, int]
'''


class atomic_int_fast32_t(PrimitiveType):
    depends = int_fast32_t
    decl = '''
class atomic_int_fast32_t(int_fast32_t):
    pass


_type_atomic_int_fast32_t = Union[atomic_int_fast32_t, int]
'''


class atomic_uint_fast32_t(PrimitiveType):
    depends = uint_fast32_t
    decl = '''
class atomic_uint_fast32_t(uint_fast32_t):
    pass


_type_atomic_uint_fast32_t = Union[atomic_uint_fast32_t, int]
'''


class atomic_int_fast64_t(PrimitiveType):
    depends = int_fast64_t
    decl = '''
class atomic_int_fast64_t(int_fast64_t):
    pass


_type_atomic_int_fast64_t = Union[atomic_int_fast64_t, int]
'''


class atomic_uint_fast64_t(PrimitiveType):
    depends = uint_fast64_t
    decl = '''
class atomic_uint_fast64_t(uint_fast64_t):
    pass


_type_atomic_uint_fast64_t = Union[atomic_uint_fast64_t, int]
'''


class atomic_intptr_t(PrimitiveType):
    depends = intptr_t
    decl = '''
class atomic_intptr_t(intptr_t):
    pass


_type_atomic_intptr_t = Union[atomic_intptr_t, int]
'''


class atomic_uintptr_t(PrimitiveType):
    depends = uintptr_t
    decl = '''
class atomic_uintptr_t(uintptr_t):
    pass


_type_atomic_uintptr_t = Union[atomic_uintptr_t, int]
'''


class atomic_size_t(PrimitiveType):
    depends = size_t
    decl = '''
class atomic_size_t(size_t):
    pass


_type_atomic_size_t = Union[atomic_size_t, int]
'''


class ptrdiff_t(PrimitiveType):
    depends = intptr_t
    decl = '''
class ptrdiff_t(intptr_t):
    pass


_type_ptrdiff_t = Union[ptrdiff_t, int]
'''


class atomic_ptrdiff_t(PrimitiveType):
    depends = ptrdiff_t
    decl = '''
class atomic_ptrdiff_t(ptrdiff_t):
    pass


_type_atomic_ptrdiff_t = Union[atomic_ptrdiff_t, int]
'''


class intmax_t(PrimitiveType):
    depends = int64_t
    decl = '''
class intmax_t(int64_t):
    pass


_type_intmax_t = Union[intmax_t, int]
'''


class atomic_intmax_t(PrimitiveType):
    depends = intmax_t
    decl = '''
class atomic_intmax_t(intmax_t):
    pass


_type_atomic_intmax_t = Union[atomic_intmax_t, int]
'''


class uintmax_t(PrimitiveType):
    depends = uint64_t
    decl = '''
class uintmax_t(uint64_t):
    pass


_type_uintmax_t = Union[uintmax_t, int]
'''


class atomic_uintmax_t(PrimitiveType):
    depends = uintmax_t
    decl = '''
class atomic_uintmax_t(uintmax_t):
    pass


_type_atomic_uintmax_t = Union[atomic_uintmax_t, int]
'''


PRIMITIVES = {
    '_Bool': bool_t,
    'bool': bool_t,
    'long double': longdouble_t,
    'double': double_t,
    'unsigned char': uchar_t,
    'signed char': char_t,
    'char': char_t,
    'unsigned short int': ushort_t,
    'signed short int': short_t,
    'unsigned short': ushort_t,
    'signed short': short_t,
    'short int': short_t,
    'short': short_t,
    'unsigned long long int': ulonglong_t,
    'signed long long int': longlong_t,
    'unsigned long long': ulonglong_t,
    'signed long long': longlong_t,
    'long long int': longlong_t,
    'long long': longlong_t,
    'unsigned long int': ulong_t,
    'signed long int': long_t,
    'unsigned long': ulong_t,
    'signed long': long_t,
    'long int': long_t,
    'long': long_t,
    'unsigned int': uint_t,
    'signed int': int_t,
    'unsigned': uint_t,
    'signed': int_t,
    'int': int_t,
    'float': float_t,
    '_Atomic _Bool': atomic_bool_t,
    '_Atomic char': atomic_char_t,
    '_Atomic signed char': atomic_schar_t,
    '_Atomic unsigned char': atomic_uchar_t,
    '_Atomic short': atomic_short_t,
    '_Atomic unsigned short': atomic_ushort_t,
    '_Atomic int': atomic_int_t,
    '_Atomic unsigned int': atomic_uint_t,
    '_Atomic long': atomic_long_t,
    '_Atomic unsigned long': atomic_ulong_t,
    '_Atomic long long': atomic_llong_t,
    '_Atomic unsigned long long': atomic_ullong_t,
    '_Atomic char16_t': atomic_char16_t,
    '_Atomic char32_t': atomic_char32_t,
    '_Atomic wchar_t': atomic_wchar_t,
    '_Atomic int_least8_t': atomic_int_least8_t,
    '_Atomic uint_least8_t': atomic_uint_least8_t,
    '_Atomic int_least16_t': atomic_int_least16_t,
    '_Atomic uint_least16_t': atomic_uint_least16_t,
    '_Atomic int_least32_t': atomic_int_least32_t,
    '_Atomic uint_least32_t': atomic_uint_least32_t,
    '_Atomic int_least64_t': atomic_int_least64_t,
    '_Atomic uint_least64_t': atomic_uint_least64_t,
    '_Atomic int_fast8_t': atomic_int_fast8_t,
    '_Atomic uint_fast8_t': atomic_uint_fast8_t,
    '_Atomic int_fast16_t': atomic_int_fast16_t,
    '_Atomic uint_fast16_t': atomic_uint_fast16_t,
    '_Atomic int_fast32_t': atomic_int_fast32_t,
    '_Atomic uint_fast32_t': atomic_uint_fast32_t,
    '_Atomic int_fast64_t': atomic_int_fast64_t,
    '_Atomic uint_fast64_t': atomic_uint_fast64_t,
    '_Atomic intptr_t': atomic_intptr_t,
    '_Atomic uintptr_t': atomic_uintptr_t,
    '_Atomic size_t': atomic_size_t,
    '_Atomic ptrdiff_t': atomic_ptrdiff_t,
    '_Atomic intmax_t': atomic_intmax_t,
    '_Atomic uintmax_t': atomic_uintmax_t,
    'void': void_t
}
