# Polls flood for notifications and sends new ones to the bot owner
import asyncio
import json
import time

import aiohttp

from bepis_bot.runtime import client, logger, require, config

core = require('core')
send_message = lambda s: core.send_message('flood', s)
SERVER_URL = config.flood_server_url
USERNAME = config.flood_username
PASSWORD = config.flood_password
last_processed = time.time() * 1000


async def send_notification(item):
  title = {
    'notification.feed.torrent.added': 'feed item queued',
    'notification.torrent.finished': 'finished downloading'
  }.get(item['id'], item['id'])
  data = item['data']
  text = data.get('title') or data.get('name') or json.dumps(data)
  send_message(f'{title}: {text}')


async def main_loop():
  global last_processed

  cookie_jar = aiohttp.CookieJar(unsafe=True)
  connector = aiohttp.TCPConnector(force_close=True)
  async with aiohttp.ClientSession(
    cookie_jar=cookie_jar,
    connector=connector
  ) as session:
    r = await session.post(
      f'{SERVER_URL}/api/auth/authenticate',
      json={
        'username': USERNAME,
        'password': PASSWORD
      }
    )
    if r.status != 200:
      logger.error(f'Authentication error: {await r.text()}')
      await asyncio.sleep(60)
      return

    logger.info('Connected to flood, polling')

    num_errors = 0
    while 1:
      r = await session.get(f'{SERVER_URL}/api/notifications')
      res = await r.text()
      if r.status != 200:
        logger.warning(f'Error getting notifications: {res}')
        num_errors += 1
        if num_errors == 5:
          send_message(f'Failed to fetch notifications 5 times, check logs.')
        await asyncio.sleep(60)
        continue
      num_errors = 0
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
