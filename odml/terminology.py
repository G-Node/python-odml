"""
Handles (deferred) loading of terminology data and access to it
for odML documents
"""
import tools.xmlparser

import urllib
import threading

class Terminologies(dict):
    loading = {}

    def load(self, url):
        """
        load and cache a terminology-url

        returns the odml-document for the url
        """
        if url in self:
            return self[url]

        if url in self.loading:
            self.loading[url].join()
            del self.loading[url]
            return self.load(url)

        return self._load(url)

    def _load(self, url):
        # TODO also cache the data locally on disk
        # if url.startswith("http"): return None
        fp = urllib.urlopen(url)
        term = tools.xmlparser.parseXML(fp)
        self[url] = term
        return term

    def deferred_load(self, url):
        """
        start a thread to load the terminology in background
        """
        if url in self or url in self.loading: return
        self.loading[url] = threading.Thread(target=self._load, args=(url,))
        self.loading[url].start()

terminologies = Terminologies()
load = terminologies.load
deferred_load = terminologies.deferred_load
