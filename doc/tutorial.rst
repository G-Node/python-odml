=============
odML Tutorial
=============

:Author:
	Lyuba Zehl
	based on work by Hagen Fritsch
:Release:
	0.1
:License:
	Creative Commons Attribution-ShareAlike 4.0 International License http://creativecommons.org/licenses/by-sa/4.0/
------------------------------------------------------------------------

odML Description
================

odML (open metadata Markup Language) helps to collect, store and share
metadata. It is an open, flexible, easy-to-use, machine-, but also 
human-readable format based on XML. Developed in the German Neuroinformatics 
Node (G-Node) of the International Neuroinformatics Coordinating Facility 
(INCF) in Munich, odML was a first initiative to connect electrophysiological
recorded data to the documentation of the project the data belong to and 
to all metadata describing the experimental conditions the data were acquired
from.

What are metadata and why are they needed?
	Metadata are data about data, and describing therefore the conditions under 
	which the actual raw-data of an experiment were acquired. A simple example 
	in an electrophysiological context is the sampling-rate which was used 
	recording the raw-data. This may sound ridiculous for everyone doing such 
	an experiment should know how the raw-data were acquired, but what if the 
	data have to be shared in a collaboration and a complete description about 
	how and under which conditions the data were recorded is required?

	odML can help to collect all metadata which are usually distributed over 
	several files and formats, store and share them, while maintaining 
	their relation to the actual raw-data.

Key features of odML
	- open, XML based language, to collect, store and share metadata
	- Machine- and human-readable
	- Interactive odML-Editor for interactive exploration and generation of odML files
	- Python odML library with integrated helper functions
		- to generate an odML file
		- to screen metadata content independent from the structure of an odML file

------------------------------------------------------------------------


Structure of this tutorial
==========================

The scientific background of the possible user community of odML varies 
enormously (e.g. physics, informatics, mathematics, biology, medicine,
psychology). Some users will be trained programmers, others probably have
never learned a programming language. 

To cover the different demands of all user types, we first provide a slow 
introduction to odML that allows programming beginners to learn the basic 
concepts behind odML and how to generate and use their own odML files either 
using the interactive odML-Editor or the Python library. In later chapters 
we present the more advanced possibilies of the Python odML library.

A set of example odML files, which we use within this tutorial are part of
the documentation package (see example_odMLs folder).

------------------------------------------------------------------------


Download and Installation
=========================

Dependencies
------------

Windows
-------

Debian/Ubuntu
-------------
Should be easy using::

    $ python setup.py install

You should be able to just test the library using the following::

    $ export PYTHONPATH=.
    $ python
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import odml

See `github:python-odml#Installation <https://github.com/G-Node/python-odml#installation>`_
for more descriptions including setup on Windows and Debian/Ubuntu.

------------------------------------------------------------------------


Introduction to odml
====================

Before we start, it is important to know the basic structure of an odML file. 
Within an odML file metadata are grouped and stored in a hierachical tree 
structure which consists of four different odML objects.

- 'document':
	- corresponds to the root of the tree (groups everything together)
	- parent: no parent
	- children: section
- 'section':
	- corresponds to branches of the tree
	- parent: section or document
	- children: section and/or property
- 'property':
	- are possible at every node of the tree
	- parent: section
	- children: at least one value
- 'value':
	- corresponds to leaf of the tree (contains metadata)
	- parent: property
	- children: no children
			
Each of these odML objects has a certain set of attributes where the user
can describe the object and its contents. Which attribute belongs to which
object and the meaning of each attribute are better explained in an example
odML file (e.g., "intro-example.odml").

A first look with the odML-Editor
---------------------------------
The best way to get familiar how the different odML objects are linked to 
a complete structure of an odML file, which attribute belongs to which object 
and what each attribute means, is to open one of the example odML files 
in the odML-Editor.

Open the odML-Editor and use the "open files" button in the menu bar (top
of the editor window) to select and open the odML example file "intro-example.odml".

You should then see that the editor window is subdivided into three parts.
	
- Sections window:
	The part on the upper left displays a tree view starting from the top 
	section level of the document.
	
- Properties window:
	If you select one section in the tree view, the part on the upper right 
	will display a table containing the name, value and value attributes of 
	each property (row) belonging to the selected section.
	
- Attributes window:
	The part on the bottom shows you the attributes of the current selected 
	section or property or of the document. As header above the values of 
	the attributes the path to the selected section or property is displayed 
	in red starting from the document. 

Below the attributes window the file path to the currently loaded odML file 
is displayed ("file:///.../doc/example_odMLs/intro-example.odml").
	
A more detailed look at the different objects and their attributes of the 
example odML file ("intro-example.odml") is given in subchapters for each
odML object type (document, section, property, value).

