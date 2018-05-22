# -*- coding: utf-8

import uuid

from . import base
from . import dtypes
from . import format as frmt
from .tools.doc_inherit import inherit_docstring, allow_inherit_docstring


@allow_inherit_docstring
class BaseProperty(base.BaseObject):
    """An odML Property"""
    _format = frmt.Property

    def __init__(self, name=None, value=None, parent=None, unit=None,
                 uncertainty=None, reference=None, definition=None,
                 dependency=None, dependency_value=None, dtype=None,
                 value_origin=None, oid=None):
        """
        Create a new Property. If a value without an explicitly stated dtype
        has been provided, the method will try to infer the value's dtype.
        Example:
        >>> p = Property("property1", "a string")
        >>> p.dtype
        >>> str
        >>> p = Property("property1", 2)
        >>> p.dtype
        >>> int
        >>> p = Property("prop", [2, 3, 4])
        >>> p.dtype
        >>> int
        :param name: The name of the property.
        :param value: Some data value, it can be a single value or
                      a list of homogeneous values.
        :param unit: The unit of the stored data.
        :param uncertainty: The uncertainty (e.g. the standard deviation)
                            associated with a measure value.
        :param reference: A reference (e.g. an URL) to an external definition
                          of the value.
        :param definition: The definition of the property.
        :param dependency: Another property this property depends on.
        :param dependency_value: Dependency on a certain value.
        :param dtype: The data type of the values stored in the property,
                      if dtype is not given, the type is deduced from the values.
                      Check odml.DType for supported data types.
        :param value_origin: Reference where the value originated from e.g. a file name.
        :param oid: object id, UUID string as specified in RFC 4122. If no id is provided,
                   an id will be generated and assigned. An id has to be unique
                   within an odML Document.
        """
        try:
            if oid is not None:
                self._id = str(uuid.UUID(oid))
            else:
                self._id = str(uuid.uuid4())
        except ValueError as e:
            print(e)
            self._id = str(uuid.uuid4())

        # Use id if no name was provided.
        if not name:
            name = self._id

        self._name = name
        self._parent = None
        self._name = name
        self._value_origin = value_origin
        self._unit = unit
        self._uncertainty = uncertainty
        self._reference = reference
        self._definition = definition
        self._dependency = dependency
        self._dependency_value = dependency_value

        self._dtype = None
        if dtypes.valid_type(dtype):
            self._dtype = dtype
        else:
            print("Warning: Unknown dtype '%s'." % dtype)

        self._value = []
        self.value = value

        self.parent = parent

    def __len__(self):
        return len(self._value)

    def __getitem__(self, key):
        return self._value[key]

    def __setitem__(self, key, item):
        if int(key) < 0 or int(key) > self.__len__():
            raise IndexError("odml.Property.__setitem__: key %i invalid for "
                             "array of length %i" % (int(key), self.__len__()))
        try:
            val = dtypes.get(item, self.dtype)
            self._value[int(key)] = val
        except Exception:
            raise ValueError("odml.Property.__setitem__:  passed value cannot be "
                             "converted to data type \'%s\'!" % self._dtype)

    @property
    def oid(self):
        """
        The uuid for the property. Required for entity creation and comparison,
        saving and loading.
        """
        return self.id

    @property
    def id(self):
        """
        The uuid for the property.
        """
        return self._id

    def new_id(self, oid=None):
        """
        new_id sets the object id of the current object to an RFC 4122 compliant UUID.
        If an id was provided, it is assigned if it is RFC 4122 UUID format compliant.
        If no id was provided, a new UUID is generated and assigned.
        :param oid: UUID string as specified in RFC 4122.
        """
        if oid is not None:
            self._id = str(uuid.UUID(oid))
        else:
            self._id = str(uuid.uuid4())

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if self.name == new_name:
            return

        curr_parent = self.parent
        if hasattr(curr_parent, "properties") and new_name in curr_parent.properties:

            raise KeyError("Object with the same name already exists!")

        self._name = new_name

    def __repr__(self):
        return "<Property %s>" % self._name

    @property
    def dtype(self):
        """
        The data type of the value. Check odml.DType for supported data types.
        """
        return self._dtype

    @dtype.setter
    def dtype(self, new_type):
        """
        If the data type of a property value is changed, it is tried
        to convert existing values to the new type. If this doesn't work,
        the change is refused. The dtype can always be changed, if
        a Property does not contain values.
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
        The section containing this property.
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
        """
        Returns the value(s) stored in this property. Method always returns a list
        that is a copy (!) of the stored value. Changing this list will NOT change
        the property.
        For manipulation of the stored values use the append, extend, and direct
        access methods (using brackets).

        For example:
        >>> p = odml.Property("prop", value=[1, 2, 3])
        >>> print(p.value)
        [1, 2, 3]
        >>> p.value.append(4)
        >>> print(p.value)
        [1, 2, 3]

        Individual values can be accessed and manipulated like this:
        >>> print(p[0])
        [1]
        >>> p[0] = 4
        >>> print(p[0])
        [4]

        The values can be iterated e.g. with a loop:
        >>> for v in p.value:
        >>>   print(v)
        4
        2
        3
        """
        return list(self._value)

    def value_str(self, index=0):
        """
        Used to access typed data of the value at a specific
        index position as a string.
        """
        return dtypes.set(self._value[index], self._dtype)

    def _validate_values(self, values):
        """
        Method ensures that the passed value(s) can be cast to the
        same dtype, i.e. that are associated with this property or the
        inferred dtype of the first entry of the values list.

        :param values: an iterable that contains the values.
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

        :return: list of new_value
        """
        if isinstance(new_value, str):
            if new_value[0] == "[" and new_value[-1] == "]":
                new_value = list(map(str.strip, new_value[1:-1].split(",")))
            else:
                new_value = [new_value]
        elif isinstance(new_value, dict):
            new_value = [str(new_value)]
        elif hasattr(new_value, '__iter__') or hasattr(new_value, '__next__'):
            new_value = list(new_value)
        elif not isinstance(new_value, list):
            new_value = [new_value]
        else:
            raise ValueError("odml.Property._convert_value_input: "
                             "unsupported data type for values: %s" % type(new_value))
        return new_value

    @value.setter
    def value(self, new_value):
        """
        Set the value of the property discarding any previous information.
        Method will try to convert the passed value to the dtype of
        the property and raise an ValueError if not possible.

        :param new_value: a single value or list of values.
        """
        # Make sure boolean value 'False' gets through as well...
        if new_value is None or \
                (isinstance(new_value, (list, tuple, str)) and len(new_value) == 0):
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
        if new_value == "":
            new_value = None
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
        Remove a value from this property. Only the first encountered
        occurrence of the passed in value is removed from the properties
        list of values.
        """
        if value in self._value:
            self._value.remove(value)

    def get_path(self):
        """
        Return the absolute path to this object.
        """
        if not self.parent:
            return "/"

        return self.parent.get_path() + ":" + self.name

    def clone(self):
        """
        Clone this object to copy it independently to another document.
        The id of the cloned object will be set to a different uuid.
        """
        obj = super(BaseProperty, self).clone()
        obj._parent = None
        obj.value = self._value
        obj._id = str(uuid.uuid4())

        return obj

    def merge_check(self, source, strict=True):
        """
        Checks whether a source Property can be merged with self as destination and
        raises a ValueError if the values of source and destination are not compatible.
        With parameter *strict=True* a ValueError is also raised, if any of the
        attributes unit, definition, uncertainty, reference or value_origin and dtype
        differ in source and destination.

        :param source: an odML Property.
        :param strict: If True, the attributes dtype, unit, uncertainty, definition,
                       reference and value_origin of source and destination
                       must be identical.
        """
        if not isinstance(source, BaseProperty):
            raise ValueError("odml.Property.merge: odML Property required.")

        # Catch unmerge-able values at this point to avoid
        # failing Section tree merges which cannot easily be rolled back.
        new_value = self._convert_value_input(source.value)
        if not self._validate_values(new_value):
            raise ValueError("odml.Property.merge: passed value(s) cannot "
                             "be converted to data type '%s'!" % self._dtype)
        if not strict:
            return

        if (self.dtype is not None and source.dtype is not None and
                self.dtype != source.dtype):
            raise ValueError("odml.Property.merge: src and dest dtypes do not match!")

        if self.unit is not None and source.unit is not None and self.unit != source.unit:
            raise ValueError("odml.Property.merge: "
                             "src and dest units (%s, %s) do not match!" %
                             (source.unit, self.unit))

        if (self.uncertainty is not None and source.uncertainty is not None and
                self.uncertainty != source.uncertainty):
            raise ValueError("odml.Property.merge: "
                             "src and dest uncertainty both set and do not match!")

        if self.definition is not None and source.definition is not None:
            self_def = ''.join(map(str.strip, self.definition.split())).lower()
            other_def = ''.join(map(str.strip, source.definition.split())).lower()
            if self_def != other_def:
                raise ValueError("odml.Property.merge: "
                                 "src and dest definitions do not match!")

        if self.reference is not None and source.reference is not None:
            self_ref = ''.join(map(str.strip, self.reference.lower().split()))
            other_ref = ''.join(map(str.strip, source.reference.lower().split()))
            if self_ref != other_ref:
                raise ValueError("odml.Property.merge: "
                                 "src and dest references are in conflict!")

        if self.value_origin is not None and source.value_origin is not None:
            self_ori = ''.join(map(str.strip, self.value_origin.lower().split()))
            other_ori = ''.join(map(str.strip, source.value_origin.lower().split()))
            if self_ori != other_ori:
                raise ValueError("odml.Property.merge: "
                                 "src and dest value_origin are in conflict!")

    def merge(self, other, strict=True):
        """
        Merges the Property 'other' into self, if possible. Information
        will be synchronized. By default the method will raise a ValueError when the
        information in this property and the passed property are in conflict.

        :param other: an odML Property.
        :param strict: Bool value to indicate whether types should be implicitly converted
               even when information may be lost. Default is True, i.e. no conversion,
               and a ValueError will be raised if types or other attributes do not match.
               If a conflict arises with strict=False, the attribute value of self will
               be kept, while the attribute value of other will be lost.
        """
        if not isinstance(other, BaseProperty):
            raise TypeError("odml.Property.merge: odml Property required.")

        self.merge_check(other, strict)

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
        self.extend(to_add, strict=strict)

    def unmerge(self, other):
        """
        Stub that doesn't do anything for this class.
        """
        pass

    def get_merged_equivalent(self):
        """
        Return the merged object (i.e. if the parent section is linked to another one,
        return the corresponding property of the linked section) or None.
        """
        if self.parent is None or self.parent._merged is None:
            return None

        return self.parent._merged.contains(self)

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

    def extend(self, obj, strict=True):
        """
        Extend the list of values stored in this property by the passed values. Method
        will raise a ValueError, if values cannot be converted to the current dtype.
        One can also pass another Property to append all values stored in that one.
        In this case units must match!

        :param obj: single value, list of values or a Property.
        :param strict: a Bool that controls whether dtypes must match. Default is True.
        """
        if isinstance(obj, BaseProperty):
            if obj.unit != self.unit:
                raise ValueError("odml.Property.extend: src and dest units (%s, %s) "
                                 "do not match!" % (obj.unit, self.unit))
            self.extend(obj.value)
            return

        if self.__len__() == 0:
            self.value = obj
            return

        new_value = self._convert_value_input(obj)
        if len(new_value) > 0 and strict and dtypes.infer_dtype(new_value[0]) != self.dtype:
            raise ValueError("odml.Property.extend: "
                             "passed value data type does not match dtype!")

        if not self._validate_values(new_value):
            raise ValueError("odml.Property.extend: passed value(s) cannot be converted "
                             "to data type \'%s\'!" % self._dtype)
        self._value.extend([dtypes.get(v, self.dtype) for v in new_value])

    def append(self, obj, strict=True):
        """
        Append a single value to the list of stored values. Method will raise
        a ValueError if the passed value cannot be converted to the current dtype.

        :param obj: the additional value.
        :param strict: a Bool that controls whether dtypes must match. Default is True.
        """
        # Ignore empty values before nasty stuff happens, but make sure
        # 0 and False get through.
        if obj in [None, "", [], {}]:
            return

        if not self.value:
            self.value = obj
            return

        new_value = self._convert_value_input(obj)
        if len(new_value) > 1:
            raise ValueError("odml.property.append: Use extend to add a list of values!")

        if len(new_value) > 0 and strict and dtypes.infer_dtype(new_value[0]) != self.dtype:
            raise ValueError("odml.Property.append: "
                             "passed value data type does not match dtype!")

        if not self._validate_values(new_value):
            raise ValueError("odml.Property.append: passed value(s) cannot be converted "
                             "to data type \'%s\'!" % self._dtype)

        self._value.append(dtypes.get(new_value[0], self.dtype))
