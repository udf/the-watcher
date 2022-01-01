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
    plugin_names=['core'] + sys.argv[1:],
  )

  await client.run_until_disconnected()


client.loop.run_until_complete(main())
