from engines import searchobject
import requests

# Asks the Google API for an image, returns a GSO if found (None if not)
def searchimages(term, config): 
    if config['api']['api_key'] == "":
        print("The Google Custom Search API key is not set.")
        return None

    try:
        search_url = "https://www.googleapis.com/customsearch/v1?key={}&cx=016079215605992494498:z4taegakbcc&searchType=image&q={}".format(config['api']['api_key'],term.replace('-','+'))
        search_data = requests.get(search_url).json()
        if 'error' in search_data:
            raise KeyError("Error!")
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
        gso = searchobject.genGSO(term, search_result['title'], search_result['image']['contextLink'], search_url, "image")
        print('Google image result for ' + gso['term'].replace('-',' ') + ' found!')
        return gso

def searchyoutube(term, config):
    if config['api']['api_key'] == "":
        print("The Google Custom Search API key is not set")
        return None

    try:
        print("Searching Youtube for '" + term.replace("-"," ") + "'")
        search_url = "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={}&type=video&key={}".format(term.replace('-','+'), config['api']['api_key'])
        search_data = requests.get(search_url).json()
        if 'error' in search_data:
            raise KeyError("Error!")
    except KeyError:
        print("Your Google Custome Search API key has met its quota")
        return None

    print("Found result: '" + search_data['items'][0]['snippet']['title'] + "'")
    result_url = "https://youtu.be/" + search_data['items'][0]['id']['videoId']
    title = search_data['items'][0]['snippet']['title']
    gso = searchobject.genGSO(term, title, "context", result_url, "youtube")
    return gso