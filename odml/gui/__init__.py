#!/usr/bin/env python
import os, sys
import gtk

import Editor

def main(filenames=[]):
    """
    start the editor, with a new empty document
    or load all *filenames* as tabs

    returns the tab object
    """
    Editor.register_stock_icons()
    editor = Editor.EditorWindow()
    tabs = map(editor.load_document, filenames)
    if len(filenames) == 0:
        tabs = [editor.new_file()]
    return tabs
