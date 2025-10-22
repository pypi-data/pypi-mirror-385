#!/usr/bin/env python3
from __future__ import annotations

import typing
import argparse
import textwrap
from pathlib import Path
from shutil import which
import os
import sys
import getpass
import time
from curses.ascii import unctrl
import subprocess

import signal
import struct
import termios
import fcntl

from configparser import ConfigParser, ParsingError
import re

try:
    import pexpect
except ImportError:
    print('pexpect not installed')
    sys.exit(1)
try:
    from exbw import BwData

    USE_BW = True
except ImportError:
    USE_BW = False


def get_bw_password(name: str, *, debug: bool = False) -> str | None:
    bw = BwData(f'{name}', debug=debug)
    return bw.get_data('password')


class PtyInteract:
    def __init__(
        self,
        host: str,
        command: str,
        *,
        use_bw: bool = False,
        timeout: int = 30,
        expect_config: typing.Mapping[str, str] | None = None,
        copy_config: typing.Mapping[str, str] | None = None,
        debug: bool = False,
    ) -> None:
        self.prompt = r'[$#>/%:](\s*|\x1b.*)$'

        print(f'Connecting by: {command}')
        self.child = pexpect.spawn(command, timeout=timeout, encoding='utf8')
        self.debug = debug
        if debug:
            self.child.logfile = sys.stdout
        self.set_sigwinch()
        signal.signal(signal.SIGWINCH, self.set_sigwinch)
        self.host = host
        self.lag = None
        self.use_bw = use_bw
        self.expect_list = None
        self.expect_cursor = 0
        if expect_config:
            self.expect_list = list(expect_config.items())
            if self.expect_list and self.expect_list[0][0] == 'prompt':
                self.prompt = self.expect_list[0][1]
                self.expect_cursor = 1
        self.escape = '\x1d'
        self.input_buffer = b''
        self.input_detect_start = b'\x60\x60'
        self.input_detect_end = b'\x09'
        self.copy_config = copy_config
        if self.copy_config:
            if self.copy_config.get('start'):
                self.input_detect_start = eval(self.copy_config.get('start', ''))
            if self.copy_config.get('end'):
                self.input_detect_end = eval(self.copy_config.get('end', ''))
        try:
            self.login()
        except KeyboardInterrupt:
            pass

    def _pty_size(self) -> tuple:
        fmt = 'HH'
        buf = struct.pack(fmt, 0, 0)
        try:
            result = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, buf)
            rows, cols = struct.unpack(fmt, result)
            return (rows, cols)
        except (struct.error, TypeError, IOError, AttributeError):
            pass
        return (None, None)

    def term_size(self) -> tuple:
        rows, cols = self._pty_size()
        return ((rows or 24), (cols or 80))

    def set_sigwinch(self, signum=None, frame=None) -> None:
        term_size = self.term_size()
        if getattr(self, 'child', None) and not self.child.closed:
            self.child.setwinsize(term_size[0], term_size[1])

    def login(self) -> None:
        start_timer = time.time()
        timeout = -1
        if self.lag is not None:
            if self.lag < 0.5:
                timeout = 1
            elif self.lag < 1.5:
                timeout = 3
            elif self.lag < 2.5:
                timeout = 5
        res = self.child.expect(
            [
                pexpect.TIMEOUT,
                pexpect.EOF,
                r'(?i)\(yes/no/\[fingerprint\]\)\?',
                r'(?i)\'s password:',
                r'(?i)(?<=passphrase for )(key.*)',
                r'(?i)permission denied',
                self.prompt,
            ],
            timeout=timeout,
        )
        self.lag = time.time() - start_timer
        text_before = ''
        if isinstance(self.child.before, str):
            text_before = self.child.before
        text_after = ''
        if isinstance(self.child.after, str):
            text_after = self.child.after
        if res == 0:
            print(f'Escape: {unctrl(self.escape)}')
            print('no propmt')
            self.start_interaction()
        elif res == 1:
            print(text_before)
            self.child.close()
        elif res == 2:
            print(text_before, end='')
            print(text_after)
            cmd = input()
            self.child.sendline(cmd)
            if cmd.lower() == 'yes':
                self.login()
            else:
                self.child.close()
        elif res == 3:
            password: str = self.get_password(text_before.strip())
            self.child.sendline(password)
            self.login()
        elif res == 4:
            password = self.get_password(text_after.strip(':\n '))
            self.child.sendline(password)
            self.login()
        elif res == 5:
            print(text_before.strip(), end='')
            print(text_after)
            self.login()
        elif res == 6:
            print(f'Escape: {unctrl(self.escape)}')
            print(text_before.strip(), end='')
            print(text_after, end='', flush=True)
            self.start_interaction()

    def get_password(self, identity: str) -> str:
        password = None
        if self.use_bw:
            print('<-- Using BW PWD Manager -->')
            for _ in range(3):
                password = get_bw_password(self.host, debug=self.debug)
                if password is not None:
                    self.use_bw = False
                    break
        if not password:
            password = getpass.getpass(f'Password for {identity}:')
        return password

    def start_interaction(self) -> None:
        self.child.logfile = None
        self.child.interact(
            escape_character=self.escape,
            output_filter=self.output_filter,
            input_filter=self.input_filter,
        )

    def output_filter(self, data: bytes) -> bytes:
        if self.expect_list and self.expect_cursor < len(self.expect_list):
            expect_tuple = self.expect_list[self.expect_cursor]
            if expect_tuple[0] in data.decode().lower():
                if self.debug:
                    print(expect_tuple)
                self.child.sendline(expect_tuple[1])
                self.expect_cursor += 1
        return data

    def input_filter(self, data: bytes) -> bytes:
        self.input_buffer += data
        if (
            self.input_detect_start in self.input_buffer
            and self.input_detect_end in self.input_buffer
            and self.copy_config
            and (
                search := re.search(
                    f'(?<={self.input_detect_start.decode("utf8")})([^{self.input_detect_start.decode("utf8")}]+)(?={self.input_detect_end.decode("utf8")})',
                    self.input_buffer.decode('utf8'),
                )
            )
        ):
            cfg_key = search[0]
            if self.debug:
                print(cfg_key)
            if filepath := self.copy_config.get(cfg_key):
                if sys.platform == 'linux':
                    cmd = f'cat {filepath} | xsel -b'
                elif (
                    sys.platform == 'win32'
                    or sys.platform == 'cygwin'
                    or sys.platform == 'msys'
                ):
                    cmd = f'type {filepath} | clip'
                elif sys.platform == 'darwin':
                    cmd = f'cat {filepath} | pbcopy'
                exec_out = subprocess.DEVNULL
                if self.debug:
                    exec_out = sys.stdout
                subprocess.Popen(
                    cmd,
                    stdout=exec_out,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    shell=True,
                )
                os.write(self.child.child_fd, b'\x15')
                self.input_buffer = b''
                return b''
        if data in [b'\x0d', b'\x03']:
            self.input_buffer = b''
        return data


