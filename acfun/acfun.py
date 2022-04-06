import os
import requests
import json

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
}


def mkDir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            print(e)


class Acfun:
    def __init__(self, mid="") -> None:
        # TODO(thekips): Add Episode Download.
        self.mid = mid

    def getJson(self, data: str):
        index1 = data.find("ksPlayJson")
        index2 = data.find("{", index1)

        old_index = index2
        li = ["{"]
        while True:
            left = data.find("{", old_index + 1)
            right = data.find("}", old_index + 1)
            if left < right:
                old_index = left
                li.append("{")
            else:
                old_index = right
                li.pop()

            if len(li) == 0:
                index3 = right
                break

        videoInfo = data[index2 : index3 + 1]
        videoInfo = eval(repr(videoInfo).replace("\\\\", "\\"))
        return json.loads(videoInfo)

    def dlVideo(self, url, path="data/"):
        mkDir(path)
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.text
            videoInfo = self.getJson(data)
            m3u8 = videoInfo["adaptationSet"][0]["representation"][0]["url"]
            videoId = videoInfo["videoId"]
            path_to_file = path + videoId + ".mp4"

            if os.path.exists(path_to_file):
                print("Video [%s] has been download" % videoId)
                return
            cmd = 'ffmpeg -loglevel warning -i "%s" -codec copy %s' % (m3u8, path_to_file)
            print('Downloading...')
            os.system(cmd)
        else:
            print(response.status_code)


if __name__ == "__main__":
    acfun = Acfun()
    url = input("Please input url of the video:")
    acfun.dlVideo(url)
