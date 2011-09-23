import doc, section, property, value

# the original property-function is overwritten
# so get it back!
from __builtin__ import property as _property

class odml_implementation(object):
    Value = None
    Property = None
    Section = None
    Document = None

class BasicImplementation(odml_implementation):
    @_property
    def Value(self):
        return value.BaseValue
    @_property
    def Section(self):
        return section.BaseSection
    @_property
    def Property(self):
        return property.BaseProperty
    @_property
    def Document(self):
        return doc.BaseDocument

# the default implementation
impl = BasicImplementation()
# the other available ones
impls = {'basic': impl}

def addImplementation(key, implementation, make_default=False):
    impls[key] = implementation
    if make_default:
        setDefaultImplementation(key)

def getImplementation(key=None):
    if key is None: return impl
    return impls[key]

def setDefaultImplementation(key):
    global impl
    impl = impls[key]

def Value(*args, **kwargs):
    return impl.Value(*args, **kwargs)

def Property(*args, **kwargs):
    return impl.Property(*args, **kwargs)

def Section(*args, **kwargs):
    return impl.Section(*args, **kwargs)

def Document(*args, **kwargs):
    return impl.Document(*args, **kwargs)

#__all__ = [Value, Property, Section, Document]
