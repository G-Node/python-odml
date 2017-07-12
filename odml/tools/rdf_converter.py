import sys
from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import XSD, RDF
import odml.format as format
import odml

try:
    unicode = unicode
except NameError:
    unicode = str


class RDFWriter:
    """ 
    Creates the RDF graph storing information about the odML document 
    """
    def __init__(self, odml_document, hub_id):
        self.doc = odml_document
        self.hub_id = hub_id
        self.hub_root = None
        self.g = Graph()

    def save_element(self, e, node=None):
        """
        Save the current element to the RDF graph
        :param e: current element 
        :param node: Blank node to pass the earlier created node to inner elements
        :return: the RDF graph 
        """
        fmt = e._format

        if not node:
            curr_node = BNode(e.id)
        else:
            curr_node = node

        self.g.add((curr_node, fmt.rdf_type(), URIRef(fmt.rdf_type())))

        # adding doc to the hub
        if isinstance(fmt, format.Document.__class__):
            self.hub_root = BNode(self.hub_id)
            self.g.add((self.hub_root, fmt.namespace().Hub, URIRef(fmt.namespace().Hub)))
            self.g.add((self.hub_root, fmt.namespace().hasDocument, curr_node))

        for k in fmt._rdf_map:
            if k == 'id':
                continue
            elif isinstance(fmt, format.Document.__class__) and k == "repository":
                terminology_url = getattr(e, k)
                if terminology_url is None or not terminology_url:
                    continue
                # adding terminology to the hub
                terminology_node = self._get_terminology_by_value(terminology_url, self.hub_root)
                if terminology_node:
                    self.g.add((curr_node, fmt.rdf_map(k), terminology_node))
                else:
                    node = BNode()
                    self.g.add((node, fmt.namespace().Terminology, URIRef(terminology_url)))
                    self.g.add((self.hub_root, fmt.namespace().hasTerminology, node))
                    self.g.add((curr_node, fmt.rdf_map(k), node))

            # generating nodes for entities: sections, properties and bags of values
            elif (isinstance(fmt, format.Document.__class__) or
                    isinstance(fmt, format.Section.__class__)) and \
                    k == 'sections' and len(getattr(e, k)) > 0:
                sections = getattr(e, k)
                for s in sections:
                    node = BNode(s.id)
                    self.g.add((curr_node, fmt.rdf_map(k), node))
                    self.save_element(s, node)
            elif isinstance(fmt, format.Section.__class__) and \
                    k == 'properties' and len(getattr(e, k)) > 0:
                properties = getattr(e, k)
                for p in properties:
                    node = BNode(p.id)
                    self.g.add((curr_node, fmt.rdf_map(k), node))
                    self.save_element(p, node)
            elif isinstance(fmt, format.Property.__class__) and \
                    k == 'value' and len(getattr(e, k)) > 0:
                values = getattr(e, k)
                bag = BNode()
                self.g.add((curr_node, fmt.rdf_map(k), bag))
                for v in values:
                    self.g.add((bag, RDF.li, Literal(v)))
            # adding attributes to the entities
            else:
                val = getattr(e, k)
                if val is None or not val:
                    continue
                elif k == 'date':
                    self.g.add((curr_node, fmt.rdf_map(k), Literal(val, datatype=XSD.date)))
                self.g.add((curr_node, fmt.rdf_map(k), Literal(val)))
        return self.g

    # TODO implement search when pass several docs to the converter
    def _get_terminology_by_value(self, url, hub_root):
        return None

    def __str__(self):
        return self.save_element(self.doc).serialize(format='turtle').decode("utf-8")

    def __unicode__(self):
        return self.save_element(self.doc).serialize(format='turtle').decode("utf-8")

    def write_file(self, filename):
        if sys.version_info < (3,):
            data = unicode(self).encode('utf-8')
        else:
            data = str(self)

        f = open(filename, "w")
        f.write(data)
        f.close()

if __name__ == "__main__":
    l = "./python-odml/doc/example_odMLs/ex_1.odml"
    o = odml.load(l)
    r = RDFWriter(o, "hub1")
    r.write_file("./ex_1.rdf")
