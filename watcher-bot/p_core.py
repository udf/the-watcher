from datetime import datetime
from socket import gethostname
import sys

from telethon import events

from .proxy_globals import client, logger
from .common import OWNER


start_date = datetime.now().astimezone().replace(microsecond=0).isoformat()

@client.on(events.NewMessage(chats=OWNER, pattern='/ping$'))
async def ping(event):
  plugins = [p for p in sys.modules.keys() if p.startswith('p_')]
  await event.respond(
    f'Running on <code>{gethostname()}</code> since <code>{start_date}</code>'
    f'\nwith plugins: <code>{" ".join(plugins)}</code>',
    parse_mode='HTML'
  )