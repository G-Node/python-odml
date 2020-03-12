#!/usr/bin/env python
"""
A generic odML parsing module. It parses odML files and documents.
All supported formats can be found in parser_utils.SUPPORTED_PARSERS.
"""

import datetime
import json
import sys

from os.path import basename

import yaml

from . import xmlparser
from .dict_parser import DictWriter, DictReader
from ..info import FORMAT_VERSION
from .parser_utils import ParserException
from .parser_utils import SUPPORTED_PARSERS
from .rdf_converter import RDFReader, RDFWriter
from ..validation import Validation

try:
    unicode = unicode
except NameError:
    unicode = str


class ODMLWriter:
    """
        A generic odML document writer for JSON, XML, YAML and RDF.
        The output format is specified on init.

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
        """
        Writes an odml.Document to a file using the format
        defined in the ODMLWriter.parser property. Supported formats are
        JSON, XML, YAML and RDF.
        Will raise a ParserException if the odml.Document is not valid.

        :param odml_document: odml.Document.
        :param filename: path and filename of the output file.
        """

        # Write document only if it does not contain validation errors.
        validation = Validation(odml_document)
        msg = ""
        for err in validation.errors:
            if err.is_error:
                msg += "\n\t- %s %s: %s" % (err.obj, err.rank, err.msg)
        if msg != "":
            msg = "Resolve document validation errors before saving %s" % msg
            raise ParserException(msg)

        with open(filename, 'w') as file:
            # Add XML header to support odML stylesheets.
            if self.parser == 'XML':
                file.write(xmlparser.XMLWriter.header)

            file.write(self.to_string(odml_document))

    def to_string(self, odml_document):
        """
        Parses an odml.Document to a string in the file format
        defined in the ODMLWriter.parser property. Supported formats are
        JSON, XML, YAML and RDF.

        :param odml_document: odml.Document.
        :return: string containing the content of the odml.Document in the
                 specified format.
        """
        string_doc = ''

        if self.parser == 'XML':
            string_doc = unicode(xmlparser.XMLWriter(odml_document))
        elif self.parser == "RDF":
            # Use XML as default output format for now.
            string_doc = RDFWriter(odml_document).get_rdf_str("xml")
        else:
            self.parsed_doc = DictWriter().to_dict(odml_document)

            odml_output = {'Document': self.parsed_doc,
                           'odml-version': FORMAT_VERSION}

            if self.parser == 'YAML':
                yaml.add_representer(datetime.time, yaml_time_serializer)
                string_doc = yaml.dump(odml_output, default_flow_style=False)
            elif self.parser == 'JSON':
                string_doc = json.dumps(odml_output, indent=4,
                                        cls=JSONDateTimeSerializer)

        if sys.version_info.major < 3:
            string_doc = string_doc.encode("utf-8")

        return string_doc


def yaml_time_serializer(dumper, data):
    """
    This function is required to serialize datetime.time as string objects
    when working with YAML as output format.
    """
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data))


class JSONDateTimeSerializer(json.JSONEncoder):
    """
    Required to serialize datetime objects as string objects when working with JSON
    as output format.
    """
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

    def __init__(self, parser='XML', show_warnings=True):
        """
        :param parser: odml parser; supported are 'XML', 'JSON', 'YAML' and 'RDF'.
        :param show_warnings: Toggle whether to print warnings to the command line.
        """
        self.doc = None  # odML document
        self.parsed_doc = None  # Python dictionary object equivalent
        parser = parser.upper()
        if parser not in SUPPORTED_PARSERS:
            raise NotImplementedError("'%s' odML parser does not exist!" % parser)
        self.parser = parser
        self.show_warnings = show_warnings
        self.warnings = []

    def from_file(self, file, doc_format=None):
        """
        Loads an odML document from a file. The ODMLReader.parser specifies the
        input file format. If the input file is an RDF file, the specific RDF format
        has to be provided as well.
        Available RDF formats: 'xml', 'n3', 'turtle', 'nt', 'pretty-xml',
        'trix', 'trig', 'nquads'.

        :param file: file path to load an odML document from.
        :param doc_format: Required for RDF files only and provides the specific format
                           of an RDF file.
        :return: parsed odml.Document
        """
        if self.parser == 'XML':
            par = xmlparser.XMLReader(ignore_errors=True,
                                      show_warnings=self.show_warnings)
            self.warnings = par.warnings
            self.doc = par.from_file(file)
            return self.doc

        if self.parser == 'YAML':
            with open(file) as yaml_data:
                try:
                    yaml.SafeLoader.add_constructor("tag:yaml.org,2002:python/unicode",
                                                    unicode_loader_constructor)
                    self.parsed_doc = yaml.safe_load(yaml_data)
                except yaml.parser.ParserError as err:
                    print(err)
                    return None

            par = DictReader(show_warnings=self.show_warnings)
            self.doc = par.to_odml(self.parsed_doc)
            # Provide original file name via the in memory document
            self.doc.origin_file_name = basename(file)
            return self.doc

        if self.parser == 'JSON':
            with open(file) as json_data:
                try:
                    self.parsed_doc = json.load(json_data)
                except ValueError as err:  # Python 2 does not support JSONDecodeError
                    print("JSON Decoder Error: %s" % err)
                    return None

            par = DictReader(show_warnings=self.show_warnings)
            self.doc = par.to_odml(self.parsed_doc)
            # Provide original file name via the in memory document
            self.doc.origin_file_name = basename(file)
            return self.doc

        if self.parser == 'RDF':
            if not doc_format:
                raise ValueError("Format of the rdf file was not specified")

            self.doc = RDFReader().from_file(file, doc_format)
            return self.doc

    def from_string(self, string, doc_format=None):
        """
        Loads an odML document from a string object. The ODMLReader.parser specifies the
        input file format. If the input string contains an RDF format,
        the specific RDF format has to be provided as well.
        Available RDF formats: 'xml', 'n3', 'turtle', 'nt', 'pretty-xml',
        'trix', 'trig', 'nquads'.

        :param string: file path to load an odML document from.
        :param doc_format: Required for RDF files only and provides the specific format
                           of an RDF file.
        :return: parsed odml.Document
        """

        if self.parser == 'XML':
            self.doc = xmlparser.XMLReader().from_string(string)
            return self.doc

        if self.parser == 'YAML':
            try:
                self.parsed_doc = yaml.safe_load(string)
            except yaml.parser.ParserError as err:
                print(err)
                return

            self.doc = DictReader().to_odml(self.parsed_doc)
            return self.doc

        if self.parser == 'JSON':
            try:
                self.parsed_doc = json.loads(string)
            except ValueError as err:  # Python 2 does not support JSONDecodeError
                print("JSON Decoder Error: %s" % err)
                return

            self.doc = DictReader().to_odml(self.parsed_doc)
            return self.doc

        if self.parser == 'RDF':
            if not doc_format:
                raise ValueError("Format of the rdf file was not specified")

            self.doc = RDFReader().from_string(string, doc_format)
            return self.doc


# Needed only for < Python 3
def unicode_loader_constructor(_, node):
    """
    Constructor for PyYAML to load unicode characters
    """
    return node.value
