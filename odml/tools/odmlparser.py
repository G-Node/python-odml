#!/usr/bin/env python
"""

A generic odML parsing module.

Parses odML files and documents.

"""

import json
import yaml

from .. import format
from . import xmlparser
from .dict_parser import DictWriter, DictReader
from ..info import FORMAT_VERSION
from .parser_utils import ParserException
from .parser_utils import SUPPORTED_PARSERS
from .rdf_converter import RDFReader
from ..validation import Validation


class ODMLWriter:
    """
        A generic odML document writer, for XML, YAML and JSON.

        Usage:
            xml_writer = ODMLWriter(parser='XML')
            xml_writer.write_file(odml_document, filepath)
    """

    def __init__(self, parser='XML'):
        self.doc = None  # odML document
        self.parsed_doc = None  # Python dictionary object equivalent
        parser = parser.upper()
        if parser not in SUPPORTED_PARSERS:
            raise NotImplementedError("'%s' odML parser does not exist!" % parser)
        self.parser = parser

    def write_file(self, odml_document, filename):
        # Write document only if it does not contain validation errors.
        validation = Validation(odml_document)
        msg = ""
        for e in validation.errors:
            if e.is_error:
                msg += "\n\t- %s %s: %s" % (e.obj, e.type, e.msg)
        if msg != "":
            msg = "Resolve document validation errors before saving %s" % msg
            raise ParserException(msg)

        file = open(filename, 'w')
        file.write(self.to_string(odml_document))
        file.close()

    def to_string(self, odml_document):
        string_doc = ''

        if self.parser == 'XML':
            string_doc = str(xmlparser.XMLWriter(odml_document))
        else:
            self.parsed_doc = DictWriter().to_dict(odml_document)

            odml_output = {'Document': self.parsed_doc,
                           'odml-version': FORMAT_VERSION}

            if self.parser == 'YAML':
                string_doc = yaml.dump(odml_output, default_flow_style=False)
            elif self.parser == 'JSON':
                string_doc = json.dumps(odml_output, indent=4)
        return string_doc


class ODMLReader:
    """
    A reader to parse odML files or strings into odml documents,
    based on the given data exchange format, like XML, YAML or JSON.

    Usage:
        yaml_odml_doc = ODMLReader(parser='YAML').from_file("odml_doc.yaml")
        json_odml_doc = ODMLReader(parser='JSON').from_file("odml_doc.json")
    """

    def __init__(self, parser='XML'):
        self.odml_version = None  # odML version of input file
        self.doc = None  # odML document
        self.parsed_doc = None  # Python dictionary object equivalent
        parser = parser.upper()
        if parser not in SUPPORTED_PARSERS:
            raise NotImplementedError("'%s' odML parser does not exist!" % parser)
        self.parser = parser
        self.warnings = []

    def is_valid_attribute(self, attr, fmt):
        if attr in fmt.arguments_keys():
            return attr
        if fmt.revmap(attr):
            return attr
        msg = "Invalid element <%s> inside <%s> tag" % (attr, fmt.__class__.__name__)
        print(msg)
        self.warnings.append(msg)
        return None

    def to_odml(self):
        # Parse only odML documents of supported format versions.
        if 'odml-version' not in self.parsed_doc:
            raise ParserException("Invalid odML document: Could not find odml-version.")
        elif self.parsed_doc.get('odml-version') != FORMAT_VERSION:
            msg = ("Cannot read file: invalid odML document format version '%s'. \n"
                   "This package supports odML format versions: '%s'."
                   % (self.parsed_doc.get('odml-version'), FORMAT_VERSION))
            raise ParserException(msg)

        self.odml_version = self.parsed_doc.get('odml-version')
        self.parsed_doc = self.parsed_doc['Document']

        doc_attrs = {}
        doc_secs = []

        for i in self.parsed_doc:
            attr = self.is_valid_attribute(i, format.Document)
            if attr == 'sections':
                doc_secs = self.parse_sections(self.parsed_doc['sections'])
            elif attr:
                doc_attrs[i] = self.parsed_doc[i]

        doc = format.Document.create(**doc_attrs)
        for sec in doc_secs:
            doc.append(sec)
        self.doc = doc
        return self.doc

    def parse_sections(self, section_list):

        odml_sections = []

        for section in section_list:
            sec_attrs = {}
            children_secs = []
            sec_props = []
            for i in section:
                attr = self.is_valid_attribute(i, format.Section)
                if attr == 'properties':
                    sec_props = self.parse_properties(section['properties'])
                elif attr == 'sections':
                    children_secs = self.parse_sections(section['sections'])
                elif attr:
                    sec_attrs[attr] = section[attr]

            sec = format.Section.create(**sec_attrs)
            for prop in sec_props:
                sec.append(prop)
            for child_sec in children_secs:
                sec.append(child_sec)
            odml_sections.append(sec)

        return odml_sections

    def parse_properties(self, props_list):
        odml_props = []

        for _property in props_list:
            prop_attrs = {}
            values = []

            for i in _property:
                attr = self.is_valid_attribute(i, format.Property)
                if attr == 'value':
                    values = _property['value']
                if attr:
                    prop_attrs[attr] = _property[attr]

            prop = format.Property.create(**prop_attrs)
            prop._value = values
            odml_props.append(prop)

        return odml_props

    def from_file(self, file, doc_format=None):

        if self.parser == 'XML':
            par = xmlparser.XMLReader(ignore_errors=True)
            self.warnings = par.warnings
            odml_doc = par.from_file(file)
            self.doc = odml_doc
            return odml_doc

        elif self.parser == 'YAML':
            with open(file) as yaml_data:
                try:
                    self.parsed_doc = yaml.load(yaml_data)
                except yaml.parser.ParserError as e:
                    print(e)
                    return

            self.doc = DictReader().to_odml(self.parsed_doc)
            return self.doc

        elif self.parser == 'JSON':
            with open(file) as json_data:
                try:
                    self.parsed_doc = json.load(json_data)
                except ValueError as e:  # Python 2 does not support JSONDecodeError
                    print("JSON Decoder Error: %s" % e)
                    return

            self.doc = DictReader().to_odml(self.parsed_doc)
            return self.doc

        elif self.parser == 'RDF':
            if not doc_format:
                raise KeyError("Format of the rdf file was not specified")

            self.doc = RDFReader().from_file(file, doc_format)
            return self.doc

    def from_string(self, string, doc_format=None):

        if self.parser == 'XML':
            odml_doc = xmlparser.XMLReader().from_string(string)
            self.doc = odml_doc
            return self.doc

        elif self.parser == 'YAML':
            try:
                self.parsed_doc = yaml.load(string)
            except yaml.parser.ParserError as e:
                print(e)
                return

            self.doc = DictReader().to_odml(self.parsed_doc)
            return self.doc

        elif self.parser == 'JSON':
            try:
                self.parsed_doc = json.loads(string)
            except ValueError as e:  # Python 2 does not support JSONDecodeError
                print("JSON Decoder Error: %s" % e)
                return

            self.doc = DictReader().to_odml(self.parsed_doc)
            return self.doc

        elif self.parser == 'RDF':
            if not doc_format:
                raise KeyError("Format of the rdf file was not specified")

            self.doc = RDFReader().from_string(string, doc_format)
            return self.doc
