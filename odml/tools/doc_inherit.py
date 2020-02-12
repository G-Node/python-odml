"""
This is a working hack to provide inherited docstrings.
The only other working way I tried would involve metaclasses.

Each method to inherit a docstring is flagged using the @inherit_docstring
decorator.

The actual inheritance is done in the class decorator @allow_inherit_docstring,
which uses the classes base-classes and its mro and copies the first docstring
it finds.
"""


def allow_inherit_docstring(cls):
    """
    The base classes of a provided class will be used to copy and inherit the first
    docstring it finds.

    :param cls: class the decorator function will be used on to inherit the docstring
                from its base classes.
    :returns: class with the inherited docstring.
    """
    bases = cls.__bases__
    for attr, attribute in cls.__dict__.items():
        if hasattr(attribute, "inherit_docstring"):
            if not attribute.__doc__:
                for mro_cls in (mro_cls for base in bases
                                for mro_cls in base.mro()
                                if hasattr(mro_cls, attr)):
                    doc = getattr(getattr(mro_cls, attr), '__doc__')
                    if doc:
                        attribute.__doc__ = doc
                        break
    return cls


def inherit_docstring(obj):
    """
    Sets the inherit_docstring attribute of an object to True and returns the object.
    """
    obj.inherit_docstring = True

    return obj
