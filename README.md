## Media Crawler

一些常用社交网站的媒体资源（视频，图片）的爬取脚本

### Usage

- 安装代码中的python依赖库
  ```shell
  pip install -r requirements.txt
  ```

- 进入到想要爬取的网站文件夹，填写该文件夹下的config.yaml文件中列举的所有字段。

  提示：打开浏览器的开发者工具，在网络面板里查找与目标网站通信时的包记录，多找几个，可能在`Request Headers`中找到这些字段；填写字段的时候，填至冒号的一个空格后即可，不需要加双引号。

- 执行：

  ```shell
  # windows下可能需要按一下<Tab>键
  python *.py
  ```

  之后，根据提示输入想要爬取的账号ID即可。

### Support
bilibilii -> 哔哩哔哩：支持单个账号的所有视频爬取，支持单个bv号的所有视频爬取（需要自己主动调用类的dlVideo方法）

instgram -> 图享: 支持单个账号的所有图片和视频爬取

karaoke -> 全民K歌：支持单个账号的所有歌曲爬取

twitter -> 推特：支持单个账号的所有图片和视频爬取

weibo -> 新浪微博：支持单个账号的所有图片和视频爬取
