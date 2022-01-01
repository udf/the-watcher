import asyncio
import re

from systemd import journal

from bepis_bot.runtime import require, config, logger

core = require('core')
send_message = lambda s: core.send_message('systemd', s)

IGNORE_RE = {
  key: re.compile(regex)
  for key, regex in config['systemd.ignore_info'].items()
}

j = journal.Reader()
j.log_level(journal.LOG_INFO)
j.add_match(_COMM='systemd')
j.seek_tail()
j.get_previous()


def should_ignore(e):
  if e['PRIORITY'] < 6:
    return False
  for key, regex in IGNORE_RE.items():
    value = str(e.get(key, ''))
    if regex.search(value):
      logger.debug(f'Skipping {key}={value}, matches re {regex.pattern}')
      return True


def on_journal_change(j):
  if j.process() != journal.APPEND:
    return

  for e in j:
    if should_ignore(e):
      continue
    tag = e.get('UNIT') or e.get('USER_UNIT') or e["CODE_FUNC"]
    uid = e.get('_UID', 0)
    if uid:
      tag = f'{tag}@{uid}'
    send_message(f'<b>[{tag}]</b> {e["MESSAGE"]}')


async def on_load():
  loop = asyncio.get_event_loop()
  loop.add_reader(j, on_journal_change, j)
