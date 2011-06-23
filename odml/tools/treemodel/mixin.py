"""
This module extends the odML base class by adding tree-functionality for
gtk.GenericTreeModels using MixIns

to use it just import this module::

    >>> import odml.tools.treemodel.mixin

Alternatively you can import the modified Value/Property/Section/Document
classes manually::

    >>> import odml.tools.treemodel.nodes as odml
    >>> s = odml.Section("sample section")

"""
#Please note: tree-functionality is already based on event-functionality.
#Therefore mixin in odml.tools.events will be troublesome / not work.

import nodes
from ... import doc, section, property, value

doc.Document      = nodes.Document
section.Section   = nodes.Section
property.Property = nodes.Property
value.Value       = nodes.Value
