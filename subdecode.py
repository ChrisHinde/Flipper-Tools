# -*- coding: utf-8 -*-

# Created by Chris Hindefjord / chris.hindefjord.se
# 2023-04
#
# Licensed under MIT License (see LICENSE file for more information)
#
#  Usage : ./subdecode.py input.sub [> output]
VERSION      =    'v0.2a'
VERSION_DATE =    '230429'

import os
import re
import sys
import math

# Check Python version before continuing
if sys.version_info.major < 3:
  import platform
  
  print("Python version (" + platform.python_version() + ") is too old! Please use Python3!")
  exit(30)

settings = dict(
    filename       = "",

    output_to_file = False,
    output_file    = "",

    mode           = 0,
    add_time_end   = False,

    start_limit    = -1,
    stop_limit     = -1,

    debug          = False
)
signals = []
#data_len = 0

from helpers import *

shortest_tone = dict(tone = 10000000, silence = 0)
longest_tone = dict(tone = 0, silence = 0)
shortest_silence = dict(tone = 0, silence = -100000000)
longest_silence = dict(tone = 0, silence = 0)

def printHelp():
  print("Usage:", sys.argv[0], "[ARGS] input_file\n"
  "Arguments:\n"
  "  -h       --help\t\tShow this text\n"
  "  -V,      --version\t\tShow the version of the script\n"
  "  -D,      --debug\t\tRun the script in debug mode\n"
  "    \t\t\t\t Outputs debug information to the console/STDOUT \n"
  "    \t\t\t\t (including some statistics) (NOTE: does not affect file output)\n"
  "  -c,      --csv\t\tExport the data as CSV (Comma seperated values)\n"
  "  -ct,     --csv-time\t\tExport the data as CSV (Comma seperated values), but \"timed\"\n"
  "  -cs,     --csv-add-end\tAdd an \"end point\" to the previous data point just before the next point\n"
  "    \t\t\t\t This helps when plotting the CSV data in a spreadsheet editor\n"
  "  -b=X,    --begin=X\t\tStart processing at X microseconds (μs)\n"
  "    \t\t\t\t (exported timestamps will still be from the beginning of the data)\n"
  "  -e=X,    --end=X\t\tStop processing at X μs\n"
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
      elif arg == '-o' or arg == '--output':
        settings['output_to_file'] = True
        is_output_file = True
      elif arg == '-D' or arg == '--debug':
        settings['debug'] = True
        enable_debug(True)
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
          #data_len = int(parts[count])

        for n in range(0, count, 2):
          tone = int(parts[n])
          silence = int(parts[n+1])

          #shortest_tone
          # = min(shortest_tone
          #['tone'], tone)
          #longest_tone = max(longest_tone['tone'], tone)
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

  if len(signals) == 0:
    print("No RAW data found! Exiting!")
    exit(4)

def output(str):
  if settings['output_to_file']:
    with open(settings['output_file'], 'w') as f:
      f.write(str)
    print("Data vas exported to", settings['output_file'])
  else:
    print(str)

def outputCSV():
  csv = ""
  
  total_time = 0
  total_signals = 0

  for s in signals:
    total_time += s[0]
    
    if total_time < settings['start_limit']:
      total_time += abs(s[1])
      continue

    csv += str(s[0]) + "," + str(s[1]) + "\n"
    
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
      csv += str(total_time - 1) + ",1\n"
    csv += str(total_time) + ",0\n"
    
    total_signals += 1
    
    if (settings['stop_limit'] > 0) and (settings['stop_limit'] <= total_time):
      deb("Stoped at", total_time)
      break

    total_time += abs(s[1])
    if settings['add_time_end']:
      csv += str(total_time - 1) + ",0\n"
    csv += str(total_time) + ",1\n"
    
    total_signals += 1

    if (settings['stop_limit'] > 0) and (settings['stop_limit'] <= total_time):
      deb("Stopped at", total_time)
      break
  
  csv = csv.strip()
  
  deb("Exported timed signals:", total_signals)

  output(csv)

def decode():

  for sig in signals:
    print(sig)

# - - - - - MAIN - - - - - - -

readArgs()

deb("DEBUG MODE ENABLED!")

readFile()

deb("Total signal pairs:", len(signals))
deb("Shortest tone:", shortest_tone)
deb("Longest tone:", longest_tone)
deb("Shortest silence:", shortest_silence)
deb("Longest silence:", longest_silence)


if settings['mode'] == 0:
  decode()
elif settings['mode'] == 1:
  outputCSV()
elif settings['mode'] == 2:
  outputTimedCSV()