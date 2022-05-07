#!/usr/bin/env python
#encoding=utf8

import json



class CommonSessionGenerator():
    fileName = "sessions.json"

    def generate(self, data):
        with open(self.fileName, "w", encoding="utf-8") as f:
            json.dump(data, f)