A first look with Python
------------------------
If you are already a little bit familiar with the concept behind an odML
file and you can also have a first look at the example odML file "intro-example.odml"
in Python.

If you open a Python shell, first, import the odml package::

	>>> import odml
	
You can load an odML file with the following command lines::
	
	>>> odmlfile = odml.tools.xmlparser.load("/doc/example_odMLs/intro-example.odml")
	
How you can access the attributes of the different odML objects is described
in more detail in the subchapters for each odML object type (document, 
section, property, value).

The document
------------
Display attributes using the odML-Editor:
*****************************************
To display the attributes of the document of the example odML file click 
on 'Document' in the path of the attributes window (bottom part) of the 
odML-Editor window. 
	
Display attributes using Python:
********************************
To print out the attributes of the document of the example odML file,
use the following commands::

	>>> odmlfile.document.author
	'Arthur Dent'
	>>> odmlfile.document.date
	'2014-03-20'
	>>> odmlfile.document.version
	4.7
	>>> odmlfile.document.repository
	'http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml'

Document attributes:
********************
The meaning of the document attributes are described in the following.
Please note that some attributes are obligatory, some are recommended and 
others are optional. The optional attributes are important for the advanced 
odML possibilies and can for now be ignored by odML beginners. You can find 
an example of their usage in later chapters where the more advanced possibilies 
of the Python odML library are described.

- author
	- recommended document attribute
	- The author of this odML file. 
	- In our example 'Arthur Dent' is the author of the "intro-example.odml" file.
- date
	- recommended document attribute
	- The date this odML file was created (yyyy-mm-dd format). 
	- In our example 'Arthur Dent' created the "intro-example.odml" file at 20th of March 2014 (2014-03-20).
- version
	- recommended document attribute
	- The version of this odML file. 
	- In our example 'Arthur Dent' created version 4.7 of the "intro-example.odml" file.
- repository
	- optional document attribute
	- The URL to the repository of terminologies used in this odML file. 
	- In our example 'Arthur Dent' used the G-Node terminology ("http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml").
		
The sections
------------
Display attributes using the odML-Editor
****************************************
To display the attribute of a section of the example odML file click on 
the section 'Setup' in the sections window (upper left) and a have a look 
at the attributes window (bottom) of the odML-Editor.

Display attributes using Python
*******************************
To print out the attributes of a section, e.g. section 'Setup' of the 
example odML file, use the following commands::

	>>> odmlfile.sections['Setup'].name
	'Setup'
	>>> odmlfile.sections['Setup'].definition
	'Description of the used experimental setup.'
	>>> odmlfile.sections['Setup'].type
	'setup'
	>>> odmlfile.sections['Setup'].reference
	>>> odmlfile.sections['Setup'].link
	>>> odmlfile.sections['Setup'].include
	>>> odmlfile.sections['Setup'].repository
	>>> odmlfile.sections['Setup'].mapping

Section attributes:
*******************
The meaning of the section attributes are described in the following.
Please note that some attributes are obligatory, some are recommended and 
others are optional. The optional attributes are important for the advanced 
odML possibilies and can for now be ignored by odML beginners. You can find 
an example of their usage in later chapters where the more advanced possibilies 
of the Python odML library are described.

- name
	- obligatory section attribute
	- The name of the section. Should describe what kind of information can be found in this section.
	- In our example 'Arthur Dent' used the section name 'Setup'.
- definition
	- recommended section attribute
	- The definition of the content within this section. 
	- In our example 'Arthur Dent' defines the 'Setup' section with the following sentence 'Description of the used experimental setup.'.
- type
	- recommended section attribute
	- The category type of this section which allows to group related sections due to a superior semantic context.
	- In our example 'Arthur Dent' chose 'setup' as superior categorization type of section 'Setup'.
- reference
	- optional section attribute
	- The ? 
	- In our example the section 'Setup' has no reference.
- link
	- optional section attribute
	- The odML path within the same odML file (internal link) to another section from which this section should 'inherit' information.
	- In our example the section 'Setup' is not linked from another section in the odML file.
- include
	- optional section attribute
	- The URL to an other odML file or a section within this external odML file from which this section should 'inherit' information.	
	- In our example  the section 'Setup' is not included from another section of another odML file.
- repository
	- optional section attribute
	- The URL to the repository of terminologies used in this odML file. 
	- In our example the section 'Setup' is not linked to a terminology.
- mapping
	- optional section attribute
	- The odML path within the same odML file (internal link) to another section to which all children of this section, if a conversion is requested, should be transferred to, as long as the children not themselves define a mapping.
	- In our example the section 'Setup' has no mapping.
		
