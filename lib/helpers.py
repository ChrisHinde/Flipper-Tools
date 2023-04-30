if __name__ == '__main__':
  print("This isn't a runnable script! Please run ´subdecode.py´ instead!")
  exit(1)

from lib.config import settings

def deb(*arg, end="\n"):
  print(*arg, end=end) if settings['debug'] else None

def decode_format(out, zfill=0, hex=False):
  if hex:
    out = f'{out:x}'

  if settings['format_output']:
    return str(out).zfill(zfill).center(8)
  elif hex:
    return out.zfill(zfill)
  else:
    return str(out)
def decode_newline(time = None):
  if settings['format_output']:
    if settings['output_timestamps'] and time != None:
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
    print(str)