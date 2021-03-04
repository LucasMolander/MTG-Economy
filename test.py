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



cards = SetUtil.loadFromFiles(only="Core Set 2021")
print('Total number of cards: {}\n'.format(len(cards)))


bordlessCards = []
showcaseCards = []
extendedartCards = []
regularCards = []
for card in cards:
    if card['border_color'] == 'borderless':
        bordlessCards.append(card)
    elif 'frame_effects' in card and 'showcase' in card['frame_effects']:
        showcaseCards.append(card)
    elif 'frame_effects' in card and 'extendedart' in card['frame_effects']:
        extendedartCards.append(card)
    else:
        regularCards.append(card)

print('Bordless: {}'.format(len(bordlessCards)))
print('{}'.format(valToCount([card['rarity'] for card in bordlessCards])))
dupeNames = list(valToCountAtLeastN([card['name'] for card in bordlessCards], 2).keys())
printDupePrices(dupeNames, bordlessCards)
print('{}\n'.format(valToCountAtLeastN([card['name'] for card in bordlessCards], 2)))

print('Showcase: {}'.format(len(showcaseCards)))
print('{}'.format(valToCount([card['rarity'] for card in showcaseCards])))
dupeNames = list(valToCountAtLeastN([card['name'] for card in showcaseCards], 2).keys())
printDupePrices(dupeNames, showcaseCards)
print('{}\n'.format(valToCountAtLeastN([card['name'] for card in showcaseCards], 2)))

print('Extended art: {}'.format(len(extendedartCards)))
print('{}'.format(valToCount([card['rarity'] for card in extendedartCards])))
dupeNames = list(valToCountAtLeastN([card['name'] for card in extendedartCards], 2).keys())
printDupePrices(dupeNames, extendedartCards)
print('{}\n'.format(valToCountAtLeastN([card['name'] for card in extendedartCards], 2)))

print('Regular: {}'.format(len(regularCards)))
print('{}'.format(valToCount([card['rarity'] for card in regularCards])))
dupeNames = list(valToCountAtLeastN([card['name'] for card in regularCards], 2).keys())
printDupePrices(dupeNames, regularCards)
print('{}\n'.format(valToCountAtLeastN([card['name'] for card in regularCards], 2)))


