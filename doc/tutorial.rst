
=============
odML Tutorial
=============

:Author:
	Lyuba Zehl;
	based on work by Hagen Fritsch
:Release:
	0.2
:License:
	Creative Commons Attribution-ShareAlike 4.0 International 
	`License <http://creativecommons.org/licenses/by-sa/4.0/>`_
-------------------------------------------------------------------------------


odML (open metadata Markup Language)
====================================

odML (open metadata Markup Language) is a framework, proposed by `Grewe et al. 
(2011) <http://journal.frontiersin.org/article/10.3389/fninf.2011.00016/full>`_, 
to organize and store experimental metadata in a human- and machine-readable, 
XML based format (odml). In this tutorial we will illustrate the conceptual 
design of the odML framework and show hands-on how you can generate your own 
odML metadata file collection. A well organized metadata management of your 
experiment is a key component to guarantee the reproducibility of your research 
and facilitate the provenance tracking of your analysis projects.

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

To cover the different demands of all users, we provide a slow introduction to 
the odML framework that even allows programming beginners to learn the basic 
concepts. We will demonstrate how to generate an odML file and present more 
advanced possibilies of the Python-odML library (e.g., how to search for 
certain metadata or how to integrate existing terminologies). 

At the end of this tutorial we will provide a few guidelines that will help you
to create an odML file structure that is optimised for your individual 
experimental project and complements the special needs of your laboratory. 

The code for the example odML files, which we use within this tutorial is part 
of the documentation package (see doc/example_odMLs/). 

A summary of available odML terminologies and templates can be found `here
<http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml>`_. 


-------------------------------------------------------------------------------


Download and Installation
=========================

The odML framework is an open source project of the German Neuroinformatics
Node (`G-Node <http://www.g-node.org/>`_, `odML project website 
<http://www.g-node.org/projects/odml>`_) of the International Neuroinformatics 
Coordination Facility (`INCF <http://www.g-node.org/>`_). The source code for 
the Python-odML library is available on `GitHub <https://github.com/>`_ under 
the project name `python-odml <https://github.com/G-Node/python-odml>`_.

Dependencies
------------

The Python-odML library (version 1.3) runs under Python 2.7 or 3.5. 

Additionally, the Python-odML library depends on Enum (version 0.4.4).

When the odML-Python library is installed via pip or the setup.py, these 
packages will be automatically downloaded and installed. Alternatively, they 
can be installed from the OS package manager. 

On Ubuntu, the dependency packages are available as ``python-enum`` and 
``python-lxml``.

Note that on Ubuntu 14.04, the latter package additionally requires the 
installation of ``libxml2-dev``, ``libxslt1-dev``, and ``lib32z1-dev``.


Installation...
---------------

... via pip:
************

The simplest way to install the Python-odML library is from `PyPI 
<https://pypi.python.org/pypi>`_ using `pip <https://pip.pypa.io/en/stable/>`_::

	$ pip install odml

The appropriate Python dependencies (Enum and lxml) will be automatically 
downloaded and installed.

If you are not familiar with PyPI and pip, please have a look at the available
online documentation.

Installation
------------

To download the Python-odML library please either use git and clone the 
repository from GitHub::

	$ cd /home/usr/toolbox/
	$ git clone https://github.com/G-Node/python-odml.git
	
... or if you don't want to use git download the ZIP file also provided on 
GitHub to your computer (e.g. as above on your home directory under a "toolbox" 
folder).

To install the Python-odML library, enter the corresponding directory and run::

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


Basic knowledge on odML
=======================

Before we start, it is important to know the basic structure of an odML 
file. Within an odML file metadata are grouped and stored in a 
hierarchical tree structure which consists of four different odML 
objects.

Document:
	- description: *root of the tree*
	- parent: *no parent*
	- children: *Section*

Section:
	- description: *branches of the tree*
	- parent: *Document or Section*
	- children: *Section and/or Property*

Property:
	- description: *leafs of the tree (contains metadata values)*
	- parent: *Section*
	- children: *none*


