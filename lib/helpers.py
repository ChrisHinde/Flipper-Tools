if __name__ == '__main__':
  print("This isn't a runnable script! Please run ´subdecode.py´ instead!")
  exit(1)

from lib.config import settings

def deb(*arg, end="\n"):
  print(*arg, end=end) if settings['debug'] else None

def decode_format(out, type=''):
  zfill = 0

  if type == 'h':
    out = f'{out:x}' if out != '-' else '-'
    if settings['word_size'] <= 4:
      zfill = 1
  if type == 'd':
    if settings['format_output']:
      if settings['word_size'] <= 4:
        out = str(out).rjust(2)
      elif out != '-':
        out = str(out).rjust(3)
    zfill = 0
  if type == 'a':
    if out == '-':
      out = " "
    else:
      out = chr(out)

  if settings['format_output']:
    if type == 'a':
      return out.ljust(settings['align_width'])
    else:
      return str(out).zfill(zfill).center(settings['align_width'])
  elif type == 'h':
    return out.zfill(zfill)
  else:
    return str(out)

def decode_newline(time = None):
  if settings['format_output']:
    if settings['output_timestamps'] and time != None:
      time += settings['start_limit'] if settings['start_limit'] != -1 else 0
      return "\n " + str(time).ljust(settings['time_pad'] + 2)
    else:
      return "\n".ljust(settings['time_pad'] + 2)
  else:
    return " "

def output(str):
  if settings['output_to_file']:
    with open(settings['output_file'], 'w') as f:
      f.write(str)
    print("Data vas exported to", settings['output_file'])
  else:
    print(str.strip())