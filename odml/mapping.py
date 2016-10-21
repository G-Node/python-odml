import odml
import odml.terminology as terminology
import weakref
from functools import wraps

# late import, as the proxy module relies on the latest available
# concrete odml-class implementations, that would not be available if they
# were directly imported in the beginning
proxy = None


class mapped(object):
    """
    Keeps information for objects that can have a current mapped object associated
    with them
    """
    __active_mapping = None
    @property
    def _active_mapping(self):
        if self.__active_mapping is None: return None
        return self.__active_mapping()

    @_active_mapping.setter
    def _active_mapping(self, new_value):
        self.__active_mapping = weakref.ref(new_value)

    @_active_mapping.deleter
    def _active_mapping(self):
        if not self.__active_mapping is None:
            del self.__active_mapping


class mapable(mapped):
    """
    Provides assisting functionality for objects that support
    the mapping attribute (i.e. sections and properties)
    """
    def get_mapping(self):
        """
        returns the current valid mapping for this section / property
        which may be defined by the object itsself, by its terminology equivalent
        or inherited from its parent
        """
        mapping = self.mapping
        if mapping is None:
            if self.parent.parent is not None: # i.e. not the root node
                return self.parent.get_mapping()
        return (self, mapping)

    @staticmethod
    def parse_mapping(url):
        """
        parse u url of format http://host/file.xml#section_type:property_name

        returns a 3-tuple: (url, stype, prop_name)
        where stype or prop_name may be None
        """
        stype = None
        prop_name = None
        if '#' in url:
            url, stype = url.split('#', 1)
            if ':' in stype:
                stype, prop_name = stype.split(':', 1)
        terminology.deferred_load(url)
        return (url, stype, prop_name)

    @staticmethod
    def get_mapping_object(url):
        """
        returns the object instance a mapping-url points to
        """
        url, stype, prop_name = mapable.parse_mapping(url)
        term = terminology.load(url)
        if term is None:
            raise MappingError("Terminology '%s' could not be loaded" % url)
        if stype is None:
            return term.sections[0]
        sec = term.find_related(type=stype)
        if sec is None:
            raise MappingError("No section of type '%s' could be found" % stype)
        if prop_name is None:
            return sec
        try:
            return sec.properties[prop_name]
        except KeyError:
            raise MappingError("No property named '%s' could be found in section '%s'" % (prop_name, sec.name))

    @property
    def mapped_object(self):
        """
        if there is a mapping defined (or inherited), returns the corresponding
        mapping object
        """
        url = self.mapping
        if url is not None:
            return self.get_mapping_object(url)

        return None
        #if self.parent is not None: # i.e. not the root node
        #    obj = self.parent.mapped_object
        #    if obj is not None:
        #        return obj.contains(self)

    @property
    def mapping(self):
        """
        return the applicable mapping-url (which may be provided by the terminology)
        """
        if self._mapping is None:
            term = self.get_terminology_equivalent()
            if term is not None:
                return term._mapping
        return self._mapping

    @mapping.setter
    def mapping(self, new_value):
        if new_value == '':
            new_value = None

        term = self.get_terminology_equivalent()
        if term is not None and term._mapping == new_value:
            new_value = None
        if self._mapping == new_value: return

        remap = None
        # TODO should save the old index when unmapping and then use insert to
        #      (re)introduce the new mapping, to keep order intact
        if self._active_mapping is not None:
            remap = self.unmap()

        self._mapping = new_value

        if remap is not None:
            self.remap(remap)

    def unmap(self):
        """
        unestablish the mapping for this object
        """
        raise NotImplementedError

    def remap(self, mobj):
        """
        reestablish the mapping for this object
        """
        raise NotImplementedError


class mapableProperty(mapable):
    def unmap(self):
        """
        uninstall the property mapping by removing its proxy object from its mapped section
        """
        return unmap_property(prop=self)

    def remap(self, mprop):
        """
        install the mapping for this property
        """
        create_property_mapping(self.parent, self)


class mapableSection(mapable):
    def unmap(self):
        """
        recursively unmap this section

        in certain configurations, a mapping cannot be completely removed for a
        whole section. In this case, this will raise a MappingError-Exception.

        To still do it, unmap the whole document (or destroy the mapped view)
        prior to the change execution.
        """
        return unmap_section(self)

    def remap(self, msec):
        """
        reestablish a mapping assuming that this section was successfully unmapped
        earlier. To avoid undefined side-effects, only call this, if this section
        is the only section without an established mapping.
        """
        # map the section subtree
        nmsec = create_section_mapping(self)

        # remap all the properties
        for child in self.itersections(recursive=True, yield_self=True):
            for prop in child.properties:
                create_property_mapping(child, prop)


