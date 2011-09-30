import odml
import terminology
import weakref

class mapable(object):
    """
    Provides assisting functionality for objects that support
    the mapping attribute (i.e. sections and properties)
    """
    __active_mapping = None
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
        if stype is None:
            return term.sections[0]
        sec = term.find_related(type=stype)
        if sec is None:
            return None
        if prop_name is None:
            return sec
        return sec.properties[prop_name]

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
        print "active mapping:", self._active_mapping, self.__active_mapping
        if self._active_mapping is not None:
            remap = self.unmap()

        self._mapping = new_value

        if remap is not None:
            self.remap(remap)

    @property
    def _active_mapping(self):
        if self.__active_mapping is None: return None
        return self.__active_mapping()

    @_active_mapping.setter
    def _active_mapping(self, new_value):
        self.__active_mapping = weakref.ref(new_value)

    @_active_mapping.deleter
    def _active_mapping(self):
        del self.__active_mapping

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
        print "unmap property"
        return unmap_property(prop=self)

    def remap(self, mprop):
        print "remap property"
        create_property_mapping(self.parent, self)

class mapableSection(mapable):
    def unmap(self):
        return unmap_section(self)

    def remap(self, msec):
        # the mapping might have changed, we create a new
        # mapped section and replace msec in its tree if appropriate
        nmsec = create_section_mapping(self)
        nmsec._sections = msec._sections

        self._active_mapping = nmsec
        for prop in self.properties:
            create_property_mapping(self, prop)

class MappingError(TypeError):
    pass

def create_mapping(doc):
    global proxy # we install the proxy only late time
    import tools.proxy as proxy
    mdoc = doc.clone(children=False) # TODO might need to proxy this too
    mdoc._proxy_obj = doc
    doc._active_mapping = mdoc

    # iterate each section and property
    # take the mapped object and try to put it at a meaningful place
    for sec in doc.itersections(recursive=True):
        create_section_mapping(sec)

    for sec in doc.itersections(recursive=True):
        for prop in sec.properties: # not needed anymore: [:]:
            create_property_mapping(sec, prop)

    return mdoc

def create_section_mapping(sec):
    obj = sec.mapped_object
    msec = proxy.MappedSection(sec, template=obj)
    sec._active_mapping = msec
    sec.parent._active_mapping.append(msec)

    if obj:
        term = obj.get_repository()
        if msec.get_repository() != term:
            msec.repository = term

    return msec

def create_property_mapping(sec, prop):
    msec = sec._active_mapping
    mprop = proxy.PropertyProxy(prop)
    mprop._section = None
    prop._active_mapping = mprop

    mapping = prop.mapped_object
    if mapping is None: # easy case: just proxy the property
        msec.append(mprop)
        return

    print mprop.parent
    mprop.name = mapping.name

    dst_type = mapping._section.type

    # rule 4c: target-type == section-type
    #          copy attributes, keep property
    if dst_type == msec.type:
        msec.append(mprop)
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
                child.append(mprop)
                msec.append(child)

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
            msec.append(child)
    elif len(child) > 1:
        raise MappingError("""Your data organisation does not make sense,
        there are %d children of type '%s'. Don't know how to handle.""" % (len(child), dst_type))
    else: # exactly one child found
        child = child[0]

    child.append(mprop)
    return mprop

def unmap_property(prop=None, mprop=None):
    print "unmap prop"
    if mprop is None:
        if prop is None or prop._active_mapping is None: return
        mprop = prop._active_mapping

    if prop is None:
        prop = mprop._proxy_obj

    msec = mprop.parent

    msec.remove_proxy(mprop)
    # figure out, if we can safely remove mprop's section
    if isinstance(msec, proxy.NonexistantSection) and \
        len(msec) == 0:
        # there are no subsections/properties left
        msec.parent.remove_proxy(msec)
        # TODO cascade till toplevel?

    del prop._active_mapping
    return mprop

def unmap_section(sec):
    """
    try to unmap the section, but make sure, that there are
    no dependencies. i.e. we cannot unmap a section if properties
    from other sections are mapped here, this would break stuff
    """
    print "unmap sec"
    if sec._active_mapping is None: return
    msec = sec._active_mapping
    for mprop in msec:
        if mprop._proxy_obj.parent is not msec._proxy_obj:
            raise MappingError("""
            There are other active mappings to this section.
            Unmapping can't be done safely. Destroy the mapped view
            before editing. (%s vs %s) (%s.%s)
            """ % (mprop._proxy_obj.parent, msec._proxy_obj, msec, mprop))

    # all properties we find here are from our own section,
    # so it seems safe to unmap all
    for mprop in msec:
        unmap_property(mprop=mprop)

    # now the section should have no properties left
    assert len(msec.properties) == 0

    # TODO do we need to do anything more with this section?
    if isinstance(msec.parent, proxy.Proxy):
        msec.parent.remove_proxy(msec)
    else:
        msec.parent.remove(msec)

    return msec

def unmap_document(doc):
    """
    clear all mappings from the document
    """
    print "unmap doc"
    for sec in doc.itersections(recursive=True):
        del sec._active_mapping
        for prop in sec.properties:
            del prop._active_mapping
