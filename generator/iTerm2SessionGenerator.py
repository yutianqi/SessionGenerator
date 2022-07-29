#!/usr/bin/env python
#encoding=utf8

import json

CONFIG_FILE_PATH = "D:\\Code\\Github\\SessionManager\\sessions.json"

TMP_FILE_NAME = "sessions.json"

class iTerm2SessionGenerator():
    nodeIdIndex = 0

    def getNodeId(self):
        self.nodeIdIndex += 1
        return self.nodeIdIndex

    def arrangeNodeId(self, node):
        node["nodeId"] = self.getNodeId()
        if node.get("childNodes"):
            for item in node.get("childNodes"):
                self.arrangeNodeId(item)

    def generate(self, data, update=False):
        for item in data:
            self.arrangeNodeId(item)
        # print(data)
        if update:
            # self.save(data, CONFIG_FILE_PATH)
            self.save(data, TMP_FILE_NAME)
        else:
            with open(TMP_FILE_NAME, "w", encoding="utf-8") as f:
                json.dump(data, f)

    def save(self, data, filePath):
        sessions = []
        '''
        with open(filePath, encoding="utf-8") as f:
            lines = f.readlines()
            sessions = json.loads("".join(lines))
        # print(sessions)
        '''
        # sessions.get('nodes').extend(data)
        sessions.extend(data)
        with open(filePath, "w", encoding="utf-8") as f:
            json.dump(sessions, f)
        # print("finished to save")



