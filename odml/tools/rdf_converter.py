import os
import uuid

from io import StringIO
from rdflib import Graph, Literal, URIRef
from rdflib.graph import Seq
from rdflib.namespace import XSD, RDF

import yaml
import odml

from ..doc import BaseDocument
from ..format import Format, Document, Section, Property
from ..info import FORMAT_VERSION
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

    subclass_file = os.path.join(odml.__path__[0], 'resources', 'section_subclasses.yaml')

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
        self.docs = odml_documents if not isinstance(odml_documents, BaseDocument) else [odml_documents]
        self.hub_root = None
        self.graph = Graph()
        self.graph.bind("odml", ODML_NS)

        self.section_subclasses = load_rdf_subclasses()

    def convert_to_rdf(self):
        self.hub_root = URIRef(ODML_NS.Hub)
        if self.docs:
            for doc in self.docs:
                self.save_element(doc)
        return self.graph

    def save_element(self, odml_elem, node=None):
        """
        Save the current element to the RDF graph
        :param odml_elem: current element
        :param node: A node to pass the earlier created node to inner elements
        :return: the RDF graph
        """
        fmt = odml_elem.format()

        if not node:
            curr_node = URIRef(ODML_NS + unicode(odml_elem.id))
        else:
            curr_node = node

        if fmt.name == "section":
            sub_sec = self._get_section_subclass(odml_elem)
            sec_type = sub_sec if sub_sec else fmt.rdf_type
            self.graph.add((curr_node, RDF.type, URIRef(sec_type)))
        else:
            self.graph.add((curr_node, RDF.type, URIRef(fmt.rdf_type)))

        # adding doc to the hub
        if isinstance(fmt, Document.__class__):
            self.graph.add((self.hub_root, ODML_NS.hasDocument, curr_node))

            # If available add the documents filename to the document node
            # so we can identify where the data came from.
            if hasattr(odml_elem, "_origin_file_name"):
                self.graph.add((curr_node, ODML_NS.hasFileName, Literal(odml_elem._origin_file_name)))

        for k in fmt.rdf_map_keys:
            if k == 'id':
                continue
            elif (isinstance(fmt, Document.__class__) or
                    isinstance(fmt, Section.__class__)) and k == "repository":
                terminology_url = getattr(odml_elem, k)
                if terminology_url is None or not terminology_url:
                    continue
                terminology_node = self._get_terminology_by_value(terminology_url)
                if terminology_node:
                    self.graph.add((curr_node, fmt.rdf_map(k), terminology_node))
                else:
                    # adding terminology to the hub and to link with the doc
                    node = URIRef(ODML_NS + unicode(uuid.uuid4()))
                    self.graph.add((node, RDF.type, URIRef(terminology_url)))
                    self.graph.add((self.hub_root, ODML_NS.hasTerminology, node))
                    self.graph.add((curr_node, fmt.rdf_map(k), node))
            # generating nodes for entities: sections, properties and bags of values
            elif (isinstance(fmt, Document.__class__) or
                    isinstance(fmt, Section.__class__)) and \
                    k == 'sections' and getattr(odml_elem, k):
                sections = getattr(odml_elem, k)
                for curr_sec in sections:
                    node = URIRef(ODML_NS + unicode(curr_sec.id))
                    self.graph.add((curr_node, fmt.rdf_map(k), node))
                    self.save_element(curr_sec, node)
            elif isinstance(fmt, Section.__class__) and \
                    k == 'properties' and getattr(odml_elem, k):
                properties = getattr(odml_elem, k)
                for curr_prop in properties:
                    node = URIRef(ODML_NS + unicode(curr_prop.id))
                    self.graph.add((curr_node, fmt.rdf_map(k), node))
                    self.save_element(curr_prop, node)
            elif isinstance(fmt, Property.__class__) and \
                    k == 'value' and getattr(odml_elem, fmt.map(k)):
                # "value" needs to be mapped to its appropriate
                # Property library attribute.
                values = getattr(odml_elem, fmt.map(k))
                seq = URIRef(ODML_NS + unicode(uuid.uuid4()))
                self.graph.add((seq, RDF.type, RDF.Seq))
                self.graph.add((curr_node, fmt.rdf_map(k), seq))

                # rdflib so far does not respect RDF:li item order
                # in RDF:Seq on loading so we have to use custom
                # numbered Node elements for now. Once rdflib upgrades
                # this should be reversed to RDF:li again!
                # see https://github.com/RDFLib/rdflib/issues/280
                # -- keep until supported
                # bag = URIRef(ODML_NS + unicode(uuid.uuid4()))
                # self.graph.add((bag, RDF.type, RDF.Bag))
                # self.graph.add((curr_node, fmt.rdf_map(k), bag))
                # for curr_val in values:
                #     self.graph.add((bag, RDF.li, Literal(curr_val)))
                counter = 1
                for curr_val in values:
                    pred = "%s_%s" % (unicode(RDF), counter)
                    self.graph.add((seq, URIRef(pred), Literal(curr_val)))
                    counter = counter + 1

            # adding entities' properties
            else:
                val = getattr(odml_elem, k)
                if val is None or not val:
                    continue
                elif k == 'date':
                    self.graph.add((curr_node, fmt.rdf_map(k), Literal(val, datatype=XSD.date)))
                else:
                    self.graph.add((curr_node, fmt.rdf_map(k), Literal(val)))
        return self.graph

    def _get_terminology_by_value(self, url):
        return self.graph.value(predicate=RDF.type, object=URIRef(url))

    def _get_section_subclass(self, elem):
        """
        :return: RDF identifier of section subclass type if present in section_subclasses dict
        """
        sec_type = getattr(elem, "type")
        if sec_type and sec_type in self.section_subclasses:
            return ODML_NS[self.section_subclasses[sec_type]]
        else:
            return None

    def __str__(self):
        return self.convert_to_rdf().serialize(format='turtle').decode("utf-8")

    def __unicode__(self):
        return self.convert_to_rdf().serialize(format='turtle').decode("utf-8")

    def get_rdf_str(self, rdf_format="turtle"):
        """
        Get converted into one of the supported formats data
        :param rdf_format: possible formats: 'xml', 'n3', 'turtle',
                                             'nt', 'pretty-xml', 'trix',
                                             'trig', 'nquads', 'json-ld'.
               Full lists see in utils.RDFConversionFormats
        :return: string object
        """
        if rdf_format not in RDFConversionFormats:
            raise ValueError("odml.RDFWriter.get_rdf_str: Format for output files is incorrect. "
                             "Please choose from the list: {}".format(list(RDFConversionFormats)))
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
        rdf_doc = Document
        doc_attrs = {}
        for attr in rdf_doc.rdf_map_items:
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
        rdf_sec = Section
        sec_attrs = {}
        for attr in rdf_sec.rdf_map_items:
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
        rdf_prop = Property
        prop_attrs = {}
        for attr in rdf_prop.rdf_map_items:
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
                    valseq = Seq(graph=self.graph, subject=elems[0])
                    for seqitem in valseq:
                        prop_attrs[attr[0]].append(seqitem.toPython())

            elif attr[0] == "id":
                prop_attrs[attr[0]] = prop_uri.split("#", 1)[1]
            elif elems:
                prop_attrs[attr[0]] = unicode(elems[0].toPython())

        self._check_mandatory_attrs(prop_attrs)
        return prop_attrs

    def _check_mandatory_attrs(self, attrs):
        if "name" not in attrs:
            if "id" in attrs:
                raise ParserException("Entity with id: %s does not have required \"name\" attribute" % attrs["id"])
            else:
                raise ParserException("Some entities does not have required \"name\" attribute")
