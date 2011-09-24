import odml
import event

class Proxy(object):
    # common interface
    pass

_odml_base___eq__ = odml.base.baseobject.__eq__
def _proxy___eq__(self, obj):
    if isinstance(obj, Proxy):
        return obj == self
    return _odml_base___eq__(self, obj)

odml.base.baseobject.__eq__ = _proxy___eq__

class BaseProxy(Proxy):
    """
    A nonfunctional proxy, having only the delegate
    self._proxy_obj

    Comparism is hooked, so the following always holds
    >>> BaseProxy(o) == o
    True
    """
    def __init__(self, obj):
        object.__setattr__(self, "_proxy_obj", obj)

    def __eq__(self, obj):
        """
        return True if both reference to equal objects
        or there referenced object equals *obj*
        """
        if not isinstance(obj, BaseProxy):
            return self._proxy_obj == obj
        return self._proxy_obj == obj._proxy_obj

    def __neq__(self, obj):
        return not self == obj

    def __repr__(self):
        return "P(%s)" % repr(self._proxy_obj)

class EqualityBaseProxy(BaseProxy):
    def __eq__(self, obj):
        for key in self._format:
            if not hasattr(self, key) or not hasattr(obj, key):
                return False
            if getattr(self, key) != getattr(obj, key):
                return False
        return True

class PassProxy(BaseProxy):
    PASS_THROUGH = "PASS_THROUGH"
    inaccessable = {}
    personal = set()

    def __getattr__(self, name):
        val = self.inaccessable.get(name, self.PASS_THROUGH)
        if val != self.PASS_THROUGH:
            return val
        return getattr(self._proxy_obj, name)

    def __hasattr__(self, name):
        return getattr(self._proxy_obj, name)

    def __setattr__(self, name, value):
        if name in self.inaccessable:
            raise AttributeError("Cannot set '%s' attribute on Proxy object" % name)
        if name in self.personal:
            return object.__setattr__(self, name, value)
        return setattr(self._proxy_obj, name, value)

    def __len__(self):
        return self._proxy_obj.__len__()

class HookProxy(BaseProxy):
    """
    A proxy that only intercepts certain attributes
    """
    hooks = set()

    def __getattribute__(self, name):
        if name in object.__getattribute__(self, "hooks"):
            return self._proxy_obj.__getattribute__(name)
        return super(HookProxy, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name in object.__getattribute__(self, "hooks"):
            setattr(self._proxy_obj, name, value)
        else:
            super(HookProxy, self).__setattr__(name, value)

class PropertyProxy(EqualityBaseProxy, PassProxy, event.ChangeHandlable, odml.property.Property):
    """
    A PropertyProxy provides transparent access to a Property,
    blocking only the 'mapping' attribute.
    """
    inaccessable = {"mapping": None}#, "name": PassProxy.PASS_THROUGH}
    personal = set(["_section", "_change_handler", "name"])
    forwards = ["__len__", "__repr__"]
    _Changed = event.Property._Changed
    _change_handler = None

    def __init__(self, obj):
        super(PropertyProxy, self).__init__(obj)
        # TODO memory impairments? GC
        obj.add_change_handler(self.change_handler)

    # TODO make this generic
    @property
    def parent(self):
        return self._section

    def change_handler(self, context):
        context.passOn(self)

class ReadOnlyObject(object):
    enable_protection = False
    def __setattr__(self, name, value):
        if self.enable_protection and name in self._format._args:
            raise AttributeError("attribute '%s' is read-only" % name)
        object.__setattr__(self, name, value)

class SectionProxy(odml.getImplementation().Section, Proxy):
    pass

class BaseSectionProxy(SectionProxy):
    pass

class ReadOnlySection(SectionProxy, ReadOnlyObject):
    """
    A NonexistantSection is a fake section that only exists
    in the mapping. However it has real children.
    """
#    @property
#    def sections(self):
#        return []

    # TODO make this generic
    @property
    def parent(self):
        return self._parent

    def append(self, obj):
        if self.enable_protection:
            raise TypeError("Cannot append to a proxy section")
        super(SectionProxy, self).append(obj)

    def insert(self, index, obj):
        raise TypeError("Cannot insert into a proxy section")

    def remove(self, obj):
        raise TypeError("Cannot remove from a proxy section")

class NonexistantSection(ReadOnlySection):
    def append(self, obj):
        # always allow to insert proxy objects
        if isinstance(obj, Proxy):
            super(SectionProxy, self).append(obj)
        else:
            super(NonexistantSection, self).append(obj)

class MappedSection(EqualityBaseProxy, HookProxy, ReadOnlySection):
    """
    Like a fake section, but we reference a concrete section
    and forward changes to it
    """
    hooks = set(["name", "repository"])

    def __init__(self, obj, template=None):
        super(MappedSection, self).__init__(obj)
        if template is not None:
            obj = template
        super(ReadOnlySection, self).__init__(obj.name, obj.type)
        obj.add_change_handler(self.change_handler)

    def change_handler(self, context):
        #print context, context.obj
        if context.postChange and context.obj is context.cur:
            # intercept append and remove actions
            if context.action == "append" or context.action == "insert":
                self.append(self.mkproxy(context.val))
                return # don't pass this event further
            elif context.action == "remove":
                obj = self.contains(context.val) # find an equal one
                #print "remove", obj, "from", self, "vs", context.cur
                #print object.__repr__(obj), object.__repr__(self._props[0])
                assert obj is not None
                super(SectionProxy, self).remove(obj)
                return # don't pass this event further

        # TODO this could cause conflicts in gui (maybe)
        context.passOn(self)

    def mkproxy(self, obj):
        if isinstance(obj, odml.property.Property):
            return PropertyProxy(obj)
        return MappedSection(obj)

    def append(self, obj):
        # properties are kept
        if not isinstance(obj, Proxy):
            self._proxy_obj.append(obj)
            # we append the corresponding proxy object to ourselves
            # in the change_handler
            return

        # use the normal append method of Section
        super(SectionProxy, self).append(obj)

    # won't support insert. its crazy

    def remove(self, obj):
        if not isinstance(obj, Proxy):
            obj = self.contains(obj)
        assert isinstance(obj, Proxy)

        if isinstance(obj, NonexistantSection):
            # can't remove what doesn't really exist
            raise TypeError("Cannot remove from a proxy section")

        # remove the mapped object, which may be somewhere else!
        parent = obj._proxy_obj.parent
        if parent is not None:
            parent.remove(obj._proxy_obj)
        try:
            # use the normal remove method of Section
            super(SectionProxy, self).remove(obj)
        except ValueError: # we might have already removed the property in the change handler
            pass
