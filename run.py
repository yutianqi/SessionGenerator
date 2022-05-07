#!/usr/bin/env python
# encoding=utf8

import os
import sys
import base64
import shutil
from tkinter import NE
import win32api
import win32security
from Crypto.Hash import SHA256
from Crypto.Cipher import ARC4
from NetEcoConfigParser import NetEcoConfigParser
from XShellSessionGenerator import XShellSessionGenerator
from domain.my_config_parser import MyConfigParser

DATA_FILE_NAME = 'data.csv'

VERSION_6_CONFIG_PATH = os.path.join(
    os.environ["USERPROFILE"], "Documents", "NetSarang Computer", "6", "Xshell", "Sessions")
VERSION_7_CONFIG_PATH = os.path.join(
    os.environ["USERPROFILE"], "Documents", "NetSarang Computer", "7", "Xshell", "Sessions")
CONFIG_PATH = ""


def main():
    global CONFIG_PATH
    if os.path.exists(VERSION_6_CONFIG_PATH):
        CONFIG_PATH = VERSION_6_CONFIG_PATH
    elif os.path.exists(VERSION_7_CONFIG_PATH):
        CONFIG_PATH = VERSION_7_CONFIG_PATH

    fileName = ""
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = DATA_FILE_NAME
    parser = NetEcoConfigParser()
    data = parser.parse(fileName)

    generator = XShellSessionGenerator()
    generator.generate(data)


if __name__ == '__main__':
    # print(getkey())
    # print(encrypt("Changeme_123"))
    main()
