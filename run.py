#!/usr/bin/env python
#encoding=utf8

import sys
from NetEcoConfigParser import NetEcoConfigParser
from NetEcoConfigParserV2 import NetEcoConfigParserV2
from XShellSessionGenerator import XShellSessionGenerator
from CommonSessionGenerator import CommonSessionGenerator
from iTerm2SessionGenerator import iTerm2SessionGenerator


DATA_FILE_NAME = 'data.csv'


def main():
    fileName = ""
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = DATA_FILE_NAME
    # parser = NetEcoConfigParser()
    parser = NetEcoConfigParserV2()
    data = parser.parse(fileName)
    # print(data)

    generator = XShellSessionGenerator()
    # generator = CommonSessionGenerator()
    generator = iTerm2SessionGenerator()
    generator.generate(data, True)
    # generator.generate(data, False)


if __name__ == '__main__':
    # print(getkey())
    # print(encrypt("Changeme_123"))
    main()
