import os
import uuid

from io import StringIO
from rdflib import Graph, Literal, URIRef
from rdflib.graph import Seq
from rdflib.namespace import XSD, RDF

import yaml

from ..doc import BaseDocument
from ..format import Format, Document, Section, Property
from ..info import FORMAT_VERSION, INSTALL_PATH
from .dict_parser import DictReader
from .parser_utils import ParserException
from .utils import RDFConversionFormats

try:
    unicode = unicode
except NameError:
    unicode = str

ODML_NS = Format.namespace()


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
            section_subclasses = yaml.load(yaml_file)
        except yaml.parser.ParserError as err:
            print("[Error] Loading RDF subclass file: %s" % err)

    return section_subclasses


class RDFWriter(object):
    """
    A writer to parse odML files into RDF documents.

    Usage:
        RDFWriter(odml_docs).get_rdf_str('turtle')
        RDFWriter(odml_docs).write_file("/output_path", "rdf_format")
    """

    def __init__(self, odml_documents):
        """
        :param odml_documents: list of odml documents
        """
        if not isinstance(odml_documents, list):
            odml_documents = [odml_documents]

        self.docs = odml_documents
        self.hub_root = None
        self.graph = Graph()
        self.graph.bind("odml", ODML_NS)

        self.section_subclasses = load_rdf_subclasses()

    def convert_to_rdf(self):
        self.hub_root = URIRef(ODML_NS.Hub)
        if self.docs:
            for doc in self.docs:
                if isinstance(doc, BaseDocument):
                    self.save_element(doc)

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
        seq = URIRef(ODML_NS + unicode(uuid.uuid4()))
        self.graph.add((seq, RDF.type, RDF.Seq))
        self.graph.add((parent_node, rdf_predicate, seq))

        # rdflib so far does not respect RDF:li item order in RDF:Seq on
        # loading so we have to use custom numbered Node elements for now.
        # Once rdflib upgrades this should be reversed to RDF:li again!
        # see https://github.com/RDFLib/rdflib/issues/280
        # -- keep until supported
        # bag = URIRef(ODML_NS + unicode(uuid.uuid4()))
        # self.graph.add((bag, RDF.type, RDF.Bag))
        # self.graph.add((curr_node, fmt.rdf_map(k), bag))
        # for curr_val in values:
        #     self.graph.add((bag, RDF.li, Literal(curr_val)))
        counter = 1
        for curr_val in values:
            custom_predicate = "%s_%s" % (unicode(RDF), counter)
            self.graph.add((seq, URIRef(custom_predicate), Literal(curr_val)))
            counter = counter + 1

    def save_odml_list(self, odml_list, parent_node, rdf_predicate):
        """
        save_odml_list adds all odml elements in a list to the current
        parent node and handles all child items via save_element.

        :param odml_list: list of odml entities.
        :param parent_node: current parent node in the RDF graph.
        :param rdf_predicate: RDF predicate used to add all odml entities
                              to the parent node.
        """
        for curr_item in odml_list:
            node = URIRef(ODML_NS + unicode(curr_item.id))
            self.graph.add((parent_node, rdf_predicate, node))
            self.save_element(curr_item, node)

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
            terminology_node = URIRef(ODML_NS + unicode(uuid.uuid4()))
            self.graph.add((terminology_node, RDF.type, URIRef(leaf_value)))
            self.graph.add((self.hub_root, ODML_NS.hasTerminology, terminology_node))

        self.graph.add((parent_node, rdf_predicate, terminology_node))

    def save_element(self, odml_elem, node=None):
        """
        Save the current odml element to the RDF graph and handle all child
        elements of the current odml element recursively.

        :param odml_elem: An odml element that should be added to the RDF graph.
        :param node: An RDF node that is used to append the current odml element
                     to the RDF graph. If None, a new node will be created and
                     added to the 'Hub' node of the RDF graph.
        """
        fmt = odml_elem.format()

        is_doc = fmt.name == Document.name
        is_sec = fmt.name == Section.name
        is_prop = fmt.name == Property.name

        curr_node = node
        if not curr_node:
            curr_node = URIRef(ODML_NS + unicode(odml_elem.id))

        # Add type of current node to the RDF graph
        curr_type = fmt.rdf_type
        # Handle section subclass types
        if is_sec:
            sub_sec = self._get_section_subclass(odml_elem)
            if sub_sec:
                curr_type = sub_sec
        self.graph.add((curr_node, RDF.type, URIRef(curr_type)))

        # Add a new document to the RDF Hub node
        if is_doc:
            self.graph.add((self.hub_root, ODML_NS.hasDocument, curr_node))

            # If available, add the documents' filename to the document node
            # so we can identify where the data came from.
            if hasattr(odml_elem, "_origin_file_name"):
                curr_lit = Literal(odml_elem._origin_file_name)
                self.graph.add((curr_node, ODML_NS.hasFileName, curr_lit))

        for k in fmt.rdf_map_keys:
            # Ignore "id" and empty values, but make sure the content of "value"
            # is only accessed via its non deprecated property "values".
            if k == "id" or k == "value" and not getattr(odml_elem, fmt.map(k)):
                continue
            elif k != "value" and not getattr(odml_elem, k):
                continue

            if (is_doc or is_sec) and k == "repository":
                self.save_repository_node(curr_node, fmt.rdf_map(k),
                                          getattr(odml_elem, k))

            # generating nodes for sections and properties
            elif ((is_doc or is_sec) and k == "sections") or \
                    (is_sec and k == "properties"):
                self.save_odml_list(getattr(odml_elem, k), curr_node, fmt.rdf_map(k))

            # generating nodes for Property values
            elif is_prop and k == "value":
                # 'value' needs to be mapped to its appropriate odml Property attribute.
                self.save_odml_values(curr_node, fmt.rdf_map(k),
                                      getattr(odml_elem, fmt.map(k)))

            elif k == "date":
                curr_lit = Literal(getattr(odml_elem, k), datatype=XSD.date)
                self.graph.add((curr_node, fmt.rdf_map(k), curr_lit))

            else:
                curr_lit = Literal(getattr(odml_elem, k))
                self.graph.add((curr_node, fmt.rdf_map(k), curr_lit))

    def _get_section_subclass(self, elem):
        """
        :return: RDF identifier of section subclass type if present
                 in section_subclasses dict.
        """
        sec_type = getattr(elem, "type")
        if sec_type and sec_type in self.section_subclasses:
            return ODML_NS[self.section_subclasses[sec_type]]

        return None

    def __str__(self):
        return self.convert_to_rdf().serialize(format='turtle').decode("utf-8")

    def __unicode__(self):
        return self.convert_to_rdf().serialize(format='turtle').decode("utf-8")

    def get_rdf_str(self, rdf_format="turtle"):
        """
        Get converted into one of the supported formats data

        :param rdf_format: possible formats: 'xml', 'n3', 'turtle', 'nt', 'pretty-xml',
                                             'trix', 'trig', 'nquads', 'json-ld'.
               Full lists see in utils.RDFConversionFormats
        :return: string object
        """
        if rdf_format not in RDFConversionFormats:
            msg = "odml.RDFWriter.get_rdf_str: Format for output files is incorrect."
            msg = "%s Please choose from the list: %s" % (msg, list(RDFConversionFormats))
            raise ValueError(msg)

        return self.convert_to_rdf().serialize(format=rdf_format).decode("utf-8")

    def write_file(self, filename, rdf_format="turtle"):
        data = self.get_rdf_str(rdf_format)
        filename_ext = filename
        if filename.find(RDFConversionFormats.get(rdf_format)) < 0:
            filename_ext += RDFConversionFormats.get(rdf_format)

        with open(filename_ext, "w") as out_file:
            out_file.write(data)


