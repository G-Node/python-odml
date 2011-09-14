import GenericIter
import string

class PropIter(GenericIter.GenericIter):
    """
    An iterator for a Property

    returns ValueIter objects if queried for children.
    Since Values don't have a parent relationship, the PropIter will store
    pass a corresponding parent attribute (the Property object) to the ValueIter

    As odML supports multi-values, each property may or may not have multiple children.
    """

    def get_value(self, attr):
        if attr == "name":
            return self._obj.name

        if self.has_child:
            return self.get_mulitvalue(attr)
        else:
            return self.get_singlevalue(attr)

    def get_mulitvalue(self, name):
        #Most of the stuff is empty and handled by the
        #value
        if name == "value":
                return "<multi>"
        return ""

    def get_singlevalue(self, name):
        #here we proxy the value object
        if len(self._obj._values) == 0:
            return ""

        prop = self._obj.values[0]
        return getattr(prop, name)

    @property
    def has_child(self):
        return self.n_children > 1

    @property
    def n_children(self):
        return len(self._obj._values)

    @property
    def parent(self):
        return None

class ValueIter(GenericIter.GenericIter):
    """
    An iterator for a Value object
    """

    def get_value(self, attr):
        if attr == "name":
            return
        if attr == "value":
            if self._obj.dtype == "binary":
                # fix how binary context is displayed here
                data = self._obj.data
                unprintable = filter(lambda x: x not in string.printable, data)
                if len(data) > 15 or len(unprintable) > 0:
                    return "(%d bytes binary content)" % len(data)
        return super(ValueIter, self).get_value(attr)

class SectionIter(GenericIter.GenericIter):
    @property
    def parent(self):
        if not self._obj.parent:
            return None
        if not self._obj.parent.parent: # the parent is the document root
            return None
        return super(SectionIter, self).parent
