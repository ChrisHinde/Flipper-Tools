if __name__ == '__main__':
  print("This isn't a runnable script! Please run ´subdecode.py´ instead!")
  exit(1)

settings = dict(
  filename          = "",

  output_to_file    = False,
  output_file       = "",

  mode              = 0,
  add_time_end      = False,

  auto_detect       = False,

  start_limit       = -1,
  stop_limit        = -1,

  format_output     = True,

  decode_method     = 1,

  silence_avg_ratio = 1.5,
  tone_length       = 500,
  silence_length    = 1000,

  debug             = False,
)