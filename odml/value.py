#-*- coding: utf8
import types
import base
import format

import string
from tools.doc_inherit import *

class Value(base._baseobj):
    pass

@allow_inherit_docstring
class BaseValue(base.baseobject, Value):
    """
    An odML value

    value
        mandatory (unless data is set). It's the string representation of the value.

    data
        mandatory (unless value is set). It's the content itself.
        (see the data and value attributes of this object)

    uncertainty (optional)
        an estimation of the value's uncertainty.

    unit (optional)
        the value's unit

    dtype (optional)
        the data type of the value

    reference (optional)
        an external reference number (e.g. entry in a database)

    filename (optional)
        the default file name which should be used when saving the object

    encoder (encoder)
        binary content must be encoded into ascii to be included in odML files.
        Currently supported is only base64

    checksum (optional)
        if binary content is directly included or if the URL of an external file is given,
        a checksum entry can be used to validate the file's identity, integrity.
        Use this element to indicate the algorithm and the checksum in the format algorithm$checksum
        e.g. crc32$b84892a2 or md5$d41d8cd98f00b204e9800998ecf8427e

    definition (optional)
        additional comments on the value of the property

    TODO: comment
    """

    _format = format.Value

    def __init__(self, value=None, data=None, uncertainty=None, unit=None, dtype=None, definition=None, reference=None, filename=None, encoder=None, checksum=None, comment=None):
        if data is None and value is None:
            raise TypeError("either data or value has to be set")
        if data is not None and value is not None:
            raise TypeError("only one of data or value can be set")

        self._property = None
        self._unit = unit
        self._uncertainty = uncertainty
        self._dtype = dtype
        self._definition = definition
        self._reference = reference
        self._filename = filename
        self._comment = comment
        self._encoder = encoder

        if value is not None:
            # assign value directly (through property would raise a change-event)
            self._value  = types.get(value, self._dtype, self._encoder)
        elif data is not None:
            self._value = data

        self._checksum_type = None
        if checksum is not None:
            self.checksum = checksum

    def __repr__(self):
        if self._dtype:
            return "<%s %s>" % (str(self._dtype), self.get_display())
        return "<%s>" % str(self._value)

    @property
    def parent(self):
        """the property containing this value"""
        return self._property

    @property
    def data(self):
        """
        used to access the raw data of the value
        (i.e. a datetime-object if dtype is "datetime")
        see also the value attribute
        """
        return self._value

    @data.setter
    def data (self, new_value):
        self._value = new_value

    @property
    def value(self):
        """
        used to access typed data of the value as a string.
        Use data to access the raw type, i.e.:

        >>> v = Value("1", type="float")
        >>> v.data
        1.0
        >>> v.data = 1.5
        >>> v.value
        "1.5"
        >>> v.value = 2
        >>> v.data
        2.0
        """
        return types.set(self._value, self._dtype, self._encoder)

    @value.setter
    def value(self, new_string):
        self._value = types.get(new_string, self._dtype, self._encoder)

    @property
    def dtype(self):
        """
        the data type of the value

        If the data type is changed, it is tried, to convert the value to the new type.

        If this doesn't work, the change is refused.
        This behaviour can be overridden by directly accessing the *_dtype* attribute
        and adjusting the *data* attribute manually.
        """
        return self._dtype

    @dtype.setter
    def dtype(self, new_type):
        # check if this is a valid type
        if not types.valid_type(new_type):
            raise AttributeError("'%s' is not a valid type." % (new_type))
        # we convert the value if possible
        old_type  = self._dtype
        old_value = types.set(self._value, self._dtype, self._encoder)
        try:
            new_value = types.get(old_value,  new_type, self._encoder)
        except: # cannot convert, try the other way around
            try:
                old_value = types.set(self._value, new_type, self._encoder)
                new_value = types.get(old_value,   new_type, self._encoder)
            except: #doesn't work either, therefore refuse
                raise ValueError("cannot convert '%s' from '%s' to '%s'" % (self.value, old_type, new_type))
        self._value = new_value
        self._dtype = new_type

    @property
    def encoder(self):
        """
        the encoding of binary data

        changing the encoding also converts the data
        """
        if self._dtype == "binary":
            return self._encoder
        return None

    @encoder.setter
    def encoder(self, encoding):
        if not self._dtype == "binary":
            raise AttributeError("attribute 'encoding' can only be set for binary types, not for '%s'" % self._dtype)

        if not encoding: encoding = None

        if not types.valid_encoding(encoding):
            raise AttributeError("'%s' is not a valid encoding" % encoding)

        # no need to cast anything here, because the encoding
        # effects only the display, not the representation
        self._encoder = encoding

    @property
    def uncertainty(self):
        return self._uncertainty

    @uncertainty.setter
    def uncertainty(self, new_value):
        self._uncertainty = new_value

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, new_value):
        self._unit = new_value

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, new_value):
        self._reference = new_value

    @property
    def definition(self):
        return self._definition

    @definition.setter
    def definition(self, new_value):
        self._definition = new_value

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, new_value):
        self._comment = new_value

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, new_value):
        self._filename = new_value

    @property
    def checksum(self):
        if not self._dtype == "binary":
            return None
        cs_type = self._checksum_type
        if cs_type is None:
            cs_type = "crc32"
        return "%s$%s" % (cs_type, self.calculate_checksum(cs_type))

    @checksum.setter
    def checksum(self, value):
        if not self._dtype == "binary":
            raise AttributeError("attribute 'checksum' can only be set for binary types, not for '%s'" % self._dtype)

        data = value.split("$", 1)
        if not types.valid_checksum_type(data[0]):
            raise AttributeError("unsupported checksum type '%s'" % data[0])
        self._checksum_type = data[0]

    def calculate_checksum(self, cs_type):
        """
        returns the checksum for the data of this Value-object

        *cs_type* is the checksum mechanism (e.g. 'crc32' or 'md5')
        """
        return types.calculate_checksum(self._value, cs_type)

    def can_display(self, text=None, max_length=-1):
        """
        return whether the content of this can be safely displayed in the gui
        """
        if text is None:
            text = self._value
        if text is None:
            return True

        if max_length != -1 and len(text) > max_length:
            return False

        if self._dtype == "binary":
            unprintable = filter(lambda x: x not in string.printable, text)
            if self._encoder is None and len(unprintable) > 0:
                return False

        if "\n" in text or "\t" in text:
            return False

        return True

    def get_display(self, max_length=-1):
        """
        return a textual representation that can be used for display

        typically takes the first line (max *max_length* chars) and adds '…'
        """
        text = self.value
        if self.can_display(text, max_length):
            return text

        text = text.split("\n")[0]
        if max_length != -1:
            text = text[:max_length]
        if self.can_display(text, max_length):
            return text + u'…'

        return "(%d bytes)" % len(self._value)

#    def can_edit(self, max_length=-1)
#        if not self.can_display(self): return False
#
#        return True
#
    @inherit_docstring
    def reorder(self, new_index):
        return self._reorder(self.parent.values, new_index)

    def clone(self):
        obj = super(BaseValue, self).clone()
        obj._property = None
        return obj

    @inherit_docstring
    def get_terminology_equivalent(self):
        prop = self._property.get_terminology_equivalent()
        if prop is None: return None
        for val in prop:
            if val == self: # TODO: shouldn't we take the index or st.?
                return val
        return None
