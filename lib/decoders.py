if __name__ == '__main__':
  print("This isn't a runnable script! Please run ´subdecode.py´ instead!")
  exit(1)

from config import settings

def decoder_0(sigs, silence_avg):
  values = []
  time = 0
  for sig in sigs:
    tone    = sig[0]
    silence = sig[1]
    time += tone

    if silence > silence_avg * settings['silence_avg_ratio']: # "ignore" long silences
      values.append(("-", time))
    elif tone < silence:
      values.append((0, time))
    else:
      values.append((1, time))

    time += silence

  return values

def decoder_1(sigs, silence_avg):
  values = []
  time = 0
  for sig in sigs:
    tone    = sig[0]
    silence = sig[1]
    time += tone

    if silence > silence_avg * settings['silence_avg_ratio']: # "ignore" long silences
      values.append(("-", time))
    elif tone < settings['tone_length'] and silence > settings['silence_length']:
      values.append((0, time))
    else:
      values.append((1, time))

    time += silence

  return values

def run_decoder(sigs, silence_avg):
  if settings['decode_method'] == 0:
    return decoder_0(sigs, silence_avg)
  elif settings['decode_method'] == 1:
    return decoder_1(sigs, silence_avg)

  print("Unknown decode method:", settings['decode_method'])
  return []