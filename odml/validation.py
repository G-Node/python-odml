# -*- coding: utf-8
"""
Generic odML validation framework.
"""

import re

from enum import Enum

from . import dtypes

try:
    unicode = unicode
except NameError:
    unicode = str

LABEL_ERROR = 'error'
LABEL_WARNING = 'warning'


class IssueID(Enum):
    """
    IDs identifying registered validation handlers.
    """
    unspecified = 1

    # Required attributes validations
    object_required_attributes = 101
    section_type_must_be_defined = 102

    # Unique id, name and type validations
    section_unique_ids = 200
    property_unique_ids = 201
    section_unique_name_type = 202
    property_unique_name = 203

    # Good form validations
    object_name_readable = 300

    # Property specific validations
    property_terminology_check = 400
    property_dependency_check = 401
    property_values_check = 402
    property_values_string_check = 403

    # Cardinality validations
    section_properties_cardinality = 500
    section_sections_cardinality = 501
    property_values_cardinality = 502

    # Optional validations
    section_repository_present = 600

    # Custom validation
    custom_validation = 701


class ValidationError(object):
    """
    Represents an error found in the validation process.

    The error is bound to an odML-object (*obj*) or a list of those and contains
    a message and a rank which may be one of: 'error', 'warning'.
    """

    def __init__(self, obj, msg, rank=LABEL_ERROR, validation_id=None):
        self.obj = obj
        self.msg = msg
        self.rank = rank
        self.validation_id = validation_id

    @property
    def is_warning(self):
        """
        :returns: Boolean whether the current ValidationError has rank 'Warning'.
        """
        return self.rank == LABEL_WARNING

    @property
    def is_error(self):
        """
        :returns: Boolean whether the current ValidationError has rank 'Error'.
        """
        return self.rank == LABEL_ERROR

    @property
    def path(self):
        """
        :returns: The absolute path to the odml object the ValidationError is bound to.
        """
        return self.obj.get_path()

    def __repr__(self):
        # Cleanup the odml object print strings
        print_str = unicode(self.obj).split()[0].split("[")[0].split(":")[0]
        # Document has no name attribute and should not print id or name info
        if hasattr(self.obj, "name"):
            if self.obj.name and self.obj.name != self.obj.id:
                print_str = "%s[%s]" % (print_str, self.obj.name)
            else:
                print_str = "%s[%s]" % (print_str, self.obj.id)
        return "Validation%s: %s '%s'" % (self.rank.capitalize(), print_str, self.msg)


class Validation(object):
    """
    Validation provides a set of default validations that can used to validate
    odml objects. Custom validations can be added via the 'register_handler' method.

    :param obj: odml object the validation will be applied to.
    """

    _handlers = {}

    @staticmethod
    def register_handler(klass, handler):
        """
        Adds a validation handler for an odml class. The handler is called in the
        validation process for each corresponding object.
        The *handler* is assumed to be a generator function yielding
        all ValidationErrors it finds.

        Section handlers are only called for sections and not for the document node.
        If both are required, the handler needs to be registered twice.

        :param klass: string corresponding to an odml class. Valid strings are
                      'odML', 'section' and 'property'.
        :param handler: validation function applied to the odml class.
        """
        Validation._handlers.setdefault(klass, set()).add(handler)

    def __init__(self, obj, validate=True, reset=False):
        self.obj = obj  # may also be a section
        self.errors = []

        # If initialized with reset=True, reset all handlers and
        # do not run any validation yet to allow custom Validation objects.
        if reset:
            self._handlers = {}
            return

        if validate:
            self.run_validation()

    def validate(self, obj):
        """
        Runs all registered handlers that are applicable to a provided odml class instance.
        Occurring validation errors will be collected in the Validation.error attribute.

        :param obj: odml class instance.
        """
        handlers = self._handlers.get(obj.format().name, [])
        for handler in handlers:
            for err in handler(obj):
                self.error(err)

    def error(self, validation_error):
        """
        Registers an error found during the validation process.
        """
        self.errors.append(validation_error)

    def run_validation(self):
        """
        Runs a clean new validation on the registered Validation object.
        """
        self.errors = []

        self.validate(self.obj)

        if self.obj.format().name == "property":
            return

        for sec in self.obj.itersections(recursive=True):
            self.validate(sec)
            for prop in sec.properties:
                self.validate(prop)

    def report(self):
        """
        Validates the registered object and returns a results report.
        """
        self.run_validation()

        err_count = 0
        reduce = set()
        sec_count = 0
        prop_count = 0

        for i in self.errors:
            if i.is_error:
                err_count += 1

            if i.obj not in reduce and 'section' in str(i.obj).lower():
                sec_count += 1
            elif i.obj not in reduce and 'property' in str(i.obj).lower():
                prop_count += 1

            reduce.add(i.obj)

        warn_count = len(self.errors) - err_count
        msg = ""
        if err_count or warn_count:
            msg = "Validation found %s errors and %s warnings" % (err_count, warn_count)
            msg += " in %s Sections and %s Properties." % (sec_count, prop_count)

        return msg

    def register_custom_handler(self, klass, handler):
        """
        Adds a validation handler for an odml class. The handler is called in the
        validation process for each corresponding object.
        The *handler* is assumed to be a generator function yielding
        all ValidationErrors it finds.

        Section handlers are only called for sections and not for the document node.
        If both are required, the handler needs to be registered twice.

        :param klass: string corresponding to an odml class. Valid strings are
                      'odML', 'section' and 'property'.
        :param handler: validation function applied to the odml class.
        """
        self._handlers.setdefault(klass, set()).add(handler)

    def __getitem__(self, obj):
        """
        Return a list of the errors for a certain object.
        """
        errors = []
        for err in self.errors:
            if err.obj is obj:
                errors.append(err)
        return errors


