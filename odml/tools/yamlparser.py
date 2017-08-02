#!/usr/bin/env python
"""
The YAML parsing module.

Parses odML files.

"""
import yaml
from odml import format


class YAMLWriter:

    def __init__(self, odml_document):
        self.doc = odml_document
        self.yaml_doc = {}
        self.to_yaml()

    def to_yaml(self):
        yaml_doc = {}

        for i in format.Document._args:
            attr = i
            if i in format.Document._map:
                attr = format.Document._map[i]
            if hasattr(self.doc, attr):
                if attr == 'sections':
                    sections = self.get_sections(self.doc.sections)
                    yaml_doc[attr] = sections
                else:
                    t = getattr(self.doc, attr)
                    if t:
                        yaml_doc[attr] = t

        self.yaml_doc = yaml_doc

    def get_sections(self, section_list):

        section_yaml_seq = []

        for section in section_list:
            section_yaml = {}
            for i in format.Section._args:
                attr = i
                if i in format.Section._map:
                    attr = format.Section._map[i]
                if hasattr(section, attr):
                    if attr == 'properties':
                        properties = self.get_properties(section.properties)
                        section_yaml[attr] = properties
                    elif attr == 'sections':
                        sections = self.get_sections(section.sections)
                        section_yaml[attr] = sections
                    else:
                        t = getattr(section, attr)
                        if t:
                            section_yaml[attr] = t

            section_yaml_seq.append(section_yaml)

        return section_yaml_seq

    def get_properties(self, props_list):

        props_yaml_list = []

        for prop in props_list:
            prop_yaml = {}
            for i in format.Property._args:
                attr = i
                if i in format.Property._map:
                    attr = format.Property._map[i]
                if hasattr(prop, attr):
                    t = getattr(prop, attr)
                    if (t == []) or t:  # Even if 'value' is empty, allow '[]'
                        prop_yaml[attr] = t

            props_yaml_list.append(prop_yaml)
        
        return props_yaml_list

    def write_file(self, filename):
        f = open(filename, 'w')
        f.write(yaml.dump(self.yaml_doc, default_flow_style=False))
        f.close()


class YAMLReader:
    """
    A reader to parse YAML files or strings into odml data documents.

    Usage:

        >>> doc = YAMLReader().fromFile("odml_doc.yaml")
    """

    def __init__(self):
        self.doc = None
        self.yaml_doc = None

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

        for i in self.yaml_doc:
            attr = self.is_valid_attribute(i, format.Document)
            if attr == 'sections':
                doc_secs = self.parse_sections(self.yaml_doc['sections'])
            elif attr:
                doc_attrs[i] = self.yaml_doc[i]
            
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
        try:
            self.yaml_doc = yaml.load(file)
        except yaml.parser.ParserError as e:
            print(e)
            return
        return self.to_odml()

    def fromString(self, string):
        try:
            self.yaml_doc = yaml.load(string)
        except yaml.parser.ParserError as e:
            print(e)
            return
        return self.to_odml()
