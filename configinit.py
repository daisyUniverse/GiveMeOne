import os
import json

# Read config from config.json. If it does not exist, create new.
def getConfig():
    if not os.path.exists("config.json"):
        with open("config.json", "w") as outfile:
            default_config = {
                "config":{
                    "engine":"hybrid",
                    "database":"",
                    "link_cache":"json",
                    "database":"",
                    "color":"#43B581", 
                    "appname": "GiveMeOne", 
                    "repo": "https://github.com/robinuniverse/givemeone", 
                    "url": "https://giveme.one"},
                    "api":{
                        "api_key":"",
                        "dictionary":""
                        }
                    }
            json.dump(default_config, outfile, indent=4, sort_keys=True)

        config = default_config
        print("You are currently using default configs, you will need to close and app an API key to the config file")
        return config
    else:
        f = open("config.json")
        config = json.load(f)
        f.close()
        return config