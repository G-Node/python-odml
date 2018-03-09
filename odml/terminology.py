"""
Handles (deferred) loading of terminology data and access to it
for odML documents
"""

import datetime
import os
import sys
import tempfile
import threading
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

from hashlib import md5

from .tools.parser_utils import ParserException
from .tools.xmlparser import XMLReader


REPOSITORY_BASE = 'http://portal.g-node.org/odml/terminologies'
REPOSITORY = '/'.join([REPOSITORY_BASE, 'v1.1', 'terminologies.xml'])

CACHE_AGE = datetime.timedelta(days=1)


def cache_load(url):
    """
    Load the url and store it in a temporary cache directory
    subsequent requests for this url will use the cached version
    """
    filename = '.'.join([md5(url.encode()).hexdigest(), os.path.basename(url)])
    cache_dir = os.path.join(tempfile.gettempdir(), "odml.cache")
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir)
        except OSError:  # might happen due to concurrency
            if not os.path.exists(cache_dir):
                raise
    cache_file = os.path.join(cache_dir, filename)
    if not os.path.exists(cache_file) \
       or datetime.datetime.fromtimestamp(os.path.getmtime(cache_file)) < \
       datetime.datetime.now() - CACHE_AGE:
        try:
            data = urllib2.urlopen(url).read()
            if sys.version_info.major > 2:
                data = data.decode("utf-8")
        except Exception as e:
            print("failed loading '%s': %s" % (url, e))
            return
        fp = open(cache_file, "w")
        fp.write(str(data))
        fp.close()
    return open(cache_file)


class Terminologies(dict):
    loading = {}

    def load(self, url):
        """
        Load and cache a terminology-url

        Returns the odml-document for the url
        """
        if url in self:
            return self[url]

        if url in self.loading:
            self.loading[url].join()
            self.loading.pop(url, None)
            return self.load(url)

        return self._load(url)

    def _load(self, url):
        # TODO also cache the data locally on disk
        # if url.startswith("http"): return None
        fp = cache_load(url)
        if fp is None:
            print("did not successfully load '%s'" % url)
            return
        try:
            term = XMLReader(filename=url, ignore_errors=True).from_file(fp)
            term.finalize()
        except ParserException as e:
            print("Failed to load %s due to parser errors" % url)
            print(' "%s"' % e)
            term = None
        self[url] = term
        return term

    def deferred_load(self, url):
        """
        Start a thread to load the terminology in background
        """
        if url in self or url in self.loading:
            return
        self.loading[url] = threading.Thread(target=self._load, args=(url,))
        self.loading[url].start()


terminologies = Terminologies()
load = terminologies.load
deferred_load = terminologies.deferred_load


if __name__ == "__main__":
    f = cache_load(REPOSITORY)
