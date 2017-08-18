import os
import uuid
from io import StringIO

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import XSD, RDF

import odml
import odml.format
from odml.tools.odmlparser import ODMLReader
from odml.tools.xmlparser import ParserException
from odml.tools.xmlparser import XML_VERSION

try:
    unicode = unicode
except NameError:
    unicode = str

odmlns = odml.format.Format.namespace()


class RDFWriter(object):
    """
    A writer to parse odML files into RDF documents.

    Usage:
        file = RDFReader().fromFile("/path_to_input_rdf", "rdf_format")
        file = RDFReader().fromString("rdf file as string", "rdf_format")
        RDFReader().write_file("/input_path", "rdf_format", "/output_path")
        RDFReader().write_files("/input_path", "rdf_format", "/output_directory_path")
    """

    def __init__(self, odml_documents):
        """
        :param odml_documents: list of odml documents 
        """
        self.docs = odml_documents if not isinstance(odml_documents, odml.doc.BaseDocument) else [odml_documents]
        self.hub_root = None
        self.g = Graph()
        self.g.bind("odml", odmlns)

    def convert_to_rdf(self):
        self.hub_root = URIRef(odmlns.Hub)
        if self.docs:
            for doc in self.docs:
                self.save_element(doc)
        return self.g

    def save_element(self, e, node=None):
        """
        Save the current element to the RDF graph
        :param e: current element 
        :param node: A node to pass the earlier created node to inner elements
        :return: the RDF graph 
        """
        fmt = e._format

        if not node:
            curr_node = URIRef(odmlns + str(e.id))
        else:
            curr_node = node

        self.g.add((curr_node, RDF.type, URIRef(fmt.rdf_type())))

        # adding doc to the hub
        if isinstance(fmt, odml.format.Document.__class__):
            self.g.add((self.hub_root, odmlns.hasDocument, curr_node))

        for k in fmt._rdf_map:
            if k == 'id':
                continue
            elif (isinstance(fmt, odml.format.Document.__class__) or
                      isinstance(fmt, odml.format.Section.__class__)) and k == "repository":
                terminology_url = getattr(e, k)
                if terminology_url is None or not terminology_url:
                    continue
                terminology_node = self._get_terminology_by_value(terminology_url)
                if terminology_node:
                    self.g.add((curr_node, fmt.rdf_map(k), terminology_node))
                else:
                    # adding terminology to the hub and to link with the doc
                    node = URIRef(odmlns + str(uuid.uuid4()))
                    self.g.add((node, RDF.type, URIRef(terminology_url)))
                    self.g.add((self.hub_root, odmlns.hasTerminology, node))
                    self.g.add((curr_node, fmt.rdf_map(k), node))
            # generating nodes for entities: sections, properties and bags of values
            elif (isinstance(fmt, odml.format.Document.__class__) or
                      isinstance(fmt, odml.format.Section.__class__)) and \
                            k == 'sections' and len(getattr(e, k)) > 0:
                sections = getattr(e, k)
                for s in sections:
                    node = URIRef(odmlns + str(s.id))
                    self.g.add((curr_node, fmt.rdf_map(k), node))
                    self.save_element(s, node)
            elif isinstance(fmt, odml.format.Section.__class__) and \
                            k == 'properties' and len(getattr(e, k)) > 0:
                properties = getattr(e, k)
                for p in properties:
                    node = URIRef(odmlns + str(p.id))
                    self.g.add((curr_node, fmt.rdf_map(k), node))
                    self.save_element(p, node)
            elif isinstance(fmt, odml.format.Property.__class__) and \
                            k == 'value' and len(getattr(e, k)) > 0:
                values = getattr(e, k)
                bag = URIRef(odmlns + str(uuid.uuid4()))
                self.g.add((bag, RDF.type, RDF.Bag))
                self.g.add((curr_node, fmt.rdf_map(k), bag))
                for v in values:
                    self.g.add((bag, RDF.li, Literal(v)))
            # adding entities' properties
            else:
                val = getattr(e, k)
                if val is None or not val:
                    continue
                elif k == 'date':
                    self.g.add((curr_node, fmt.rdf_map(k), Literal(val, datatype=XSD.date)))
                else:
                    self.g.add((curr_node, fmt.rdf_map(k), Literal(val)))
        return self.g

    def _get_terminology_by_value(self, url):
        return self.g.value(predicate=RDF.type, object=URIRef(url))

    def __str__(self):
        return self.convert_to_rdf().serialize(format='turtle').decode("utf-8")

    def __unicode__(self):
        return self.convert_to_rdf().serialize(format='turtle').decode("utf-8")

    def get_rdf_str(self, rdf_format):
        """
        Get converted into one of the supported formats data 
        :param rdf_format: possible formats: 'xml', 'n3', 'turtle', 
                                             'nt', 'pretty-xml', 'trix', 
                                             'trig', 'nquads', 'json-ld'.
               Full lists see in odml.tools.format_converter.FormatConverter._conversion_formats
        :return: string object
        """
        return self.convert_to_rdf().serialize(format=rdf_format).decode("utf-8")

    def write_file(self, filename, rdf_format):
        data = self.get_rdf_str(rdf_format)
        f = open(filename, "w")
        f.write(data)
        f.close()


