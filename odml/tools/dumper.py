"""
The dumper module provides functions to dump odML objects;
Document, Section, Property; to the command line.
"""
from .xmlparser import to_csv


def get_props(obj, props):
    """
    Retrieves the values of a list of provided properties
    from an object and returns all values as a concatenated string.

    :param obj: odml object from which to retrieve specific property values.
    :param props: list of properties
    :returns: the obj property values as a concatenated string
    """
    out = []
    for prop in props:
        if hasattr(obj, prop):
            curr = getattr(obj, prop)
            if curr is not None:
                if isinstance(curr, (list, tuple)):
                    out.append("%s=%s" % (prop, to_csv(curr)))
                else:
                    out.append("%s=%s" % (prop, repr(curr)))

    return ", ".join(out)


def dump_property(prop, indent=1):
    """
    Prints the content of an odml.Property.

    :param prop: odml.Property
    :param indent: number of prepended whitespaces. Default is 1.
    """
    prop_list = ["definition", "values", "uncertainty", "unit", "dtype",
                 "value_reference", "dependency", "dependencyValue"]
    prop_string = get_props(prop, prop_list)
    print("%*s:%s (%s)" % (indent, " ", prop.name, prop_string))


def dump_section(section, indent=1):
    """
    Prints the content of an odml.Section including any subsections
    and odml.Properties.

    :param section: odml.Section
    :param indent: number of prepended whitespaces. Default is 1.
    """
    if section is None:
        return

    prop_list = ["type", "definition", "link", "include", "repository"]
    prop_string = get_props(section, prop_list)
    print("%*s*%s (%s)" % (indent, " ", section.name, prop_string))

    for prop in section.properties:
        dump_property(prop, indent + 1)

    for sub in section.sections:
        dump_section(sub, indent * 2)


def dump_doc(doc):
    """
    Prints the content of an odml.Document including any subsections
    and odml.Properties.

    :param doc: odml.Section
    """
    for sec in doc:
        dump_section(sec)
