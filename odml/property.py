# -*- coding: utf-8

import uuid

from . import base
from . import dtypes
from . import format as frmt
from .tools.doc_inherit import inherit_docstring, allow_inherit_docstring


class Property(base._baseobj):
    pass


@allow_inherit_docstring
class BaseProperty(base.baseobject, Property):
    """An odML Property"""
    _format = frmt.Property

    def __init__(self, name, value=None, parent=None, unit=None,
                 uncertainty=None, reference=None, definition=None,
                 dependency=None, dependency_value=None, dtype=None,
                 value_origin=None, id=None):
        """
        Create a new Property with a single value. The method will try to infer
        the value's dtype from the type of the value if not explicitly stated.
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
        :param name: The name of the property
        :param value: Some data value, this may be a list of homogeneous values
        :param unit: The unit of the stored data.
        :param uncertainty: the uncertainty (e.g. the standard deviation)
                            associated with a measure value.
        :param reference: A reference (e.g. an URL) to an external definition
                          of the value.
        :param definition: The definition of the property.
        :param dependency: Another property this property depends on.
        :param dependency_value: Dependency on a certain value.
        :param dtype: the data type of the values stored in the property,
                     if dtype is not given, the type is deduced from the values
        :param value_origin: Reference where the value originated from e.g. a file name.
        """
        # TODO validate arguments
        try:
            if id is not None:
                self._id = str(uuid.UUID(id))
            else:
                self._id = str(uuid.uuid4())
        except ValueError as e:
            print(e)
            self._id = str(uuid.uuid4())
        self._name = name
        self._parent = None
        self._value = []
        self._value_origin = value_origin
        self._unit = unit
        self._uncertainty = uncertainty
        self._reference = reference
        self._definition = definition
        self._dependency = dependency
        self._dependency_value = dependency_value
        self._dtype = dtype
        self.value = value
        self.parent = parent

    @property
    def id(self):
        return self._id

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
        The data type of the value
        """
        return self._dtype

    @dtype.setter
    def dtype(self, new_type):
        """
        If the data type of a property value is changed, it is tried
        to convert the value to the new type.
        If this doesn't work, the change is refused.

        This behaviour can be overridden by directly accessing the *_dtype*
        attribute and adjusting the *data* attribute manually.
        """
        # check if this is a valid type
        if not dtypes.valid_type(new_type):
            raise AttributeError("'%s' is not a valid type." % new_type)
        # we convert the value if possible
        old_type = self._dtype
        old_values = self._value
        try:
            self._dtype = new_type
            self.value = old_values
        except:
            self._dtype = old_type  # If conversion failed, restore old dtype
            raise ValueError("cannot convert from '%s' to '%s'" %
                             (old_type, new_type))

    @property
    def parent(self):
        """
        The section containing this property
        """
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        if new_parent is None and self._parent is None:
            return
        elif new_parent is None and self._parent is not None:
            self._parent.remove(self)
            self._parent = None
        elif self._validate_parent(new_parent):
            if self._parent is not None:
                self._parent.remove(self)
            self._parent = new_parent
            self._parent.append(self)
        else:
            raise ValueError(
                "odml.Property.parent: passed value is not of consistent type!"
                "odml.Section expected")

    @staticmethod
    def _validate_parent(new_parent):
        from odml.section import BaseSection
        if isinstance(new_parent, BaseSection):
            return True
        return False

    @property
    def value(self):
        return self._value.copy()

    def value_str(self, index=0):
        """
        Used to access typed data of the value as a string.
        Use data to access the raw type, i.e.:
        """
        return dtypes.set(self._value[index], self._dtype)

    def _validate_values(self, values):
        """
            Method ensures that the passed value(s) can be cast to the
            same dtype, i.e. that associated with this property or the
            inferred dtype of the first entry of the values list.
        """
        for v in values:
            try:
                dtypes.get(v, self.dtype)
            except Exception:
                return False
        return True

    def _convert_value_input(self, new_value):
        """
        This method ensures, that the passed new value is a list.
        If new_value is a string, it will convert it to a list of
        strings if the new_value contains embracing brackets.

        returns list of new_value
        """
        if isinstance(new_value, str):
            if new_value[0] == "[" and new_value[-1] == "]":
                new_value = new_value[1:-1].split(",")
        if not isinstance(new_value, list):
            new_value = [new_value]
        return new_value

    @value.setter
    def value(self, new_value):
        # Make sure boolean value 'False' gets through as well...
        if new_value is None or (isinstance(new_value, (list, tuple, str)) and len(new_value) == 0):
            self._value = []
            return

        new_value = self._convert_value_input(new_value)

        if self._dtype is None:
            self._dtype = dtypes.infer_dtype(new_value[0])

        if not self._validate_values(new_value):
            raise ValueError("odml.Property.value: passed values are not of "
                             "consistent type!")
        self._value = [dtypes.get(v, self.dtype) for v in new_value]

    @property
    def value_origin(self):
        return self._value_origin

    @value_origin.setter
    def value_origin(self, new_value):
        if new_value == "":
            new_value = None
        self._value_origin = new_value

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
        if new_value == "":
            new_value = None
        self._unit = new_value

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, new_value):
        if new_value == "":
            new_value = None
        self._reference = new_value

    @property
    def definition(self):
        return self._definition

    @definition.setter
    def definition(self, new_value):
        if new_value == "":
            new_value = None
        self._definition = new_value

    @property
    def dependency(self):
        return self._dependency

    @dependency.setter
    def dependency(self, new_value):
        if new_value == "":
            new_value = None
        self._dependency = new_value

    @property
    def dependency_value(self):
        return self._dependency_value

    @dependency_value.setter
    def dependency_value(self, new_value):
        if new_value == "":
            new_value = None
        self._dependency_value = new_value

    def remove(self, value):
        """
        Remove a value from this property and unset its parent.
        Raises a TypeError if this would cause the property not to hold any
        value at all. This can be circumvented by using the *_values* property.
        """
        if value in self._value:
            self._value.remove(value)

    def get_path(self):
        """
        Return the absolute path to this object
        """
        return self.parent.get_path() + ":" + self.name

    def clone(self):
        """
        Clone this object to copy it independently
        to another document
        """
        obj = super(BaseProperty, self).clone()
        obj._section = None
        obj.value = self._value
        return obj

    def merge(self, other):
        """
        Merges the property 'other' into self, if possible.
        """
        assert(isinstance(other, (BaseProperty)))

        if self.unit is not None and other.unit is not None and self.unit != other.unit:
            raise ValueError("odml.Property.merge: src and dest units (%s, %s) do not match!"
                             % (other.unit, self.unit))

        if self.definition is not None and other.definition is not None:
            self_def = ''.join(map(str.strip, self.definition.split())).lower()
            other_def = ''.join(map(str.strip, other.definition.split())).lower()
            if self_def != other_def:
                raise ValueError("odml.Property.merge: src and dest definitions do not match!")

        if self.uncertainty is not None and other.uncertainty is not None:
            raise ValueError("odml.Property.merge: src and dest uncertainty both set and do not match!")

        if self.reference is not None and other.reference is not None:
            self_ref = ''.join(map(str.strip, self.reference.lower().split()))
            other_ref = ''.join(map(str.strip, other.reference.lower().split()))
            if self_ref != other_ref:
                raise ValueError("odml.Property.merge: src and dest references are in conflict!")

        if self.value_origin is not None and other.value_origin is not None:
            self_ori = ''.join(map(str.strip, self.value_origin.lower().split()))
            other_ori = ''.join(map(str.strip, other.value_origin.lower().split()))
            if self_ori != other_ori:
                raise ValueError("odml.Property.merge: src and dest value_origin are in conflict!")

        if self.value_origin is None and other.value_origin is not None:
            self.value_origin = other.value_origin
        if self.uncertainty is None and other.uncertainty is not None:
            self.uncertainty = other.uncertainty
        if self.reference is None and other.reference is not None:
            self.reference = other.reference
        if self.definition is None and other.definition is not None:
            self.definition = other.definition
        if self.unit is None and other.unit is not None:
            self.unit = other.unit

        to_add = [v for v in other.value if v not in self._value]
        self.append(to_add)

    def unmerge(self, other):
        """
        Stub that doesn't do anything for this class
        """
        pass

    def get_merged_equivalent(self):
        """
        Return the merged object (i.e. if the section is linked to another one,
        return the corresponding property of the linked section) or None
        """
        if self._parent._merged is None:
            return None
        return self._parent._merged.contains(self)

    @inherit_docstring
    def get_terminology_equivalent(self):
        if self._parent is None:
            return None
        sec = self._parent.get_terminology_equivalent()
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

    def append(self, obj):
        if isinstance(obj, BaseProperty):
            if (obj.unit != self.unit):
                raise ValueError("odml.Property.append: src and dest units (%s, %s) do not match!"
                                 % (obj.unit, self.unit))
            self.append(list(obj.value))
            return
        if self._value == []:
            self.value = obj
        else:
            new_value = self._convert_value_input(obj)
            if not self._validate_values(new_value):
                raise ValueError("odml.Property.append: passed value(s) cannot be converted to "
                                 "data type \'%s\'!" % self._dtype)
            self._value.extend([dtypes.get(v, self.dtype) for v in new_value])

