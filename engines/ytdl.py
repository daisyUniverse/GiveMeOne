from engines import searchobject
from youtube_dl import YoutubeDL
from requests import get

options = {'format': 'bestaudio', 'noplaylist':'True'}

def searchyoutube(term, config):
    with YoutubeDL(options) as ydl:
        try:
            video = ydl.extract_info(f"ytsearch:{term}", download=False)['entries'][0]
        except:
            return None
    
    result_url = "https://youtu.be/" + video['id']
    print("Found result for " + term.replace("-"," ") + " using YTDL: " + video['title'])
    gso = searchobject.genGSO(term, video['title'], "context", result_url,'youtube')
    return gso