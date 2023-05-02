"""
The RDF converter module provides conversion of odML documents to RDF and
the conversion of odML flavored RDF to odML documents.
"""

import os
import string
import uuid
import warnings

from io import StringIO

from rdflib import __version__ as rdflib_version
from rdflib import Graph, Literal, URIRef
from rdflib.graph import Seq
try:
    from rdflib.container import Seq as CollSeq
except ImportError as exc:
    # annoy people to upgrade their rdflib version but still support the usage
    print("deprecated rdflib version. Please upgrade to the latest version.")
from rdflib.namespace import XSD, RDF, RDFS

import yaml

import odml

from ..format import Format, Document, Section, Property
from ..info import FORMAT_VERSION, INSTALL_PATH
from .dict_parser import DictReader
from .parser_utils import ParserException, RDF_CONVERSION_FORMATS

ODML_NS = Format.namespace()


def rdflib_version_major():
    version_split = rdflib_version.split(".")
    if len(version_split) < 3 or not version_split[0].isdigit():
        print("Could not parse rdflib version %s" % rdflib_version)
        return 0
    return int(version_split[0])


def load_rdf_subclasses():
    """
    load_rdf_subclasses loads odml section types to RDF Section subclass types
    mappings from a file and returns the mapping as a dictionary.
    Will return an empty dictionary, if the Subclasses file cannot be loaded.

    :return: Dictionary of the form {'Section type': 'RDF class type'}
    """
    section_subclasses = {}

    subclass_file = os.path.join(INSTALL_PATH, "resources", "section_subclasses.yaml")

    if not os.path.isfile(subclass_file):
        print("[Warning] Could not find subclass file '%s'" % subclass_file)
        return section_subclasses

    with open(subclass_file, "r") as yaml_file:
        try:
            section_subclasses = yaml.safe_load(yaml_file)
        except yaml.parser.ParserError as err:
            print("[Error] Loading RDF subclass file: %s" % err)

    return section_subclasses


class RDFWriter(object):
    """
    A writer to parse odML files into RDF documents.

    Use the 'rdf_subclassing' flag to disable default usage of Section type conversion to
    RDF Subclasses.
    Provide a custom Section type to RDF Subclass Name mapping dictionary via the
    'custom_subclasses' attribute to add custom or overwrite default RDF Subclass mappings.

    Usage:
        RDFWriter(odml_docs).get_rdf_str('turtle')
        RDFWriter(odml_docs).write_file("/output_path", "rdf_format")

        RDFWriter(odml_docs, rdf_subclassing=False).write_file("path", "rdf_format")
        RDFWriter(odml_docs, custom_subclasses=custom_dict).write_file("path", "rdf_format")
    """

    def __init__(self, odml_documents, rdf_subclassing=True, custom_subclasses=None):
        """
        :param odml_documents: list of odML documents
        :param rdf_subclassing: Flag whether Section types should be converted to RDF Subclasses
                                for enhanced SPARQL queries. Default is 'True'.
        :param custom_subclasses: A dict where the keys reference a Section type and the
                                  corresponding values reference an RDF Class Name. When exporting
                                  a Section of a type contained in this dict, the resulting RDF
                                  Instance will be of the corresponding Class and this Class will
                                  be added as a Subclass of RDF Class "odml:Section" to the
                                  RDF document.
                                  Key:value pairs of the "custom_subclasses" dict will overwrite
                                  existing key:value pairs of the default subclassing dict.
        """
        if not isinstance(odml_documents, list):
            odml_documents = [odml_documents]

        self.docs = odml_documents
        self.hub_root = None
        self.graph = Graph()
        self.graph.bind("odml", ODML_NS)

        self.rdf_subclassing = rdf_subclassing

        self.section_subclasses = load_rdf_subclasses()
        # If a custom Section type to RDF Subclass dict has been provided,
        # parse it and update the default section_subclasses dict with the content.
        if custom_subclasses and isinstance(custom_subclasses, dict):
            self._parse_custom_subclasses(custom_subclasses)

    def convert_to_rdf(self):
        """
        convert_to_rdf converts all odML documents to RDF,
        connects them via a common "Hub" RDF node and
        returns the created RDF graph.

        :return: An RDF graph.
        """
        self.hub_root = URIRef(ODML_NS.Hub)
        if self.docs:
            for doc in self.docs:
                if isinstance(doc, odml.doc.BaseDocument):
                    doc.finalize()
                    self.save_document(doc)

        return self.graph

    def save_odml_values(self, parent_node, rdf_predicate, values):
        """
        save_odml_values adds an RDF seq node to the parent RDF node
        and creates a value leaf node for every odml value.

        :param parent_node: current parent node in the RDF graph.
        :param rdf_predicate: RDF predicate used to add the Seq node
                              to the current parent node.
        :param values: list of odml values.
        """
        seq = URIRef(ODML_NS + str(uuid.uuid4()))
        self.graph.add((seq, RDF.type, RDF.Seq))
        self.graph.add((parent_node, rdf_predicate, seq))

        # rdflib so far does not respect RDF:li item order in RDF:Seq on
        # loading so we have to use custom numbered Node elements for now.
        # Once rdflib upgrades this should be reversed to RDF:li again!
        # see https://github.com/RDFLib/rdflib/issues/280
        # -- keep until supported
        #bag = URIRef(ODML_NS + str(uuid.uuid4()))
        #self.graph.add((bag, RDF.type, RDF.Bag))
        #self.graph.add((parent_node, rdf_predicate, bag))
        #for curr_val in values:
        #    self.graph.add((bag, RDF.li, Literal(curr_val)))
        if rdflib_version_major() >= 6:
            seq_list = []
            for curr_val in values:
                seq_list.append(Literal(curr_val))
            _ = CollSeq(self.graph, seq, seq_list)
        else:
            # manually create and use the value blank nodes order
            counter = 1
            for curr_val in values:
                custom_predicate = "%s_%s" % (str(RDF), counter)
                self.graph.add((seq, URIRef(custom_predicate), Literal(curr_val)))
                counter = counter + 1

    def save_odml_list(self, parent_node, rdf_predicate, odml_list):
        """
        save_odml_list adds all odml elements in a list to the current
        parent node and handles all child items via save_element.

        :param parent_node: current parent node in the RDF graph.
        :param rdf_predicate: RDF predicate used to add all odml entities
                              to the parent node.
        :param odml_list: list of odml entities.
        """
        for curr_item in odml_list:
            node = URIRef(ODML_NS + str(curr_item.id))
            self.graph.add((parent_node, rdf_predicate, node))

            fmt = curr_item.format()
            if fmt.name == Section.name:
                self.save_section(curr_item, node)
            elif fmt.name == Property.name:
                self.save_property(curr_item, node)

    def save_repository_node(self, parent_node, rdf_predicate, leaf_value):
        """
        save_repository_node adds a node with a given repository url to
        the current graphs terminology node. If the current graph does
        not yet contain a terminology node, it creates one and attaches
        the current node to it.

        :param parent_node: current parent node in the RDF graph.
        :param rdf_predicate: RDF predicate used to add the terminology
                              to the parent node.
        :param leaf_value: Value that will be added to the RDF graph.
        """
        terminology_node = self.graph.value(predicate=RDF.type, object=URIRef(leaf_value))
        if not terminology_node:
            # adding terminology url value to the graph and linking it
            # to the current RDF node.
            terminology_node = URIRef(ODML_NS + str(uuid.uuid4()))
            self.graph.add((terminology_node, RDF.type, URIRef(leaf_value)))
            self.graph.add((self.hub_root, ODML_NS.hasTerminology, terminology_node))

        self.graph.add((parent_node, rdf_predicate, terminology_node))

    def save_document(self, doc, curr_node=None):
        """
        Add the current odML Document to the RDF graph and handle all child
        elements recursively.

        :param doc: An odml Document that should be added to the RDF graph.
        :param curr_node: An RDF node that is used to append the current odml element
                          to the Hub node of the current RDF graph.
        """
        fmt = doc.format()

        if not curr_node:
            curr_node = URIRef(ODML_NS + str(doc.id))

        self.graph.add((curr_node, RDF.type, URIRef(fmt.rdf_type)))
        self.graph.add((self.hub_root, ODML_NS.hasDocument, curr_node))

        # If available, add the documents' filename to the document node
        # so we can identify where the data came from.
        if hasattr(doc, "origin_file_name"):
            curr_lit = Literal(doc.origin_file_name)
            self.graph.add((curr_node, ODML_NS.hasFileName, curr_lit))

        for k in fmt.rdf_map_keys:
            curr_pred = fmt.rdf_map(k)
            curr_val = getattr(doc, k)

            # Ignore an "id" entry, it has already been used to create the node itself.
            if k == "id" or not curr_val:
                continue

            if k == "repository":
                self.save_repository_node(curr_node, curr_pred, curr_val)
            elif k == "sections":
                # generating nodes for child sections
                self.save_odml_list(curr_node, curr_pred, curr_val)
            elif k == "date":
                curr_lit = Literal(curr_val, datatype=XSD.date)
                self.graph.add((curr_node, curr_pred, curr_lit))
            else:
                curr_lit = Literal(curr_val)
                self.graph.add((curr_node, curr_pred, curr_lit))

    def save_section(self, sec, curr_node):
        """
        Add the current odML Section to the RDF graph and handle all child
        elements recursively.

        :param sec: An odml Section that should be added to the RDF graph.
        :param curr_node: An RDF node that is used to append the current odml element
                          to the current RDF graph.
        """
        fmt = sec.format()

        # Add type of current node to the RDF graph
        curr_type = fmt.rdf_type

        # Handle section subclass types
        if self.rdf_subclassing:
            sub_sec = self._get_section_subclass(sec)
            if sub_sec:
                curr_type = sub_sec
                self.graph.add((URIRef(fmt.rdf_type), RDF.type, RDFS.Class))
                self.graph.add((URIRef(curr_type), RDF.type, RDFS.Class))
                self.graph.add((URIRef(curr_type), RDFS.subClassOf, URIRef(fmt.rdf_type)))

        self.graph.add((curr_node, RDF.type, URIRef(curr_type)))

        for k in fmt.rdf_map_keys:
            curr_pred = fmt.rdf_map(k)
            curr_val = getattr(sec, k)

            # Ignore an "id" entry, it has already been used to create the node itself.
            if k == "id" or not curr_val:
                continue

            if k == "repository":
                self.save_repository_node(curr_node, curr_pred, curr_val)

            # generating nodes for sections and properties
            elif k in ["sections", "properties"]:
                self.save_odml_list(curr_node, curr_pred, curr_val)
            else:
                curr_lit = Literal(curr_val)
                self.graph.add((curr_node, curr_pred, curr_lit))

    def save_property(self, prop, curr_node):
        """
        Add the current odML Property to the RDF graph and handle all child
        elements.

        :param prop: An odml Section that should be added to the RDF graph.
        :param curr_node: An RDF node that is used to append the current odml element
                          to the current RDF graph.
        """
        fmt = prop.format()

        self.graph.add((curr_node, RDF.type, URIRef(fmt.rdf_type)))

        for k in fmt.rdf_map_keys:
            curr_pred = fmt.rdf_map(k)
            # Make sure the content of "value" is only accessed via its
            # non deprecated property "values".
            if k == "value":
                curr_val = getattr(prop, fmt.map(k))
            else:
                curr_val = getattr(prop, k)

            # Ignore "id" and empty values, but make sure the content of "value"
            # is only accessed via its non deprecated property "values".
            if k == "id" or not curr_val:
                continue

            if k == "value":
                # generating nodes for Property values
                self.save_odml_values(curr_node, curr_pred, curr_val)
            else:
                curr_lit = Literal(curr_val)
                self.graph.add((curr_node, curr_pred, curr_lit))

    def _get_section_subclass(self, elem):
        """
        _get_section_subclass checks whether the current odML element
        is of a type that can be converted into an RDF subclass of
        class Section.

        :return: RDF identifier of section subclass type if present
                 in the section_subclasses dict.
        """
        sec_type = getattr(elem, "type")
        if sec_type and sec_type in self.section_subclasses:
            return ODML_NS[self.section_subclasses[sec_type]]

        return None

    def _parse_custom_subclasses(self, custom_subclasses):
        """
        Parses a provided dictionary of "Section type": "RDF Subclass name"
        key value pairs and adds the pairs to the parsers' 'section_subclasses'
        default dictionary. Existing key:value pairs will be overwritten
        with provided custom key:value pairs and a Warning will be issued.
        Dictionary values containing whitespaces will raise a ValueError.

        :param custom_subclasses: dictionary of "Section type": "RDF Subclass name" key value pairs.
                                  Values must not contain whitespaces, a ValueError will be raised
                                  otherwise.
        """

        # Do not allow any whitespace characters in values
        vals = "".join(custom_subclasses.values()).encode()
        if vals != vals.translate(None, string.whitespace.encode()):
            msg = "Custom RDF Subclass names must not contain any whitespace characters."
            raise ValueError(msg)

        for k in custom_subclasses:
            val = custom_subclasses[k]
            if k in self.section_subclasses:
                msg = "RDFWriter custom subclasses: Key '%s' already exists. " % k
                msg += "Value '%s' replaces default value '%s'." % (val, self.section_subclasses[k])
                warnings.warn(msg, stacklevel=2)
            self.section_subclasses[k] = val

    def __str__(self):
        if rdflib_version_major() >= 6:
            return self.convert_to_rdf().serialize(format='turtle')
        return self.convert_to_rdf().serialize(format='turtle').decode("utf-8")

    def __unicode__(self):
        if rdflib_version_major() >= 6:
            return self.convert_to_rdf().serialize(format='turtle')
        return self.convert_to_rdf().serialize(format='turtle').decode("utf-8")

    def get_rdf_str(self, rdf_format="turtle"):
        """
        Convert the current odML content of the parser to a common RDF graph
        and return the graph as a string object in the specified RDF format.

        :param rdf_format: RDF output format. Default format is 'turtle'.
                           Available formats: 'xml', 'n3', 'turtle', 'nt',
                           'pretty-xml', 'trix', 'trig', 'nquads', 'json-ld'.

        :return: string object
        """
        if rdf_format not in RDF_CONVERSION_FORMATS:
            msg = "odml.RDFWriter.get_rdf_str: Format for output files is incorrect."
            msg = "%s Please choose from the list: %s" % (msg, list(RDF_CONVERSION_FORMATS))
            raise ValueError(msg)

        if rdflib_version_major() >= 6:
            return self.convert_to_rdf().serialize(format=rdf_format)
        return self.convert_to_rdf().serialize(format=rdf_format).decode("utf-8")

    def write_file(self, filename, rdf_format="turtle"):
        """
        Convert the current odML content of the parser to a common RDF graph
        and write the resulting graph to an output file using the provided
        RDF output format.

        :param filename:
        :param rdf_format: RDF output format. Default format is 'turtle'.
                           Available formats: 'xml', 'n3', 'turtle', 'nt',
                           'pretty-xml', 'trix', 'trig', 'nquads', 'json-ld'.
        """
        data = self.get_rdf_str(rdf_format)
        filename_ext = filename
        if filename.find(RDF_CONVERSION_FORMATS.get(rdf_format)) < 0:
            filename_ext += RDF_CONVERSION_FORMATS.get(rdf_format)

        with open(filename_ext, "w") as out_file:
            out_file.write(data)


