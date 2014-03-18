==================
odML Documentation
==================

:Author:
	Lyuba Zehl
:Release:
	0.1

-----------------------------------------------------------------------

odML Description
================

odML (open metadata Markup Language) is an initiative, based on XML, to 
define and establish an open, flexible, easy-to-use, machine-, but also 
human-readable textual format to collect, store and share metadata. 

What are metadata and why are they needed?
	Metadata are data about data, and describing therefore the conditions under 
	which the actual raw-data of an experiment were acquired. A simple example 
	in an electrophysiological context is the sampling-rate which was used 
	recording the raw-data. This may sound ridiculous for everyone doing such 
	an experiment should know how the raw-data were acquired, but what if the 
	data have to be shared in a collaboration and a complete description about 
	how and under which conditions the data were recorded is required?

	odML can help to collect all metadata which are usually distributed over 
	in several files and formats, store them and share them, while maintaining 
	their relation to the actual raw-data.

Key features of odML
	- open, XML based language, to collect, store and share metadata
	- Machine- and human-readable
	- Interactive odML editor for interactive exploration and generation of odML files
	- Python odML library with integrated helper functions':'
		- to generate an odML file
		- to screen metadata content independent from the structure of an odML file


Structure of this tutorial
==========================

The scientific background of the possible user community of odML varies 
enormously (e.g. physics, informatics, mathematics, biology, medicine,
psychology). Some users will be trained programmers, others probably have
never learned a programming language. 

To cover the different demands of all user types, we first provide a slow 
introduction to odML that allows programming beginners to learn the basic 
concepts behind odML and how to generate and use their own odML files either 
using the interactive odML editor or the Python library. In later chapters 
we present the more advanced possibilies of the Python odML library.


Getting Started
===============

Download and Installation
-------------------------

Should be easy using::

    $ python setup.py install

You should be able to just test the library using the following::

    $ export PYTHONPATH=.
    $ python
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import odml

See `github:python-odml#Installation <https://github.com/G-Node/python-odml#installation>`_
for more descriptions including setup on Windows and Debian/Ubuntu.






Introduction to odml
====================


As you can see an odML-file has a tree-like structure with section as branches 
property as end nodes with one value or many values as leafs.

Generating an odML-file
==============================
 
Corresponding to a root of a tree, the document-object connects the most 
highest section-objects to the final tree-like structure. To generate now an 
odML-file one has to create each odML-object individually and append them 
to the wanted tree structure.

As a first step one has to learn how one can create the different objects
and which odML-object can be attached to which other odML-object.


Creating a document
-------------------
As already mentioned the document-object is the root of the odML-file. It 
is possible to create a document-object with no attributes given.

But to be able to identify the author of the odML-file, the date the odML-file
was generated and the current version of the odML-file, it is helpful to 
give these attributes to the document-object::

	>>> document = odml.Document(author="Arthur Dent", date="2014-03-05", version=0.1)
	>>> document
	<Doc 0.1 by Arthur Dent (0 sections)>
	>>> document.author
	'Arthur Dent'
	>>> document.version
	0.1
	
If a common terminology (e.g. the terminology provided by the G-Node) is 
used for the odML-file (how to use the attached terminology see ???), one 
can also already provide the URL to the terminology.odml in the document::
	
	>>> gnode_terminology = "http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml"
	>>> document = odml.Document(author="Arthur Dent", date="2014-03-05", version=0.1, repository=gnode_terminology)
	>>> document
	<Doc 0.1 by Arthur Dent (0 sections)>
	>>> document.repository
	'https://github.com/G-Node/odml-terminologies/blob/master/v1.0/odMLTerminologies.xml'
	
	
Creating a section
------------------
The sections are the branches of the odML-file tree structure. The can either
have section- or property-objects as childrens. The 'name' of a section-object
is a required attribute and has to be given::
	
Other important attributes of a section-object are type and definition::

	>>> section_1 = odml.Section("Subject", type="subject", definition="The investigated experimental subject (animal or person).")
	>>> section_1
	<Section Subject[subject] (0)>
	>>> section_1.type
	'subject'
	>>> section_1.definition
	'The investigated experimental subject (animal or person).'
	
