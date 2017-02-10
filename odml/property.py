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
        Create a new Property with one single value. If something is passed as value that
        is not a Value object, the method will try to infer the values dtype from the type of the
        parameter.

        Example for a property with a single value
        >>> Property("property1", odml.Value(2)) #or
        >>> Property("property1", 2)

        :param name: The mane of the property
        :param value: Either a Value or some data a Value can be created from.
        :param definition: The definition of the property.
        :param dependency: Another property this property depends on.
        :param dependency_value: Dependency on a certain value.
        """
        #TODO doc description for arguments
        #TODO validate arguments
        self._name = name
        self._section = None
        self._value = None
        self.definition = definition
        self.dependency = dependency
        self.dependency_value = dependency_value

        if isinstance(value, list) and len(value) > 1:  # FIXME this is a nasty hack
            print("Properties can hold only a single value! A list was passed.")
            self.value = value[0]
        else:
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
    def parent(self):
        """the section containing this property"""
        return self._section

    @property
    def value(self):
        """
        returns the value of this property
        """
        return self._value

    @value.setter
    def value(self, new_value):
        if not isinstance(new_value, odml_value.Value):
            value = odml.Value(new_value)
            self._value = value
        elif new_value is not None:
            self._value = new_value

    # FIXME properties must have a value, unsetting the value will invalidate it. We could have an empty standard
    # FIXME value with an isempty property
    def remove(self, value):
        """
        Remove a value from this property and unset its parent.

        Raises a TypeError if this would cause the property not to hold any value at all.
        This can be circumvented by using the *_values* property.
        """
        #if len(self._values) == 1:
        #    raise TypeError("Cannot remove %s from %s. A property must always have at least one value." % (repr(value), repr(self)))
        # self._values.remove(value)
        # value._property = None
        pass


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

        if children:
            obj.value = self.value.clone()

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
