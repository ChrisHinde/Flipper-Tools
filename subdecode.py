#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Created by Chris Hindefjord / chris.hindefjord.se
# 2023-04
#
# Licensed under MIT License (see LICENSE file for more information)
#
#  Usage : ./subdecode.py input.sub [> output]
VERSION      =    'v0.5a'
VERSION_DATE =    '230502'

import os
import re
import sys

# Check Python version before continuing
if sys.version_info.major < 3:
  import platform
  
  print("Python version (" + platform.python_version() + ") is too old! Please use Python3!")
  exit(30)

signals = []

from config import settings
from lib.decoders import *
from lib.helpers import *

shortest_tone = dict(tone = 10000000, silence = 0)
longest_tone = dict(tone = 0, silence = 0)
shortest_silence = dict(tone = 0, silence = -100000000)
longest_silence = dict(tone = 0, silence = 0)

def printHelp():
  print("Usage:", sys.argv[0], "INPUT_FILE [ARGS]\n"
  "Arguments:\n"
  "  -h       --help\t\tShow this text\n"
  "  -V,      --version\t\tShow the version of the script\n"
  "  -D,      --debug\t\tRun the script in debug/verbose mode\n"
  "    \t\t\t\t Outputs debug information to the console/STDOUT \n"
  "    \t\t\t\t (including some statistics) (NOTE: does not affect file output)\n\n"
  "  -b=X,    --begin=X\t\tStart processing at X microseconds (μs)\n"
  "    \t\t\t\t (exported timestamps will still be from the beginning of the data)\n"
  "  -e=X,    --end=X\t\tStop processing at X μs\n\n"

  "  -c,      --csv\t\tExport the data as CSV (Comma seperated values), don't decode\n"
  "  -ct,     --csv-time\t\tExport the data as CSV (Comma seperated values), but with \"running time\"\n"
  "  -cs,     --csv-add-end\tAdd an \"end point\" to the previous data point just before the next point\n"
  "    \t\t\t\t This helps when plotting the CSV data in a spreadsheet editor\n"
  "  -cd=X,   --csv-delimiter=X\tSet a custom delimiter for CSV export, Default: ,\n"
  "    \t\t\t\t Tip: You can set it to newline with -cd=\"\\n\" or -cd=\\\\n\n\n"

  "  -x=*,    --output-conv=*\tConvert the values to '*': binary (b), hexadecimal (h), decimal/numeric (d) and/or ascii (a)\n"
  "    \t\t\t\t Default: bhd\n"
  "  -w=X,    --word-size=X\tUse X as the \"word size\", Default: 8 (bits = 1 byte)\n"
  "  -nc,     --no-color\t\tDon't add color to the output (color is automatically turned off for file output)\n"
  "  -f,      --no-format\t\tDont't format the decoded output\n"
  "  -t,      --output-timestamps\tAdd timestamps (at \"breaks\") to the (formated) decoded output\n"
  "    \t\t\t\t This can help with selecting which part you want to limit the processing to\n\n"

  "  -o FILE, --output FILE\tOutput data to FILE instead of STDOUT")

def readArgs():
  global settings
  first = True
  is_output_file = False
  do_exit = -1

  for arg in sys.argv:
    if first:
      first = False
      continue

    if arg[0] == '-':
      if arg == '-c' or arg == '--csv':
        settings['mode'] = 1
      elif arg == '-ct' or arg == '--csv-time':
        settings['mode'] = 2
      elif arg == '-cs' or arg == '--csv-add-end':
        settings['add_time_end'] = True
      elif arg.startswith('-b=') or arg.startswith('--begin='):
        settings['start_limit'] = int(arg.split("=")[1])
      elif arg.startswith('-e=') or arg.startswith('--end='):
        settings['stop_limit'] = int(arg.split("=")[1])
      elif arg.startswith('-d=') or arg.startswith('--decode-method='):
        settings['decode_method'] = int(arg.split("=")[1])
      elif arg.startswith('-w=') or arg.startswith('--word-size='):
        settings['word_size'] = int(arg.split("=")[1])
      elif arg.startswith('-x=') or arg.startswith('--output-conv='):
        settings['output_flags'] = arg.split("=")[1].lower()
      elif arg.startswith('-cd=') or arg.startswith('--csv-delimiter='):
        settings['csv_delimiter'] = arg.split("=")[1].replace("\\n", "\n")
      elif arg == '-f' or arg == '--no-format':
        settings['format_output'] = False
      elif arg == '-nc' or arg == '--no-color':
        settings['output_color'] = False
      elif arg == '-t' or arg == '--output-timestamps':
        settings['output_timestamps'] = True
      elif arg == '-o' or arg == '--output':
        settings['output_to_file'] = True
        settings['output_color']   = False  # Turn of coloring of the output when exporting to file
        is_output_file = True
      elif arg == '-D' or arg == '--debug':
        settings['debug'] = True
      elif arg == '-h' or arg == '--help':
        printHelp()
        do_exit = 0
      elif arg == '-V' or arg == '--version':
        print("SubDecode", VERSION, "(" + VERSION_DATE + ")")
        do_exit = 0
      else:
        print("Unknown argument:", arg, "(Try '" + sys.argv[0] + " -h' for information on how to use the script)")
        do_exit = 1

    else:
      if is_output_file:
        settings['output_file'] = arg
        is_output_file = False
      else:
        settings['filename'] = arg

  if do_exit >= 0:
    exit(do_exit)

  if settings['output_to_file'] and settings['output_file'] == '':
    print("No output filename given! Exiting!")
    exit(4)

  # Change the width for center alignment depending on the 'biggest' format (bin/hex/dec) selected for output
  if 'b' not in settings['output_flags']:
    settings['align_width'] = 3 if 'd' in settings['output_flags'] else 2

