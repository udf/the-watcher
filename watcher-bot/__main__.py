import asyncio
import logging
logging.basicConfig(level=logging.INFO)
import importlib
import sys

from .bepis_bot import BepisClient

from . import proxy_globals

logger = logging.getLogger('main')
client = BepisClient('bot', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e')


async def main():
  await client.start()

  proxy_globals.client = client
  proxy_globals.me = await client.get_me()
  init_funcs = []
  for module_name in ['core'] + sys.argv[1:]:
    proxy_globals.logger = logging.getLogger(module_name)
    try:
      module = importlib.import_module(f'.p_{module_name}', __package__)
    except Exception as e:
      logger.exception(f'Error loading plugin "{module_name}"')
      continue
    init_func = getattr(module, 'init', None)
    if init_func:
      init_funcs.append(init_func)

  for plugin_init in init_funcs:
    await plugin_init()

  await client.run_until_disconnected()


client.loop.run_until_complete(main())