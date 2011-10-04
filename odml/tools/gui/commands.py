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
    ChangeValue(object=, attr=, new_value=)

    params: *object* object, *attr* (an attribute of the object), *new_value* text

    if *attr* is a list, only the first attribute is changed, but all other attributes
    are stored for the undo mechanism
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
        if not isinstance(self.attr, list):
            self.attr = [self.attr]

        self.old_value = {}
        for attr in self.attr:
            self.old_value[attr] = getattr(self.object, attr)

        setattr(self.object, self.attr[0], self.new_value)

    def _undo(self):
        if not hasattr(self, "old_value"):
            # execute failed
            return

        for attr in self.attr:
            setattr(self.object, attr, self.old_value[attr])

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

class DeleteObject(Command):
    """
    DeleteObject(obj=)

    removes *obj* from its parent
    """
    def __init__(self, *args, **kwargs):
        super(DeleteObject, self).__init__(*args, **kwargs)
        # use an AppendCommand for the actual operation
        # but use it reversed
        self.append_cmd = AppendValue(obj=self.obj.parent, val=self.obj)
        self.append_cmd.index = self.obj.position

    def _execute(self):
        """remove obj (append_cmd.val) from its parent"""
        self.append_cmd._undo()

    def _undo(self):
        """append obj (append_cmd.val) to its original parent (append_cmd.obj)"""
        self.append_cmd._execute()

class ReorderObject(Command):
    """
    ReorderObject(obj=, new_index=)

    calls obj.reorder(new_index) to move obj to new position *new_index* in its
    parent list
    """
    def _execute(self):
        self.old_index = self.obj.reorder(self.new_index)

    def _undo(self):
        self.obj.reorder(self.old_index)

class CopyObject(Command):
    """
    CopyObject(obj=, dst=)

    appends a clone of *obj* to *dst*
    """
    def get_new_object(self):
        return self.obj.clone()

    def _execute(self):
        """clone the obj and append it to dst"""
        self.new_obj = self.get_new_object()
        self.dst.append(self.new_obj)

    def _undo(self):
        """
        remove the clone from its parent
        """
        parent = self.new_obj.parent
        if parent is not None:
            parent.remove(self.new_obj)

class MoveObject(CopyObject):
    """
    MoveObject(obj=, dst=)

    removes *obj* from *obj.parent* and appends it to *dst*
    """
    def get_new_object(self):
        try:
            self.index = self.obj.position
        except:
            self.index = self.obj.parent.index(self.obj)
        self.parent = self.obj.parent
        self.parent.remove(self.obj)
        return self.obj

    # _execute is inherited from CopyObject

    def _undo(self):
        """
        move the object back to its original parent
        and try to insert it at its old position
        """
        super(MoveObject, self)._undo()
        try:
            self.parent.insert(self.index, self.obj)
        except:
            self.parent.append(self.obj)

class ReplaceObject(MoveObject):
    """
    ReplaceObject(obj=, repl=)

    removes *obj* from *obj.parent* and appends *repl* to its *obj.parent*
    however, does not previously remove *repl* from its parent!
    so only use this with repl=obj.clone()
    """
    def _execute(self):
        self.new_obj = self.get_new_object()
        self.obj = self.repl
        self.repl = self.new_obj
        super(ReplaceObject, self)._undo() # insert self.obj (=repl) into self.parent (=obj.parent)

    def _undo(self):
        self._execute() # exchange the objects again and execute in reverse

class CopyOrMoveObject(Command):
    """
    CopyOrMoveObject(obj=, dst=, copy=True/False)                            tv=TreeView,)
    """
    def __init__(self, *args, **kwargs):
        super(CopyOrMoveObject, self).__init__(*args, **kwargs)
        cmd_class = CopyObject if self.copy else MoveObject
        self.cmd = cmd_class(obj=self.obj, dst=self.dst)

    def _execute(self):
        self.cmd()

    def _undo(self):
        self.cmd.undo()
