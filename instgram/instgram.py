import requests
import yaml
import os
import time
from jsonpath import jsonpath

ID_URL = 'https://www.instagram.com/%s/'
MEDIA_URL = 'https://www.instagram.com/graphql/query/'

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
        self.cursor = ''
        self.pic_path = 'data/' + screen_id + '/img/'
        self.video_path = 'data/' + screen_id + '/video/'

    def getRestID(self, screen_id):
        params = (
            ('__a', '1'),
        )
        try:
            response = requests.get(ID_URL % screen_id, headers=self.headers, params=params)
            if response.status_code == 200:
                response = response.json()
                return response['graphql']['user']['id']
            else:
                print('request error, the response error code is: ', response.status_code)
        except Exception as e:
            print(e)
            return None

    def get_media_urls(self):
        if self.cursor == '':
            params = (
                ('query_hash', '32b14723a678bd4628d70c1f877b94c9'),
                ('variables', '{"id":"%s","first":12}' % self.rest_id),
            )
        else:
            params = (
                ('query_hash', '32b14723a678bd4628d70c1f877b94c9'),
                ('variables', '{"id":"%s","first":12,"after":"%s"}' % (self.rest_id, self.cursor)),
            )
            
        try:
            response = requests.get(MEDIA_URL, headers=self.headers, params=params)
            if(response.status_code == 200):
                return response.json()
            else:
                print('request error in get_media(), the response error code is: ', response.status_code)
        except Exception as e:
            print(e)

    def scrawlMedia(self):
        mkDir(self.pic_path)
        mkDir(self.video_path)

        while self.cursor != 'END':
            response = self.get_media_urls()
            pic_urls = jsonpath(response, expr='$.data.user.edge_owner_to_timeline_media.edges.[*].node.edge_sidecar_to_children.edges.[*].node.display_url')
            video_urls = jsonpath(response, expr='$.data.user.edge_owner_to_timeline_media.edges.[*].video_url')

            #download media
            if pic_urls:
                for url in pic_urls: self.dlPic(url)
            if video_urls:
                for url in video_urls: self.dlVideo(url)

            #upgrade cursor
            page_info = response['data']['user']['edge_owner_to_timeline_media']['page_info']
            self.cursor = page_info['end_cursor'] if page_info['has_next_page'] else 'END'

    def dlPic(self, url):
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
