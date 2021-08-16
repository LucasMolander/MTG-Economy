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



# BORDERLESS
# Mythic:   8
# Rare:     4
# Uncommon: 0
# Common:   0


# SHOWCASE
# Mythic:   9
# Rare:     5
# Uncommon: 5
# Common:   10


# EXTENDED ART
# Mythic:   0
# Rare:     0
# Uncommon: 0
# Common:   0



def valToCount(values):
    vToC = {}
    for val in values:
        if val not in vToC:
            vToC[val] = 0
        vToC[val] += 1
    return vToC


def valToCountAtLeastN(values, n):
    vToC = {}
    for val in values:
        if val not in vToC:
            vToC[val] = 0
        vToC[val] += 1

    out = {}
    for val in vToC:
        if vToC[val] >= n:
            out[val] = vToC[val]

    return out


def printDupePrices(dupeNames, cards):
    printed = False
    for dupeName in dupeNames:
        printedName = False
        for card in cards:
            if card['name'] == dupeName:
                printed = True
                if not printedName:
                    printedName = True
                    print('{}'.format(dupeName))
                print('\t{}, {}'.format(card['prices']['usd'], card['prices']['usd_foil']))
    if printed:
        print('')



cards = SetUtil.loadFromFiles(only="Modern Horizons 2")
print('Total number of cards: {}\n'.format(len(cards)))


class BorderType(Enum):
    BLACK = "black"
    BORDERLESS = "borderless"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()


class FrameEffect(Enum):
    NONE = "none"
    EXTENDED_ART = "extended_art"
    SHOWCASE = "showcase"
    INVERTED = "inverted"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()


TBorderInfo = Tuple[BorderType, FrameEffect]


def getBorderInfo(card) -> TBorderInfo:
    borderType: BorderType = {
        "black": BorderType.BLACK,
        "borderless": BorderType.BORDERLESS,
    }[card['border_color']]

    if 'frame_effects' in card:
        if 'extendedart' in card['frame_effects']:
            frameEffect: FrameEffect = FrameEffect.EXTENDED_ART
        elif 'showcase' in card['frame_effects']:
            frameEffect: FrameEffect = FrameEffect.SHOWCASE
        elif 'inverted' in card['frame_effects']:
            frameEffect: FrameEffect = FrameEffect.INVERTED
        else:
            frameEffect: FrameEffect = FrameEffect.NONE
    else:
        frameEffect: FrameEffect = FrameEffect.NONE

    return (borderType, frameEffect)


borderTypeToCount: Dict[TBorderInfo, int] = {}
borderTypeToCards: Dict[TBorderInfo, List[Dict[str, Any]]] = {}

bordlessCards = []
showcaseCards = []
extendedartCards = []
regularCards = []
for card in cards:
    borderInfo = getBorderInfo(card)

    if borderInfo not in borderTypeToCount:
        borderTypeToCount[borderInfo] = 0
    borderTypeToCount[borderInfo] += 1

    if borderInfo not in borderTypeToCards:
        borderTypeToCards[borderInfo] = []

    prices = card['prices']
    borderTypeToCards[borderInfo].append({
        "name": card['name'],
        "rarity": card['rarity'],
        "price": float(prices['usd']) if ('usd' in prices and prices['usd'] != None) else 0.0,
        "priceFoil": float(prices['usd_foil']) if ('usd_foil' in prices and prices['usd_foil'] != None) else 0.0,
    })


pprint(borderTypeToCount)
pprint(borderTypeToCards)


# print('Bordless: {}'.format(len(bordlessCards)))
# print('{}'.format(valToCount([card['rarity'] for card in bordlessCards])))
# dupeNames = list(valToCountAtLeastN([card['name'] for card in bordlessCards], 2).keys())
# printDupePrices(dupeNames, bordlessCards)
# print('{}\n'.format(valToCountAtLeastN([card['name'] for card in bordlessCards], 2)))

# print('Showcase: {}'.format(len(showcaseCards)))
# print('{}'.format(valToCount([card['rarity'] for card in showcaseCards])))
# dupeNames = list(valToCountAtLeastN([card['name'] for card in showcaseCards], 2).keys())
# printDupePrices(dupeNames, showcaseCards)
# print('{}\n'.format(valToCountAtLeastN([card['name'] for card in showcaseCards], 2)))

# print('Extended art: {}'.format(len(extendedartCards)))
# print('{}'.format(valToCount([card['rarity'] for card in extendedartCards])))
# dupeNames = list(valToCountAtLeastN([card['name'] for card in extendedartCards], 2).keys())
# printDupePrices(dupeNames, extendedartCards)
# print('{}\n'.format(valToCountAtLeastN([card['name'] for card in extendedartCards], 2)))

# print('Regular: {}'.format(len(regularCards)))
# print('{}'.format(valToCount([card['rarity'] for card in regularCards])))
# dupeNames = list(valToCountAtLeastN([card['name'] for card in regularCards], 2).keys())
# printDupePrices(dupeNames, regularCards)
# print('{}\n'.format(valToCountAtLeastN([card['name'] for card in regularCards], 2)))


