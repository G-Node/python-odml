import sys
import datetime
from enum import Enum
self = sys.modules[__name__].__dict__

"""
Provides functionality for validation of the data-types specified for odML
"""

try:
    unicode = unicode
except NameError:
    unicode = str


class DType(str, Enum):
    string = 'string'
    text = 'text'
    int = 'int'
    float = 'float'
    url = 'url'
    datetime = 'datetime'
    date = 'date'
    time = 'time'
    boolean = 'boolean'
    person = 'person'

    def __str__(self):
        return self.name

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
    dtype = dtype.lower()
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


def get(string, dtype=None):
    """
    convert *string* to the corresponding *dtype*
    """
    if not dtype:
        return str_get(string)
    if dtype.endswith("-tuple"):  # special case, as the count-number is included in the type-name
        return tuple_get(string)
    return self.get(dtype + "_get", str_get)(string)


def set(value, dtype=None):
    """
    serialize a *value* of type *dtype* to a unicode string
    """
    if not dtype:
        return str_set(value)
    if dtype.endswith("-tuple"):
        return tuple_set(value)
    if sys.version_info > (3, 0):
        if isinstance(value, str):
            return str_set(value)
    else:
        if type(value) in (str, unicode):
            return str_set(value)
    return self.get(dtype + "_set", str_set)(value)


def int_get(string):
    if not string:
        return 0
    try:
        return int(string)
    except ValueError:
        # convert to float first and then cast to int
        return int(float(string))


def float_get(string):
    if not string:
        return 0.0
    return float(string)


def str_get(string):
    if sys.version_info < (3, 0):
        return unicode(string)
    return str(string)


def str_set(value):
    try:
        if sys.version_info < (3, 0):
            return unicode(value)
        else:
            return str(value)
    except Exception as ex:
        fail = ex
        raise fail


def time_get(string):
    if not string:
        return None
    if type(string) is datetime.time:
        return datetime.datetime.strptime(string.strftime('%H:%M:%S'), '%H:%M:%S').time()
    else:
        return datetime.datetime.strptime(string, '%H:%M:%S').time()


def time_set(value):
    if not value:
        return None
    if type(value) is datetime.time:
        return value.strftime("%H:%M:%S")
    return value.isoformat()


def date_get(string):
    if not string:
        return None
    if type(string) is datetime.date:
        return datetime.datetime.strptime(string.isoformat(), '%Y-%m-%d').date()
    else:
        return datetime.datetime.strptime(string, '%Y-%m-%d').date()


date_set = time_set


def datetime_get(string):
    if not string:
        return None
    if type(string) is datetime.datetime:
        return datetime.datetime.strptime(string.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


def datetime_set(value):
    if not value:
        return None
    if type(value) is datetime.datetime:
        return value.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')


def boolean_get(string):
    if string is None:
        return None
    if type(string) is bool:
        string = str(string)
    string = string.lower()
    truth = ["true", "t", "1"] # be kind, spec only accepts True / False
    if string in truth:
        return True
    false = ["false", "f", "0"]
    if string in false:
        return False
    raise ValueError("Cannot interpret '%s' as boolean" % string)


def boolean_set(value):
    if value is None:
        return None
    return str(value)


def tuple_get(string, count=None):
    """
    parse a tuple string like "(1024;768)" and return strings of the elements
    """
    if not string:
        return None
    string = string.strip()
    assert string.startswith("(") and string.endswith(")")
    string = string[1:-1]
    res = string.split(";")
    if count is not None: # be strict
        assert len(res) == count
    return res


def tuple_set(value):
    if not value:
        return None
    return "(%s)" % ";".join(value)

