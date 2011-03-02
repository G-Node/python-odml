========
Tutorial
========

Getting Started
===============

Installation
------------

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
needs a value. If the supplied value is not a :ref:`odml.value.Value` it will be converted to one::

    >>> p = Property(name="quality", value=144)
    >>> p
    <Property quality>
    >>> p.value
    <144>
    >>> s.append(p)

As you can see, to append an element to another node always uses the ``append`` function.
A property can also contain multiple values::

    >>> p.append(135)
    >>> p.value
    [<144>, <135>]

Note: If a Property has multiple values, ``p.value`` returns a list.
If the Property has only one, ``p.value`` will directly return this value.
In constrast ``p.values`` will always return the list of values, even if it’s only one.

Values
------
Values are typed data. If no dtype is set, the dtype is ``string``::

    >>> Value(144).data
    u'144'
    >>> Value(144, dtype='int').data
    144

The Value’s attribute ``data`` always holds the representation in the corresponding datatype,
whereas the ``value`` attribute contains the serialized data as a ``string``.

Working with files
==================
Currently, odML-Files can be read from and written to XML-files.
This is provided by the :ref:`odml.tools.xmlparser` module::

    >>> from odml.tools.xmlparser import parseXML, XMLWriter

Note: this API is still subject to change.

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

You can read files using the parseXML-function, which works on a file-object::

    >>> document = parseXML(open('example.odml'))
    <Doc 1.0 by None (1 sections)>

Note: the XML-parser will enforce propper structure.
