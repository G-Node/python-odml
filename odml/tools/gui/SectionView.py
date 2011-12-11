import gtk
import commands
import odml
from TreeView import TerminologyPopupTreeView
from DragProvider import DragProvider

from dnd.targets import ValueDrop, PropertyDrop, SectionDrop
from dnd.odmldrop import OdmlDrag, OdmlDrop
from dnd.text import TextDrag, TextDrop, TextGenericDropForSectionTV

class SectionView(TerminologyPopupTreeView):
    """
    A key-value ListStore based TreeView

    showing properties and allows to edit them
    based on the format-description of the obj's class
    """
    def __init__(self, registry):
        super(SectionView, self).__init__()
        self.add_column(name="Name", edit_func=self.on_edited)
        self._treeview.show()

        # set up our drag provider
        dp = DragProvider(self._treeview)
        _exec = lambda cmd: self.execute(cmd)
        pd = PropertyDrop(exec_func=_exec)
        sd = SectionDrop(exec_func=_exec)
        for target in [
            OdmlDrag(mime="odml/section-ref", inst=odml.section.Section),
            TextDrag(mime="odml/section", inst=odml.section.Section),
            TextDrag(mime="TEXT"),
            OdmlDrop(mime="odml/property-ref", target=pd, registry=registry, exec_func=_exec),
            OdmlDrop(mime="odml/section-ref", target=sd, registry=registry, exec_func=_exec),
            TextDrop(mime="odml/property", target=pd),
            TextDrop(mime="odml/section", target=sd),
            TextGenericDropForSectionTV(exec_func=_exec),
            ]:
            dp.append(target)
        dp.execute = _exec

    def set_model(self, model):
        self._treeview.set_model(model)

    def on_object_edit(self, tree_iter, attr, new_value):
        section = tree_iter._obj
        cmd = commands.ChangeValue(
            object    = section,
            attr      = "name",
            new_value = new_value)

        self.execute(cmd)

    def get_popup_menu_items(self):
        model, path, obj = self.popup_data
        original_object = obj
        if obj is None:
            obj = model.document
        menu_items = self.create_popup_menu_items("odml-add-Section", "Empty Section", obj, self.add_section, lambda sec: sec.sections, lambda sec: "%s [%s]" % (sec.name, sec.type), stock=True)
        if original_object is not None:
            menu_items.append(self.create_popup_menu_del_item(original_object))
            if original_object.is_merged:
                menu_items.append(self.create_menu_item("Unresolve links (collapse)", self.on_expand, original_object))
            elif original_object.can_be_merged:
                menu_items.append(self.create_menu_item("Resolve links (expand)", self.on_expand, original_object))
        return menu_items

    def on_expand(self, widget, obj):
        """
        called when the user requests an object to be expanded/collapsed
        """
        if obj.is_merged:
            obj.clean()
        else:
            obj.merge()

    def add_section(self, widget, (obj, section)):
        """
        popup menu action: add section

        add a section to the selected section (or document if None selected)
        """
        if section is None:
            section = odml.Section(name="unnamed section")
        else:
            section = section.clone()
        cmd = commands.AppendValue(obj=obj, val=section)

        self.execute(cmd)

    def on_selection_change(self, tree_selection):
        """
        the selection moved

        now callback another method with more meaningful information
        """
        (model, tree_iter) = tree_selection.get_selected()
        if not tree_iter:
            return

        return self.on_section_change(model.get_object(tree_iter))

    def on_section_change(self, section):
        """
        the user selected a new section
        """
        pass

    def on_get_tooltip(self, model, path, iter, tooltip):
        """
        set the tooltip text, if the gui queries for it
        """
        obj = model.get_object(iter)
        tooltip.set_text("%s [%s]" % (obj.name, obj.type))
