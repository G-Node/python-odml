# -*- coding: utf-8

import odml.base as base
import odml.format as frmt
import odml.dtypes as dtypes
from odml.tools.doc_inherit import inherit_docstring, allow_inherit_docstring


class Property(base._baseobj):
    pass


@allow_inherit_docstring
class BaseProperty(base.baseobject, Property):
    """An odML Property"""
    _format = frmt.Property

    def __init__(self, name, value=None, unit=None, uncertainty=None, value_reference=None, definition=None, dependency=None,
                 dependency_value=None, dtype=None):
        """
        Create a new Property with a single value. The method will try to infer the value's dtype from the type of the
        value.

        Example for a property with
        >>> p = Property("property1", "a string")
        >>> p.dtype
        >>> str
        >>> p = Property("property1", 2)
        >>> p.dtype
        >>> int
        >>> p = Property("prop", [2, 3, 4])
        >>> p.dtype
        >>> int
        :param name: The mane of the property
        :param value: Some data value, this may be a list of homogeneous values.
        :param unit: The unit of the stored data.
        :param uncertainty: the uncertainty (e.g. the standard deviation) associated with a measure value.
        :param value_reference: A reference (e.g. an URL) to an external definition of the value.
        :param definition: The definition of the property.
        :param dependency: Another property this property depends on.
        :param dependency_value: Dependency on a certain value.
        :param dtype: the data type of the values stored in the property, if dtype is not given, the type is deduced
        from the values.
        """
        #TODO validate arguments
        self._name = name
        self._section = None
        self._value = []
        self._unit = unit
        self._uncertainty = uncertainty
        self._value_reference = value_reference
        self._definition = definition
        self._dependency = dependency
        self._dependency_value = dependency_value
        self._dtype = dtype
        self.value = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    def __repr__(self):
        return "<Property %s>" % self._name

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
                # doesn't work either, therefore refuse
                raise ValueError("cannot convert '%s' from '%s' to '%s'" % (self.value, old_type, new_type))
        self._value = new_value
        self._dtype = new_type

    @property
    def parent(self):
        """the section containing this property"""
        return self._section

    @property
    def value(self):  # FIXME check the usage of value in the xmlwriter, jsonwriter
        return self._value

    def value_str(self, index=0):
        """
        used to access typed data of the value as a string.
        Use data to access the raw type, i.e.:
        """
        return dtypes.set(self._value[index], self._dtype)

    def _validate_values(self, values):
        """
            Method ensures that the passed value(s) can be cast to the same dtype, i.e. that
            associated with this property or the inferred dtype of the first entry of the values list.
        """
        for v in values:
            try:
                dtypes.get(v, self.dtype)
            except Exception as ex:
                return False
        return True

    @value.setter
    def value(self, new_value):
        if new_value is None:
            return
        if not isinstance(new_value, list):
            new_value = [new_value]
        if len(new_value) == 0:
            return
        nv = new_value[0] if isinstance(new_value, list) else new_value
        if self._dtype is None:
            self._dtype = dtypes.infer_dtype(nv)
        if not self._validate_values(new_value):
            raise ValueError("odml.Property.value: passed values are not of consistent type!")
        self._value = [dtypes.get(v, self.dtype) for v in new_value]

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
    def value_reference(self):
        return self._value_reference

    @value_reference.setter
    def value_reference(self, new_value):
        self._value_reference = new_value

    @property
    def definition(self):
        return self._definition

    @definition.setter
    def definition(self, new_value):
        self._definition = new_value

    @property
    def dependency(self):
        return self._dependency

    @dependency.setter
    def dependency(self, new_value):
        self._dependency = new_value

    @property
    def dependency_value(self):
        return self._dependency_value

    @dependency_value.setter
    def dependency_value(self, new_value):
        self._dependency_value = new_value

    def remove(self, value):
        """
        Remove a value from this property and unset its parent.

        Raises a TypeError if this would cause the property not to hold any value at all.
        This can be circumvented by using the *_values* property.
        """
        if value in self._value:
            self._value.remove(value)
        pass

    def get_path(self):
        """return the absolute path to this object"""
        return self.parent.get_path() + ":" + self.name

    def clone(self):
        """
        clone this object to copy it independently
        to another document
        """
        obj = super(BaseProperty, self).clone()
        obj._section = None
        obj.value = self.value
        return obj

    def merge(self, property):
        """stub that doesn't do anything for this class"""
        pass

    def unmerge(self, property):
        """stub that doesn't do anything for this class"""
        pass

    def get_merged_equivalent(self):
        """
        return the merged object (i.e. if the section is linked to another one,
        return the corresponding property of the linked section) or None
        """
        if self._section._merged is None:
            return None
        return self._section._merged.contains(self)

    @inherit_docstring
    def get_terminology_equivalent(self):
        if self._section is None:
            return None
        sec = self._section.get_terminology_equivalent()
        if sec is None:
            return None
        try:
            return sec.properties[self.name]
        except KeyError:
            return None

    def __len__(self):
        return len(self._value)

    def __getitem__(self, key):
        return self._value[key]
