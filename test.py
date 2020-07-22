from pprint import pprint
import urllib.parse

from tcgplayer_api import TCGPlayerAPI
from set_util import SetUtil
from file_util import FileUtil

# TCGPlayerAPI.init()

# print("\nBearer token:")
# print(TCGPlayerAPI.bearerToken)
# print('')

# TCGPlayerAPI.doStuff()



# baseURL = 'https://api.scryfall.com/cards/search?q='
# query = urllib.parse.quote('set=%s' % 'm21')
# finalURL = baseURL + query

# print(finalURL)



# Try doing unique%3Aprints


baseURL = 'https://api.scryfall.com/cards/search?q='
mpCode = 'm21'
query = urllib.parse.quote('set=%s unique:prints' % mpCode)
finalURL = baseURL + query

print(finalURL)


# isCollectorsEd = SetUtil.isCollectorsEd('m20')
# print(isCollectorsEd)




# cards = SetUtil.loadFromFiles(only="Core Set 2021")
# print(len(cards))
