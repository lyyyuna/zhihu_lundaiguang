import logging
import logging.handlers

handler = logging.handlers.RotatingFileHandler('zhihu.log', maxBytes = 1024*1024, backupCount = 5) # 实例化handler
fmt = '%(asctime)s <%(filename)s><%(lineno)d>: [%(levelname)s] - %(message)s'
formatter = logging.Formatter(fmt)   #
handler.setFormatter(formatter)      #
logger = logging.getLogger('zhihu')    #
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


import asyncio
import aiohttp
from zhihuclient import ZhihuClient
import config

with aiohttp.ClientSession() as client:
    lunzi = ZhihuClient(client, config.email, config.password)

    tasks = [lunzi.crawl_voteup_answer()]
    
    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