def remapable_append(func):
    """
    decorator for append-functions to deal with Proxy objects
    """
    @wraps(func)
    def f(self, obj):
        ret = func(self, obj)
        if (proxy and not isinstance(obj, proxy.Proxy)) and hasattr(obj, "_remap_info"):
            obj.remap(obj._remap_info)
        return ret
    return f


def remapable_insert(func):
    """
    decorator for insert-functions to deal with Proxy objects
    """
    @wraps(func)
    def f(self, position, obj):
        ret = func(self, position, obj)
        if (proxy and not isinstance(obj, proxy.Proxy)) and hasattr(obj, "_remap_info"):
            obj.remap(obj._remap_info)
        return ret
    return f


def remapable_remove(func):
    """
    decorator for remove-functions to deal with Proxy objects
    """
    @wraps(func)
    def f(self, obj):
        # don't attempt anything on proxy objects
        if (proxy and not isinstance(obj, proxy.Proxy)) and obj._active_mapping is not None:
            obj._remap_info = obj.unmap()
        return func(self, obj)
    return f


class MappingError(TypeError):
    pass


def create_mapping(doc):
    """
    install the mapping for the document

    1. recursively map all sections
    2. afterwards map all their properties
    """
    global proxy  # we install the proxy only late time
    import odml.tools.proxy as proxy
    mdoc = proxy.DocumentProxy(doc)
    # TODO copy attributes, but also make this generic
    mdoc._proxy_obj = doc
    doc._active_mapping = mdoc

    # iterate each section and property
    # take the mapped object and try to put it at a meaningful place
    for sec in doc.sections:
        create_section_mapping(sec)  # this recurses on its own

    for sec in doc.itersections(recursive=True):
        for prop in sec.properties:  # not needed anymore: [:]:
            create_property_mapping(sec, prop)

    return mdoc


def create_section_mapping(sec):
    """
    recursively install the mapping for a section

    Note: the mappings for the properties contained in the sections need to be
    installed afterwards (after all sections have been mapped) manually
    """
    obj = sec.mapped_object
    msec = proxy.MappedSection(sec, template=obj)
    sec._active_mapping = msec
    sec.parent._active_mapping.proxy_append(msec)

    if obj:
        term = obj.get_repository()
        if msec.get_repository() != term:
            msec.repository = term

    # map all child sections
    for child in sec.sections:
        create_section_mapping(child)

    return msec


def create_property_mapping(sec, prop):
    """
    map a property to its destination place using the mapping rules (see test/mapping.py)

    Note: all sections of the document need already to be mapped
    """
    msec = sec._active_mapping
    mprop = proxy.PropertyProxy(prop)
    mprop._section = None
    prop._active_mapping = mprop

    mapping = prop.mapped_object
    if mapping is None: # easy case: just proxy the property
        msec.proxy_append(mprop)
        return

    mprop.name = mapping.name

    dst_type = mapping._section.type

    # rule 4c: target-type == section-type
    #          copy attributes, keep property
    if dst_type == msec.type:
        msec.proxy_append(mprop)
        return mprop

    # rule 4d: one child has the type
    child = msec.find_related(type=dst_type, siblings=False, parents=False, findAll=True)
    if child is None:
        # rule 4e: a sibling has the type
        sibling = msec.find_related(type=dst_type, children=False, parents=False)
        if sibling is not None:
            rel = sibling.find_related(type=msec.type, findAll=True)
            if len(rel) > 1:
                # rule 4e2: create a subsection linked to the sibling
                # TODO set repository and other attributes?
                child = proxy.NonexistantSection(sibling.name, sibling.type)
                child.proxy_append(mprop)
                msec.proxy_append(child)

                # TODO the link will have trouble to be resolved, as the
                # nonexistant section does not allow to create any attributes in it
                # as it cannot be proxied
                child._link = sibling.get_path()
                return mprop
            # rule 4e1: exactly one relation for sibling
            child = sibling # once we found the target section, the code stays the same
        else:
            # rule 4f: no sibling, create a new section
            # TODO set repository and other attributes?
            child = proxy.NonexistantSection(mapping._section.name, dst_type)
            msec.proxy_append(child)
    elif len(child) > 1:
        raise MappingError("""Your data organisation does not make sense,
        there are %d children of type '%s'. Don't know how to handle.""" % (len(child), dst_type))
    else: # exactly one child found
        child = child[0]

    # corner-case: we are remapping and/or the section already contains a property
    # with the same name
    # however this will also hold true, if multiple properties map to the same target
    # for now live with it being there multiple times (TODO)
    obj = child.contains(mprop)
    if obj is not None:
        pass #child.proxy_remove(obj)

    child.proxy_append(mprop)
    return mprop


