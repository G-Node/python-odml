#!/usr/bin/env python
"""
The XML parsing module.

Parses odML files. Can be invoked standalone:

    python -m odml.tools.xmlparser file.odml
"""
# TODO make this module a parser class, allow arguments (e.g. skip_errors=1 to parse even broken documents)
import sys
import csv
try:
    from StringIO import StringIO
except:
    from io import StringIO
from odml import format
from lxml import etree as ET
from lxml.builder import E
# this is needed for py2exe to include lxml completely
from lxml import _elementpath as _dummy

try:
    unicode = unicode
except NameError:
    unicode = str

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

format.Document._xml_name = "odML"
format.Section._xml_name = "section"
format.Property._xml_name = "property"

format.Document._xml_attributes = {}
format.Section._xml_attributes = {'name': None}  # attribute 'name' maps to 'name', but writing it as a tag is preferred
format.Property._xml_attributes = {}


XML_VERSION = "1.1"


def to_csv(val):
    unicode_values = list(map(unicode, val))
    stream = StringIO()
    writer = csv.writer(stream, dialect="excel")
    writer.writerow(unicode_values)
    csv_string = stream.getvalue().strip()
    csv_string = "[" + csv_string + "]"
    return csv_string


def from_csv(value_string):
    if len(value_string) == 0:
        return []
    if value_string[0] == "[":
        value_string = value_string[1:-1]
    stream = StringIO(value_string)
    stream.seek(0)
    reader = csv.reader(stream, dialect="excel")
    return list(reader)[0]


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
            val = getattr(e, fmt.map(fmt._xml_content))
            if val is None:
                val = ''
            cur = E(fmt._name, val)
        else:
            cur = E(fmt._name)

        # generate attributes
        if isinstance(fmt, format.Document.__class__):
            cur.attrib['version'] = XML_VERSION

        for k, v in fmt._xml_attributes.items():
            if not v or not hasattr(e, fmt.map(v)):
                continue

            val = getattr(e, fmt.map(v))
            if val is None:
                continue  # no need to save this
            if sys.version_info < (3, 0):
                cur.attrib[k] = unicode(val)
            else:
                cur.attrib[k] = str(val)

        # generate elements
        for k in fmt._args:
            if (k in fmt._xml_attributes and fmt._xml_attributes[k] is not None) or not hasattr(e, fmt.map(k)) \
                    or (hasattr(fmt, "_xml_content") and fmt._xml_content == k):
                continue
            val = getattr(e, fmt.map(k))
            if val is None:
                continue
            if isinstance(fmt, format.Property.__class__) and k == "value":
                ele = E(k, to_csv(val))
                cur.append(ele)
            else:
                if isinstance(val, list):
                    for v in val:
                        if v is None:
                            continue
                        ele = XMLWriter.save_element(v)
                        cur.append(ele)
                else:
                    if sys.version_info < (3,):
                        ele = E(k, unicode(val))
                    else:
                        ele = E(k, str(val))
                    cur.append(ele)
        return cur

    def __str__(self):
        return ET.tounicode(self.save_element(self.doc), pretty_print=True)

    def __unicode__(self):
        return ET.tounicode(self.save_element(self.doc), pretty_print=True)

    def write_file(self, filename):
        # calculate the data before opening the file in case we get any
        # exception
        if sys.version_info < (3,):
            data = unicode(self).encode('utf-8')
        else:
            data = str(self)

        f = open(filename, "w")
        f.write(self.header)
        f.write(data)
        f.close()


def load(filename):
    """
    shortcut function for XMLReader().fromFile(open(filename))
    """
    return XMLReader().fromFile(open(filename))


class ParserException(Exception):
    pass


