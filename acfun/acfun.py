#%%
from operator import index, le
from turtle import right
from unittest import result
import requests

cookies = {
}

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
}

response = requests.get('https://www.acfun.cn/bangumi/aa6002257_36188_1723857', headers=headers, cookies=cookies)

#%%
data = response.text
index1 = data.find('window.pageInfo')
index2 = data.find('{', index1)

old_index = index2
li = ['{']

cnt = 0
while True:
    left = data.find('{', old_index + 1)
    right = data.find('}', old_index + 1)
    if left < right:
        old_index = left
        li.append('{')
    else:
        old_index = right
        li.pop()
    print(left, right)
    print('li is:', li)
    cnt += 1
    # if cnt ==20:
    #     break

    if len(li) == 0:
        index3 = right
        break

#%%
import json
import html
new = data[index2:index3+1]
end = json.loads(new)

# %%
x = end['currentVideoInfo']['ksPlayJson']
x = json.loads(x)
# %%
m3u8Slice = x['adaptationSet'][0]['representation'][0]['m3u8Slice']
index4 = m3u8Slice.find('https://')
m3u8Slice[index4:].strip()
