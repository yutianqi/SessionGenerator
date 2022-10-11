#!/usr/bin/env python
#encoding=utf8
import os

class NetEcoConfigParserV2():

    def read(self, dataFileName):
        """
        Load data from configuration file and parse lines

		Parameters:
		  dataFileName - configuration file name 

        Returns:
          raw record map
        """
        if not os.path.exists(dataFileName):
            raise RuntimeError("Session配置文件[{}]不存在".format(dataFileName))
        ret = {}
        with open(dataFileName, 'r') as f:
            for x in f.readlines()[1:]:
                if not x.replace(",", "").strip():
                    continue
                fields = x.strip().split(",")
                projectName = fields[0]
                regionName = fields[1]
                nodeType = fields[2]
                nodeName = fields[3]
                nodeIP = fields[4]
                nodePort = fields[5]
                username = fields[6]
                password = fields[7]
                proxy = fields[8]

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
                    "password": password,
                    "proxy": proxy
                })
        return ret

    def parseNode(self, rawMap, jumper):
        """
        trans raw record to nodes

		Parameters:
		  rawMap - node raw data
          jumper - jumper of the node

        Returns:
          node
        """
        node = {
            "nodeName": rawMap.get("nodeName"),
            "nodeType": "session",
        }

        node["ip"] = rawMap.get("ip")
        node["port"] = rawMap.get("port")
        node["username"] = rawMap.get("username")
        node["password"] = rawMap.get("password")
        node["proxy"] = rawMap.get("proxy")

        if jumper:
            node["jumper"] = jumper
            node["expectCmds"] = [
                {
                    "expect": "]$ ",
                    "send": "export HISTSIZE=1000",
                    "hide": "0"
                }
            ]
        return node

    def parse(self, dataFileName):
        rawMap = self.read(dataFileName)
        projectNodes = []
        for projectName, projectData in rawMap.items():
            # print("projectName=" + projectName)

            childRegionNodes = []
            for regionName, reginData in projectData.items():
                # print("regionName=" + regionName)
                # print(reginData)
                # 每个project数据，首先找到Backend数据，作为其他节点的jumper
                if reginData.get("Backend"):
                    backEndNode = reginData.get("Backend")[0]
                    jumper = self.parseNode(backEndNode, {})

                childTypeNodes = []
                for typeName, typeData in reginData.items():
                    # print("typeName=" + typeName)
                    # 对于Backend节点，仅作为其他节点跳转使用，无需创建真实节点
                    if typeName == 'Backend':
                        continue

                    childNodes = []
                    for node in typeData:
                        # print(node.get("nodeName"))
                        if typeName == 'Master':
                            # childNodes.append(self.parseNode(node, jumper))
                            # continue
                            pass
                        if typeName == 'DB':
                            tmpNode = self.parseNode(node, jumper)
                            if not tmpNode.get("expectCmds"):
                                tmpNode["expectCmds"] = []
                            tmpNode["expectCmds"] = [
                                {
                                    "expect": "]$ ",
                                    "send": "su -",
                                    "hide": "0"
                                },
                                {
                                    "expect": "Password: ",
                                    "send": tmpNode["password"],
                                    "hide": "0"
                                },
                                {
                                    "expect": "]# ",
                                    "send": "su - dbuser",
                                    "hide": "0"
                                }
                            ] + tmpNode["expectCmds"]
                            childNodes.append(tmpNode)
                            continue
                        childNodes.append(self.parseNode(node, jumper))
                    typeNode = {
                        "nodeName": typeName,
                        "nodeType": "directory",
                        "childNodes": childNodes
                    }
                    childTypeNodes.append(typeNode)

                if backEndNode:
                    regionName += "_" + backEndNode.get("ip")

                regionNode = {
                    "nodeName": regionName,
                    "nodeType": "directory",
                    "childNodes": childTypeNodes
                }
                childRegionNodes.append(regionNode)

            projectNode = {
                "nodeName": projectName,
                "nodeType": "directory",
                "childNodes": childRegionNodes
            }
            projectNodes.append(projectNode)
        return projectNodes
