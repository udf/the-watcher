import logging
from configparser import ConfigParser
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)

from .bepis_bot import BepisClient

logger = logging.getLogger('main')
config = ConfigParser()
config.read('config.ini')
client = BepisClient(
  session='bot',
  api_id=6,
  api_hash='eb06d4abfb49dc3eeb1aeb98ae0f581e',
  plugin_config=config
)


async def main():
  await client.start(bot_token=config['core']['token'])

  await client.load_plugins(
    path=Path(__file__).parent / 'plugins',
    plugin_names=['core'] + sys.argv[1:],
  )

  await client.run_until_disconnected()


client.loop.run_until_complete(main())
