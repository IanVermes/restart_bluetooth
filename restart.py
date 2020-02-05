#!/usr/bin/python
# -*- codeing: utf8 -*-
"""
Restart OS X Bluetooth

OS X bluetooth devices sometimes disconnect and cannot reconnect without turn the
systems Bluetooth support off and then back on.

`$ python restart.py`
or
`$ python restart.py $PATH_TO_HOMEBREW_INSTALL_DIR "platypus"`

The $PATH_TO_HOMEBREW_INSTALL_DIR value may be something like `/usr/local/bin` and is a
pass-through value for things Desktop app wrappers like Platypus.
"""
from __future__ import print_function

import os
import sys
import subprocess
import shlex
import time

PY3 = sys.version_info.major >= 3


class Constants(object):
    def __init__(self):
        self.use_platypus = False
        self.program = "blueutil"
        self.blueutil = self.program


class PlatypusPrint:
    def __init__(self, constants):
        self._constants = constants

    def alert(self, title, message):
        if self._constants.use_platypus:
            self.print("ALERT:%s|%s\n" % title, message)
        else:
            alert_message = "\aALERT: %s" % message
            self.print(alert_message)

    def notification(self, message):
        if self._constants.use_platypus:
            self.print("NOTIFICATION:%s\n" % message)
        else:
            self.print(message)

    def progress_bar(self, percent):
        if self._constants.use_platypus:
            self.print("PROGRESS:%i\n" % int(percent))

    def progress_bar_show_details(self):
        self.print("DETAILS:SHOW\n")

    def progress_bar_hide_details(self):
        self.print("DETAILS:HIDE\n")

    def exit_gui(self):
        if self._constants.use_platypus:
            print("QUITAPP\n")
        else:
            exit(0)

    def print(self, message):
        if PY3:
            print(message, flush=True)
        else:
            print(message)
            sys.stdout.flush()


CONSTANTS = Constants()
PRINTER = PlatypusPrint(CONSTANTS)


def _is_blueutil():
    # We need this program
    command_s = "which %s" % CONSTANTS.blueutil
    command = shlex.split(command_s)
    result = _do_command(command, capture_output=True)
    return result == 0


def stop_bluetooth_service():
    command_s = "%s -p 0" % CONSTANTS.blueutil
    command = shlex.split(command_s)
    _do_command(command, check=True)
    return


def start_bluetooth_service():
    command_s = "%s -p 1" % CONSTANTS.blueutil
    command = shlex.split(command_s)
    _do_command(command, check=True)
    return command


def auto_exit():
    duration = 10  # Seconds
    time_stop = time.time() + duration
    while True:
        if time.time() > time_stop:
            break
        else:
            wait()
    PRINTER.exit_gui()


def wait():
    time.sleep(1)


def _do_command(command, check=False, capture_output=False):
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


def _process_constants():
    # set `blueutil`
    try:
        brew_directory = sys.argv[1]
    except IndexError:
        brew_directory = ""

    if brew_directory:
        fullpath = os.path.join(brew_directory, CONSTANTS.program)
    else:
        fullpath = CONSTANTS.program
    CONSTANTS.blueutil = fullpath

    # set `use_platypus`
    try:
        raw_platypus = sys.argv[2]
    except IndexError:
        raw_platypus = ""

    if raw_platypus:
        use_platypus = "platypus" in raw_platypus.lower().strip()
    else:
        use_platypus = False
    CONSTANTS.use_platypus = use_platypus
    return


def main():
    if not _is_blueutil():
        PRINTER.alert(
            "Oh no!",
            "Install blueutil first, then run script again\n"
            "  $ brew install blueutil",
        )
    else:
        bar = [
            (stop_bluetooth_service, "BlueTooth OFF"),
            (wait, ""),
            (wait, ""),
            (start_bluetooth_service, "BlueTooth ON"),
            (wait, ""),
            (wait, ""),
            (None, "Done!"),
            (wait, ""),
        ]
        PRINTER.progress_bar_show_details()
        PRINTER.progress_bar(0)
        for i, (func, message) in enumerate(bar):
            percent = int(float(i) / len(bar) * 100)
            if func is not None:
                func()

            if message:
                PRINTER.print(message)
            PRINTER.progress_bar(percent)
        else:
            PRINTER.progress_bar(100)
            PRINTER.progress_bar_hide_details()
            PRINTER.print("\n\n\n(... automatically quitting in 10 seconds ...)")
            auto_exit()


if __name__ == "__main__":
    _process_constants()
    main()