def readFile():
  global signals, shortest_tone, longest_tone, shortest_silence, longest_silence

  deb("Reading File:", settings['filename'])

  if settings['filename'] == '':
    print("No Filename given! Exiting!")
    exit(2)
  if not os.path.isfile(settings['filename']):
    print("Can't find the file '" + settings['filename'] + "'! Exiting!")
    exit(3)

  with open(settings['filename'], 'r') as f:
    for line in f:
      m = re.match(r'RAW_Data:\s*([-0-9 ]+)\s*$', line)
      if m:
        parts = m[1].split()
        count = len(parts)
        if (count % 2):
          count -= 1

        for n in range(0, count, 2):
          tone = int(parts[n])
          silence = int(parts[n+1])

          if (tone < shortest_tone['tone']):
            shortest_tone['tone'] = tone
            shortest_tone['silence'] = silence
          elif (tone > longest_tone['tone']):
            longest_tone['tone'] = tone
            longest_tone['silence'] = silence
          if (silence > shortest_silence['silence']):
            shortest_silence['tone'] = tone
            shortest_silence['silence'] = silence
          elif (silence < longest_silence['silence']):
            longest_silence['tone'] = tone
            longest_silence['silence'] = silence

          signals.append((tone, silence))
      else:
        l = line.split(':')
        settings['file_info'][l[0]] = l[1].strip()

  if len(signals) == 0:
    print("No RAW data found! Exiting!")
    exit(4)

def outputCSV():
  csv = ""

  total_time = 0
  total_signals = 0

  for s in signals:
    total_time += s[0]

    if total_time < settings['start_limit']:
      total_time += abs(s[1])
      continue

    csv += str(s[0]) + settings['csv_delimiter'] + str(s[1]) + "\n"

    total_time += abs(s[1])

    total_signals += 1

    if (settings['stop_limit'] > 0) and (settings['stop_limit'] <= total_time):
      deb("Stopped at", total_time)
      break

  deb("Exported signal pairs:", total_signals)

  csv = csv.strip()

  output(csv)

def outputTimedCSV():
  csv = ""

  total_time = 0
  total_signals = 0

  for s in signals:
    total_time += s[0]

    if total_time < settings['start_limit']:
      total_time += abs(s[1])
      continue

    if settings['add_time_end']:
      csv += str(total_time - 1) + settings['csv_delimiter'] + "1\n"
    csv += str(total_time) + settings['csv_delimiter'] + "0\n"

    total_signals += 1

    if (settings['stop_limit'] > 0) and (settings['stop_limit'] <= total_time):
      deb("Stoped at", total_time)
      break

    total_time += abs(s[1])
    if settings['add_time_end']:
      csv += str(total_time - 1) + settings['csv_delimiter'] + "0\n"
    csv += str(total_time) + settings['csv_delimiter'] + "1\n"
    
    total_signals += 1

    if (settings['stop_limit'] > 0) and (settings['stop_limit'] <= total_time):
      deb("Stopped at", total_time)
      break

  csv = csv.strip()

  deb("Exported timed signals:", total_signals)

  output(csv)

