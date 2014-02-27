"""
Provides functionality for validation of the data-types specified
for odml
"""

import sys

self = sys.modules[__name__].__dict__

import datetime
import binascii
import hashlib
from enum import Enum


class DType(str, Enum):
    string = 'string'
    text = 'text'
    int = 'int'
    float = 'float'
    URL = 'url'
    datetime = 'datetime'
    date = 'date'
    time = 'time'
    boolean = 'boolean'
    person = 'person'
    binary = 'binary'


_dtype_map = {'str': 'string', 'bool': 'boolean'}


def infer_dtype(value):
    dtype = (type(value)).__name__

    if dtype in _dtype_map:
        dtype = _dtype_map[dtype]

    if valid_type(dtype):
        if dtype == 'string' and '\n' in value:
            dtype = 'text'
        return dtype
    else:
        return None


def valid_type(dtype):
    """
    checks if *dtype* is a valid type
    """
    if dtype in _dtype_map:
        dtype = _dtype_map[dtype]

    if hasattr(DType, dtype):
        return True
    if dtype is None:
        return True

    if dtype.endswith("-tuple"):
        try:
            int(dtype[:-6])
            return True
        except ValueError:
            pass

    return False


# TODO also take encoding into account
def validate(string, dtype):
    """
    checks if:

     * *dtype* is a valid type
     * *string* is a valid expression of type *dtype*
    """
    try:
        if not valid_type(dtype):
            if dtype.endswith("-tuple"):
                count = int(dtype[:-6])
                #try to parse it
                tuple_get(string, count=count)
                return True
                #try to parse it
            self.get(dtype + "_get", str_get)(string)
        else:
            return False
    except RuntimeError:
        #any error, this type ain't valid
        return False


def get(string, dtype=None, encoding=None):
    """
    convert *string* to the corresponding *dtype*
    """
    if not dtype: return str_get(string)
    if dtype.endswith("-tuple"): # special case, as the count-number is included in the type-name
        return tuple_get(string)
    if dtype == "binary":
        return binary_get(string, encoding)
    return self.get(dtype + "_get", str_get)(string)


def set(value, dtype=None, encoding=None):
    """
    serialize a *value* of type *dtype* to a unicode string
    """
    if not dtype: return str_set(value)
    if dtype.endswith("-tuple"):
        return tuple_set(value)
    if dtype == "binary":
        return binary_set(value, encoding)
    return self.get(dtype + "_set", str_set)(value)


def int_get(string):
    if not string: return 0
    try:
        return int(string)
    except ValueError:
        # convert to float first and then cast to int
        return int(float(string))


def float_get(string):
    if not string: return 0.0
    return float(string)


def str_get(string):
    return unicode(string)


def str_set(value):
    return unicode(value)


def time_get(string):
    if not string: return None
    if type(string) is datetime.time:
        return datetime.strptime(string.isoformat(), '%H:%M:%S').time()
    else:
        return datetime.strptime(string, '%H:%M:%S').time()


def time_set(value):
    if not value: return None
    return value.isoformat()


def date_get(string):
    if not string: return None
    if type(string) is datetime.date:
        return datetime.datetime.strptime(string.isoformat(), '%Y-%m-%d').date()
    else:
        return datetime.datetime.strptime(string, '%Y-%m-%d').date()


date_set = time_set


def datetime_get(string):
    if not string: return None
    if type(string) is datetime.datetime:
        return datetime.datetime.strptime(string.isoformat(), '%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


def datetime_set(value):
    if not value: return None
    return value.isoformat(' ')


def boolean_get(string):
    if not string: return None
    if type(string) is bool:
        string = str(string)
    string = string.lower()
    truth = ["true", "t", "1"] # be kind, spec only accepts True / False
    if string in truth: return True
    false = ["false", "f", "0"]
    if string in false: return False
    raise ValueError("Cannot interpret '%s' as boolean" % string)


def boolean_set(value):
    if value is None: return None
    return str(value)


def tuple_get(string, count=None):
    """
    parse a tuple string like "(1024;768)" and return strings of the elements
    """
    if not string: return None
    string = string.strip()
    assert string.startswith("(") and string.endswith(")")
    string = string[1:-1]
    res = string.split(";")
    if count is not None: # be strict
        assert len(res) == count
    return res


def tuple_set(value):
    if not value: return None
    return "(%s)" % ";".join(value)

###############################################################################
# Binary Encoding Stuff
###############################################################################

class Encoder(object):
    def __init__(self, encode, decode):
        self._encode = encode
        self._decode = decode

    def encode(self, data):
        return self._encode(data)

    def decode(self, string):
        return self._decode(string)


encodings = {
    'base64': Encoder(lambda x: binascii.b2a_base64(x).strip(), binascii.a2b_base64),
    'quoted-printable': Encoder(binascii.b2a_qp, binascii.a2b_qp),
    'hexadecimal': Encoder(binascii.b2a_hex, binascii.a2b_hex),
    None: Encoder(lambda x: x, lambda x: x), #identity encoder
}


def valid_encoding(encoding):
    return encoding in encodings


def binary_get(string, encoding=None):
    "binary decode the *string* according to *encoding*"
    if not string: return None
    return encodings[encoding].decode(string)


def binary_set(value, encoding=None):
    "binary encode the *value* according to *encoding*"
    if not value: return None
    return encodings[encoding].encode(value)


def calculate_crc32_checksum(data):
    return "%08x" % (binascii.crc32(data) & 0xffffffff)


checksums = {
    'crc32': calculate_crc32_checksum,
}
# allow to use any available algorithm
if not sys.version_info < (2, 7):
    for algo in hashlib.algorithms:
        checksums[algo] = lambda data, func=getattr(hashlib, algo): func(data).hexdigest()


def valid_checksum_type(checksum_type):
    return checksum_type in checksums


def calculate_checksum(data, checksum_type):
    if data is None: data = ''
    return checksums[checksum_type](data)
