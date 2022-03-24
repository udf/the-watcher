
import asyncio

from bepis_bot.runtime import client, logger, config
from telethon import events

from .msg_sender import _sender_loop, send_message, hostname, utc_fmt

start_date = utc_fmt()
my_send_message = lambda content: send_message('core', content)


@client.on(events.NewMessage(chats=config.owner, pattern='/ping$'))
async def ping(event):
  plugins = list(client._plugins.keys())
  my_send_message(
    f'Running since <code>{start_date}</code>'
    f'\nwith plugins: <code>{" ".join(plugins)}</code>'
  )


async def on_load():
  asyncio.create_task(loop_runner(logger, _sender_loop))
  my_send_message('Watcher started')


async def loop_runner(logger, loop_body):
  while 1:
    try:
      await loop_body()
    except Exception as e:
      logger.exception('Unhandled exception in loop body')
    await asyncio.sleep(1)