class RDFReader(object):
    """
    A reader to parse odML RDF files or strings into odml documents.

    Usage:
        file = RDFReader().from_file("/path_to_input_rdf", "rdf_format")
        file = RDFReader().from_string("rdf file as string", "rdf_format")
        RDFReader().write_file("/input_path", "rdf_format", "/output_path")
    """

    def __init__(self, filename=None, doc_format=None):
        self.docs = []  # list of parsed odml docs
        if filename and doc_format:
            self.graph = Graph().parse(source=filename, format=doc_format)

    def to_odml(self):
        """
        :return: list of converter odml documents
        """
        docs_uris = list(self.graph.objects(subject=URIRef(ODML_NS.Hub),
                                            predicate=ODML_NS.hasDocument))
        for doc in docs_uris:
            par = self.parse_document(doc)
            par_doc = DictReader().to_odml(par)
            self.docs.append(par_doc)

        return self.docs

    def from_file(self, filename, doc_format):
        self.graph = Graph().parse(source=filename, format=doc_format)
        docs = self.to_odml()
        for curr_doc in docs:
            # Provide original file name via the document
            curr_doc._origin_file_name = os.path.basename(filename)
        return docs

    def from_string(self, file, doc_format):
        self.graph = Graph().parse(source=StringIO(file), format=doc_format)
        return self.to_odml()

    # TODO check mandatory attrs
    def parse_document(self, doc_uri):
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
                doc_attrs[attr[0]] = unicode(elems[0].toPython())

        return {'Document': doc_attrs, 'odml-version': FORMAT_VERSION}

    # TODO section subclass conversion
    def parse_section(self, sec_uri):
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
                sec_attrs[attr[0]] = unicode(elems[0].toPython())

        self._check_mandatory_attrs(sec_attrs)
        return sec_attrs

    def parse_property(self, prop_uri):
        prop_attrs = {}
        for attr in Property.rdf_map_items:
            elems = list(self.graph.objects(subject=prop_uri, predicate=attr[1]))
            if attr[0] == "value" and elems:
                prop_attrs[attr[0]] = []

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
                prop_attrs[attr[0]] = unicode(elems[0].toPython())

        self._check_mandatory_attrs(prop_attrs)
        return prop_attrs

    @staticmethod
    def _check_mandatory_attrs(attrs):
        if "name" not in attrs:
            msg = "Entity missing required 'name' attribute"
            if "id" in attrs:
                msg = "%s id:'%s'" % (msg, attrs["id"])

            raise ParserException(msg)