The properties
--------------
Display attributes using the odML-Editor
****************************************
To display the attribute of a property of the example odML file click on 
the section 'Setup' in the sections window (upper left) and then on the 
the property 'Creator' in the properties window (upper right). The attributes
of this property are then displayed in the attributes window (bottom) of 
the odML-Editor.

Display attributes using Python
*******************************
To print out the attributes of a property of a section, e.g. property
'Creator' of the section 'Setup' of the example odML file, use the following 
commands::

	>>> odmlfile.sections['Setup'].properties['Creator'].name
	'Creator'
	>>> odmlfile.sections['Setup'].properties['Creator'].value
	<person Arthur Dent>
	>>> odmlfile.sections['Setup'].properties['Creator'].definition
	'The person who built the setup.'
	>>> odmlfile.sections['Setup'].properties['Creator'].dependency
	>>> odmlfile.sections['Setup'].properties['Creator'].dependency_value
	>>> odmlfile.sections['Setup'].properties['Creator'].mapping	

Property attributes:
********************
The meaning of the property attributes are described in the following.
Please note that some attributes are obligatory, some are recommended and 
others are optional. The optional attributes are important for the advanced 
odML possibilies and can for now be ignored by odML beginners. You can find 
an example of their usage in later chapters where the more advanced possibilies 
of the Python odML library are described.

- name
	- obligatory property attribute
	- The name of the property. Should describe what kind of values can be found in this property.
	- In our example 'Creator' is the property name.
- value
	- obligatory property attribute
	- The value (containing the metadata) of this property. A property can have multiple values.		
	- In our example the person 'Arthur Dent' created the setup.
- definition
	- recommended property attribute
	- The definition of this property.
	- In our example 'Arthur Dent' defines the property 'Creator' as 'The person/s who built the setup.'.
- dependency
	- optional property attribute
	- A name of a propery within the same section, which this property depends on.
	- In our example the property 'Creator' has no dependency.
- dependency value
	- optional property attribute
	- Restriction of the dependency of this property to the property specified in 'dependency' to the very value given in this field.		
	- In our example the property 'Creator' has no dependency, and therefore no dependency value.
- mapping
	- recommended property attribute
	- The odML path within the same odML file (internal link) to another section to which all children of this section, if a conversion is requested, should be transferred to, as long as the children not themselves define a mapping.
	- In our example the property 'Creator' has no mapping.
		
The values
----------
Display attributes using the odML-Editor:
*****************************************
To display the attribute of a value of the example odML file click on 
the section 'Setup' in the sections window (upper left). The attributes
of the value of the property 'Creator' are displayed in the row of the 
property in the properties window (upper right) of the odML-Editor.

Display attributes using Python:
********************************
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
	
Value attributes:
*****************
The meaning of the value attributes are described in the following.
Please note that some attributes are obligatory, some are recommended and 
others are optional. The optional attributes are important for the advanced 
odML possibilies and can for now be ignored by odML beginners. You can find 
an example of their usage in later chapters where the more advanced possibilies 
of the Python odML library are described.

- data
	- obligatory value attribute
	- The actual metadata value.
	- In our example 'Arthur Dent' is the 'Creator'.
- dtype
	- recommended value attribute
	- The data-type of the given metadata value.		
	- In our example 'Arthur Dent' sets the data-type of the given value for the property 'Creator' to 'person'.
- definition
	- recommended value attribute
	- The definition of the given metadata value.
	- In our example 'Arthur Dent' defines the value as 'First and last name of a person.'.
- uncertainty
	- recommended value attribute
	- Specifies the uncertainty of the given metadata value, if it has an uncertainty.
	- In our example the given value of the property 'Creator' has no uncertainty.
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
	- Checksum and name of the algorithm that calculated the checksum of a given value (algorithm$checksum format)
	- In our example there was no checksum calculated for the value 'Arthur Dent'.

------------------------------------------------------------------------


Generating an odML-file
=======================

After getting familiar with the different odml objects and their attributes
during the introduction to odML, you will now learn how to generate your 
own odML file. We will show you first how to create the different odML objects 
with their obligatory and recommended attributes using the odML-Editor and 
Python. Please have a look at the tutorial part describing the advanced 
possibilities of the Python odML library for the usage of the optional attributes.

Creating a document ...
-----------------------
... using the odML-Editor
*************************
You can create then a new document in three ways. In all cases a new window the "New Document Wizard" will open guiding you through the first steps of creating a new odML document.

- If you newly open the odML-Editor, you can also use the link "create a new document" in the "Welcome to the odML-Editor" window. 
- If the odML-Editor is already open use the "create a new document" button in the menu bar (top of the editor window).
- You can also select 'File/New' in the menu of the odML-Editor.

If you click on the 'Forward' button at the right bottom corner, the wizard will display the document attributes with default entries.

