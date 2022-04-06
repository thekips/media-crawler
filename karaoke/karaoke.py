import time
import os
import requests
import re
import music_tag

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

class Karaoke(object):
    def __init__(self, uid: str) -> None:
        super().__init__()
        self.songs_id = []
        self.songs_name = []
        self.songs_date = []
        self.get_songs(uid)
    
    def get_songs(self, uid: str) -> list:
        url = 'https://node.kg.qq.com/cgi/fcgi-bin/kg_ugc_get_homepage?type=get_uinfo&start=%d&num=8&share_uid=%s'
        res = requests.get(url % (1, uid)).text
        self.artist = re.search(r'(?<="nickname": ").*?(?=",)', res).group()
        self.path = 'data/' + self.artist
        num = re.search(r'(?<="ugc_total_count":).+?(?=,)', res).group()
        total = (int(num)+ 7) // 8

        for start in range(1, total + 1):
            res = requests.get(url % (start, uid)).text
            self.songs_id += re.findall(r'(?<="shareid": ").*?(?=",)', res)
            self.songs_name += re.findall(r'(?<="title": ").*?(?=",)', res)
            self.songs_date += re.findall(r'(?<="time": ).*?(?=,)', res)

        if '' in self.songs_name:
            index = []
            for i in range(len(self.songs_name)):
                if self.songs_name[i] == '':
                   index.append(i+1) 
            for i in index:
                del self.songs_name[i]

        print(self.songs_name)
        print('found %d songs.' % len(self.songs_id))

    def scrawlMedia(self):
        mkdir(self.path)

        url = 'https://node.kg.qq.com/cgi/fcgi-bin/fcg_get_play_url?shareid=%s'
        for song_id, song_name, song_date in zip(self.songs_id, self.songs_name, self.songs_date):
            song_date = time.strftime("%Y-%m-%d", time.localtime(int(song_date)))
            self.dlSong(url % song_id, song_name, song_date)
        
    def dlSong(self, url, name, date):
        try:
            name += '-' + date + '.m4a'
            name = re.sub(r'[\/:*?"<>|]', ' ', name)
            path_to_file = self.path + '/' + name
            if os.path.exists(path_to_file): return

            song = requests.get(url)
            if song:
                print(name)
                with open(path_to_file, 'wb') as f:
                    f.write(song.content)

                file = music_tag.load_file(path_to_file)
                file['title'] = name[:name.find('-')]
                file['artist'] = self.artist
                file['year'] = date
                file.save()
        except:
            print('try download the song again...')
            self.dlSong(url, name, date)

if __name__ == '__main__':
    uid = input('Please input the karaoke share uid of the user: ')
    karaoke = Karaoke(uid)

    start_time = time.time()
    karaoke.scrawlMedia()
    end_time = time.time()

    print("All finished in %ds!" % (end_time-start_time))
    os.system('pause')
