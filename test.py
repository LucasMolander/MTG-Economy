from pprint import pprint
import urllib.parse
import json
from enum import Enum, IntEnum
from typing import Tuple, Dict, Any, List

from tcgplayer_api import TCGPlayerAPI
from set_util import SetUtil
from file_util import FileUtil


# name = "iko"
# code = SetUtil.coerceToCode(name)
# name = SetUtil.coerceToName(name)

# print(name)
# exit()

# stuff = SetUtil.loadFromFiles(only=iko)
# pprint(stuff)
# exit()






TCGPlayerAPI.init()

print("\nBearer token:")
print(TCGPlayerAPI.bearerToken)
print('')

# TCGPlayerAPI.doStuff()
# TCGPlayerAPI.getSKUIDs()





# baseURL = 'https://api.scryfall.com/cards/search?q='
# query = urllib.parse.quote('set=%s' % 'm21')
# finalURL = baseURL + query

# print(finalURL)



# Try doing unique%3Aprints


# baseURL = 'https://api.scryfall.com/cards/search?q='
# mpCode = 'm21'
# query = urllib.parse.quote('set=%s unique:prints' % mpCode)
# finalURL = baseURL + query

# print(finalURL)


# isCollectorsEd = SetUtil.isCollectorsEd('m20')
# print(isCollectorsEd)



# setCode = 'm21'
# mpCode = None

# baseURL = 'https://api.scryfall.com/cards/search?q='
# if (mpCode):
#     query = urllib.parse.quote('set=%s' % mpCode)
# else:
#     query = urllib.parse.quote('set=%s unique:prints' % setCode)

# finalURL = baseURL + query

# print(finalURL)








# class BorderType(Enum):
#   BLACK = "black"
#   BORDERLESS = "borderless"

#   def __str__(self):
#     return str(self.value)

#   def __repr__(self):
#     return self.__str__()


# class FrameEffect(Enum):
#   NONE = "none"
#   EXTENDED_ART = "extended_art"
#   FULL_ART = "full_art"
#   SHOWCASE = "showcase"
#   INVERTED = "inverted"

#   def __str__(self):
#     return str(self.value)

#   def __repr__(self):
#     return self.__str__()


# TBorderInfo = Tuple[BorderType, FrameEffect]


# def getBorderInfo(card) -> TBorderInfo:
#   borderType: BorderType = {
#     "black": BorderType.BLACK,
#     "borderless": BorderType.BORDERLESS,
#   }[card['border_color']]

#   # These frames don't change the cardinality of a card,
#   # i.e. "This card" will always have "that frame"
#   ignoreFrames = {'legendary', 'nyxtouched', 'nyxborn', 'miracle', 'sunmoondfc', 'devoid', 'compasslanddfc', 'originpwdfc', 'companion', 'snow'}

#   if 'frame_effects' in card:
#     frameEffects: List[str] = card['frame_effects']
#     keepFrameEffects = set(frameEffects).difference(ignoreFrames)

#     if len(keepFrameEffects) > 1:
#       raise Exception(f"More than 1 keep frame effect: {keepFrameEffects}\nCard: {card['name']}")

#     if 'extendedart' in keepFrameEffects:
#       frameEffect: FrameEffect = FrameEffect.EXTENDED_ART
#     elif 'fullart' in keepFrameEffects:
#       frameEffect: FrameEffect = FrameEffect.FULL_ART
#     elif 'showcase' in keepFrameEffects:
#       frameEffect: FrameEffect = FrameEffect.SHOWCASE
#     elif 'inverted' in keepFrameEffects:
#       frameEffect: FrameEffect = FrameEffect.INVERTED
#     else:
#       if len(keepFrameEffects) > 0:
#         raise Exception(f"Unknown frame effect: {keepFrameEffects}\nCard: {card['name']}")
#       else:
#         frameEffect: FrameEffect = FrameEffect.NONE
#   else:
#     frameEffect: FrameEffect = FrameEffect.NONE

#   return (borderType, frameEffect)


# def doASet(setName):
#   print(f"{setName}\n{'-'*len(setName)}")
#   cards = SetUtil.loadFromFile(setName)

#   borderTypeToCount: Dict[TBorderInfo, int] = {}
#   borderTypeToCards: Dict[TBorderInfo, List[Dict[str, Any]]] = {}

#   for card in cards:
#     borderInfo = getBorderInfo(card)

#     if borderInfo not in borderTypeToCount:
#       borderTypeToCount[borderInfo] = 0
#     borderTypeToCount[borderInfo] += 1

#     if borderInfo not in borderTypeToCards:
#       borderTypeToCards[borderInfo] = []

#     prices = card['prices']
#     borderTypeToCards[borderInfo].append({
#       "name": card['name'],
#       "rarity": card['rarity'],
#       "price": float(prices['usd']) if ('usd' in prices and prices['usd'] != None) else 0.0,
#       "priceFoil": float(prices['usd_foil']) if ('usd_foil' in prices and prices['usd_foil'] != None) else 0.0,
#     })

#   borderTypeToCount = dict(sorted(borderTypeToCount.items(), key = lambda itm: itm[1]))
#   print(borderTypeToCount)



# setToInfo = SetUtil.loadAllFromFiles()
# for setName in setToInfo:
#   doASet(setName)
#   print()
