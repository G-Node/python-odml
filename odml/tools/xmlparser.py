#!/usr/bin/env python
"""
The XML parsing module.

Parses odML files. Can be invoked standalone:

    python -m odml.tools.xmlparser file.odml
"""
#TODO make this module a parser class, allow arguments (e.g. skip_errors=1 to parse even broken documents)

from .. import Document, Section, Property, Value
from .. import format
from dumper import dumpSection
from lxml import etree as ET
from lxml.builder import E
import sys

from StringIO import StringIO

format.Document._xml_name = "odML"
format.Section._xml_name = "section"
format.Property._xml_name = "property"
format.Value._xml_name = "value"
format.Document._xml_attributes = ['version']
format.Section._xml_attributes = ['name']
format.Property._xml_attributes = []
format.Value._xml_attributes = []
format.Value._xml_content = 'value'

class XMLWriter:
    """
    Creates XML nodes storing the information of an odML Document
    """
    header = """<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet  type="text/xsl" href="odmlTerms.xsl"?>
<?xml-stylesheet  type="text/xsl" href="odml.xsl"?>
"""
    def __init__(self, odml_document):
        self.doc = odml_document
    
    @staticmethod
    def save_element(e):
        """
        returns an xml node for the odML object e
        """
        fmt = e._format
        if hasattr(fmt, "_xml_content"):
            cur = E(fmt._name, getattr(e, fmt.map(fmt._xml_content)))
        else:
            cur = E(fmt._name)
            
        # generate attributes
        for k in fmt._xml_attributes:
            if not hasattr(e, fmt.map(k)): continue
            
            val = getattr(e, fmt.map(k))
            if val is None: continue # no need to save this
            cur.attrib[k] = unicode(val)

        # generate elements
        for k in fmt._args:
#            print "processing %s -> %s" % (e, k)
            if k in fmt._xml_attributes \
                or not hasattr(e, fmt.map(k)) \
                or (hasattr(fmt, "_xml_content") and fmt._xml_content == k):
                    continue
            
            val = getattr(e, fmt.map(k))
            if val is None: continue
            
            if type(val) is list:
                for v in val:
                    ele = XMLWriter.save_element(v)
                    cur.append(ele)
            else:
                ele = E(k, unicode(val))
                cur.append(ele)
        
        return cur
    
    def __unicode__(self):
        return ET.tounicode(self.save_element(self.doc), pretty_print=True)
    
    def write_file(self, filename):
        f = open(filename, "w")
        f.write(self.header)
        f.write(unicode(self))
        f.close()


class ParserException(Exception): pass

def check_mandatory_arguments(data, ArgClass, tag_name, node):
    for k, v in ArgClass._args.iteritems():
        if v != 0 and not ArgClass.map(k) in data:
            error("missing element <%s> within <%s> tag" % (k, tag_name), node)

def is_valid_argument(child, ArgClass, tag_name):
     if not child.tag in ArgClass._args:
        error("Invalid element <%s> inside <%s> tag" % (child.tag, tag_name), child)

def error(msg, elem):
    if not elem is None:
        msg += " (line %d)" % elem.sourceline
    raise ParserException(msg)

def warn(msg, elem):
    if not elem is None:
        msg = "warning[<%s>:%d]: %s\n" % (elem.tag, elem.sourceline, msg)
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
        args[format.Value.map(child.tag)] = child.text.strip() if child.text else None
        text += child.tail.strip() if child.tail else ""

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
        args[format.Property.map(child.tag)] = child.text.strip() if child.text else None

    if values:
        # set this, because the constructor users the value property even for multiple values
        # (and also so that the mandatory arguments-checker is fine)
        args['value'] = values
        
    check_mandatory_arguments(args, format.Property, "property", node)
    
    # same hack as above: Property constructor takes a value argument
    # kind of violating the format description
    del args['values']

    return Property(**args)

def parseSection(node):
    name = node.get("name") # property name= overrides
    if name is None:        # the element
        name = node.find("name")
        if name is not None: name = name.text
    
    if name is None:
        return error("Missing name element in <section>", node)

    section = Section(name)
    args = {}

    for child in node:
        is_valid_argument(child, format.Section, "section")
        tag = format.Section.map(child.tag)
        if child.tag == "section":
            subsection = parseSection(child)
            if subsection:
                section.append(subsection)
        elif child.tag == "property":
            prop = parseProperty(child)
            if prop:
                section.append(prop)
        else:
            args[tag] = child.text.strip() if child.text else None

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
    tree = ET.ElementTree()
    root = tree.parse(xml_file)

    doc = Document()
    for node in root:
        if node.tag in format.Document._args:
            if node.tag == "section":
                section = parseSection(node)
                if section:
                    doc.append(section)
            else:
                setattr(doc, format.Document.map(node.tag), node.text.strip() if node.text else None)
        else:
            error("Invalid element <%s> in odML document" % node.tag, node)

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
        doc = parseXML(open(args[0]))
    