def decode():
  total_time    = 0
  tone_total    = 0
  silence_total = 0
  silence_avg   = 0
  count         = 0
  sigs          = []
  values        = []
  first_after_limit = False

  sh_tone = dict(tone = 10000000, silence = 0)
  lon_tone = dict(tone = 0, silence = 0)
  sh_silence = dict(tone = 0, silence = 100000000)
  lon_silence = dict(tone = 0, silence = 0)

  # First, go through the signals, make them all posetive, collect statistics
  #  and, if set, limit them to the selected range
  for sig in signals:
    tone    = sig[0]
    silence = abs(sig[1])

    total_time += tone

    if total_time < settings['start_limit']:
      total_time += silence
      first_after_limit = True
      continue
    elif first_after_limit:
      settings['start_limit'] = total_time - tone
      first_after_limit = False

    total_time += silence

    tone_total    += tone
    silence_total += silence
    count         += 1

    if (tone < sh_tone['tone']):
      sh_tone['tone'] = tone
      sh_tone['silence'] = silence
    elif (tone > lon_tone['tone']):
      lon_tone['tone'] = tone
      lon_tone['silence'] = silence
    if (silence < sh_silence['silence']):
      sh_silence['tone'] = tone
      sh_silence['silence'] = silence
    elif (silence > lon_silence['silence']):
      lon_silence['tone'] = tone
      lon_silence['silence'] = silence

    sigs.append((tone, silence))
    
    if (settings['stop_limit'] > 0) and (settings['stop_limit'] <= total_time):
      deb("Stopped at", total_time)
      break

  settings['total_time'] = total_time
  if settings['output_timestamps']:
    settings['time_pad'] = len(str(total_time))

  silence_avg = silence_total / count
  incomplete = 0
  out = ""

  # Run the signals through the selected decoding
  values = run_decoder(sigs, silence_avg)

  # Output the results (if there are any)
  if len(values) == 0:
    print("No values to output!")
    deb("")
  else:
    c = 1
    bin_tmp = ''
    bin_out = decode_newline(values[0][1]) if 'b' in settings['output_flags'] else ""
    hex_out = decode_newline(values[0][1]) if 'h' in settings['output_flags'] else ""
    dec_out = decode_newline(values[0][1]) if 'd' in settings['output_flags'] else ""
    chr_out = decode_newline(values[0][1]) if 'a' in settings['output_flags'] else ""
    sum = 0

    # Output the decoded signals in a human-friendly format
    for v in values:
      if v[0] == '-':
        if c == 1:
          continue

        sum = int(bin_tmp, 2) if bin_tmp != '' else 0
        bin_out += bin_tmp
        bin_out += decode_newline(v[1]) if 'b' in settings['output_flags'] else ""
        hex_out += decode_format("-", 'h') + decode_newline(v[1]) if 'h' in settings['output_flags'] else ""
        dec_out += decode_format("-", 'd') + decode_newline(v[1]) if 'd' in settings['output_flags'] else ""
        chr_out += decode_format("-", 'a') + decode_newline(v[1]) if 'a' in settings['output_flags'] else ""

        bin_tmp = ""
        sum = 0
        c = 1
        incomplete += 1
        continue

      #sum += v[0] * 2**(8-c)
      bin_tmp += str(v[0])

      # If we have collected enough bits to make up a byte
      #  add it to the output (as binary, hexadecimal, and decimal)
      if c == settings['word_size']:
        sum = int(bin_tmp.zfill(settings['word_size']), 2)
        bin_out += bin_tmp + " " if 'b' in settings['output_flags'] else ""
        hex_out += decode_format(sum, 'h') + " " if 'h' in settings['output_flags'] else ""
        dec_out += decode_format(sum, 'd') + " " if 'd' in settings['output_flags'] else ""
        chr_out += decode_format(sum, 'a') + " " if 'a' in settings['output_flags'] else ""

        bin_tmp = ""
        sum = 0
        c = 1
      else:
        c += 1

    # If the values ended before a whole byte was collected
    #  output the incomplete binary, but skip converting to hex and decimal
    if bin_tmp != '':
      sum = int(bin_tmp, 2)
      bin_out += bin_tmp + " "
      hex_out += decode_format("-", 'h')
      dec_out += decode_format("-", 'd')
      chr_out += decode_format("-", 'a')
      incomplete += 1

    out = (c_lbl("Bin:")   + bin_out.rstrip() + "\n\n" if 'b' in settings['output_flags'] else "") + \
          (c_lbl("Hex:")   + hex_out.rstrip() + "\n\n" if 'h' in settings['output_flags'] else "") + \
          (c_lbl("Dec:")   + dec_out.rstrip() + "\n\n" if 'd' in settings['output_flags'] else "") + \
          (c_lbl("Ascii:") + chr_out.rstrip() + "\n"   if 'a' in settings['output_flags'] else "")

  # Output statistics
  deb("Decode Information:")
  deb(" Signal count:", count)
  deb(" Shortest tone:", sh_tone)
  deb(" Longest tone:", lon_tone)
  deb(" Shortest silence:", sh_silence)
  deb(" Longest silence:", lon_silence)
  deb(" Tone average:", tone_total / count)
  deb(" Silence average:", silence_avg)
  deb(" Incomplete bytes:", incomplete)

  if out != "":
    deb("")

    output(out)


# - - - - - MAIN - - - - - - -

readArgs()

deb("DEBUG MODE ENABLED!\n")

readFile()

deb("")
deb("File information:")
for fi in settings['file_info']:
  deb(" " + fi + ":", settings['file_info'][fi])

deb("\nIngest information:")
deb(" Total signal pairs:", len(signals))
deb(" Shortest tone:", shortest_tone)
deb(" Longest tone:", longest_tone)
deb(" Shortest silence:", shortest_silence)
deb(" Longest silence:", longest_silence)
deb("")


if settings['mode'] == 0:
  decode()
elif settings['mode'] == 1:
  outputCSV()
elif settings['mode'] == 2:
  outputTimedCSV()