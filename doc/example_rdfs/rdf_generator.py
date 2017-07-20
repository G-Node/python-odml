from rdflib import Graph, BNode, Literal, Namespace
from rdflib.namespace import XSD

odml = Namespace("http://g-node/odml#")

g = Graph()

doc = BNode("d1")
s1 = BNode("s1")
p12 = BNode("p1")

g.add((doc, odml.version, Literal(1.1)))
g.add((doc, odml.docversion, Literal(42)))
g.add((doc, odml.author, Literal('D. N. Adams')))
g.add((doc, odml.date, Literal('1979-10-12', datatype=XSD.date)))
g.add((doc, odml.hasSection, s1))

g.add((s1, odml.property, p12))
g.add((s1, odml.type, Literal('crew')))
g.add((s1, odml.description, Literal('Information on the crew')))
g.add((s1, odml.name, Literal('TheCrew')))

g.add((p12, odml.hasValue, Literal('[Arthur Philip Dent,Zaphod Beeblebrox,Tricia Marie McMillan,Ford Prefect]')))
g.add((p12, odml.description, Literal('List of crew members names')))
g.add((p12, odml.dtype, Literal('person')))
g.add((p12, odml.name, Literal('NameCrewMembers')))

res = g.serialize(format='application/rdf+xml').decode("utf-8")
print(res)

f = open("generated_ex1.xml", "w")
f.write(res)
f.close()