#!/usr/bin/env python
"""

A generic odML parsing module.

Parses odML files and documents.

"""

import yaml
import json
from odml import format
from . import xmlparser


class ODMLWriter:
    '''
        A generic odML document writer, for XML, YAML and JSON.

        Usage:
            xml_writer = ODMLWriter(parser='XML')
            xml_writer.write_file(odml_document, filepath)
    '''

    def __init__(self, parser='XML'):
        self.doc = None  # odML document
        self.parsed_doc = None  # Python dictionary object
        self.parser = parser.upper()

    def to_dict(self, odml_document):
        parsed_doc = {}

        for i in format.Document._args:
            attr = i
            if i in format.Document._map:
                attr = format.Document._map[i]
            if hasattr(odml_document, attr):
                if attr == 'sections':
                    sections = self.get_sections(odml_document.sections)
                    parsed_doc[attr] = sections
                else:
                    t = getattr(odml_document, attr)
                    if t:
                        parsed_doc[attr] = t

        self.parsed_doc = parsed_doc

    def get_sections(self, section_list):

        section_seq = []

        for section in section_list:
            section_dict = {}
            for i in format.Section._args:
                attr = i
                if i in format.Section._map:
                    attr = format.Section._map[i]
                if hasattr(section, attr):
                    if attr == 'properties':
                        properties = self.get_properties(section.properties)
                        section_dict[attr] = properties
                    elif attr == 'sections':
                        sections = self.get_sections(section.sections)
                        section_dict[attr] = sections
                    else:
                        t = getattr(section, attr)
                        if t:
                            section_dict[attr] = t

            section_seq.append(section_dict)

        return section_seq

    def get_properties(self, props_list):

        props_seq = []

        for prop in props_list:
            prop_dict = {}
            for i in format.Property._args:
                attr = i
                if i in format.Property._map:
                    attr = format.Property._map[i]
                if hasattr(prop, attr):
                    t = getattr(prop, attr)
                    if (t == []) or t:  # Even if 'value' is empty, allow '[]'
                        prop_dict[attr] = t

            props_seq.append(prop_dict)
        
        return props_seq

    def write_file(self, odml_document, filename):

        if self.parser == 'XML':
            xmlparser.XMLWriter(odml_document).write_file(filename)
        else:
            self.to_dict(odml_document)
            f = open(filename, 'w')
            if self.parser == 'YAML':
                f.write(yaml.dump(self.parsed_doc, default_flow_style=False))
            elif self.parser == 'JSON':
                f.write(json.dumps(self.parsed_doc, indent=4))
            f.close()


class ODMLReader:
    """
    A reader to parse odML files or strings into odml documents,
    based on the given data exchange format, like XML, YAML or JSON.

    Usage:
        yaml_odml_doc = ODMLReader(parser='YAML').fromFile(open("odml_doc.yaml"))
        json_odml_doc = ODMLReader(parser='JSON').fromFile(open("odml_doc.json"))
    """

    def __init__(self, parser='XML'):
        
        self.doc = None  # odML document
        self.parsed_doc = None  # Python dictionary object
        self.parser = parser.upper()

    def is_valid_attribute(self, attr, fmt):
        if attr in fmt._args:
            return attr
        if fmt.revmap(attr):
            return attr
        print("Invalid element <%s> inside <%s> tag" % (attr, fmt.__class__.__name__))
        return None

    def to_odml(self):
        doc_attrs = {}
        doc_secs = []

        for i in self.parsed_doc:
            attr = self.is_valid_attribute(i, format.Document)
            if attr == 'sections':
                doc_secs = self.parse_sections(self.parsed_doc['sections'])
            elif attr:
                doc_attrs[i] = self.parsed_doc[i]
            
        doc = format.Document.create(**doc_attrs)
        doc._sections = doc_secs
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
            sec._props = sec_props
            sec._sections = children_secs
            odml_sections.append(sec)

        return odml_sections


    def parse_properties(self, props_list):
        odml_props = []

        for _property in props_list:
            prop_attrs = {}
            value = []

            for i in _property:
                attr = self.is_valid_attribute(i, format.Property)
                if attr == 'value':
                    value = _property['value']
                if attr:
                    prop_attrs[attr] = _property[attr]

            prop = format.Property.create(**prop_attrs)
            prop._value = value
            odml_props.append(prop)

        return odml_props


    def fromFile(self, file):

        if self.parser == 'XML':
            odml_doc = xmlparser.XMLReader().fromFile(file)
            self.doc = odml_doc
            return odml_doc

        elif self.parser == 'YAML':
            try:
                self.parsed_doc = yaml.load(file)
            except yaml.parser.ParserError as e:
                print(e)
                return
            finally:
                file.close()
            return self.to_odml()

        elif self.parser == 'JSON':
            try:
                self.parsed_doc = json.load(file)
            except json.decoder.JSONDecodeError as e:
                print(e)
                return
            finally:
                file.close()
            return self.to_odml()


    def fromString(self, string):

        if self.parser == 'XML':
            odml_doc = xmlparser.XMLReader().fromString(string)
            self.doc = odml_doc
            return self.doc
        elif self.parser == 'YAML':
            try:
                odml_doc = yaml.load(string)
            except yaml.parser.ParserError as e:
                print(e)
                return
            return self.to_odml()
        elif self.parser == 'JSON':
            try:
                odml_doc = json.loads(string)
            except json.decoder.JSONDecodeError as e:
                print(e)
                return
            return self.to_odml()
