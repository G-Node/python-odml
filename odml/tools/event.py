from .. import doc, section, value
from .. import property as prop

class Event (object):
    def __init__(self):
        self.handlers = set()

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

    @property
    def n_handler(self):
        return len(self.handlers)

    __iadd__ = add_handler
    __isub__ = remove_handler
    __call__ = fire
    __len__  = n_handler


class ChangedEvent(object):
    def __init__(self):
        pass

class EventHandler(object):
    def __init__(self, func):
        self._func = func
        
    def __call__(self, *args, **kargs):
        return self._func(*args, **kargs)
    
class ModificationNotifier(object):
    def __setattr__(self, name, value):
        super(ModificationNotifier, self).__setattr__(name, value)
        if not name.startswith('_') and hasattr(self, name):
            self._Changed(self)

# create a seperate Event listener for each class
# and provide ModificationNotifier Capabilities
class Value(value.Value, ModificationNotifier):
    _Changed = Event()

class Property(prop.Property, ModificationNotifier):
    _Changed = Event()

class Section(section.Section, ModificationNotifier):
    _Changed = Event()

class Document(doc.Document, ModificationNotifier):
    _Changed = Event()

