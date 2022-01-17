import asyncio

from systemd import journal

from bepis_bot.runtime import require, config, logger

core = require('core')
send_message = lambda s: core.send_message('systemd', s)

should_ignore = getattr(config, 'systemd_should_ignore', lambda e: False)
priority_emoji = {
  journal.LOG_EMERG: '🆘',
  journal.LOG_ALERT: '🚨',
  journal.LOG_CRIT: '❗️',
  journal.LOG_ERR: '❌',
  journal.LOG_WARNING: '⚠️',
  journal.LOG_NOTICE: '💬',
  journal.LOG_INFO: 'ℹ️',
  journal.LOG_DEBUG: '🔤'
}

j = journal.Reader()
j.log_level(journal.LOG_INFO)
j.seek_tail()
j.get_previous()


def on_journal_change(j):
  if j.process() != journal.APPEND:
    return

  for e in j:
    if should_ignore(e):
      continue
    tag = (
      e.get('UNIT')
      or e.get('USER_UNIT')
      or e.get('_SYSTEMD_UNIT')
      or e.get('CODE_FUNC')
      or e.get('SYSLOG_IDENTIFIER')
      or e.get('_COMM')
    )
    uid = e.get('_UID', 0)
    if uid:
      tag = f'{tag}@{uid}'
    priority = priority_emoji.get(e['PRIORITY'], f'[{e["PRIORITY"]}]')
    send_message(f'{priority} <b>[{tag}]</b> {e["MESSAGE"].encode("unicode-escape").decode("utf-8")}')


async def on_load():
  loop = asyncio.get_event_loop()
  loop.add_reader(j, on_journal_change, j)
