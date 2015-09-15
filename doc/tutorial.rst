
=============
odML Tutorial
=============

:Author:
	Lyuba Zehl;
	based on work by Hagen Fritsch
:Release:
	0.1
:License:
	Creative Commons Attribution-ShareAlike 4.0 International 
	License http://creativecommons.org/licenses/by-sa/4.0/
-------------------------------------------------------------------------------

odML (open metadata Markup Language)
====================================

odML (open metadata Markup Language) is an XML based file format, 
proposed by [Grewe et al. (2011) Front Neuroinform 5:16], in order 
to provide metadata in an organized, human- and machine-readable way. 
In this tutorial we will illustrate the conceptual design of odML and 
show handson how you can generate your own odML metadata collection. 
In addition, we demonstrate the advantages of using odML to screen 
large numbers of data sets according to selection criteria relevant for 
subsequent analyses. Well organized metadata management is a key 
component to guarantee reproducibility of experiments and to track 
provenance of performed analyses.

What are metadata and why are they needed?
	Metadata are data about data, and describing the conditions under 
	which the actual raw-data of an experiment were acquired. A simple 
	example in an electrophysiological context is the sampling-rate 
	which was used to record the raw-data. This may sound ridiculous for 
	everyone doing such an experiment, but what if the data have to be 
	shared in a collaboration and a complete description about how and 
	under which conditions the data were recorded is required?

	While maintaining their relation to the actual raw-data, odML can 
	help to collect all metadata which are usually distributed over 
	several files and formats, and to store them unitetly which 
	facilitates sharing data and metadata.

Key features of odML
	- open, XML based language, to collect, store and share metadata
	- Machine- and human-readable
	- Interactive odML-Editor
	- Python-odML library
-------------------------------------------------------------------------------


Structure of this tutorial
==========================

The scientific background of the possible user community of odML varies 
enormously (e.g. physics, informatics, mathematics, biology, medicine,
psychology). Some users will be trained programmers, others probably 
have never learned a programming language. 

To cover the different demands of all users, we first provide a slow 
introduction to odML that allows programming beginners to learn the 
basic concepts behind odML. In a next step, we will demonstrate 
how to generate an odML file via the Python-odML library. In 
later chapters we present more advanced possibilies of the Python-odML
library (e.g. how to search for a certain metadata within an odML file). 

Although the structure of an odML is depending on the needs of each 
individual user, we would like to provide at the end of this tutorial a 
few examples on how you can construct an odML assuming a set of use 
case scenarios.

The set of example odML files, which we use within this tutorial are 
part of the documentation package (see doc/example_odMLs/). 

A summary of available odML Terminologies can be found `here
<http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml>`_. 
In the later chapters of this tutorial we will show you how one can 
make use of these terminologies as templates for generating your own 
odML. 


-------------------------------------------------------------------------------


Download and Installation
=========================

The Python-odML library (including the odML-Editor) is available
on `GitHub <https://github.com/G-Node/python-odml>`_:

Dependencies
------------

Windows
-------

Linux (Debian/Ubuntu)
---------------------

Mac OSX
-------


-------------------------------------------------------------------------------


Introduction to odml
====================

Before we start, it is important to know the basic structure of an odML 
file. Within an odML file metadata are grouped and stored in a 
hierarchical tree structure which consists of four different odML 
objects.

- **Document**:
	- corresponds to the root of the tree (groups everything together)
	- *parent*: no parent
	- *children*: Section
- **Section**:
	- corresponds to (big) branches of the tree
	- *parent*: Section or Document
	- *children*: Section and/or Property
- **Property**:
	- corresponds to (small) branches of the tree (groups values)
	- *parent*: Section
	- *children*: at least one Value
- **Value**:
	- corresponds to leaf of the tree (contains metadata)
	- *parent*: Property
	- *children*: no children
			
Each of these odML objects has a certain set of attributes where the 
user can describe the object and its contents. Which attribute belongs 
to which object and what each attribute is used for, is better explained 
in an example odML file (e.g., "intro-example.odml").


A first look
------------
If you want to get familiar with the concept behind an odML and how to handle 
odML files in Python, you can have a first look at the example odML file 
("doc/example_odMLs/intro-example.odml") provided in the Python-odML library.

If you open a Python shell within the Python-odML library directory, first, 
import the odml package::

	>>> import odml
	
You can load an odML file with the following command lines::
	
	>>> odmlfile = "/doc/example_odMLs/intro-example.odml"
	>>> odmlEX1 = odml.tools.xmlparser.load(odmlfile)
	
If you open a Python shell outside of the Python-odML library directory, please
adapt your Python-Path and the path to the "intro-example.odml" file 
accordingly.
	
