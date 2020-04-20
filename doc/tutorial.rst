
=============
odML Tutorial
=============

:Author:
    Lyuba Zehl;
    based on work by Hagen Fritsch
:Release:
    1.4
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
    formats, and to store them unitedly which facilitates sharing data and
    metadata.

Key features of odML
    - open, XML based language, to collect, store and share metadata
    - Machine- and human-readable
    - Python-odML library
    - Interactive odML-Editor

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
advanced possibilities of the Python-odML library (e.g., how to search for
certain metadata or how to integrate existing terminologies).

At the end of this tutorial we will provide a few guidelines that will help you
to create an odML file structure that is optimised for your individual
experimental project and complements the special needs of your laboratory.

The code for the example odML files, which we use within this tutorial is part
of the documentation package (see doc/example_odMLs/).

A summary of available odML terminologies and templates can be found `here
<https://terminologies.g-node.org/v1.1/terminologies.xml>`_.

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

The Python-odML library (version 1.4+) runs under Python 3.6+.

Additionally, the Python-odML library depends on the lxml, pyyaml and rdflib python packages.

When the odML-Python library is installed via pip or the setup.py, these
packages will be automatically downloaded and installed. Alternatively, they
can be installed from the OS package manager.

On Ubuntu, the dependency packages are available as ``python-lxml``, ``python-yaml`` and ``python-rdflib``.

Note that on Ubuntu 14.04, the latter package additionally requires the
installation of ``libxml2-dev``, ``libxslt1-dev``, and ``lib32z1-dev``.

Python 2 has reached end of life. We will not keep any future versions of odml Python 2 compatible and also recommend using a Python version >= 3.6. If a Python version < 3.6 is a requirement, the following dependency needs to be installed as well:

The ``enum34`` package with a ``pip`` installation or ``python-enum`` using the OS package manager.

Installation...
---------------

... via pip:
************

The simplest way to install the Python-odML library is from `PyPI
<https://pypi.python.org/>`_ using `pip <https://pip.pypa.io/en/stable/>`_::

    $ pip install odml

The appropriate Python dependencies will be automatically
downloaded and installed.

If you are not familiar with PyPI and pip, please have a look at the available
online documentation.

... from source:
****************

To download the Python-odML library please either use git and clone the
repository from GitHub::

    $ cd /home/usr/toolbox/
    $ git clone https://github.com/G-Node/python-odml.git

... or if you don't want to use git, download the ZIP file also provided on
GitHub to your computer (e.g. as above on your home directory under a "toolbox"
folder).

To install the Python-odML library, enter the corresponding directory and run::

    $ cd /home/usr/toolbox/python-odml/
    $ python setup.py install


Bugs & Questions
----------------

Should you find a behaviour that is likely a bug, please file a bug report at
`the github bug tracker <https://github.com/G-Node/python-odml/issues>`_.

-------------------------------------------------------------------------------

Basic knowledge on odML
=======================

Before we start, it is important to know the basic structure of an odML
file. Within an odML file metadata are grouped and stored in a
hierarchical tree structure which consists of three basic odML
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
to which object and what the attributes are used for is better explained
in an example odML file (cf., "THGTTG.odml").


A first look
============

If you want to get familiar with the concept behind the odML framework and how
to handle odML files in Python, you can have a first look at the example odML
file provided in the Python-odML library. For this you first need to run the
python code ("thgttg.py") to generate the example odML file ("THGTTG.odml").
When using the following commands, make sure you adapt the paths to the
python-odml module to your own!::

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

    >>> to_load = './doc/example_odMLs/THGTTG.odml'
    >>> odmlEX = odml.load(to_load)

If you open a Python shell outside of the Python-odML library directory, please
adapt your Python-Path and the path to the "THGTTG.odml" file accordingly.

How you can access the different odML objects and their attributes once you
loaded an odML file and how you can make use of the attributes is described in
more detail in the following chapters for each odML object type (Document,
Section, Property).