class LoadConfig:
    def __init__(self, config_file: Path | None) -> None:
        self.config = ConfigParser(delimiters=('=',), interpolation=None)
        if not config_file:
            return
        if not config_file.is_file():
            return
        try:
            self.config.read(config_file)
        except ParsingError as ex:
            print(f'Config File Format Error: {ex}')
            sys.exit(1)

    def get_config(self, name: str) -> typing.Mapping[str, str] | None:
        if name in self.config.sections():
            return self.config[name]
        possibles = []
        for section in self.config.sections():
            pattern = section
            if '*' in section:
                pattern = pattern.replace('*', '.*')
            if '?' in section:
                pattern = pattern.replace('?', '.')
            if re.match(pattern, name):
                possibles.append(section)
        if possibles:
            return self.config[max(possibles, key=len)]


def generate_command(
    host: str,
    *,
    port: int | None = None,
    user: str | None = None,
    prog: str | None = None,
    arg_list: list | None = None,
    connect_config: typing.Mapping[str, str] | None = None,
    extra: str | None = '',
) -> tuple:
    conf_prog = ''
    conf_params = ''
    conf_extra = ''
    if connect_config:
        if params_list := [
            param
            for conn_tuple in connect_config.items()
            if conn_tuple[0] != 'extra' and conn_tuple[0] != 'prog'
            for param in conn_tuple
        ]:
            conf_params += ' '
            conf_params += ' '.join(params_list)
        conf_prog = connect_config.get('prog') if connect_config.get('prog') else ''
        conf_extra = connect_config.get('extra') if connect_config.get('extra') else ''
    add_params = ''
    if arg_list:
        add_params += ' '
        add_params += ' '.join([f'{arg}' for arg in arg_list])
    parameters = ''
    if port:
        parameters += f' -p {port}'
    if user:
        parameters += f' {user}@{host}'
    else:
        parameters += f' {host}'
    if prog and conf_prog and prog != conf_prog:
        conf_params = ''
        conf_extra = ''
    if not prog:
        if conf_prog:
            prog = conf_prog
        else:
            prog = 'ssh'
    extra = extra if extra else conf_extra
    return prog, f'{prog}{add_params}{conf_params}{parameters} {extra}'


