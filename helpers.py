debug_enabled = False
format_output = True

def enable_debug(en):
    global debug_enabled
    debug_enabled = en

def enable_format_output(en):
    global format_output
    format_output = en

def deb(*arg, end="\n"):
  print(*arg, end=end) if debug_enabled else None

def decode_format(out, zfill=0, hex=False):
  if hex:
    out = f'{out:x}'

  if format_output:
    return str(out).zfill(zfill).center(8)
  elif hex:
    return out.zfill(zfill)
  else:
    return str(out)
def decode_newline():
  return "\n     " if format_output else " "