# ------------------------------------------------
# validation rules

def object_required_attributes(obj):
    """
    Tests that no Object has undefined attributes, given in format.

    :param obj: document, section or property.
    """
    validation_id = IssueID.object_required_attributes

    args = obj.format().arguments
    for arg in args:
        if arg[1] == 1:
            msg = "Missing required attribute '%s'" % (arg[0])
            if not hasattr(obj, arg[0]):
                yield ValidationError(obj, msg, LABEL_ERROR, validation_id)
                continue
            obj_arg = getattr(obj, arg[0])
            if not obj_arg and not isinstance(obj_arg, bool):
                yield ValidationError(obj, msg, LABEL_ERROR, validation_id)


Validation.register_handler('odML', object_required_attributes)
Validation.register_handler('section', object_required_attributes)
Validation.register_handler('property', object_required_attributes)


def section_type_must_be_defined(sec):
    """
    Tests that no Section has an unspecified type and adds a warning otherwise.

    :param sec: odml.Section.
    """
    validation_id = IssueID.section_type_must_be_defined

    if sec.type and sec.type == "n.s.":
        yield ValidationError(sec, "Section type not specified", LABEL_WARNING, validation_id)


Validation.register_handler('section', section_type_must_be_defined)


# The Section repository present is no longer part of the default validation
# and should be added on demand.
def section_repository_present(sec):
    """
    1. warn, if a section has no repository or
    2. the section type is not present in the repository
    """
    validation_id = IssueID.section_repository_present

    repo = sec.get_repository()
    if repo is None:
        msg = "A section should have an associated repository"
        yield ValidationError(sec, msg, LABEL_WARNING, validation_id)
        return

    try:
        tsec = sec.get_terminology_equivalent()
    except Exception as exc:
        msg = "Could not load terminology: %s" % exc
        yield ValidationError(sec, msg, LABEL_WARNING, validation_id)
        return

    if tsec is None:
        msg = "Section type '%s' not found in terminology" % sec.type
        yield ValidationError(sec, msg, LABEL_WARNING, validation_id)


def document_unique_ids(doc):
    """
    Traverse an odML Document and check whether all
    assigned ids are unique within the document.

    Yields all duplicate odML object id entries that are encountered.

    :param doc: odML document
    """
    id_map = {doc.id: "Document '%s'" % doc.get_path()}
    for i in section_unique_ids(doc, id_map):
        yield i


def section_unique_ids(parent, id_map=None):
    """
    Traverse a parent (odML Document or Section)
    and check whether all assigned ids are unique.

    A "id":"odML object / path" dictionary of additional 'to-be-excluded' ids may be
    handed in via the *id_map* attribute.

    Yields all duplicate odML object id entries that are encountered.

    :param parent: odML Document or Section
    :param id_map: "id":"odML object / path" dictionary
    """
    validation_id = IssueID.section_unique_ids

    if not id_map:
        id_map = {}

    for sec in parent.sections:
        for i in property_unique_ids(sec, id_map):
            yield i

        if sec.id in id_map:
            msg = "Duplicate id in Section '%s' and %s" % (sec.get_path(), id_map[sec.id])
            yield ValidationError(sec, msg, validation_id=validation_id)
        else:
            id_map[sec.id] = "Section '%s'" % sec.get_path()

        for i in section_unique_ids(sec, id_map):
            yield i


