#-*- coding: utf-8
import base
import format
import mapping
import value as odml_value
import odml
from tools.doc_inherit import *

class Property(base._baseobj):
    pass

@allow_inherit_docstring
class BaseProperty(base.baseobject, mapping.mapableProperty, Property):
    """An odML Property"""
    _format = format.Property

    def __init__(self, name, value, section=None,
        definition=None, dependency=None, dependency_value=None, mapping=None,
        unit=None, dtype=None, uncertainty=None):
        """
        create a new Property

        *value*
            specifies a direct value that shall be assigned as a first value
            if *value* is a list, the whole list of values will be assigned.
            Further info

                    *unit*
                    the unit of the value(s)

                *dtype*
                    the data type of the value(s)

                *uncertainty*
                    an estimation of uncertainty of the value(s)

        *section*
            the parent section to which this property belongs

         * @param definition {@link String}
         * @param dependency {@link String}
         * @param dependency_value {@link String}
         * @param mapping {@link URL}
        """
        #TODO doc description for arguments
        #TODO validate arguments
        self._name = name
        self._section = section
        self._reset_values()

        self.definition = definition
        self.dependency = dependency
        self.dependency_value = dependency_value
        self._mapping = mapping

        if isinstance(value, list):
            for v in value:
                if not isinstance(v, odml_value.Value):
                    v = odml.Value(v, unit=unit, uncertainty=uncertainty, dtype=dtype)
                self.append(v)
        elif not value is None:
            self.append(value)

        # getter and setter methods are omnitted for now, but they can easily
        # be introduced later using python-properties

    #odML "native" properties
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_value):
        self._name = new_value

    def __repr__(self):
        return "<Property %s>" % self._name


    # API (public)
    #
    #  properties
    @property
    def parent(self):
        """the section containing this property"""
        return self._section

    @property
    def values(self):
        """returns the list of values for this property"""
        return self._values

    @values.setter
    def values(self, new_values):
        # TODO for consistency this actually needs to manually remove each existing value
        self._reset_values()
        for i in new_values:
            self.append(i)

    @property
    def value(self):
        """
        returns the value of this property (or list if multiple values are present)

        use :py:meth:`odml.property.BaseProperty.values` to always return the list
        """
        if len(self._values) == 1:
            return self._values[0]

        #create a copy of the list, so mutations in there won’t affect us:
        return self._values[:]

    @value.setter
    def value(self, new_value):
        self._reset_values()
        self.append(new_value)

    def append(self, value, unit=None, dtype=None, uncertainty=None, copy_attributes=False):
        """
        adds a value to the list of values

        If *value* is not an odml.Value instance, such an instance will be created
        given the addition function arguments (see :ref:`__init__` for their description).

        If *value* is not an odml.Value instance and *unit*, *dtype* or *uncertainty* are
        missing, the values will be copied from the last value in this properties
        value-list if *copy_attributes* is True. If there is no value present to be
        copied from, an IndexError will be raised.
        """
        if not isinstance(value, odml_value.Value):
            if copy_attributes:
                if unit is None: unit = self._values[-1].unit
                if type is None: dtype = self._values[-1].dtype
                if uncertainty is None: uncertainty = self._values[-1].uncertainty
            value = odml.Value(value, unit=unit, dtype=dtype, uncertainty=uncertainty)
        self._values.append(value)
        value._property = self

    def remove(self, value):
        """
        Remove a value from this property and unset its parent.

        Raises a TypeError if this would cause the property not to hold any value at all.
        This can be circumvented by using the *_values* property.
        """
        if len(self._values) == 1:
            raise TypeError("Cannot remove %s from %s. A property must always have at least one value." % (repr(value), repr(self)))
        self._values.remove(value)
        value._property = None

    @inherit_docstring
    def reorder(self, new_index):
        return self._reorder(self.parent.properties, new_index)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return self._values.__iter__()

    def get_path(self):
        """return the absolute path to this object"""
        return self.parent.get_path() + ":" + self.name

    def clone(self, children=True):
        """
        clone this object recursively allowing to copy it independently
        to another document
        """
        obj = super(BaseProperty, self).clone(children)
        obj._section = None

        obj._reset_values()
        if children:
            for v in self._values:
                obj.append(v.clone())

        return obj

    def _reset_values(self):
        """
        reinitialize the list of values with an empty list
        """
        self._values = base.SafeList()

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
        if self._section._merged is None: return None
        return self._section._merged.contains(self)

    @inherit_docstring
    def get_terminology_equivalent(self):
        if self._section is None: return None
        sec = self._section.get_terminology_equivalent()
        if sec is None: return None
        try:
            return sec.properties[self.name]
        except KeyError:
            return None
