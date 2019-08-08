"""odmlView

odmlView sets up a minimal webserver and serves
and renders odml files locally from the directory
the server is started in.

Usage: odmlView [-d DIRECTORY] [-p PORT]
Usage: odmlview [-p PORT] [--fetch]

Options:
    -p PORT         Port the server will use.
                    Default is port 8000.
    --fetch         Fetch latest stylesheet from templates.g-node.org
                    to current directory
    -h --help       Show this screen
    --version       Show version
"""

import http.server as hs
import socketserver
import sys
import urllib.request as urllib2
import webbrowser

from docopt import docopt

PORT = 8000
REPOSITORY = "https://templates.g-node.org/_resources/"
STYLESHEET = "odmlTerms.xsl"


def fetch_stylesheet():
    try:
        data = urllib2.urlopen("%s%s" % (REPOSITORY, STYLESHEET)).read()
        data = data.decode("utf-8")
    except Exception as e:
        print("failed loading '%s%s': %s" % (REPOSITORY, STYLESHEET, e))
        return

    with open(STYLESHEET, "w") as fp:
        fp.write(str(data))


def run(port=PORT):
    handler = hs.SimpleHTTPRequestHandler
    # files with odML extensions should be interpreted as XML
    handler.extensions_map.update({'.odml': 'application/xml'})

    server_address = ('', port)

    with socketserver.TCPServer(server_address, handler) as httpd:
        webbrowser.open_new_tab('http://localhost:%s' % port)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Received Keyboard interrupt, shutting down")
            httpd.server_close()


def main(args=None):
    parser = docopt(__doc__, argv=args, version="0.1.0")

    # Fetch stylesheet
    if parser['--fetch'] and not os.path.exists(STYLESHEET):
        fetch_stylesheet()

    server_port = int(parser['-p']) if parser['-p'] else PORT

    run(server_port)


if __name__ == "__main__":
    main(sys.argv[1:])