How you can create the different odML objects on your own and how to connect
them to build your own metadata odML file will be described in later chapters.
Further advanced functions you can use to navigate through your odML files, or to
create an odML template file, or to make use of common odML terminologies
provided via `the G-Node repository
<https://terminologies.g-node.org/v1.1/terminologies.xml>`_ can also
be found later on in this tutorial.

But now, let us first have a look at the example odML file (THGTTG.odml)!


The Document
------------

If you loaded the example odML file, let's have a first look at the Document::

    >>> print odmlEX
    Document 42 {author = D. N. Adams, 2 sections}

As you can see, the printout gives you a short summary of the Document of the
loaded example odML file.

The print out gives you already the following information about the odML file:

- ``Document`` tells you that you are looking at an odML Document
- ``42`` is the user defined version of this odML file
- ``{...}`` provides ``author`` and number of attached sections
- ``author`` states the author of the odML file, "D. N. Adams" in the example case
- ``2 sections`` tells you that this odML Document has 2 Section directly
  appended

Note that the Document printout tells you nothing about the depth of the
complete tree structure, because it is not displaying the children of its
directly attached Sections. It also does not display all Document attributes.
In total, a Document has the following attributes:

author
    - Returns the author (returned as string) of an odML document.

date
    - Returns a user defined date. Could for example be used to state
      the date of the document creation or the date of the latest change.

document
    - Returns the current Document object.

parent
    - Returns the parent object (which is ``None`` for a Document).

repository
    - Returns the URL (returned as string) to a user defined repository of
      terminologies used in this Document. Could be the URL to the G-Node
      terminologies or to a user defined template.

version
    - Returns the user defined version (returned as string) of this odML file.

id
    - id is a UUID (universally unique identifier) that uniquely identifies
      the current document. If not otherwise specified, this id is automatically
      created and assigned.

Let's check out all attributes with the following commands::

    >>> print(odmlEX.author)
    D. N. Adams
    >>> print(odmlEX.date)
    1979-10-12
    >>> print(odmlEX.document)
    Document 42 {author = D. N. Adams, 2 sections}
    >>> print(odmlEX.parent)
    None
    >>> print(odmlEX.repository)
    https://terminologies.g-node.org/v1.1/terminologies.xml
    >>> print(odmlEX.version)
    42

As expected for a Document, the attributes ``author`` and ``version`` match the
information given in the Document printout, the document attribute just returns
the Document, and the parent attribute is ``None``.

As you learned in the beginning, Sections can be attached to a Document. They
represent the next hierarchy level of an odML file. Let's have a look which
Sections were attached to the Document of our example odML file using the
following command::

    >>> print(odmlEX.sections)
    [Section[4|2] {name = TheCrew, type = crew, id = ...},
     Section[1|7] {name = TheStarship, type = starship, id = ...}]

As expected from the Document printout our example contains two Sections. The
printout and attributes of a Section are explained in the next chapter.

The Sections
------------

There are several ways to access Sections. You can either call them by name or
by index using either explicitly the function that returns the list of
Sections (see last part of `The Document`_ chapter) or using again a short cut
notation. Let's test all the different ways to access a Section, by having a
look at the first Section in the sections list attached to the Document in our
example odML file::

    >>> print(odmlEX.sections['TheCrew'])
    Section[4|2] {name = TheCrew, type = crew, id = ...}
    >>> print(odmlEX.sections[0])
    Section[4|2] {name = TheCrew, type = crew, id = ...}
    >>> print(odmlEX['TheCrew'])
    Section[4|2] {name = TheCrew, type = crew, id = ...}
    >>> print(odmlEX[0])
    Section[4|2] {name = TheCrew, type = crew, id = ...}

In the following we will call Sections explicitly by their name using the
short cut notation.

The printout of a Section is similar to the Document printout and gives you
already the following information:

- ``Section`` tells you that you are looking at an odML Section
- ``[4|2]`` states that this Section has four Sections and two Properties directly attached to it
- ``{...}`` provides ``name``, ``type`` and ``id`` of the Section
- ``name`` is the name of this Section, 'TheCrew' in the example case
- ``type`` provides the type of the Section, 'crew' in the example case
- ``id`` provides the uuid of the Section, the actual value has been omitted in the example to improve readability.


Note that the Section printout tells you nothing about the depth of a possible
sub-Section tree below the directly attached ones. It also only lists the type
of the Section as one of the Section attributes. In total, a Section can be
defined by the following attributes:

name
    - Returns the name of this Section. Should indicate what kind of
      information can be found in this Section.

definition
    - Returns the definition of the content within this Section. Should
      describe what kind of information can be found in this Section.

document
    - Returns the Document to which this Section belongs to. Note that this
      attribute is set automatically for a Section and all its children when
      it is attached to a Document.

parent
    - Returns the parent to which this Section was directly attached to. Can be
      either a Document or another Section.

type
    - Returns the classification type which allows to connect related Sections
      due to a superior semantic context.

reference
    - Returns a reference that can be used to state the origin or source file
      of the metadata stored in the Properties that are grouped by this
      Section.

repository
    - Returns the URL (returned as string) to a user defined repository of
      terminologies used in this Document. Could be the URL to the G-Node
      terminologies or to a user defined template.

id
    - id is a UUID (universally unique identifiers) that uniquely identifies
      the current section. If not otherwise specified, this id is automatically
      created and assigned.

Let's have a look at the attributes for the Section 'TheCrew'::

    >>> print(odmlEX['TheCrew'].name)
    TheCrew
    >>> print(odmlEX['TheCrew'].definition)
    Information on the crew
    >>> print(odmlEX['TheCrew'].document)
    Document 42 {author = D. N. Adams, 2 sections}
    >>> print(odmlEX['TheCrew'].parent)
    Document 42 {author = D. N. Adams, 2 sections}
    >>> print(odmlEX['TheCrew'].type)
    crew
    >>> print(odmlEX['TheCrew'].reference)
    None
    >>> print(odmlEX['TheCrew'].repository)
    None
    >>> print(odmlEX['TheCrew'].id)
    6df940b5-b502-4749-8ad9-33d7432064f3

As expected for this Section, the name and type attribute match the information
given in the Section printout, and the document and parent attributes return the
same object, namely our example Document.

To see which Sections are directly attached to the Section 'TheCrew' again use
the following command::

    >>> print(odmlEX['TheCrew'].sections)
    [Section[0|5] {name = Arthur Philip Dent, type = crew/person, id = ...},
     Section[0|5] {name = Zaphod Beeblebrox, type = crew/person, id = ...},
     Section[0|5] {name = Tricia Marie McMillan, type = crew/person, id = ...},
     Section[0|5] {name = Ford Prefect, type = crew/person, id = ...}]

Or, for accessing these sub-Sections::

    >>> print(odmlEX['TheCrew'].sections['Ford Prefect'])
    Section[0|5] {name = Ford Prefect, type = crew/person, id = ...}
    >>> print(odmlEX['TheCrew'].sections[3])
    Section[0|5] {name = Ford Prefect, type = crew/person, id = ...}
    >>> print(odmlEX['TheCrew']['Ford Prefect'])
    Section[0|5] {name = Ford Prefect, type = crew/person, id = ...}
    >>> print(odmlEX['TheCrew'][3])
    Section[0|5] {name = Ford Prefect, type = crew/person, id = ...}

As you learned, besides sub-Sections, a Section can also have Properties
attached. Let's see which Properties are attached to the Section 'TheCrew'::

    >>> print(odmlEX['TheCrew'].properties)
    [Property: {name = NameCrewMembers},
     Property: {name = NoCrewMembers}]

The printout and attributes of a Property are explained in the next chapter.


The Properties
--------------

Properties need to be called explicitly via the properties function of a
Section. You can then either call a Property by name or by index::

    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'])
    Property: {name = NoCrewMembers}
    >>> print(odmlEX['TheCrew'].properties[1])
    Property: {name = NoCrewMembers}

In the following we will only call Properties explicitly by their name.

The Property printout is reduced and only gives you information about the
following:

- ``Property`` tells you that you are looking at an odML Property
- ``{...}`` provides the ``name`` of the Property
- ``NoCrewMembers`` is the name of this Property

Note that the Property printout tells you nothing about the number of Values,
and very little about the Property attributes. In total, a Property can be
defined by the following attributes:

name
    - Returns the name of the Property. Should indicate what kind of metadata
      are stored in this Property.

definition
    - Returns the definition of this Property. Should describe what kind of
      metadata are stored in this Property.

document
    - Returns the Document to which the parent Section of this Property belongs
      to. Note that this attribute is set automatically for a Section and all
      its children when it is attached to a Document.

parent
    - Returns the parent Section to which this Property was attached to.

values
    - Returns the metadata of this Property. Can be either a single metadata or
      multiple, but homogeneous metadata (all with the same dtype, unit and uncertainty).
      For this reason, the output is always provided as a list.

dtype
    - Returns the odml data type of the stored metadata.

unit
    - Returns the unit of the stored metadata.

uncertainty
    - recommended
    - Can be used to specify the uncertainty of the given metadata value.

reference
    - Returns a reference that can be used to state an external definition
      of the metadata value.

dependency
    - optional
    - A name of another Property within the same section, which this property
      depends on.

dependency_value
    - optional
    - Value of the other Property specified in the 'dependency' attribute on
      which this Property depends on.

value_origin
    - A reference to state the origin of the metadata value e.g. a file name.

Let's check which attributes were defined for the Property 'NoCrewMembers'::

    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'].name)
    NoCrewMembers
    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'].definition)
    Number of crew members
    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'].document)
    Document 42 {author = D. N. Adams, 2 sections}
    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'].values)
    [4]
    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'].dtype)
    int
    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'].unit)
    None
    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'].uncertainty)
    1
    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'].reference)
    The Hitchhiker's guide to the Galaxy (novel)
    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'].dependency)
    None
    >>> print(odmlEX['TheCrew'].properties['NoCrewMembers'].dependency_value)
    None

As mentioned the ``values`` attribute of a Property can only contain multiple
metadata when they have the same ``dtype`` and ``unit``, as it is the case for
the Property 'NameCrewMembers'::

    >>> print(odmlEX['TheCrew'].properties['NameCrewMembers'].values)
    ['Arthur Philip Dent',
     'Zaphod Beeblebrox',
     'Tricia Marie McMillan',
     'Ford Prefect']
    >>> print(odmlEX['TheCrew'].properties['NameCrewMembers'].dtype)
    person
    >>> print(odmlEX['TheCrew'].properties['NameCrewMembers'].unit)
    None

NOTE: ``property.values`` will always return a copy! Any direct changes to the
returned list will have no affect on the actual Property values. If you want to
make changes to a Property value, either use the ``append``, ``extend`` and ``remove``
methods or assign a new value list to the property.

Printing overviews to navigate the contents of an odML document
---------------------------------------------------------------

The odML entities ``Property``, ``Section`` and ``Document`` feature
a method that allows to print a tree-like representation of
all child entities to get an overview of the file structure.

    >>> MYodML.pprint()
    >>> sec = MYodML['TheCrew']
    >>> sec.pprint()
    >>> prop = odmlEX['TheCrew'].properties['NameCrewMembers']
    >>> prop.pprint()

-------------------------------------------------------------------------------

Generating an odML-file
=======================

After getting familiar with the different odML objects and their attributes, 
you will now learn how to generate your own odML file by reproducing some parts 
of the example THGTTG.odml.

We will show you first how to create the different odML objects with their 
attributes. Please note that some attributes are obligatory, some are 
recommended and others are optional when creating the corresponding odML 
objects. A few are automatically generated in the process of creating an odML 
file. Furthermore, all attributes of an odML object can be edited at any time.

If you opened a new IPython shell, please import first again the odml package::

    >>> import odml


Create a document
-----------------

Let's start by creating the Document. Note that none of the Document attributes
are obligatory::
 
    >>> MYodML = odml.Document()

You can check if your new Document contains actually what you created by using
some of the commands you learned before::

    >>> MYodML
    >>> Document None {author = None, 0 sections}

As you can see, we created an "empty" Document where the version and the author
attributes are not defined and no section is yet attached. You will learn how to create
and add a Section to a Document in the next chapter. Let's focus here on defining
the Document attributes::

    >>> MYodML.author = 'D. N. Adams'
    >>> MYodML.version = 42

For the date attribute you require a datetime object as entry. For this reason, 
you need to first import the Python package datetime::

    >>> import datetime as dt

Now, let's define the date attribute of the Document::

    >>> MYodML.date = dt.date(1979, 10, 12)

Next, let us also add a repository attribute. Exemplary, we can import the 
Python package ``os`` to extract the absolute path to our previously used example
odML file and add this as repository::

    >>> import os
    >>> url2odmlEX = 'file:///' + os.path.abspath(to_load)
    >>> MYodML.repository = url2odmlEX

The document and parent attribute are automatically set and should not be 
fiddled with.

Check if your new Document actually contains all attributes now::

    >>> print(MYodML.author)
    D. N. Adams
    >>> print(MYodML.date)
    1979-10-12
    >>> print(MYodML.document)
    Document 42 {author = D. N. Adams, 0 sections}
    >>> print(MYodML.parent)
    None
    >>> print(MYodML.repository)
    file:///home/usr/.../python-odml/doc/example_odMLs/THGTTG.odml
    >>> print(MYodML.version)
    42

Note that you can also define all attributes when first creating a Document::

    >>> MYodML = odml.Document(author='D. N. Adams',
                               version=42,
                               date=dt.date(1979, 10, 12),
                               repository=url2odmlEX)

Our newly created Document is, though, still "empty", because it does not contain
Sections yet. Let's change this!


Create a section
----------------

We now create a Section by reproducing the Section "TheCrew" of the example 
odML file from the beginning::

    >>> sec1 = odml.Section(name="TheCrew",
                           definition="Information on the crew",
                           type="crew")

Note that only the attribute name is obligatory. The attributes ``definition`` and
``type`` are recommended, but could be either not defined at all or defined later on.

Let us now attach this Section to our previously generated Document. With this,
the attribute document and parent of our new Section are automatically updated::

    >>> MYodML.append(sec1)

    >>> print(MYodML)
    Document 42 {author = D. N. Adams, 1 sections}
    >>> print(MYodML.sections)
    [Section[0|0] {name = TheCrew, type = crew, id = ...}]

    >>> print(sec1.document)
    Document 42 {author = D. N. Adams, 1 sections}
    >>> print(sec1.parent)
    Document 42 {author = D. N. Adams, 1 sections}

It is also possible to connect a Section directly to a parent object.
Let's try this with the next Section we create::

    >>> sec2 = odml.Section(name="Arthur Philip Dent",
                            definition="Information on Arthur Dent",
                            type="crew/person",
                            parent=sec1)

    >>> print(sec2)
    Section[0|0] {name = Arthur Philip Dent, type = crew/person, id = ...}

    >>> print(sec2.document)
    Document 42 {author = D. N. Adams, 1 sections}
    >>> print(sec2.parent)
    [Section[1|0] {name = TheCrew, type = crew, id = ...}

Note that all of our created Sections do not contain any Properties yet. Let's 
see if we can change this...


Create a Property:
------------------

Let's create our first Property::

    >>> prop1 = odml.Property(name="Gender",
                              definition="Sex of the subject",
                              values="male")

Note that again, only the ``name`` attribute is obligatory for creating a Property.
The remaining attributes can be defined later on, or are automatically 
generated in the process.

If a value is defined, but the ``dtype`` is not, as it is the case for our example
above, the ``dtype`` is deduced automatically::

    >>> print(prop1.dtype)
    string

Generally, you can use the following odML data types to describe the format of 
the stored metadata:

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
| odml.DType.text or 'text'         | 'any text containing \n linebreaks'   |
+-----------------------------------+---------------------------------------+
| odml.DType.url or 'url'           | "https://en.wikipedia.org/wiki/Earth" |
+-----------------------------------+---------------------------------------+
| odml.DType.tuple                  | "(39.12; 67.19)" cf. usage note below |
+-----------------------------------+---------------------------------------+

The available types are implemented in the 'odml.dtypes' Module. Note that the
last four data types, if not defined, cannot be deduced, but are instead
always interpreted as string.

If we append now our new Property to the previously created sub-Section 
'Arthur Philip Dent', the Property will also inherit the document attribute and
automatically update its parent attribute::

    >>> MYodML['TheCrew']['Arthur Philip Dent'].append(prop1)

    >>> print(prop1.document)
    Document 42 {author = D. N. Adams, 1 sections}
    >>> print(prop1.parent)
    Section[0|1] {name = Arthur Philip Dent, type = crew/person, id = ...}

Next, let us create a Property with multiple metadata entries::

    >>> prop2 = odml.Property(name="NameCrewMembers",
                              definition="List of crew members names",
                              values=["Arthur Philip Dent",
                                      "Zaphod Beeblebrox",
                                      "Tricia Marie McMillan",
                                      "Ford Prefect"],
                              dtype=odml.DType.person)

As you learned before, in such a case the metadata entries must be
homogeneous! That means they have to be of the same ``dtype``, ``unit``, and
``uncertainty`` (here ``odml.DType.person``, None, and None, respectively).

To further build up our odML file, let us attach now this new Property to the
previously created Section 'TheCrew'::

    >>> MYodML['TheCrew'].append(prop2)

Note that it is also possible to add a metadata entry later on::

    >>> prop2.append("Blind Passenger")
    >>> print(MYodML['TheCrew'].properties['NameCrewMembers'].values)
    ['Arthur Philip Dent',
     'Zaphod Beeblebrox',
     'Tricia Marie McMillan',
     'Ford Prefect',
     'Blind Passenger']


The ``tuple`` datatype you might have noticed in the dtype table above has to be
specially handled. It is intended to enforce a specific number of data points
for each value entry. This is useful in case of 2D or 3D data, where all
data points always have to be present for each entry.
The dtype itself has to contain the number corresponding to the required value
data points. For the value data points themselves, they have to be enclosed
by brackets and separated by a semicolon.

    >>> pixel_prop = odml.Property(name="pixel map")
    >>> pixel_prop.dtype = "2-tuple"
    >>> pixel_prop.values = ["(1; 2)", "(3; 4)"]

    >>> voxel_prop = odml.Property(name="voxel map")
    >>> voxel_prop.dtype = "3-tuple"
    >>> voxel_prop.values = "(1; 2; 3)"

Please note, that inconsistent tuple values will raise an error:

    >>> tprop = odml.Property(name="tuple fail")
    >>> tprop.dtype = "3-tuple"
    >>> tprop.values = ["(1; 2)"]


Printing the XML-representation of an odML file:
------------------------------------------------

Although the XML-representation of an odML file is a bit hard to read, it is 
sometimes helpful to check, especially during a generation process, how the 
hierarchical structure of the odML file looks like.

Let's have a look at the XML-representation of our small odML file we just 
generated::

    >>> print(odml.tools.xmlparser.XMLWriter(MYodML))
    <odML version="1.1">
      <date>1979-10-12</date>
      <section>
        <definition>Information on the crew</definition>
        <property>
          <definition>List of crew members names</definition>
          <name>NameCrewMembers</name>
          <type>person</type>
          <value>[Arthur Philip Dent,Zaphod Beeblebrox,Tricia Marie McMillan,Ford Prefect,Blind Passenger&#13;]</value>
        </property>
        <name>TheCrew</name>
        <section>
          <definition>Information on Arthur Dent</definition>
          <property>
            <definition>Sex of the subject</definition>
            <name>Gender</name>
            <type>string</type>
            <value>[male&#13;]</value>
          </property>
          <name>Arthur Philip Dent</name>
          <type>crew/person</type>
        </section>
        <type>crew</type>
      </section>
      <version>42</version>
      <repository>file:///home/usr/Projects/toolbox/python-odml/doc/example_odMLs/THGTTG.odml</repository>
      <author>D. N. Adams</author>
    </odML>


Saving an odML file:
--------------------

You can save your odML file using the following command::

    >>> save_to = '/home/usr/toolbox/python-odml/doc/example_odMLs/myodml.odml'
    >>> odml.save(MYodML, save_to)


By default, every odML file will be saved using the ``XML`` file format.
Note, that you can also choose to save an odML Document using the ``JSON``
or the ``YAML`` file format as well, specifying the corresponding option in
the command.

    >>> save_to = '/home/usr/toolbox/python-odml/doc/example_odMLs/myodml.json'
    >>> odml.save(MYodML, save_to, "JSON")
    >>> save_to = '/home/usr/toolbox/python-odml/doc/example_odMLs/myodml.yaml'
    >>> odml.save(MYodML, save_to, "YAML")


Loading an odML file:
---------------------

You already learned how to load the example odML file. Here just as a reminder
you can try to reload your own saved odML file::

    >>> my_reloaded_odml = odml.load(save_to)



Again, the load function by default assumes, that an odML file was saved using the
``XML`` format. If it was saved in either ``JSON`` or ``YAML``, add the appropriate
format option when loading the document:

    >>> my_reloaded_odml_json = odml.load(save_to, "JSON")
    >>> my_reloaded_odml_yaml = odml.load(save_to, "YAML")


-------------------------------------------------------------------------------

Advanced odML-Features
======================

View odML documents in a web browser
------------------------------------

By default all odML files are saved in the XML format without the capability to view
the plain files in a browser. By default you can use the command line tool ``odmlview``
to view saved odML files locally. Since this requires the start of a local server,
there is another option to view odML XML files in a web browser.

You can use an additional feature of the ``odml.tools.XMLWriter`` to save an odML
document with an embedded default stylesheet for local viewing:

    >>> import odml
    >>> from odml.tools import XMLWriter
    >>> doc = odml.Document() # minimal example document
    >>> filename = "viewable_document.xml"
    >>> XMLWriter(doc).write_file(filename, local_style=True)

Now you can open the resulting file 'viewable_document.xml' in any current web-browser
and it will render the content of the odML file.

If you want to use a custom style sheet to render an odML document instead of the default
one, you can provide it as a string to the XML writer. Please note, that it cannot be a
full XSL stylesheet, the outermost tag of the XSL code has to be
``<xsl:template match="odML"> [your custom style here] </xsl:template>``:

    >>> import odml
    >>> from odml.tools import XMLWriter
    >>> doc = odml.Document() # minimal example document
    >>> filename = "viewable_document.xml"
    >>> own_template = """<xsl:template match="odML"> [your custom style here] </xsl:template>"""
    >>> XMLWriter(doc).write_file(filename, custom_template=own_template)

Please note that if the file is saved using the '.odml' extension and you are using
Chrome, you will need to map the '.odml' extension to the browsers Mime-type database as
'application/xml'.

Also note that any style that is saved with an odML document will be lost, when this
document is loaded again and changes to the content are added. In this case the required
style needs to be specified again when saving the changed file as described above.


Defining and working with feature cardinality
---------------------------------------------

The odML format allows users to define a cardinality for
the number of subsections and properties of Sections and
the number of values a Property might have.

A cardinality is checked when it is set, when its target is
set and when a document is saved or loaded. If a specific
cardinality is violated, a corresponding warning will be printed.

Setting a cardinality
*********************

A cardinality can be set for sections or properties of sections
or for values of properties. By default every cardinality is None,
but it can be set to a defined minimal and/or a maximal number of
an element.

A cardinality is set via its convenience method:

    >>> # Set the cardinality of the properties of a Section 'sec' to
    >>> # a maximum of 5 elements.
    >>> sec = odml.Section(name="cardinality", type="test")
    >>> sec.set_properties_cardinality(max_val=5)

    >>> # Set the cardinality of the subsections of Section 'sec' to
    >>> # a minimum of one and a maximum of 2 elements.
    >>> sec.set_sections_cardinality(min_val=1, max_val=2)

    >>> # Set the cardinality of the values of a Property 'prop' to
    >>> # a minimum of 1 element.
    >>> prop = odml.Property(name="cardinality")
    >>> prop.set_values_cardinality(min_val=1)

    >>> # Re-set the cardinality of the values of a Property 'prop' to not set.
    >>> prop.set_values_cardinality()
    >>> # or
    >>> prop.val_cardinality = None


Advanced knowledge on Values
----------------------------

Data type conversions
*********************

After creating a Property with metadata, the data type can be changed and the
format of the corresponding entry will be converted to the new data type, if the
new type is valid for the given metadata::

    >>> test_dtype_conv = odml.Property('p', values=1.0)
    >>> print(test_dtype_conv.values)
    [1.0]
    >>> print(test_dtype_conv.dtype)
    float
    >>> test_dtype_conv.dtype = odml.DType.int
    >>> print(test_dtype_conv.values)
    [1]
    >>> print(test_dtype_conv.dtype)
    int

If the conversion is invalid, a ``ValueError`` is raised.

Also note, that during such a process metadata loss may occur, if a float is
converted to integer and then back to float::

    >>> test_dtype_conv = odml.Property('p', values=42.42)
    >>> print(test_dtype_conv.values)
    [42.42]
    >>> test_dtype_conv.dtype = odml.DType.int
    >>> test_dtype_conv.dtype = odml.DType.float
    >>> print(test_dtype_conv.values)
    [42.0]


Links & Includes
****************
Please note, that this section is outdated but still valid.

Sections can be linked to other Sections, so that they include their defined
attributes. A link can be within the document (``link`` property) or to an
external one (``include`` property).

After parsing a document, these links are not yet resolved, but can be using
the ``odml.doc.BaseDocument.finalize`` method::

    >>> d = xmlparser.load("sample.odml")
    >>> d.finalize()

Note: Only the parser does not automatically resolve link properties, as the referenced
sections may not yet be available.
However, when manually setting the ``link`` (or ``include``) attribute, it will
be immediately resolved. To avoid this behaviour, set the ``_link`` (or ``_include``)
attribute instead.
The object remembers to which one it is linked in its ``_merged`` attribute.
The link can be unresolved manually using ``odml.section.BaseSection.unmerge``
and merged again using ``odml.section.BaseSection.merge``.

Unresolving means to remove sections and properties that do not differ from their
linked equivalents. This should be done globally before saving using the
``odml.doc.BaseDocument.clean`` method::

    >>> d.clean()
    >>> xmlparser.XMLWriter(d).write_file('sample.odml')

Changing a ``link`` (or ``include``) attribute will first unmerge the section and
then set merge with the new object.

Terminologies
*************
Please note, that this section is outdated but still valid.

odML supports terminologies that are data structure templates for typical use cases.
Sections can have a ``repository`` attribute. As repositories can be inherited,
the current applicable one can be obtained using the
``odml.section.BaseSection.get_repository`` method.

To see whether an object has a terminology equivalent, use the
``odml.property.BaseProperty.get_terminology_equivalent``
method, which returns the corresponding object of the terminology.
