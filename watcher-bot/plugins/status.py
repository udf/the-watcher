# Shows online status (of all instances) in a pinned message

import asyncio
import json
import time
from random import randint
import dataclasses
from dataclasses import dataclass

from telethon import types
from telethon.tl.functions.users import GetFullUserRequest

from bepis_bot.runtime import client, logger, require, config

# how often to edit the message
update_period = 10
# how long to wait before marking a status as yellow
warning_time = update_period * 2
# how long to wait before marking a status as red
offline_time = update_period * 5

pinned_id = None
next_trigger_time = 0
trigger_offset = randint(0, update_period - 1)

core = require('core')


@dataclass
class StatusLine:
  status: str
  hostname: str = ''
  timestamp: str = '0'

  def as_line(self):
    return ' '.join(dataclasses.asdict(self).values())


def update_status_message(old_msg):
  status_lines = [StatusLine(*l.split(' ')) for l in old_msg.split('\n')[1:]]

  try:
    status = next(s for s in status_lines if s.hostname == core.hostname)
  except StopIteration:
    status = StatusLine('', core.hostname, 0)
    status_lines.append(status)
    status_lines = sorted(status_lines, key=lambda s: s.hostname)

  # TODO: store timestamp to detect race conditions

  current_timestamp = round(time.time())
  status.timestamp = str(current_timestamp)

  for s in status_lines:
    s.status = '🟩'
    delta = current_timestamp - int(s.timestamp)
    if delta >= warning_time:
      s.status = '🟨'
    if delta >= offline_time:
      s.status = '🟥'

  return (
    ''.join(s.status for s in status_lines) + '\n'
    + '\n'.join(s.as_line() for s in status_lines)
  )


async def update_pinned_id():
  global pinned_id
  r = await client(GetFullUserRequest(config.owner))
  current_pin = r.full_user.pinned_msg_id

  # TODO: try to edit or check date
  if not current_pin:
    m = await client.send_message(config.owner, 'placeholder please ignore')
    await client.pin_message(config.owner, m)
    pinned_id = m.id
    logger.info(f'Pinned new message #{pinned_id}')
    return

  if current_pin != pinned_id:
    logger.info(f'Found new pinned message #{current_pin} (prev was #{pinned_id})')
    pinned_id = current_pin


async def main_loop():
  global next_trigger_time
  if time.time() < next_trigger_time:
    return

  next_trigger_time = (time.time() // update_period) * update_period + update_period + trigger_offset
  await update_pinned_id()
  old_msg = await client.get_messages(config.owner, ids=pinned_id)
  new_msg = update_status_message(old_msg.raw_text)
  await client.edit_message(config.owner, message=pinned_id, text=new_msg)


async def on_load():
  asyncio.create_task(core.loop_runner(logger, main_loop))
