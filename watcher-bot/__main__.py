import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)

from .bepis_bot import BepisClient

logger = logging.getLogger('main')
client = BepisClient('bot', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e')


async def main():
  await client.start()

  await client.load_plugins(
    path=Path(__file__).parent / 'plugins',
    plugin_names=['core'] + sys.argv[1:],
  )

  await client.run_until_disconnected()


client.loop.run_until_complete(main())
