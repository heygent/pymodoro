#!/usr/bin/env python
# authors: Dat Chu <dattanchu@gmail.com>
#          Dominik Mayer <dominik.mayer@gmail.com>
# Prerequisite
#  - aplay to play a sound of your choice
# To do
#  - add support for locking the screen with gnome-screensaver-command --lock
#  - add support for multiple counters
#  - add expected/finished number of pomodoros by weekday
#  - load configuration from file?

import time
import os
import sys
import argparse

from datetime import timedelta

# ———————————————————————————— CONFIGURATIONS ————————————————————————————

# Files and Folders
pymodoro_directory_config = '~/.pymodoro'
session_file_config = 'pomodoro_session'

# Times
session_duration_in_seconds = 25 * 60 +1
break_duration_in_seconds = 5 * 60
update_interval_in_seconds = 1

# Progress Bar
total_number_of_marks = 10
session_full_mark_character = '#'
break_full_mark_character = '|'
empty_mark_character = '·'

# Sound
enable_sound = True
session_sound_file_config = 'nokiaring.wav'
break_sound_file_config = 'rimshot.wav'

# —————————————————————————— END CONFIGURATIONS ———————————————————————————

# constant inferred from configurations
pymodoro_directory = os.path.expanduser(pymodoro_directory_config)
session_file = pymodoro_directory + '/' + session_file_config
session_sound_file = pymodoro_directory + '/' + session_sound_file_config
break_sound_file = pymodoro_directory + '/' + break_sound_file_config

def set_configuration_from_arguments(args):
	#print(args)
    global session_duration_in_seconds
    global break_duration_in_seconds
    global update_interval_in_seconds
    global total_number_of_marks
    global session_full_mark_character
    global break_full_mark_character
    global empty_mark_character
    global session_sound_file
    global break_sound_file
    global enable_sound
    if args.session_duration_in_seconds_arg:
        session_duration_in_seconds = args.session_duration_in_seconds_arg
    if args.session_duration_in_minutes_arg:
        session_duration_in_seconds = args.session_duration_in_minutes_arg * 60
    if args.break_duration_in_seconds_arg:
        break_duration_in_seconds = args.break_duration_in_seconds_arg
    if args.break_duration_in_minutes_arg:
        break_duration_in_seconds = args.break_duration_in_minutes_arg * 60
    if args.update_interval_in_seconds_arg:
        update_interval_in_seconds = args.update_interval_in_seconds_arg
    if args.total_number_of_marks_arg:
        total_number_of_marks = args.total_number_of_marks_arg
    if args.session_full_mark_character_arg:
        session_full_mark_character = args.session_full_mark_character_arg
    if args.break_full_mark_character_arg:
        break_full_mark_character = args.break_full_mark_character_arg
    if args.empty_mark_character_arg:
        empty_mark_character = args.empty_mark_character_arg
    if args.session_sound_file_arg:
        session_sound_file = args.session_sound_file_arg
    if args.break_sound_file_arg:
        break_sound_file = args.break_sound_file_arg
    if args.silent:
        enable_sound = False

# Parse command line arguments
parser = argparse.ArgumentParser(description='Create a Pomodoro display for a status bar.')

session_group = parser.add_mutually_exclusive_group()
session_group.add_argument('-ps', '--pomodoro-sec', action='store', type=int, help='Pomodoro duration in seconds (default: 25 * 60).', metavar='DURATION', dest='session_duration_in_seconds_arg')
session_group.add_argument('-pm', '--pomodoro-min', action='store', type=int, help='Pomodoro duration in minutes (default: 25).', metavar='DURATION', dest='session_duration_in_minutes_arg')

break_group = parser.add_mutually_exclusive_group()
break_group.add_argument('-bs', '--break-sec', action='store', type=int, help='Break duration in seconds (default: 5 * 60).', metavar='DURATION', dest='break_duration_in_seconds_arg')
break_group.add_argument('-bm', '--break-min', action='store', type=int, help='Break duration in minutes (default: 5).', metavar='DURATION', dest='break_duration_in_minutes_arg')

parser.add_argument('-i', '--interval', action='store', type=int, help='Update interval in seconds (default: 1).', metavar='DURATION', dest='update_interval_in_seconds_arg')
parser.add_argument('-l', '--length', action='store', type=int, help='Bar length in characters (default: 10).', metavar='CHARACTERS', dest='total_number_of_marks_arg')

