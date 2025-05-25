owner = 1234567890
token = '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi'

flood_server_url = 'http://127.0.0.1:3000'

# Ignore anything not from systemd
#   https://www.freedesktop.org/software/systemd/man/systemd.journal-fields.html#_COMM=
# (`journalctl -eo verbose` shows all message fields)
# and ignore anything from systemd-tmpfiles-clean that's a notice or below
# PRIORITY is the same as https://en.wikipedia.org/wiki/Syslog#Severity_level
# tag is the string printed between the [] in the message, it's usually the same as e['UNIT']
def systemd_should_ignore(e, tag):
  if e['_COMM'] != 'systemd':
    return True
  unit = e.get('UNIT', '')
  return e['PRIORITY'] >= 5 and (
    unit == 'systemd-tmpfiles-clean.service'
  )