"""
Provides functionality for validation of the data-types specified for odML
"""

import datetime as dt
import re
import sys

from enum import Enum

self = sys.modules[__name__].__dict__

FORMAT_DATE = "%Y-%m-%d"
FORMAT_DATETIME = "%Y-%m-%d %H:%M:%S"
FORMAT_TIME = "%H:%M:%S"


class DType(str, Enum):
    """
    The DType class enumerates all data types supported by odML.
    """
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
    """
    Returns the default value for a provided odml data type.

    :param dtype: odml.DType or string corresponding to an odml data type.
    :returns: default value for an identified odml data type or empty string.
    """
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
        return dt.datetime.now().replace(microsecond=0)
    if dtype == 'date':
        return dt.datetime.now().date()
    if dtype == 'time':
        return dt.datetime.now().replace(microsecond=0).time()

    return ''  # Maybe return None ?


_dtype_map = {'str': 'string', 'bool': 'boolean'}

special_dtypes = ["url", "person", "text"]


def infer_dtype(value):
    """
    Tries to identify the odml data type for a provided value.

    :param value: single value to infer the odml datatype from.
    :returns: The identified dtype name. If it cannot be identified, "string" is returned.
    """
    dtype = (type(value)).__name__
    if dtype in _dtype_map:
        dtype = _dtype_map[dtype]

    if valid_type(dtype):
        if dtype == 'string' and '\n' in value:
            dtype = 'text'
        return dtype

    return 'string'


def valid_type(dtype):
    """
    Checks if *dtype* is a valid odML value data type.

    :param dtype: odml.DType or string corresponding to an odml data type.
    :returns: Boolean.
    """
    if dtype is None:
        return True

    if not isinstance(dtype, str):
        return False

    dtype = dtype.lower()
    if dtype in _dtype_map:
        dtype = _dtype_map[dtype]

    if hasattr(DType, dtype):
        return True

    # Check odML tuple dtype.
    rexp = re.compile("^[1-9][0-9]*-tuple$")
    if len(rexp.findall(dtype)) == 1:
        return True

    return False


def get(string, dtype=None):
    """
    Converts *string* to the corresponding *dtype*.
    The appropriate function is derived from the provided dtype.
    If no dtype is provided, the string conversion function is used by default.

    :param string: string to be converted into an odml specific value.
    :param dtype: odml.DType or string corresponding to an odml data type.
                  If provided it is used to identify the appropriate conversion function.
    :returns: value converted to the appropriate data type.
    """
    if not dtype:
        return str_get(string)
    # special case, as the count-number is included in the type-name
    if dtype.endswith("-tuple"):
        return tuple_get(string, int(dtype[:-6]))
    return self.get(dtype + "_get", str_get)(string)


def set(value, dtype=None):
    """
    Serializes a *value* of type *dtype* to a unicode string.
    The appropriate function is derived from the provided dtype.

    :param value: odml specific value to be converted into a string.
    :param dtype: odml.DType or string corresponding to an odml data type.
                  If provided it is used to identify the appropriate conversion function.
    :returns: value converted to an appropriately formatted string.
    """
    if not dtype:
        return str_set(value)

    if dtype.endswith("-tuple"):
        return tuple_set(value)

    if isinstance(value, str):
        return str_set(value)

    return self.get(dtype + "_set", str_set)(value)


def int_get(string):
    """
    Converts an input string to an integer value. If *string* is empty
    the default value for int is returned.

    :param string: string value to convert to int.
    :return: Integer value.
    """
    if string is None or string == "":
        return default_values("int")

    try:
        return int(string)
    except ValueError:
        # convert to float first and then cast to int
        return int(float(string))


def float_get(string):
    """
    Converts an input string to a float value. If *string* is empty
    the default value for float is returned.

    :param string: string value to convert to int.
    :return: Float value.
    """
    if string is None or string == "":
        return default_values("float")

    return float(string)


def str_get(string):
    """
    Handles an input string value and escapes None and empty collections.

    :param string: value to check for None value or empty collections.
    :return: string value.
    """
    # Do not stringify empty list or dict but make sure boolean False gets through.
    if string in [None, "", [], {}]:
        return default_values("string")

    return str(string)


# Alias  str_set to str_get. Both perform same function.

str_set = str_get
string_get = str_get
string_set = str_get


def time_get(string):
    """
    Checks an input string against the required time format and converts it to
    a time object with the default format. If *string* is empty the default
    value for time is returned.

    :param string: string value to convert to time.
    :return: time object.
    """
    if string is None or string == "":
        return default_values("time")

    if isinstance(string, dt.time):
        return dt.datetime.strptime(string.strftime(FORMAT_TIME), FORMAT_TIME).time()

    return dt.datetime.strptime(string, FORMAT_TIME).time()


time_set = time_get


def date_get(string):
    """
    Checks an input string against the required date format and converts it to
    a date object with the default format. If *string* is empty the default
    value for date is returned.

    :param string: string value to convert to date.
    :return: date object.
    """
    if string is None or string == "":
        return default_values("date")

    if isinstance(string, dt.date):
        return dt.datetime.strptime(string.isoformat(), FORMAT_DATE).date()

    return dt.datetime.strptime(string, FORMAT_DATE).date()


date_set = date_get


def datetime_get(string):
    """
    Checks an input string against the required datetime format and converts
    it to a datetime object with the default format. If *string* is empty the
    default value for datetime is returned.

    :param string: string value to convert to datetime.
    :return: datetime object.
    """
    if string is None or string == "":
        return default_values("datetime")

    if isinstance(string, dt.datetime):
        return dt.datetime.strptime(string.strftime(FORMAT_DATETIME), FORMAT_DATETIME)

    return dt.datetime.strptime(string, FORMAT_DATETIME)


datetime_set = datetime_get


def boolean_get(string):
    """
    Handles an input string value and escapes None and empty collections and
    provides the default boolean value in these cases. String values
    "true", "1", True, "t" are interpreted as boolean True, string values
    "false", "0", False, "f" are interpreted as boolean False.
    A ValueError is raised if the input value cannot be interpreted as boolean.

    :param string: value to convert to boolean.
    :return: boolean value.
    """
    if string in [None, "", [], {}]:
        return default_values("boolean")

    if isinstance(string, str):
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
    Parses a tuple string like "(1024;768)" and return a list of strings with the
    individual tuple elements.

    :param string: string to be parsed into odML style tuples.
    :param count: list of strings.
    """
    if not string:
        return None

    string = string.strip()
    if not (string.startswith("(") and string.endswith(")")):
        msg = "Tuple value misses brackets: '%s'" % string
        raise ValueError(msg)

    string = string[1:-1]
    res = [x.strip() for x in string.split(";")]
    if count is not None and not len(res) == count:
        msg = "%s-tuple value does not match required item length" % count
        raise ValueError(msg)

    return res


def tuple_set(value):
    """
    Serializes odml style tuples to a string representation.

    :param value: odml style tuple values.
    :return: string.
    """
    if not value:
        return None
    return "(%s)" % ";".join(value)
