#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Seaky
# @Date:   2021/5/30 14:29


from configparser import RawConfigParser
from pathlib import Path
import sys

import os
import re

DefaultCrtConfig = open('Default.ini', encoding='utf-8').read()


def dec2hex(i, zfill=8):
    return hex(int(str(i))).replace('0x', '').zfill(zfill)


def convert(source_dir, output_dir):
    for i, objs in enumerate(os.walk(source_dir)):
        root, dirs, files = objs
        dir_path = Path(root)

        for file_name in files:
            if not file_name.endswith('.xsh'):
                continue
            file_path = dir_path / file_name
            target_path = Path(str(file_path).replace(source_dir, output_dir))
            # ConfigParser() 不能解析含 % 的字串
            config = RawConfigParser()
            try:
                config.read_file(open(file_path, encoding='utf-16'))
            except Exception as e:
                config.read_file(open(file_path))
            protocol = config.get("CONNECTION", "Protocol")
            if protocol in ['SSH', 'FTP', 'TELNET'][:1]:
                cols = {
                    'Username': config.get("CONNECTION:AUTHENTICATION", "UserName"),
                    'Hostname': config.get("CONNECTION", "Host"),
                    'Protocol Name': 'SSH2',
                    '[SSH2] 端口': dec2hex(config.get("CONNECTION", "Port")),
                    '[SSH2] Port': dec2hex(config.get("CONNECTION", "Port")),
                    'Description': '00000002\n ' + config.get("CONNECTION", "Description").replace('\n', '\n ')
                }
                s = DefaultCrtConfig
                for k, v in cols.items():
                    pattern = '("{}")(=.*)'.format(k)
                    s = re.sub(pattern, r'\1={}'.format(v), s)

                target_path.parent.mkdir(parents=True, exist_ok=True)
                open(str(target_path).replace('.xsh', '.ini'), 'w', encoding='utf-8').write(s)
            else:
                print('unknown {}, {}'.format(protocol, file_path))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python {} <XShell_Sessions_dir>'.format(Path(__file__).name))
    elif not Path(sys.argv[1]).is_dir():
        print('Error: {} is not a valid source'.format(sys.argv[1]))
    else:
        source_dir = sys.argv[1]
        output_dir = 'Sessions'
        convert(source_dir, output_dir)
        print('Export {} to {} done.'.format(source_dir, output_dir))