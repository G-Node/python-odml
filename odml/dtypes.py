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


def default_values(dtype):
    dtype = dtype.lower()
    default_dtype_value = {
        'string': '',
        'text': '',
        'int': 0,
        'float': 0.0,
        'url': '',
        'boolean': False
    }

    if dtype in default_dtype_value:
        return default_dtype_value[dtype]

    if dtype == 'datetime':
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if dtype == 'date':
        return datetime.datetime.now().strftime('%Y-%m-%d')
    if dtype == 'time':
        return datetime.datetime.now().strftime('%H:%M:%S')

    return ''  # Maybe return None ?


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
        # If unable to infer a dtype of given value, return defalt as *string*
        return 'string'


def valid_type(dtype):
    """
    Checks if *dtype* is a valid type
    """
    dtype = dtype.lower()
    if dtype in _dtype_map:
        dtype = _dtype_map[dtype]
    if hasattr(DType, dtype):
        return True
    if dtype is None:
        return True

    return False


def get(string, dtype=None):
    """
    Convert *string* to the corresponding *dtype*
    """
    if not dtype:
        return str_get(string)
    # special case, as the count-number is included in the type-name
    if dtype.endswith("-tuple"):
        return tuple_get(string, int(dtype[:-6]))
    return self.get(dtype + "_get", str_get)(string)


def set(value, dtype=None):
    """
    Serialize a *value* of type *dtype* to a unicode string
    """
    if not dtype:
        return str_set(value)
    if dtype.endswith("-tuple"):
        return tuple_set(value)
    if sys.version_info > (3, 0):
        if isinstance(value, str):
            return str_set(value)
    else:
        if isinstance(value, (str, unicode)):
            return str_set(value)
    return self.get(dtype + "_set", str_set)(value)


def int_get(string):
    if not string:
        return default_values("int")
    try:
        return int(string)
    except ValueError:
        # convert to float first and then cast to int
        return int(float(string))


def float_get(string):
    if not string:
        return default_values("float")
    return float(string)


def str_get(string):
    if not string:
        return default_values("string")
    if sys.version_info < (3, 0):
        return unicode(string)
    return str(string)


# Alias  str_set to str_get. Both perform same function.

str_set = str_get
string_get = str_get
string_set = str_get


def time_get(string):
    if not string:
        return default_values("time")
    if isinstance(string, datetime.time):
        return datetime.datetime.strptime(string.strftime('%H:%M:%S'),
                                          '%H:%M:%S').time()
    else:
        return datetime.datetime.strptime(string, '%H:%M:%S').time()


def time_set(value):
    if not value:
        return default_values("time")
    if isinstance(value, datetime.time):
        return value.strftime("%H:%M:%S")
    return value.isoformat()


def date_get(string):
    if not string:
        return default_values("date")
    if isinstance(string, datetime.date):
        return datetime.datetime.strptime(string.isoformat(),
                                          '%Y-%m-%d').date()
    else:
        return datetime.datetime.strptime(string, '%Y-%m-%d').date()


date_set = time_set


def datetime_get(string):
    if not string:
        return default_values("datetime")
    if isinstance(string, datetime.datetime):
        return datetime.datetime.strptime(string.strftime('%Y-%m-%d %H:%M:%S'),
                                          '%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')


def datetime_set(value):
    if not value:
        return default_values("datetime")
    if isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')


def boolean_get(string):
    if not string:
        return default_values("boolean")
    if isinstance(string, (unicode, str)):
        string = string.lower()
    truth = ["true", "1", True, "t"]  # be kind, spec only accepts True / False
    if string in truth:
        return True
    false = ["false", "0", False, "f"]
    if string in false:
        return False
    # disallow any values that cannot be interpreted as boolean.
    raise ValueError

# Alias boolean_set to boolean_get. Both perform same function.


boolean_set = boolean_get
bool_get = boolean_get
bool_set = boolean_set


def tuple_get(string, count=None):
    """
    Parse a tuple string like "(1024;768)" and return strings of the elements
    """
    if not string:
        return None
    string = string.strip()
    assert string.startswith("(") and string.endswith(")")
    string = string[1:-1]
    res = [x.strip() for x in string.split(";")]
    if count is not None:  # be strict
        assert len(res) == count
    return res


def tuple_set(value):
    if not value:
        return None
    return "(%s)" % ";".join(value)
