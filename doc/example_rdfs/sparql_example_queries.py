from rdflib import Graph, Namespace, RDF
from rdflib.plugins.sparql import prepareQuery

g = Graph()
g.parse(
    "/home/rick/g-node/python-odml/rdf_dev/for_copy/test_v1_1_odml_turtle/2010-04-16-ab_cutoff_300_contrast_20%.ttl",
    format='turtle')
q1 = prepareQuery("""SELECT *
            WHERE {
               ?d rdf:type odml:Document .
               ?d odml:hasSection ?s .
               ?s rdf:type odml:Section .
               ?s odml:hasName "Stimulus" .
               ?s odml:hasProperty ?p .
               ?p odml:hasName "Contrast" .
               ?p odml:hasValue ?v .
               ?p odml:hasUnit "%" .
               ?v rdf:type rdf:Bag .
               ?v rdf:li "20.0" .
            }""", initNs={"odml": Namespace("https://g-node.org/projects/odml-rdf#"),
                          "rdf": RDF})

g = Graph()
g.parse(
    "/home/rick/g-node/python-odml/rdf_dev/for_copy/test_v1_1_odml_turtle/2010-04-16-ab_cutoff_300_contrast_20%.ttl",
    format='turtle')
q2 = prepareQuery("""SELECT *
                WHERE {
                   ?d rdf:type odml:Document .
                   ?d odml:hasSection ?s .
                   ?s rdf:type odml:Section .
                   ?s odml:hasName "Stimulus" .
                   ?s odml:hasProperty ?p .

                   ?p odml:hasName "Contrast" .
                   ?p odml:hasValue ?v .
                   ?p odml:hasUnit "%" .    
                   ?v rdf:type rdf:Bag .
                   ?v rdf:li "20.0" .


                   ?d odml:hasSection ?s1 .
                   ?s1 odml:hasName "Cell" .
                   ?s1 odml:hasProperty ?p1 .   

                   ?p1 odml:hasName "CellType" .
                   ?p1 odml:hasValue ?v1 .   
                   ?v1 rdf:li "P-unit" .                      
                }""", initNs={"odml": Namespace("https://g-node.org/projects/odml-rdf#"),
                              "rdf": RDF})

print("q1")
for row in g.query(q1):
    print("Doc: {0}, Sec: {1}, \n"
          "Prop: {2}, Bag: {3}".format(row.d, row.s, row.p, row.v))

print("q2")
for row in g.query(q2):
    print("Doc: {0}, Sec: {1}, \n"
          "Prop: {2}, Bag: {3}".format(row.d, row.s, row.p, row.v))
    print("Doc: {0}, Sec: {1}, \n"
          "Prop: {2}, Bag: {3}".format(row.d, row.s1, row.p1, row.v1))
