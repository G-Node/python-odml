"""odmlview

odmlview sets up a minimal webserver to view odml files saved in the
XML format via the webbrowser. After it started, the webserver will
open a new tab in the default webbrowser and display the content of
the directory the server was started from. odML files can then be
viewed from there.
To properly render XML, an odML file may contain the element
'<?xml-stylesheet  type="text/xsl" href="odmlTerms.xsl"?>' where the
'odmlTerms.xsl' stylesheet should reside in the same directory as the
odML file to be rendered. By using the '--fetch' flag the latest version
of this stylesheet will be downloaded from 'templates.g-node.org' to
the current directory when starting up the service.

Usage: odmlview [-p PORT] [--fetch]

Options:
    -p PORT         Port the server will use. Default: 8000
    --fetch         Fetch latest stylesheet from templates.g-node.org
                    to current directory
    -h --help       Show this screen
    --version       Show version
"""

import os
try:
    import http.server as hs
except ImportError:
    print("This script is only supported with Python 3")
    exit(-1)

import socketserver
import sys
import urllib.request as urllib2
import webbrowser

from docopt import docopt

PORT = 8000
REPOSITORY = "https://templates.g-node.org/_resources/"
STYLESHEET = "odmlTerms.xsl"


def download_file(repo, filename):
    """
    download_file fetches 'filename' from url 'repo' and
    saves it in the current directory as file 'filename'.
    """
    try:
        data = urllib2.urlopen("%s%s" % (repo, filename)).read()
        data = data.decode("utf-8")
    except Exception as err:
        print("[Warning] Failed loading '%s%s': %s" % (repo, filename, err))
        return

    with open(filename, "w") as local_file:
        local_file.write(str(data))


def run(port=PORT, extensions=None):
    """
    run starts a simple webserver on localhost serving the current directory.
    Once started, it will open a tab on the default webbrowser and will continue
    to serve until manually stopped.

    :param port: server port
    :param extensions: dictionary containing additional file extension - mime type
                       mappings the server should be aware of.
                       e.g. {'.xml': 'application/xml'}
    """
    handler = hs.SimpleHTTPRequestHandler

    if extensions:
        handler.extensions_map.update(extensions)

    server_address = ('', port)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, handler) as httpd:
        webbrowser.open_new_tab('http://localhost:%s' % port)
        try:
            print("[Info] The server can be stopped by pressing Ctrl+C")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("[Info] Received Keyboard interrupt, shutting down")
            httpd.shutdown()
            httpd.server_close()


def main(args=None):
    parser = docopt(__doc__, argv=args, version="0.1.0")

    # Fetch stylesheet
    if parser['--fetch'] and not os.path.exists(STYLESHEET):
        print("[Info] Downloading stylesheet '%s'" % STYLESHEET)
        download_file(REPOSITORY, STYLESHEET)

    server_port = int(parser['-p']) if parser['-p'] else PORT

    # files with odML file extensions should be interpreted as XML
    extensions = {'.odml': 'application/xml'}

    run(server_port, extensions)


if __name__ == "__main__":
    main(sys.argv[1:])
