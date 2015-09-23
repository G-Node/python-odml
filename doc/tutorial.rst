
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
	`License <http://creativecommons.org/licenses/by-sa/4.0/>`_
-------------------------------------------------------------------------------


odML (open metadata Markup Language)
====================================

odML (open metadata Markup Language) is an XML based file format, 
proposed by [Grewe et al. (2011) Front Neuroinform 5:16], in order 
to provide metadata in an organized, human- and machine-readable way. 
In this tutorial we will illustrate the conceptual design of odML and 
show hands-on how you can generate your own odML metadata collection. 
In addition, we demonstrate the advantages of using odML to screen 
large numbers of data sets according to selection criteria relevant for 
subsequent analyses. Well organized metadata management is a key 
component to guarantee reproducibility of experiments and to track 
provenance of performed analyses.

What are metadata and why are they needed?
	Metadata are data about data. They describe the conditions under which the 
	actual raw-data of an experimental study were acquired. The organization of 
	such metadata and their accessibility may sound like a trivial task, and 
	most laboratories developed their home-made solutions to keep track of 
	their metadata. Most of these solutions, however, break down if data and 
	metadata need to be shared within a collaboration, because implicit 
	knowledge of what is important and how it is organized is often 
	underestimated.

	While maintaining the relation to the actual raw-data, odML can help to 
	collect all metadata which are usually distributed over several files and 
	formats, and to store them unitetly which facilitates sharing data and 
	metadata.

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
psychology). Some users will be trained programmers, others probably have never 
learned a programming language. 

To cover the different demands of all users, we first provide a slow 
introduction to odML that allows programming beginners to learn the basic 
concepts. In a next step, we will demonstrate how to generate an odML file via 
the Python-odML library. In later chapters we present more advanced possibilies 
of the Python-odML library (e.g. how to search for certain metadata or how to
integrate existing terminologies or templates). 

Although the structure of an odML is depending on the needs of each individual 
user, we would like to provide at the end of this tutorial a few guidelines.

The set of example odML files, which we use within this tutorial are 
part of the documentation package (see doc/example_odMLs/). 

A summary of available odML terminologies and templates can be found `here
<http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml>`_. 


-------------------------------------------------------------------------------


Download and Installation
=========================

The Python-odML library (including the odML-Editor) is available on 
`GitHub <https://github.com/G-Node/python-odml>`_. If you are not familiar with 
the version control system **git**, but still want to use it, have a look at 
the documentaion available on the `git-scm website <https://git-scm.com/>`_. 

Dependencies
------------

The Python-odML library runs under Python 2.7. Additionally, there are several
packages the library depence on:
	- **Cairo**
	- **Pango** 
	- **Atk**
	- **GObject**
	- **Gio**
	- **lxml**
	- **gzip**
	- **Enum** (version 0.4.4)


Installation
------------

To download the Python-odML library please either use git and clone the 
repository from GitHub::

	$ cd /home/usr/toolbox/
	$ git clone https://github.com/G-Node/python-odml.git
	
... or if you don't want to use git download the ZIP file also provided on 
GitHub to your computer (e.g. as above on your home directory under a "toolbox" 
folder).

To install the Python-odML library, enter the directory (in our example here, 
/home/usr/toolbox/python-odml/) and run::

	$ cd /home/usr/toolbox/python-odml/
	$ python setup.py install
	

Bugs & Questions
----------------

Should you find a behaviour that is likely a bug, please file a bug report at 
`the github bug tracker <https://github.com/G-Node/python-odml/issues>`_.

If you have questions regarding the use of the library or the editor, ask
the question on `Stack Overflow <http://stackoverflow.com/>`_, be sure to tag
it with `odml` and we'll do our best to quickly solve the problem.


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
provided in the Python-odML library. For this you first need to run the python 
code ("thgttg.py") to generate the example odML file ("THGTTG.odml")::

	$ cd /home/usr/toolbox/python-odml/
	$ python doc/example_odMLs/thgttg.py
    $ ls doc/example_odMLs/
    THGTTG.odml  thgttg.py

If you open a Python shell within the Python-odML library directory, first, 
import the odml package::

	>>> import odml
	
