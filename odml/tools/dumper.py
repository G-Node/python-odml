"""
Dumps odML-Structures
"""


def get_props(obj, props):
    out = []
    for p in props:
        if hasattr(obj, p):
            x = getattr(obj, p)
            if x is not None:
                out.append("%s=%s" % (p, repr(x)))
    return ", ".join(out)


def dumpProperty(property, indent=1):
    print("%*s:%s (%s)" % (indent, " ", property.name, get_props(property,
                                                                 ["definition", "value", "uncertainty", "unit", "dtype",
                                                                  "value_reference", "dependency", "dependencyValue"])))


def dumpSection(section, indent=1):
    if section is None:
        return

    print("%*s*%s (%s)" % (indent, " ", section.name, get_props(section,
                                                                ["type", "definition", "link",
                                                                 "include", "repository"])))
    for prop in section.properties:
        dumpProperty(prop, indent + 1)

    for sub in section.sections:
        dumpSection(sub, indent * 2)


def dumpDoc(doc):
    for sec in doc:
        dumpSection(sec)
