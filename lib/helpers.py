if __name__ == '__main__':
  print("This isn't a runnable script! Please run ´subdecode.py´ instead!")
  exit(1)

from config import settings

# Color helpers
def c_wrap(str, color):           #  Wrap output string with ASCII escape codes for coloring
  pre = ""
  suf = ""

  if settings['output_color']:
    pre = "\033[" + color + "m"
    suf = "\033[0m"

  return pre + str + suf
def c_lbl(str):                   # Color labels (Bin, Hex, etc) green
  return c_wrap(str, '0;32')
def c_ts(str):                    # Color timestamps cyan
  return c_wrap(str, '0;36')
def c_d(str, blank = False):      # Color data output white (or red for "blank")
  col = '1;37' if not blank else '0;31'
  return c_wrap(str, col)

# Output debug info
def deb(*arg, end="\n"):
  print(*arg, end=end) if settings['debug'] else None

# Format the decode outpet
def decode_format(out, type=''):
  zfill = 0
  blank = out == '-'

  if type == 'h':
    if out != '-':
      out = f'{out:x}'
      zfill = 2
    else:
      out = '-'
    if settings['word_size'] <= 4:
      zfill = 1
  if type == 'd':
    if settings['format_output']:
      if settings['word_size'] <= 4:
        out = str(out).rjust(2)
      elif not blank:
        out = str(out).rjust(3)
    zfill = 0
  if type == 'a':
    if blank:
      out = "-"
    else:
      out = chr(out)

  if settings['format_output']:
    if type == 'a':
      out = out.ljust(settings['align_width'])
    else:
      out = str(out).zfill(zfill).center(settings['align_width'])
  elif type == 'h':
    out = out.zfill(zfill)
  else:
    out = str(out)

  return c_d(out, blank)

# Format new lines for decode output
def decode_newline(time = None):
  if settings['format_output']:
    if settings['output_timestamps'] and time != None:
      time += settings['start_limit'] if settings['start_limit'] != -1 else 0
      return "\n " + c_ts(str(time).ljust(settings['time_pad'] + 2))
    else:
      return "\n".ljust(settings['time_pad'] + 2)
  else:
    return " "

# Output the data to a file or stdout
def output(str):
  if settings['output_to_file']:
    with open(settings['output_file'], 'w') as f:
      f.write(str)
    print("Data vas exported to", settings['output_file'])
  else:
    print(str.strip())