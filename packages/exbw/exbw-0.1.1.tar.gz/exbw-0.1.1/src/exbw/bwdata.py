#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import sys

import pexpect


class BwData:
    def __init__(self, item: str, *, debug: bool = False) -> None:
        os.environ['LANGUAGE'] = 'en'
        self.item = item
        self.debug = debug
        self.start()

    def start(self) -> None:
        self.child = pexpect.spawn(
            f'bw get item {self.item}',
            env=os.environ,
            timeout=10,
            encoding='utf8',
        )
        if self.debug:
            self.child.logfile = sys.stdout
        try:
            self.raw_output = self.pwd_session()
        except KeyboardInterrupt:
            self.raw_output = []

    def get_data(self, field: str) -> str | None:
        if self.raw_output:
            return self.parse_output(self.raw_output, field)
        return ''

    def pwd_session(self) -> list | None:
        res = self.child.expect(
            [
                r'(?i)master password:',
                r'(?i)fingerprint reader',
                r'(?i)password for',
                r'(?i)key not found',
                r'(?i)with key(.*)',
                pexpect.EOF,
                pexpect.TIMEOUT,
            ]
        )
        if res == 0:
            master = getpass.getpass('BW Master Password:')
            if not master:
                print('No Input')
                return None
            self.child.sendline(master)
            print('Waiting for BW...')
            return self.child.readlines()[1:]
        elif res == 1:
            print('Place your finger on the fingerprint reader:')
            return self.pwd_session()
        elif res == 2:
            sudo_pwd = getpass.getpass('System User Password:')
            if not sudo_pwd:
                print('No Input')
                return None
            self.child.sendline(sudo_pwd)
            return self.pwd_session()
        elif res == 3:
            print('BW Session Not Found')
            return None
        elif res == 4:
            print('Trying BW Session...')
            sub_res = self.child.expect(
                [r'(?i)master password:', pexpect.EOF, pexpect.TIMEOUT]
            )
            sub_text_before = ''
            if isinstance(self.child.before, str):
                sub_text_before = self.child.before
            if sub_res == 0:
                print('Invalid BW Session')
                return None
            elif sub_res == 1:
                return sub_text_before.strip().split('\n')
            else:
                return None
        else:
            return None

    def parse_output(self, raw_lines: list, field: str) -> str | None:
        if len(raw_lines) == 1:
            try:
                item = json.loads(raw_lines[0])
                print(f'Best Match: {item.get("name")}')
                if field == 'password':
                    return item.get('login').get(field)
                elif item.get('fields'):
                    for element in item.get('fields'):
                        if re.search(field, element.get('name')):
                            print(f'Found: {element.get("name")}')
                            return element.get('value')
                return ''
            except json.decoder.JSONDecodeError:
                line = raw_lines[0].strip()
                if 'invalid master password' in line.lower():
                    print('Invalid Password')
                    return None
                elif 'not found' in line.lower():
                    print('No Match')
                    return ''
                print(line)
        for line in raw_lines:
            line = line.strip()
            if 'invalid master password' in line.lower():
                print('Invalid Password')
                return None
            print(line)
        return ''


def run(args: argparse.Namespace) -> None:
    bw = BwData(getattr(args, 'item', ''), debug=getattr(args, 'debug', False))
    print(bw.get_data(getattr(args, 'field', 'password')))


def main() -> None:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('item', type=str, help='BitWarden Item Name')
    parser.add_argument(
        '-f',
        dest='field',
        type=str,
        default='password',
        help='BitWarden Item Field (default: %(default)s)',
    )
    parser.add_argument('--debug', action='store_true', help='turn on debug echo')
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