You can load an odML file with the following command lines::
	
	>>> odmlfile = '/home/usr/toolbox/python-odml/doc/example_odMLs/THGTTG.odml'
	>>> odmlEX = odml.tools.xmlparser.load(odmlfile)
	
If you open a Python shell outside of the Python-odML library directory, please
adapt your Python-Path and the path to the "THGTTG.odml" file accordingly.
	
How you can access the different odML objects and their attributes once you 
loaded an odML file and how you can make use of the attributes is described in 
more detail in the following chapters for each odML object type (document, 
section, property, value). Please note that some attributes are obligatory, 
some are recommended and others are optional. The optional attributes are 
important for the advanced odML possibilities and can for now be ignored by 
odML beginners. You can find an example of their usage in later chapters.


The Document
------------

If you loaded an odML file, you can access the Document either by 
explicitely calling the object,...::

	>>> odmlEX.document
	<Doc 42 by Douglas Adams (2 sections)>
	
... or using a short cut, by just typing::

	>>> odmlEX
	<Doc 42 by Douglas Adams (2 sections)>
	
As you can see, both commands will printout the same short summary about the 
Document of the loaded odML file. In the following we will only use the 
short cut notation. 

The print out gives you already the follwing information about the odML file:

- '<...>' indicates that you are looking at an object
- 'Doc' tells you that you are looking at an odML Document
- '42' is the version of the odML file
- 'by Douglas Adams' states the author of the odML file
- '(2 sections)' tells you that this odML Document has 2 Section directly 
  appended
  
Note that the print out of the Document tells you nothing about the depth of
the complete tree structure, because it is not displaying the children of its 
directly appended Sections. 
	
The Document is defined by its attributes, which occur only partially in the 
Document printout. In total a Document has the following attributes:

- **author**
	- recommended Document attribute
	- The author of this odML file. 
- **date**
	- recommended Document attribute
	- The date this odML file was created (yyyy-mm-dd format). 
- **repository**
	- optional Document attribute
	- The URL to the repository of terminologies used in this odML file. 
- **version**
	- recommended Document attribute
	- The version of this odML file. 

To find out what attributes were defined for our example Document, we print out 
or access the attributes using the following commands::

	>>> odmlEX.author
	'Douglas Adams'
	>>> odmlfile.date
	'1979-10-12'
	>>> odmlEX.version
	42 
	>>> odmlEX.repository

To list all two Sections which are directly attached to our example odML file 
use the following command::

	>>> odmlEX.sections
	[<Section TheCrew[crew] (4)>, <Section TheStarship[crew] (1)>]
	
The print out of the section object is explained in the next subchapter.
	
	
The Sections
------------

Similar to the different ways how you access and print out a Document, there 
are several ways to access and print out Sections. You can either call them by 
name or by index using, by either explicitely calling the function that returns 
the list of Sections or using again a short cut notation. Here are all the 
different ways to access a Section of the odML example file::

	>>> odmlEX.sections['TheCrew']
	<Section TheCrew[crew] (4)>
	>>> odmlEX.sections[0]
	<Section TheCrew[crew] (4)>
	>>> odmlEX['TheCrew']
	<Section TheCrew[crew] (4)>
	>>> odmlEX[0]
	<Section TheCrew[crew] (4)>
	
In the following we will only use the again the short cut notation and calling 
Sections explicitely by their name.

The printout is similar to the Document printout and gives you already the 
follwing information about the odML Section:

- '<...>' indicates that you are looking at an object
- 'Section' tells you that you are looking at an odML Section
- 'TheCrew' tells you that the Section was named 'TheCrew'
- '[...]' highlights the classification type of the Section (here 'crew')
- '(4)' states that this Section has four sub-Sections directly attached to it

Note that the printout of the Section tells you nothing about the number of
Properties, and, except the classification type of the Section, nothing about 
the remaining Section attributes or again the depth of a possible sub-section
tree below the directly attached ones.

The Section can be defined by the following 5 attributes:

- **name**
	- obligatory section attribute
	- The name of the section. Should describe what kind of information can be 
	  found in this section.
- **definition**
	- recommended section attribute
	- The definition of the content within this section. 
- **type**
	- recommended section attribute
	- The category type of this section which allows to group related sections 
	  due to a superior semantic context.