How you can access the different odML objects and their attributes once you 
loaded an odML file and how you can make use of the attributes is described in 
more detail in the following subchapters for each odML object type (document, 
section, property, value). Please note that some attributes are obligatory, 
some are recommended and others are optional. The optional attributes are 
important for the advanced odML possibilities and can for now be ignored by 
odML beginners. You can find an example of their usage in later chapters.


The Document
************

If you loaded an odML file, you can access the Document either by 
explicitely calling the object,...::

	>>> odmlEX1.document
	<Doc 4.7 by Arthur Dent (1 sections)>
	
... or using a short cut, by just typing::

	>>> odmlEX1
	<Doc 4.7 by Arthur Dent (1 sections)>
	
As you can see, both commands will printout the same short summary about the 
Document of the loaded odML file. In the following we will only use the 
short cut notation. 

The print out gives you already the follwing information about the odML file:

- '<...>' indicates that you are looking at an object
- 'Doc' tells you that you are looking at an odML Document
- '4.7' is the version of the odML file
- 'by Arthur Dent' states the author of the odML file
- '(1 sections)' tells you that this odML Document has exactly 1 Section
  directly appended
  
Note that the print out of the Document tells you nothing about the depth of
the complete tree structure, because it is not displaying the children of its 
directly appended Sections. 
	
The Document is defined by its attributes, which occur only partially in the 
Document printout. In total a Document has the following attributes:

- **author**
	- recommended Document attribute
	- The author of this odML file. 
	- In our example 'Arthur Dent' is the author of the 
	  "intro-example.odml" file.
- **date**
	- recommended Document attribute
	- The date this odML file was created (yyyy-mm-dd format). 
	- In our example 'Arthur Dent' created the "intro-example.odml" file 
	  at 1st of Januarary 2015 (2015-01-01).
- **repository**
	- optional Document attribute
	- The URL to the repository of terminologies used in this odML file. 
	- In our example 'Arthur Dent' used the repository of the odML 
	  terminologies (see link above).  
- **version**
	- recommended Document attribute
	- The version of this odML file. 
	- In our example 'Arthur Dent' created version 1.0 of the 
	  "intro-example.odml" file.

To explicitely print out or access the attributes of the Document of the 
example odML file, use the following commands::

	>>> odmlEX1.author
	'Arthur Dent'
	>>> odmlfile.date
	'2015-01-01'
	>>> odmlEX1.version
	4.7 
	>>> odmlEX1.repository
	'http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml'
	
Besides the Document attributes, there are also multiple functions which can be 
used to screen through the content of the odML file. One of them returns a list 
of all section objects which are directly attached to the Document::

	>>> odmlEX1.sections
	[<Section Setup[setup] (0)>]
	
The print out of the section object is explained in the next subchapter.
	
	
The Sections
************

Similar to the different ways how you access and print out a Document, there 
are several ways to access and print out Sections. You can either call them by 
name or by index using, by either explicitely calling the function that returns 
the list of Sections or using again a short cut notation. Here are all the 
different ways to access the same Section of the odML example file::

	>>> odmlEX1.sections['Setup']
	<Section Setup[setup] (0)>
	>>> odmlEX1.sections[0]
	<Section Setup[setup] (0)>
	>>> odmlEX1['Setup']
	<Section Setup[setup] (0)>
	>>> odmlEX1[0]
	<Section Setup[setup] (0)>
	
In the following we will only use the again the short cut notation and calling 
Sections explicitely by their name.

The printout is similar to the Document printout and gives you already the 
follwing information about the odML Section:

- '<...>' indicates again that you are looking at an object
- 'Section' tells you that you are looking at an odML Section
- 'Setup' tells you that the Section you are looking at was named 'Setup'
- '[...]' highlights the classification type of the Section (here 'setup')
- '(0)' states that this Section has zero sub-Sections attached to it

Note that the printout of the Section tells you nothing about the number of
Properties, and, except the classification type of the Section, nothing about 
the remaining Section attributes. 

The Section can be defined by the following 5 attributes:

- **name**
	- obligatory section attribute
	- The name of the section. Should describe what kind of information can be 
	  found in this section.
	- In our example 'Arthur Dent' used the section name 'Setup'.
- **definition**
	- recommended section attribute
	- The definition of the content within this section. 
	- In our example 'Arthur Dent' defines the 'Setup' section with the 
	  following sentence 'Description of the used experimental setup.'.
- **type**
	- recommended section attribute
	- The category type of this section which allows to group related sections 
	  due to a superior semantic context.
	- In our example 'Arthur Dent' chose 'setup' as superior categorization 
	  type of section 'Setup'.
- **reference**
	- optional section attribute
	- The ? 
	- In our example the section 'Setup' has no reference.
