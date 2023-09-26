from engines import searchobject
import requests
import json
import re

# Search Wikipedia
def searchwikipedia(term, config):
    search_url = "https://en.wikipedia.org/w/api.php?action=opensearch&search={}&limit=1".format(term.replace("-","_"))
    search_data = requests.get(search_url).json()
    try:
        url = search_data[3][0]
        gso = searchobject.genGSO(term, "title", "context", url, "wiki")
        return gso
    except IndexError:
        return None

# Search the Arch Wiki
def searcharchwiki(term, config):
    search_url = "https://wiki.archlinux.org/api.php?action=opensearch&export&search={}&limit=1".format(term.replace("-","_"))
    search_data = requests.get(search_url).json()
    try:
        url = search_data[3][0]
        gso = searchobject.genGSO(term, "title", "context", url, "arch")
        return gso
    except IndexError:
        return None

# This bit of code is cursed till I can figure out how to interpret it
def searchmcwiki(term, config):
    search_url = "https://minecraft.wiki/w/api.php?action=opensearch&export&search={}&limit=1".format(term.replace("-","_"))
    search_data = requests.get(search_url).text
    
    print(search_data)
    try:
        url = re.findall(r'(https?://[^\s]+)', search_data)[0]
        print(url)
        gso = searchobject.genGSO(term, "title", "context", url, "minecraft")
        return gso
    except IndexError:
        return None

# Just gives back a link to an SCP - Will make it do a fancy embed soon
def scpwiki(term, config):
    url = "http://scp-wiki.net/scp-" + term.replace("-","_")
    gso = searchobject.genGSO(term, "title", "context", url, "scp")
    return gso

# Search urban dictionary. Kinda stretching the definition of Wiki, but whatever
def searchurban(term, config):
    search_url = "http://api.urbandictionary.com/v0/define?term=" + term.replace("-","%20")
    search_data = requests.get(search_url).json()
    try:
        url = search_data['list'][0]['permalink']
        gso = searchobject.genGSO(term, "title", "context", url, "urban")
        return gso
    except IndexError:
        return None

# Search the dictionary
def searchdict(term, config):
    search_url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/" + term.replace("-","%20") + config['api']['dictionary']
    search_data = requests.get(search_url).json()
    try:
        url = "> "+"\n> ".join(search_data[0]['shortdef'])
        gso = searchobject.genGSO(term, "title", "context", url, "dict")
        return gso
    except IndexError:
        return None