- Date: the current date (yyyy-mm-dd format)
- Version: 1.0
- Repository: http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml
- Author: your user name

You can easily change the attributes. For our intro-example.odml we chose the following entries.

- Date: 2014-03-20
- Version: 4.7
- Repository: http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml
- Author: Arthur Dent

If you changed the entries to your needs, you get with the 'Forward' button to the next window, where you can chose, if you provided a link to a terminology repository as document attribute, a set of top section out of your specified terminology. You don't need to select a section. This is optional.

If you click then 'Forward' and 'Apply' you will get back to the actual odML-Editor window, which we described in the 'Introduction to odml'.
You can see your document attributes in the Attributes window at the bottom. You can also see, if you didn't select already some top section out of the terminology, that the sections and the properties window of the odML-Editor are empty.

... using Python
****************
First open a Python shell and import the odml package::

	>>> import odml

You can create a new odML document with its attributes using the following
command::

	>>> document = odml.Document(author = "Arthur Dent", 
	                             date = "2014-03-20", 
	                             version = 4.7)
	
Creating a section ...
----------------------
... using the odML-Editor
*************************
In the odML-Editor, you can create a new (unnamed) section in three ways. In all cases appears a new unnamed section in the Sections window.

- Press the 'add a section to the current selected one' button in the menu bar.
- Select 'Edit/Add/Add Section' in the menu.
- Click the right mice button in the Sections window and then selecting 'Add Section/Empty Section'.

To name this section you have again two options.

- Click on the unnamed section in the sections windows, rename it and press 'Enter'.
- First, select the section you want to rename in the Sections window, then select the attribute 'name' in the Attributes window, click on its 'Value' cell ("unnamed section"), rename it and press 'Enter'.
- In our intro-example.odml we named the section "Setup".

You can change the attributes of a in the Sections window selected section in the Attributes window.

- Select the attribute you want to change, click on its 'Value' cell, change it and press 'Enter'.
- In our intro_example.odml we changed the attribute 'type' to "setup" and the attribute 'definition' to "Description of the used experimental setup."

... using Python
****************
You can create a new odML section with its attributes using the following
command::

	>>> top_section_1 = odml.Section(name = "Setup",
                                     definition = "Description of the used experimental setup.",
                                     type = "setup")

Creating a property with a value ...
------------------------------------
Since a property must contain at least one value, it is best to show you
how you create and combine these two odML objects directly.

... using the odML-Editor
*************************
If you want to create a property in the odML-Editor, first select the section you want to add the property to.
You can create then a new (unnamed) property in three ways. In all cases appears a new unnamed property in the Properties window.

- Press the 'add a property to the current section' button in the menu bar.
- Select 'Edit/Add/Add Property' in the menu.
- Click the right mice button in the Properties window and then selecting 'Add Property'.

To name this property you have again two options.

- Select the unnamed property in the Properties window, click on its 'Name' cell ("unnamed property"), rename it and press 'Enter'.
- First, select the unnamed property in the Properties window, then select the attribute 'name' in the Attributes window, click on its 'Value' cell ("unnamed property"), rename it and press 'Enter'.
- In our intro-example.odml we named the property "Creator".

If you want to change the attributes of a property you have to do it in the Attributes window.

- First, select the property you want to modify in the Properties window, then select the attribute you want to change, click on its 'Value' cell, change it and press 'Enter'.
- In our intro_example.odml we changed the attribute 'definition' to "The person/s who built the setup."

Each new property has directly one value attached to it, which needs to be defined.

- To define a value click on the 'Value' cell of the property in the Properties window, enter a value and press 'Enter'.
- In our intro_example.odml we entered the value "Arthur Dent" to the property "Creator".

To change the attributes of this value stay in the Properties window.

- Click in the row of the value on the cell of the corresponding attribute, change it and press 'Enter'.
- In our intro_example.odml we changed the 'Definition' of the value "Arthur Dent" of the property "Creator" to "First and last name of a person." and the 'Type' of the the value "Arthur Dent" of the property "Creator" to "person"

You can also add multiple values to a selected property. This is possible in three ways.

- Press the 'add a value to the current selected property' button in the menu bar.
- Select 'Edit/Add/Add Value' in the menu.
- Click the right mice button on the property of the Properties window and then selecting 'Add Value'.

... using Python
****************
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

Creating the odML tree
----------------------
... using the odML-Editor
*************************
In the odML-Editor the tree structure is directly created by the user by 
creating top sections and subsections interactively. After creating all
sections, properties and values you can validate your document by pressing
the 'Validate the document and check for errors' button in the menu bar or
by selecting 'Edit/Validate' in the menu. The odML-Editor will present you
a list of error notifications in a new window, if you generated your document
wrongly or if you still forgot some obligatory entries.

... using Python
****************
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
