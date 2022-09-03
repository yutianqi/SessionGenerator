#!/usr/bin/env python
#encoding=utf8

import os
import sys
from NetEcoConfigParser import NetEcoConfigParser
from parser.NetEcoConfigParserV2 import NetEcoConfigParserV2
from XShellSessionGenerator import XShellSessionGenerator
from CommonSessionGenerator import CommonSessionGenerator
from generator.XShellSessionGeneratorV2 import XShellSessionGeneratorV2
from generator.iTerm2SessionGenerator import iTerm2SessionGenerator


DATA_FILE_NAME = 'data.csv'


def main():
    fileName = ""
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = DATA_FILE_NAME
    # runV1(fileName)
    runV2(fileName)

def runV1(fileName):
    parser = NetEcoConfigParser()
    data = parser.parse(fileName)
    # print(data)
    generator = XShellSessionGeneratorV2()
    # generator = CommonSessionGenerator()
    # generator = iTerm2SessionGenerator()
    # generator.generate(data, True)
    # generator.generate(data, False)


def runV2(fileName):
    parser = NetEcoConfigParserV2()
    data = parser.parse(fileName)
    # print(json.dumps(data))
    generator = XShellSessionGeneratorV2()
    # generator = CommonSessionGenerator()
    # generator = iTerm2SessionGenerator()
    generator.generate(data, True)
    # generator.generate(data, False)

if __name__ == '__main__':
    main()
    os.system("pause")
