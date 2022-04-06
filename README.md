## Media Crawler

一些常用社交网站的媒体资源（视频，图片）的爬取脚本

### Support

| 英文名    | 中文名   | 爬取范围                                               |
| --------- | -------- | ------------------------------------------------------ |
| acfun     | A站      | 支持播放页URL的单视频爬取                              |
| bilibilii | 哔哩哔哩 | 支持单个账号的所有视频爬取，支持单个bv号的所有视频爬取 |
| instgram  | 图享     | 支持单个账号的所有图片和视频爬取                       |
| karaoke   | 全民K歌  | 支持单个账号的所有歌曲爬取                             |
| twitter   | 推特     | 支持单个账号的所有图片和视频爬取                       |
| weibo     | 新浪微博 | 支持单个账号的所有图片和视频爬取                       |

### Usage

- **Python依赖：**
  
  ```shell
  pip install -r requirements.txt
  ```
  
- **其他依赖：**

  定位到想要爬取的网站对应的文件夹，填写该文件夹下的`config.yaml`中列举的所有字段。

  | 英文名    | 字段                                | 额外依赖                 |
  | --------- | ----------------------------------- | ------------------------ |
  | acfun     |                                     | ffmpeg（添加到环境变量） |
  | bilibilii | cookie                              | ffmpeg（添加到环境变量） |
  | instgram  | cookie                              |                          |
  | karaoke   |                                     |                          |
  | twitter   | cookie, x-csrf-token, authorization |                          |
  | weibo     | cookie                              |                          |

  提示：打开浏览器的开发者工具，在网络面板里查找与目标网站通信时的包记录，多找几个，可能在`Request Headers`中找到这些字段；填写字段的时候，填至冒号的一个空格后即可，不需要加双引号，如：

  ```yaml
  cookie: you_cookie_str_without_q
  ```

- 执行程序，根据提示输入想要爬取的账号ID或URL即可。

  ```shell
  # 将*替换成网站对应的英文名
  python *.py
  ```


