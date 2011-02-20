#!/usr/bin/python

from odML import *
from xml.etree.ElementTree import ElementTree
from optparse import OptionParser
from StringIO import StringIO
from event import Event

def dumpSection(section, indent=1):
    if not section:
        return

    print "%*s*%s {%s}" % (indent, " ", section.name, section.NameDefinition)

    for prop in section.properties:
        print  "%*s:%s" % (indent + 1, " ", prop.name)
        for value in prop.values:
            print  "%*s:%s (%s)" % (indent + 3, " ", value.data, value.dtype)

    for sub in section.sections:
        dumpSection(sub, indent * 2)

def parseValue(this_node, prop):
    txt = this_node.text
    #FIXME tailed text!
        
    if not txt:
        print "node does not have text: %s [%s] of %s" % (this_node, this_node.tag, prop.name)
        return
    
    val = Value (txt)
     
    nodes = list (this_node)
    for node in nodes:
        if node.tag == "type":
            val.dtype = node.text
   
    prop.add_value (val)
    

def parseProperty(this_node):
    name = this_node.find ("name")
    if name is None:
        return None
    prop = Property(name.text)

    vls = list (this_node)
    for v in vls:
        if v.tag != "value":
            continue
        parseValue(v, prop)

    return prop

def parseSection(this_node):
    name = this_node.get("name")
    if not name:
        return None
    section = Section(name)

    for node in list(this_node):
        if node.tag == "section":
            subsection = parseSection(node)
            if subsection is None:
                continue
            section.append (subsection)
        elif node.tag == "property":
            prop = parseProperty(node)
            if prop is None:
                continue
            section.append (prop)
        elif node.tag == "nameDefinition":
            section.NameDefinition = node.text
             
    return section

def parseXML(xml_file):
    """parses an xml-file
    
    *xml_file* is a file-object
    
    returns an odML-Document
    """
    tree = ElementTree()
    root = tree.parse(xml_file)

    print "Parsing odML"
    nodes = list (root)
    doc = Document()
    for node in nodes:
        if node.tag != "section":
            continue
        odMLSection = parseSection(node)
        doc.add_section (odMLSection)

    for sec in doc.sections:
        dumpSection(sec)

    return doc
    

def xml_main():
    parser = OptionParser()
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        return 1
        
    doc = parseXML (open(args[0]))


if __name__ == '__main__':
    xml_main()
