from rdflib import Graph, BNode, Literal
from rdflib.namespace import XSD

from odml.tools.rdf_converter import ODML_NS

g = Graph()

doc = BNode("d1")
s1 = BNode("s1")
p12 = BNode("p1")

g.add((doc, ODML_NS.version, Literal(1.1)))
g.add((doc, ODML_NS.docversion, Literal(42)))
g.add((doc, ODML_NS.author, Literal('D. N. Adams')))
g.add((doc, ODML_NS.date, Literal('1979-10-12', datatype=XSD.date)))
g.add((doc, ODML_NS.hasSection, s1))

g.add((s1, ODML_NS.property, p12))
g.add((s1, ODML_NS.type, Literal('crew')))
g.add((s1, ODML_NS.description, Literal('Information on the crew')))
g.add((s1, ODML_NS.name, Literal('TheCrew')))

content = '[Arthur Philip Dent,Zaphod Beeblebrox,Tricia Marie McMillan,Ford Prefect]'
g.add((p12, ODML_NS.hasValue, Literal(content)))
g.add((p12, ODML_NS.description, Literal('List of crew members names')))
g.add((p12, ODML_NS.dtype, Literal('person')))
g.add((p12, ODML_NS.name, Literal('NameCrewMembers')))

res = g.serialize(format='application/rdf+xml').decode("utf-8")
print(res)

with open("generated_odml_rdf.xml", "w") as f:
    f.write(res)
