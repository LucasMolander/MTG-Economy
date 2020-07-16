from pprint import pprint

from tcgplayer_api import TCGPlayerAPI

TCGPlayerAPI.init()

print("\nBearer token:")
print(TCGPlayerAPI.bearerToken)
