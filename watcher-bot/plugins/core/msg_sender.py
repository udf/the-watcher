import asyncio
import time
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from socket import gethostname

from telethon.errors import MessageTooLongError
from telethon.extensions import html
from bepis_bot.runtime import client, logger, config

hostname = gethostname()
_msg_queues = defaultdict(asyncio.Queue)


@dataclass
class Message:
  content: str
  timestamp: float = field(default_factory=time.time)


def utc_fmt(ts=None):
  t = datetime.utcfromtimestamp(ts) if ts else datetime.utcnow()
  return t.strftime('%Y-%m-%d %H:%M:%S UTC')


def send_message(sender, content):
  for text in content.splitlines():
    for line in textwrap.wrap(text, width=4000):
      _msg_queues[sender].put_nowait(Message(line))


async def _try_send_message(text):
  raw_text, entities = html.parse(text)
  if len(raw_text) >= 4096:
    return MessageTooLongError(None)
  try:
    await client.send_message(
      config.owner,
      raw_text,
      formatting_entities=entities
    )
  except MessageTooLongError as e:
    return e
  except Exception as e:
    logger.exception(f'Error sending message')
    return e


async def _loop_send_message(text):
  while 1:
    err = await _try_send_message(text)
    if err is None or isinstance(err, MessageTooLongError):
      return err
    await asyncio.sleep(1)


def _format_msgs(sender, msgs):
  timestamp = msgs[0].timestamp
  content = '\n'.join(m.content for m in msgs)

  original_time = ''
  if time.time() - timestamp > 10:
    original_time = f'@{utc_fmt(timestamp)}'

  sep = '\n' if '\n' in content else ' '
  return f'<b>{hostname}.{sender}</b>{original_time}:{sep}{content}'


async def _send_all_messages(sender, q):
  msgs = []
  try:
    while 1:
      msgs.append(q.get_nowait())
  except asyncio.QueueEmpty:
    pass

  end = len(msgs)
  while msgs:
    text = _format_msgs(sender, msgs[:end])
    err = await _loop_send_message(text)
    if isinstance(err, MessageTooLongError):
      # retry without one less message
      if end > 1:
        end -= 1
        continue
      logger.error(f'Dropped message from {sender}: {msgs[0].content}')
      await _loop_send_message(
        f'Warning: dropping long message from {sender}, see log for details'
      )
    msgs = msgs[end:]
    end = len(msgs)


async def _sender_loop():
  while 1:
    await asyncio.sleep(5)
    for sender, q in _msg_queues.items():
      if not q.qsize():
        continue
      await _send_all_messages(sender, q)
