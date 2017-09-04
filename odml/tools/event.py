import sys
import odml


class Event (object):
    def __init__(self, name):
        self.handlers = []
        self.name = name

    def add_handler(self, handler):
        try:
            if handler not in self.handlers:
                self.handlers.append(handler)
        except:
            print("cannot add handler.")
        return self

    def remove_handler(self, handler):
        if handler in self.handlers:
            self.handlers.remove(handler)
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)
        self.finish(*args, **kargs)

    def finish(self, *args, **kargs):
        """
        a final handler for this event
        (typically passing the event on to higher layers)
        """
        pass

    def __len__(self):
        return len(self.handlers)

    def __repr__(self):
        return "<%sEvent>" % self.name

    __iadd__ = add_handler
    __isub__ = remove_handler
    __call__ = fire


class ChangeContext(object):
    """
    A ChangeContext holds information about a change event

    the context object stays the same within preChange and postChange
    events, thus you can store information in a preChange event and use
    it later in the postChange event where the information might not be
    available any more.

    Attributes:

    * action: the action that caused the event
    * obj: the object upon which the action is executed
    * val: a value assotiated with a action
    * preChange: True if the change has not yet occurred
    * postChange: True if the change has already occured

    Actions defined so far:

    * "set": val = (attribute_name, new_value)
    * "insert", "append": val = object to be inserted
    * "remove": val = object to be remove

    Events may be passed on in the hierarchy, thus the context also
    holds state for this. *cur* holds the current node receiving the
    event and is a direct or indirect parent of obj.

    The hidden attribute *_obj* holds the complete pass stack, where
    obj is obj[0] and cur is _obj[-1]
    """
    def __init__(self, val):
        self._obj = []
        self.val = val
        self.action = None
        self.when = None

    @property
    def preChange(self):
        return self.when is True

    @preChange.setter
    def preChange(self, val):
        self.when = True if val else None

    @property
    def postChange(self):
        return self.when is False

    @postChange.setter
    def postChange(self, val):
        self.when = False if val else None

    @property
    def obj(self):
        return self._obj[0]

    def getStack(self, count):
        """
        helper function used to obtain a event-pass-stack for a certain hierarchy

        i.e. for a property-change event caught at the parent section, _obj will be
        [property, section] with getStack you can now obtain:

        >>> value, property, section = getStack(3)

        without checking the depth of the level, this will also hold true for longer stacks
        such as [val, prop, sec, doc] and will still work as expected
        """
        if len(self._obj) < count:
            return ([None] * count + self._obj)[-count:]
        return self._obj[:count]

    @property
    def cur(self):
        return self._obj[-1]

    def passOn(self, obj):
        """
        pass the event to obj

        appends obj to the event-pass-stack and calls obj._Changed
        after handling obj is removed from the stack again
        """
        self._obj.append(obj)
        if obj._change_handler is not None: #hasattr(obj, "_change_handler"):
            obj._change_handler(self)
        obj._Changed(self)
        self._obj.remove(obj)

    def reset(self):
        self._obj = []

    def __repr__(self):
        v = ""
        if self.preChange: v = "Pre"
        if self.postChange: v = "Post"
        return "<%sChange %s.%s(%s)>" % (v, repr(self.obj), self.action, repr(self.val))

    def dump(self):
        return repr(self) + "\nObject stack:\n\t" + "\n\t".join(map(repr, self._obj))


class ChangedEvent(object):
    def __init__(self):
        pass


class EventHandler(object):
    def __init__(self, func):
        self._func = func

    def __call__(self, *args, **kargs):
        return self._func(*args, **kargs)


class ChangeHandlable(object):
    """
    For objects that support the add_change_handler
    and remove_change_handler functions.
    """
    _change_handler = None

    def add_change_handler(self, func):
        if self._change_handler is None:
            self._change_handler = Event(self.__class__.__name__)
        self._change_handler += func

    def remove_change_handler(self, func):
        if self._change_handler is not None:
            self._change_handler -= func
        if len(self._change_handler) == 0:
            del self._change_handler


class ModificationNotifier(ChangeHandlable):
    """
    Override some methods, to get notification on their calls
    """
    def __setattr__(self, name, value):
        fire = not name.startswith('_') and hasattr(self, name)
        func = lambda: super(ModificationNotifier, self).__setattr__(name, value)
        if fire:
            self.__fireChange("set", (name, value), func)
        else:
            func()

    def __fireChange(self, action, obj, func):
        """
        create a ChangeContext and

        * fire a preChange-event
        * call func
        * fire a postChange-event
        """
        c = ChangeContext(obj)
        c.action = action
        c.preChange = True
        c.passOn(self)
        res = func()
        c.reset()
        c.postChange = True
        c.passOn(self)
        return res

    def append(self, obj, *args, **kwargs):
        func = lambda: super(ModificationNotifier, self).append(obj, *args, **kwargs)
        self.__fireChange("append", obj, func)

    def remove(self, obj):
        func = lambda: super(ModificationNotifier, self).remove(obj)
        self.__fireChange("remove", obj, func)

    def insert(self, position, obj):
        func = lambda: super(ModificationNotifier, self).insert(position, obj)
        self.__fireChange("insert", obj, func)

    def _reorder(self, childlist, new_index):
        func = lambda: super(ModificationNotifier, self)._reorder(childlist, new_index)
        return self.__fireChange("reorder", (childlist, new_index), func)

# create a seperate global Event listeners for each class
# and provide ModificationNotifier Capabilities
name = "event"
provides = odml.getImplementation().provides + ["event"]

class Property(ModificationNotifier, odml.getImplementation().Property):
    _Changed = Event("prop")


class Section(ModificationNotifier, odml.getImplementation().Section):
    _Changed = Event("sec")


class Document(ModificationNotifier, odml.getImplementation().Document):
    _Changed = Event("doc")


def pass_on_change(context):
    """
    pass the change event to the parent node
    """
    parent = context.cur.parent
    if parent is not None:
        context.passOn(parent)


def pass_on_change_section(context):
    """
    pass the change event directly to the document in question
    don't go through all parents
    """
    document = context.cur.document
    if document is not None:
        context.passOn(document)

Property._Changed.finish = pass_on_change
Section._Changed.finish  = pass_on_change_section

odml.addImplementation(sys.modules[__name__])
