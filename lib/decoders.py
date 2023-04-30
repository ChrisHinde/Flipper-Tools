if __name__ == '__main__':
  print("This isn't a runnable script! Please run ´subdecode.py´ instead!")
  exit(1)

from lib.config import settings

def decoder_1(sigs, silence_avg):
  values = []
  time = 0
  for sig in sigs:
    tone    = sig[0]
    silence = sig[1]
    time += tone

    if silence > silence_avg * settings['silence_avg_ratio']:
      values.append(("-", time))
    elif tone < silence:
      values.append((0, time))
    else:
      values.append((1, time))

    time += silence

  return values