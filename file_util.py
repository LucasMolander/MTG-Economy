import json


class FileUtil(object):
    @staticmethod
    def getJSONContents(filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
            return json.loads(f.read().encode(encoding='utf-8'))
