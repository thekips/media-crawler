import json
import requests
import yaml
import os
import time
from jsonpath import jsonpath

ID_URL = 'https://i.instagram.com/api/v1/users/web_profile_info/'
QUERY_URL = 'https://i.instagram.com/api/v1/feed/user/%s/username/?count=12'
MEDIA_URL = 'https://i.instagram.com/api/v1/feed/user/%s/'

def mkDir(path):
    if(not os.path.exists(path)):
        try:
            os.makedirs(path)
        except Exception as e:
            print(e)

class Instgram:
    
    def __init__(self, screen_id):
        with open('config.yaml', 'r', encoding='utf-8') as f:
            self.headers = yaml.safe_load(f)
        self.rest_id = self.getRestID(screen_id)
        self.screen_id = screen_id
        self.cursor = ''
        self.pic_path = 'data/' + screen_id + '/img/'
        self.video_path = 'data/' + screen_id + '/video/'

    def getRestID(self, screen_id):
        headers = {
        'x-ig-app-id': '936619743392459',
        }

        params = {
            'username': screen_id,
        }

        try:
            response = requests.get(ID_URL, params=params, headers=headers)
            if response.status_code == 200:
                response = response.json()
                return response['data']['user']['id']
            else:
                print('request error, the response error code is: ', response.status_code)
        except Exception as e:
            print(e)
            return None

    def get_media_urls(self, cursor):
        headers = {
            'x-ig-app-id': '936619743392459',
        }


        try:
            if cursor == '':
                response = requests.get(QUERY_URL % self.screen_id, headers=headers)
            else:
                params = {
                    'count': '12',
                    'max_id': cursor,
                }
                response = requests.get(MEDIA_URL % self.rest_id, params=params, headers=headers)

            if(response.status_code == 200):
                response = json.dumps(response.json(), sort_keys=True)
                return json.loads(response)
            else:
                print('request error in get_media(), the response error code is: ', response.status_code)

        except Exception as e:
            print(e)
    
    def getMax(self, candidates):
        max_urls = []
        for candidate in candidates:
            max_height = 0
            max_url = ''

            for pic in candidate:
                if pic['height'] > max_height:
                    max_height = pic['height']
                    max_url = pic['url']
            max_urls.append(max_url)

        return max_urls

    def scrawlMedia(self):
        mkDir(self.pic_path)
        mkDir(self.video_path)

        while self.cursor != 'END':
            response = self.get_media_urls(self.cursor)
            pic_candidates = jsonpath(response, expr='$.items.[*].image_versions2.candidates')
            video_candidates = jsonpath(response, expr='$.items.[*].video_versions')

            #get max resolution
            if pic_candidates:
                pic_urls = self.getMax(pic_candidates)
            if video_candidates:
                video_urls = self.getMax(video_candidates )
            
            #download media
            if pic_urls:
                for url in pic_urls: self.dlPic(url)
            if video_urls:
                for url in video_urls: self.dlVideo(url)

            #upgrade cursor
            self.cursor = response['next_max_id'] if response['more_available'] == True else 'END'

    def dlPic(self, url):
        if url == '':
            return

        try:
            pic_name = url[url.rfind('/') + 1 : url.rfind('?')]
            path_to_file = self.pic_path + '/' + pic_name
            if os.path.exists(path_to_file): return

            pic = requests.get(url)
            if pic:
                print(pic_name)
                with open(path_to_file, 'wb') as f:
                    f.write(pic.content)
        except:
            print('try download the picture again...')
            self.dlPic(url)
        

    def dlVideo(self, url):
        try:
            video_name = url[url.rfind('/') + 1 : url.rfind('?')]
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

if __name__ == '__main__':
    screen_id = input('Please input instgram id of the user:')
    instgram = Instgram(screen_id)

    start_time = time.time()
    instgram.scrawlMedia()
    end_time = time.time()

    print("All finished in %ds!" % (end_time-start_time))
    os.system('pause')
