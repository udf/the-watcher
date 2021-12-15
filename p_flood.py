# Polls flood for notifications and sends new ones to the bot owner
import asyncio
import json
import time
from math import floor

import aiohttp

from proxy_globals import client, logger
from common import OWNER

SERVER_URL = 'http://127.0.0.1:3000'
last_processed = time.time()


async def send_notification(item):
  title = {
    'notification.feed.torrent.added': 'feed item queued',
    'notification.torrent.finished': 'finished downloading'
  }.get(item['id'], item['id'])
  data = item['data']
  text = data.get('title') or data.get('name') or json.dumps(data)
  await client.send_message(OWNER, f'Torrent {title}: {text}')


async def main_loop():
  global last_processed

  cookie_jar = aiohttp.CookieJar(unsafe=True)
  connector = aiohttp.TCPConnector(force_close=True)
  async with aiohttp.ClientSession(
    cookie_jar=cookie_jar,
    connector=connector
  ) as session:
    await session.get(f'{SERVER_URL}/api/auth/verify')
    logger.info('Connected to flood, polling')

    while 1:
      last_fetch = floor(time.time())
      r = await session.get(f'{SERVER_URL}/api/notifications')
      res = json.loads(await r.text())
      notifications = res['notifications']
      for item in notifications:
        if item['ts'] / 1000 >= last_processed:
          await send_notification(item)
      last_processed = last_fetch
      await asyncio.sleep(5)
