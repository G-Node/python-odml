#!/usr/bin/python


from odml import *
from xml.etree.ElementTree import ElementTree
from optparse import OptionParser
from StringIO import StringIO

def dumpSection(section, indent=1):
    if not section:
        return

    print "%*s*%s {%s}" % (indent, " ", section.Name, section.NameDefinition)

    for prop in section.getproperties():
        print  "%*s:%s" % (indent + 1, " ", prop.Name)
        for value in prop.values:
            print  "%*s:%s (%s)" % (indent + 3, " ", value.data, value.dtype)

    for sub in section.getsections():
        dumpSection(sub, indent * 2)

def parseValue(this_node, prop):
    txt = this_node.text
    #FIXME tailed text!
        
    if not txt:
        print "node does not have text: %s [%s] of %s" % (this_node, this_node.tag, prop.name)
        return
    
    val = odMLValue (txt)
     
    nodes = list (this_node)
    for node in nodes:
        if node.tag == "type":
            val.dtype = node.text
   
    prop.add_value (val)
    

def parseProperty(this_node):
    name = this_node.find ("name")
    if name is None:
        return None
    prop = odMLProperty(name.text)

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
    section = odMLSection(name)

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
    (data, length, etag) = xml_file.load_contents ()
    path = StringIO(data)

    tree = ElementTree()
    root = tree.parse(path)

    print "Parsing odML"
    nodes = list (root)
    doc = odMLDocument()
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
        
    doc = parseXML (args[0])


if __name__ == '__main__':
    xml_main()
