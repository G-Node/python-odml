#!/usr/bin/env python
"""
The XML parsing module.

Parses odML files. Can be invoked standalone:

    python -m odml.tools.xmlparser file.odml
"""
#TODO make this module a parser class, allow arguments (e.g. skip_errors=1 to parse even broken documents)

from .. import Document, Section, Property, Value
from .. import format
from lxml.etree import ElementTree
from StringIO import StringIO

def get_props(obj, props):
    out = []
    for p in props:
        if hasattr(obj, p):
            x = getattr(obj, p)
            if not x is None:
                out.append("%s=%s" % (p, repr(x)))
    return ", ".join(out)

def dumpSection(section, indent=1):
    if not section:
        return

    print "%*s*%s (%s)" % (indent, " ", section.name, get_props(section, ["type", "definition", "id", "link", "import", "repository", "mapping"]))

    for prop in section.properties:
        print  "%*s:%s (%s)" % (indent + 1, " ", prop.name, get_props(prop, ["synonym", "definition", "mapping", "dependency", "dependencyValue"]))
        for value in prop.values:
            print  "%*s:%s (%s)" % (indent + 3, " ", value.data, get_props(value, ["dtype", "unit", "uncertainty", "definition", "id", "defaultFileName"]))

    for sub in section.sections:
        dumpSection(sub, indent * 2)

class ParserException(Exception): pass

def check_mandatory_arguments(data, ArgClass, tag_name, node):
    for k, v in ArgClass._args.iteritems():
        if v != 0 and not k in data:
            error("missing element <%s> within <%s> tag" % (k, tag_name), node)

def is_valid_argument(child, ArgClass, tag_name):
     if not child.tag in ArgClass._args:
        error("Invalid element <%s> inside <%s> tag" % (child.tag, tag_name), child)

def error(msg, elem):
    if not elem is None:
        msg += " (line %d)" % elem.sourceline
    raise ParserException(msg)

def warn(msg, elem):
    if elem:
        msg = "warning[%d]: %s\n" % (elem.sourceline, msg)
    else:
        msg = "warning: %s\n" % msg
    sys.stderr.write(msg)

def parseValue(node):
    """
    parse a <value>-tag *node*

    reads all sub-nodes and constructs corresponding attributes from which
    a Value object is created and returned
    """
    text = node.text.strip() if node.text else ""
    args = {}
    for child in node:
        is_valid_argument(child, format.Value, "value")
        if child.tag in args:
            error("Element <%s> is given multiple times in <value> tag" % child.tag, child)
        args[child.tag] = child.text.strip() if child.text else None
        text += child.tail.strip() if child.tail else ""

    if 'type' in args: #rename the attribute, it's called dtype in the python implementation
        args['dtype'] = args['type']
        del args['type']

    if text == "":
        warn("empty value", node)
    return Value(text, **args)

def parseProperty(node):
    """
    parse a <property>-tag *node*

    reads all sub-nodes and constructs corresponding attributes from which
    a Property object is created and returned
    all <value>-tags within this node will be parsed by `parseValue` and added to the
    list of this properties' values
    """
    args = {}
    values = []
    for child in node:
        is_valid_argument(child, format.Property, "property")
        #TODO check if tags occur multiple times?
        if child.tag == "value":
            values.append(parseValue(child))
        args[child.tag] = child.text.strip() if child.text else None

    check_mandatory_arguments(args, format.Property, "property", node)
    args['value'] = values
    return Property(**args)

def parseSection(node):
    name = node.get("name") # property name= overrides
    if not name:            # the element
        name = node.find("name")
        if name: name = name.text
    
    if not name:
        return error("Missing name element in <section>", node)

    section = Section(name)
    args = {}

    for child in node:
        is_valid_argument(child, format.Section, "section")
        if child.tag == "section":
            subsection = parseSection(child)
            if subsection:
                section.append(subsection)
        elif child.tag == "property":
            prop = parseProperty(child)
            if prop:
                section.append(prop)
        else:
            args[child.tag] = child.text.strip() if child.text else None

    check_mandatory_arguments(args, format.Section, "section", node)

    if 'name' in args: #don't want to overwrite it
        del args['name']
    if 'import' in args: # import is a reserved name in python
        args['reference'] = args['import']
        del args['import']

    for k, v in args.iteritems():
        if hasattr(section, k):
            setattr(section, k, v)
    return section

def parseXML(xml_file):
    """parses an xml-file
    
    *xml_file* is a file-object
    
    returns an odML-Document
    """
    tree = ElementTree()
    root = tree.parse(xml_file)

    doc = Document()
    for node in root:
        if node.tag != "section":
            error("Invalid element <%s> in odML document" % node.tag)
        section = parseSection(node)
        if section:
            doc.append(section)

    for sec in doc.sections:
        dumpSection(sec)

    return doc

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
    else:
        doc = parseXML (open(args[0]))
