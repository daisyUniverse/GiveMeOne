from engines import searchobject
import requests
import json
import re

# Search DuckDuckGo for an image
# Code adapted from https://github.com/deepanprabhu/duckduckgo-images-api/
def searchimages(term, config):
    url = 'https://duckduckgo.com/'
    params = { 'q': term }
    print("Hitting DuckDuckGo for Token")
    res = requests.post(url, data=params)
    searchObj = re.search(r'vqd=([\d-]+)\&', res.text, re.M|re.I)

    if not searchObj:
        print("Token Parsing Failed !")
        return -1

    print("Obtained Token")
    headers = {
        'authority': 'duckduckgo.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'sec-fetch-dest': 'empty',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'referer': 'https://duckduckgo.com/',
        'accept-language': 'en-US,en;q=0.9',
    }

    params = (
        ('l', 'us-en'),
        ('o', 'json'),
        ('q', term),
        ('vqd', searchObj.group(1)),
        ('f', ',,,'),
        ('p', '1'),
        ('v7exp', 'a'),
    )

    requestUrl = url + "i.js"
    print("Hitting Url : %s", requestUrl)

    try:
        res = requests.get(requestUrl, headers=headers, params=params)
        data = json.loads(res.text)
    except ValueError as e:
        print("Hitting Url Failure - Sleep and Retry: %s", requestUrl)

    print("Hitting Url Success : %s", term)
    gso = searchobject.genGSO(term, data["results"][0]["title"].encode('utf-8'), data["results"][0]["url"], data["results"][0]["image"], "image")
    return gso