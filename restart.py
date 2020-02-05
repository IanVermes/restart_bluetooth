#!/usr/bin/env python3
# -*- codeing: utf8 -*-
"""
Restart OS X Bluetooth

OS X bluetooth devices sometimes disconnect and cannot reconnect without turn the
systems Bluetooth support off and then back on.

"""
import subprocess
import shlex
import time


def is_blueutil():
    # We need this program
    command_s = "which blueutil"
    command = shlex.split(command_s)
    result = do_command(command, capture_output=True)
    return result.returncode == 0


def stop_bluetooth_service():
    command_s = "blueutil -p 0"
    command = shlex.split(command_s)
    do_command(command, check=True)
    return


def start_bluetooth_service():
    command_s = "blueutil -p 1"
    command = shlex.split(command_s)
    do_command(command, check=True)
    return command


def wait():
    time.sleep(1)


def do_command(command, *_, **kwargs):
    result = subprocess.run(command, **kwargs)
    return result


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
