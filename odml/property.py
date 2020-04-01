# -*- coding: utf-8
"""
This module provides the Base Property class.
"""
import uuid

from . import base
from . import dtypes
from . import validation
from . import format as frmt
from .tools.doc_inherit import inherit_docstring, allow_inherit_docstring


def odml_tuple_import(t_count, new_value):
    """
    Checks via a heuristic if the values in a string fit the general
    odml style tuple format and the individual items match the
    required number of tuple values.
    Legacy Python2 code required to parse unicode strings to a list
    of odml style tuples.

    :param t_count: integer, required values within a single odml style tuple.
    :param new_value: string containing an odml style tuple list.
    :return: list of odml style tuples.
    """
    try:
        unicode = unicode
    except NameError:
        unicode = str

    if len(new_value) != 1 and not isinstance(new_value[0], unicode):
        return new_value

    cln = new_value[0].strip()
    l_check = cln.startswith("[") and cln.endswith("]")
    br_check = cln.count("(") == cln.count(")")
    com_check = cln.count("(") == (cln.count(",") + 1)
    sep_check = t_count == 1 or cln.count("(") == (cln.count(";") / (t_count - 1))

    if l_check and br_check and com_check and sep_check:
        new_value = cln[1:-1].split(",")

    return new_value


@allow_inherit_docstring
class BaseProperty(base.BaseObject):
    """
    An odML Property.

    If a value without an explicitly stated dtype has been provided, dtype will
    be inferred from the value.

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

    :param name: The name of the Property.
    :param values: Some data value, it can be a single value or
                   a list of homogeneous values.
    :param parent: the parent object of the new Property. If the object is not an
                   odml.Section a ValueError is raised.
    :param unit: The unit of the stored data.
    :param uncertainty: The uncertainty (e.g. the standard deviation)
                        associated with a measure value.
    :param reference: A reference (e.g. an URL) to an external definition
                      of the value.
    :param definition: The definition of the Property.
    :param dependency: Another Property this Property depends on.
    :param dependency_value: Dependency on a certain value.
    :param dtype: The data type of the values stored in the property,
                  if dtype is not given, the type is deduced from the values.
                  Check odml.DType for supported data types.
    :param value_origin: Reference where the value originated from e.g. a file name.
    :param oid: object id, UUID string as specified in RFC 4122. If no id is provided,
               an id will be generated and assigned. An id has to be unique
               within an odML Document.
    :param val_cardinality: Value cardinality defines how many values are allowed for this Property.
                            By default unlimited values can be set.
                            A required number of values can be set by assigning a tuple of the
                            format "(min, max)".
    :param value: Legacy code to the 'values' attribute. If 'values' is provided,
                  any data provided via 'value' will be ignored.
    """

    _format = frmt.Property

    def __init__(self, name=None, values=None, parent=None, unit=None,
                 uncertainty=None, reference=None, definition=None,
                 dependency=None, dependency_value=None, dtype=None,
                 value_origin=None, oid=None, val_cardinality=None, value=None):

        try:
            if oid is not None:
                self._id = str(uuid.UUID(oid))
            else:
                self._id = str(uuid.uuid4())
        except ValueError as exc:
            print(exc)
            self._id = str(uuid.uuid4())

        # Use id if no name was provided.
        if not name:
            name = self._id

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

        self._values = []
        self.values = values
        if not values and (value or isinstance(value, (bool, int))):
            self.values = value

        self.parent = parent

        self._val_cardinality = None
        self.val_cardinality = val_cardinality

        for err in validation.Validation(self).errors:
            if err.is_error:
                msg = "\n\t- %s %s: %s" % (err.obj, err.rank, err.msg)
                print(msg)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, item):
        if int(key) < 0 or int(key) > self.__len__():
            raise IndexError("odml.Property.__setitem__: key %i invalid for "
                             "array of length %i" % (int(key), self.__len__()))
        try:
            val = dtypes.get(item, self.dtype)
            self._values[int(key)] = val
        except Exception:
            raise ValueError("odml.Property.__setitem__:  passed value cannot be "
                             "converted to data type \'%s\'!" % self._dtype)

    def __repr__(self):
        return "Property: {name = %s}" % self._name

    @property
    def oid(self):
        """
        The uuid of the Property. Required for entity creation and comparison,
        saving and loading.
        """
        return self.id

    @property
    def id(self):
        """
        The uuid of the Property.
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
        """
        The name of the Property.
        """
        return self._name

    @name.setter
    def name(self, new_name):
        if self.name == new_name:
            return

        curr_parent = self.parent
        if hasattr(curr_parent, "properties") and new_name in curr_parent.properties:

            raise KeyError("Object with the same name already exists!")

        self._name = new_name

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
        old_values = self._values
        try:
            self._dtype = new_type
            self.values = old_values
        except:
            self._dtype = old_type  # If conversion failed, restore old dtype
            raise ValueError("cannot convert from '%s' to '%s'" %
                             (old_type, new_type))

    @property
    def parent(self):
        """
        The Section containing this Property.
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
        """
        Checks whether a provided object is a valid odml.Section.

        :param new_parent: object to check whether it is an odml.Section.
        :returns: Boolean whether the object is an odml.Section or not.
        """
        from odml.section import BaseSection
        if isinstance(new_parent, BaseSection):
            return True
        return False

    @property
    def value(self):
        """
        Deprecated alias of 'values'. Will be removed with the next minor release.
        """
        print("The attribute 'value' is deprecated. Please use 'values' instead.")
        return self.values

    @value.setter
    def value(self, new_value):
        """
        Deprecated alias of 'values'. Will be removed with the next minor release.

        :param new_value: a single value or list of values.
        """
        print("The attribute 'value' is deprecated. Please use 'values' instead.")
        self.values = new_value

    def value_str(self, index=0):
        """
        Used to access typed data of the value at a specific
        index position as a string.
        """
        return dtypes.set(self._values[index], self._dtype)

    def _validate_values(self, values):
        """
        Method ensures that the passed value(s) can be cast to the
        same dtype, i.e. that are associated with this property or the
        inferred dtype of the first entry of the values list.

        :param values: an iterable that contains the values.
        """
        for val in values:
            try:
                dtypes.get(val, self.dtype)
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

    @property
    def values(self):
        """
        Returns the value(s) stored in this property. Method always returns a list
        that is a copy (!) of the stored value. Changing this list will NOT change
        the property.
        For manipulation of the stored values use the append, extend, and direct
        access methods (using brackets).

        For example:
        >>> p = odml.Property("prop", values=[1, 2, 3])
        >>> print(p.values)
        [1, 2, 3]
        >>> p.values.append(4)
        >>> print(p.values)
        [1, 2, 3]

        Individual values can be accessed and manipulated like this:
        >>> print(p[0])
        [1]
        >>> p[0] = 4
        >>> print(p[0])
        [4]

        The values can be iterated e.g. with a loop:
        >>> for v in p.values:
        >>>   print(v)
        4
        2
        3
        """
        return list(self._values)

    @values.setter
    def values(self, new_value):
        """
        Set the values of the property discarding any previous information.
        Method will try to convert the passed value to the dtype of
        the property and raise a ValueError if not possible.

        :param new_value: a single value or list of values.
        """
        # Make sure boolean value 'False' gets through as well...
        if new_value is None or \
                (isinstance(new_value, (list, tuple, str)) and len(new_value) == 0):
            self._values = []
            return

        new_value = self._convert_value_input(new_value)

        if self._dtype is None:
            self._dtype = dtypes.infer_dtype(new_value[0])

        # Python2 legacy code for loading odml style tuples from YAML or JSON.
        # Works from Python 3 onwards.
        if self._dtype.endswith("-tuple") and not self._validate_values(new_value):
            t_count = int(self._dtype.split("-")[0])
            new_value = odml_tuple_import(t_count, new_value)

        if not self._validate_values(new_value):
            if self._dtype in ("date", "time", "datetime"):
                req_format = dtypes.default_values(self._dtype)
                msg = "odml.Property.values: passed values are not of consistent type "
                msg += "\'%s\'! Format should be \'%s\'." % (self._dtype, req_format)
                raise ValueError(msg)
            else:
                msg = "odml.Property.values: passed values are not of consistent type!"
                raise ValueError(msg)
        self._values = [dtypes.get(v, self.dtype) for v in new_value]

    @property
    def value_origin(self):
        """
        Reference where the value originated from e.g. a file name.
        :returns: the value_origin of the Property.
        """
        return self._value_origin

    @value_origin.setter
    def value_origin(self, new_value):
        if new_value == "":
            new_value = None
        self._value_origin = new_value

    @property
    def uncertainty(self):
        """
        The uncertainty (e.g. the standard deviation) associated with
        the values of the Property.
        :returns: the uncertainty of the Property.
        """
        return self._uncertainty

    @uncertainty.setter
    def uncertainty(self, new_value):
        if new_value == "":
            new_value = None

        if new_value and not isinstance(new_value, (int, float)):
            try:
                new_value = float(new_value)
            except ValueError:
                raise ValueError("odml.Property.uncertainty: passed uncertainty '%s' "
                                 "is not float or int." % new_value)

        self._uncertainty = new_value

    @property
    def unit(self):
        """
        The unit associated with the values of the Property.
        :returns: the unit of the Property.
        """
        return self._unit

    @unit.setter
    def unit(self, new_value):
        if new_value == "":
            new_value = None
        self._unit = new_value

    @property
    def reference(self):
        """
        A reference (e.g. an URL) to an external definition of the value.
        :returns: the reference of the Property.
        """
        return self._reference

    @reference.setter
    def reference(self, new_value):
        if new_value == "":
            new_value = None
        self._reference = new_value

    @property
    def definition(self):
        """
        :returns the definition of the Property:
        """
        return self._definition

    @definition.setter
    def definition(self, new_value):
        if new_value == "":
            new_value = None
        self._definition = new_value

    @property
    def dependency(self):
        """
        Another Property this Property depends on.
        :returns: the dependency of the Property.
        """
        return self._dependency

    @dependency.setter
    def dependency(self, new_value):
        if new_value == "":
            new_value = None
        self._dependency = new_value

    @property
    def dependency_value(self):
        """
        Dependency on a certain value in a dependency Property.
        :returns: the required value to be found in a dependency Property.
        """
        return self._dependency_value

    @dependency_value.setter
    def dependency_value(self, new_value):
        if new_value == "":
            new_value = None
        self._dependency_value = new_value

    @property
    def val_cardinality(self):
        """
        The value cardinality of a Property. It defines how many values
        are minimally required and how many values should be maximally
        stored. Use 'values_set_cardinality' to set.
        """
        return self._val_cardinality

    @val_cardinality.setter
    def val_cardinality(self, new_value):
        """
        Sets the values cardinality of a Property.

        The following cardinality cases are supported:
        (n, n) - default, no restriction
        (d, n) - minimally d entries, no maximum
        (n, d) - maximally d entries, no minimum
        (d, d) - minimally d entries, maximally d entries

        Only positive integers are supported. 'None' is used to denote
        no restrictions on a maximum or minimum.

        :param new_value: Can be either 'None', a positive integer, which will set
                          the maximum or an integer 2-tuple of the format '(min, max)'.
        """
        invalid_input = False

        # Empty values reset the cardinality to None.
        if not new_value or new_value == (None, None):
            self._val_cardinality = None

        # Providing a single integer sets the maximum value in a tuple.
        elif isinstance(new_value, int) and new_value > 0:
            self._val_cardinality = (None, new_value)

        # Only integer 2-tuples of the format '(min, max)' are supported to set the cardinality
        elif isinstance(new_value, tuple) and len(new_value) == 2:
            v_min = new_value[0]
            v_max = new_value[1]

            min_int = isinstance(v_min, int) and v_min >= 0
            max_int = isinstance(v_max, int) and v_max >= 0

            if max_int and min_int and v_max > v_min:
                self._val_cardinality = (v_min, v_max)

            elif max_int and not v_min:
                self._val_cardinality = (None, v_max)

            elif min_int and not v_max:
                self._val_cardinality = (v_min, None)

            else:
                invalid_input = True
        else:
            invalid_input = True

        if invalid_input:
            msg = "Can only assign single int or int-tuples of the format '(min, max)'"
            raise ValueError(msg)

    def set_values_cardinality(self, min_val=None, max_val=None):
        """
        Sets the values cardinality of a Property.

        :param min_val: Required minimal number of values elements. None denotes
                        no restrictions on values elements minimum. Default is None.
        :param max_val: Allowed maximal number of values elements. None denotes
                        no restrictions on values elements maximum. Default is None.
        """
        self.val_cardinality = (min_val, max_val)

    def remove(self, value):
        """
        Remove a value from this property. Only the first encountered
        occurrence of the passed in value is removed from the properties
        list of values.
        """
        if value in self._values:
            self._values.remove(value)

    def get_path(self):
        """
        Return the absolute path to this object.
        """
        if not self.parent:
            return "/"

        return self.parent.get_path() + ":" + self.name

    def clone(self, keep_id=False):
        """
        Clone this property to copy it independently to another document.
        By default the id of the cloned object will be set to a different uuid.

        :param keep_id: If this attribute is set to True, the uuid of the
                        object will remain unchanged.
        :return: The cloned property
        """
        obj = super(BaseProperty, self).clone()
        obj._parent = None
        obj.values = self._values
        if not keep_id:
            obj.new_id()

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
        new_value = self._convert_value_input(source.values)
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

        to_add = [v for v in other.values if v not in self._values]
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
            self.extend(obj.values)
            return

        if self.__len__() == 0:
            self.values = obj
            return

        new_value = self._convert_value_input(obj)
        if len(new_value) > 0 and strict and \
                dtypes.infer_dtype(new_value[0]) != self.dtype:

            type_check = dtypes.infer_dtype(new_value[0])
            if not (type_check == "string" and self.dtype in dtypes.special_dtypes) \
                    and not self.dtype.endswith("-tuple"):
                msg = "odml.Property.extend: passed value data type found "
                msg += "(\"%s\") does not match expected dtype \"%s\"!" % (type_check,
                                                                           self._dtype)
                raise ValueError(msg)

        if not self._validate_values(new_value):
            raise ValueError("odml.Property.extend: passed value(s) cannot be converted "
                             "to data type \'%s\'!" % self._dtype)
        self._values.extend([dtypes.get(v, self.dtype) for v in new_value])

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

        if not self.values:
            self.values = obj
            return

        new_value = self._convert_value_input(obj)
        if len(new_value) > 1:
            raise ValueError("odml.property.append: Use extend to add a list of values!")

        if len(new_value) > 0 and strict and \
                dtypes.infer_dtype(new_value[0]) != self.dtype:

            type_check = dtypes.infer_dtype(new_value[0])
            if not (type_check == "string" and self.dtype in dtypes.special_dtypes) \
                    and not self.dtype.endswith("-tuple"):
                msg = "odml.Property.append: passed value data type found "
                msg += "(\"%s\") does not match expected dtype \"%s\"!" % (type_check,
                                                                           self._dtype)
                raise ValueError(msg)

        if not self._validate_values(new_value):
            raise ValueError("odml.Property.append: passed value(s) cannot be converted "
                             "to data type \'%s\'!" % self._dtype)

        self._values.append(dtypes.get(new_value[0], self.dtype))

    def pprint(self, indent=2, max_length=80, current_depth=-1):
        """
        Pretty print method to visualize Properties and Section-Property trees.

        :param indent: number of leading spaces for every child Property.
        :param max_length: maximum number of characters printed in one line.
        :param current_depth: number of hierarchical levels printed from the
                              starting Section.
        """
        property_spaces = ""
        prefix = ""
        if current_depth >= 0:
            property_spaces = " " * ((current_depth + 2) * indent)
            prefix = "|-"

        if self.unit is None:
            value_string = str(self.values)
        else:
            value_string = "{}{}".format(self.values, self.unit)

        p_len = len(property_spaces) + len(self.name) + len(value_string)
        if p_len >= max_length - 4:
            split_len = int((max_length - len(property_spaces)
                             + len(self.name) - len(prefix))/2)
            str1 = value_string[0: split_len]
            str2 = value_string[-split_len:]
            print(("{}{} {}: {} ... {}".format(property_spaces, prefix,
                                               self.name, str1, str2)))
        else:
            print(("{}{} {}: {}".format(property_spaces, prefix, self.name,
                                        value_string)))

    def export_leaf(self):
        """
        Export only the path from this property to the root.
        Include all properties of parent sections.

        :returns: cloned odml tree to the root of the current document.
        """
        curr = self.parent
        par = self.parent
        child = self.parent

        while curr is not None:
            par = curr.clone(children=False, keep_id=True)
            if curr != self.parent:
                par.append(child)
            if hasattr(curr, 'properties'):
                if curr == self.parent:
                    par.append(self.clone(keep_id=True))
                else:
                    for prop in curr.properties:
                        par.append(prop.clone(keep_id=True))
            child = par
            curr = curr.parent

        return par
