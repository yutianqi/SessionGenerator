

class NetEcoConfigParser():

    def parse(self, dataFileName):
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