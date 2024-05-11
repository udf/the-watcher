import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)

from .bepis_bot import BepisClient
import config

logger = logging.getLogger('main')
client = BepisClient(
  session='bot',
  api_id=6,
  api_hash='eb06d4abfb49dc3eeb1aeb98ae0f581e',
  plugin_config=config
)


async def main():
  client.flood_sleep_threshold = 999999
  await client.start(bot_token=config.token)

  await client.load_plugins(
    path=Path(__file__).parent / 'plugins',
    plugin_names=['core'],
  )

  # dir/plugin -> load plugin from dir if it's a file, load everything if it's a dir
  # plugin -> load plugin from built-ins

  for name in sys.argv[1:]:
    path = Path(name)
    if path.name == name:
      # no directory, load single plugin from built-in dir
      await client.load_plugins(
        path=Path(__file__).parent / 'plugins',
        plugin_names=[name],
      )
      continue
    if path.is_dir():
      # directory, load everything in there
      await client.load_plugins(path=path.parent)
      continue
    # path to file, load it
    await client.load_plugins(
      path=path.parent,
      plugin_names=[path.stem if path.suffix == '.py' else path.name],
    )

  await client.run_until_disconnected()


client.loop.run_until_complete(main())
