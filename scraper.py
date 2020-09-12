import requests
import time
from bs4 import BeautifulSoup
import re
import json
import api
import db
import cfg

def scrapeCatalog():
    catalog = requests.get(cfg.catalogURL)
    text = (str)(catalog.content)
    script = re.search(r"\"threads\":(.*),\"count\"",text)
    cat = json.loads(script.group(1))
    ret = []
    for tid in cat:
        for trig in cfg.triggers:
            if(trig.lower() in cat[tid]['teaser'].lower() or trig.lower() in cat[tid]['sub'].lower()):
                ret.append(tid)
                break

    return ret

def scrapeThread(tID):
    print("scrape thread", tID)
    videos = []
    page = requests.get(cfg.baseURL+tID)
    soup = BeautifulSoup(page.content, 'html.parser')
    replies = soup.find_all("div", class_='replyContainer')
    for r in replies:
        date = r.find("span", class_="dateTime").attrs.get("data-utc")
        pid = r.attrs.get("id")
        pid = re.search(r"pc([0-9]*)",pid)
        pid = pid.group(1)
        
        text = (str)(r.text)
        find = re.findall(r"youtube\.com\/watch\?v=([a-zA-Z0-9\-\_]{11})", text)
        find += re.findall(r"youtu\.be\/([a-zA-Z0-9\-\_]{11})", text)
        if(len(find)>0):
            print("find: ", find)
        for yt in find:
            a = {'tid':tID, 'pid':pid, 'yt':yt, 'date':date}
            videos.append(a)

    return videos

def main(api):
    threads = scrapeCatalog()
    videos = []
    print("threads:",threads)
    for thread in threads:
        videos += scrapeThread(thread)
    
    videos = sorted(videos, key = lambda x:x['date'])
    for video in videos:
        new = db.insertVideo(video)
        if(new):
            api.add(video['yt'])
            print("added", video)

if __name__ == "__main__":
    db.createTables()
    api = api.Api(cfg.client_secrets_file, cfg.scopes, cfg.oauth_file, cfg.playlist_name)
    while True:
        try:
            main(api)
        except:
            pass
        time.sleep(300)