import gtk

import odmldrop
import tree
from targets import *

import odml
import odml.tools.xmlparser as xmlparser

class TextDrop(odmldrop.OdmlTreeDropTarget):
    """
    Target-Specific Drop-Capability for xml-text containing odml-objects
    """
    actions = gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE
    app = gtk.TARGET_OTHER_APP

    def odml_tree_can_drop(self, action, dst, position, data=None):
        if data is not None:
            try:
                data = xmlparser.XMLReader().fromString(data)
            except xmlparser.ParserException:
                return False
        return self.text_can_drop(action, dst, position, data)

    def text_can_drop(self, action, dst, position, data):
        return self.odml_can_drop(action, dst, position, data)

    def odml_tree_receive_data(self, action, dst, position, data):
        if data is None:
            return
        obj = xmlparser.XMLReader().fromString(data)
        if action.move:
            action = tree.Action(gtk.gdk.ACTION_COPY)
            # TODO issue MOVE signal
        return self.text_receive_data(action, dst, position, obj)

    def text_receive_data(self, action, dst, position, obj):
        return self.drop_object(action, dst, position, obj)

class TextGenericDrop(TextDrop, SectionDrop, PropertyDrop, ValueDrop):
    """
    Can drop objects if they parse to an class contained in self.targets
    """
    mime = "TEXT"
    preview_required = True

    def drop_object(self, action, dst, position, obj):
        for kls, tkls in [
            (odml.value.Value, ValueDrop),
            (odml.property.Property, PropertyDrop),
            (odml.section.Section, SectionDrop)
            ]:
            if not kls in self.targets:
                continue
            if isinstance(obj, kls):
                return tkls.drop_object(self, action, dst, position, obj)
        raise DNDException("Cannot drop %s" % repr(dst))

    def text_can_drop(self, action, dst, position, obj):
        for kls in self.targets:
            if isinstance(obj, kls): return True
        return False

class TextGenericDropForPropertyTV(TextGenericDrop):
    """
    can drop Properties and Values, but only Values into Properties
    and Properties into Sections
    """
    targets = [odml.property.Property, odml.value.Value]
    def text_can_drop(self, action, dst, position, obj):
        if not super(TextGenericDropForPropertyTV, self).text_can_drop(action, dst, position, obj):
            return False
        # can't drop values to anything but properties
        if isinstance(obj, odml.value.Value) and not isinstance(dst, odml.property.Property):
            return False
        # can't drop properties to anything but sections
        if isinstance(obj, odml.property.Property) and not isinstance(dst, odml.section.Section):
            return False
        return True

class TextGenericDropForSectionTV(TextGenericDropForPropertyTV):
    """
    can drop Properties and Section, inherited is the capability to only drop
    Properties into Sections (not into Documents)
    """
    targets = [odml.property.Property, odml.section.Section]

class TextDrag(odmldrop.OdmlDrag):
    """
    Drag the object as its xml-representation and handle delete-data requests
    using the DeleteObject-command
    """
    def odml_get_data(self, action, obj):
        return unicode(xmlparser.XMLWriter(obj))

    def odml_delete_data(self, obj):
        return commands.DeleteObject(obj=obj)
