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
    def __init__(self, odml_document):
        self.doc = odml_document
        self.g = Graph()

    def save_element(self, e, node=None):

        fmt = e._format

        if not node:
            curr_node = BNode(e.id)
        else:
            curr_node = node

        for k in fmt._rdf_map:
            if k == 'id':
                continue
            # generating nodes for entities: sections, properties and bags of values
            elif (isinstance(fmt, format.Document.__class__) or
                    isinstance(fmt, format.Section.__class__)) and \
                    k == 'sections' and len(getattr(e, k)) > 0:
                sections = getattr(e, k)
                for s in sections:
                    node = BNode(s.id)
                    self.g.add((curr_node, fmt.rdf_map(k), node))
                    self.save_element(s)
            elif isinstance(fmt, format.Section.__class__) and \
                    k == 'properties' and len(getattr(e, k)) > 0:
                properties = getattr(e, k)
                for p in properties:
                    node = BNode(p.id)
                    self.g.add((curr_node, fmt.rdf_map(k), node))
                    self.save_element(p)
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
                print("elem: ", e)
                print("k ", k)
                print("Val ", val)
                if val is None or not val:
                    continue
                elif k == 'date':
                    self.g.add((curr_node, fmt.rdf_map(k), Literal(val, datatype=XSD.date)))
                elif k == 'reference':
                    # TODO check if reference is a string pointing to DB
                    self.g.add((curr_node, fmt.rdf_map(k), URIRef(val)))
                self.g.add((curr_node, fmt.rdf_map(k), Literal(val)))
        return self.g

    def __str__(self):
        return self.save_element(self.doc).serialize(format='pretty-xml').decode("utf-8")

    def __unicode__(self):
        return self.save_element(self.doc).serialize(format='pretty-xml').decode("utf-8")

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
    l = "/home/rick/g-node/python-odml/doc/example_odMLs/ex_1.odml"
    o = odml.load(l)
    r = RDFWriter(o)
    r.save_element(r.doc)
    # r.write_file("./ex_1.xml")
    r.write_file("/home/rick/g-node/python-odml/doc/example_odMLs/ex_1.xml")