class RDFReader(object):
    """
    A reader to parse odML RDF files or strings into odML documents.

    Usage:
        file = RDFReader().from_file("/path_to_input_rdf", "rdf_format")
        file = RDFReader().from_string("rdf file as string", "rdf_format")
        RDFReader().write_file("/input_path", "rdf_format", "/output_path")
    """

    def __init__(self, filename=None, doc_format=None):
        """
        :param filename: Path of the input odML RDF file.
        :param doc_format: RDF format of the input odML RDF file.
        """
        self.docs = []  # list of parsed odml docs
        if filename and doc_format:
            self.graph = Graph().parse(source=filename, format=doc_format)

    def to_odml(self):
        """
        to_odml converts all odML documents from a common RDF graph
        into individual odML documents.

        :return: list of converted odML documents
        """
        docs_uris = list(self.graph.objects(subject=URIRef(ODML_NS.Hub),
                                            predicate=ODML_NS.hasDocument))
        for doc in docs_uris:
            par = self.parse_document(doc)
            par_doc = DictReader().to_odml(par)
            self.docs.append(par_doc)

        return self.docs

    def from_file(self, filename, doc_format):
        """
        from_file loads an odML RDF file and converts all odML documents
        from this RDF graph into individual odML documents.

        :param filename: Path of the input odML RDF file.
        :param doc_format: RDF format of the input odML RDF file.
        :return: list of converted odML documents
        """
        self.graph = Graph().parse(source=filename, format=doc_format)
        docs = self.to_odml()
        for curr_doc in docs:
            # Provide original file name via the document
            curr_doc.origin_file_name = os.path.basename(filename)

        return docs

    def from_string(self, file, doc_format):
        """
        from_string loads an odML RDF file or string object and converts all
        odML documents from this RDF graph into individual odML documents.

        :param file: Path of the input odML RDF file or an RDF graph string object.
        :param doc_format: RDF format of the input odML RDF graph.
        :return: list of converted odML documents
        """
        self.graph = Graph().parse(source=StringIO(file), format=doc_format)
        return self.to_odml()

    def parse_document(self, doc_uri):
        """
        parse_document parses an odML RDF Document node into an odML Document.

        :param doc_uri: RDF URI of an odML Document node within an RDF graph.
        :return: dict containing an odML Document
        """
        doc_attrs = {}
        for attr in Document.rdf_map_items:
            elems = list(self.graph.objects(subject=doc_uri, predicate=attr[1]))
            if attr[0] == "sections":
                doc_attrs[attr[0]] = []
                for sec in elems:
                    doc_attrs[attr[0]].append(self.parse_section(sec))
            elif attr[0] == "id":
                doc_attrs[attr[0]] = doc_uri.split("#", 1)[1]
            elif elems:
                doc_attrs[attr[0]] = str(elems[0].toPython())

        return {'Document': doc_attrs, 'odml-version': FORMAT_VERSION}

    def parse_section(self, sec_uri):
        """
        parse_section parses an odML RDF Section node into an odML Section.

        :param sec_uri: RDF URI of an odML Section node within an RDF graph.
        :return: dict containing an odML Section
        """
        sec_attrs = {}
        for attr in Section.rdf_map_items:
            elems = list(self.graph.objects(subject=sec_uri, predicate=attr[1]))
            if attr[0] == "sections":
                sec_attrs[attr[0]] = []
                for sec in elems:
                    sec_attrs[attr[0]].append(self.parse_section(sec))
            elif attr[0] == "properties":
                sec_attrs[attr[0]] = []
                for prop in elems:
                    sec_attrs[attr[0]].append(self.parse_property(prop))
            elif attr[0] == "id":
                sec_attrs[attr[0]] = sec_uri.split("#", 1)[1]
            elif elems:
                sec_attrs[attr[0]] = str(elems[0].toPython())

        self._check_mandatory_attrs(sec_attrs)
        return sec_attrs

    def parse_property(self, prop_uri):
        """
        parse_property parses an odML RDF Property node into an odML Property.

        :param prop_uri: RDF URI of an odML Property node within an RDF graph.
        :return: dict containing an odML Property
        """
        prop_attrs = {}
        for attr in Property.rdf_map_items:
            elems = list(self.graph.objects(subject=prop_uri, predicate=attr[1]))
            if attr[0] == "value" and elems:
                prop_attrs[attr[0]] = []

                if rdflib_version_major() >= 6:
                    # rdflib version 6.x.x+ should support rdf:_nnn only, RDF.li
                    # are not supported; reverse import the blank node values;
                    # hopefully in the correct order.
                    val_seq = Seq(graph=self.graph, subject=elems[0])
                    for seq_item in val_seq:
                        prop_attrs[attr[0]].append(seq_item.toPython())
                else:
                    # rdflib does not respect order with RDF.li items yet, see comment above
                    # support both RDF.li and rdf:_nnn for now.
                    # Remove rdf:_nnn once rdflib respects RDF.li order in an RDF.Seq obj.
                    values = list(self.graph.objects(subject=elems[0], predicate=RDF.li))
                    if values:
                        for curr_val in values:
                            prop_attrs[attr[0]].append(curr_val.toPython())
                    else:
                        # rdf:__nnn part
                        val_seq = Seq(graph=self.graph, subject=elems[0])
                        for seq_item in val_seq:
                            prop_attrs[attr[0]].append(seq_item.toPython())

            elif attr[0] == "id":
                prop_attrs[attr[0]] = prop_uri.split("#", 1)[1]
            elif elems:
                prop_attrs[attr[0]] = str(elems[0].toPython())

        self._check_mandatory_attrs(prop_attrs)
        return prop_attrs

    @staticmethod
    def _check_mandatory_attrs(odml_entity):
        """
        _check_mandatory_attrs checks whether a passed odML entity contains
        the required "name" attribute and raises a ParserException otherwise.

        :param odml_entity: dict containing an odmL entity
        """
        if "name" not in odml_entity:
            msg = "Entity missing required 'name' attribute"
            if "id" in odml_entity:
                msg = "%s id:'%s'" % (msg, odml_entity["id"])

            raise ParserException(msg)
