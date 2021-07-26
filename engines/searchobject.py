
# This is the module responsible for managing search objects
def genGSO(term, title="", context="", url=""):
    
    gso = {
        "term": term,
        "title": title,
        "context": context,
        "url": url
    }

    return gso