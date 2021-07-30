import json
from jsonpath import jsonpath
import os
import re
import requests
import time
import yaml

ID_URL = 'https://twitter.com/i/api/graphql/hc-pka9A7gyS3xODIafnrQ/UserByScreenName'
MEDIA_URL = 'https://twitter.com/i/api/2/timeline/media/%s.json'

def mkDir(path):
    if not os.path.exists(path):
        os.makedirs(path)

class Twitter:
    
    def __init__(self, screen_id):
        with open('config.yaml', 'r', encoding='utf-8') as f:
            self.headers = yaml.safe_load(f)
        self.rest_id = self.getRestID(screen_id)
        self.cursor = ''
        self.pic_path = 'data/' + screen_id + '/img/'
        self.video_path = 'data/' + screen_id + '/video/'

    def dlPic(self, url):
        try:
            pic_name = url[url.rfind('/')+1:]
            path_to_file = self.pic_path + '/' + pic_name
            if os.path.exists(path_to_file): return

            pic = requests.get(url + '?name=large')
            if pic:
                print(pic_name)
                with open(path_to_file, 'wb') as f:
                    f.write(pic.content)
        except:
            print('try download the picture again...')
            self.dlPic(url)
        

    def dlVideo(self, url):
        try:
            video_name = url[url.rfind('/') + 1 :]
            path_to_file = self.video_path + '/' + video_name
            if os.path.exists(path_to_file): return

            video = requests.get(url)
            if video:
                print(video_name)
                with open(path_to_file, 'wb') as f:
                    f.write(video.content)
        except:
            print('try download the video again...')
            self.dlVideo(url)


    def getRestID(self, screen_id):
        params = (
            ('variables', '{"screen_name":"%s","withHighlightedLabel":true}' % screen_id),
        )

        response = requests.get(ID_URL, headers=self.headers, params=params)
        content = json.loads(response.text)
        
        return content["data"]["user"]["rest_id"]

    def getMedia(self):
        params = (
            ('cursor', '{}'.format(self.cursor)), 
        )
        if self.cursor == '':
            self.res = requests.get(MEDIA_URL % self.rest_id, headers=self.headers)
        else:
            self.res = requests.get(MEDIA_URL % self.rest_id, headers=self.headers, params=params)

    def scrawlMedia(self):
        
        mkDir(self.pic_path)
        mkDir(self.video_path)
        
        cursor = '#'
        while cursor != self.cursor:
            
            # handing the response and get links of videos and pictures
            self.getMedia()
            res = json.loads(self.res.text)
            res = json.loads(json.dumps(res, sort_keys=True, ensure_ascii=False))
            tweets = res['globalObjects']['tweets']
            pic_urls = jsonpath(tweets, expr='$.[*].entities.media.[*].media_url_https')
            video_urls = jsonpath(tweets, expr='$.[*].extended_entities.media.[*].video_info.variants[0].url')

            # download picture
            if pic_urls:
                for url in pic_urls: self.dlPic(url)
            
            # download video
            if video_urls:
                for url in video_urls: self.dlVideo(url)
                
            # upgrade cursor
            cursor = self.cursor
            self.cursor = res['timeline']['instructions'][0]['addEntries']['entries'][-1]['content']['operation']['cursor']['value']

if __name__ == '__main__':
    screen_id = input('Please input twitter id of the user: ')
    twitter = Twitter(screen_id)

    start_time = time.time()
    twitter.scrawlMedia()
    end_time = time.time()

    print("All finished in %ds!" % (end_time-start_time))
    os.system('pause')