Each of these odML objects has a certain set of attributes where the 
user can describe the object and its contents. Which attribute belongs 
to which object and what the attributes are used for, is better explained 
in an example odML file (e.g., "THGTTG.odml").


A first look
============

If you want to get familiar with the concept behind the odML framework and how 
to handle odML files in Python, you can have a first look at the example odML 
file provided in the Python-odML library. For this you first need to run the 
python code ("thgttg.py") to generate the example odML file ("THGTTG.odml"). 
When using the following commands, make sure you adapt the paths to the 
python-odml module to your owns!::

	$ cd /home/usr/.../python-odml
	$ ls doc/example_odMLs
	thgttg.py
	$ python doc/example_odMLs/example_odMLs.py "/home/usr/.../python-odml"
	$ ls doc/example_odMLs
	THGTTG.odml  thgttg.py

Now open a Python shell within the Python-odML library directory, e.g. with
IPython::

	$ ipython 

In the IPython shell, first import the odml package::

	>>> import odml

Second, load the example odML file with the following command lines::

	>>> to_load = '/home/usr/toolbox/python-odml/doc/example_odMLs/THGTTG.odml'
	>>> odmlEX = odml.tools.xmlparser.load(to_load)
	
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

If you loaded the example odML file, you can have a first look at the Document 
either by explicitely calling the odml object,...::

	>>> print odmlEX.document
	<Doc 42 by Douglas Adams (2 sections)>
	
... or using the following short cut::

	>>> print odmlEX
	<Doc 42 by Douglas Adams (2 sections)>
	
As you can see, both commands will printout the same short summary about the 
Document of the loaded example odML file. In the following we will only use the 
short cut notation. 

The print out gives you already the follwing information about the odML file:

- '<...>' indicates that you are looking at an object
- 'Doc' tells you that you are looking at an odML Document
- '42' is the version of the odML file
- 'by D. N. Adams' states the author of the odML file
- '(2 sections)' tells you that this odML Document has 2 Section directly 
  appended
  
Note that the Document printout tells you nothing about the depth of the 
complete tree structure, because it is not displaying the children of its 
directly attached Sections. It also does not display all Document attributes. 
In total, a Document has the following 4 attributes:

author
	- recommended Document attribute
	- The author of this odML file. 
	
date
	- recommended Document attribute
	- The date this odML file was created (yyyy-mm-dd format). 
	
repository
	- optional Document attribute
	- The URL to the repository of terminologies used in this odML file. 
	
version
	- recommended Document attribute
	- The version of this odML file. 

Let's find out what attributes were defined for our example Document using the 
following commands::

	>>> odmlEX.author
	'D. N. Adams'
	>>> odmlfile.date
	'1979-10-12'
	>>> odmlEX.version
	42 
	>>> odmlEX.repository

As you learned in the beginning, Sections can be attached to a Document, as the
first hierarchy level of the odML file. Let's have a look which Sections were
attached to the Document of our example odML file using the following command::

	>>> odmlEX.sections
	[<Section TheCrew[crew] (4)>, <Section TheStarship[crew] (1)>]
	
The printout of a Section is explained in the next chapter.
	
	
The Sections
------------

There are several ways to access Sections. You can either call them by name or 
by index using either explicitely the function that returns the list of 
Sections (see last part of 'The Document' chapter) or using again a short cut 
notation. Let's test all the different ways to access a Section, by having a 
look at the first Section in the sections list attached to the Document in our
example odML file::

	>>> odmlEX.sections['TheCrew']
	<Section TheCrew[crew] (4)>
	>>> odmlEX.sections[0]
	<Section TheCrew[crew] (4)>
	>>> odmlEX['TheCrew']
	<Section TheCrew[crew] (4)>
	>>> odmlEX[0]
	<Section TheCrew[crew] (4)>
	
In the following we will use the short cut notation and calling Sections 
explicitely by their name.

The printout of a Section is similar to the Document printout and gives you 
already the following information:

- '<...>' indicates that you are looking at an object
- 'Section' tells you that you are looking at an odML Section
- 'TheCrew' tells you that the Section was named 'TheCrew'
- '[...]' highlights the type of the Section (here 'crew')
- '(4)' states that this Section has four sub-Sections directly attached to it

Note that the Section printout tells you nothing about the number of attached
Properties or again about the depth of a possible sub-Section tree below the 
directly attached ones. It also only list the type of the Section as one of the 
Section attributes. In total, a Section can be defined by the following 5 
attributes:

name
	- obligatory Section attribute
	- The name of the section. Should describe what kind of information can be 
	  found in this section.
	  
definition
	- recommended Section attribute
	- The definition of the content within this section. 
	
type
	- recommended Section attribute
	- The classification type which allows to connect related Sections due to 
	  a superior semantic context.
	  
reference
	- optional Section attribute
	- The ? 
	
repository
	- optional Section attribute
	- The URL to the repository of terminologies used in this odML file. 

Let's have a look what attributes were defined for the Section "TheCrew" using 
the following commands::

	>>> odmlEX['TheCrew'].name
	'TheCrew'
	>>> odmlEX['TheCrew'].definition
	'Information on the crew'
	>>> odmlEX['TheCrew'].type
	'crew'
	>>> odmlEX['TheCrew'].reference
	>>> odmlEX['TheCrew'].repository

To see which Sections are directly attached to the Section 'TheCrew' use again 
the following command::

	>>> odmlEX['TheCrew'].sections
	[<Section Arthur Philip Dent[crew/person] (0)>, 
	 <Section Zaphod Beeblebrox[crew/person] (0)>, 
	 <Section Tricia Marie McMillan[crew/person] (0)>, 
	 <Section Ford Prefect[crew/person] (0)>]
	 
For accessing these sub-Sections you can use again all the following commands::

	>>> odmlEX['TheCrew'].sections['Ford Prefect']
	<Section Ford Prefect[crew/person] (0)>
	>>> odmlEX['TheCrew'].sections[3]
	<Section Ford Prefect[crew/person] (0)>
	>>> odmlEX['TheCrew']['Ford Prefect']
	<Section Ford Prefect[crew/person] (0)>
	>>> odmlEX['TheCrew'][3]
	<Section Ford Prefect[crew/person] (0)>
	 
Besides sub-Sections a Section can also have Properties attached. To see if and
which Properties are attached to the Section 'TheCrew' you have to use the 
following command::

	>>> odmlEX['TheCrew'].properties
	[<Property NameCrewMembers>, <Property NoCrewMembers>]
	
The printout of a Property is explained in the next chapter.
	
	
The Properties
--------------

Properties need to be called explicitely via the properties function of a 
Section. You can then, either call a Property by name or by index::

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

Note that the Property printout tells you nothing about the number of Values, 
and very little about the Property attributes. In total, a Property can be 
defined by the following 6 attributes:

name
	- obligatory Property attribute
	- The name of the Property. Should describe what kind of Values can be 
	  found in this Property.
	  
value
	- obligatory Property attribute
	- The value container of this property. See in 'The Value' chapter for 
	  details.		
	  
definition
	- recommended Property attribute
	- The definition of this Property.
	
dependency
	- optional Property attribute
	- A name of another Property within the same section, which this property 
	  depends on.
	  
dependency_value
	- optional Property attribute
	- Value of the other Property specified in the 'dependency' attribute on 
	  which this Property depends on.	
	  
mapping
	- optional Property attribute
	- The odML path within the same odML file (internal link) to another 
	  Section to which all children of this section, if a conversion is 
	  requested, should be transferred to, as long as the children not 
	  themselves define a mapping.

Let's check which attributes were defined for the Property "NoCrewMembers"::

	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].name
	'NoCrewMembers'
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].definition
	'Number of crew members'
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].dependency
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].dependency_value
	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].mapping

The Value or Values attached to a Property can be accessed via two different
commands. If only one value object was attached to the Property, the first 
command returns directly a Value:: 

	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value
	<int 4>
	
