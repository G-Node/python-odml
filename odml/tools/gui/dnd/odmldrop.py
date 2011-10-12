import gtk

import tree
from ..DocumentRegistry import DocumentRegistry
from .. import commands
from targets import ActionDrop

class OdmlTreeDropTarget(tree.TreeDropTarget):
    """
    A DropTarget for odml-TreeViews

    it wraps a Data-Target for the actual handling and abstracts the treeview
    model, iter, position data to odml-objects *dst* and a desired drop position
    index *position*.
    """
    def __init__(self, mime=None, target=None, preview_required=None, *args, **kwargs):
        super(OdmlTreeDropTarget, self).__init__(*args, **kwargs)
        if mime is not None:
            self.mime = mime
        if preview_required is not None:
            self.preview_required = preview_required
        self.target = target

    def get_target(self, model, iter, position):
        """
        returns the odml-object and the desired drop position index
        """
        if iter is None:
            obj = model._section
        else:
            obj = model.get_object(iter)
        if position == gtk.TREE_VIEW_DROP_BEFORE:
            return obj.parent, obj.position
        if position == gtk.TREE_VIEW_DROP_AFTER:
            return obj.parent, obj.position+1
        return obj, -1

    def tree_can_drop(self, action, model, iter, position, data=None):
        obj, position = self.get_target(model, iter, position)
        self.model = model # store the model for later use
        return self.odml_tree_can_drop(action, obj, position, data)

    def odml_tree_can_drop(self, action, dst, position, data):
        raise NotImplementedError

    def odml_can_drop(self, action, dst, position, src):
        if self.target is None:
            raise NotImplementedError
        return self.target.odml_can_drop(action, dst, position, src)

    def tree_receive_data(self, action, data, model, iter, position):
        obj, position = self.get_target(model, iter, position)
        self.model = model # store the model for later use
        return self.odml_tree_receive_data(action, obj, position, data)

    def odml_tree_receive_data(self, action, dst, position, data):
        raise NotImplementedError

    def drop_object(self, action, dst, position, obj):
        """
        fulfill the actual drop action. delegate to target
        """
        if self.target is None:
            raise NotImplementedError
        return self.target.drop_object(action, dst, position, obj)

class OdmlDrop(ActionDrop, OdmlTreeDropTarget):
    """
    Base for most Odml-Object Drop Targets

    needs a DocumentRegistry to resolve text-references to Documents
    """
    app = gtk.TARGET_SAME_APP
    def __init__(self, registry=None, *args, **kwargs):
        super(OdmlDrop, self).__init__(*args, **kwargs)
        self.registry = registry

    def get_document(self, doc_id):
        """
        return the document referenced by *doc_id* from the DocumentRegistry
        """
        return self.registry.get(int(doc_id))

    def get_object(self, doc, path):
        """
        return the object indicated by *path*, starting from *doc*
        """
        return doc.from_path(map(int, path.split(",")))

    def odml_tree_can_drop(self, action, dst, position, data):
        src = None
        if data is not None:
            doc, src = self.get_source(data)
            if src is dst and not action.copy: # allow to copy
                print "can't drop to myself"
                return False
        return self.odml_can_drop(action, dst, position, src)

    def get_source(self, data):
        """
        parse data and return (doc, src), i.e. the source document *doc*
        and source object *src*
        """
        doc, path = data.split(";", 1)
        doc = self.get_document(doc)
        src = self.get_object(doc, path)
        return doc, src

    def odml_tree_receive_data(self, action, dst, position, data):
        """
        handle a drop, pass to drop_object unless this is to be handled
        using reorder functionality.
        """
        doc, src = self.get_source(data)
        if dst is None: return False
        # try to find out if this is a reorder-thing
        if action.move and position != -1 and dst is src.parent:
            cmd = commands.ReorderObject(obj=src, new_index=position)
            return self.execute(cmd)
        return self.drop_object(action, dst, position, src)

    def drop_object(self, action, dst, position, src):
        return super(OdmlDrop, self).drop_object(action, dst, position, src)
        # the delete event still occurs, but is not handled by OdmlDrag objects
        # so we are fine

class OdmlDrag(tree.TreeDragTarget):
    """
    A TreeDragTarget valid for a certain odml object class *inst*
    """
    inst = object
    def __init__(self, mime=None, inst=None, *args, **kwargs):
        super(OdmlDrag, self).__init__(*args, **kwargs)
        if mime is not None:
            self.mime = mime
        if inst is not None:
            self.inst = inst

    def tree_get_data(self, action, model, iter):
        if iter is None: return
        obj = model.get_object(iter)
        if isinstance(obj, self.inst):
            return self.odml_get_data(action, obj)

    def odml_get_data(self, action, obj):
        """
        serialize the object-path and its document reference into a string
        """
        return "%d;%s" % (DocumentRegistry.get_id(obj.document), ",".join(map(str, obj.to_path())))

    def tree_delete_data(self, model, iter):
        if iter is None: return
        obj = model.get_object(iter)
        if isinstance(obj, self.inst):
            return self.odml_delete_data(obj)

    def odml_delete_data(self, obj):
        pass
