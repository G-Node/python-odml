import gtk
import odml
from ... import format
import commands
from TreeView import TreeView
from odml.tools.treemodel import SectionModel

COL_KEY = 0
COL_VALUE = 1
class ValueView(TreeView):
    """
    The Main treeview for editing properties and their value-attributes
    """
    def __init__(self, execute_func=lambda x: x()):
        self.execute = execute_func

        super(ValueView, self).__init__()
        tv = self._treeview

        for name, (id, propname) in SectionModel.ColMapper.sort_iteritems():
            column = self.add_column(
                name=name,
                edit_func=self.on_prop_edited,
                id=id, data=propname)
            if name == "Value":
                tv.set_expander_column(column)

        tv.set_headers_visible(True)
        tv.set_rules_hint(True)
        tv.show()

    @property
    def section(self):
        return self._section

    @section.setter
    def section(self, section):
        self._section = section
        self.model = SectionModel.SectionModel(section)

    @property
    def model(self):
        return self._treeview.get_model()

    @model.setter
    def model(self, new_value):
        self._treeview.set_model(new_value)

    def on_selection_change(self, tree_selection):
        (model, tree_iter) = tree_selection.get_selected()
        if not tree_iter:
            return

        path = model.get_path(tree_iter)
        print path
        if path:
            self.on_property_select(self.model.section.from_path(path))

    def on_property_select(self, prop):
        """called when a different property is selected"""
        pass

    def on_edited(self, foo):
        pass

    def on_prop_edited(self, cell, path_string, new_text, column_name):
        """
        called upon an edit event of the list view

        updates the underlying model property that corresponds to the edited cell
        """
        print "n: %s -> %s %s %s" % (path_string, new_text, cell, column_name)
        section = self.section
        path    = tuple(int(s) for s in path_string.split(':'))

        prop = section._props[path[0]]

        # are we editing the first_row of a <multi> value?
        first_row_of_multi = len(path) == 1 and len(prop.values) > 1
        print "multi", first_row_of_multi

        # can only edit the subvalues, but not <multi> itself
        if first_row_of_multi and column_name == "value":
            return

        self.edited = True # don't be too strict about real modification
                           # could also wait for real change events of our
                           # data structures in the future
        cmd = None
        # if we edit another attribute (e.g. unit), set this for all values of this property

        if first_row_of_multi and column_name != "name":
            cmds = []
            for value in prop.values:
                cmds.append(commands.ChangeValue(
                    value     = value,
                    prop      = column_name,
                    new_value = new_text))

            cmd = commands.Multiple(cmds=cmds)

        elif len(path) > 1: # we edit a sub-value
            # but do not allow to modify the name of the property there
            if column_name == "name":
                return
            value = prop.values[path[1]]
            cmd = commands.ChangeValue(
                    value     = value,
                    prop      = column_name,
                    new_value = new_text)

        else:
            # otherwise we edit a simple property, name maps to the property
            # everything else to the value
            if column_name == "name":
                cmd = commands.ChangeValue(
                    value     = prop,
                    prop      = "name",
                    new_value = new_text)
            else:
                value = prop.values[0]
                cmd = commands.ChangeValue(
                    value     = value,
                    prop      = column_name,
                    new_value = new_text)

        if cmd:
            self.execute(cmd)

    def add_value(self, action):
        """
        popup menu action: add value

        add a value to the selected property
        """
        # TODO this can be reached also if no property is selected
        #      the context-menu item should be disabled in this case?
        model, path = self.popup_data
        obj = self._document.from_path(path)
        val = odml.Value("")

        cmd = commands.AppendValue(obj=obj, val=val, model=self.model, odml_path=path)

        def cmd_action(undo=False):
            model = self.model
            if model.section != cmd.model.section: return

            if not undo:
                # notify the current property row, that it might have got a new child
                path = model.odml_path_to_model_path(cmd.odml_path)
                model.row_has_child_toggled(path, model.get_iter(path))
                cmd.prop_path = path

                # notify the model about the newly inserted row
                path = model.odml_path_to_model_path(val.to_path())
                model.row_inserted(path, model.get_iter(path))
                cmd.val_path = path
            else:
                model.row_has_child_toggled(cmd.prop_path, model.get_iter(cmd.prop_path))
                model.row_deleted(cmd.val_path)

        cmd.on_action = cmd_action
        self.execute(cmd)


    def add_property(self, action):
        """
        popup menu action: add property

        add a property to the active section
        """
        model, path = self.popup_data
        prop = odml.Property(name="unnamed property", value="")
        cmd = commands.AppendValue(
                obj = model.section,
                val = prop,
                model = self.model)

        def cmd_action(undo=False): #TODO
            # notify the model about the newly inserted row (unless the model changed anyways)
            model = self.model
            if model.section != cmd.model.section: return

            if undo:
                model.row_deleted(cmd.path)
            else:
                cmd.path = model.odml_path_to_model_path(prop.to_path())
                model.row_inserted(cmd.path, model.get_iter(cmd.path))

        cmd.on_action = cmd_action
        self.execute(cmd)