- **repository**
	- optional section attribute
	- The URL to the repository of terminologies used in this odML file. 
	- In our example the section 'Setup' is not linked to a terminology.

To explicitely printout or access the attributes of the Section of the example 
odML file, use the following commands::

	>>> odmlEX1['Setup'].name
	'Setup'
	>>> odmlEX1['Setup'].definition
	'Description of the used experimental setup.'
	>>> odmlEX1['Setup'].type
	'setup'
	>>> odmlEX1['Setup'].reference
	>>> odmlEX1['Setup'].repository

Besides the section attributes, the section object also provides multiple 
functions. Two of them return either a list of all sub-Sections, or a list of 
all Properties, which are directly attached to this Section::

	>>> odmlEX1['Setup'].sections
	[]
	>>> odmlEX1['Setup'].properties
	[<Property Creator>, <Property User>]
	
The printout of the Properties is explained in the next subchapter.
	
	
The Properties
**************

Properties need to called explicitely via the properties function of a Section.
You can then either call a Property by name or by index. Here are all the 
different ways to access the same Property of the Section 'Setup' of the odML 
example file::

	>>> odmlEX1['Setup'].properties['Creator']
	<Property Creator>
	>>> odmlEX1['Setup'].properties[0]
	<Property Creator>

In the following we will only call Properties explicitely by their name.

The Property printout is reduced and only gives you information about the 
following:

- '<...>' indicates that you are looking at an object
- 'Property' tells you that you are looking at an odML Property
- 'Creator' tells you that the Property you are looking at was named 'Creator'

Note that the printout of the Property tells you nothing about the number of
Values, and nothing about the remaining Property attributes. 

The Property can be defined by the following 6 attributes:

- **name**
	- obligatory property attribute
	- The name of the property. Should describe what kind of values can be 
	  found in this property.
	- In our example 'Creator' is the property name.
- **value**
	- obligatory property attribute
	- The value (containing the metadata) of this property. A property can 
	  have multiple values.		
	- In our example the person 'Arthur Dent' created the setup.
- **definition**
	- recommended property attribute
	- The definition of this property.
	- In our example 'Arthur Dent' defines the property 'Creator' as 
	  'The person/s who built the setup.'.
- **dependency**
	- optional property attribute
	- A name of a propery within the same section, which this property depends on.
	- In our example the property 'Creator' has no dependency.
- **dependency value**
	- optional property attribute
	- Restriction of the dependency of this property to the property specified 
	  in 'dependency' to the very value given in this field.		
	- In our example the property 'Creator' has no dependency, and therefore 
	  no dependency value.
- **mapping**
	- optional property attribute
	- The odML path within the same odML file (internal link) to another 
	  section to which all children of this section, if a conversion is 
	  requested, should be transferred to, as long as the children not 
	  themselves define a mapping.
	- In our example the property 'Creator' has no mapping.

To print out the attributes of a property of a section, e.g. property
'Creator' of the section 'Setup' of the example odML file, use the following 
commands::

	>>> odmlEX1['Setup'].properties['Creator'].name
	'Creator'
	>>> odmlEX1['Setup'].properties['Creator'].value
	<person Arthur Dent>
	>>> odmlEX1['Setup'].properties['Creator'].definition
	'The person who built the setup.'
	>>> odmlEX1['Setup'].properties['Creator'].dependency
	>>> odmlEX1['Setup'].properties['Creator'].dependency_value
	>>> odmlEX1['Setup'].properties['Creator'].mapping

Besides the Property attributes, the Property also provides multiple functions. 
Two of them return either a list of odML Values or a single Value, attached to 
this Property::

	>>> odmlEX1['Setup'].sections
	[]
	>>> odmlEX1['Setup'].properties
	[<Property Creator>, <Property User>]
	
The printout of the Properties is explained in the next subchapter.

		
The Values
**********

Values can be accessed and printed out in two different ways. The first 
You can then either call a Property by name or by index. Here are all the 
different ways to access the same Property of the Section 'Setup' of the odML 
example file::

	>>> odmlEX1['Setup'].properties['Creator']
	<Property Creator>
	>>> odmlEX1['Setup'].properties[0]
	<Property Creator>

In the following we will only call Properties explicitely by their name.

The Property printout is reduced and only gives you information about the 
following:

- '<...>' indicates that you are looking at an object
- 'Property' tells you that you are looking at an odML Property
- 'Creator' tells you that the Property you are looking at was named 'Creator'

Note that the printout of the Property tells you nothing about the number of
Values, and nothing about the remaining Property attributes. 

The Property can be defined by the following 6 attributes:

- data
	- obligatory value attribute
	- The actual metadata value.
	- In our example 'Arthur Dent' is the 'Creator'.
- dtype
	- recommended value attribute
	- The data-type of the given metadata value.		
	- In our example 'Arthur Dent' sets the data-type of the given value for 
	  the property 'Creator' to 'person'.
- definition
	- recommended value attribute
	- The definition of the given metadata value.
	- In our example 'Arthur Dent' defines the value as 'First and last name 
	  of a person.'.
- uncertainty
	- recommended value attribute
	- Specifies the uncertainty of the given metadata value, if it has an 
	  uncertainty.
	- In our example the given value of the property 'Creator' has no 
	  uncertainty.
- unit
	- recommended value attribute
	- The unit of the given metadata value, if it has a unit.
	- In our example the given value of the property 'Creator' has no unit.
- reference
	- optional value attribute
	- The ?
	- In our example the value 'Arthur Dent' has no reference.
- filename
	- optional value attribute
	- The ?
	- In our example the value 'Arthur Dent' has no connection to a file.
- encoder
	- optional value attribute
	- Name of the applied encoder used to encode a binary value into ascii.
	- In our example the value 'Arthur Dent' do not need an encoder.
- checksum
	- optional value attribute
	- Checksum and name of the algorithm that calculated the checksum of a 
	  given value (algorithm$checksum format)
	- In our example there was no checksum calculated for the value 
	  'Arthur Dent'.

To print out the attributes of a value of a property of a section, e.g. 
value of property 'Creator' of the section 'Setup' of the example odML 
file, use the following commands::

	>>> odmlfile.sections['Setup'].properties['Creator'].value.data
	u'Arthur Dent'
	>>> odmlfile.sections['Setup'].properties['Creator'].value.dtype
	'person'
	>>> odmlfile.sections['Setup'].properties['Creator'].value.definition
	'First and last name of a person.'	
	>>> odmlfile.sections['Setup'].properties['Creator'].value.uncertainty
	>>> odmlfile.sections['Setup'].properties['Creator'].value.unit
	>>> odmlfile.sections['Setup'].properties['Creator'].value.reference
	>>> odmlfile.sections['Setup'].properties['Creator'].value.filename
	>>> odmlfile.sections['Setup'].properties['Creator'].value.encoder
	>>> odmlfile.sections['Setup'].properties['Creator'].value.checksum
	
Note that these commands are for properties containing one value. For
accessing attributes of one value of a property with multiple values,
see chapter ?.

------------------------------------------------------------------------


Generating an odML-file
=======================

After getting familiar with the different odml objects and their attributes
during the introduction to odML, you will now learn how to generate your 
own odML file. We will show you first how to create the different odML objects 
with their obligatory and recommended attributes using the odML-Editor and 
Python. Please have a look at the tutorial part describing the advanced 
possibilities of the Python odML library for the usage of the optional attributes.

Create a document
*****************

First open a Python shell and import the odml package::

	>>> import odml

You can create a new odML document with its attributes using the following
command::

	>>> document = odml.Document(author = "Arthur Dent", 
	                             date = "2014-03-20", 
	                             version = 4.7)
	

Create a section
****************

You can create a new odML section with its attributes using the following
command::

	>>> top_section_1 = odml.Section(name = "Setup",
                                     definition = "Description of the used experimental setup.",
                                     type = "setup")


Create a property-value(s) pair:
********************************

First we create the value with its attributes using the following command::

	>>> value_1 = odml.Value(data = "Arthur Dent",
	                         dtype = "person",
	                         definition = "First and last name of a person.")
	                       
Then we create the property with its attributes and its value with::

	>>> property_1 = odml.Property(name = "Creator",
	                               definition = "The person/s who built the setup.",
	                               value = value_1)
	                             
The resulting odML property object contains now the first generated odML
value object. Note that you can also enter multiple value objects to one 
property::

	>>> value_2 = odml.Value(data = "Zaphod Beeblebrox",
	                         dtype = "person",
	                         definition = "First and last name of a person.")
	>>> value_3 = odml.Value(data = "Trillian Astra",
	                         dtype = "person",
	                         definition = "First and last name of a person.")
	>>> value_4 = odml.Value(data = "Ford Prefect",
	                         dtype = "person",
	                         definition = "First and last name of a person.")
	                         
	>>> property_2 = odml.Property(name = "User",
		                           definition = "The person/s who use the setup.",
		                           value = [value_2, value_3, value_4])

Build the tree structure
************************
In Python you need to link the created document to the created sections, and
the properties with their already included values to the corresponding sections.

For our intro-example.odml, this meant the following commands::

	>>> document.append(top_section_1)
	>>> top_section_1.append(property_1)
	>>> top_section_1.append(property_2)
	
	

------------------------------------------------------------------------


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
