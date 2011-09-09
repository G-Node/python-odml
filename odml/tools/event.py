from .. import doc, section, value
from .. import property as prop

class Event (object):
    def __init__(self, name):
        self.handlers = set()
        self.name = name

    def add_handler(self, handler):
        self.handlers.add(handler)
        return self

    def remove_handler(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("No such handler.")
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

    @property
    def n_handler(self):
        return len(self.handlers)

    def __repr__(self):
        return "<%sEvent>" % (self.name)

    __iadd__ = add_handler
    __isub__ = remove_handler
    __call__ = fire
    __len__  = n_handler

class ChangeContext(object):
    def __init__(self, obj, val):
        self._obj = [obj]
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
        return ([None * count] + self._obj)[-count:]

    @property
    def cur(self):
        return self._obj[-1]

    def passOn(self, obj):
        self._obj.append(obj)
        obj._Changed(self)
        self._obj.remove(obj)

    def reset(self):
        self._obj = [self.obj]

    def __repr__(self):
        v = ""
        if self.preChange: v = "Pre"
        if self.postChange: v = "Post"
        return "<%sChange %s.%s(%s)>" % (v, repr(self.obj), self.action, repr(self.val))

class ChangedEvent(object):
    def __init__(self):
        pass

class EventHandler(object):
    def __init__(self, func):
        self._func = func

    def __call__(self, *args, **kargs):
        return self._func(*args, **kargs)

class ModificationNotifier(object):
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
        c = ChangeContext(self, obj)
        c.action = action
        c.preChange = True
        self._Changed(c)
        func()
        c.postChange = True
        self._Changed(c)

    def append(self, obj):
        func = lambda: super(ModificationNotifier, self).append(obj)
        self.__fireChange("append", obj, func)

    def remove(self, obj):
        func = lambda: super(ModificationNotifier, self).remove(obj)
        self.__fireChange("remove", obj, func)

    def insert(self, position, obj):
        func = lambda: super(ModificationNotifier, self).insert(position, obj)
        self.__fireChange("insert", obj, func)

# create a seperate Event listener for each class
# and provide ModificationNotifier Capabilities
class Value(ModificationNotifier, value.Value):
    _Changed = Event("value")

class Property(ModificationNotifier, prop.Property):
    _Changed = Event("prop")

class Section(ModificationNotifier, section.Section):
    _Changed = Event("sec")

class Document(ModificationNotifier, doc.Document):
    _Changed = Event("doc")

