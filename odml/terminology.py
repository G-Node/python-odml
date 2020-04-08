"""
Handles (deferred) loading of terminology data and access to it for odML documents.
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


REPOSITORY_BASE = 'https://terminologies.g-node.org'
REPOSITORY = '/'.join([REPOSITORY_BASE, 'v1.1', 'terminologies.xml'])

CACHE_AGE = datetime.timedelta(days=1)


def cache_load(url, replace_file=False):
    """
    Loads the url and store it in a temporary cache directory
    subsequent requests for this url will use the cached version.

    :param url: URL from where to load an odML terminology file from.
    :param replace_file: True, if file should be reloaded
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
    if replace_file and os.path.exists(cache_file):
        os.remove(cache_file)
    if not os.path.exists(cache_file) \
            or replace_file \
            or datetime.datetime.fromtimestamp(os.path.getmtime(cache_file)) < \
            datetime.datetime.now() - CACHE_AGE:
        try:
            data = urllib2.urlopen(url).read()
            if sys.version_info.major > 2:
                data = data.decode("utf-8")
        except Exception as exc:
            print("failed loading '%s': %s" % (url, exc))
            return

        file_obj = open(cache_file, "w")
        file_obj.write(str(data))
        file_obj.close()

    return open(cache_file)


class Terminologies(dict):
    """
    Terminologies facilitates synchronous and deferred loading, caching,
    browsing and importing of full or partial odML terminologies.
    """
    loading = {}
    reload_cache = False

    def load(self, url):
        """
        Loads and caches an odML XML file from a URL.

        :param url: location of an odML XML file.
        :return: The odML document loaded from url.
        """
        if url in self:
            return self[url]

        if url in self.loading:
            self.loading[url].join()
            self.loading.pop(url, None)
            return self.load(url)

        return self._load(url)

    def _load(self, url):
        """
        Cache loads an odML XML file from a URL and returns
        the result as a parsed odML document.

        :param url: location of an odML XML file.
        :return: The odML document loaded from url.
                 It will silently return None, if any exceptions
                 occur to enable loading of nested odML files.
        """
        file_obj = cache_load(url, self.reload_cache)
        if file_obj is None:
            print("did not successfully load '%s'" % url)
            return
        try:
            term = XMLReader(filename=url, ignore_errors=True).from_file(file_obj)
            term.finalize()
        except ParserException as exc:
            print("Failed to load %s due to parser errors" % url)
            print(' "%s"' % exc)
            term = None
        self[url] = term
        return term

    def deferred_load(self, url):
        """
        Starts a background thread to load an odML XML file from a URL.

        :param url: location of an odML XML file.
        """
        if url in self or url in self.loading:
            return
        self.loading[url] = threading.Thread(target=self._load, args=(url,))
        self.loading[url].start()

    def refresh(self, url):
        """
        Deletes and reloads all cached odML XML files given in the
        terminology file from a URL.

        :param url: location of an odML XML file.
        """
        self.reload_cache = True
        self.clear()
        self.load(url)
        self.reload_cache = False


terminologies = Terminologies()
load = terminologies.load
deferred_load = terminologies.deferred_load
refresh = terminologies.refresh


if __name__ == "__main__":
    FILE_OBJECT = cache_load(REPOSITORY)
