===============================
odML and RDF - Export and usage
===============================

Semantic Web and graph database searches
========================================

Searches within odML documents are part of the library implementation and imports from linked, external sources into odML documents can be easily done with the core library functionality.
With the option to export odML documents to the RDF format, users also gain the option to search across multiple documents using tools from the Semantic Web technology.

If you are unfamiliar with it, we linked additional information to the `Semantic web <https://www.w3.org/standards/semanticweb>`_ and `RDF <https://www.w3.org/TR/rdf11-concepts>`_ for your convenience and give the briefest introduction below.

RDF was designed by the World Wide Web Consortium (W3C) as a standard model for data representation and exchange on the web with the heterogeneity of data in mind. Even tough the RDF file format might vary, the underlying concept features two key points. The first is that information is structured in subject-predicate-object triples e.g. "apple hasColor red". The second key point is that multiple subjects and objects can be connected to form a graph e.g. "tree hasFruit apple" can be combined with the previous example to form a minimal graph. These graphs can contain very heterogeneous data, but can still be queried due to the semantic structure of the underlying data.

odML to RDF export
==================

Without further ado the next sections will expose you to the range of odML to RDF features the core library provides.

Default odML to XML RDF export
------------------------------

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


Specific RDF format export
--------------------------

The ``RDFWriter`` class is used to convert odML documents to one of the supported RDF formats:

``xml, pretty-xml, trix, n3, turtle, ttl, ntriples, nt, nt11, trig``

``turtle`` is the format that is best suited for storage and human readability while for cross-tool usage, saving RDF in its ``XML`` variant is probably the safest choice.

The exported output can be returned as a string::

    from odml.tools.rdf_converter import RDFWriter

    print(RDFWriter(doc).get_rdf_str('turtle'))

This will print the content of the odML document in the Turtle flavor of RDF::

    @prefix odml: <https://g-node.org/odml-rdf#> .

    odml:Hub odml:hasDocument odml:08c6e31a-533f-443b-acd2-8e961215d38e .

    odml:08c6e31a-533f-443b-acd2-8e961215d38e a odml:Document ;
        odml:hasFileName "None" ;
        odml:hasSection odml:eebe4bf7-af10-4321-87ec-2cdf77289478 .

    odml:281c5aa7-8fea-4852-85ec-db127f753647 a odml:Property ;
        odml:hasName "rdf_export_property" .

    odml:eebe4bf7-af10-4321-87ec-2cdf77289478 a odml:Section ;
        odml:hasName "rdf_export_section" ;
        odml:hasProperty odml:281c5aa7-8fea-4852-85ec-db127f753647 ;
        odml:hasType "n.s." .

The output can of course also be written to a file with a specified RDF output format; the output file will autmatically be assigned the appropriate file ending::

    from odml.tools.rdf_converter import RDFWriter

    RDFWriter(doc).write_file("./rdf_export_turtle", "turtle")

All available RDF output formats can be viewed via ``odml.tools.parser_utils.RDF_CONVERSION_FORMATS.keys()``.

Bulk export to XML RDF
----------------------

Existing odML files can be exported to XML RDF in bulk using the ``odmltordf`` command line tool that is automatically installed with the core library.

odmlToRDF searches for odML files within a provided SEARCHDIR and converts them to the newest odML format version and exports all found and resulting odML files to XML formatted RDF. Original files will never be overwritten. New files will be written either to a new directory at the current or a specified location.

Usage: odmltordf [-r] [-o OUT] SEARCHDIR

The command line option ``-r`` enables recursive search, ``-o OUT`` specifies a dedicated output folder for the created output files.


Advanced features
=================

RDF subclassing of odml.Section.type
------------------------------------

By default a set of pre-defined odml.Section.types will export Sections not as an odml:Section but as a specific RDF subclass of an odml:Section. This is meant to simplify SPARQL query searches on graph databases that contain odml specific RDF.

As an example an odml.Section normally gets exported as RDF class type odml-rdf:Section::

    <rdf:type rdf:resource="https://g-node.org/odml-rdf#Section"/>

An odml.Section with the odml.Section.type="protocol" will by default be exported as a different RDF class type::

    <rdf:type rdf:resource="https://g-node.org/odml-rdf#Protocol"/>

In an RDF query this can now be searched for directly by asking for RDF class "odml-rdf:Protocol" instead of asking for RDF class "odml-rdf:Section" with type "Protocol".

On install the core library already provides a list of odml.Section.type mappings to RDF subclasses. On initialisation the ``RDFWriter`` loads all subclasses that are available and uses them by default when exporting an odML document to RDF. The available terms and the mappings of odml.Section.types to RDF subclasses can be viewed by accessing the ``section_subclasses`` attribute of an initialised ``RDFWriter``::

    rdf_export = RDFWriter(doc)
    rdf_export.section_subclasses

This export also adds all used subclass definitions to the resulting file to enable query reasoners to makes sense of the introduced subclasses upon a query.

Currently the following mappings of ``odml.Section.type`` values to odml-rdf:Section subclass are available::

    analysis: Analysis
    analysis/power_spectrum: PowerSpectrum
    analysis/psth: PSTH
    cell: Cell
    datacite/alternate_identifier: AlternateIdentifier
    datacite/contributor: Contributer
    datacite/contributor/affiliation: Affiliation
    datacite/contributor/named_identifier: NamedIdentifier
    datacite/creator: Creator
    datacite/creator/affiliation: Affiliation
    datacite/creator/named_identifier: NamedIdentifier
    datacite/date: Date
    datacite/description: Description
    datacite/format: Format
    datacite/funding_reference: FundingReference
    datacite/geo_location: GeoLocation
    datacite/identifier: Identifier
    datacite/related_identifier: RelatedIdentifier
    datacite/resource_type: ResourceType
    datacite/rights: Rights
    datacite/size: Size
    datacite/subject: Subject
    datacite/title: Title
    dataset: Dataset
    data_reference: DataReference
    blackrock: Blackrock
    electrode: Electrode
    event: Event
    event_list: EventList
    experiment: Experiment
    experiment/behavior: Behavior
    experiment/electrophysiology: Electrophysiology
    experiment/imaging: Imaging
    experiment/psychophysics: Psychophysics
    hardware_properties: HardwareProperties
    hardware_settings: HardwareSettings
    hardware: Hardware
    hardware/amplifier: Amplifier
    hardware/attenuator: Attenuator
    hardware/camera_objective: CameraObjective
    hardware/daq: DataAcquisition
    hardware/eyetracker: Eyetracker
    hardware/filter: Filter
    hardware/filter_set: Filterset
    hardware/iaq: ImageAcquisition
    hardware/light_source: Lightsource
    hardware/microscope: Microscope
    hardware/microscope_objective: MicroscopeObjective
    hardware/scanner: Scanner
    hardware/stimulus_isolator: StimulusIsolator
    model/lif: LeakyIntegrateAndFire
    model/pif: PerfectIntegrateAndFire
    model/multi_compartment: MultiCompartmentModel
    model/single_compartment: SingleCompartmentModel
    person: Person
    preparation: Preparation
    project: Project
    protocol: Protocol
    recording: Recording
    setup: Setup
    stimulus: Stimulus
    stimulus/dc: DC
    stimulus/gabor: Gabor
    stimulus/grating: Grating
    stimulus/pulse: Pulse
    stimulus/movie: Movie
    stimulus/ramp: Ramp
    stimulus/random_dot: RandomDot
    stimulus/sawtooth: Sawtooth
    stimulus/sine_wave: Sinewave
    stimulus/square_wave: Squarewave
    stimulus/white_noise: Whitenoise
    subject: Subject

