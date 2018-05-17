"""
Dict parser converts the content of a dictionary
into a proper and verified odML document.
"""

from .. import format as odmlfmt
from ..info import FORMAT_VERSION
from .parser_utils import InvalidVersionException, ParserException


class DictWriter:
    """
    A writer to parse an odML document to a Python dictionary object equivalent.
    """

    def __init__(self):
        self.doc = None  # odML document

    def to_dict(self, odml_document):
        self.doc = odml_document
        parsed_doc = {}

        for i in odmlfmt.Document.arguments_keys:
            attr = i
            if i in odmlfmt.Document.map_keys:
                attr = odmlfmt.Document.map(i)

            if hasattr(odml_document, attr):
                if attr == 'sections':
                    sections = self.get_sections(odml_document.sections)
                    parsed_doc[attr] = sections
                else:
                    tag = getattr(odml_document, attr)

                    if tag:
                        # Always use the arguments key attribute name when saving
                        parsed_doc[i] = tag

        return parsed_doc

    def get_sections(self, section_list):
        section_seq = []

        for section in section_list:
            section_dict = {}

            for i in odmlfmt.Section.arguments_keys:
                attr = i

                if i in odmlfmt.Section.map_keys:
                    attr = odmlfmt.Section.map(i)

                if hasattr(section, attr):
                    if attr == 'properties':
                        properties = self.get_properties(section.properties)
                        section_dict[attr] = properties
                    elif attr == 'sections':
                        sections = self.get_sections(section.sections)
                        section_dict[attr] = sections
                    else:
                        tag = getattr(section, attr)

                        if tag:
                            # Always use the arguments key attribute name when saving
                            section_dict[i] = tag

            section_seq.append(section_dict)

        return section_seq

    @staticmethod
    def get_properties(props_list):
        props_seq = []

        for prop in props_list:
            prop_dict = {}

            for i in odmlfmt.Property.arguments_keys:
                attr = i
                if i in odmlfmt.Property.map_keys:
                    attr = odmlfmt.Property.map(i)

                if hasattr(prop, attr):
                    tag = getattr(prop, attr)
                    if isinstance(tag, tuple):
                        prop_dict[attr] = list(tag)
                    elif (tag == []) or tag:  # Even if 'value' is empty, allow '[]'
                        # Custom odML tuples require special handling
                        # for save loading from file.
                        if attr == "value" and prop.dtype and \
                                prop.dtype.endswith("-tuple") and len(prop.value) > 0:
                            prop_dict["value"] = "(%s)" % ";".join(prop.value[0])
                        else:
                            # Always use the arguments key attribute name when saving
                            prop_dict[i] = tag

            props_seq.append(prop_dict)

        return props_seq


class DictReader:
    """
    A reader to parse dictionaries with odML content into a proper odML document.
    """

    def __init__(self):
        self.parsed_doc = None  # Python dictionary object equivalent
        self.warnings = []

    def is_valid_attribute(self, attr, fmt):
        if attr in fmt.arguments_keys:
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
        if 'Document' not in self.parsed_doc:
            msg = "Missing root element 'Document'"
            raise ParserException(msg)
        elif 'odml-version' not in self.parsed_doc:
            raise ParserException("Invalid odML document: Could not find odml-version.")

        elif self.parsed_doc.get('odml-version') != FORMAT_VERSION:
            msg = ("Cannot parse odML document with format version '%s'. \n"
                   "\tUse the 'tools.VersionConverter' to import previous odML formats."
                   % self.parsed_doc.get('odml-version'))
            raise InvalidVersionException(msg)

        self.parsed_doc = self.parsed_doc['Document']

        doc_attrs = {}
        doc_secs = []

        for i in self.parsed_doc:
            attr = self.is_valid_attribute(i, odmlfmt.Document)
            if attr == 'sections':
                doc_secs = self.parse_sections(self.parsed_doc['sections'])
            elif attr:
                # Make sure to always use the correct odml format attribute name
                doc_attrs[odmlfmt.Document.map(attr)] = self.parsed_doc[i]

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
                    # Make sure to always use the correct odml format attribute name
                    sec_attrs[odmlfmt.Section.map(attr)] = section[attr]

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

            for i in _property:
                attr = self.is_valid_attribute(i, odmlfmt.Property)
                if attr:
                    # Make sure to always use the correct odml format attribute name
                    prop_attrs[odmlfmt.Property.map(attr)] = _property[attr]

            prop = odmlfmt.Property.create(**prop_attrs)
            odml_props.append(prop)

        return odml_props
