import json
from pathlib import Path


class FileUtil(object):
    TOKENS_FOLDER_PATH = 'tokens'

    @staticmethod
    def getJSONContents(filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
            return json.loads(f.read().encode(encoding='utf-8'))

    @staticmethod
    def writeJSONContents(filePath: str, obj):
        p = Path(filePath)
        parentFolderPath: Path = p.parent.absolute()
        parentFolderPath.mkdir(parents=True, exist_ok=True)
        p.touch()
        with open(filePath, 'w', encoding='utf-8') as f:
            return json.dump(obj, f)
