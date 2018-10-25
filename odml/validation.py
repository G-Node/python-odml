# -*- coding: utf-8
"""
Generic odML validation framework
"""


class ValidationError(object):
    """
    Represents an error found in the validation process

    The error is bound to an odML-object (*obj*) or a list of
    those and contains a message and a rank which may be one of:
    'error', 'warning', 'info'
    """

    def __init__(self, obj, msg, rank='error'):
        self.obj = obj
        self.msg = msg
        self.rank = rank

    @property
    def is_warning(self):
        return self.rank == 'warning'

    @property
    def is_error(self):
        return self.rank == 'error'

    @property
    def path(self):
        return self.obj.get_path()

    def __repr__(self):
        return "<ValidationError(%s):%s '%s'>" % (self.rank,
                                                  self.obj,
                                                  self.msg)


class Validation(object):

    _handlers = {}

    @staticmethod
    def register_handler(klass, handler):
        """
        Add a validation handler for a odml class.
        *type* may be one of the following:
         * odML
         * section
         * property

        And is called in the validation process for each corresponding
        object. The *handler* is assumed to be a generator function
        yielding all ValidationErrors it finds:

          handler(obj)

        The section handlers are only called for sections and not for
        the document node. If both are required, you need to register
        the handler twice.
        """
        Validation._handlers.setdefault(klass, set()).add(handler)

    def __init__(self, doc):
        self.doc = doc  # may also be a section
        self.errors = []
        self.validate(doc)

        for sec in doc.itersections(recursive=True):
            self.validate(sec)
            for prop in sec.properties:
                self.validate(prop)

    def validate(self, obj):
        handlers = self._handlers.get(obj.format().name, [])
        for handler in handlers:
            for err in handler(obj):
                self.error(err)

    def error(self, validation_error):
        """
        Register an error found during the validation process
        """
        self.errors.append(validation_error)

    def __getitem__(self, obj):
        """return a list of the errors for a certain object"""
        errors = []
        for err in self.errors:
            if err.obj is obj:
                errors.append(err)
        return errors


# ------------------------------------------------
# validation rules

def section_type_must_be_defined(sec):
    """test that no section has an undefined type"""
    if sec.type is None or sec.type == '' or sec.type == 'undefined':
        yield ValidationError(sec, 'Section type undefined', 'warning')


Validation.register_handler('section', section_type_must_be_defined)


def section_repository_present(sec):
    """
    1. warn, if a section has no repository or
    2. the section type is not present in the repository
    """
    repo = sec.get_repository()
    if repo is None:
        yield ValidationError(sec,
                              'A section should have an associated repository',
                              'warning')
        return

    try:
        tsec = sec.get_terminology_equivalent()
    except Exception as exc:
        yield ValidationError(sec,
                              'Could not load terminology: %s' % exc,
                              'warning')
        return

    if tsec is None:
        yield ValidationError(sec,
                              "Section type '%s' not found in terminology" % sec.type,
                              'warning')


Validation.register_handler('section', section_repository_present)


def document_unique_ids(doc):
    """
    Traverse an odML Document and check whether all
    assigned ids are unique within the document.

    Yields all duplicate odML object id entries
    that are encountered.

    :param doc: odML document
    """
    id_map = {doc.id: "Document '%s'" % doc.get_path()}
    for i in section_unique_ids(doc, id_map):
        yield i


def section_unique_ids(parent, id_map=None):
    """
    Traverse a parent (odML Document or Section)
    and check whether all assigned ids are unique.

    A "id":"odML object / path" dictionary of additional
    'to-be-excluded' ids may be handed in via the
    *id_map* attribute.

    Yields all duplicate odML object id entries
    that are encountered.

    :param parent: odML Document or Section
    :param id_map: "id":"odML object / path" dictionary
    """
    if not id_map:
        id_map = {}

    for sec in parent.sections:
        for i in property_unique_ids(sec, id_map):
            yield i

        if sec.id in id_map:
            yield ValidationError(sec, "Duplicate id in Section '%s' and '%s'" %
                                  (sec.get_path(), id_map[sec.id]))
        else:
            id_map[sec.id] = "Section '%s'" % sec.get_path()

        for i in section_unique_ids(sec, id_map):
            yield i


def property_unique_ids(section, id_map=None):
    """
    Check whether all ids assigned to the odML
    Properties of an odML Section are unique.

    A "id":"odML object / path" dictionary of additional
    'to-be-excluded' ids may be handed in via the
    *id_map* attribute.

    Yields all duplicate odML object id entries
    that are encountered.

    :param section: odML Section
    :param id_map: "id":"odML object / path" dictionary
    """
    if not id_map:
        id_map = {}

    for prop in section.properties:
        if prop.id in id_map:
            yield ValidationError(prop, "Duplicate id in Property '%s' and '%s'" %
                                  (prop.get_path(), id_map[prop.id]))
        else:
            id_map[prop.id] = "Property '%s'" % prop.get_path()


Validation.register_handler('odML', document_unique_ids)


def object_unique_names(obj, children, attr=lambda x: x.name,
                        msg="Object names must be unique"):
    """
    Test that object names within one section are unique

    *attr* is a function, that returns the item that needs to be unique

    *children* is a function, that returns the children to be
    considered. This is to be able to use the same function
    for sections and properties
    """
    names = set(map(attr, children(obj)))
    if len(names) == len(children(obj)):
        return  # quick exit
    names = set()
    for i in children(obj):
        if attr(i) in names:
            yield ValidationError(i, msg, 'error')
        names.add(attr(i))


def section_unique_name_type(obj):
    for i in object_unique_names(
            obj,
            attr=lambda x: (x.name, x.type),
            children=lambda x: x.sections,
            msg="name/type combination must be unique"):
        yield i


def property_unique_names(obj):
    for i in object_unique_names(obj, lambda x: x.properties):
        yield i


Validation.register_handler('odML', section_unique_name_type)
Validation.register_handler('section', section_unique_name_type)
Validation.register_handler('section', property_unique_names)


def property_terminology_check(prop):
    """
    Executes a couple of checks:

    1. warn, if there are properties that do not occur in the terminology
    2. warn, if there are multiple values with different units or the unit does
       not match the one in the terminology
    """
    tsec = prop.parent.get_terminology_equivalent()
    if tsec is None:
        return
    try:
        tsec.properties[prop.name]
    except KeyError:
        yield ValidationError(prop,
                              "Property '%s' not found in terminology" % prop.name,
                              'warning')


Validation.register_handler('property', property_terminology_check)


def property_dependency_check(prop):
    """
    Warn, if the dependency attribute refers to a non-existent attribute
    or the dependency_value does not match
    """
    dep = prop.dependency
    if dep is None:
        return

    try:
        dep_obj = prop.parent[dep]
    except KeyError:
        yield ValidationError(prop,
                              "Property refers to a non-existent dependency object",
                              'warning')
        return

    if prop.dependency_value not in dep_obj.value[0]:
        yield ValidationError(prop, "Dependency-value is not equal to value of"
                              " the property's dependency", 'warning')


Validation.register_handler('property', property_dependency_check)
