import cgi

class GenericIter(object):
    """
    A generic TreeIter mapper for objects.

    These need to support the next() method.

    Objects returned by the object's parent, children[n] or next() attribute
    need to have a IterClass attribute. If it is missing a GenericIter
    will be used.
    """

    def __init__(self, obj):
        """
        create a new iterator for a object
        """
        self._obj = obj

    def new_iter(self, obj):
        if hasattr(obj, "IterClass"):
            return obj.IterClass(obj)
        return self.__class__(obj)

    @staticmethod
    def escape(value):
        """escape html for use in marked up cellrenderers"""
        return cgi.escape(value) if value is not None else None

    def get_value(self, attr):
        return self.escape(getattr(self._obj, attr))

    def to_path(self):
        """
        return the full odml model path
        """
        return self._obj.to_path()

    def get_next(self):
        """
        returns a new Iter object for the next element in this multivalue list
        or None
        """
        obj = self._obj.next()
        if obj is not None:
            return obj.IterClass(obj)

    def get_children(self):
        return self.get_nth_child(0)

    @property
    def has_child(self):
        if hasattr(self._obj, "children"):
            return bool(self._obj.children)
        return False

    @property
    def n_children(self):
        if not self.has_child:
            return 0

        return len(self._obj.children)

    @property
    def parent(self):
        if not hasattr(self._obj, "parent"):
            return None
        obj = self._obj.parent
        return obj.IterClass(obj)

    def get_nth_child(self, n):
        if not self.has_child:
            return None

        obj = self._obj.children[n]
        return obj.IterClass(obj)

    def __repr__(self):
        return "<%s %s <= %s[%d]>" % (
            str(self.__class__.__name__),
            repr(self._obj),
            repr(self._obj.parent),
            self._obj.position)

