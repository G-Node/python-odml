#-*- coding: utf8
import odml.dtypes as dtypes
import odml.base as base
import odml.format as format

import string
from odml.tools.doc_inherit import inherit_docstring, allow_inherit_docstring


class Value(base._baseobj):
    pass


@allow_inherit_docstring
class BaseValue(base.baseobject, Value):
    """
    An odML value

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

    definition (optional)
        additional comments on the value of the property

    value
        mandatory (unless data is set). It's the string representation of the value.

    TODO: comment
    """

    _format = format.Value

    def __init__(self, data=None, uncertainty=None, unit=None, dtype=None,
                 definition=None, reference=None, comment=None, value=None):
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
        self._comment = comment

        if value is not None:
            # assign value directly (through property would raise a change-event)
            self._value = dtypes.get(value, self._dtype)
        elif data is not None:
            if dtype is None:
                self._dtype = dtypes.infer_dtype(data)
            self._value = data

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
    def data(self, new_value):
        self._value = new_value

    @property
    def value(self):
        """
        used to access typed data of the value as a string.
        Use data to access the raw type, i.e.:

        >>> v = Value(1, type="float")
        >>> v.data
        1.0
        >>> v.data = 1.5
        >>> v.value
        "1.5"
        >>> v.value = 2
        >>> v.data
        2.0
        """
        return dtypes.set(self._value, self._dtype)

    @value.setter
    def value(self, new_string):
        self._value = dtypes.get(new_string, self._dtype)

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
        if not dtypes.valid_type(new_type):
            raise AttributeError("'%s' is not a valid type." % new_type)
        # we convert the value if possible
        old_type = self._dtype
        old_value = dtypes.set(self._value, self._dtype)
        try:
            new_value = dtypes.get(old_value, new_type)
        except:
            # cannot convert, try the other way around
            try:
                old_value = dtypes.set(self._value, new_type)
                new_value = dtypes.get(old_value, new_type)
            except:
                #doesn't work either, therefore refuse
                raise ValueError("cannot convert '%s' from '%s' to '%s'" % (self.value, old_type, new_type))
        self._value = new_value
        self._dtype = new_type

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
            unprintable = list(filter(lambda x: x not in string.printable,
                                      text))
            if len(unprintable) > 0:
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

        if prop is None:
            return None

        for val in prop:
            if val == self:  # TODO: shouldn't we take the index or st.?
                return val

        return None
