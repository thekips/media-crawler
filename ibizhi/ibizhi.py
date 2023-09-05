import base64
import js2py
import os
import re
import requests
import yaml
from concurrent.futures import ThreadPoolExecutor

# Init for decode
URL_CLIENT = 'https://client.ibzhi.com/http/client'
CryptoJS = js2py.require('crypto-js')
CLASS = ['wallpaper/get_wallpaper_list', 'wallpaper/get_list_by_classify']
PATH_DICT = {-1:'最近壁纸', 0: '电脑壁纸', 1: '静物'}
CLASSIFY_ID = ['5fb341d2d1cb4d00014a38dd', '5fac0f5e8404d300019eeb5f']
FUNC = [
    lambda page:'{"page":%s,"size":30,"v":3}' % str(page),
    lambda page, c_id:'{"page":%s,"size":30,"v":3,"classify_ids":"%s"}' % (str(page), c_id),
]

# Request params
def get_params(page, f_index, c_index=None):
    if page == None: page = 1e16

    params = {
        "token": token,
        "path": CLASS[f_index],
    }
    if f_index == 0:
        params['param'] = FUNC[f_index](page)
    if f_index == 1:
        params['param'] = FUNC[f_index](page, CLASSIFY_ID[c_index])

    # print(params)
    return params

# Initial args.
f_index = int(input('输入 0.获取最近壁纸 1.获取类别壁纸 :'))
if f_index == 0:
    params = lambda page=None : get_params(page, f_index)
    PATH = 'data/' + PATH_DICT[-1]
elif f_index == 1:
    c_index = int(input(f'输入 {PATH_DICT} :'))
    params = lambda page=None : get_params(page, f_index, c_index)
    PATH = 'data/' + PATH_DICT[c_index]

with open('config.yaml', 'r', encoding='utf-8') as f:
    token = yaml.safe_load(f)['token']


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
    return eval(dec)


def dl_pic(img_url, tag):
    img_name = re.findall(r'(?<=wallpaper/).*?(?=\?x-image)', img_url)[0]
    path = os.path.join(PATH, tag)
    img_path = os.path.join(path, img_name)

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
        dl_pic(img_url, tag)


# Get total pages num.
resp = requests.get(URL_CLIENT, params=params())
# print(resp.text)
info = decode_b64_aes(resp.text)
total_pages = info['totalPages']
print(f'Total Pages Num: {total_pages}')

while True:
    begin_page = input('Input the page num you want to start with: ')
    if begin_page.isnumeric():
        begin_page = int(begin_page)
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
    for wallpaper_info in wallpaper_list['data']:
        img_urls.append(wallpaper_info['originalUrl'])
        tags.append(wallpaper_info['tag'].encode('latin1').decode('utf-8'))
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(dl_pic, img_urls, tags)