"""
This module extends the odML base class by adding tree-functionality for
gtk.GenericTreeModels using MixIns

to use it just import this module::

    >>> import odml.gui.treemodel.mixin

Alternatively you can import the modified Value/Property/Section/Document
classes manually::

    >>> import odml.tools.nodes as odml
    >>> s = odml.Section("sample section")

Or get the implementation once it is registered::

    >>> import odml
    >>> import odml.tools.nodes
    >>> odml.getImplementation('nodes').Section("sample section")

"""
#Please note: tree-functionality is already based on event-functionality.
#Therefore mixin in odml.tools.events will be troublesome / not work.

import odml
import odml.tools.nodes
odml.setMinimumImplementation('nodes')

