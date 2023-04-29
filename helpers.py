
debug_enabled = False

def enable_debug(en):
    global debug_enabled
    debug_enabled = en

def deb(*arg):
  print(*arg) if debug_enabled else None