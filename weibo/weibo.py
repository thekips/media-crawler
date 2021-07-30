import requests
import yaml
import json
from jsonpath import jsonpath
import os
import time

WEIBO_URL = 'https://m.weibo.cn/api/container/getIndex'
PHOTO_WALL_URL = 'https://m.weibo.cn/api/container/getSecond'

def mkDir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def responseToJson(response):
    res = json.loads(response.text)
    res = json.loads(json.dumps(res, ensure_ascii=False, sort_keys=True))

    return res

class Weibo(object):
    def __init__(self, uid):
        with open('config.yaml', 'r', encoding='utf-8') as f:
            self.headers = yaml.safe_load(f)
        self.uid = uid
        self.index = 1  #for count.
        self.cursor = ''    #location for video info.
        self.pic_path = 'data/' + self.getScreenName() + '/img/'
        self.video_path = 'data/' + self.getScreenName() + '/video/'

    def dlPic(self, url):
        try:
            pic_name = url[url.rfind('/') + 1:]
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
            video_name = url[url.find('.mp4') - 37: url.find('.mp4') + 4]
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

    def getScreenName(self):
        params = (
            ('type', 'uid'),
            ('value', self.uid),
            ('containerid', '100505' + self.uid)
        )

        res = requests.get(WEIBO_URL, params=params)
        res = responseToJson(res)
        return res['data']['userInfo']['screen_name']
        
    def getPicInfo(self):
        params = (
            ('containerid', '107803' + self.uid + '_-_photoall'),
            ('count', '24'),
            ('type', 'uid'),
            ('value', self.uid),
            ('page', self.index)
        )

        res = requests.get(PHOTO_WALL_URL, headers=self.headers, params=params)
        return responseToJson(res)

    def getVideoInfo(self):
        params = (
            ('containerid', '231567' + self.uid),
            ('is_all/[/]', ['1?is_all=1', '1']),
            ('type', 'uid'),
            ('value', self.uid),
            ('since_id', self.cursor),
        )

        res = requests.get('https://m.weibo.cn/api/container/getIndex', headers=self.headers, params=params)
        return responseToJson(res)

    def scrawlMedia(self):
        mkDir(self.pic_path)
        # get picture links from response and download them.
        while True:
            res = self.getPicInfo()
            if res['ok'] == 0: break

            pic_urls = jsonpath(res, expr='$.data.cards.[*].pics.[*].pic_big')
            if pic_urls:
                for url in pic_urls: self.dlPic(url)
            
            print("we have downloaded %d pictures." % (self.index * 24))
            self.index += 1

        self.index = 1
        mkDir(self.video_path)
        # get video links from response and download them.
        while True:
            res = self.getVideoInfo()
            if res['ok'] == 0 or self.cursor == 0: break

            video_urls = jsonpath(res, expr='$.data.cards.[*].mblog.page_info.urls.mp4_720p_mp4')
            if video_urls:
                for url in video_urls: self.dlVideo(url)

            self.cursor = res['data']['cardlistInfo']['since_id']
            print("We have downloaded %d videos." % (self.index * 20))
            self.index += 1

if __name__ == '__main__':
    uid = input('Please input weibo uid of the user: ')
    weibo = Weibo(uid)

    start_time = time.time()
    weibo.scrawlMedia()
    end_time = time.time()

    print("All finished in %ds!" % (end_time-start_time))
    os.system('pause')