def property_unique_ids(section, id_map=None):
    """
    Checks whether all ids assigned to the odML Properties of an odML Section are unique.

    A "id":"odML object / path" dictionary of additional 'to-be-excluded' ids may be
    handed in via the *id_map* attribute.

    Yields all duplicate odML object id entries that are encountered.

    :param section: odML Section
    :param id_map: "id":"odML object / path" dictionary
    """
    validation_id = IssueID.property_unique_ids

    if not id_map:
        id_map = {}

    for prop in section.properties:
        if prop.id in id_map:
            msg = "Duplicate id in Property '%s' and %s" % (prop.get_path(),
                                                            id_map[prop.id])
            yield ValidationError(prop, msg, validation_id=validation_id)
        else:
            id_map[prop.id] = "Property '%s'" % prop.get_path()


Validation.register_handler('odML', document_unique_ids)


def object_unique_names(obj, validation_id, children, attr=lambda x: x.name,
                        msg="Object names must be unique"):
    """
    Tests that object names within a Section are unique.

    :param obj: odml class instance the validation is applied on.
    :param validation_id: id of the
    :param children: a function that returns the children to be considered.
           Required when handling Sections.
    :param attr: a function that returns the attribute that needs to be unique.
    :param msg: error message that will be registered with a ValidationError.
    """
    names = set(map(attr, children(obj)))
    if len(names) == len(children(obj)):
        return

    names = set()
    for i in children(obj):
        if attr(i) in names:
            yield ValidationError(i, msg, LABEL_ERROR, validation_id)
        names.add(attr(i))


def section_unique_name_type(obj):
    """
    Tests that the values of names and types within the scope of a Section are unique.

    :param obj: odml class instance the validation is applied on.
    """
    for i in object_unique_names(
            obj,
            validation_id=IssueID.section_unique_name_type,
            attr=lambda x: (x.name, x.type),
            children=lambda x: x.sections,
            msg="name/type combination must be unique"):
        yield i


def property_unique_names(obj):
    """
    Tests that the values of Property names within the scope of a Section are unique.

    :param obj: odml class instance the validation is applied on.
    """
    for i in object_unique_names(obj,
                                 validation_id=IssueID.property_unique_name,
                                 children=lambda x: x.properties):
        yield i


Validation.register_handler('odML', section_unique_name_type)
Validation.register_handler('section', section_unique_name_type)
Validation.register_handler('section', property_unique_names)


def object_name_readable(obj):
    """
    Tests if object name is easily readable, so not equal to id.

    :param obj: odml.Section or odml.Property.
    """
    validation_id = IssueID.object_name_readable

    if obj.name == obj.id:
        yield ValidationError(obj, "Name not assigned", LABEL_WARNING, validation_id)


Validation.register_handler('section', object_name_readable)
Validation.register_handler('property', object_name_readable)


def property_terminology_check(prop):
    """
    1. warn, if there are properties that do not occur in the terminology.
    2. warn, if there are multiple values with different units or the unit does
       not match the one in the terminology.
    """
    validation_id = IssueID.property_terminology_check

    if not prop.parent:
        return

    tsec = prop.parent.get_terminology_equivalent()
    if tsec is None:
        return
    try:
        tsec.properties[prop.name]
    except KeyError:
        msg = "Property '%s' not found in terminology" % prop.name
        yield ValidationError(prop, msg, LABEL_WARNING, validation_id)


Validation.register_handler('property', property_terminology_check)


def property_dependency_check(prop):
    """
    Produces a warning if the dependency attribute refers to a non-existent attribute
    or the dependency_value does not match.
    """
    validation_id = IssueID.property_dependency_check

    if not prop.parent:
        return

    dep = prop.dependency
    if dep is None:
        return

    try:
        dep_obj = prop.parent[dep]
    except KeyError:
        msg = "Property refers to a non-existent dependency object"
        yield ValidationError(prop, msg, LABEL_WARNING, validation_id)
        return

    if prop.dependency_value not in dep_obj.values[0]:
        msg = "Dependency-value is not equal to value of the property's dependency"
        yield ValidationError(prop, msg, LABEL_WARNING, validation_id)


Validation.register_handler('property', property_dependency_check)


def property_values_check(prop):
    """
    Tests that the values are of consistent dtype.
    If dtype is not given, infer from first item in list.

    :param prop: property the validation is applied on.
    """
    validation_id = IssueID.property_values_check

    if prop.dtype is not None and prop.dtype != "":
        dtype = prop.dtype
    elif prop.values:
        dtype = dtypes.infer_dtype(prop.values[0])
    else:
        return

    for val in prop.values:
        if dtype.endswith("-tuple"):
            tuple_len = int(dtype[:-6])
            if len(val) != tuple_len:
                msg = "Tuple of length %s not consistent with dtype %s!" % (len(val), dtype)
                yield ValidationError(prop, msg, LABEL_WARNING, validation_id)
        else:
            try:
                dtypes.get(val, dtype)
            except ValueError:
                msg = "Property values not of consistent dtype!"
                yield ValidationError(prop, msg, LABEL_WARNING, validation_id)


