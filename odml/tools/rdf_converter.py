import sys
import uuid

from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import XSD, RDF

import odml
import odml.format as format

try:
    unicode = unicode
except NameError:
    unicode = str

odmlns = format.Format.namespace()


class RDFWriter:
    """ 
    Creates the RDF graph storing information about the odML document 
    """

    def __init__(self, odml_documents, hub_id=None):
        self.docs = odml_documents
        self.hub_id = hub_id
        self.hub_root = None
        self.g = Graph()
        self.g.bind("odml", odmlns)

    def create_hub_root(self):
        if self.hub_root is None:
            if self.hub_id is None:
                self.hub_root = URIRef(odmlns + str(uuid.uuid4()))
            else:
                self.hub_root = URIRef(odmlns + self.hub_id)

    def convert_to_rdf(self, docs):
        self.create_hub_root()
        if docs:
            self.g.add((self.hub_root, odmlns.Hub, URIRef(odmlns.Hub)))
            for doc in docs:
                self.save_element(doc)
        return self.g

    def save_element(self, e, node=None):
        """
        Save the current element to the RDF graph
        :param e: current element 
        :param node: Blank node to pass the earlier created node to inner elements
        :return: the RDF graph 
        """
        fmt = e._format

        if not node:
            curr_node = URIRef(odmlns + str(e.id))
        else:
            curr_node = node

        self.g.add((curr_node, fmt.rdf_type(), URIRef(fmt.rdf_type())))

        # adding doc to the hub
        if isinstance(fmt, format.Document.__class__):
            self.g.add((self.hub_root, odmlns.hasDocument, curr_node))

        for k in fmt._rdf_map:
            if k == 'id':
                continue
            elif (isinstance(fmt, format.Document.__class__) or
                      isinstance(fmt, format.Section.__class__)) and k == "repository":
                terminology_url = getattr(e, k)
                if terminology_url is None or not terminology_url:
                    continue
                terminology_node = self._get_terminology_by_value(terminology_url)
                if terminology_node:
                    self.g.add((curr_node, fmt.rdf_map(k), terminology_node))
                else:
                    # adding terminology to the hub and to link with the doc
                    node = URIRef(odmlns + str(uuid.uuid4()))
                    self.g.add((node, odmlns.Terminology, URIRef(terminology_url)))
                    self.g.add((self.hub_root, odmlns.hasTerminology, node))
                    self.g.add((curr_node, fmt.rdf_map(k), node))
            # generating nodes for entities: sections, properties and bags of values
            elif (isinstance(fmt, format.Document.__class__) or
                      isinstance(fmt, format.Section.__class__)) and \
                            k == 'sections' and len(getattr(e, k)) > 0:
                sections = getattr(e, k)
                for s in sections:
                    node = URIRef(odmlns + str(s.id))
                    self.g.add((curr_node, fmt.rdf_map(k), node))
                    self.save_element(s, node)
            elif isinstance(fmt, format.Section.__class__) and \
                            k == 'properties' and len(getattr(e, k)) > 0:
                properties = getattr(e, k)
                for p in properties:
                    node = URIRef(odmlns + str(p.id))
                    self.g.add((curr_node, fmt.rdf_map(k), node))
                    self.save_element(p, node)
            elif isinstance(fmt, format.Property.__class__) and \
                            k == 'value' and len(getattr(e, k)) > 0:
                values = getattr(e, k)
                bag = BNode(str(uuid.uuid4()))
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
                self.g.add((curr_node, fmt.rdf_map(k), Literal(val)))
        return self.g

    def _get_terminology_by_value(self, url):
        return self.g.value(predicate=odmlns.Terminology, object=URIRef(url))

    def __str__(self):
        return self.convert_to_rdf(self.docs).serialize(format='turtle').decode("utf-8")

    def __unicode__(self):
        return self.convert_to_rdf(self.docs).serialize(format='turtle').decode("utf-8")

    def write_file(self, filename):
        if sys.version_info < (3,):
            data = unicode(self).encode('utf-8')
        else:
            data = str(self)

        f = open(filename, "w")
        f.write(data)
        f.close()


if __name__ == "__main__":
    l1 = "./python-odml/doc/example_odMLs/ex_1.odml"
    l2 = "./python-odml/doc/example_odMLs/ex_2.odml"
    o1 = odml.load(l1)
    o2 = odml.load(l2)
    r = RDFWriter([o1, o2], "hub1")
    r.write_file("./ex_1.rdf")