from httpclient import HttpClient
import asyncio
from bs4 import BeautifulSoup
import keywords
import config
import html
import os

ZHIHU_URL = 'https://www.zhihu.com'
LOGIN_URL = ZHIHU_URL + '/login/email'
VCZH_URL = ZHIHU_URL + '/people/excited-vczh'

class ZhihuClient():
    def __init__(self, client, email, password):
        self._session = client
        self._client = HttpClient(client)
        self._email = email
        self._password = password

        self._imgurl = asyncio.Queue()

    async def _login(self):
        data = {'email': self._email, 'password': self._password, 'remember_me': 'true'}
        dic = await self._client.post_json(LOGIN_URL, data=data)
        await self._client.get(ZHIHU_URL)
        self._xsrf = self._session.cookies['_xsrf'].value
        print (dic['msg'])
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
                print ('网络错误')
                # break
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
            print ('网络错误')
            return False

        data = dic['data']
        count = 0
        for comment in data:
            for keyword in keywords.keywords:
                if comment['content'].find(keyword) != -1:
                    # print ()
                    # print (keyword)
                    # print (comment['content'])
                    # print ()
                    count += 1
        if count >= 2:
            return True
        return False

    async def download_image(self):
        if not os.path.exists('img'):
            os.makedirs('img')
        self._count = 1
        while True:
            url = await self._imgurl.get()
            if url == 'the end':
                print ('下载完毕')
                break
            print ('正在下载第 %s 张图片。。。' % self._count)
            await self._client.downloadfile(url, './img/' + str(self._count) + '.jpg')
            await asyncio.sleep(config.img_interval)
            self._count += 1
