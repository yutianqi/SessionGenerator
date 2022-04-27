#!/usr/bin/env python
# encoding=utf8

import os
import sys
import base64
import shutil
import win32api
import win32security
from Crypto.Hash import SHA256
from Crypto.Cipher import ARC4
from domain.my_config_parser import MyConfigParser

DATA_FILE_NAME = 'data.csv'
TEMPALTE_FILE_NAME = 'template.xsh'
VERSION_6_CONFIG_PATH = os.path.join(
    os.environ["USERPROFILE"], "Documents", "NetSarang Computer", "6", "Xshell", "Sessions")
VERSION_7_CONFIG_PATH = os.path.join(
    os.environ["USERPROFILE"], "Documents", "NetSarang Computer", "7", "Xshell", "Sessions")
config_path = ""


def main():
    global config_path
    if os.path.exists(VERSION_6_CONFIG_PATH):
        config_path = VERSION_6_CONFIG_PATH
    elif os.path.exists(VERSION_7_CONFIG_PATH):
        config_path = VERSION_7_CONFIG_PATH

    fileName = ""
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = DATA_FILE_NAME
    data = parse(fileName)
    # print(data)
    generate(data)


def parse(dataFileName):
    ret = {}
    with open(dataFileName, 'r') as f:
        for x in f.readlines()[1:]:
            if not x.replace(",", "").strip():
                continue
            # print(x.strip())
            fields = x.strip().split(",")
            projectName = fields[0]
            regionName = fields[1]
            nodeType = fields[2]
            nodeName = fields[3]
            nodeIP = fields[4]
            nodePort = fields[5]
            username = fields[6]
            password = fields[7]

            if not ret.get(projectName):
                ret[projectName] = {}
            prject = ret.get(projectName)

            if not prject.get(regionName):
                prject[regionName] = {}
            region = prject.get(regionName)

            if not region.get(nodeType):
                region[nodeType] = []
            nodeList = region.get(nodeType)
            nodeList.append({
                "nodeName": nodeName + "_" + nodeIP.split(".")[-1],
                "ip": nodeIP,
                "port": nodePort,
                "username": username,
                "password": password
            })
    return ret


def generate(data):
    for (projectName, project) in data.items():
        # print("Projet:" + projectName)
        for (regionName, region) in project.items():
            # print("Region:" + regionName)
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
                    generateFile(projectName, regionName, nodeType, backendIP,
                                 backendPort, backendUserName, backendPassWord, node)
        shutil.move(projectName, config_path)
    return ""


def generateFile(projectName, regionName, nodeType, backendIP, backendPort, backendUserName, backendPassWord, node):
    # print(node.get("nodeName"))
    config = loadTemplate(TEMPALTE_FILE_NAME)
    # print(config.get("CONNECTION","Host"))
    if not backendIP:
        config.set("CONNECTION", "Host", node.get("ip"))
        config.set("CONNECTION", "Port", node.get("port"))
        config.set("CONNECTION:AUTHENTICATION",
                   "UserName", node.get("username"))
        config.set("CONNECTION:AUTHENTICATION",
                   "Password", encrypt(node.get("password")))

        config.set("CONNECTION:AUTHENTICATION", "UseExpectSend", "0")
        config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Count", "0")
    else:
        config.set("CONNECTION", "Host", backendIP)
        config.set("CONNECTION", "Port", backendPort)
        config.set("CONNECTION:AUTHENTICATION", "UserName", backendUserName)
        config.set("CONNECTION:AUTHENTICATION",
                   "Password", encrypt(backendPassWord))

        config.set("CONNECTION:AUTHENTICATION", "UseExpectSend", "1")
        config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Count", "2")

        config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Expect_0", "]$ ")
        config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Send_0",
                   "ssh {0}@{1} -p {2}".format(node.get("username"), node.get("ip"), node.get("port")))
        config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Hide_0", "0")

        config.set("CONNECTION:AUTHENTICATION",
                   "ExpectSend_Expect_1", "password: ")
        config.set("CONNECTION:AUTHENTICATION",
                   "ExpectSend_Send_1", node.get("password"))
        config.set("CONNECTION:AUTHENTICATION", "ExpectSend_Hide_1", "0")

    filePath = os.path.join(projectName, regionName, nodeType)
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    config.write(open(os.path.join(filePath, node.get("nodeName") + ".xsh"), "w", encoding="utf-16"),
                 space_around_delimiters=False)


def loadTemplate(fileName):
    config = MyConfigParser()
    try:
        config.read(fileName)
    except UnicodeDecodeError:
        config.read(fileName, encoding="utf-16")
    # config.read(fileName, encoding="utf-8")
    # print(config.sections())
    return config


def encrypt(passwd, key=None):
    key = getkey()
    tmp = SHA256.new(key.encode('ascii')).digest()
    r3 = passwd.encode('ascii')
    r1 = ARC4.new(tmp).encrypt(r3) + \
        SHA256.new(passwd.encode('ascii')).digest()
    r = base64.b64encode(r1).decode('ascii')
    return r


def getkey():
    userName = win32api.GetUserName()
    computerName = win32api.GetComputerName()
    userSID = win32security.LookupAccountName(
        computerName, userName)[0]
    userSIDString = win32security.ConvertSidToStringSid(userSID)
    return userName + userSIDString


if __name__ == '__main__':
    # print(getkey())
    # print(encrypt("Changeme_123"))
    main()
