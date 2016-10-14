import doc, section, property, value
from odml.dtypes import DType

# the original property-function is overwritten
# so get it back!
from __builtin__ import property as _property


class odml_implementation(object):
    name = None
    provides = []
    Value = None
    Property = None
    Section = None
    Document = None


class BasicImplementation(odml_implementation):
    name = 'basic'
    provides = ['basic']

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

# here the available implementations are stored
impls = {}

# the default implementation
current_implementation = BasicImplementation()
minimum_implementation = current_implementation


def addImplementation(implementation, make_minimum=False, make_default=False):
    """register a new available implementation"""
    impls[implementation.name] = implementation
    if make_minimum:
        setMinimumImplementation(key)
    if make_default:
        setDefaultImplementation(key)


def getImplementation(key=None):
    """retrieve a implementation named *key*"""
    if key is None: return current_implementation
    implementation = impls[key]
    return implementation


def setDefaultImplementation(key):
    """
    set a new default implementation

    if it does not fulfill the minimum requirements, a TypeError is raised
    """
    global current_implementation
    if not minimum_implementation.name in impls[key].provides:
        raise TypeError(
            "Cannot set default odml-implementation to '%s', because %s-capabilities are required which are not provided (provides: %s)" %
            (key, minimum_implementation.name, ', '.join(impls[key].provides)))
    current_implementation = impls[key]


def setMinimumImplementation(key):
    """
    Set a new minimum requirement for a default implementation.
    This can only be increased, i.e. 'downgrades' are not possible.
    If the current_implementation does not provide the requested capability,
    make the minimum implementation the default.
    """
    global minimum_implementation
    if key in minimum_implementation.provides:
        return # the minimum implementation is already capable of this feature
    if not minimum_implementation.name in impls[key].provides:
        raise TypeError(
            "Cannot set new minimum odml-implementation to '%s', because %s-capabilities are already required which are not provided (provides: %s)" %
            (key, minimum_implementation.name, ', '.join(impls[key].provides)))
    if not key in current_implementation.provides:
        setDefaultImplementation(key)
    minimum_implementation = impls[key]


addImplementation(current_implementation)


def Value(*args, **kwargs):
    return current_implementation.Value(*args, **kwargs)


def Property(*args, **kwargs):
    return current_implementation.Property(*args, **kwargs)


def Section(*args, **kwargs):
    return current_implementation.Section(*args, **kwargs)


def Document(*args, **kwargs):
    return current_implementation.Document(*args, **kwargs)

#__all__ = [Value, Property, Section, Document]
