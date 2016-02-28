# 知乎轮带逛

定向下载轮子哥赞过的美女图片。

## 简单说明

### 依赖

* >= Python 3.5
* aiohttp, BeautifulSoup

### 使用

当前目录下新建 auth.py，按如下格式写入你的知乎账号。会优先使用邮箱登陆。

    email = 'xxx@xxx.xxx'
    phone_num = 'xxxxxxxxxxx'
    password = 'xxxxx'

在 config.py 中可以对爬取页面的速度作调整，在 keywords.py 中可以修改爬取的关键字。

然后运行

    python3 main.py
    
然后就会在 img 目录下存放下载的图片。

## Changelog

### 2016.2.27

目前算法是在答案的评论中查找相关的关键字。