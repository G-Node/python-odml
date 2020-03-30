"""
The dict_parser module provides access to the DictWriter and DictReader class.
Both handle the conversion of odML documents from and to Python dictionary objects.
"""

from .. import format as odmlfmt
from ..info import FORMAT_VERSION
from .parser_utils import InvalidVersionException, ParserException, odml_tuple_export


def parse_cardinality(vals):
    """
    Parses an odml specific cardinality from an input value.

    If the input content is valid, returns an appropriate tuple.
    Returns None if the input is empty or the content cannot be
    properly parsed.

    :param vals: list or tuple
    :return: None or 2-tuple
    """
    if not vals:
        return None

    if isinstance(vals, (list, tuple)) and len(vals) == 2:
        min_val = vals[0]
        max_val = vals[1]

        if min_val is None or str(min_val).strip() == "None":
            min_val = None

        if max_val is None or str(max_val).strip() == "None":
            max_val = None

        min_int = isinstance(min_val, int) and min_val >= 0
        max_int = isinstance(max_val, int) and max_val >= 0

        if min_int and max_int and max_val > min_val:
            return min_val, max_val

        if min_int and not max_val:
            return min_val, None

        if max_int and not min_val:
            return None, max_val

    # We were not able to properly parse the current cardinality, so add
    # an appropriate Error/Warning once the reader 'ignore_errors' option has been implemented.
    return None


class DictWriter:
    """
    A writer to parse an odml.Document to a Python dictionary object equivalent.
    """

    def __init__(self):
        self.doc = None  # odML document

    def to_dict(self, odml_document):
        """
        Parses a full odml.Document to a Python dict object. Will also parse any
        contained odml.Sections, their subsections and odml.Properties.

        :param odml_document: an odml.Document.
        :return: parsed odml.Document as a Python dict object.
        """
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
        """
        Parses a list of odml.Sections to a Python dict object. Will also parse any
        contained subsections and odml.Properties.

        :param section_list: list of odml.Sections.
        :return: list of parsed odml.Sections as a single Python dict object.
        """
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
        """
        Parses a list of odml.Properties to a Python dict object.

        :param props_list: list of odml.Properties.
        :return: list of parsed odml.Properties as a single Python dict object.
        """
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
                    elif (tag == []) or tag:  # Even if 'values' is empty, allow '[]'
                        # Custom odML tuples require special handling.
                        if attr == "values" and prop.dtype and \
                                prop.dtype.endswith("-tuple") and prop.values:
                            prop_dict["value"] = odml_tuple_export(prop.values)
                        else:
                            # Always use the arguments key attribute name when saving
                            prop_dict[i] = tag

            props_seq.append(prop_dict)

        return props_seq


class DictReader:
    """
    A reader to parse dictionaries with odML content into an odml.Document.
    """

    def __init__(self, show_warnings=True):
        """
        :param show_warnings: Toggle whether to print warnings to the command line.
                              Any warnings can be accessed via the Reader's class
                              warnings attribute after parsing is done.
        """
        self.parsed_doc = None  # Python dictionary object equivalent
        self.show_warnings = show_warnings
        self.warnings = []

    def is_valid_attribute(self, attr, fmt):
        """
        Checks whether a provided attribute is valid for a provided odml class
        (Document, Section, Property).

        :param attr: Python dictionary tag that will be checked if it is a valid
                     attribute for the provided format class.
        :param fmt: required odml format class format.Document, format.Section or
                    format.Property against which the attribute is checked.
        :returns: the attribute if the attribute is valid, None otherwise.
        """
        if attr in fmt.arguments_keys:
            return attr

        if fmt.revmap(attr):
            return attr

        msg = "Invalid element <%s> inside <%s> tag" % (attr, fmt.__class__.__name__)
        self.warnings.append(msg)
        if self.show_warnings:
            print(msg)

        return None

    def to_odml(self, parsed_doc):
        """
        Parses a Python dictionary object containing an odML document to an odml.Document.
        Will raise a ParserException if the Python dictionary does not contain a valid
        odML document. Also raises an InvalidVersionException if the odML document
        is of a previous odML format version.

        :param parsed_doc: Python dictionary object containing an odML document.
        :returns: parsed odml.Document.
        """
        self.parsed_doc = parsed_doc

        # Parse only odML documents of supported format versions.
        if 'Document' not in self.parsed_doc:
            msg = "Missing root element 'Document'"
            raise ParserException(msg)

        if 'odml-version' not in self.parsed_doc:
            raise ParserException("Invalid odML document: Could not find odml-version.")

        if self.parsed_doc.get('odml-version') != FORMAT_VERSION:
            msg = ("Cannot parse odML document with format version '%s'. \n"
                   "\tUse the 'VersionConverter' from 'odml.tools.converters' "
                   "to import previous odML formats."
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
        """
        Parses a list of Python dictionary objects containing odML sections to the
        odml.Section equivalents including any subsections and properties.

        :param section_list: list of Python dictionary objects containing odML sections.
        :returns: list of parsed odml.Sections
        """
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
        """
        Parses a list of Python dictionary objects containing odML properties to the
        odml.Property equivalents.

        :param props_list: list of Python dictionary objects containing odML properties.
        :returns: list of parsed odml.Properties
        """
        odml_props = []

        for _property in props_list:
            prop_attrs = {}

            for i in _property:
                attr = self.is_valid_attribute(i, odmlfmt.Property)
                if attr:
                    content = _property[attr]
                    if attr.endswith("_cardinality"):
                        content = parse_cardinality(content)

                    # Make sure to always use the correct odml format attribute name
                    prop_attrs[odmlfmt.Property.map(attr)] = content

            prop = odmlfmt.Property.create(**prop_attrs)
            odml_props.append(prop)

        return odml_props
