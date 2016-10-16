import odml
import odml.tools.event as event
import odml.tools.weakmeth as weakmeth
import odml.tools.nodes as nodes

# events are required for proxy objects 
odml.setMinimumImplementation('event')

class Proxy(object):
    """common interface"""
    pass

# here we hook the base-class-comparism functionality to
# prefer comparism provided by the proxy obj
_odml_base___eq__ = odml.base.baseobject.__eq__
def _proxy___eq__(self, obj):
    if isinstance(obj, Proxy) and not isinstance(self, Proxy):
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
    """
    A BaseProxy that uses a set of attributes (defined in self._format)
    to compare to other objects
    """
    def __eq__(self, obj):
        for key in self._format:
            if not hasattr(self, key) or not hasattr(obj, key):
                return False
            if getattr(self, key) != getattr(obj, key):
                return False
        return True

class PassProxy(BaseProxy):
    """
    A simple Proxy forwarding all attribute access to the delegate

    It can have inaccessable values (write protected)::

        inaccessable = {'name': 'default name'}

    Attributes indicated in the dictionary *personal* are stored in the proxy
    and not in the delegate, however note: functions not defined in the proxy
    are actually attributes of the delegate and executed on it, so they will not
    work on the *personal* attributes, but on the delegates ones.
    """
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

class NotifyingProxy(event.ModificationNotifier, PassProxy):
    """
    Hooks the personal attributes to cause change events
    """
    def __setattr__(self, name, value):
        if name in self.personal:
            return super(NotifyingProxy, self).__setattr__(name, value)
        return PassProxy.__setattr__(self, name, value)

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

class ChangeAbleProxy(NotifyingProxy):
    """
    A notifying PassProxy with a change handler, attached to original object
    and passing events on modifying them in such that they appear to originate
    from the Proxy object.

    Change handlers are installed as weak references, s.t. the installed change
    handlers don't solely cause the Proxy object to stay in memory
    """
    personal = set(["_change_handler"])
    _change_handler = None

    def __init__(self, obj):
        super(ChangeAbleProxy, self).__init__(obj)

        # use a weak ref and detach at some point
        weak_change_handler = weakmeth.WeakMethod(self.change_handler)
        def call(context):
            if weak_change_handler() is None: return
            return weak_change_handler()(context)

        self._weak_change_handler = call
        obj.add_change_handler(call)

    @property
    def _Changed(self):
        return self._proxy_obj._Changed

    def change_handler(self, context):
        """
        redo the change handler but replace the proxied object
        with our instance
        """
        cur = context._obj.pop()
        context.passOn(self)
        context._obj.append(cur)

    def __del__(self):
        """
        our object is no longer needed, so we can also remove the change handler
        from the original object
        """
        self._proxy_obj.remove_change_handler(self._weak_change_handler)

class PropertyProxy(EqualityBaseProxy, ChangeAbleProxy, odml.property.Property, nodes.PropertyNode):
    """
    A PropertyProxy provides transparent access to a Property,
    blocking only the 'mapping' attribute.

    It has however to take care, that when accessing its values, appropriate
    proxy objects are returned, as otherwise gui functionality breaks
    """
    inaccessable = {"mapping": None}#, "name": PassProxy.PASS_THROUGH}
    personal = set(["_section", "name", "_p_values"]) | ChangeAbleProxy.personal
    _Changed = event.Property._Changed
    _p_values = []

    # TODO make this generic
    @property
    def parent(self):
        return self._section

    @property
    def values(self):
        """
        provide transparent access to values as Proxy objects

        use "caching" to return the same proxy object for the same value
        as other functionality needs to be able to identify a certain object
        exactly (TODO append/insert/remove invalidates the cache and might still
        break stuff)
        """
        # do some caching
        if len(self._p_values) == len(self._proxy_obj.values):
            cached = True

            for i, val in enumerate(self._p_values):
                if not val._proxy_obj is self._proxy_obj.values[i]:
                    cached = False
                    break

            if cached:
                return self._p_values

        # transparently create proxy objects
        self._p_values = map(ValueProxy, self._proxy_obj.values)
        for i in self._p_values: # and make them remember to which property they belong
            i._property = self
        return self._p_values

    def change_handler(self, context):
        """
        we need to fix append/insert/remove notifications
        so that they deal with ProxyObjects instead
        """
        # TODO this needs to be double checked
        oval = None
        if isinstance(context.val, odml.value.Value):
            oval = context.val
            if context.postChange ^ (context.action == "remove"):
                assert oval.parent is not None
                i = self.values.index(oval)
                context.val = self.values[i]
            else: # the val does not yet/anymore exist
                assert oval.parent is None
                context.val = ValueProxy(oval)
            context.val._property = self
        super(PropertyProxy, self).change_handler(context)
        if oval is not None:
            context.val = oval

    def path_to(self, child):
        """
        override this, to account for proxy objects
        """
        if not isinstance(child, PassProxy):
            return super(PropertyProxy, self).path_to(child)
        for (i, obj) in enumerate(self._values):
            if obj is child._proxy_obj: return (i,)
        raise ValueError("%s does not contain the item %s" % (repr(self), repr(child)))

