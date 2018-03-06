import io
import os
import sys

from lxml import etree as ET
from .. import format
from ..info import FORMAT_VERSION
from ..terminology import Terminologies, REPOSITORY_BASE

try:
    unicode = unicode
except NameError:
    unicode = str


class VersionConverter(object):
    """
    Class for converting odml xml files from version 1.0 to 1.1
    """
    _version_map = {
        'filename': 'value_origin'
    }

    _error_strings = {
        '<B0>': ''
    }

    def __init__(self, filename):
        self.filename = filename
        self.conversion_log = []

    def convert(self):
        """
        This method returns the content of the provided file object converted
        to odML version 1.1 as a string object which is directly consumable
        by the odml.tools.ODMLReader.
        """
        tree = self.convert_odml_file()
        return ET.tounicode(tree, pretty_print=True) if tree else ""

    def convert_odml_file(self):
        """
        Converts a given file to the odml version 1.1.
        Unites multiple value objects and brings value attributes out of the <value> tag.
        """
        # Reset status messages
        self.conversion_log = []

        tree = self._parse_document()
        tree = self._replace_same_name_entities(tree)
        root = tree.getroot()
        root.set("version", FORMAT_VERSION)

        # Handle Values, exclude unsupported Property attributes and unnamed Properties.
        self._handle_properties(root)

        # Exclude unsupported Section attributes, ignore comments, handle repositories.
        for sec in root.iter("section"):
            sec_name = sec.find("name").text
            for e in sec:
                if e.tag not in format.Section.arguments_keys and isinstance(e.tag, str):
                    self._log("[Info] Omitted non-Section attribute "
                              "'%s: %s/%s'" % (sec_name, e.tag, e.text))
                    sec.remove(e)
                    continue

                if e.tag == "repository":
                    self._handle_repository(e)

        # Exclude unsupported Document attributes, ignore comments, handle repositories.
        for e in root:
            if e.tag not in format.Document.arguments_keys and isinstance(e.tag, str):
                self._log("[Info] Omitted non-Document "
                          "attribute '%s/%s'" % (e.tag, e.text))
                root.remove(e)
                continue

            if e.tag == "repository":
                self._handle_repository(e)

        return tree

    def _handle_repository(self, element):
        """
        The method handles provided odML repositories.
        :param element: lxml element containing the provided odML repository link.
        """
        content = element.text
        cache = {}
        term_handler = Terminologies(cache)
        term = term_handler.load(element.text)

        # If the repository url can be loaded and parsed, everything is fine.
        if term is not None:
            return

        # If the repository url is a v1.0 odml-terminology one,
        # check whether a v1.1 is available and use it instead.
        if os.path.join(REPOSITORY_BASE, "v1.0") in element.text:
            element.text = element.text.replace('v1.0', 'v1.1')
            term = term_handler.load(element.text)

            if term is not None:
                msg = "[Info] Replaced repository url '%s' with '%s'." \
                      % (content, element.text)
                self._log(msg)
                return

        # Remove a repo element if no v1.1 compatible repository url can be provided.
        parent = element.getparent()
        parent.remove(element)
        self._log("[Warning] Excluded v1.0 repository '%s'." % content)

    def _handle_properties(self, root):
        """
        Method removes all property elements w/o name attribute, converts Value
        elements from v1.0 to v1.1 style and removes unsupported Property elements.
        :param root:
        """
        for prop in root.iter("property"):
            main_val = ET.Element("value")
            multiple_values = False
            parent = prop.getparent()

            # If a Property has no name attribute, remove it from its parent and
            # continue with the next Property.
            if prop.find("name") is None:
                self._log("[Warning] Omitted Property without "
                          "name tag: '%s'" % ET.tostring(prop))
                parent.remove(prop)
                continue

            sname = "unnamed"
            if parent.find("name") is not None:
                sname = parent.find("name").text
            stype = "untyped"
            if parent.find("type") is not None:
                stype = parent.find("type").text
            prop_id = "%s|%s:%s" % (sname, stype, prop.find("name").text)

            # Special handling of Values
            for value in prop.iter("value"):
                # Move supported elements from Value to parent Property.
                self._handle_value(value, prop_id)

                if value.text:
                    if main_val.text:
                        main_val.text += ", " + value.text.strip()
                        multiple_values = True
                    else:
                        main_val.text = value.text.strip()

                prop.remove(value)

            # Append value element only if it contains an actual value
            if main_val.text:
                # Multiple values require brackets
                if multiple_values:
                    main_val.text = "[" + main_val.text + "]"

                prop.append(main_val)

            # Exclude unsupported Property attributes, ignore comments
            for e in prop:
                if e.tag not in format.Property.arguments_keys and isinstance(e.tag, str):
                    self._log("[Info] Omitted non-Property attribute "
                              "'%s: %s/%s'" % (prop_id, e.tag, e.text))
                    prop.remove(e)

    def _handle_value(self, value, log_id):
        """
        Values changed from odML v1.0 to v1.1. This function moves all supported
        odML Property elements from a v1.0 Value element to the parent Property element.
        Adds a log entry for every non-exported element.
        :param value: etree element containing the v1.0 Value.
        :param log_id: String containing Section and Property name and type to log
                       omitted elements and value contents.
        """
        for val_elem in value.iter():
            if val_elem.tag != "value":
                # Check whether current Value attribute has already been exported
                # under its own or a different name. Give a warning, if the values differ.
                parent = value.getparent()
                if val_elem.tag in self._version_map:
                    check_export = parent.find(self._version_map[val_elem.tag])
                else:
                    check_export = parent.find(val_elem.tag)

                if check_export is not None:
                    if check_export.text != val_elem.text:
                        self._log("[Warning] Value element '%s: %s/%s' already exported, "
                                  "omitting further element value '%s'"
                                  % (log_id, val_elem.tag,
                                     check_export.text, val_elem.text))

                # Include only supported Property attributes
                elif val_elem.tag in format.Property.arguments_keys:
                    new_elem = ET.Element(val_elem.tag)
                    new_elem.text = val_elem.text
                    parent.append(new_elem)
                elif val_elem.tag in self._version_map:
                    new_elem = ET.Element(self._version_map[val_elem.tag])
                    new_elem.text = val_elem.text
                    parent.append(new_elem)
                else:
                    self._log("[Info] Omitted non-Value attribute '%s: %s/%s'"
                              % (log_id, val_elem.tag, val_elem.text))

    def _parse_document(self):
        """
        _parse_document checks whether the provided file object can be parsed,
        fixes known mismatching elements and returns the parsed lxml tree.
        :return: ElementTree
        """
        if isinstance(self.filename, io.StringIO):
            doc = self.filename.getvalue()
        elif os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            with open(self.filename, 'r+') as file:
                doc = file.read()
        else:
            msg = "Cannot parse provided file object '%s'." % self.filename
            raise Exception(msg)

        # Fix known mismatching elements
        for elem, val in self._error_strings.items():
            if elem in doc:
                doc = doc.replace(elem, val)

        # Make pretty print available by resetting format
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.ElementTree(ET.fromstring(doc, parser))

        return tree

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

    def _log(self, msg):
        """
        Adds the passed message to the conversion_log attribute and
        prints the message to the command line.
        """
        self.conversion_log.append(msg)
        print(msg)

    def __str__(self):
        tree = self.convert_odml_file()
        return ET.tounicode(tree, pretty_print=True) if tree else ""

    def __unicode__(self):
        tree = self.convert_odml_file()
        return ET.tounicode(tree, pretty_print=True) if tree else ""

    def write_to_file(self, filename):
        """
        This method converts the content of the provided converter file object
        to odML version 1.1 and writes the results to `filename`.
        :param filename: Output file.
        """
        if sys.version_info < (3,):
            data = unicode(self).encode('utf-8')
        else:
            data = str(self)

        ext = [".xml", ".odml"]
        if not filename.endswith(tuple(ext)):
            filename = "%s.xml" % filename

        if data and "<odML " in data:
            with open(filename, "w") as file:
                file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                file.write(data)
