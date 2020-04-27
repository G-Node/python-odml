"""
This module provides the class VersionConverter to convert
odML XML files from version 1.0 to 1.1.
"""

import io
import json
import os
import sys
import uuid
import yaml

from lxml import etree as ET

from ..parser_utils import ParserException
from ..xmlparser import XML_HEADER

from ...format import Document, Section, Property
from ...info import FORMAT_VERSION
from ...terminology import Terminologies, REPOSITORY_BASE

try:
    unicode = unicode
except NameError:
    unicode = str


class VersionConverter(object):
    """
    Class for converting odML XML files from version 1.0 to 1.1.
    """
    _version_map = {
        'filename': 'value_origin',
        'dtype': 'type'
    }

    def __init__(self, filename):
        self.filename = filename
        self.conversion_log = []

    def _parse_xml(self):
        """
        _parse_xml checks whether the provided file object can be parsed
        and returns the parsed lxml tree.

        :return: ElementTree
        """
        # Make pretty print available by resetting format
        parser = ET.XMLParser(remove_blank_text=True)
        if isinstance(self.filename, io.StringIO):
            doc = self.filename.getvalue()
            tree = ET.ElementTree(ET.fromstring(doc, parser))

        elif os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            tree = ET.parse(self.filename, parser)
        else:
            msg = "Cannot parse provided file object '%s'." % self.filename
            raise ParserException(msg)

        return tree

    def _parse_json(self):
        with open(self.filename) as file:
            parsed_doc = json.load(file)

        return self._parse_dict_document(parsed_doc)

    def _parse_yaml(self):
        with open(self.filename) as file:
            parsed_doc = yaml.safe_load(file)

        return self._parse_dict_document(parsed_doc)

    @classmethod
    def _parse_dict_document(cls, parsed_doc):
        """
        _parse_dict_document parses a python dictionary containing a valid
        v1.0 odML document into an lxml.ElementTree XML equivalent and returns
        the resulting lxml ElementTree.

        :param parsed_doc: python dictionary containing a valid v1.0 odML document.
        :return: lxml ElementTree
        """
        root = ET.Element("odML")

        parsed_doc = parsed_doc['Document']

        for elem in parsed_doc:
            if elem == 'sections':
                cls._parse_dict_sections(root, parsed_doc['sections'])
            elif elem:
                curr_element = ET.Element(elem)
                curr_element.text = parsed_doc[elem]
                root.append(curr_element)

        return ET.ElementTree(root)

    @classmethod
    def _parse_dict_sections(cls, parent_element, section_list):
        """
        _parse_dict_sections parses a list containing python dictionaries of v1.0 odML
        style sections into lxml.Element XML equivalents and appends the parsed Sections
        to the provided lxml.Element parent.

        :param parent_element: lxml.Element to which parsed sections will be appended.
        :param section_list: list of python dictionaries containing valid v1.0 odML
                             Sections.
        """
        for section in section_list:
            sec = ET.Element("section")
            for element in section:
                if element == 'properties':
                    cls._parse_dict_properties(sec, section['properties'])
                elif element == 'sections':
                    cls._parse_dict_sections(sec, section['sections'])
                elif element:
                    elem = ET.Element(element)
                    elem.text = section[element]
                    sec.append(elem)

            parent_element.append(sec)

    @classmethod
    def _parse_dict_properties(cls, parent_element, props_list):
        """
        _parse_dict_properties parses a list containing python dictionaries of v1.0 odML
        style properties into lxml.Element XML equivalents and appends the parsed
        Properties to the provided lxml.Element parent.

        :param parent_element: lxml.Element to which parsed properties will be appended.
        :param props_list: list of python dictionaries containing valid v1.0 odML
                           Properties.
        """
        for curr_prop in props_list:
            prop = ET.Element("property")
            for element in curr_prop:
                if element == 'values':
                    cls._parse_dict_values(prop, curr_prop['values'])
                elif element:
                    elem = ET.Element(element)
                    elem.text = curr_prop[element]
                    prop.append(elem)

            parent_element.append(prop)

    @staticmethod
    def _parse_dict_values(parent_element, value_list):
        """
        _parse_dict_values parses a list containing python dictionaries of v1.0 odML
        style values into lxml.Element XML equivalents and appends the parsed
        Values to the provided lxml.Element parent.

        :param parent_element: lxml.Element to which parsed values will be appended.
        :param value_list: list of python dictionaries containing valid v1.0 odML Values.
        """
        for value in value_list:
            val = ET.Element("value")
            for element in value:
                if element:
                    if element == 'value':
                        val.text = str(value[element])
                    else:
                        elem = ET.Element(element)
                        elem.text = str(value[element])
                        val.append(elem)

            parent_element.append(val)

    def _convert(self, tree):
        """
        Converts an lxml.ElementTree containing a v1.0 odML document to odML v1.1.
        Unites multiple value objects and moves all supported Value elements to
        its parent Property. Exports only Document, Section and Property elements,
        that are supported by odML v1.1.

        :param tree: lxml.ElementTree containing a v1.0 odML document.
        """
        # Reset status messages
        self.conversion_log = []

        tree = self._replace_same_name_entities(tree)
        root = tree.getroot()
        root.set("version", FORMAT_VERSION)

        # Handle Values, exclude unsupported Property attributes and unnamed Properties.
        self._handle_properties(root)

        # Exclude unsupported Section attributes, ignore comments, handle repositories.
        for sec in root.iter("section"):
            sec_name = sec.find("name").text
            for elem in sec:
                if elem.tag not in Section.arguments_keys and isinstance(elem.tag, str):
                    self._log("[Info] Omitted non-Section attribute "
                              "'%s: %s/%s'" % (sec_name, elem.tag, elem.text))
                    sec.remove(elem)
                    continue

                if elem.tag == "repository":
                    self._handle_repository(elem)
                elif elem.tag == "include":
                    self._handle_include(elem)

        # Exclude unsupported Document attributes, ignore comments, handle repositories.
        for elem in root:
            if elem.tag not in Document.arguments_keys and isinstance(elem.tag, str):
                self._log("[Info] Omitted non-Document "
                          "attribute '%s/%s'" % (elem.tag, elem.text))
                root.remove(elem)
                continue

            if elem.tag == "repository":
                self._handle_repository(elem)

        tree = self._check_add_ids(tree)

        return tree

    def _handle_include(self, element):
        """
        _handle_include checks whether a provided include element is
        v1.1 compatible and logs a warning message otherwise.

        :param element: lxml element containing the provided include link.
        """
        content = element.text
        cache = {}
        term_handler = Terminologies(cache)
        term = term_handler.load(element.text)

        # If the include url can be loaded and parsed, everything is fine.
        if term is not None:
            return

        # If the include url is a v1.0 odml-terminology one,
        # check whether a v1.1 is available and use it instead.
        if '/'.join([REPOSITORY_BASE, "v1.0"]) in element.text:
            element.text = element.text.replace('v1.0', 'v1.1')
            term = term_handler.load(element.text)

            if term is not None:
                msg = "[Info] Replaced Section.include url '%s' with '%s'." \
                      % (content, element.text)
                self._log(msg)
                return

        # Log a warning, if no v1.1 compatible url can be provided.
        self._log("[Warning] Section include file '%s' "
                  "is not odML v1.1 compatible." % content)

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
        if '/'.join([REPOSITORY_BASE, "v1.0"]) in element.text:
            element.text = element.text.replace('v1.0', 'v1.1')
            term = term_handler.load(element.text)

            if term is not None:
                msg = "[Info] Replaced repository url '%s' with '%s'." \
                      % (content, element.text)
                self._log(msg)
                return

        # Print a warning, if no v1.1 compatible repository url can be provided.
        self._log("[Warning] Repository file '%s' is not odML v1.1 compatible." % content)

    def _handle_properties(self, root):
        """
        Removes all property elements without name attribute, converts Value
        elements from v1.0 to v1.1 style and removes unsupported Property elements.

        :param root: lxml.ElementTree containing a v1.0 odML property list.
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
                        main_val.text += "," + value.text.strip()
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

            # Reverse map "dependency_value", exclude unsupported Property attributes.
            for elem in prop:
                if elem.tag == "dependency_value":
                    elem.tag = "dependencyvalue"

                if (elem.tag not in Property.arguments_keys and
                        isinstance(elem.tag, str)):
                    self._log("[Info] Omitted non-Property attribute "
                              "'%s: %s/%s'" % (prop_id, elem.tag, elem.text))
                    prop.remove(elem)

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
                elif val_elem.tag in Property.arguments_keys:
                    new_elem = ET.Element(val_elem.tag)
                    new_elem.text = val_elem.text

                    if val_elem.tag in ["type", "dtype"] and val_elem.text == "binary":
                        new_elem.text = "text"
                        self._log("[Warning] Replacing unsupported value type "
                                  "'binary' with 'text' (%s)" % log_id)

                    parent.append(new_elem)
                elif val_elem.tag in self._version_map:
                    new_elem = ET.Element(self._version_map[val_elem.tag])
                    new_elem.text = val_elem.text

                    if val_elem.tag in ["type", "dtype"] and val_elem.text == "binary":
                        new_elem.text = "text"
                        self._log("[Warning] Replacing unsupported value type "
                                  "'binary' with 'text' (%s)" % log_id)

                    parent.append(new_elem)
                else:
                    self._log("[Info] Omitted non-Value attribute '%s: %s/%s'"
                              % (log_id, val_elem.tag, val_elem.text))

    @classmethod
    def _replace_same_name_entities(cls, tree):
        """
        Changes same section names in the doc by adding <-{index}>
        to the next section occurrences.

        :param tree: ElementTree of the doc
        :return: ElementTree
        """
        sec_map = {}
        prop_map = {}
        root = tree.getroot()
        for sec in root.iter("section"):

            sec_name = sec.find("name")
            if sec_name is not None:
                cls._change_entity_name(tree, sec_map, sec_name)
            else:
                raise Exception("Section attribute name is not specified")

            for prop in sec.iter("property"):
                if prop.getparent() == sec:
                    prop_name = prop.find("name")
                    if prop_name is not None:
                        cls._change_entity_name(tree, prop_map, prop_name)
            prop_map.clear()
        return tree

    @staticmethod
    def _change_entity_name(tree, elem_map, name):
        """
        Adds numbering to identical element names where their odml.Section
        or odml.Property parents reside on the same level in the tree.

        :param tree: The element tree containing the 'name' element.
        :param elem_map: lxml path to occurrence maps of named Sections or Properties.
        :param name: lxml element containing the name text of a Section or Property.
        """
        named_path = "%s:%s" % (tree.getpath(name.getparent().getparent()), name.text)
        if named_path not in elem_map:
            elem_map[named_path] = 1
        else:
            elem_map[named_path] += 1
            name.text += "-" + str(elem_map[named_path])

    def _check_add_ids(self, tree):
        """
        Checks, whether elements (properties) possess an UUID
        and adds one in case of absence.

        :param tree: ElementTree of the doc
        :return: ElementTree
        """
        root = tree.getroot()
        self._add_id(root)
        for sec in root.iter("section"):
            self._add_id(sec)
            for prop in sec.iter("property"):
                self._add_id(prop)

        return tree

    @staticmethod
    def _add_id(element):
        """
        Checks, whether an element possesses an ID. If yes, make sure it has
        the right format. Otherwise a new UUID is created.

        :param element: lxml element.
        """
        oid = element.find("id")
        new_id = ET.Element("id")
        new_id.text = str(uuid.uuid4())
        if oid is not None:
            try:
                if oid.text is not None:
                    new_id.text = str(uuid.UUID(oid.text))
            except ValueError as exc:
                print(exc)
            element.remove(oid)
        element.append(new_id)

    def _log(self, msg):
        """
        Adds the passed message to the conversion_log attribute and
        prints the message to the command line.

        :param msg: string that is appended to the conversion log and
                    printed to the command line.
        """
        self.conversion_log.append(msg)
        print(msg)

    def __str__(self):
        tree = self.convert()
        return ET.tounicode(tree, pretty_print=True) if tree else ""

    def __unicode__(self):
        tree = self.convert()
        return ET.tounicode(tree, pretty_print=True) if tree else ""

    def convert(self, backend="XML"):
        """
        This method returns the content of the provided file object converted
        to odML version 1.1 as a string object which is directly consumable
        by the odml.tools.ODMLReader.
        Will raise an Exception, if the backend format is not supported.

        :param backend: File format of the source file. 'JSON', 'YAML' and 'XML' are
                        supported. Default backend is 'XML'.
        :returns an odML v1.1 document as an XML string
        """
        if backend.upper() == "JSON":
            old_tree = self._parse_json()
        elif backend.upper() == "YAML":
            old_tree = self._parse_yaml()
        elif backend.upper() == "XML":
            old_tree = self._parse_xml()
        else:
            raise Exception("Unknown backend, only XML, JSON and YAML are supported.")

        tree = self._convert(old_tree)
        return ET.tounicode(tree, pretty_print=True) if tree else ""

    def write_to_file(self, filename, backend="XML"):
        """
        This method converts the content of the provided converter file object
        to odML version 1.1 and writes the results to `filename`.

        :param filename: Output file.
        :param backend: Format of the source file, default is XML.
        """
        data = self.convert(backend)
        if sys.version_info < (3,):
            data = data.encode('utf-8')

        ext = [".xml", ".odml"]
        if not filename.endswith(tuple(ext)):
            filename = "%s.xml" % filename

        if data and "<odML " in data:
            with open(filename, "w") as file:
                file.write("%s\n" % XML_HEADER)
                file.write(data)
