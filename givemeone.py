from flask import Flask, render_template, redirect, request
import textwrap
import requests
import pymongo
import json
import re
import os

app = Flask(__name__)
discord_user_agents = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0", "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)"]
telegram_user_agents = ["TelegramBot (like TwitterBot)"]

# Read config from config.json. If it does not exist, create new.
if not os.path.exists("config.json"):
    with open("config.json", "w") as outfile:
        default_config = {"config":{"engine":"hybrid","database":"","link_cache":"json","database":"","color":"#43B581", "appname": "GiveMeOne", "repo": "https://github.com/robinuniverse/givemeone", "url": "https://giveme.one"},"api":{"api_key":""}}
        json.dump(default_config, outfile, indent=4, sort_keys=True)

    config = default_config
    print("You are currently using default configs, you will need to close and app an API key to the config file")
else:
    f = open("config.json")
    config = json.load(f)
    f.close()

# Check to see what link caching system the user wants, and do the setup appropriate for that
link_cache_system = config['config']['link_cache']
if link_cache_system == "json":
    link_cache = {}
    if not os.path.exists("links.json"):
        with open("links.json", "w") as outfile:
            default_link_cache = {"test":"test"}
            json.dump(default_link_cache, outfile, indent=4, sort_keys=True)

    f = open('links.json',)
    link_cache = json.load(f)
    f.close()
elif link_cache_system == "db":
    client = pymongo.MongoClient(config['config']['database'], connect=False)
    db = client.GiveMeOne

# Site without any arguments
@app.route('/') 
def default():
    user_agent = request.headers.get('user-agent')
    if user_agent in discord_user_agents:
        return message("GiveMeOne is a shortcut to help make googling images a bit easier")
    else:
        return redirect(config['config']['repo'], 301)

# Main function
@app.route('/<term>') 
def givemeone(term):
    return search(term)

# Duck Duck Go function
@app.route('/ddg/<term>') 
def duckduckgo(term):
    return search(term, engine='ddg')

# Sends a simple embed with a message
def message(text): 
    return render_template('default.html', message=text, color=config['config']['color'], appname=config['config']['appname'], repo=config['config']['repo'], url=config['config']['url'])

# Attempts to return a render template from a search term by searching the link cache, or adding a new entry if one is not found
def search(term, engine=config['config']['engine']): 
    cached_gso = get_gso_from_link_cache(term)

    if cached_gso == None:
        if engine == 'hybrid':
            try:
                gso = google(term)
                add_gso_to_link_cache(gso)
                return redirect(gso['url'], 301)

            except Exception as e:
                print(e)
                gso = ddg(term)
                add_gso_to_link_cache(gso)
                return redirect(gso['url'], 301)
        elif engine == 'google':
            try:
                gso = google(term)
                add_gso_to_link_cache(gso)
                return redirect(gso['url'], 301)
            except Exception as e:
                print(e)
                return message('Google API quota has been reached for the day!')
        elif engine == 'ddg':
            try:
                gso = ddg(term)
                add_gso_to_link_cache(gso)
                return redirect(gso['url'], 301)
            except Exception as e:
                print(e)
                return message('DuckDuckGo failed to respond!')

    else:
            return redirect(cached_gso['url'], 301)

# Asks the Google API for an image, returns a GSO if found (None if not)
def google(term): 
    if config['api']['api_key'] == "":
        print("The Google API key is not set.")
        return message("The Google API key is not set.")

    try:
        search_url = "https://www.googleapis.com/customsearch/v1?key={}&cx=016079215605992494498:z4taegakbcc&searchType=image&q={}".format(config['api']['api_key'],term.replace('-','+'))
        search_data = requests.get(search_url).json()
        if 'error' in search_data:
            raise KeyError("error!")
    except KeyError:
        print("Your API key has reached it's quota")
        return None
    
    search_error = 0
    while True:
        if search_error == 3:
            break

        try:
            search_result = search_data['items'][0 + int(search_error)]
        except KeyError:
            print("No image found!")
            return None

        try:
            search_url = search_result['link']
            break
        except:
            search_error += 1
            continue

    if search_error == 3:
        print("Search failed")
        return None
    else:
        gso = genGSO(term, search_result['title'], search_result['image']['contextLink'], search_url)
        print('Google image result for ' + gso['term'].replace('-',' ') + ' found!')
        return gso

# Try to get a GSO from the link cache
def get_gso_from_link_cache(term):
    if link_cache_system == "db":
        collection = db.linkCache
        gso = collection.find_one({'term': term})
        if gso != None: 
            print("Link located in DB cache")
            return gso
        else:
            print("Link not in DB cache")
            return None
    elif link_cache_system == "json":
        if term in link_cache:
            print("Link located in json cache")
            gso = link_cache[term]
            return gso
        else:
            print("Link not in json cache")
            return None

# Add a GSO to the Link Cache
def add_gso_to_link_cache(gso):
    if link_cache_system == "db":
        try:
            out = db.linkCache.insert_one(gso)
            print("Link added to DB cache")
            return True
        except Exception:
            print("Failed to add link to DB cache")
            return None
    elif link_cache_system == "json":
        link_cache[gso['term']] = gso
        with open("links.json", "w") as outfile: 
            json.dump(link_cache, outfile, indent=4, sort_keys=True)
            print("Link added to JSON cache")
            return None

# Generate a Google Search Object
def genGSO(term, title="", context="", url=""):
    
    gso = {
        "term": term,
        "title": title,
        "context": context,
        "url": url
    }

    return gso

# Search DuckDuckGo for an image
# Code adapted from https://github.com/deepanprabhu/duckduckgo-images-api/
def ddg(term):
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
    gso = genGSO(term, data["results"][0]["title"].encode('utf-8'), data["results"][0]["url"], data["results"][0]["image"])
    return gso


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