def run(args: argparse.Namespace, arg_list: list) -> None:
    host_parsed = getattr(args, 'host', '').split('@')
    user = None
    host = host_parsed[0]
    if len(host_parsed) > 1:
        user = host_parsed[0]
        host = host_parsed[1]
    connect_config = LoadConfig(getattr(args, 'connect_config', None))
    expect_config = LoadConfig(getattr(args, 'expect_config', None))
    copy_config = LoadConfig(getattr(args, 'copy_config', None))
    prog, command = generate_command(
        host,
        port=getattr(args, 'port', None),
        user=user,
        prog=getattr(args, 'prog', None),
        arg_list=arg_list,
        connect_config=connect_config.get_config(host),
        extra=getattr(args, 'extra', None),
    )
    if which(prog) is None:
        print(f'{prog} not found')
        sys.exit(1)
    PtyInteract(
        host,
        command,
        use_bw=USE_BW and which('bw') is not None,
        timeout=getattr(args, 'timeout', 10),
        expect_config=expect_config.get_config(host),
        copy_config=copy_config.get_config(host),
        debug=getattr(args, 'debug', False),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        additional arguments:
            any arguments not listed above will be passed through
        """),
    )
    parser.add_argument('host', type=str, help='[user@]host to connect')
    parser.add_argument('-p', dest='port', type=int, help='port to connect')
    parser.add_argument(
        '--timeout', type=int, default=10, help='timeout for initial connection'
    )
    parser.add_argument(
        '--connect-config',
        type=Path,
        default=Path('~').expanduser() / '.ssh/connect.conf',
        help='config file for connection (default: %(default)s)',
    )
    parser.add_argument(
        '--expect-config',
        type=Path,
        default=Path('~').expanduser() / '.ssh/expect.conf',
        help='config file for automation (default: %(default)s)',
    )
    parser.add_argument(
        '--copy-config',
        type=Path,
        default=Path('~').expanduser() / '.ssh/copy.conf',
        help='config file for automation (default: %(default)s)',
    )
    parser.add_argument(
        '--prog', type=str, default='', help='ssh program to use (default: ssh)'
    )
    parser.add_argument(
        '--extra', type=str, default='', help='extra arguments attach to the end'
    )
    parser.add_argument('--debug', action='store_true', help='turn on debug echo')
    parser.set_defaults(func=run)
    args = parser.parse_known_args()
    args[0].func(args[0], args[1])


if __name__ == '__main__':
    main()