- **reference**
	- optional section attribute
	- The ? 
- **repository**
	- optional section attribute
	- The URL to the repository of terminologies used in this odML file. 

To find out what attributes were defined for the Section "TheCrew", we print 
out or access the attributes using the following commands::

	>>> odmlEX['TheCrew'].name
	'TheCrew'
	>>> odmlEX['TheCrew'].definition
	'Information on the crew'
	>>> odmlEX['TheCrew'].type
	'crew'
	>>> odmlEX['TheCrew'].reference
	>>> odmlEX['TheCrew'].repository

To list all two Sections which are directly attached to the Section 'TheCrew'  
use again the following command::

	>>> odmlEX['TheCrew'].sections
	[<Section Arthur Philip Dent[crew/person] (0)>, 
	 <Section Zaphod Beeblebrox[crew/person] (0)>, 
	 <Section Tricia Marie McMillan[crew/person] (0)>, 
	 <Section Ford Prefect[crew/person] (0)>]
	 
For accessing sub-sections you can use again all the following commands::

	>>> odmlEX['TheCrew'].sections['Ford Prefect']
	<Section Ford Prefect[crew/person] (0)>
	>>> odmlEX['TheCrew'].sections[3]
	<Section Ford Prefect[crew/person] (0)>
	>>> odmlEX['TheCrew']['Ford Prefect']
	<Section Ford Prefect[crew/person] (0)>
	>>> odmlEX['TheCrew'][3]
	<Section Ford Prefect[crew/person] (0)>
	 
To list all two Properties which are directly attached to the Section 
'TheCrew', you always have to use the following command::

	>>> odmlEX['TheCrew'].properties
	[<Property NameCrewMembers>, <Property NoCrewMembers>]
	
The printout of the Properties is explained in the next chapter.
	
	
The Properties
--------------

Properties need to called explicitely via the properties function of a Section.
You can then, either call a Property by name or by index. To access a Property 
of the Section 'TheCrew' in our example you can use the following commands::

	>>> odmlEX['TheCrew'].properties['NoCrewMembers']
	<Property NoCrewMembers>
	>>> odmlEX['Setup'].properties[1]
	<Property NoCrewMembers>

In the following we will only call Properties explicitely by their name.

The Property printout is reduced and only gives you information about the 
following:

- '<...>' indicates that you are looking at an object
- 'Property' tells you that you are looking at an odML Property
- 'NoCrewMembers' tells you that the Property was named 'NoCrewMembers'

Note that the printout of the Property tells you nothing about the number of
Values, and nothing about the remaining Property attributes. 

The Property can be defined by the following 6 attributes:

- **name**
	- obligatory property attribute
	- The name of the property. Should describe what kind of values can be 
	  found in this property.
- **value**
	- obligatory property attribute
	- The value (containing the metadata) of this property. A property can 
	  have multiple values.		
- **definition**
	- recommended property attribute
	- The definition of this property.
- **dependency**
	- optional property attribute
	- A name of a propery within the same section, which this property depends on.
	- In our example the property 'Creator' has no dependency.
- **dependency value**
	- optional property attribute
	- Restriction of the dependency of this property to the property specified 
	  in 'dependency' to the very value given in this field.		
- **mapping**
	- optional property attribute
	- The odML path within the same odML file (internal link) to another 
	  section to which all children of this section, if a conversion is 
	  requested, should be transferred to, as long as the children not 
	  themselves define a mapping.

To find out what attributes were defined for the Property "NoCrewMembers", we 
print out or access the attributes using the following commands::

	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].name
	'NoCrewMembers'
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].definition
	'Number of crew members'
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].dependency
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].dependency_value
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].mapping

To list all Values which are directly attached to the Property 'NoCrewMembers', 
you can use two different commands. The first command returns directly a value 
object, if only one value object was attached to the property, while it will 
return a list of value objects if more than one value object was attached::

	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value
	<int 4>
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].value
    [<string Arthur Philip Dent>, <string Zaphod Beeblebrox>, 
     <string Tricia Marie McMillan>, <string Ford Prefect>]
     
The second command will always return a list independent of the number of value
objects attached::

	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].values
	[<int 4>]
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values
    [<string Arthur Philip Dent>, <string Zaphod Beeblebrox>, 
     <string Tricia Marie McMillan>, <string Ford Prefect>]
	
