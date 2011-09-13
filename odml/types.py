"""
Provides functionality for validation of the data-types specified
for odml
"""

import sys
self = sys.modules[__name__].__dict__

from datetime import datetime, date, time
import base64

types = ['string', 'int', 'text', 'float', 'URL', 'datetime', 'boolean', 'date', 'binary', 'person', 'time']

def valid_type(dtype):
    """
    checks if *dtype* is a valid type
    """
    if dtype in types: return True
    if dtype is None: return True
    if dtype.endswith("-tuple"):
        try:
            count = int(dtype[:-6])
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
        if not dtype in types:
            if dtype.endswith("-tuple"):
                count = int(dtype[:-6])
                #try to parse it
                tuple_get(string, count=count)
                return True
            return False
        #try to parse it
        self.get(dtype+"_get", str_get)(string)
    except: #any error, this type ain't valid
        return False

def get(string, dtype=None):
    """
    convert *string* to the corresponding *dtype*
    """
    if not dtype: return str_get(string)
    if dtype.endswith("-tuple"): # special case, as the count-number is included in the type-name
        return tuple_get(string)
    return self.get(dtype+"_get", str_get)(string)

def set(value, dtype=None):
    """
    serialize a *value* of type *dtype* to a unicode string
    """
    if not dtype: return str_set(value)
    if dtype.endswith("-tuple"):
        return tuple_set(value)
    return self.get(dtype+"_set", str_set)(value)

def int_get(string):
    if not string: return 0
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
    return datetime.strptime(string, '%H:%M:%S').time()

def time_set(value):
    if not value: return None
    return value.isoformat()

def date_get(string):
    if not string: return None
    return datetime.strptime(string, '%Y-%m-%d').date()

date_set = time_set

def datetime_get(string):
    if not string: return None
    return datetime.strptime(string, '%Y-%m-%d %H:%M:%S')

def datetime_set(value):
    if not value: return None
    return value.isoformat(' ')

def boolean_get(string):
    if not string: return None
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

def binary_get(string):
    "base64decode the data"
    if not string: return None
    return base64.b64decode(string)

def binary_set(value):
    "base64encode the data"
    if not value: return None
    return base64.b64encode(value)