If multiple Values were attached to the Property, a list of Values is 
returned::

	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].value
	[<string Arthur Philip Dent>, <string Zaphod Beeblebrox>, 
	 <string Tricia Marie McMillan>, <string Ford Prefect>]
     
The second command will always return a list independent of the number of 
Values attached::

	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].values
	[<int 4>]
	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values
	[<string Arthur Philip Dent>, <string Zaphod Beeblebrox>, 
	 <string Tricia Marie McMillan>, <string Ford Prefect>]
	
The printout of the Value is explained in the next chapter.

		
The Values
----------

Depending on how many Values are attached to a Property, it can be accessed 
in two different ways. If you know, only one value is attached, you can use the 
following command::

	>>> odmlEX['TheCrew'].properties['NoCrewMembers'].value
	<int 4>
	
If you know, more then one Value is attached, and you would like for e.g., 
access the forth one you can use::

	>>> odmlEX['TheCrew'].properties['NameCrewMembers'].values[3]
	<string Ford Prefect>

The Value printout is reduced and only gives you information about the 
following:

- '<...>' indicates that you are looking at an object
- 'int' tells you that the value has the odml data type (dtype) 'int'
- '4' is the actual data stored within the value object

In total, a Value can be defined by the following 6 attributes:

data
	- obligatory Value attribute
	- The actual metadata value.
	
dtype
	- recommended Value attribute
	- The odml data type of the given metadata value.	
		
definition
	- recommended Value attribute
	- The definition of the given metadata value.
	
uncertainty
	- recommended Value attribute
	- Can be used to specify the uncertainty of the given metadata value.
	
unit
	- recommended Value attribute
	- The unit of the given metadata value, if it has a unit.
	
reference
	- optional Value attribute
	- The ?
	
filename
	- optional Value attribute
	- The ?
	
encoder
	- optional Value attribute
	- Name of the applied encoder used to encode a binary metadata value into 
	  ascii.
	  
checksum
	- optional Value attribute
	- Checksum and name of the algorithm that calculated the checksum of a 
	  given binary metadata value (algorithm$checksum format)

Let's see which attributes were defined for the Value of the Property 
'NoCrewMembers' of the Section 'TheCrew'::

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
	
Note that these commands are for Properties containing one Value. For
accessing attributes of a Value of a Property with multiple Values use::

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
	
If you would like to get all the actual metadata values back from a Property 
with multiple Values, iterate over the Values list::

	>>> all_metadata = []
	>>> for val in doc['TheCrew'].properties['NameCrewMembers'].values:
	...     all_metadata.append(val.data)
	... 
	>>> all_metadata
		['Arthur Philip Dent', 'Zaphod Beeblebrox', 
		 'Tricia Marie McMillan', 'Ford Prefect']
	

------------------------------------------------------------------------


Generating an odML-file
=======================

After getting familiar with the different odml objects and their attributes, 
you will now learn how to generate your own odML file by reproducing some parts 
of the example odml file we presented before.

We will show you first how to create the different odML objects with their 
obligatory and recommended attributes. Please have a look at the tutorial part 
describing the advanced possibilities of the Python odML library for the usage 
of all other attributes.

If you opened a new IPython shell, please import first again the odml package::

	>>> import odml


Create a document
-----------------

Let's start by creating the Document::
 
	>>> MYodML = odml.Document(author='Douglas Adams',
	                           version=42)

You can check if your new Document contains actually what you created by using
some of the commands you learned before::
	                           
	>>> MYodML
	>>> <Doc 42 by Douglas Adams (0 sections)>
	>>> MYodML.date

As you can see, we created a Document with the same attributes as the example,
except that we forgot to define the date. Note that you can always edit 
attributes of generated odml objects. For this let's first import the Python 
package datetime::
	
	>>> import datetime as dt
	
Now we edit the date attribute of the Document::

	>>> MYodML.date = dt.date(1979, 10, 12)
	>>> MYodML.date
	'1979-10-12'

Another part which is still missing is that so far we have no Sections attached 
to our Document. Let's change this!
	

Create a section
----------------

