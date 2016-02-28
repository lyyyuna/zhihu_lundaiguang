import asyncio
import aiohttp
from zhihuclient import ZhihuClient
import auth

with aiohttp.ClientSession() as client:
    lunzi = ZhihuClient(client, auth.email, auth.phone_num, auth.password)

    tasks = [
            lunzi.crawl_voteup_answer(),
            lunzi.download_image() ,
            lunzi.monitor()
            ]

    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