The printout of the Value is explained in the next chapter.

		
The Values
----------

Depending on how many Values are attached to a Property, it can be accessed 
and printed out in two different ways. If you know, only one value is attached,
you can use the following command::

	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value
	<int 4>
	
If you know, more then one Value is attached, and you would like for e.g., 
access the first one you can use::

	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3]
	<string Ford Prefect>

The Value printout is reduced and only gives you information about the 
following:

- '<...>' indicates that you are looking at an object
- 'int' tells you that the value has the odml data type (dtype) 'int'
- '4' is the actual data stored within the value object

The Value can be defined by the following 6 attributes:

- data
	- obligatory value attribute
	- The actual metadata value.
- dtype
	- recommended value attribute
	- The data-type of the given metadata value.		
- definition
	- recommended value attribute
	- The definition of the given metadata value.
- uncertainty
	- recommended value attribute
	- Specifies the uncertainty of the given metadata value, if it has an 
	  uncertainty.
- unit
	- recommended value attribute
	- The unit of the given metadata value, if it has a unit.
- reference
	- optional value attribute
	- The ?
- filename
	- optional value attribute
	- The ?
- encoder
	- optional value attribute
	- Name of the applied encoder used to encode a binary value into ascii.
- checksum
	- optional value attribute
	- Checksum and name of the algorithm that calculated the checksum of a 
	  given value (algorithm$checksum format)

To print out the attributes of a value of a property of a section, e.g. 
value of property 'Creator' of the section 'Setup' of the example odML 
file, use the following commands::

	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value.data
	4
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value.dtype
	'int'
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value.definition
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value.uncertainty
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value.unit
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value.reference
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value.filename
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value.encoder
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value.checksum
	
Note that these commands are for properties containing one value. For
accessing attributes of a value of a property with multiple values use::

	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3].data
	'Ford Prefect'
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3].dtype
	'person'
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3].definition
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3].uncertainty
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3].unit
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3].reference
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3].filename
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3].encoder
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3].checksum
	
If you would like to get the data back from a Property with multiple values,
iterate over the values list::

    >>> all_data = []
	>>> for val in doc['TheCrew'].properties['NameCrewMembers'].values:
	...     all_data.append(val.data)
	... 
	>>> all_data
		['Arthur Philip Dent', 'Zaphod Beeblebrox', 
		 'Tricia Marie McMillan', 'Ford Prefect']
	

------------------------------------------------------------------------


Generating an odML-file
=======================

After getting familiar with the different odml objects and their attributes, 
you will now learn how to generate your own odML file by reproducing the 
example odml file we presented before.

We will show you first how to create the different odML objects with their 
obligatory and recommended attributes. Please have a look at the tutorial part 
describing the advanced possibilities of the Python odML library for the usage 
of all other attributes.

Create a document
-----------------

First open a Python shell and import the odml package::

	>>> import odml
	
Let's start by creating the Document::
 
	>>> MYodML = odml.Document(author='Douglas Adams',
	                           date='1979-10-12',
	                           version=42)

You can check if your new Document contains actually what you created by using
some of the commands you learned before::
	                           
	>>> MYodML
	>>> <Doc 42 by Douglas Adams (0 sections)>
	>>> MYodML.date
	'1979-10-12'

As you can see we created a Document with the same attributes as the example, 
except for the repository. You can also see that, so far, no sections is 
attached to it. Let's change this!
	

Create a section
----------------

We now create a Section by reproducing the Section "TheCrew" of the example 
odml file from the beginning::

	>>> sec = odml.Section(name='TheCrew',
	                       definition='Information on the crew',
	                       type='crew')

You can check if your new Section contains actually what you created by using
some of the commands you learned before::

	>>> sec.name
	'TheCrew'
	>>> sec.definition
	'Information on the crew'
	>>> sec.type
	'crew'

Now we need to attach the Section to our previously generated Document:

	>>> MYodML.append(sec)
	
	>>> MYodML
	<Doc 42 by Douglas Adams (1 sections)>
	>>> MYodML.sections
	[<Section TheCrew[crew] (0)>]
	
