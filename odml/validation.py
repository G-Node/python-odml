# -*- coding: utf-8
"""
Generic odML validation framework.
"""

from . import dtypes

LABEL_ERROR = 'error'
LABEL_WARNING = 'warning'


class ValidationError(object):
    """
    Represents an error found in the validation process.

    The error is bound to an odML-object (*obj*) or a list of those and contains
    a message and a rank which may be one of: 'error', 'warning'.
    """

    def __init__(self, obj, msg, rank=LABEL_ERROR):
        self.obj = obj
        self.msg = msg
        self.rank = rank

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
        return "<ValidationError(%s):%s '%s'>" % (self.rank,
                                                  self.obj,
                                                  self.msg)


class Validation(object):
    """
    Validation provides a set of default validations that can used to validate
    an odml.Document. Custom validations can be added via the 'register_handler' method.

    :param doc: odml.Document that the validation will be applied to.
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

    def __init__(self, obj):
        self.doc = obj  # may also be a section
        self.errors = []

        self.validate(obj)

        if obj.format().name == "property":
            return

        for sec in obj.itersections(recursive=True):
            self.validate(sec)
            for prop in sec.properties:
                self.validate(prop)

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

def object_args_must_be_defined(obj):
    """
    Tests that no Object has undefined attributes, given in format.

    :param obj: document, section or property.
    """

    args = obj.format().arguments
    for arg in args:
        if arg[1] == 1:
            obj_arg = getattr(obj, arg[0])
            if obj_arg is None or obj_arg == '' or obj_arg == 'undefined':
                yield ValidationError(obj, obj.format().name.capitalize() + ' ' + arg[0] + ' undefined', LABEL_WARNING)


Validation.register_handler('odML', object_args_must_be_defined)
Validation.register_handler('section', object_args_must_be_defined)
Validation.register_handler('property', object_args_must_be_defined)


def section_type_must_be_defined(sec):
    """
    Tests that no Section has an undefined type.

    :param sec: odml.Section.
    """
    if sec.type is None or sec.type == '' or sec.type == 'undefined':
        yield ValidationError(sec, 'Section type undefined', LABEL_WARNING)


Validation.register_handler('section', section_type_must_be_defined)


def section_repository_present(sec):
    """
    1. warn, if a section has no repository or
    2. the section type is not present in the repository
    """
    repo = sec.get_repository()
    if repo is None:
        msg = "A section should have an associated repository"
        yield ValidationError(sec, msg, LABEL_WARNING)
        return

    try:
        tsec = sec.get_terminology_equivalent()
    except Exception as exc:
        msg = "Could not load terminology: %s" % exc
        yield ValidationError(sec, msg, LABEL_WARNING)
        return

    if tsec is None:
        msg = "Section type '%s' not found in terminology" % sec.type
        yield ValidationError(sec, msg, LABEL_WARNING)


Validation.register_handler('section', section_repository_present)


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
    if not id_map:
        id_map = {}

    for sec in parent.sections:
        for i in property_unique_ids(sec, id_map):
            yield i

        if sec.id in id_map:
            msg = "Duplicate id in Section '%s' and %s" % (sec.get_path(), id_map[sec.id])
            yield ValidationError(sec, msg)
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
    if not id_map:
        id_map = {}

    for prop in section.properties:
        if prop.id in id_map:
            msg = "Duplicate id in Property '%s' and %s" % (prop.get_path(),
                                                            id_map[prop.id])
            yield ValidationError(prop, msg)
        else:
            id_map[prop.id] = "Property '%s'" % prop.get_path()


Validation.register_handler('odML', document_unique_ids)


def object_unique_names(obj, children, attr=lambda x: x.name,
                        msg="Object names must be unique"):
    """
    Tests that object names within one Section are unique.

    :param obj: odml class instance the validation is applied on.
    :param children: a function that returns the children to be considered.
    This is to be able to use the same function for sections and properties.
    :param attr: a function that returns the item that needs to be unique
    :param msg: error message that will be registered upon a ValidationError.
    """
    names = set(map(attr, children(obj)))
    if len(names) == len(children(obj)):
        return  # quick exit
    names = set()
    for i in children(obj):
        if attr(i) in names:
            yield ValidationError(i, msg, LABEL_ERROR)
        names.add(attr(i))


def section_unique_name_type(obj):
    """
    Tests that the values of names and types within the scope of a Section are unique.

    :param obj: odml class instance the validation is applied on.
    """
    for i in object_unique_names(
            obj,
            attr=lambda x: (x.name, x.type),
            children=lambda x: x.sections,
            msg="name/type combination must be unique"):
        yield i


def property_unique_names(obj):
    """
    Tests that the values of Property names within the scope of a Section are unique.

    :param obj: odml class instance the validation is applied on.
    """
    for i in object_unique_names(obj, lambda x: x.properties):
        yield i


Validation.register_handler('odML', section_unique_name_type)
Validation.register_handler('section', section_unique_name_type)
Validation.register_handler('section', property_unique_names)


def property_terminology_check(prop):
    """
    1. warn, if there are properties that do not occur in the terminology.
    2. warn, if there are multiple values with different units or the unit does
       not match the one in the terminology.
    """
    if not prop.parent:
        return

    tsec = prop.parent.get_terminology_equivalent()
    if tsec is None:
        return
    try:
        tsec.properties[prop.name]
    except KeyError:
        msg = "Property '%s' not found in terminology" % prop.name
        yield ValidationError(prop, msg, LABEL_WARNING)


Validation.register_handler('property', property_terminology_check)


def property_dependency_check(prop):
    """
    Produces a warning if the dependency attribute refers to a non-existent attribute
    or the dependency_value does not match.
    """
    if not prop.parent:
        return

    dep = prop.dependency
    if dep is None:
        return

    try:
        dep_obj = prop.parent[dep]
    except KeyError:
        msg = "Property refers to a non-existent dependency object"
        yield ValidationError(prop, msg, LABEL_WARNING)
        return

    if prop.dependency_value not in dep_obj.values[0]:
        msg = "Dependency-value is not equal to value of the property's dependency"
        yield ValidationError(prop, msg, LABEL_WARNING)


Validation.register_handler('property', property_dependency_check)


def property_values_check(prop):
    """
    PROTOTYPE

    Tests that the values are of consistent dtype.
    If dtype is not given, infer from first item in list.

    :param prop: property the validation is applied on.
    """

    if prop.dtype is not None and prop.dtype is not "":
        dtype = prop.dtype
    elif len(prop.values) != 0:
        dtype = dtypes.infer_dtype(prop.values[0])
    else:
        return

    for val in prop.values:
        try:
            dtypes.get(val, dtype)
        except Exception:
            msg = "Property values not of consistent dtype!"
            yield ValidationError(prop, msg, LABEL_ERROR)
