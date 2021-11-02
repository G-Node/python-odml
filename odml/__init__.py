import warnings

from sys import version_info as _python_version

_property = property

from . import doc
from . import property
from . import section
from .dtypes import DType
from .fileio import load, save, display
from .info import VERSION
from .tools.parser_utils import SUPPORTED_PARSERS as PARSERS


def _format_warning(warn_msg, *args, **kwargs):
    """
    Used to provide users with deprecation warnings via the warnings module
    but without spamming them with full stack traces.
    """
    final_msg = "%s\n" % str(warn_msg)
    # If available add category name to the message
    if args and hasattr(args[0], "__name__"):
        final_msg = "%s: %s" % (args[0].__name__, final_msg)

    return final_msg


# Monkey patch formatting 'warnings' messages for the whole module.
warnings.formatwarning = _format_warning

if _python_version.major < 3:
    msg = "Python 2 has reached end of live."
    msg += "\n\todML support for Python 2 has been dropped."
    warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
elif _python_version.major == 3 and _python_version.minor < 6:
    msg = "The '%s' package is not tested with your Python version. " % __name__
    msg += "\n\tPlease consider upgrading to the latest Python distribution."
    warnings.warn(msg)

__version__ = VERSION


class odml_implementation(object):
    name = None
    provides = []
    Property = None
    Section = None
    Document = None


class BasicImplementation(odml_implementation):
    name = 'basic'
    provides = ['basic']

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


def addImplementation(implementation, make_minimum=False,
                      make_default=False, key=None):
    """register a new available implementation"""
    impls[implementation.name] = implementation
    if make_minimum and key is not None:
        setMinimumImplementation(key)
    if make_default and key is not None:
        setDefaultImplementation(key)


def getImplementation(key=None):
    """retrieve a implementation named *key*"""
    if key is None:
        return current_implementation
    implementation = impls[key]
    return implementation


def setDefaultImplementation(key):
    """
    set a new default implementation

    if it does not fulfill the minimum requirements, a TypeError is raised
    """
    global current_implementation
    if minimum_implementation.name not in impls[key].provides:
        raise TypeError(
            "Cannot set default odml-implementation to '%s', "
            "because %s-capabilities are required which are not "
            "provided (provides: %s)" %
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
        return  # the minimum implementation is already capable of this feature
    if minimum_implementation.name not in impls[key].provides:
        raise TypeError(
            "Cannot set new minimum odml-implementation to '%s', "
            "because %s-capabilities are already required which are "
            "not provided (provides: %s)" %
            (key, minimum_implementation.name, ', '.join(impls[key].provides)))
    if key not in current_implementation.provides:
        setDefaultImplementation(key)
    minimum_implementation = impls[key]


addImplementation(current_implementation)


def Property(*args, **kwargs):
    return current_implementation.Property(*args, **kwargs)


def Section(*args, **kwargs):
    return current_implementation.Section(*args, **kwargs)


def Document(*args, **kwargs):
    return current_implementation.Document(*args, **kwargs)

# __all__ = [Property, Section, Document]
