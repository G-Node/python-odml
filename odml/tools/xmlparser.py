#!/usr/bin/env python
"""
The XML parsing module.
Parses odML files. Can be invoked standalone:
    python -m odml.tools.xmlparser file.odml
"""
import csv
import sys
from lxml import etree as ET
from lxml.builder import E
# this is needed for py2exe to include lxml completely
from lxml import _elementpath as _dummy

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .. import format
from ..info import FORMAT_VERSION
from .parser_utils import InvalidVersionException, ParserException

try:
    unicode = unicode
except NameError:
    unicode = str


def to_csv(val):
    unicode_values = list(map(unicode, val))
    stream = StringIO()
    writer = csv.writer(stream, dialect="excel")
    writer.writerow(unicode_values)
    csv_string = stream.getvalue().strip()
    if len(unicode_values) > 1:
        csv_string = "[" + csv_string + "]"
    return csv_string


def from_csv(value_string):
    if not value_string:
        return []
    if value_string[0] == "[":
        value_string = value_string[1:-1]
    if not value_string:
        return []
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
        fmt = e.format()
        cur = E(fmt.name)

        # generate attributes
        if isinstance(fmt, format.Document.__class__):
            cur.attrib['version'] = FORMAT_VERSION

        # generate elements
        for k in fmt.arguments_keys:
            if not hasattr(e, fmt.map(k)):
                continue

            val = getattr(e, fmt.map(k))
            if val is None:
                continue
            if isinstance(fmt, format.Property.__class__) and k == "value":
                # Custom odML tuples require special handling for save loading from file.
                if e.dtype and e.dtype.endswith("-tuple") and len(val) > 0:
                    ele = E(k, "(%s)" % ";".join(val[0]))
                else:
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

        with open(filename, "w") as file:
            file.write(self.header)
            file.write(data)


def load(filename):
    """
    shortcut function for XMLReader().from_file(filename)
    """
    return XMLReader().from_file(filename)


class XMLReader(object):
    """
    A reader to parse xml-files or strings into odml data structures
    Usage:
        >>> doc = XMLReader().from_file("file.odml")
    """

    def __init__(self, ignore_errors=False, filename=None):
        self.parser = ET.XMLParser(remove_comments=True)
        self.tags = dict([(obj.name, obj) for obj in format.__all__])
        self.ignore_errors = ignore_errors
        self.filename = filename
        self.warnings = []

    @staticmethod
    def _handle_version(root):
        """
        Check if the odML version of a handed in parsed lxml.etree is supported
        by the current library and raise an Exception otherwise.
        :param root: Root node of a parsed lxml.etree. The root tag has to
                     contain a supported odML version number, otherwise it is not
                     accepted as a valid odML file.
        """
        if root.tag != 'odML':
            raise ParserException("Expecting <odML> tag but got <%s>.\n" % root.tag)
        elif 'version' not in root.attrib:
            raise ParserException("Could not find format version attribute "
                                  "in <odML> tag.\n")
        elif root.attrib['version'] != FORMAT_VERSION:
            msg = ("Cannot parse odML document with format version '%s'. \n"
                   "\tUse the 'tools.VersionConverter' to import previous odML formats."
                   % root.attrib['version'])
            raise InvalidVersionException(msg)

    def from_file(self, xml_file):
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

        self._handle_version(root)
        return self.parse_element(root)

    def from_string(self, string):
        try:
            root = ET.XML(string, self.parser)
        except ET.XMLSyntaxError as e:
            raise ParserException(e.msg)

        self._handle_version(root)
        return self.parse_element(root)

    def check_mandatory_arguments(self, data, ArgClass, tag_name, node):
        for k, v in ArgClass.arguments:
            if v != 0 and not ArgClass.map(k) in data:
                self.error("missing element <%s> within <%s> tag" %
                           (k, tag_name) + repr(data), node)

    def is_valid_argument(self, tag_name, ArgClass, parent_node, child=None):
        if tag_name not in ArgClass.arguments_keys:
            self.error("Invalid element <%s> inside <%s> tag" %
                       (tag_name, parent_node.tag),
                       parent_node if child is None else child)

    def error(self, msg, elem):
        if elem is not None:
            msg += " (line %d)" % elem.sourceline
        if self.ignore_errors:
            return self.warn(msg, elem)
        raise ParserException(msg)

    def warn(self, msg, elem):
        if elem is not None:
            msg = "warning[%s:%d:<%s>]: %s\n" % (
                self.filename, elem.sourceline, elem.tag, msg)
        else:
            msg = "warning: %s\n" % msg
        self.warnings.append(msg)
        sys.stderr.write(msg)

    def parse_element(self, node):
        if node.tag not in self.tags:
            self.error("Invalid element <%s>" % node.tag, node)
            return None  # won't be able to parse this one
        return getattr(self, "parse_" + node.tag)(node, self.tags[node.tag])

    def parse_tag(self, root, fmt, insert_children=True):
        """
        Parse an odml node based on the format description *fmt*
        and instantiate the corresponding object.
        :param root: lxml.etree node containing an odML object or object tree.
        :param fmt: odML class corresponding to the content of the root node.
        :param insert_children: Bool value. When True, child elements of the root node
                                will be parsed to their odML equivalents and appended to
                                the odML document. When False, child elements of the
                                root node will be ignored.
        """
        arguments = {}
        extra_args = {}
        children = []

        for k, v in root.attrib.iteritems():
            k = k.lower()
            # 'version' is currently the only supported XML attribute.
            if k == 'version' and root.tag == 'odML':
                continue

            # We currently do not support XML attributes.
            self.error("Attribute not supported, ignoring '%s=%s'" % (k, v), root)

        for node in root:
            node.tag = node.tag.lower()
            self.is_valid_argument(node.tag, fmt, root, node)
            if node.tag in fmt.arguments_keys:
                # this is a heuristic, but works for now
                if node.tag in self.tags and node.tag in fmt.map_keys:
                    sub_obj = self.parse_element(node)
                    if sub_obj is not None:
                        extra_args[fmt.map(node.tag)] = sub_obj
                        children.append(sub_obj)
                else:
                    tag = fmt.map(node.tag)
                    if tag in arguments:
                        self.warn("Element <%s> is given multiple times in "
                                  "<%s> tag" % (node.tag, root.tag), node)

                    # Special handling of values;
                    curr_text = node.text.strip() if node.text else None
                    if tag == "value" and curr_text:
                        content = from_csv(node.text)
                        arguments[tag] = content
                    else:
                        arguments[tag] = curr_text
            else:
                self.error("Invalid element <%s> in odML document section <%s>"
                           % (node.tag, root.tag), node)

        if sys.version_info > (3,):
            check_args = dict(list(arguments.items()) + list(extra_args.items()))
        else:
            check_args = dict(arguments.items() + extra_args.items())

        self.check_mandatory_arguments(check_args, fmt, root.tag, root)

        # Instantiate the current odML object with the parsed attributes.
        obj = fmt.create(**arguments)

        if insert_children:
            for child in children:
                obj.append(child)

        return obj

    def parse_odML(self, root, fmt):
        doc = self.parse_tag(root, fmt)
        return doc

    def parse_section(self, root, fmt):
        return self.parse_tag(root, fmt)

    def parse_property(self, root, fmt):
        return self.parse_tag(root, fmt, insert_children=False)


if __name__ == '__main__':
    from optparse import OptionParser
    import odml.tools.dumper as dumper

    parser = OptionParser()
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
    else:
        dumper.dumpDoc(load(args[0]))
