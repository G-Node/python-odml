"""
Dumps odML-Structures
"""


def get_props(obj, props):
    out = []
    for p in props:
        if hasattr(obj, p):
            x = getattr(obj, p)
            if not x is None:
                out.append("%s=%s" % (p, repr(x)))
    return ", ".join(out)


def dumpSection(section, indent=1):
    if section is None:
        return

    print("%*s*%s (%s)" % (
        indent, " ", section.name, get_props(
            section,
            ["type", "definition", "id", "link", "include", "repository"]
        )
    ))

    for prop in section.properties:
        print("%*s:%s (%s)" % (
            indent + 1, " ", prop.name,
            get_props(
                prop,
                ["definition", "dependency", "dependencyValue"]
            )
        ))
        for value in prop.values:
            print("%*s:%s (%s)" % (
                indent + 3, " ", value.data,
                get_props(
                    value,
                    ["dtype", "unit", "uncertainty", "definition",
                     "id", "defaultFileName"]
                )
            ))

    for sub in section.sections:
        dumpSection(sub, indent * 2)


def dumpDoc(doc):
    for sec in doc:
        dumpSection(sec)
