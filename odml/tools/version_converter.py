import io
import os
import sys

from lxml import etree as ET
from .. import format
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
        'type': 'type',
        'filename': 'value_origin'
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
            # Make pretty print available by resetting format
            parser = ET.XMLParser(remove_blank_text=True)
            tree = ET.parse(filename, parser)
        else:
            print("File \"{}\" has not been converted because it is not a valid path to odml .xml file "
                  "nor io.StringIO object".format(filename))
            return

        tree = cls._replace_same_name_entities(tree)
        root = tree.getroot()
        root.set("version", XML_VERSION)

        rem_property = []
        for prop in root.iter("property"):
            main_val = ET.Element("value")
            multiple_values = False

            # If a property has no name tag, mark it for removal
            if prop.find("name") is None:
                rem_property.append(prop)
                continue

            prop_name = prop.find("name").text
            # Special handling of Values
            for value in prop.iter("value"):
                for val_elem in value.iter():
                    if val_elem.tag != "value":
                        # Check whether current Value attribute has already been exported
                        # under its own or a different name. Give a warning, if the values differ.
                        check_export = value.getparent().find(cls._version_map[val_elem.tag]) \
                            if val_elem.tag in cls._version_map else value.getparent().find(val_elem.tag)

                        if check_export is not None:
                            if check_export.text != val_elem.text:
                                print("[Warning] Property '%s' Value attribute '%s/%s' "
                                      "already exported, omitting '%s'" %
                                      (prop_name, val_elem.tag, check_export.text, val_elem.text))
                        # Include only supported Property attributes
                        elif val_elem.tag in format.Property._args:
                            new_elem = ET.Element(val_elem.tag)
                            new_elem.text = val_elem.text
                            value.getparent().append(new_elem)
                        elif val_elem.tag in cls._version_map:
                            new_elem = ET.Element(cls._version_map[val_elem.tag])
                            new_elem.text = val_elem.text
                            value.getparent().append(new_elem)
                        else:
                            print("[Info] Omitted non-Value attribute '%s: %s/%s'" %
                                  (prop_name, val_elem.tag, val_elem.text))

                if value.text:
                    if main_val.text:
                        main_val.text += ", " + value.text
                        multiple_values = True
                    else:
                        main_val.text = value.text

                prop.remove(value)

            # Append value element only if it contains an actual value
            if main_val.text:
                # Multiple values require brackets
                if multiple_values:
                    main_val.text = "[" + main_val.text + "]"

                prop.append(main_val)

            # Exclude unsupported Property attributes
            for e in prop:
                if e.tag not in format.Property._args and e.tag != "value":
                    print("[Info] Omitted non-Property attribute '%s: %s/%s'" % (prop_name, e.tag, e.text))
                    prop.remove(e)

        # Exclude Properties without name tags
        for p in rem_property:
            print("[Warning] Omitted Property without name tag: '%s'" % ET.tostring(p))
            parent = p.getparent()
            parent.remove(p)

        # Exclude unsupported Section attributes, ignore comments
        for sec in root.iter("section"):
            sec_name = sec.find("name").text
            for e in sec:
                if e.tag not in format.Section._args and e.tag != "value":
                    print("[Info] Omitted non-Section attribute '%s: %s/%s'" % (sec_name, e.tag, e.text))
                    sec.remove(e)

        # Exclude unsupported Document attributes
        for e in root:
            if e.tag not in format.Document._args and e.tag != "value":
                print("[Info] Omitted non-Document attribute '%s/%s'" % (e.tag, e.text))
                root.remove(e)

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