We now create a Section by reproducing the Section "TheCrew" of the example 
odml file from the beginning::

	>>> sec = odml.Section(name='TheCrew',
	                       definition='Information on the crew',
	                       type='crew')

Check if your new Section contains actually what you created::

	>>> sec.name
	'TheCrew'
	>>> sec.definition
	'Information on the crew'
	>>> sec.type
	'crew'

Now we need to attach the Section to our previously generated Document::

	>>> MYodML.append(sec)
	
	>>> MYodML
	<Doc 42 by Douglas Adams (1 sections)>
	>>> MYodML.sections
	[<Section TheCrew[crew] (0)>]
	
We repeat the procedure to create now a second Section which we will attach as 
a sub-Section to the Section 'TheCrew'::

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
	
Note that all of our created Sections do not contain any Properties and Values, 
yet. Let's see if we can change this...


Create a Property-Value(s) pair:
--------------------------------

The creation of a Property is not independent from creating a Value, because a 
Property always needs at least on Value attached. Therefore we will demonstrate 
the creation of Value and Property together.

Let's first create a Property with a single Value::

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

As you can see, we define a odML data type (dtype) for the Value. Generally,
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

The available types are implemented in the odml.types Module.

After learning how we create a simple Porperty-Value-pair, we need to know how
we can attach it to a Section. As exercise, we attach our first Porperty-Value-
pair to the sub-Section 'Arthur Philip Dent'::

	>>> MYodML['TheCrew']['Arthur Philip Dent'].append(prop)
	
	>>> MYodML['TheCrew']['Arthur Philip Dent'].properties
	[<Property Gender>]
	                       
If the odML data type of a Value is distinctly deducible ('int', 'float', 
'boolean', 'string', 'date', 'datetime', or 'time'), you can also use a short 
cut to create a Property-Value pair::

	>>> prop = odml.Property(name='Gender',
	                         definition='Sex of the subject',
	                         value='male')   
	>>> prop
	<Property Gender>
	>>> prop.value
	<string male>
                        
Mark that this short cut will not work for the following odML data types 
'person', 'text', 'url', and 'binary', because they are not automatically 
distinguishable from the odML data type 'string'. 

Next we learn how to create a Property with multiple Values attached to it::

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

To build up our odML file further, we attach this Porperty-Values-pair to 
the Section 'TheCrew'::

	>>> MYodML['TheCrew'].append(prop)
	
	>>> MYodML['TheCrew'].properties
	[<Property NameCrewMembers>]

Just to illustrate you again, we could also make use again of the short cut 
notation, if we would agree to use the odML data type 'string' instead of 
'person' for our Porperty-Values-pair::

	>>> prop = odml.Property(name = 'NameCrewMembers',
	                         definition = 'List of crew members names',
	                         value = ['Arthur Philip Dent', 
	                                  'Zaphod Beeblebrox', 
	                                  'Tricia Marie McMillan', 
	                                  'Ford Prefect'])
	>>> prop.value
	[<string Arthur Philip Dent>, <string Zaphod Beeblebrox>, 
	 <string Tricia Marie McMillan>, <string Ford Prefect>]                 

Note that this short cut also works for creating a Property with a list of 
Values of different data types, e.g.::

	>>> prop = odml.Property(name = 'TestMultipleValueList',
	                         definition = 'List of Values of with different '
	                                      'odML data types',
	                         value = [42,
	                                  42.0,
	                                  True,
	                                  "Don't Panic", 
	                                  dt.date(1979, 10, 12), 
	                                  dt.datetime(1979, 10, 12, 11, 11, 11), 
	                                  dt.time(11, 11, 11)])                         
	>>> prop.values
	[<int 42>, 
	 <float 42.0>, 
	 <boolean True>, 
	 <string Don't Panic>, 
	 <date 1979-10-12>, 
	 <datetime 1979-10-12 11:11:11>, 
	 <time 11:11:11>]         
                                                 
A third way to create a Porperty with multiple Values would be to attach first
one Value and the append further Values later on::

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


