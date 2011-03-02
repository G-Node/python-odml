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

Document
--------
.. autoclass:: odml.doc.Document
   :members:
   :inherited-members:
   :undoc-members:

Section
-------
.. autoclass:: odml.section.Section
   :members:
   :inherited-members:
   :undoc-members:

Property
--------
.. autoclass:: odml.property.Property
   :members:
   :inherited-members:
   :undoc-members:

Value
-----
.. autoclass:: odml.value.Value
   :members:
   :inherited-members:
   :undoc-members:

