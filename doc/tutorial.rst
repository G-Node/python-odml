========
Tutorial
========

Getting Started
===============

Installation
------------

Should be easy using::

    $ python setup.py install

You should be able to just test the library using the following::

    $ export PYTHONPATH=.
    $ python
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import odml

See `github:python-odml#Installation <https://github.com/G-Node/python-odml#installation>`_
for more descriptions including setup on Windows and Debian/Ubuntu.

Running python-odml
-------------------
Once python-odml is installed, you can use it in your python shell::

    >>> import odml
    >>> odml.Document(version=0.9, author="Kermit")
    <Doc 0.9 by Kermit (0 sections)>

Creating and manipulating data
==============================
The objects allow to play around freely. You can just edit the properties.
Most directly map to their odML-Names. Few are mapped to other names (e.g.
the ``type`` property of an odML-Value is mapped to ``dtype``).
See the description of the classes in the Reference for the :ref:`class-reference`
if you don't find the property you’re looking for.

Document & Sections
-------------------

To add a sections to a document::

    >>> from odml import *
    >>> d = Document()
    >>> s = Section(name="section1")
    >>> d.append(s)
    
Properties
----------

Now we have a section and can create a property. Keep in mind that a property always
needs a value. If the supplied value is not a :py:mod:`odml.value.Value` it will be converted to one::

    >>> p = Property(name="quality", value=144)
    >>> p
    <Property quality>
    >>> p.value
    <144>
    >>> s.append(p)

As you can see, the ``append`` function is always used to append an element to another node.
A property can also contain multiple values::

    >>> p.append(135)
    >>> p.value
    [<144>, <135>]

Note: If a Property has multiple values, ``p.value`` returns a list.
If the Property has only one, ``p.value`` will directly return this value.
In contrast ``p.values`` will always return the list of values, even if it’s only one.

Values
------
Values are typed data. If no ``dtype`` is set, the ``dtype`` is ``string``::

    >>> Value(144).data
    u'144'
    >>> Value(144, dtype='int').data
    144

The Value’s attribute ``data`` always holds the representation in the corresponding datatype,
whereas the ``value`` attribute contains the serialized data as a ``string``.

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
    <odML version="1.0">
      <section name="section1">
        <property>
          <name>quality</name>
          <value>144</value>
          <value>135</value>
        </property>
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
