# Copyright (C) 2020-2024, Svetlin Ankov

# TODO: Support for different ADB versions
# verified with adb:
# 30.0.5-6877874
from enum import Enum
from shutil import which
import re
import subprocess


class ADB(object):
    DEBUG = False

    def __init__(self, name):
        self._name = name

    State = Enum('State', [
        'OFFLINE',
        'BOOTLOADER',
        'DEVICE',
        'RECOVERY',
        'RESCUE',
        'SIDELOAD',
        'DISCONNECT',
    ])

    Transport = Enum('Transport', [
        'USB',
        'LOCAL',
        'ANY',
    ])

    @classmethod
    def available(cls):
        return which('adb')

    def command(self, command, binary=False):
        if not isinstance(command, list):
            command = [ command ]

        cmd = [ 'adb', '-s', self.name ] + command

        if self.DEBUG:
            print(" ".join(cmd))

        return subprocess.check_output(cmd, stderr=subprocess.PIPE, universal_newlines=not binary)

    @property
    def name(self):
        return self._name

    def shell(self, cmd):
        if isinstance(cmd, list):
            cmd = " ".join(cmd)

        return self.command(
            ['shell', cmd, ]
        )

    def exec_out(self, cmd):
        return self.command(
            [ 'exec-out', cmd, ], binary=True
        )

    def get_state(self):
        state = self.command('get-state')
        state = state.splitlines()[0].upper()

        if state not in ADB.State.__members__:
            raise Exception("Unknown state " + state)

        return ADB.State.__members__[state]

    def wait(self, transport=None, state=State.DEVICE):
        # Backward compatibility if transport is not present
        transport = "-" + transport.name.lower() if transport else ""
        state = state.name.lower()

        self.command('wait-for{}-{}'.format(transport, state))

    PORT = 5555

    @classmethod
    def connect(cls, host, port=PORT):
        # adb connect does not return error code on error
        # and uses stdout for error messages
        return subprocess.check_output(
            ['adb', 'connect', '{}:{}'.format(host, port)],
            universal_newlines=True
        )

    @classmethod
    def disconnect(cls, host=None, port=PORT):
        cmd = ['adb', 'disconnect']
        if host:
            cmd.append('{}:{}'.format(host, port))

        subprocess.check_call(cmd)

    @classmethod
    def create_default(cls, *args, **kargs):
        devices = cls.list_devices()

        if not devices:
            raise Exception("No devices found")
        elif len(devices) > 1:
            raise Exception("Multiple devices found")

        return cls(devices[0], *args, **kargs)

    DEVICES_PATTERN = re.compile(r'^(.*?)\W+device$', re.MULTILINE)

    @staticmethod
    def list_devices():
        out = subprocess.check_output(
            [ 'adb', 'devices' ],
            universal_newlines=True
        )

        return ADB.DEVICES_PATTERN.findall(out)
