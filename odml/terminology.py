"""
Handles (deferred) loading of terminology data and access to it
for odML documents
"""

import os
import tempfile
import datetime
import odml.tools.xmlparser
from hashlib import md5
py3 = True
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen
import threading

CACHE_AGE = datetime.timedelta(days=14)
CACHE_DIR = os.path.join(tempfile.gettempdir(), "odml.cache")
FILE_MAP_FILE = os.path.join(CACHE_DIR, "odml_filemap.csv")

if not os.path.exists(CACHE_DIR):
    try:
        os.makedirs(CACHE_DIR)
    except OSError:  # might happen due to concurrency
        if not os.path.exists(CACHE_DIR):
            raise


def open_file_map():
    """
    Opens the file_map file stored in the cache that maps the filenames to the urls of the 
    respective terminolgies.
    """
    file_map = {}
    if not os.path.exists(FILE_MAP_FILE):
       return file_map
    else:
        with open(FILE_MAP_FILE, 'r') as f:
            for l in f.readlines():
                parts = l.strip().split(';')
                file_map[parts[0].strip()] = parts[1].strip()
    return file_map


def cache_load(url):
    """
    Load the url and store it in a temporary cache directory
    subsequent requests for this url will use the cached version
    """
    filename = md5(url.encode()).hexdigest() + '__' + os.path.basename(url)
    cache_file = os.path.join(CACHE_DIR, filename)

    if not os.path.exists(cache_file) \
       or datetime.datetime.fromtimestamp(os.path.getmtime(cache_file)) < \
       datetime.datetime.now() - CACHE_AGE:
        try:
            data = urlopen(url).read().decode("utf-8")
        except Exception as e:
            print("Failed loading '%s': %s" % (url, e))
            return
        fp = open(cache_file, "w")
        fp.write(data)
        fp.close()
        with open(FILE_MAP_FILE, 'a') as fm:
            fm.write(filename + "; " + url + "\n")
    return open(cache_file)


def cached_files():
    """
    Returns a list of all locally cached files.
    """
    filelist = [ f for f in os.listdir(CACHE_DIR) if \
                 (f.endswith(".xml") and os.path.isfile(os.path.join(CACHE_DIR, f)))]
    return filelist


def show_cache():
    """
    Show all locally cached files. Just for display.
    """
    print("terminology %s \t updated"%(19*" "))
    print(60*"-")
    files = cached_files()
    for f in files:
        cache_file = os.path.join(CACHE_DIR, f)
        file_timestamp = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file))
        disp_name = '_'.join(f.split('__')[1:])
        if len(disp_name) > 30:
            disp_name = disp_name[:16] + "..."
        if len(disp_name) < 30:
            disp_name = disp_name + (30 -len(disp_name)) * " "
        print(" %s \t %s"%(disp_name, file_timestamp))


def clear_cache():
    """
    Clears the cache, i.e. deletes all locally stored files. Does not remove the cache folder, though.
    """
    filelist = cached_files();
    for f in filelist:
        os.remove(os.path.join(CACHE_DIR, f))
    if os.path.exists(FILE_MAP_FILE):
        os.remove(FILE_MAP_FILE)


def from_cache(term):
    """
    Fills the terminology with the definitions stored in the cache.
    """
    assert isinstance(term, Terminologies)
    file_list = cached_files();
    file_map = open_file_map();
    for f in file_map:
        if file_map[f] not in term:
            term.load(file_map[f])


class Terminologies(dict):
    loading = {}
    types = None

    def load(self, url="http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml"):
        """
        load and cache a terminology-url

        returns the odml-document for the url
        """
        if url in self:
            return self[url]

        encode_name =  md5(url.encode()).hexdigest() + '__' + os.path.basename(url)
        if encode_name in self:
            return self[encode_name]

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
            print("Did not successfully load '%s'" % url)
            return
        try:
            term = odml.tools.xmlparser.XMLReader(filename=url, ignore_errors=True).fromFile(fp)
            term.finalize()
        except odml.tools.xmlparser.ParserException as e:
            print("Failed to load %s due to parser errors" % url)
            print(' "%s"' % e)
            term = None
        self[url] = term
        return term

    def deferred_load(self, url):
        """
        start a thread to load the terminology in background
        """
        if url in self or url in self.loading:
            return
        self.loading[url] = threading.Thread(target=self._load, args=(url,))
        self.loading[url].start()

    def empty(self):
        """
        Tells whether there are no terminolgies stored.
        """
        return len(self) == 0

    def type_list(self):
        """
        returns a dict of all types stored in the cache together with the terminologies it is defined in.
        """
        if self.empty():
            from_cache(self)
        if not self.types:
            self.types = {}
            for k in self.items():
                for s in k[1].itersections():
                    if s.type in self.types:
                        self.types[s.type].append((k[0], s.get_path()))
                    else:
                        self.types[s.type] = [(k[0], s.get_path())]
        return self.types

    def _compare_repo(self, candidate_repo, candidate_path, pattern, relaxed):
        parts = pattern.lower().split()
        match = True
        repo = candidate_repo.lower()
        path = candidate_path.lower()
        for p in parts:
            if p.startswith("!"):
                if relaxed:
                    match = match or (p[1:] not in repo.lower() and p[1:] not in path)
                else:
                    match = match and (p[1:] not in repo and p[1:] not in path)
            else:
                if relaxed:
                    match = match or (p in repo or p in path)
                else:
                    match = match and (p in repo or p in path)
        return match

    def _find_match(self, type_matches, pattern, relaxed=False):
        if pattern:
            matches = []
            for i, (r, p) in enumerate(type_matches):
                if self._compare_repo(r, p, pattern, relaxed):
                    matches.append(type_matches[i])
            return matches
        else: # simply return first
            return type_matches
        return []

    def _get_section_by_type(self, section_type, pattern=None, relaxed=False, find_all=False):
        if self.empty() or len(self.types) == 0:
            self.type_list()
        matches = []
        if section_type in self.types:
            matches = self._find_match(self.types[section_type], pattern, relaxed)
        if len(matches) > 0:
            if len(matches) > 1 and find_all:
                sections = []
                for m in matches:
                    sections.append(self[m[0]].get_section_by_path(m[1]).clone())
                return sections
            else:
                return self[matches[0][0]].get_section_by_path(matches[0][1]).clone()
        else:
            return None


terminologies = Terminologies()
load = terminologies.load
deferred_load = terminologies.deferred_load


def get_section_by_type(section_type, pattern=None, relaxed=False, find_all=False):
    """
    Finds a section type in the cached repositories and returns it.

    @param section_type  the type of the section must be a valid full match. Returns the
                         first match.
    @param pattern       a optional filter pattern, i.e. a string with characteristics
                         regarding the repository the section should originate from
                         and its path in the file (see below)
    @param relaxed       optional, defines whether all criteria must be met or not.
    @param find_all      optional, sets whether all possible matches are returned

    @return  Section or list of sections depending on the find_all parameter, None,
                         if no match was found.

    Example:
    Suppose we are looking for a section type 'analysis' and it should be from the g-node
    terminologies.
    s = get_section_by_type("analysis", "g-node")
    print(s)
    <Section Analysis[analysis] (0)>
    If we want to exclude the g-node terminologies, simply put an ! in front of the pattern
    s = get_section_by_type("analysis", "!g-node")

    Multiple criteria can be combined (e.g. get_section_by_type("setup/daq", "g-node blackrock !cerebus")).
    The relaxed parameter controls whether all criteria have to match.
    """
    return terminologies._get_section_by_type(section_type, pattern, relaxed, find_all)

def find_definitions(section_type):
    """
    Finds repositories that define the provided section type.

    @param section_type   the requested section type

    @return  list of tuples containing the repository and the path at which the respective
             section can be found. List may be empty.
    """
    tl = terminologies.type_list()
    if section_type in tl:
        return tl[section_type]
    else:
        return []

if __name__ == "__main__":
    from IPython import embed
    print ("Terminologies!")
    from_cache(terminologies)
    # t.load('http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml')
    # t.load('http://portal.g-node.org/odml/terminologies/v1.0/analysis/power_spectrum.xml')
    find_definitions("analysis")
    embed()