class ValueProxy(EqualityBaseProxy, ChangeAbleProxy, odml.value.Value, nodes.ValueNode):
    """
    A ValueProxy provides transparent access to a Value,
    but has its own parent (_property)
    """
    personal = set(["_property"]) | ChangeAbleProxy.personal
    _Changed = event.Value._Changed

    # TODO make this generic
    @property
    def parent(self):
        return self._property

class ReadOnlyObject(object):
    """
    An odml-object whose properties (according to *_format*)
    cannot be modified if *enable_protection* is set.
    """
    enable_protection = False
    def __setattr__(self, name, value):
        if self.enable_protection and name in self._format._args:
            raise AttributeError("attribute '%s' is read-only" % name)
        object.__setattr__(self, name, value)

class SectionProxy(odml.getImplementation().Section, Proxy):
    """
    A Section that will also pass as a Proxy
    """
    def proxy_remove(self, obj):
        """
        explicitly remove a proxy object without side-effects
        """
        assert isinstance(obj, Proxy)
        super(SectionProxy, self).remove(obj)

    def proxy_append(self, obj):
        """
        explicitly append a proxy object without side-effects
        """
        assert isinstance(obj, Proxy)
        super(SectionProxy, self).append(obj)

class BaseSectionProxy(SectionProxy):
    pass

class ReadOnlySection(SectionProxy, ReadOnlyObject):
    """
    A protected section, that cannot be modified
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
        if self.enable_protection:
            raise TypeError("Cannot remove from a proxy section")
        super(SectionProxy, self).remove(obj)

    def _unprotected(self, func):
        """
        briefly disable write protection for the execution
        of *func*
        """
        p = self.enable_protection
        self.enable_protection = False
        ret = func()
        self.enable_protection = p
        return ret

class NonexistantSection(ReadOnlySection):
    """
    A NonexistantSection is a fake section that only exists
    in the mapping. However it has real children.
    """
# there is an explicit method now: proxy_append
#    def append(self, obj):
#        # always allow to insert proxy objects
#        if isinstance(obj, Proxy):
#            super(SectionProxy, self).append(obj)
#        else:
#            super(NonexistantSection, self).append(obj)

#    def proxy_remove(self, obj):
#        # also allow to remove proxy objects
#        # unmap the original property and then remove it (this is done in mapping)
#        #if not isinstance(obj, PropertyProxy):
#        return super(NonexistantSection, self).remove(obj)
#
#        raise NotImplementedError("""
#        we could do this, but this would break undo functionality, so
#        better remove the original property from its parent section
#        """)
#        # prop = obj._proxy_objremove_proxy
#        # mapping.unmap_property(prop=prop, mprop=obj)
#        # prop.parent.remove(prop)

    def merge(self, section=None):
        """
        performs the merge operation, briefly disables read_protection
        """
        self._unprotected(lambda: super(NonexistantSection, self).merge(section))

    def unmerge(self, section):
        """
        performs the unmerge operation, briefly disables read_protection
        """
        self._unprotected(lambda: super(NonexistantSection, self).unmerge(section))

    def __repr__(self):
        return super(NonexistantSection, self).__repr__().replace("<Section", "<?Section")

