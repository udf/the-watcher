
import asyncio
import sys
from datetime import datetime
from socket import gethostname

from bepis_bot.runtime import client, logger
from telethon import events

OWNER = 232787997
start_date = datetime.now().astimezone().replace(microsecond=0).isoformat()


@client.on(events.NewMessage(chats=OWNER, pattern='/ping$'))
async def ping(event):
  plugins = [p for p in sys.modules.keys() if p.startswith('p_')]
  await event.respond(
    f'Running on <code>{gethostname()}</code> since <code>{start_date}</code>'
    f'\nwith plugins: <code>{" ".join(plugins)}</code>',
    parse_mode='HTML'
  )


async def on_load():
  await client.send_message(
    OWNER,
    f'Watcher started on <code>{gethostname()}</code>',
    parse_mode='HTML'
  )


async def loop_runner(logger, loop_body):
  while 1:
    try:
      await loop_body()
    except Exception as e:
      logger.exception('Unhandled exception in loop body')
    await asyncio.sleep(1)