We repeat the procedure to create a second section and then attach it as a 
subsection to the section we just created::

	>>> sec = odml.Section(name='Arthur Philip Dent',
	                       definition='Information on Arthur Dent',
	                       type='crew/person')
	>>> sec
	<Section Arthur Philip Dent[crew/person] (0)>
	
	>>> MYodML['TheCrew'].append(sec)
	
	>>> MYodML.sections
	[<Section TheCrew[crew] (0)>]
	>>> MYodML['TheCrew'].sections
	[<Section Arthur Philip Dent[crew/person] (0)>]
	
Note that all of our created sections do not contain any properties and values, 
yet. Let's see if we can change this in the next chapter.


Create a property-value(s) pair:
--------------------------------

The creation of a property is not independent from creating a value object, 
because a property always needs at least on value attached. Therefore we will
demonstrate the creation of value and property objects together.

Let's first create a property with a single value::

	>>> val = odml.Value(data="male", 
	                     dtype=odml.DType.string)
	>>> val
	<string male>
	
	>>> prop = odml.Property(name='Gender',
	                         definition='Sex of the subject',
	                         value=val)                     
	>>> prop
	<Property Gender>
	>>> prop.value
    <string male>

As you can see, we define a odML data type (dtype) for the value. Generally,
you can use the following odML data types to describe the format of the stored 
metadata:

+-----------------------------------+---------------------------------------+
| dtype                             | required data examples                |
+===================================+=======================================+
| odml.DType.int or 'int'           | 42                                    |
+-----------------------------------+---------------------------------------+
| odml.DType.float or 'float'       | 42.0                                  |
+-----------------------------------+---------------------------------------+
| odml.DType.boolean or 'boolean'   | True or False                         |
+-----------------------------------+---------------------------------------+
| odml.DType.string or 'string'     | 'Earth'                               |
+-----------------------------------+---------------------------------------+
| odml.DType.date or 'date'         | dt.date(1979, 10, 12)                 |
+-----------------------------------+---------------------------------------+
| odml.DType.datetime or 'datetime' | dt.datetime(1979, 10, 12, 11, 11, 11) |
+-----------------------------------+---------------------------------------+
| odml.DType.time or 'time'         | dt.time(11, 11, 11)                   |
+-----------------------------------+---------------------------------------+
| odml.DType.person or 'person'     | 'Zaphod Beeblebrox'                   |
+-----------------------------------+---------------------------------------+
| odml.DType.text or 'text'         |                                       |
+-----------------------------------+---------------------------------------+
| odml.DType.url or 'url'           | "https://en.wikipedia.org/wiki/Earth" |
+-----------------------------------+---------------------------------------+
| odml.DType.binary or 'binary'     | '00101010'                            |
+-----------------------------------+---------------------------------------+

After learning how we create a simple porperty-value-pair, we need to know how
we can attach it to a section. As exercise, we attach our first porperty-value-
pair to the subsection 'Arthur Philip Dent'::

	>>> MYodML['TheCrew']['Arthur Philip Dent'].append(prop)
	
	>>> MYodML['TheCrew']['Arthur Philip Dent'].properties
	[<Property Gender>]
	                       
If the odML data type of a value is distinctly deducible ('int', 'float', 
'boolean', 'string', 'date', 'datetime', or 'time'), you can also use a short 
cut to create a property-value pair::

    >>>> prop = odml.Property(name='Gender',
	                          definition='Sex of the subject',
	                          value='male')   
	>>> prop
	<Property Gender>
	>>> prop.value
    <string male>
                        
Mark that this short cut will not work for the following odML data types 
'person', 'text', 'url', and 'binary', because they are not automatically 
distinguishable from the odML data type 'string'. 

Next we learn how to create a property with multiple values attached to it::

	>>> vals = [odml.Value(data='Arthur Philip Dent', 
	                       dtype=odml.DType.person),
	            odml.Value(data='Zaphod Beeblebrox', 
	                       dtype=odml.DType.person),
	            odml.Value(data='Tricia Marie McMillan', 
	                       dtype=odml.DType.person),
	            odml.Value(data='Ford Prefect', 
	                       dtype=odml.DType.person)]
    >>> vals
    [<person Arthur Philip Dent>, <person Zaphod Beeblebrox>, 
     <person Tricia Marie McMillan>, <person Ford Prefect>]

	>>> prop = odml.Property(name = 'NameCrewMembers',
	                         definition = 'List of crew members names',
	                         value = vals)
	>>> prop
	<Property NameCrewMembers>
	>>> prop.values
    [<person Arthur Philip Dent>, <person Zaphod Beeblebrox>, 
     <person Tricia Marie McMillan>, <person Ford Prefect>]               