As above mentioned, it is possible to append a section to another section 
creating a subsection::

	>>> section_2 = odml.Section("Preparation", type="subject", definition="Description of the preparation procedure.")
	>>> section_2
	<Section Preparation[subject] (0)>
	>>> section_2.type
	'subject'
	>>> section_2.definition
	'Description of the preparation procedure.'
	>>> section_1.append(section_2)
	>>> section_1
	<Section Subject[subject] (1)>
	>>> section_1.sections
	[<Section Preparation[subject] (0)>]
	
Note that the number in the round brackets of section-object 'Subject' 
increased by one. It corresponds to the number of section-objects below 
the current section-object.


A tree with branches: a document with sections
----------------------------------------------
Let's create first a third section-object before creating a first tree 
structure::

	>>> section_3 = odml.Section("Electrode", type="electrode", definition="Properties to describe an electrode.")
	>>> section_3
	<Section Electrode[electrode] (0)>
	>>> section_3.type
	'electrode'
	>>> section_3.definition
	'Properties to describe an electrode.'
	
Now one append all created section-objects to the document-object::

	>>> document.append(section_1)
	>>> document.append(section_2)
	>>> document
	<Doc 0.1 by Arthur Dent (2 sections)>
	>>> document.sections
	[<Section Subject[subject] (1)>, <Section Electrode[electrode] (0)>]

Note that the section-object 'Subject' still has one subsection. Appending
a section-object always includes all of its appended children (subsections
and/or properties).


Creating properties with values
-------------------------------
Before one creates a property-object one should create a value-object. The 
'data' of a value-object is a required attribute and has to be given::

	>>> value_1 = odml.Value(14)
	>>> value_1
	<int 14>
	>>> value_1.data
	14
	>>> value_1.dtype
	'int'
	
Note that the data type 'int' of the given 'data' of value_1 is automatically 
assigned. This odml data type guessing only works for 'data' of python type 
int, float, str, datetime-objects (date, time, datetime) and bool. One 
can also directly specify the odml data type while creating a value-object
via the 'dtype' attribute. Possible odml data types are 'int', 'float', 
'string', 'date', 'time', 'datetime', 'booleans', 'person', 'text' and 'URL' 
(for details see odml.Value documentation). 

It is also possible to specify in the attributes the uncertainty, the unit 
and the definition of a value-object ::

	>>> value_1 = odml.Value(14, unit="day")
	>>> value_1.unit
	'day'
	>>> value_2 = odml.Value(258.4, uncertainty=1.4, unit="g")
	>>> value_2
	<float 258.4>
	>>> value_2.uncertainty
	1.4
	>>> value_2.unit
	'g'
	>>> value_3 = odml.Value("Rattus norvegicus", definition="Species of the genus Rattus")
	>>> value_3
	<string Rattus norvegicus>
	>>> value_3.definition
	'Species of the genus Rattus'
	
Note that every attribute of a value-object can be overwritten afterwards, 
but the type guessing only works while creating the value-object. If one
changes the data afterwards one needs to change the dtype as well if 
neccessary.

Now let's create a property-object. The name and the value are required
attributes of a property-object. Optional one can give also a definition
to a property-object::

	>>> property_1 = odml.Property("Age", value_1, definition="The age of the subject since birth.")
	>>> property_1
	<Property Age>
	>>> property_1.value
	<int 14>
	>>> property_1.value.data
	14
	>>> property_1.value.dtype
	'int'
	>>> property_1.value.unit
	'day'
	>>> property_1.definition
	'The age of the subject since birth.'
	
	>>> property_2 = odml.Property("Weight", value_2, defintion="The weigth of this subject.")
	>>> property_2
	<Property Weight>
	>>> property_2.value
	<float 258.4>
	>>> property_2.value.data
	258.4
	>>> property_2.value.uncertainty
	1.4	
	>>> property_2.value.dtype
	'float'
	>>> property_2.value.unit
	'g'
	>>> property_2.definition
	'The weigth of this subject.'
	
	>>> property_3 = odml.Property("Species", value_3, definition="The scientific name of the species.")
	>>> property_3
	<Property Species>
	>>> property_3.value
	<string Rattus norvegicus>
	>>> property_2.value.data
	'Rattus norvegicus'
	>>> property_2.value.dtype
	'string'
	>>> property_2.value.definition
	'Species of the genus Rattus'
	>>> property_2.definition
	'The scientific name of the species.'

