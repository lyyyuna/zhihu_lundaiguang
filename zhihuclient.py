from httpclient import HttpClient
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import keywords
import config
import html
import os
import re

ZHIHU_URL = 'https://www.zhihu.com'
LOGIN_URL = ZHIHU_URL + '/login/email'
VCZH_URL = ZHIHU_URL + '/people/excited-vczh'

class ZhihuClient():
    def __init__(self, client, email, phone_num, password):
        self._session = client
        self._client = HttpClient(client)
        self._email = email
        self._phone_num = phone_num
        self._password = password
        self._finish = False
        self._commenttime = '1970'
        self._imgurl = asyncio.Queue()

    async def _login(self):
        # r = requests.get(ZHIHU_URL, headers=Default_Header)
        # results = re.compile(r"\<input\stype=\"hidden\"\sname=\"_xsrf\"\svalue=\"(\S+)\"", re.DOTALL).findall(r.text)
        # self._xsrf = results[0]
        # print (self._xsrf)
        if self._email != '':
            data = {'email': self._email, 'password': self._password, 'remember_me': 'true'}
        else:
            data = {'phone_num': self._phone_num, 'password': self._password, 'remember_me': 'true'}
        print (data)
        dic = await self._client.post_json(LOGIN_URL, data=data)
        await self._client.get(ZHIHU_URL)
        self._xsrf = self._session.cookies['_xsrf'].value
        print (dic['r'])
        print (self._xsrf)

    async def crawl_voteup_answer(self):
        await self._login()

        feed_num = 20
        start = '0'
        api_url = VCZH_URL + '/activities'
        while feed_num == 20:
            data = {'_xsrf':self._xsrf, 'start':start}
            dic = await self._client.post_json(api_url, data=data)
            if dic == None:
                print ('获取更多状态网络错误')
                continue

            feed_num = dic['msg'][0]
            soup = BeautifulSoup(dic['msg'][1], 'html.parser')
            acts = soup.find_all('div', class_='zm-profile-section-item zm-item clearfix')
            start = acts[-1]['data-time'] if len(acts) > 0 else 0
            for act in acts:
                # 查看所有的赞，其他“回答、关注”忽略
                if act.attrs['data-type-detail'] != "member_voteup_answer":
                    continue
                # 获取评论的链接
                comment_div = act.find_all('div', class_='zm-item-answer')
                if comment_div == []:
                    continue
                comment_link = comment_div[0]['data-aid']
                comment_url = ZHIHU_URL + '/r/answers/' + comment_link + '/comments'
                # 根据评论里的关键字判断出是否有目标
                HIT = await self._analyze_comments(comment_url)
                await asyncio.sleep(config.comment_interval)
                if HIT == False:
                    continue
                # 获取回答
                answer = act.find_all('textarea', class_='content hidden')
                if answer == []:
                    continue
                answer[0] = html.unescape(answer[0].get_text())
                # 从回答中找出图片链接
                soup2 = BeautifulSoup(answer[0], 'html.parser')
                img_urls = soup2.find_all('img')
                for img in img_urls:
                    await self._imgurl.put(img.attrs['src'])

            asyncio.sleep(config.more_interval)
            print ('more...')

        await self._imgurl.put('the end')


    async def _analyze_comments(self, url):
        dic = await self._client.get_json(url)
        if dic == None:
            print ('获取评论网络错误')
            return False

        data = dic['data']
        count = 0
        for comment in data:
            self._commenttime = comment['createdTime']
            for keyword in keywords.keywords:
                if comment['content'].find(keyword) != -1:
                    count += 1
        if count >= 3:
            return True
        return False

    async def download_image(self):
        if not os.path.exists('img'):
            os.makedirs('img')
        self._count = 1
        while True:
            url = await self._imgurl.get()
            count = self._count
            self._count += 1
            print ('正在下载第 %s 张图片。。。' % count)
            imgname = url.split('/')[-1]
            # 避免重复下载
            if os.path.exists('./img/' + imgname):
                print ('第 %s 张图片已经下载过，不重复下载。。。' % count)
                continue
            if url == 'the end':
                print ('下载完毕')
                self._finish = True
                break
            await self._client.downloadfile(url, './img/' + imgname)
            await asyncio.sleep(config.img_interval)


    async def monitor(self):
        count = 1
        more_interval = config.more_interval
        comment_interval = config.comment_interval
        img_interval = config.img_interval
        while True:
            if self._finish == True:
                break
            print ()
            print ('目前下载队列还有：%s 个。' % self._imgurl.qsize())
            print ('大概分析到的赞的时间：' + self._commenttime)
            print ()
            count += 1
            config.more_interval = more_interval
            config.comment_interval = comment_interval
            config.img_interval = img_interval
            # 约 200s 后停 10s，避免知乎反爬虫
            if count > 10:
                count = 1
                config.more_interval = 10
                config.comment_interval = 10
                print ('让爬虫休息一下。。。')

            await asyncio.sleep(20)
