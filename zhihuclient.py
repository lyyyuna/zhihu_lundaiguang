from httpclient import HttpClient
import asyncio

ZHIHU_URL = 'https://www.zhihu.com'
LOGIN_URL = ZHIHU_URL + '/login/email'

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

    async def analyze_comments(self):
        pass

    async def download_image(self):
        pass
