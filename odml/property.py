#-*- coding: utf-8

import odml.base as base
import odml.format as format
import odml.value as odml_value
import odml
from odml.tools.doc_inherit import inherit_docstring, allow_inherit_docstring


class Property(base._baseobj):
    pass


@allow_inherit_docstring
class BaseProperty(base.baseobject, Property):
    """An odML Property"""
    _format = format.Property

    def __init__(self, name, value, definition=None, dependency=None, dependency_value=None):
        """
        Create a new Property with one single or multiple values. If something is passed as value that
        is not a Value object, the method will try to infer the values dtype from the type of the
        parameter.

        Example for a property with a single value
        >>> Property("property1", odml.Value(2)) #or
        >>> Property("property1", 2)

        Example for a property with multiple values
        >>> Property("property2", [odml.Value(data=1), odml.Value(data=2)]) #or
        >>> Property("property2", [1, 2])

        :param name: The mane of the property
        :param value: Either a Value or some type a Value can be created from or a list of values.
        :param definition: The definition of the property.
        :param dependency: Another property this property depends on.
        :param dependency_value: Dependency on a certain value.
        """
        #TODO doc description for arguments
        #TODO validate arguments
        self._name = name
        self._section = None
        self._reset_values()

        self.definition = definition
        self.dependency = dependency
        self.dependency_value = dependency_value

        if isinstance(value, list):
            for v in value:
                if not isinstance(v, odml_value.Value):
                    v = odml.Value(v)
                self.append(v)
        elif value is not None:
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

    def append(self, value):
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
            value = odml.Value(value)
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