class XMLReader(object):
    """
    A reader to parse xml-files or strings into odml data structures

    Usage:

        >>> doc = XMLReader().fromFile(open("file.odml"))
    """

    def __init__(self, ignore_errors=False, filename=None):
        self.parser = ET.XMLParser(remove_comments=True)
        self.tags = dict([(obj._xml_name, obj) for obj in format.__all__])
        self.ignore_errors = ignore_errors
        self.filename = filename

    def fromFile(self, xml_file):
        """
        parse the datastream from a file like object *xml_file*
        and return an odml data structure
        """
        try:
            root = ET.parse(xml_file, self.parser).getroot()
            if hasattr(xml_file, "close"):
                xml_file.close()
        except ET.XMLSyntaxError as e:
            raise ParserException(e.msg)
        return self.parse_element(root)

    def fromString(self, string):
        try:
            root = ET.XML(string, self.parser)
        except ET.XMLSyntaxError as e:
            raise ParserException(e.msg)
        return self.parse_element(root)

    def check_mandatory_arguments(self, data, ArgClass, tag_name, node):
        for k, v in ArgClass._args.items():
            if v != 0 and not ArgClass.map(k) in data:
                self.error("missing element <%s> within <%s> tag" % (k, tag_name) + repr(data), node)

    def is_valid_argument(self, tag_name, ArgClass, parent_node, child=None):
        if tag_name not in ArgClass._args:
            self.error("Invalid element <%s> inside <%s> tag" % (tag_name, parent_node.tag),
                       parent_node if child is None else child)

    def error(self, msg, elem):
        if elem is not None:
            msg += " (line %d)" % elem.sourceline
        if self.ignore_errors:
            return self.warn(msg, elem)
        raise ParserException(msg)

    def warn(self, msg, elem):
        if elem is not None:
            msg = "warning[%s:%d:<%s>]: %s\n" % (self.filename, elem.sourceline, elem.tag, msg)
        else:
            msg = "warning: %s\n" % msg
        sys.stderr.write(msg)

    def parse_element(self, node):
        if node.tag not in self.tags:
            self.error("Invalid element <%s>" % node.tag, node)
            return None  # won't be able to parse this one
        return getattr(self, "parse_" + node.tag)(node, self.tags[node.tag])

    def parse_tag(self, root, fmt, insert_children=True, create=None):
        """
        parse an odml node based on the format description *fmt*
        and a function *create* to instantiate a corresponding object
        """
        arguments = {}
        extra_args = {}
        children = []
        text = []

        if root.text:
            text.append(root.text.strip())

        for k, v in root.attrib.iteritems():
            k = k.lower()
            self.is_valid_argument(k, fmt, root)
            if k == 'version' and root.tag == 'odML':
                continue  # special case for XML version
            if k not in fmt._xml_attributes:
                self.error("<%s %s=...>: is not a valid attribute for %s" % (root.tag, k, root.tag), root)
            else:
                k = fmt._xml_attributes[k] or k
                arguments[k] = v
        for node in root:
            node.tag = node.tag.lower()
            self.is_valid_argument(node.tag, fmt, root, node)
            if node.tag in fmt._args:
                if node.tag in self.tags and node.tag in fmt._map:  # this is a heuristic, but works for now
                    sub_obj = self.parse_element(node)
                    if sub_obj is not None:
                        extra_args[fmt.map(node.tag)] = sub_obj
                        children.append(sub_obj)
                else:
                    tag = fmt.map(node.tag)
                    if tag in arguments:
                        # TODO make this an error, however first figure out a way to let <odML version=><version/> pass
                        self.warn("Element <%s> is given multiple times in <%s> tag" % (node.tag, root.tag), node)
                    if tag == "value" and node.text:  # special handling of values ...
                        content = from_csv(node.text.strip())
                        arguments[tag] = content
                    else:
                        arguments[tag] = node.text.strip() if node.text else None
            else:
                self.error("Invalid element <%s> in odML document section <%s>" % (node.tag, root.tag), node)
            if node.tail:
                text.append(node.tail.strip())

        if sys.version_info > (3,):
            self.check_mandatory_arguments(dict(list(arguments.items()) + list(extra_args.items())),
                                           fmt, root.tag, root)
        else:
            self.check_mandatory_arguments(dict(arguments.items() + extra_args.items()),
                                           fmt, root.tag, root)
        if create is None:
            obj = fmt.create()
        else:
            obj = create(args=arguments, text=''.join(text), children=children)

        for k, v in arguments.items():
            if hasattr(obj, k) and getattr(obj, k) is None:
                try:
                    setattr(obj, k, v)
                except Exception as e:
                    self.warn("cannot set '%s' property on <%s>: %s" % (k, root.tag, repr(e)), root)
                    if not self.ignore_errors:
                        raise e

        if insert_children:
            for child in children:
                obj.append(child)
        return obj

    def parse_odML(self, root, fmt):
        doc = self.parse_tag(root, fmt)
        return doc

    def parse_section(self, root, fmt):
        name = root.get("name")  # property name= overrides
        if name is None:  # the element
            name_node = root.find("name")
            if name_node is not None:
                name = name_node.text
                root.remove(name_node)
                # delete the name_node so its value won't
                # be used to overwrite the already set name-attribute

        if name is None:
            self.error("Missing name element in <section>", root)

        return self.parse_tag(root, fmt, create=lambda **kargs: fmt.create(name))

    def parse_property(self, root, fmt):
        create = lambda children, args, **kargs: fmt.create(**args)
        return self.parse_tag(root, fmt, insert_children=False, create=create)

    """
    def parse_value(self, root, fmt):
        create = lambda text, args, **kargs: fmt.create(text, **args)
        return self.parse_tag(root, fmt, insert_children=False, create=create)
    """


if __name__ == '__main__':
    from optparse import OptionParser
    import odml.tools.dumper as dumper

    parser = OptionParser()
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
    else:
        dumper.dumpDoc(load(args[0]))
