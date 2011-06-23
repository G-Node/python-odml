class Command(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __call__(self):
        self._execute()
        self.on_action()

    def _execute(self):
        pass

    def on_action(self, undo=False):
        pass

    def undo(self):
        self._undo()
        self.on_action(undo=True)

    def _undo(self):
        pass

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, ', '.join(["%s=%s" % (k,v) for k,v in self.__dict__.iteritems()]))

class Multiple(Command):
    """
    Multiple(cmds=[])

    aggregator for multiple command, args: cmds=[]
    """
    def _execute(self):
        for cmd in self.cmds:
            cmd()

    def _undo(self):
        for cmd in self.cmds:
            cmd.undo()

class ChangeValue(Command):
    """
    ChangeValue(value=, prop=, new_value=)

    params: *value* object, *prop* (a property of the value), *new_value* text
    """
    # TODO known bug: if the data type of a Value is edited, other properties
    # are affected as well (i.e. the value) which is not undone in undo
    # fix1:
    #   use the format description and save all attributes
    # fix2:
    #   clone the object and restore it later (needs treemanipulation or stuff from fix1)
    # hack:
    #   save the value as well for Value objects
    def _execute(self):
        self.old_value = getattr(self.value, self.prop)
        setattr(self.value, self.prop, self.new_value)

    def _undo(self):
        if not hasattr(self, "old_value"):
            # execute failed
            return
        setattr(self.value, self.prop, self.old_value)

class AppendValue(Command):
    """
    AppendValue(obj=, val=)

    appends value *val* to object *obj*
    """
    def _execute(self):
        self.index = len(self.obj)
        self.obj.append(self.val)

    def _undo(self):
        """try to remove the object again"""
        try:
            if self.obj[self.index] == self.val:
                del self.obj[self.index]
                return
        except:
            pass

        if hasattr(self.obj, "pop"):
            val = self.obj.pop()
            if val == self.val: return
            self.obj.append(val)
        self.obj.remove(self.val)
