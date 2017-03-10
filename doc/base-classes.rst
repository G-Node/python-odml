.. _class-reference:

odML-Base Classes
=================

These classes are the core data-structures of odML.
To sum things up, an odML-Document consists of several Sections.
Each Section may contain other Sections and Properties.
Again each Property can have multiple Values.

The odml Module contains wrappers, that are shortcuts for creating the main objects::

    >>> from odml import Document, Section, Property, Value
    >>> Document(version=0.9, author="Kermit")
    <Doc 0.9 by Kermit (0 sections)>

Several modules exist to extend the implementation.
The ones included in the library are those:

* :py:mod:`odml.tools.event` provides event capabilities, allowing to add change-listeners to objects
* :py:mod:`odml.tools.nodes` provides a tree-interface used by the gui with functions like next() and position()

Document
--------
.. autoclass:: odml.doc.BaseDocument
   :members:
   :inherited-members:
   :undoc-members:

Section
-------
.. autoclass:: odml.section.BaseSection
   :members:
   :inherited-members:
   :undoc-members:

Property
--------
.. autoclass:: odml.property.BaseProperty
   :members:
   :inherited-members:
   :undoc-members:

Value
-----
.. autoclass:: odml.value.BaseValue
   :members:
   :inherited-members:
   :undoc-members:

