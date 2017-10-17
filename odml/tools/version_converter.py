import io
import os
import sys

from lxml import etree as ET
from odml.tools.xmlparser import XML_VERSION

try:
    unicode = unicode
except NameError:
    unicode = str


class VersionConverter(object):
    """
    Class for converting odml xml files from version 1.0 to 1.1
    """
    header = """<?xml version="1.0" encoding="UTF-8"?>\n"""

    _version_map = {
        'type': 'type'
    }

    _error_strings = {
        '<B0>': ''
    }

    def __init__(self, filename):
        self.filename = filename

    @classmethod
    def convert_odml_file(cls, filename):
        """
        Converts a given file to the odml version 1.1.
        Unites multiple value objects and brings value attributes out of the <value> tag.
        :param filename: The path to the file or io.StringIO object
        """
        tree = None
        if isinstance(filename, io.StringIO):
            cls._fix_unmatching_tags(filename)
            tree = ET.ElementTree(ET.fromstring(filename.getvalue()))
        elif os.path.exists(filename) and os.path.getsize(filename) > 0:
            cls._fix_unmatching_tags(filename)
            tree = ET.parse(filename)
        else:
            print("File \"{}\" has not been converted because it is not a valid path to odml .xml file "
                  "nor io.StringIO object".format(filename))
            return

        tree = cls._replace_same_name_entities(tree)
        root = tree.getroot()
        root.set("version", XML_VERSION)
        for prop in root.iter("property"):
            one_value = True
            first_value = None
            for value in prop.iter("value"):
                if one_value:
                    first_value = value
                    for val_elem in value.iter():
                        if val_elem.tag != "value" and one_value:
                            elem_name = cls._version_map[val_elem.tag] \
                                if val_elem.tag in cls._version_map else val_elem.tag
                            new_elem = ET.Element(elem_name)
                            new_elem.text = val_elem.text
                            value.getparent().append(new_elem)  # appending to the property
                            value.remove(val_elem)
                    one_value = False
                else:
                    first_value.text += ", " + value.text
                    prop.remove(value)
        return tree

    @classmethod
    def _fix_unmatching_tags(cls, filename):
        """
        Fix an xml file by deleting known mismatching tags.
        :param filename: The path to the file or io.StringIO object
        """
        changes = False
        if isinstance(filename, io.StringIO):
            doc = filename.getvalue()
        elif os.path.exists(filename) and os.path.getsize(filename) > 0:
            f = open(filename, 'r+')
            doc = f.read()
        for k, v in cls._error_strings.items():
            if k in doc:
                doc = doc.replace(k, cls._error_strings[k])
                changes = True

        if changes:
            if isinstance(filename, io.StringIO):
                return io.StringIO(doc)
            else:
                f.truncate(0)
                f.write(doc)
                f.close()

    @classmethod
    def _replace_same_name_entities(cls, tree):
        """
        Changes same section names in the doc by adding <-{index}> to the next section occurrences.
        :param tree: ElementTree of the doc
        :return: ElementTree
        """
        sec_map = {}
        prop_map = {}
        root = tree.getroot()
        for sec in root.iter("section"):
            n = sec.find("name")
            if n is not None:
                cls._change_entity_name(sec_map, n)
            else:
                raise Exception("Section attribute name is not specified")
            for prop in sec.iter("property"):
                if prop.getparent() == sec:
                    n = prop.find("name")
                    if n is not None:
                        cls._change_entity_name(prop_map, n)
            prop_map.clear()
        return tree

    @staticmethod
    def _change_entity_name(elem_map, name):
        if name.text not in elem_map:
            elem_map[name.text] = 1
        else:
            elem_map[name.text] += 1
            name.text += "-" + str(elem_map[name.text])

    def __str__(self):
        tree = self.convert_odml_file(self.filename)
        return ET.tounicode(tree, pretty_print=True) if tree else ""

    def __unicode__(self):
        tree = self.convert_odml_file(self.filename)
        return ET.tounicode(tree, pretty_print=True) if tree else ""

    def write_to_file(self, filename):
        if sys.version_info < (3,):
            data = unicode(self).encode('utf-8')
        else:
            data = str(self)
        if data and "<odML " in data:
            f = open(filename, "w")
            f.write(self.header)
            f.write(data)
            f.close()
