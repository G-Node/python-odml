==================
odML to RDF export
==================

Opening odML to graph database searches
=======================================

Searches within odML documents are part of the library implementation and imports from linked, external sources into odML documents are possible.
With the option to export odML documents to the RDF format, users also gain the option to search across multiple documents using tools from the Semantic Web technology.

If you are unfamiliar with it, we linked additional information to the `Semantic web` <https://www.w3.org/standards/semanticweb> and `RDF` <https://www.w3.org/TR/rdf11-concepts> for your convenience and give a brief introduction below.

RDF was designed by the World Wide Web Consortium (W3C) as a standard model for data representation and exchange on the web with the heterogeneity of data in mind. Even tough the RDF file format might vary, the underlying concept features two key points. The first is that information is structured in subject-predicate-object triples e.g. "apple hasColor red". The second key point is that multiple subjects and objects can be connected to form a graph e.g. "tree hasFruit apple" can be combined with the previous example to form a minimal graph. These graphs can contain very heterogeneous data, but can still be queried due to the semantic structure of the underlying data.