Saving an odML file:
--------------------

You can save your odML file using the following command::

	>>> save_to = '/home/usr/toolbox/python-odml/doc/example_odMLs/myodml.odml'
	>>> odml.tools.xmlparser.XMLWriter(MYodML).write_file(save_to)
	
	
Loading an odML file:
---------------------

You already learned how to load the example odML file. Here just as a reminder
you can try to reload your own saved odML file::

	>>> to_load = '/home/usr/toolbox/python-odml/doc/example_odMLs/myodml.odml'
	>>> my_reloaded_odml = odml.tools.xmlparser.load(to_load)


-------------------------------------------------------------------------------


Advanced odML-Features
======================


Advanced knowledge on Values
----------------------------

Data type conversions
*********************

After creating a Value the data type can be changed and the corresponding Value
will converted to the new data type, if the new format is valid for the given
metadata:: 

	>>> test_value = odml.Value(data=1.0)
	>>> test_value
	<float 1.0>
	>>> test_value.dtype = odml.DType.int
	>>> test_value
	<int 1>
	>>> test_value.dtype = odml.DType.boolean
	>>> test_value
	<boolean True>

If the conversion is invalid a ValueError is raised::
    
	>>> test_value.dtype = odml.DType.date
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	  File "/home/zehl/Projects/toolbox/python-odml/odml/value.py", line 163, in dtype
        raise ValueError("cannot convert '%s' from '%s' to '%s'" % (self.value, old_type, new_type))
	ValueError: cannot convert 'True' from 'boolean' to 'date'
       
Also note, that during such a process, metadata loss may occur if a float is 
converted to an integer and then back to a float::

	>>> test_value = odml.Value(data=42.42)
	>>> test_value
	<float 42.42>
	>>> test_value.dtype = odml.DType.int
	>>> test_value
	<int 42>
	>>> test_value.dtype = odml.DType.float
	>>> test_value
	<float 42.0>


Binary metadata
***************

For metadata of binary data type you also need to be specify the correct 
encoder. The following table lists all possible encoders of the odML-libarary
and their binary metadata representation:

+------------------+--------------------------+
| binary encoder   | binary metadata example  |
+==================+==========================+
| quoted-printable | Ford Prefect             |
+------------------+--------------------------+
| hexadecimal      | 466f72642050726566656374 |
+------------------+--------------------------+
| base64           | Rm9yZCBQcmVmZWN0         |
+------------------+--------------------------+

The encoder can also be edited later on::

	>>> test_value = odml.Value(data='Ford Prefect', 
	                            dtype=odml.DType.binary, 
	                            encoder='quoted-printable')
	>>> test_value
	<binary Ford Prefect>
	>>> test_value.encoder = 'hexadecimal'
	>>> test_value
	<binary 466f72642050726566656374>
	>>> test_value.encoder = 'base64'
	>>> test_value
	<binary Rm9yZCBQcmVmZWN0>

The checksum of binary metadata is automatically calculated with ``crc32`` as
default checksum::

	>>> test_value.checksum
	'crc32$10e6c0cf
    
Alternatively, ``md5`` can be used for the checksum calculation::
 
	>>> test_value.checksum = "md5"
	>>> test_value.checksum
	'md5$c1282d5763e2249028047757b6209518'


Advanced knowledge on Properties
--------------------------------

Dependencies & dependency values
********************************
(coming soon)

Advanced knowledge on Sections
------------------------------

Links & Includes
****************
(deprecated; new version coming soon)
Sections can be linked to other Sections, so that they include their defined 
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
*************
(deprecated; new version coming soon)
odML supports terminologies that are data structure templates for typical use cases.
Sections can have a ``repository`` attribute. As repositories can be inherited,
the current applicable one can be obtained using the :py:meth:`odml.section.BaseSection.get_repository`
method.

To see whether an object has a terminology equivalent, use the :py:meth:`odml.property.BaseProperty.get_terminology_equivalent`
method, which returns the corresponding object of the terminology.

Mappings
********
(deprecated; new version coming soon)
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
