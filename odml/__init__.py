import doc, property, section, value

def Value(*args, **kwargs):
    return value.Value(*args, **kwargs)

def Property(*args, **kwargs):
    return property.Property(*args, **kwargs)

def Section(*args, **kwargs):
    return section.Section(*args, **kwargs)
    
def Document(*args, **kwargs):
    return doc.Document(*args, **kwargs)
