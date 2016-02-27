# coding=utf-8

import asyncio
import aiohttp
import json

class HttpClient:
    def __init__(self, client):
        if not isinstance(client, aiohttp.ClientSession):
            raise TypeError('Please init with a aiohttp.ClientSession instance')
        self.__client = client

    async def get(self, url, params=None):
        try:
            async with await self.__client.get(url, params=params) as r:
                return await r.text()
        except aiohttp.errors.DisconnectedError:
            return None
        except aiohttp.errors.ClientResponseError:
            return None

    async def get_json(self, url, params=None):
        try:
            with aiohttp.Timeout(3):
                async with await self.__client.get(url, params=params) as r:
                    text = await r.text(encoding='utf-8')
                    return json.loads(text)
        except:
            return None


    async def post(self, url, data, params=None):
        try:
            async with await self.__client.post(url, params=params, data=data) as r:
                return await r.text()
        except aiohttp.errors.DisconnectedError:
            return None
        except aiohttp.errors.ClientResponseError:
            return None

    async def post_json(self, url, data, params=None):
        try:
            with aiohttp.Timeout(3):
                async with await self.__client.post(url, params=params, data=data) as r:
                    text = await r.text(encoding='utf-8')
                    return json.loads(text)
        except:
            return None

    async def downloadfile(self, url, filename):
        try:
            with aiohttp.Timeout(3):
                async with await self.__client.get(url) as r:
                    with open(filename, 'wb') as fd:
                        while True:
                            chunk = await r.content.read(4096)
                            if not chunk:
                                break
                            fd.write(chunk)
                    return True
        except:
            return False
