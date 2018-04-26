#!/usr/bin/env python
"""
A generic odML parsing module.

Parses odML files and documents.
"""

import datetime
import json
import yaml

from . import xmlparser
from .dict_parser import DictWriter, DictReader
from ..info import FORMAT_VERSION
from .parser_utils import ParserException
from .parser_utils import SUPPORTED_PARSERS
from .rdf_converter import RDFReader, RDFWriter
from ..validation import Validation


class ODMLWriter:
    """
        A generic odML document writer, for XML, YAML and JSON.

        Usage:
            xml_writer = ODMLWriter(parser='XML')
            xml_writer.write_file(odml_document, filepath)
    """

    def __init__(self, parser='XML'):
        self.parsed_doc = None  # Python dictionary object equivalent
        parser = parser.upper()

        if parser not in SUPPORTED_PARSERS:
            raise NotImplementedError("'%s' odML parser does not exist!" % parser)

        self.parser = parser

    def write_file(self, odml_document, filename):
        # Write document only if it does not contain validation errors.
        validation = Validation(odml_document)
        msg = ""
        for err in validation.errors:
            if err.is_error:
                msg += "\n\t- %s %s: %s" % (err.obj, err.type, err.msg)
        if msg != "":
            msg = "Resolve document validation errors before saving %s" % msg
            raise ParserException(msg)

        with open(filename, 'w') as file:
            # Add XML header to support odML stylesheets.
            if self.parser == 'XML':
                file.write(xmlparser.XMLWriter.header)

            file.write(self.to_string(odml_document))

    def to_string(self, odml_document):
        string_doc = ''

        if self.parser == 'XML':
            string_doc = str(xmlparser.XMLWriter(odml_document))
        elif self.parser == "RDF":
            # Use turtle as default output format for now.
            string_doc = RDFWriter(odml_document).get_rdf_str("turtle")
        else:
            self.parsed_doc = DictWriter().to_dict(odml_document)

            odml_output = {'Document': self.parsed_doc,
                           'odml-version': FORMAT_VERSION}

            if self.parser == 'YAML':
                string_doc = yaml.dump(odml_output, default_flow_style=False)
            elif self.parser == 'JSON':
                string_doc = json.dumps(odml_output, indent=4,
                                        cls=JSONDateTimeSerializer)

        return string_doc


# Required to serialize datetime values with JSON.
class JSONDateTimeSerializer(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return str(o)

        return json.JSONEncoder.default(self, o)


class ODMLReader:
    """
    A reader to parse odML files or strings into odml documents,
    based on the given data exchange format, like XML, YAML, JSON or RDF.

    Usage:
        yaml_odml_doc = ODMLReader(parser='YAML').from_file("odml_doc.yaml")
        json_odml_doc = ODMLReader(parser='JSON').from_file("odml_doc.json")
    """

    def __init__(self, parser='XML'):
        self.doc = None  # odML document
        self.parsed_doc = None  # Python dictionary object equivalent
        parser = parser.upper()
        if parser not in SUPPORTED_PARSERS:
            raise NotImplementedError("'%s' odML parser does not exist!" % parser)
        self.parser = parser
        self.warnings = []

    def from_file(self, file, doc_format=None):

        if self.parser == 'XML':
            par = xmlparser.XMLReader(ignore_errors=True)
            self.warnings = par.warnings
            self.doc = par.from_file(file)
            return self.doc

        elif self.parser == 'YAML':
            with open(file) as yaml_data:
                try:
                    self.parsed_doc = yaml.load(yaml_data)
                except yaml.parser.ParserError as err:
                    print(err)
                    return

            self.doc = DictReader().to_odml(self.parsed_doc)
            return self.doc

        elif self.parser == 'JSON':
            with open(file) as json_data:
                try:
                    self.parsed_doc = json.load(json_data)
                except ValueError as err:  # Python 2 does not support JSONDecodeError
                    print("JSON Decoder Error: %s" % err)
                    return

            self.doc = DictReader().to_odml(self.parsed_doc)
            return self.doc

        elif self.parser == 'RDF':
            if not doc_format:
                raise ValueError("Format of the rdf file was not specified")

            self.doc = RDFReader().from_file(file, doc_format)
            return self.doc

    def from_string(self, string, doc_format=None):

        if self.parser == 'XML':
            self.doc = xmlparser.XMLReader().from_string(string)
            return self.doc

        elif self.parser == 'YAML':
            try:
                self.parsed_doc = yaml.load(string)
            except yaml.parser.ParserError as err:
                print(err)
                return

            self.doc = DictReader().to_odml(self.parsed_doc)
            return self.doc

        elif self.parser == 'JSON':
            try:
                self.parsed_doc = json.loads(string)
            except ValueError as err:  # Python 2 does not support JSONDecodeError
                print("JSON Decoder Error: %s" % err)
                return

            self.doc = DictReader().to_odml(self.parsed_doc)
            return self.doc

        elif self.parser == 'RDF':
            if not doc_format:
                raise ValueError("Format of the rdf file was not specified")

            self.doc = RDFReader().from_string(string, doc_format)
            return self.doc
