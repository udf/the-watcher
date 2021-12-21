# Polls flood for notifications and sends new ones to the bot owner
import asyncio
import json
import time

import aiohttp

from bepis_bot.runtime import client, logger, require

core = require('core')
SERVER_URL = 'http://127.0.0.1:3000'
last_processed = time.time() * 1000


async def send_notification(item):
  title = {
    'notification.feed.torrent.added': 'feed item queued',
    'notification.torrent.finished': 'finished downloading'
  }.get(item['id'], item['id'])
  data = item['data']
  text = data.get('title') or data.get('name') or json.dumps(data)
  await client.send_message(core.OWNER, f'Torrent {title}: {text}')


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
      r = await session.get(f'{SERVER_URL}/api/notifications')
      res = json.loads(await r.text())

      # treat timestamp as a sequential ID
      max_id = 0
      notifications = res['notifications']
      for item in notifications:
        if item['ts'] > last_processed:
          await send_notification(item)
        max_id = max(max_id, item['ts'])

      last_processed = max_id
      await asyncio.sleep(5)


async def on_load():
  asyncio.create_task(core.loop_runner(logger, main_loop))