class DocumentProxy(EqualityBaseProxy, odml.getImplementation().Document):
    """
    A bare bones DocumentProxy not yet proxing actually much. TODO make it a HookProxy?
    """
    def __init__(self, doc):
        super(DocumentProxy, self).__init__(doc)
        odml.getImplementation().Document.__init__(self) # TODO this might already be a different implementation now. and we're not an instance
        for name in odml.format.Document:
            if name in odml.format.Document._args: # skip 'sections'
                setattr(self, name, getattr(doc, name))
    # TODO append also needs to append to original document and care about mappings and stuff
    # TODO same for insert/remove

    def proxy_remove(self, obj):
        self.remove(obj)
    def proxy_append(self, obj):
        self.append(obj)

#class DocumentProxy(EqualityBaseProxy, ChangeAbleProxy, odml.document.Document, nodes.DocumentNode):
#    """
#    A ValueProxy provides transparent access to a Value
#    """
#    personal = set(["_sections"]) | ChangeAbleProxy.personal
#    _Changed = event.Document._Changed
#
#    # TODO make this generic
#    @property
#    def sections(self):
#        return self._sections
#
#    def proxy_remove(self, obj):
#        self.remove(obj)
#
#    def proxy_append(self, obj):
#        self.append(obj)

class MappedSection(EqualityBaseProxy, HookProxy, ReadOnlySection):
    """
    Like a fake section, but we reference a concrete section
    and forward changes to it

    TODO stuff works, but clear to account for proxy_append/insert/remove
    """
    hooks = set(["name"])

    def __init__(self, obj, template=None):
        super(MappedSection, self).__init__(obj)
        if template is not None:
            obj = template
        super(ReadOnlySection, self).__init__(obj.name, obj.type)
        obj.add_change_handler(self.change_handler)

    def change_handler(self, context):
        if context.postChange and context.obj is context.cur:
            # intercept append and remove actions
            if context.action == "append" or context.action == "insert":
                self.proxy_append(self.mkproxy(context.val))
                return # don't pass this event further
            elif context.action == "remove":
                obj = self.contains(context.val) # find an equal one
                # the source section removed the object
                # if it was explicitly mapped, it might already be gone
                # if apparently not: handle it
                if obj is not None:
                    self.proxy_remove(obj)
                # don't pass this event further: either it does not affect us anyway
                # (removing the mapping causes a seperate change event for this section)
                # or we explicitly remove the obj ourselves causing a seperate event too
                return

        # TODO this could cause conflicts in gui (maybe)
        # pass on the event replacing the original object with us (the proxy equivalent)
        cur = context._obj.pop()
        context.passOn(self)
        context._obj.append(cur)

    def mkproxy(self, obj):
        """
        create a proxy equivalent of obj

        obj is either a Section (-> MappedSection) or a Property (-> PropertyProxy)
        """
        if isinstance(obj, odml.property.Property):
            return PropertyProxy(obj)
        return MappedSection(obj)

    def append(self, obj):
        assert not isinstance(obj, Proxy) # proxies should always go through the proxy_append method. TODO also when setting links?
        # a normal object needs to be appended to the proxied section and then
        # we will handle (hopefully) everything else that might be necessary in
        # the change handler (i.e. append a proxy version to ourselves)
        return self._proxy_obj.append(obj)

    # won't support insert. it'd be crazy

    def remove(self, obj):
        # we should only contain proxy objects (unless a link is present TODO)
        if not isinstance(obj, Proxy):
            print "%s should only contain proxy objects, but then look at this" % repr(self), obj
            obj = self.contains(obj)
        assert isinstance(obj, Proxy)

        # trying to remove a Section only present in the mapping is prohibited
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
