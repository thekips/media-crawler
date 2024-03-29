import base64
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

import js2py
import requests
from pyexiv2 import Image

# Init for decode
URL_CLIENT = 'https://client.ibzhi.com/http/client'
CryptoJS = js2py.require('crypto-js')
CLASS = ['wallpaper/get_wallpaper_list', 'wallpaper/get_list_by_classify']
FUNC = [
    lambda page:'{"page":%s,"size":30,"v":3}' % str(page),
    lambda page, c_id:'{"page":%s,"size":30,"v":3,"classify_ids":"%s"}' % (str(page), c_id),
]
EXIF = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

# Methods.
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
    dec = dec.encode('latin1').decode('utf-8')
    return json.loads(dec)


def write_pic(content, tag, img_path):
    # 将下载的二进制数据创建为图像
    with open(img_path, 'wb') as f:
        f.write(content)
    
    tag = re.split(r'[;,\\s]+', tag)
    tag.append(c_name[c_index])

    # 添加关键字标记到 EXIF 数据中
    img = Image(img_path, encoding='gbk')
    img_type = img.get_mime_type()
    if img_type == 'image/jpeg':
        img.modify_iptc({'Iptc.Application2.Keywords': tag})
    elif img_type == 'image/png':
        img.modify_xmp({'Xmp.dc.subject': tag})
    img.close()

def dl_pic(img_url, tag, c_time):
    img_name = re.findall(r'(?<=wallpaper/).*', img_url)[0]
    path = os.path.join(PATH, c_time)
    img_path = os.path.join(path, img_name)

    if not os.path.exists(img_path):
        resp = requests.get(img_url)
        if resp.status_code == 200:
            mkDir(path)
            try:
                print(f'Get {img_url} -> {path}')
                write_pic(resp.content, tag, img_path)
            except Exception as e:
                print(e)
                print('Try to download the picture again...')
                dl_pic(img_url, tag, c_time)
        else:
            print(f'Error {img_url} -> {path}')
    else:
        print(f'Exist {img_url} -> {path}')

# Request params
def get_params(page, f_index, c_id=None):
    if page == None: page = 1e16

    params = {
        "token": "",
        "path": CLASS[f_index],
    }
    if f_index == 0:
        params['param'] = FUNC[f_index](page)
    if f_index == 1:
        params['param'] = FUNC[f_index](page, c_id)

    # print(params)
    return params

# Initial args.
f_index = int(input('输入 0.获取最近壁纸 1.获取类别壁纸 : '))
if f_index == 0:
    params = lambda page=None : get_params(page, f_index)
    PATH = 'data/最近壁纸'
elif f_index == 1:
    params = {
        'token': '',
        'param': '{"v":3}',
        'path': 'wallpaper/get_classify_list',
    }
    resp = requests.get(URL_CLIENT, params=params)
    if resp.status_code == 200:
        print("正在获取类别，请稍等...")
        path_dict = decode_b64_aes(resp.text)['data']
    else:
        print('Get class Failure!')
        exit()

    c_name = [x['name'] for x in path_dict]
    c_ids = [x['_id'] for x in path_dict]
    for i in range(len(c_name)):
        print(str(i) + '. ' + c_name[i], end=' ')
    c_index = int(input('\n请输入类别序号:'))

    params = lambda page=None : get_params(page, f_index, c_ids[c_index])
    PATH = 'data/' + c_name[c_index]


# Get total pages num.
resp = requests.get(URL_CLIENT, params=params())
# print(resp.text)
info = decode_b64_aes(resp.text)
total_pages = info['totalPages']
print(f'Total Pages Num: {total_pages}')

while True:
    begin_page = input('Input the page num to start with(default=1): ')
    if begin_page.isnumeric():
        begin_page = int(begin_page)
        break
    elif begin_page == '':
        begin_page = 1
        break
    else:
        print('Please input num without alphabet!')

# Start crawler.
for page in range(total_pages):
    if begin_page > page + 1: continue

    print(f'=====Downloading Page {page + 1}=====')
    resp = requests.get(URL_CLIENT, params=params(page))
    # print(params())
    wallpaper_list = decode_b64_aes(resp.text)

    page_num = len(wallpaper_list['data'])
    print(f'Total Pages Image Num: {page_num}')

    tags = []
    img_urls = []
    ctimes = []
    for wallpaper_info in wallpaper_list['data']:
        url = wallpaper_info['originalUrl']
        img_urls.append(re.sub(r'\?.*', '', url))

        tags.append(wallpaper_info['tag'])

        c_time = time.localtime(wallpaper_info['create_time'] // 1000) 
        ctimes.append('%d-%02d' % (c_time.tm_year, c_time.tm_mon))
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(dl_pic, img_urls, tags, ctimes)

os.system('pause')