Note that the value of a property-object is usually given as value-object.
All attributes specified in the value-object remain intact. The value-object
is accessable via 'property.value'.











    
Properties and Values
---------------------

Now we have a section and can create a property. Keep in mind that a property always
needs a value. Values are typed data.:: 

    >>> v = Value(data=144, dtype="int")
    >>> p1 = Property(name="property1", value=v)
    >>> p1.value
    <int 144>

If the supplied value is not a :py:mod:`odml.value.Value` it will be converted to one::

    >>> p1 = Property(name="property1", value=144, dtype="int")
    >>> p1.value
    <int 144>

A property can also contain multiple values::

    >>> v1 = Value(data=1, dtype="int")
    >>> v2 = Value(data=2, dtype="int")
    >>> v3 = Value(data=3, dtype="int")
    >>> p2 = Property(name="property2", value=[v1, v2, v3])
    >>> p2.values
    [<int 1>, <int 2>, <int 3>]
    
Note: If a Property has multiple values, ``p.value`` returns a list
If the Property has only one, ``p.value`` will directly return this value.
In contrast ``p.values`` will always return the list of values, even if it’s only one::

	>>> p1.value
    <int 144>
    >>> p1.values
    [<int 144>]
    >>> p2.value
    [<int 1>, <int 2>, <int 3>]
    >>> p2.values
    [<int 1>, <int 2>, <int 3>]
      
If the supplied value list is not a list of :py:mod:`odml.value.Value` 
each element will be converted to a :py:mod:`odml.value.Value`::

    >>> p2 = Property(name="property2", value=[1, 2, 3], dtype="int")
    >>> p2.values
    [<int 1>, <int 2>, <int 3>]
    
Note: If the supplied value list is not a list of :py:mod:`odml.value.Value` 
all elements are set to the given ``dtype``, but in general a property
can contain multiple values with different ``dtype``::

    >>> v1 = Value(data=1, dtype="int")
    >>> v2 = Value(data=2.0, dtype="float")
    >>> v3 = Value(data="3", dtype="string")
    >>> p2 = Property(name="property2", value=[v1, v2, v3])
    >>> p2.values
    [<int 1>, <float 2.0>, <string 3>]

You can also use the ``append`` function to add a value to an existing property::

	>>> v = Value(data=155, dtype="int")
	>>> p1.append(v)
	>>> p1.values
	[<int 144>, <int 155>]
	
If the supplied value is not a :py:mod:`odml.value.Value` it will be converted to one::

	>>> p1.append(155, dtype="int")
	>>> p1.values
	[<int 144>, <int 155>]
	
As you can see, the ``append`` function is also used to attach a property to a section::

	>>> s.append(p1)
	>>> s.append(p2)
	s.properties
	[<Property property1>, <Property property2>]
	


Working with files
==================
Currently, odML-Files can be read from and written to XML-files.
This is provided by the :py:mod:`odml.tools.xmlparser` module::

    >>> from odml.tools.xmlparser import load, XMLReader, XMLWriter

You can write files using the XMLWriter (``d`` is our ODML-Document from the previous examples)::

    >>> writer = XMLWriter(d)
    >>> writer.write_file('example.odml')

To just print the xml-representation::

    >>> print unicode(writer)
	<odML version="1">
	  <section>
		<property>
		  <value>144<type>int</type></value>
		  <value>155<type>int</type></value>
		  <name>property1</name>
		</property>
		<property>
		  <value>1<type>int</type></value>
		  <value>2.0<type>float</type></value>
		  <value>3<type>string</type></value>
		  <name>property2</name>
		</property>
		<name>section1</name>
		<type>undefined</type>
	  </section>
	</odML>

You can read files using the load()-function for convenience::

    >>> document = load('example.odml')
    <Doc 1.0 by None (1 sections)>

Note: the XML-parser will enforce proper structure.

If you need to parse Strings, you can use the XMLParser, which can also parse odML-objects such as::

    >>> XMLReader().fromString("""<value>13<type>int</type></value>""")
    <int 13>

Advanced odML-Features
======================

Data types and conversion
-------------------------

