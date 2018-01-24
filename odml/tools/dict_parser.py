"""
Dict parser converts the content of a dictionary
into a proper and verified odML document.
"""

from .. import format as odmlfmt
from ..info import FORMAT_VERSION
from .parser_utils import ParserException


class DictReader:
    """
    A reader to parse dictionaries with odML content into,
    full a proper odML document.
    """

    def __init__(self):
        self.parsed_doc = None  # Python dictionary object equivalent
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

    def to_odml(self, parsed_doc):
        self.parsed_doc = parsed_doc

        # Parse only odML documents of supported format versions.
        if 'odml-version' not in self.parsed_doc:
            raise ParserException("Invalid odML document: Could not find odml-version.")

        elif self.parsed_doc.get('odml-version') != FORMAT_VERSION:
            msg = ("Cannot read file: invalid odML document format version '%s'. \n"
                   "This package supports odML format versions: '%s'."
                   % (self.parsed_doc.get('odml-version'), FORMAT_VERSION))
            raise ParserException(msg)

        self.parsed_doc = self.parsed_doc['Document']

        doc_attrs = {}
        doc_secs = []

        for i in self.parsed_doc:
            attr = self.is_valid_attribute(i, odmlfmt.Document)
            if attr == 'sections':
                doc_secs = self.parse_sections(self.parsed_doc['sections'])
            elif attr:
                doc_attrs[i] = self.parsed_doc[i]

        doc = odmlfmt.Document.create(**doc_attrs)
        for sec in doc_secs:
            doc.append(sec)

        return doc

    def parse_sections(self, section_list):
        odml_sections = []

        for section in section_list:
            sec_attrs = {}
            children_secs = []
            sec_props = []

            for i in section:
                attr = self.is_valid_attribute(i, odmlfmt.Section)
                if attr == 'properties':
                    sec_props = self.parse_properties(section['properties'])
                elif attr == 'sections':
                    children_secs = self.parse_sections(section['sections'])
                elif attr:
                    sec_attrs[attr] = section[attr]

            sec = odmlfmt.Section.create(**sec_attrs)
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
                attr = self.is_valid_attribute(i, odmlfmt.Property)
                if attr == 'value':
                    values = _property['value']
                if attr:
                    prop_attrs[attr] = _property[attr]

            prop = odmlfmt.Property.create(**prop_attrs)
            prop._value = values
            odml_props.append(prop)

        return odml_props
