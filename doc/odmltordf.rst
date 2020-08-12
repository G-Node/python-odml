=====================
Exporting odML to RDF
=====================

Opening odML to the Semantic Web and graph database searches
============================================================

Searches within odML documents are part of the library implementation and imports from linked, external sources into odML documents can be easily done with the core library functionality.
With the option to export odML documents to the RDF format, users also gain the option to search across multiple documents using tools from the Semantic Web technology.

If you are unfamiliar with it, we linked additional information to the `Semantic web<https://www.w3.org/standards/semanticweb>`_ and `RDF<https://www.w3.org/TR/rdf11-concepts>`_ for your convenience and give the briefest introduction below.

RDF was designed by the World Wide Web Consortium (W3C) as a standard model for data representation and exchange on the web with the heterogeneity of data in mind. Even tough the RDF file format might vary, the underlying concept features two key points. The first is that information is structured in subject-predicate-object triples e.g. "apple hasColor red". The second key point is that multiple subjects and objects can be connected to form a graph e.g. "tree hasFruit apple" can be combined with the previous example to form a minimal graph. These graphs can contain very heterogeneous data, but can still be queried due to the semantic structure of the underlying data.

odML to RDF usage
=================

Without further ado the next sections will expose you to the range of odML to RDF features the core library provides.

Saving an odML document to an RDF format file
---------------------------------------------

Using odml.save to export to default XML RDF
********************************************

Once an odML document is available, it can most easily be exported to RDF by the odml.save feature.

Given below is a minimal example::

    import odml

    doc = odml.Document()
    sec = odml.Section(name="rdf_export_section", parent=doc)
    prop = odml.Property(name="rdf_export_property", parent=sec)

    odml.save(doc, "./rdf_export", "RDF")

This will export the odML document to the RDF format in the XML flavor and will save it to the file `./rdf_export.RDF`.
The content of the file will look something like this (the UUIDs of the individual nodes will differ)::

    <?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF
       xmlns:odml="https://g-node.org/odml-rdf#"
       xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description rdf:about="https://g-node.org/odml-rdf#281c5aa7-8fea-4852-85ec-db127f753647">
        <odml:hasName>rdf_export_property</odml:hasName>
        <rdf:type rdf:resource="https://g-node.org/odml-rdf#Property"/>
      </rdf:Description>
      <rdf:Description rdf:about="https://g-node.org/odml-rdf#08c6e31a-533f-443b-acd2-8e961215d38e">
        <odml:hasSection rdf:resource="https://g-node.org/odml-rdf#eebe4bf7-af10-4321-87ec-2cdf77289478"/>
        <odml:hasFileName>None</odml:hasFileName>
        <rdf:type rdf:resource="https://g-node.org/odml-rdf#Document"/>
      </rdf:Description>
      <rdf:Description rdf:about="https://g-node.org/odml-rdf#eebe4bf7-af10-4321-87ec-2cdf77289478">
        <odml:hasName>rdf_export_section</odml:hasName>
        <odml:hasType>n.s.</odml:hasType>
        <odml:hasProperty rdf:resource="https://g-node.org/odml-rdf#281c5aa7-8fea-4852-85ec-db127f753647"/>
        <rdf:type rdf:resource="https://g-node.org/odml-rdf#Section"/>
      </rdf:Description>
      <rdf:Description rdf:about="https://g-node.org/odml-rdf#Hub">
        <odml:hasDocument rdf:resource="https://g-node.org/odml-rdf#08c6e31a-533f-443b-acd2-8e961215d38e"/>
      </rdf:Description>
    </rdf:RDF>