To build up our odML file further, we attach this porperty-values-pair to 
the section 'TheCrew'::

	>>> MYodML['TheCrew'].append(prop)
	
	>>> MYodML['TheCrew'].properties
	[<Property NameCrewMembers>]

Just to illustrate you again, we could also make use again of the short cut 
notation, if we would agree to use the odML data type 'string' instead of 
'person' for our second porperty-values-pair::

	>>> prop = odml.Property(name = 'NameCrewMembers',
	                         definition = 'List of crew members names',
	                         value = ['Arthur Philip Dent', 
	                                  'Zaphod Beeblebrox', 
	                                  'Tricia Marie McMillan', 
	                                  'Ford Prefect'])
    >>> prop.value
	[<string Arthur Philip Dent>, <string Zaphod Beeblebrox>, 
	 <string Tricia Marie McMillan>, <string Ford Prefect>]                 
	                                                           
A third way to create a porperty with multiple values would be to attach first
one value and the append further values later on::

    >>> val = odml.Value(data="Arthur Philip Dent",
                         type=odml.DType.person)

	>>> prop = odml.Property(name = 'NameCrewMembers',
	                         definition = 'List of crew members names',
	                         value = val)
	>>> prop.values
	[<person Arthur Philip Dent>]

    >>> val = odml.Value(data="Zaphod Beeblebrox",
                         type=odml.DType.person)	
    >>> prop.append(val)
    >>> prop.values
    [<person Arthur Philip Dent>, <person Zaphod Beeblebrox>]
    
    >>> val = odml.Value(data="Tricia Marie McMillan",
                         type=odml.DType.person)	
    >>> prop.append(val)      
    >>> prop.values
    [<person Arthur Philip Dent>, <person Zaphod Beeblebrox>,
     <person Tricia Marie McMillan>]
    
    >>> val = odml.Value(data="Ford Prefect",
                         type=odml.DType.person)	
    >>> prop.append(val)                                            
    >>> prop.values
    [<person Arthur Philip Dent>, <person Zaphod Beeblebrox>,
     <person Tricia Marie McMillan>, <person Ford Prefect>]


Printing XML-representation of an odML file:
--------------------------------------------

Although the XML-representation of an odML file is a bit hard to read, it is 
sometimes helpful to check, especially during a generation process, how the 
hierarchical structure of the odML file looks like.

Let's have a look at the XML-representation of our small odML file we just 
generated::

	>>> print unicode(odml.tools.xmlparser.XMLWriter(MYodML))
	<odML version="1">
	  <date>1979-10-12</date>
	  <section>
	    <definition>Information on the crew</definition>
	    <property>
	      <definition>List of crew members names</definition>
	      <value>Arthur Philip Dent<type>person</type></value>
	      <value>Zaphod Beeblebrox<type>person</type></value>
	      <value>Tricia Marie McMillan<type>person</type></value>
	      <value>Ford Prefect<type>person</type></value>
	      <name>NameCrewMembers</name>
	    </property>
	    <name>TheCrew</name>
	    <section>
	      <definition>Information on Arthur Dent</definition>
	      <property>
	        <definition>Sex of the subject</definition>
	        <value>male<type>string</type></value>
	        <name>Gender</name>
	      </property>
	      <name>Arthur Philip Dent</name>
	      <type>crew/person</type>
	    </section>
	    <type>crew</type>
	  </section>
	  <version>42</version>
	  <author>Douglas Adams</author>
	</odML>


Saving a odML file:
-------------------

You can save your odML file using the following command::

	>>> save_to = '/home/usr/toolbox/python-odml/doc/example_odMLs/myodml.odml'
	>>> odml.tools.xmlparser.XMLWriter(MYodML).write_file(save_to)

-------------------------------------------------------------------------------

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
