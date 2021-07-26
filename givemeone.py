import sys
sys.dont_write_bytecode = True

from flask import Flask, render_template, redirect, request
from engines import google, ddg
import configinit
import textwrap
import requests
import pymongo
import json
import re
import os


app = Flask(__name__)
discord_user_agents = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0", "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)"]
telegram_user_agents = ["TelegramBot (like TwitterBot)"]
engines = [ "google", "ddg", "yt" ]

config = configinit.getConfig()

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

# Specify Engine
@app.route('/<engine>/<term>') 
def engine(term, engine):
    if engine in engines:
        return search(term, engine=engine)
    else:
        return message(engine + " is not a valid search engine... yet!")

# Sends a simple embed with a message
def message(text): 
    return render_template('default.html', message=text, color=config['config']['color'], appname=config['config']['appname'], repo=config['config']['repo'], url=config['config']['url'])

# Attempts to return a render template from a search term by searching the link cache, or adding a new entry if one is not found
def search(term, engine=config['config']['engine']): 
    cached_gso = get_gso_from_link_cache(term)

    if cached_gso == None:
        if engine == 'hybrid':
            try:
                gso = google.searchimages(term, config)
                add_gso_to_link_cache(gso)
                return redirect(gso['url'], 301)

            except Exception as e:
                print(e)
                gso = ddg.searchimages(term, config)
                add_gso_to_link_cache(gso)
                return redirect(gso['url'], 301)
        elif engine == 'google':
            try:
                gso = google.searchimages(term, config)
                add_gso_to_link_cache(gso)
                return redirect(gso['url'], 301)
            except Exception as e:
                print(e)
                return message('Google API quota has been reached for the day!')
        elif engine == 'ddg':
            try:
                gso = ddg.searchimages(term, config)
                add_gso_to_link_cache(gso)
                return redirect(gso['url'], 301)
            except Exception as e:
                print(e)
                return message('DuckDuckGo failed to respond!')

    else:
            return redirect(cached_gso['url'], 301)

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
