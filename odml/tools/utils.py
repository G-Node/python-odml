import copy

RDFConversionFormats = {
    # rdflib version "4.2.2" serialization formats
    'xml': '.rdf',
    'pretty-xml': '.rdf',
    'trix': '.rdf',
    'n3': '.n3',
    'turtle': '.ttl',
    'ttl': '.ttl',
    'ntriples': '.nt',
    'nt': '.nt',
    'nt11': '.nt',
    'trig': '.trig',
    'json-ld': '.jsonld'
}

ConversionFormats = copy.deepcopy(RDFConversionFormats)
ConversionFormats.update({
    'v1_1': '.xml',
    'odml': '.odml'
})
