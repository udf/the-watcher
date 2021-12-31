import asyncio

from systemd import journal

from bepis_bot.runtime import require

core = require('core')
send_message = lambda s: core.send_message('systemd', s)

j = journal.Reader()
j.log_level(journal.LOG_INFO)
j.add_match(_COMM='systemd')
j.seek_tail()
j.get_previous()


def on_journal_change(j):
  if j.process() != journal.APPEND:
    return

  for e in j:
    tag = e.get('UNIT') or e.get('USER_UNIT') or e["CODE_FUNC"]
    uid = e.get('_UID', 0)
    if uid:
      tag = f'{tag}@{uid}'
    send_message(f'<b>[{tag}]</b> {e["MESSAGE"]}')


async def on_load():
  loop = asyncio.get_event_loop()
  loop.add_reader(j, on_journal_change, j)
