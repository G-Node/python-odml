#!/usr/bin/env python
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
    return tabs

def run():
    """
    handle all initialisation and start main() and gtk.main()
    """
    try: # this works only on linux
        from ctypes import cdll
        libc = cdll.LoadLibrary("libc.so.6")
        libc.prctl(15, 'odMLEditor', 0, 0, 0)
    except:
        pass
    from optparse import OptionParser
    parser = OptionParser()
    (options, args) = parser.parse_args()
    main(filenames=args)
    gtk.main()

if __name__=="__main__":
    run()