Values always hold their string-representation (``value`` property).
If they have a ``dtype`` set, this representation will be converted to a native
one (``data`` property)::

    >>> import odml
    >>> odml.Value("13")
    <13>
    >>> v = odml.Value("13")
    >>> v, v.value, v.data
    (<13>, u'13', u'13')
    >>> v.dtype = "int"
    >>> v, v.value, v.data
    (<int 13>, u'13', 13)
    >>> v.dtype = "float"
    >>> v, v.value, v.data
    (<float 13.0>, u'13.0', 13.0)

When changing the ``dtype``, the data is first converted back to its string
representation. Then the software tries to parse this string as the new data type.
If the representation for the data type is invalid, a ``ValueError`` is raised.
Also note, that during such a process, value loss may occur::

    >>> v.data = 13.5
    >>> v.dtype = "int"  # converts 13.5 -> u'13.5' -> 13
    >>> v.dtype = "float"
    >>> v.data
    13.0

The available types are implemented in the :py:mod:`odml.types` Module.

There is one additional special case, which is the ``binary`` data type, that
comes with different encodings (``base64``, ``hexadecimal`` and ``quoted-printable``)::

    >>> v = odml.Value("TcO8bGxlcg==", dtype="binary", encoder="base64")
    >>> v
    <binary TcO8bGxlcg==>
    >>> print v.data
    Müller
    >>> v.encoder = "hexadecimal"
    >>> v
    <binary 4dc3bc6c6c6572>

The checksum is automatically calculated on the raw data and defaults to a
``crc32`` checksum::

    >>> v.checksum
    'crc32$6c47b7c5'
    >>> v.checksum = "md5"
    >>> v.checksum
    'md5$e35bc0a78f1c870124dfc1bbbd23721f'

Links & Includes
----------------

odML-Sections can be linked to other sections, so that they include their
attributes. A link can be within the document (``link`` property) or to an
external one (``include`` property).

After parsing a document, these links are not yet resolved, but can be using
the :py:meth:`odml.doc.BaseDocument.finalize` method::

    >>> d = xmlparser.load("sample.odml")
    >>> d.finalize()

Note: Only the parser does not automatically resolve link properties, as the referenced
sections may not yet be available.
However, when manually setting the ``link`` (or ``include``) attribute, it will
be immediately resolved. To avoid this behaviour, set the ``_link`` (or ``_include``)
attribute instead.
The object remembers to which one it is linked in its ``_merged`` attribute.
The link can be unresolved manually using :py:meth:`odml.section.BaseSection.unmerge`
and merged again using :py:meth:`odml.section.BaseSection.merge`.

Unresolving means to remove sections and properties that do not differ from their
linked equivalents. This should be done globally before saving using the
:py:meth:`odml.doc.BaseDocument.clean` method::

    >>> d.clean()
    >>> xmlparser.XMLWriter(d).write_file('sample.odml')

Changing a ``link`` (or ``include``) attribute will first unmerge the section and
then set merge with the new object.

Terminologies
-------------

odML supports terminologies that are data structure templates for typical use cases.
Sections can have a ``repository`` attribute. As repositories can be inherited,
the current applicable one can be obtained using the :py:meth:`odml.section.BaseSection.get_repository`
method.

To see whether an object has a terminology equivalent, use the :py:meth:`odml.property.BaseProperty.get_terminology_equivalent`
method, which returns the corresponding object of the terminology.

Mappings
--------

A sometimes obscure but very useful feature is the idea of mappings, which can
be used to write documents in a user-defined terminology, but provide mapping
information to a standard-terminology that allows the document to be viewed in
the standard-terminology (provided that adequate mapping-information is provided).

See :py:class:`test.mapping.TestMapping` if you need to understand the
mapping-process itself.

Mappings are views on documents and are created as follows::

    >>> import odml
    >>> import odml.mapping as mapping
    >>> doc = odml.Document()
    >>> mdoc = mapping.create_mapping(doc)
    >>> mdoc
    P(<Doc None by None (0 sections)>)
    >>> mdoc.__class__
    <class 'odml.tools.proxy.DocumentProxy'>

Creating a view has the advantage, that changes on a Proxy-object are
propagated to the original document.
This works quite well and is extensively used in the GUI.
However, be aware that you are typically dealing with proxy objects only
and not all API methods may be available.
