"""
Dumps odML-Structures
"""
from .xmlparser import to_csv


def get_props(obj, props):
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
    prop_list = ["definition", "values", "uncertainty", "unit", "dtype",
                 "value_reference", "dependency", "dependencyValue"]
    prop_string = get_props(prop, prop_list)
    print("%*s:%s (%s)" % (indent, " ", prop.name, prop_string))


def dump_section(section, indent=1):
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
    for sec in doc:
        dump_section(sec)