parser.add_argument('-fp', '--full-pomodoro', action='store', help='Pomodoro full mark characters (default: #).', metavar='CHARACTER', dest='session_full_mark_character_arg')
parser.add_argument('-fb', '--full-break', action='store', help='Break full mark characters (default: |).', metavar='CHARACTER', dest='break_full_mark_character_arg')
parser.add_argument('-e', '--empty', action='store', help='Empty mark characters (default: ·).', metavar='CHARACTER', dest='empty_mark_character_arg')

parser.add_argument('-sp', '--sound-pomodoro', action='store', help='Pomodoro end sound file (default: nokiaring.wav).', metavar='PATH', dest='session_sound_file_arg')
parser.add_argument('-sb', '--sound-break', action='store', help='Break end sound file (default: rimshot.wav).', metavar='PATH', dest='break_sound_file_arg')
parser.add_argument('-s', '--silent', action='store_true', help='Play no end sounds', dest='silent')

args = parser.parse_args()
set_configuration_from_arguments(args)


# variables to keep track of sound playing
play_sound_after_session = False
play_sound_after_break = False

# sanity check
if not os.path.exists(session_sound_file):
    print("Error: Cannot find sound file %s" % sound_file)
if not os.path.exists(break_sound_file):
    print("Error: Cannot find sound file %s" % sound_file)
if not os.path.exists(session_file):
    print("Error: Cannot find session file %s. Please make it." % session_file)

def get_seconds_left():
    start_time = os.path.getmtime(session_file)
    return session_duration_in_seconds - time.time() + start_time

def print_session_output(seconds_left):
    print_output("P", session_duration_in_seconds, seconds_left, session_full_mark_character)

def print_break_output(seconds_left):
    break_seconds_left = get_break_seconds_left(seconds_left)
    print_output("B", break_duration_in_seconds, break_seconds_left, break_full_mark_character)

def get_break_seconds_left(seconds):
    return break_duration_in_seconds + seconds

def print_output(description, duration_in_seconds, seconds, full_mark_character):
    minutes = get_minutes(seconds)
    output_seconds = get_output_seconds(seconds)
    progress_bar = print_progress_bar(duration_in_seconds, seconds, full_mark_character)
    sys.stdout.write(description + " %s %02d:%02d\n" % (progress_bar, minutes, output_seconds))

def get_minutes(seconds):
    return int(seconds / 60)

def get_output_seconds(seconds):
    minutes = get_minutes(seconds)
    return int(seconds - minutes * 60)

def print_progress_bar(duration_in_seconds, seconds, full_mark_character):
    seconds_per_mark = (duration_in_seconds / total_number_of_marks)
    number_of_full_marks = int(seconds / seconds_per_mark)
    return print_full_marks(number_of_full_marks, full_mark_character) + print_empty_marks(total_number_of_marks - number_of_full_marks)
    
def print_full_marks(number_of_full_marks, full_mark_character):
    return full_mark_character * number_of_full_marks

def print_empty_marks(number_of_empty_marks):
    return empty_mark_character * number_of_empty_marks

def print_break_output_hours(seconds):
    seconds = -seconds
    minutes = get_minutes(seconds)
    output_minutes = get_output_minutes(seconds)
    hours = get_hours(seconds)
    output_seconds = get_output_seconds(seconds)

    if minutes <= 60:
        sys.stdout.write("B %02d:%02d min\n" % (minutes, output_seconds))
    else:
        sys.stdout.write("B %02d:%02d h\n" % (hours, output_minutes))
    
def get_hours(seconds):
    return int(seconds / 3600)

def get_output_minutes(seconds):
    hours = get_hours(seconds)
    minutes = get_minutes(seconds)
    return int(minutes - hours * 60)

def play_sound(sound_file):
    if enable_sound:
        os.system('aplay -q %s &' % sound_file)

def play_session_sound():
    global play_sound_after_session
    if play_sound_after_session:
        play_sound_after_session = False
        play_sound(session_sound_file)

def play_break_sound():
    global play_sound_after_break
    if play_sound_after_break:
        play_sound_after_break = False
        play_sound(break_sound_file)

# Repeat printing the status of our session
seconds_left = get_seconds_left()
while True:
    if 0 < seconds_left:
        print_session_output(seconds_left)
        play_sound_after_session = True
    elif -break_duration_in_seconds <= seconds_left < 0:
        play_session_sound()
        print_break_output(seconds_left)
        play_sound_after_break = True
    else:
        play_break_sound()
        print_break_output_hours(seconds_left)
        
    sys.stdout.flush()
    
    time.sleep(update_interval_in_seconds)

    seconds_left = get_seconds_left()
