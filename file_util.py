import json


class FileUtil(object):
    @staticmethod
    def getJSONContents(filePath):
        with open(filePath, 'r') as f:
            return json.loads(f.read().encode('utf8'))
