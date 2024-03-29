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

TEMPALTE_FILE_NAME = 'template.xsh'
VERSION_6_CONFIG_PATH = os.path.join(
    os.environ["USERPROFILE"], "Documents", "NetSarang Computer", "6", "Xshell", "Sessions")
VERSION_7_CONFIG_PATH = os.path.join(
    os.environ["USERPROFILE"], "Documents", "NetSarang Computer", "7", "Xshell", "Sessions")


class XShellSessionGenerator():
    CONFIG_PATH = "D:\\Program Files\\Xshell6\\UserConfig\\Xshell\\Sessions"
    if os.path.exists(VERSION_6_CONFIG_PATH):
        CONFIG_PATH = VERSION_6_CONFIG_PATH
    elif os.path.exists(VERSION_7_CONFIG_PATH):
        CONFIG_PATH = VERSION_7_CONFIG_PATH
    def generate(self, data, update=True):
        for (projectName, project) in data.items():
            for (regionName, region) in project.items():
                if region.get("Backend"):
                    backend = region.get("Backend")[0]
                    backendIP = backend.get("ip")
                    backendPort = backend.get("port")
                    backendUserName = backend.get("username")
                    backendPassWord = backend.get("password")
                else:
                    backend = ""
                    backendIP = ""
                    backendPort = ""
                    backendUserName = ""
                    backendPassWord = ""
                for (nodeType, nodes) in region.items():
                    if nodeType == "Backend":
                        continue
                    for node in nodes:
                        self.generateFile(projectName, regionName, nodeType, backendIP,
                                          backendPort, backendUserName, backendPassWord, node)
        if update:
            self.save(projectName)

    def save(self, projectName):
        projectPath = os.path.join(self.CONFIG_PATH, projectName)
        if os.path.exists(projectPath):
            if input("项目[{}]已存在, 是否替换, yes/no: ".format(projectPath)) == 'yes':
                shutil.rmtree(projectPath)
            else:
                return
        shutil.move(projectName, self.CONFIG_PATH)
        print("保存[{}]到[{}]".format(projectName, self.CONFIG_PATH))

    def generateFile(self, projectName, regionName, nodeType, backendIP, backendPort, backendUserName, backendPassWord, node):
        config = self.loadTemplate(TEMPALTE_FILE_NAME)
        # 更新连接配置
        if not backendIP:
            config.set("CONNECTION", "Host", node.get("ip"))
            config.set("CONNECTION", "Port", node.get("port"))
            config.set("CONNECTION:AUTHENTICATION",
                       "UserName", node.get("username"))
            config.set("CONNECTION:AUTHENTICATION",
                       "Password", self.encrypt(node.get("password")))

            config.set("CONNECTION:AUTHENTICATION", "UseExpectSend", "0")
            config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Count", "0")
        else:
            config.set("CONNECTION", "Host", backendIP)
            config.set("CONNECTION", "Port", backendPort)
            config.set("CONNECTION:AUTHENTICATION",
                       "UserName", backendUserName)
            config.set("CONNECTION:AUTHENTICATION",
                       "Password", self.encrypt(backendPassWord))

            config.set("CONNECTION:AUTHENTICATION", "UseExpectSend", "1")

            expectSendList = [
                {
                    "expect": "]$ ",
                    "send": "ssh {0}@{1} -p {2}".format(node.get("username"), node.get("ip"), node.get("port")),
                    "hide": "0"
                },
                {
                    "expect": "password: ",
                    "send": node.get("password"),
                    "hide": "0"
                },
                {
                    "expect": "]$ ",
                    "send": "export HISTSIZE=1000",
                    "hide": "0"
                }
            ]
            total = len(expectSendList)
            config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Count", str(total))

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
