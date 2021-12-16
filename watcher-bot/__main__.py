import asyncio
import logging
logging.basicConfig(level=logging.INFO)
import importlib
import sys

from telethon import TelegramClient

from . import proxy_globals

logger = logging.getLogger('main')
client = TelegramClient('bot', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e')


async def loop_runner(logger, loop):
  while 1:
    try:
      await loop()
    except Exception as e:
      logger.exception('Unhandled exception in loop body')
    await asyncio.sleep(1)


async def main():
  await client.start()

  proxy_globals.client = client
  proxy_globals.me = await client.get_me()
  loops = []
  for module_name in ['core'] + sys.argv[1:]:
    proxy_globals.logger = logging.getLogger(module_name)
    try:
      module = importlib.import_module(f'.p_{module_name}', __package__)
    except Exception as e:
      logger.exception(f'Error loading plugin "{module_name}"')
      continue
    plugin_loop = getattr(module, 'main_loop', None)
    if plugin_loop:
      loops.append((proxy_globals.logger, plugin_loop))

  for plugin_logger, loop in loops:
    await asyncio.create_task(loop_runner(plugin_logger, loop))

  await client.run_until_disconnected()


client.loop.run_until_complete(main())