Validation.register_handler('property', property_values_check)


def property_values_string_check(prop):
    """
    PROTOTYPE

    Tests whether values with dtype "string" are maybe of different dtype.

    :param prop: property the validation is applied on.
    """
    validation_id = IssueID.property_values_string_check

    if prop.dtype != "string" or not prop.values:
        return

    dtype_checks = {
        'int': r'^(-+)?\d+$',
        'date': r'^\d{2,4}-\d{1,2}-\d{1,2}$',
        'datetime': r'^\d{2,4}-\d{1,2}-\d{1,2} \d{2}:\d{2}(:\d{2})?$',
        'time': r'^\d{2}:\d{2}(:\d{2})?$',
        'float': r'^(-+)?\d+\.\d+$',
        'tuple': r'^\((.*?)\)',
        'boolean': r'^TRUE|FALSE|True|False|t|f+$',
        'text': r'[\r\n]'}

    val_dtypes = []

    for val in prop.values:
        curr_dtype = "string"

        for check_dtype in dtype_checks.items():
            if bool(re.compile(check_dtype[1]).match(val.strip())):
                if check_dtype[0] == "tuple" and val.count(';') > 0:
                    curr_dtype = str(val.count(';') + 1) + "-" + check_dtype[0]
                else:
                    curr_dtype = check_dtype[0]
                break
            if check_dtype[0] == "text" and len(re.findall(check_dtype[1], val.strip())) > 0:
                curr_dtype = check_dtype[0]
                break

        val_dtypes += [curr_dtype]

    res_dtype = max(set(val_dtypes), key=val_dtypes.count)

    if len(set(val_dtypes)) > 1:
        res_dtype = "string"

    if res_dtype != "string":
        msg = 'Dtype of property "%s" currently is "string", but might fit dtype "%s"!' % \
              (prop.name, res_dtype)
        yield ValidationError(prop, msg, LABEL_WARNING, validation_id)


Validation.register_handler('property', property_values_string_check)


def _cardinality_validation(obj, cardinality, card_target_attr, validation_rank, validation_id):
    """
    Helper function that validates the cardinality of an odml object attribute.
    Valid object-attribute combinations are Section-sections, Section-properties and
    Property-values.

    :param obj: an odml.Section or an odml.Property
    :param cardinality: 2-int tuple containing the cardinality value
    :param card_target_attr: string containing the name of the attribute the cardinality is
                             applied against. Supported values are:
                             'sections', 'properties' or 'values'
    :param validation_rank: Rank of the yielded ValidationError.
    :param validation_id: string containing the id of the parent validation.

    :return: Returns a ValidationError, if a set cardinality is not met or None.
    """
    err = None
    if cardinality and isinstance(cardinality, tuple):

        val_min = cardinality[0]
        val_max = cardinality[1]

        card_target = getattr(obj, card_target_attr)
        val_len = len(card_target) if card_target else 0

        invalid_cause = ""
        if val_min and val_len < val_min:
            invalid_cause = "minimum %s" % val_min
        elif val_max and val_len > val_max:
            invalid_cause = "maximum %s" % val_max

        if invalid_cause:
            obj_name = obj.format().name.capitalize()
            msg = "%s %s cardinality violated" % (obj_name, card_target_attr)
            msg += " (%s values, %s found)" % (invalid_cause, val_len)

            err = ValidationError(obj, msg, validation_rank, validation_id)

    return err


def section_properties_cardinality(obj):
    """
    Checks Section properties against any set property cardinality.

    :param obj: odml.Section

    :return: Yields a ValidationError warning, if a set cardinality is not met.
    """
    validation_id = IssueID.section_properties_cardinality

    err = _cardinality_validation(obj, obj.prop_cardinality, 'properties',
                                  LABEL_WARNING, validation_id)
    if err:
        yield err


Validation.register_handler("section", section_properties_cardinality)


def section_sections_cardinality(obj):
    """
    Checks Section sub-sections against any set sub-section cardinality.

    :param obj: odml.Section

    :return: Yields a ValidationError warning, if a set cardinality is not met.
    """
    validation_id = IssueID.section_sections_cardinality

    err = _cardinality_validation(obj, obj.sec_cardinality, 'sections',
                                  LABEL_WARNING, validation_id)
    if err:
        yield err


Validation.register_handler("section", section_sections_cardinality)


def property_values_cardinality(obj):
    """
    Checks Property values against any set value cardinality.

    :param obj: odml.Property

    :return: Yields a ValidationError warning, if a set cardinality is not met.
    """
    validation_id = IssueID.property_values_cardinality

    err = _cardinality_validation(obj, obj.val_cardinality, 'values',
                                  LABEL_WARNING, validation_id)
    if err:
        yield err


Validation.register_handler("property", property_values_cardinality)
