import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from socket import gethostname

from bepis_bot.runtime import client, logger

OWNER = 232787997
hostname = gethostname()
_msg_queue = asyncio.Queue()


@dataclass
class Message:
  sender: str
  content: str
  timestamp: float = field(default_factory=time.time)


def utc_fmt(ts=None):
  t = datetime.utcfromtimestamp(ts) if ts else datetime.utcnow()
  return t.strftime('%Y-%m-%d %H:%M:%S UTC')


def send_message(sender, content):
  _msg_queue.put_nowait(Message(sender, content))


async def _try_send_message(msg: Message):
  original_time = ''
  if time.time() - msg.timestamp >= 5:
    original_time = f'@{utc_fmt(msg.timestamp)}'
  sep = '\n' if '\n' in msg.content else ' '
  content = f'<b>{hostname}.{msg.sender}</b>{original_time}:{sep}{msg.content}'
  try:
    await client.send_message(
      OWNER,
      content,
      parse_mode='HTML'
    )
    return True
  except Exception as e:
    logger.exception(f'Error sending message from {hostname}.{msg.sender}')
    return False


async def _sender_loop():
  while 1:
    msg = await _msg_queue.get()
    while not (await _try_send_message(msg)):
      pass
