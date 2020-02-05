#!/usr/bin/python
# -*- codeing: utf8 -*-
"""
Restart OS X Bluetooth

OS X bluetooth devices sometimes disconnect and cannot reconnect without turn the
systems Bluetooth support off and then back on.

$ python restart.py
or
$ python restart.py $PATH_TO_HOMEBREW_INSTALL_DIR

The $PATH_TO_HOMEBREW_INSTALL_DIR value may be something like `/usr/local/bin` and is a
pass-through value for things Desktop app wrappers like Platypus.
"""
import os
import sys
import subprocess
import shlex
import time

PY3 = sys.version_info.major >= 3


def is_blueutil():
    # We need this program
    command_s = "which %s" % process_blueutil_path()
    command = shlex.split(command_s)
    result = do_command(command, capture_output=True)
    return result == 0


def stop_bluetooth_service():
    command_s = "%s -p 0" % process_blueutil_path()
    command = shlex.split(command_s)
    do_command(command, check=True)
    print("BlueTooth OFF")
    return


def start_bluetooth_service():
    command_s = "%s -p 1" % process_blueutil_path()
    command = shlex.split(command_s)
    do_command(command, check=True)
    print("BlueTooth ON")
    return command


def wait():
    print("...")
    time.sleep(1)


def do_command(command, check=False, capture_output=False):
    if PY3:
        process_obj = subprocess.run(
            command, capture_output=capture_output, check=check
        )
        check_code = process_obj.returncode
    else:
        check_code = _do_command_py2(command, check, capture_output)
    return check_code


def _do_command_py2(command, check=False, capture_output=False):
    if capture_output:
        PIPE = subprocess.PIPE
    else:
        PIPE = None
    if check:
        check_code = subprocess.check_call(command, stdout=PIPE)
    else:
        check_code = subprocess.call(command, stdout=PIPE)
    return check_code


def process_blueutil_path():
    try:
        brew_directory = sys.argv[1]
    except IndexError:
        brew_directory = ""

    basename = "blueutil"
    if brew_directory:
        fullpath = os.path.join(brew_directory, basename)
    else:
        fullpath = basename
    return fullpath


def main():
    if not is_blueutil():
        print(
            "\aInstall blueutil first, then run script again\n"
            "  $ brew install blueutil"
        )
    else:
        stop_bluetooth_service()
        wait()
        start_bluetooth_service()


if __name__ == "__main__":
    main()