class RDFReader(object):
    """
    A reader to parse odML RDF files or strings into odml documents.

    Usage:
        file = RDFReader().fromFile("/path_to_input_rdf", "rdf_format")
        file = RDFReader().fromString("rdf file as string", "rdf_format")
        RDFReader().write_file("/input_path", "rdf_format", "/output_path")
        RDFReader().write_files("/input_path", "rdf_format", "/output_directory_path")
    """

    def __init__(self, filename=None, doc_format=None):
        self.docs = []  # list of parsed odml docs
        if filename and doc_format:
            self.g = Graph().parse(source=filename, format=doc_format)

    def to_odml(self):
        docs_uris = list(self.g.objects(subject=URIRef(odmlns.Hub), predicate=odmlns.hasDocument))
        o = ODMLReader()
        for doc in docs_uris:
            o.parsed_doc = self.parse_document(doc)
            self.docs.append(o.to_odml())
        return self.docs

    def fromFile(self, filename, doc_format):
        self.g = Graph().parse(source=filename, format=doc_format)
        return self.to_odml()

    def fromString(self, file, doc_format):
        self.g = Graph().parse(source=StringIO(file), format=doc_format)
        return self.to_odml()

    # TODO check mandatory attrs
    def parse_document(self, doc_uri):
        rdf_doc = odml.format.Document
        doc_attrs = {}
        for attr in rdf_doc._rdf_map.items():
            elems = list(self.g.objects(subject=doc_uri, predicate=attr[1]))
            if attr[0] == "sections":
                doc_attrs[attr[0]] = []
                for s in elems:
                    doc_attrs[attr[0]].append(self.parse_section(s))
            elif attr[0] == "id":
                doc_attrs[attr[0]] = doc_uri.split("#", 1)[1]
            else:
                if len(elems) > 0:
                    doc_attrs[attr[0]] = str(elems[0].toPython())

        return {'Document': doc_attrs, 'odml-version': XML_VERSION}

    # TODO section subclass conversion
    def parse_section(self, sec_uri):
        rdf_sec = odml.format.Section
        sec_attrs = {}
        for attr in rdf_sec._rdf_map.items():
            elems = list(self.g.objects(subject=sec_uri, predicate=attr[1]))
            if attr[0] == "sections":
                sec_attrs[attr[0]] = []
                for s in elems:
                    sec_attrs[attr[0]].append(self.parse_section(s))
            elif attr[0] == "properties":
                sec_attrs[attr[0]] = []
                for p in elems:
                    sec_attrs[attr[0]].append(self.parse_property(p))
            elif attr[0] == "id":
                sec_attrs[attr[0]] = sec_uri.split("#", 1)[1]
            else:
                if len(elems) > 0:
                    sec_attrs[attr[0]] = str(elems[0].toPython())
        self._check_mandatory_attrs(sec_attrs)
        return sec_attrs

    def parse_property(self, prop_uri):
        rdf_prop = odml.format.Property
        prop_attrs = {}
        for attr in rdf_prop._rdf_map.items():
            elems = list(self.g.objects(subject=prop_uri, predicate=attr[1]))
            if attr[0] == "value" and len(elems) > 0:
                prop_attrs[attr[0]] = []
                values = list(self.g.objects(subject=elems[0], predicate=RDF.li))
                for v in values:
                    prop_attrs[attr[0]].append(v.toPython())
            elif attr[0] == "id":
                prop_attrs[attr[0]] = prop_uri.split("#", 1)[1]
            else:
                if len(elems) > 0:
                    prop_attrs[attr[0]] = str(elems[0].toPython())
        self._check_mandatory_attrs(prop_attrs)
        return prop_attrs

    def _check_mandatory_attrs(self, attrs):
        if "name" not in attrs:
            if "id" in attrs:
                raise ParserException("Entity with id: %s does not have required \"name\" attribute" % attrs["id"])
            else:
                raise ParserException("Some entities does not have required \"name\" attribute")

    def write_file(self, filename, doc_format, output_file):
        """
        Writes result to specified output_file if rdf doc contains exactly one odml document
        :param filename: path to input file
        :param doc_format: rdf format of the file
        :param output_file: path to output file
        """
        self.g = Graph().parse(source=filename, format=doc_format)
        self.to_odml()
        if len(self.docs) > 1:
            raise Exception("Cannot write multiple docs to one file, please choose RDFReader.write_files() instead")
        else:
            odml.save(self.docs, output_file)

    def write_files(self, filename, doc_format, dir_path):
        """
        Creates file in specified directory and writes parsed docs to them
        Example of created file: /<dir_path>/doc_<id>.odml (<id> - id of the document)
        :param filename: path to input file
        :param doc_format: rdf format of the file
        :param dir_path: path to output directory
        """
        self.g = Graph().parse(source=filename, format=doc_format)
        self.to_odml()
        if os.path.exists(dir_path):
            for doc in self.docs:
                if doc:
                    path = os.path.join(dir_path, "doc_" + doc.id)
                    odml.save(doc, path)
