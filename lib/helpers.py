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
def decode_newline():
  return "\n     " if settings['format_output'] else " "