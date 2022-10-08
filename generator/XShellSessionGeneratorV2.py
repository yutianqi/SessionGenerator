#!/usr/bin/env python
#encoding=utf8

import os
import base64
import shutil
import win32api
import win32security
from Crypto.Hash import SHA256
from Crypto.Cipher import ARC4
from domain.my_config_parser import MyConfigParser
import sys

TEMPALTE_FILE_NAME = os.path.join(os.path.dirname(sys.argv[0]), 'template.xsh')

VERSION_6_CONFIG_PATH = os.path.join(
    os.environ["USERPROFILE"], "Documents", "NetSarang Computer", "6", "Xshell", "Sessions")
VERSION_7_CONFIG_PATH = os.path.join(
    os.environ["USERPROFILE"], "Documents", "NetSarang Computer", "7", "Xshell", "Sessions")

class XShellSessionGeneratorV2():
    CONFIG_PATH = "D:\\Program Files\\Xshell6\\UserConfig\\Xshell\\Sessions"

    if os.path.exists(VERSION_6_CONFIG_PATH):
        CONFIG_PATH = VERSION_6_CONFIG_PATH
    elif os.path.exists(VERSION_7_CONFIG_PATH):
        CONFIG_PATH = VERSION_7_CONFIG_PATH

    def generate(self, data, update=True):
        for project in data:
            projectName = project.get("nodeName")
            regions = project.get("childNodes")
            for region in regions:
                regionName = region.get("nodeName")
                nodeTypes = region.get("childNodes")
                for nodeType in nodeTypes:
                    nodeTypeName = nodeType.get("nodeName")
                    nodes = nodeType.get("childNodes")
                    for node in nodes:
                        self.generateFile(projectName, regionName, nodeTypeName, node)
        if update:
            self.save(projectName)

    def save(self, projectName):
        projectPath = os.path.join(self.CONFIG_PATH, projectName)
        # 新项目，直接整目录移动
        if not os.path.exists(projectPath):
            shutil.move(projectName, self.CONFIG_PATH)
            print("保存[{}]到[{}]".format(projectName, self.CONFIG_PATH))
            return

        # 识别新增和重复的Session，逐个移动，使用allSessions，保证Session树展示顺序
        allSessions = []
        duplicateSessions = []
        for root, dirs, files in os.walk(projectName):
            for filespath in files:
                sessionPath = os.path.join(root, filespath)
                if os.path.exists(os.path.join(self.CONFIG_PATH, sessionPath)):
                    duplicateSessions.append(sessionPath)
                allSessions.append(sessionPath)
        if not allSessions:
            print("未检测到Session文件")
            return
        if not duplicateSessions or input("存在{}个重复Session, 是否合并, yes/no: ".format(len(duplicateSessions))) == 'yes':
            for item in allSessions:
                if item in duplicateSessions:
                    os.remove(os.path.join(self.CONFIG_PATH, item))
                dstPath = os.path.join(self.CONFIG_PATH, item)
                print(dstPath)
                if not os.path.exists(os.path.dirname(dstPath)):
                    os.makedirs(os.path.dirname(dstPath))
                shutil.move(item, dstPath)
        shutil.rmtree(projectName)
        print("保存[{}]到[{}]".format(projectName, self.CONFIG_PATH))

    def generateFile(self, projectName, regionName, nodeType, node):
        config = self.loadTemplate(TEMPALTE_FILE_NAME)
        jumpers = []
        jumper = node
        while(jumper):
            jumpers.append((jumper.get("ip"), jumper.get("port"), jumper.get("username"), jumper.get("password"), jumper.get("proxy"), jumper.get("expectCmds")))
            jumper = jumper.get("jumper")
        # print(jumpers)

        # 首个jumper的配置需要直接在配置文件中指定
        firstJumper = jumpers.pop()
        config.set("CONNECTION", "Host", firstJumper[0])
        config.set("CONNECTION", "Port", firstJumper[1])
        config.set("CONNECTION:AUTHENTICATION", "UserName", firstJumper[2])
        config.set("CONNECTION:AUTHENTICATION", "Password", self.encrypt(firstJumper[3]))
        if (firstJumper[4]):
            config.set("CONNECTION:PROXY", "Proxy", firstJumper[4])

        # 在expectSendList中指定其他待执行的命令
        if firstJumper[5]:
            expectSendList = firstJumper[5]
        else:
            expectSendList = []

        # 其他jumper的配置，通过expectSendList指定
        for jumper in jumpers[::-1]:
            expectSendList.extend([
                {
                    "expect": "]$ ",
                    "send": "ssh {0}@{1} -p {2}".format(jumper[2], jumper[0], jumper[1]),
                    "hide": "0"
                },
                {
                    "expect": "password: ",
                    "send": jumper[3],
                    "hide": "0"
                },
            ])
            # 在expectSendList中指定其他待执行的命令
            if jumper[5]:
                expectSendList.extend(jumper[5])

        total = len(expectSendList)
        config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Count", str(total))
        config.set("CONNECTION:AUTHENTICATION", "UseExpectSend", "1")

        for index in range(total):
            item = expectSendList[index]
            config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Expect_{}".format(index), item.get("expect"))
            config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Send_{}".format(index), item.get("send"))
            config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Hide_{}".format(index), item.get("hide"))

        # 更新日志配置
        config.set("LOGGING", "WriteFileTimestamp", "1")
        config.set("LOGGING", "AutoStart", "1")

        filePath = os.path.join(projectName, regionName, nodeType)
        if not os.path.exists(filePath):
            os.makedirs(filePath)
        config.write(open(os.path.join(filePath, node.get("nodeName") + ".xsh"), "w", encoding="utf-16"),
                     space_around_delimiters=False)

    def loadTemplate(self, fileName):
        config = MyConfigParser()
        try:
            config.read(fileName)
        except UnicodeDecodeError:
            config.read(fileName, encoding="utf-16")
        return config

    def encrypt(self, passwd):
        key = self.getkey()
        tmp = SHA256.new(key.encode('ascii')).digest()
        r3 = passwd.encode('ascii')
        r1 = ARC4.new(tmp).encrypt(r3) + \
            SHA256.new(passwd.encode('ascii')).digest()
        r = base64.b64encode(r1).decode('ascii')
        return r

    def getkey(self):
        userName = win32api.GetUserName()
        computerName = win32api.GetComputerName()
        userSID = win32security.LookupAccountName(
            computerName, userName)[0]
        userSIDString = win32security.ConvertSidToStringSid(userSID)
        return userName + userSIDString
