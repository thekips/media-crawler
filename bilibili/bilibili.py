import os
import re
import time
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import subprocess
import yaml
import requests
from tqdm import tqdm
from jsonpath import jsonpath

INFO_URL = 'https://api.bilibili.com/x/space/acc/info'
MEDIA_URL = 'https://api.bilibili.com/x/space/arc/search'
CID_URL = 'https://api.bilibili.com/x/player/pagelist'
PLAYER_URL = 'https://api.bilibili.com/x/player/playurl'

def mkDir(path):
    if(not os.path.exists(path)):
        try:
            os.makedirs(path)
        except Exception as e:
            print(e)

def enablePath(path):
    '''
    Replace character like: / \ : * ? " < > | and blank character
    to: _
    '''
    pattern = r"[\/\\\:\*\?\"\<\>\|\s]"  
    return re.sub(pattern, "_", path)

class Bilibili():
    def __init__(self, mid='') -> None:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            self.headers = yaml.safe_load(f)
        self.mid = mid
        self.session=requests.session()
        
    def __getName(self):
        if self.mid == '':
            return 'anyone'
        params = (
            ('mid', self.mid),
        )
        res = requests.get(INFO_URL, params=params)
        res = json.loads(res.text)

        return res['data']['name']

    def __getMediaID(self):
        params = (
            ('mid', self.mid),
            ('pn', self.index),
            ('order', 'pubdate'),
        )
        res = requests.get(MEDIA_URL, params=params)
        res = json.loads(res.text)

        # Get video(bvid) and music id.
        bvids = jsonpath(res, expr='$.data.list.vlist.[*].bvid')
        bv_times = jsonpath(res, expr='$.data.list.vlist.[*].created')
        tids = jsonpath(res, expr='$.data.list.tlist.[*].tid')
        t_times = jsonpath(res, expr='$.data.list.tlist.[*].created')

        return zip(bvids, bv_times) if bvids else False, False
        # return zip(bvids, bv_times), zip(tids, t_times)

    def __getEpisode(self, bvid):
        params = (
            ('bvid', bvid),
        )
        res = requests.get(CID_URL, params=params)
        res = json.loads(res.text)

        # Get all video episode(cid) under a video(vid) and their name.
        cids = jsonpath(res, expr='$.data.[*].cid')
        names = jsonpath(res, expr='$.data.[*].part')

        return zip(cids, names)

    def __getVideoUrl(self, bvid, cid):
        params = (
            ('bvid', bvid),
            ('cid', cid),
            ('fourk', '1'),
            ('fnval', '16'),
        )

        res = requests.get(PLAYER_URL, headers=self.headers, params=params)
        res = json.loads(res.text)

        video_info = jsonpath(res, expr='$.data.dash.video.[*]')
        video_url = video_info[0]['baseUrl']    # Get best quality.
        audio_info = jsonpath(res, expr='$.data.dash.audio.[*]')
        audio_url = audio_info[0]['baseUrl']    # Get best quality.

        return video_url, audio_url

    def __dlMedia(self, url, path_to_file, name, chunk=1024*1024):
        headers = {
            'user-agent': 'Safari/537.36',
            'referer': 'https://www.bilibili.com/',
            'range': 'bytes=0-1',
        }
        # Send option request to get resource of server.
        session = self.session
        session.options(url=url, headers=headers, verify=False)

        # Get total file size and set initial chunk range.
        res = session.get(url=url, headers=headers)
        range = int(res.headers['Content-Range'].split('/')[1])
        l_range, r_range = 0, min(chunk - 1, range - 1)
        bar = tqdm(total=range, unit_divisor=1024, unit='B', unit_scale=True, desc=name, ascii=' #')

        with open(path_to_file, 'wb') as f:
            while True:
                headers.update({'Range': 'bytes=%d-%d' % (l_range, r_range)})

                # Get media chunk and print download progress.
                res = session.get(url=url, headers=headers)
                f.write(res.content)
                bar.update(r_range - l_range + 1)

                if r_range + 1 != range:
                    l_range = r_range + 1
                    r_range = min(r_range + chunk, range - 1)
                else: 
                    break
        
        bar.close()

    def dlVideo(self, bvid, path='data/anyone/', bvtime=time.time()):
        '''
        Download all episode under a bvid.
        '''
        mkDir(path)

        cidinfo = self.__getEpisode(bvid)
        for cid, cname in cidinfo:

            # Go to next episode if this one exits.
            cname = enablePath(cname)
            output_path = '%s%d_%s.mp4' % (path, cid, cname)
            if os.path.exists(output_path): 
                os.utime(output_path, (bvtime, bvtime))
                print('%s have downloaded.' % output_path) 
                continue

            # Download video and audio of the episode.
            video_path = '%s%d_%s.video' % (path, cid, cname)
            audio_path = '%s%d_%s.audio' % (path, cid, cname)
            video_url, audio_url =self.__getVideoUrl(bvid, cid)
            self.__dlMedia(video_url, video_path, video_path[len(path) + 1 : ])
            self.__dlMedia(audio_url, audio_path, audio_path[len(path) + 1 : ])

            # Combine video and audio to mp4 file.
            cmd = 'ffmpeg -i %s -i %s -y -c copy %s' % (video_path, audio_path, output_path)
            ret = subprocess.call(cmd, shell=True)
            if ret != 0:
                print(' ERROR WHEN COMBINE, WITH CODE %d' % ret)

            os.utime(output_path, (bvtime, bvtime))
            os.remove(video_path)
            os.remove(audio_path)

    def scrawlMedia(self, path=''):
        if self.mid == '':
            self.mid = input('Please input bilibili mid of the user:')
        
        if path == '':
            path = self.mid + '_' + self.__getName() + '/'
        enablePath(path)

        self.index = 0
        while True:
            self.index += 1
            bvinfo, tidinfo = self.__getMediaID()
            if not bvinfo and not tidinfo: break

            if bvinfo:
                for bvid, bvtime in bvinfo:
                    self.dlVideo(bvid, 'data/' + path, bvtime)

            if tidinfo:
                pass

if __name__ == '__main__':
    bilibili = Bilibili()

    while True:
        option = input('[1] Download one video.\n[2] Download all video from a user.\n')

        if option == '1':
            bvid = input('Please input video BV number:')
            bilibili.dlVideo(bvid)
            break
        elif option == '2':
            start_time = time.time()
            bilibili.scrawlMedia()
            end_time = time.time()
            print("All finished in %ds!" % (end_time-start_time))
            break
        else:
            print('Please input a number...')
