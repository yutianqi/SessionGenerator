#!/usr/bin/env python
#encoding=utf8

class NetEcoConfigParserV2():

    def read(self, dataFileName):
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

    def parseNode(self, rawMap, jumper):
        # print(jumper)
        node = {
            "nodeName": rawMap.get("nodeName"),
            "nodeType": "session",
            "ip": rawMap.get("ip"),
            "port": rawMap.get("port"),
            "username": rawMap.get("username"),
            "password": rawMap.get("password"),
        }
        if jumper:
            node["jumper"] = jumper
        return node

    def parse(self, dataFileName):
        rawMap = self.read(dataFileName)
        projectNodes = []
        for projectName, projectData in rawMap.items():
            # print("projectName=" + projectName)

            projectNode = {
                "nodeName": projectName,
                "nodeType": "directory",
            }
            childRegionNodes = []

            for regionName, reginData in projectData.items():
                # print("regionName=" + regionName)
                backEndNode = reginData.get("Backend")[0]
                jumper = self.parseNode(backEndNode, {})

                regionNode = {
                    "nodeName": regionName,
                    "nodeType": "directory",
                }
                childTypeNodes = []
                for typeName, typeData in reginData.items():
                    # print("typeName=" + typeName)
                    if typeName == 'Backend':
                        continue

                    typeNode = {
                        "nodeName": typeName,
                        "nodeType": "directory",
                    }
                    childNodes = []
                    for node in typeData:
                        # print(node.get("nodeName"))
                        childNodes.append(self.parseNode(node, jumper))
                    typeNode["childNodes"] = childNodes
                    childTypeNodes.append(typeNode)
                regionNode["childNodes"] = childTypeNodes
                childRegionNodes.append(regionNode)
            projectNode["childNodes"] = childRegionNodes
            projectNodes.append(projectNode)
        return projectNodes
