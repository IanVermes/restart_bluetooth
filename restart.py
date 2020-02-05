#!/usr/bin/env python3
# -*- codeing: utf8 -*-
"""
Restart OS X Bluetooth

OS X bluetooth devices sometimes disconnect and cannot reconnect without turn the
systems Bluetooth support off and then back on.

"""
import subprocess
import shlex
import getpass

__KEXT_NAME = "com.apple.iokit.BroadcomBluetoothHostControllerUSBTransport"


def prompt_password():
    password = getpass.getpass("Please enter your password: ")
    return password


def unload_kext(password):
    command_s = " ".join(["sudo -S kextunload -b", __KEXT_NAME])
    command = shlex.split(command_s)
    do_command(command, password)
    return


def load_kext(password):
    command_s = " ".join(["sudo -S kextload -b", __KEXT_NAME])
    command = shlex.split(command_s)
    do_command(command, password)
    return command


def do_command(command, password):
    process = subprocess.Popen(
        command,
        shell=False,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.communicate(password.encode())
    return


def main():
    password = prompt_password()
    unload_kext(password)
    load_kext(password)


if __name__ == "__main__":
    main()