def unmap_property(prop=None, mprop=None):
    """
    uninstall the property mapping by removing its proxy object from its mapped section
    """
    if mprop is None:
        if prop is None or prop._active_mapping is None: return
        mprop = prop._active_mapping

    if prop is None:
        prop = mprop._proxy_obj

    # the section where the property is mapped to
    msec = mprop.parent

    msec.proxy_remove(mprop)

    # figure out, if we can safely remove mprop's section
    # the section can either be a MappedSection that directly corresponds to a section
    # in the original document, or it is a NonexistantSection (either linked or plain)
    #
    if isinstance(msec, proxy.NonexistantSection):
        if msec.is_merged:
            # the section is merged, i.e. it has a link attribute set (can't be include
            # as it is a non-existant section)
            # for now all properties that are no proxies (they are installed using
            # clone()-call) are just copies
            l = len(filter(lambda x: isinstance(x, proxy.Proxy), msec.properties))
        else:
            l = len(msec.properties)

        if l == 0:
            # there are no subsections/properties left
            msec.parent.proxy_remove(msec)
            # TODO cascade till toplevel? probably not

    del prop._active_mapping
    return mprop


def can_unmap_section(sec, top):
    """
    check if a section including its subsections, properties and properties of
    mapped subsections (i.e. NonexistantSections) can safely be unmapped
    """
    # all subsections must be unmap-able
    for sec in sec.sections:
        if not can_unmap_section(sec, top):
            return False

    msec = sec._active_mapping
    if not can_unmap_all_properties(msec, top):
        return False

    # proxy sections that only exist in the mapping, must fulfill the property condition too
    for mchild in msec.sections:
        if isinstance(mchild, proxy.NonexistantSection) and not can_unmap_all_properties(mchild, top):
            return False

    return True


def can_unmap_all_properties(msec, top):
    """
    find out if the mapped section *msec* contains any property whose origin (its proxied object)
    is not within the subtree indicated by section *top*
    """
    for mprop in msec.properties:
        p = mprop._proxy_obj.parent

        while p is not None:
            if p is top:
                break
            p = p.parent
        else:
            # top is not a parent of p
            return False

    return True


def unmap_section(sec, check=True):
    """
    try to unmap the section (including its children),
    but make sure, that there are no dependencies:
    i.e. we cannot unmap a section if properties
    from other sections are mapped here, this would break stuff
    """
    if sec._active_mapping is None:
        return
    msec = sec._active_mapping

    if check and not can_unmap_section(sec, sec):
        raise MappingError("""
            There are other active mappings to this section (or one of its children)
            Unmapping can't be done safely. Destroy the mapped view
            before editing.
            """)

    # first unmap all properties of this section
    for child in sec.itersections(recursive=True, yield_self=True):
        for prop in child.properties:
            mprop = prop._active_mapping
            if mprop is not None: # this may happen for linked sections
                unmap_property(mprop=mprop)

    # now each mapped section should not have any properties left
    for mchild in msec.itersections(recursive=True, yield_self=True):
        assert len(mchild.properties) == 0

    # and we are safe to remove the mappings
    for child in sec.itersections(recursive=True, yield_self=True):
        del child._active_mapping

    # TODO do we need to do anything more with this section?

    # finally we can remove this section from the tree
    assert isinstance(msec.parent, proxy.Proxy)
    msec.parent.proxy_remove(msec)

    return msec


def unmap_document(doc):
    """
    clear all mappings from the document
    """
    for sec in doc.itersections(recursive=True):
        del sec._active_mapping
        for prop in sec.properties:
            del prop._active_mapping
    del doc._active_mapping


def get_object_from_mapped_equivalent(mobj):
    """
    This function tries to find out which object was responsible for
    creating the *mobj*.
    This is straightforward in several cases (i.e. *mobj* being a BaseProxy instance)
    but is not for others (e.g. *mobj* being a section solely created
    for mapping of a property).
    """
    if isinstance(mobj, proxy.BaseProxy):
        return mobj._proxy_obj

    # TODO which other cases may we have?
    assert isinstance(mobj, proxy.NonexistantSection)
    # get the first property (TODO this may not always be the one who caused the section to be created)
    for mprop in mobj.properties:
        return get_object_from_mapped_equivalent(mprop)

    return None
