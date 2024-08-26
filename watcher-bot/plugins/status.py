# Shows online status (of all instances) in a pinned message

import asyncio
import dataclasses
import time
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from random import randint

from bepis_bot.runtime import client, config, logger, require
from telethon.tl.functions.users import GetFullUserRequest

HostState = namedtuple('HostState', ['name', 'delta'])

# how often to edit the message, period starts at epoch
# for example 60 would update every minute on the dot (plus a random offset)
UPDATE_PERIOD = 60
HOST_STATES = {
  '🟩': HostState('online', timedelta(seconds=0)),
  '🟨': HostState('unresponsive', timedelta(seconds=UPDATE_PERIOD * 2)),
  '🟥': HostState('offline', timedelta(seconds=UPDATE_PERIOD * 5)),
}
# how long a status message is valid for
MESSAGE_EXPIRY = timedelta(hours=24)

DATE_FMT = '%Y-%m-%dT%H:%M:%S'
next_trigger_time = 0
# offset to perform updates on
update_offset = randint(0, UPDATE_PERIOD - 1)
# last date we sent (to detect race conditions)
last_update_date = ''

core = require('core')
send_message = lambda s: core.send_message('status', s)


@dataclass
class StatusLine:
  status: str
  hostname: str = ''
  date: str = datetime.utcfromtimestamp(0).strftime(DATE_FMT)
  offset: str = '0'

  def as_line(self):
    return ' '.join(map(str, dataclasses.asdict(self).values()))


def update_status_message(old_msg):
  global last_update_date, update_offset
  status_lines = [StatusLine(*l.split(' ')) for l in old_msg.split('\n')[2:]]
  warnings = []

  try:
    status = next(s for s in status_lines if s.hostname == core.hostname)
  except StopIteration:
    status = StatusLine('?', core.hostname)
    status_lines.append(status)
    status_lines = sorted(status_lines, key=lambda s: s.hostname)

  # if status was present but it doesn't match our last date
  # another host might have caused us to lose an update,
  # randomise offset to try to prevent this from reoccuring
  if status.status != '?' and status.date != last_update_date:
    new_offset = randint(0, UPDATE_PERIOD - 1)
    warnings.append(f'Changing update offset from {update_offset} to {new_offset}')
    update_offset = new_offset

  current_time = datetime.utcnow()
  last_update_date = status.date = current_time.strftime(DATE_FMT)
  status.offset = update_offset

  for s in status_lines:
    new_state = '🟩'
    delta = current_time - datetime.strptime(s.date, DATE_FMT)
    for emoji, state in HOST_STATES.items():
      if delta >= state.delta:
        new_state = emoji
    if new_state != s.status:
      warnings.append(f'{s.hostname} is {HOST_STATES[new_state].name}')
    s.status = new_state

  return (
    ''.join(s.status for s in status_lines) + '\n\n'
    + '\n'.join(s.as_line() for s in status_lines)
  ), warnings


async def get_pinned_msg(force_create=False):
  r = await client(GetFullUserRequest(config.owner))
  current_pin = r.full_user.pinned_msg_id

  if current_pin:
    current_pin = await client.get_messages(config.owner, ids=current_pin)
    if datetime.utcnow() - current_pin.date.replace(tzinfo=None) > MESSAGE_EXPIRY:
      current_pin = None

  if not current_pin or force_create:
    m = await client.send_message(config.owner, 'placeholder please ignore', silent=True)
    await client.pin_message(config.owner, m)
    logger.info(f'Pinned new message #{m.id}')
    return m

  return current_pin


async def main_loop():
  global next_trigger_time
  if time.time() < next_trigger_time:
    return

  next_trigger_time = (time.time() // UPDATE_PERIOD) * UPDATE_PERIOD + UPDATE_PERIOD + update_offset

  old_msg = await get_pinned_msg()
  try:
    new_text, warnings = update_status_message(old_msg.raw_text)
  except:
    logger.exception('Error updating status message')
    old_msg = await get_pinned_msg(force_create=True)
    new_text, warnings = update_status_message(old_msg.raw_text)
  await client.edit_message(config.owner, message=old_msg, text=new_text)
  if warnings:
    send_message('\n'.join(warnings))


async def on_load():
  asyncio.create_task(core.loop_runner(logger, main_loop))
