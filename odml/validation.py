#-*- coding: utf-8
"""
generic odml validation framework
"""
import format
import mapping
import tools.event
import odml

# event capabilities are needed for mappings
odml.setMinimumImplementation('event')

class ValidationError(object):
    """
    Represents an error found in the validation process
    
    The error is bound to an odml-object (*obj*) or a list of those
    and contains a message and a type which may be one of:
    'error', 'warning', 'info'
    """
    def __init__(self, obj, msg, type='error'):
        self.obj = obj
        self.msg = msg
        self.type = type
    def __repr__(self):
        return "<ValidationError(%s):%s \"%s\">" % (self.type, self.obj, self.msg)
    

class Validation(object):
    _handlers = {}
    @staticmethod
    def register_handler(klass, handler):
        """
        Add a validation handler for a odml-class.
        *type* may be one of the following:
         * odML
         * section
         * property
         * value
        
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
        self.doc = doc # may also be a section
        self.errors = []
        self.validate(doc)
        # TODO isn't there a 'walk' method for these things?
        for sec in doc.itersections(recursive=True):
            self.validate(sec)
            for prop in sec.properties:
                self.validate(prop)
                for val in prop.values:
                    self.validate(val)

    def validate(self, obj):
        handlers = self._handlers.get(obj._format._name, [])
        for handler in handlers:
            for err in handler(obj):
                self.error(err)

    def error(self, validation_error):
        """
        Register an error found during the validation process
        """
        self.errors.append(validation_error)

# ------------------------------------------------
# validation rules

def section_type_must_be_defined(sec):
    """test that no section has an undefined type"""
    if sec.type is None or sec.type == '' or sec.type == 'undefined':
        yield ValidationError(sec, 'Section type undefined', 'warning')

Validation.register_handler('section', section_type_must_be_defined)

def object_unique_names(obj, children):
    """
    test that object names within one section are unique
    
    *children* is a function, that returns the children to be
    considered. This is to be able to use the same function
    for sections and properties
    """
    names = set([s.name for s in children(obj)])
    if len(names) == len(children(obj)):
        return # quick exit
    names = set()
    for s in children(obj):
        if s.name in names:
            yield ValidationError(s, 'Object names must be unique', 'error')
        names.add(s.name)

def section_unique_names(obj):
    for i in object_unique_names(obj, lambda x: x.sections):
        yield i
        
def property_unique_names(obj):
    for i in object_unique_names(obj, lambda x: x.properties):
        yield i

Validation.register_handler('odML',     section_unique_names)
Validation.register_handler('section',  section_unique_names)
Validation.register_handler('section', property_unique_names)

def odML_mapped_document_be_valid(doc):
    if mapping.proxy is not None and isinstance(doc, mapping.proxy.Proxy):
        return # don't try to map already mapped documents
    try:
        mdoc = mapping.create_mapping(doc)
    except mapping.MappingError, e:
        yield ValidationError(doc, 'mapping: %s' % str(e), 'error')
        return
    v = Validation(mdoc)
    for err in v.errors:
        err.mobj = err.obj
        err.obj = mapping.get_object_from_mapped_equivalent(err.obj)
        err.msg = "mapping: " + err.msg
        yield err
        
Validation.register_handler('odML', odML_mapped_document_be_valid)

def property_terminology_check(prop):
    """warn, if there are properties that do not occur in the terminology"""
    tsec = prop.parent.get_terminology_equivalent()
    if tsec is None: return
    try:
        tprop = tsec.properties[prop.name]
    except KeyError:
        yield ValidationError(prop, "Property '%s' not found in terminology" % prop.name, 'warning')
        
Validation.register_handler('property', property_terminology_check)
