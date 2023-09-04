import base64
import js2py
import os
import re
import requests
import yaml

# Init for decode
URL_CLIENT = 'https://client.ibzhi.com/http/client'
CryptoJS = js2py.require('crypto-js')
with open('config.yaml', 'r', encoding='utf-8') as f:
    token = yaml.safe_load(f)['token']

def mkDir(path):
    if(not os.path.exists(path)):
        try:
            os.makedirs(path)
        except Exception as e:
            print(e)


def decode_b64_aes(enc):
    key = 'aes'
    enc = base64.b64decode(enc).decode('utf-8')
    dec = CryptoJS.AES.decrypt(enc, key).toString(CryptoJS.enc.Utf8)
    return eval(dec)

# Request params
def get_params(page):
    params = {
        'token': token,
        'param': '{"page":%s,"size":30,"v":3}' % str(page),
        'path': 'wallpaper/get_wallpaper_list',
    }
    return params

def dl_pic(url, tag):
    img_name = re.findall(r'(?<=wallpaper/).*?(?=\?x-image)', img_url)[0]
    path = f'data/{tag}/'
    img_path = path + img_name

    try:
        if not os.path.exists(img_path):
            response = requests.get(img_url)

            if response.status_code == 200:
                mkDir(path)
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                print(f'Get {img_url} -> {tag}')
            else:
                print(f'Error {img_url} -> {tag}')
        else:
            print(f'Exist {img_url} -> {tag}')
    except:
        print('Try to download the picture again...')
        dl_pic(url, tag)

# Get total pages.
resp = requests.get(URL_CLIENT, params=get_params(1e16))
info = decode_b64_aes(resp.text)
total_pages = info['totalPages']
print(f'Total Pages Num: {total_pages}')


# Start crawler.
for page in range(total_pages):
    print(f'=====Downloading Page {page + 1}=====')
    resp = requests.get(URL_CLIENT, params=get_params(page))
    wallpaper_list = decode_b64_aes(resp.text)

    page_num = len(wallpaper_list['data'])
    print(f'Total Pages Image Num: {page_num}')

    for wallpaper_info in wallpaper_list['data']:
        tag = wallpaper_info['tag'].encode('latin1').decode('utf-8')
        img_url = wallpaper_info['originalUrl']
        dl_pic(img_url, tag)