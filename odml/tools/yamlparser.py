#!/usr/bin/env python
"""
The YAML parsing module.

Parses odML files.

"""
# TODO make this module a parser class, allow arguments (e.g.
# skip_errors=1 to parse even broken documents)
import sys
import csv
import yaml
from odml import format

try:
    unicode = unicode
except NameError:
    unicode = str


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



class YAMLReader:

    def __init__(self):
        pass

    def from_yaml(self, yaml_doc):
        pass

    def fromFile(self, filename):
        file = open(filename, 'r')
        yaml_doc = yaml.load(file)
        pass