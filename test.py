from abc import abstractclassmethod, abstractmethod, abstractstaticmethod
from dataclasses import asdict, dataclass, is_dataclass
from pprint import pprint
import urllib.parse
import json
from enum import Enum, IntEnum
from typing import ClassVar, Optional, Tuple, Dict, Any, List, Type
from card_categorizers import CardCategorizer
from set_handlers import DoubleMasters2022Collectors

from tcgplayer_api import TCGPlayerAPI
from set_util import SetUtil
from file_util import FileUtil

from statistics import mean, median



"""
Four different "Liliana, the Last Hope" cards from Double Masters 2022:


332 cards total
*
*
*
* 5


* Regular (black border)
* Borderless,                  inverted frame, boosterfun promo
* Black border, etched finish, inverted frame, boosterfun promo
* Borderless,     foil finish, inverted frame, textured and boosterfun promo



THEY DO IT LIKE THIS FOR DOUBLE MASTERS
384 total
* 332 In Boosters              set:2xm is:booster
* 2   Borderless Planeswalkers set:2xm border:borderless type:planeswalker
* 38  Alternate-art Borderless set:2xm border:borderless -type:planeswalker
* 2   Buy-a-Box                set:2xm is:bab
* 10  Cards (lands)            set:2xm not:booster not:bab border:black




THEY DO IT LIKE THIS FOR DOUBLE MASTERS 2022
579 total
* 332 In Boosters              set:2x2 is:nonfoil is:booster
* 2   Borderless Planeswalkers set:2x2 is:nonfoil border:borderless type:planeswalker
* 78  Alternate-art Borderless set:2x2 is:nonfoil border:borderless -type:planeswalker
* 160 Etched Foil-only         set:2x2 is:etched not:nonfoil not:foil
* 5   Textured Foil            set:2x2 is:textured
* 2   Promos                   set:2x2 is:promo

Double Masters 2022 Breakdowns
In Boosters
* 92  Common     set:2x2 is:nonfoil is:booster rarity:common
* 80  Uncommon   set:2x2 is:nonfoil is:booster rarity:uncommon
* 120 Rare       set:2x2 is:nonfoil is:booster rarity:rare
* 40  Mythic     set:2x2 is:nonfoil is:booster rarity:mythic

Borderless
* 9  Common     set:2x2 is:nonfoil border:borderless rarity:common
* 21 Uncommon   set:2x2 is:nonfoil border:borderless rarity:uncommon
* 30 Rare       set:2x2 is:nonfoil border:borderless rarity:rare
* 20 Mythic     set:2x2 is:nonfoil border:borderless rarity:mythic

Etched
* 120 Rare    set:2x2 is:etched not:nonfoil not:foil rarity:rare
* 40  Mythic  set:2x2 is:etched not:nonfoil not:foil rarity:mythic


COLLECTOR'S ONLY
----------------
4 packs per box

(2 foil Rare/Mythic)
Each Collector booster has 1 foil-etched Rare/Mythic
and 1 traditional foil Rare/Mythic

(2 borderless Rare/Mythic)
Each Collector box has 2 Rare/Mythic borderless.
One is non-foil, and the other is foil (traditional OR textured).
  - 3% of Collector boosters have a textured foil card (all are Mythic)
  - 97% of the foil borderless Rare/Mythic will be traditional


Each booster has two borderless Rare/Mythics.
One is foil (traditional or textured)
  -

Each booster also has a foil-etched Rare/Mythic,
as well as a traditional foil Rare/Mythic.

Contents:
  * 5 Traditional foil commons
  * 2 Traditional foil uncommons
  * 2 Non-foil borderless commons and/or uncommons
  * 2 Traditional foil borderless commons and/or uncommons
  * 1 Traditional foil Rare/Mythic
  * 1 Non-foil borderless Rare/Mythic
  * 1 Foil-etched Rare/Mythic
  * 1 Traditional foil borderless Rare/Mythic or 1 textured foil mythic rare
      - NOTE: 3% chance to be textured

Probability * avg_val_of_what?:
  * 5 Traditional foil commons
  * 2 Traditional foil uncommons
  * 2 Non-foil borderless commons and/or uncommons
  * 2 Traditional foil borderless commons and/or uncommons
  * 1 Traditional foil Rare/Mythic
  * 1 Non-foil borderless Rare/Mythic
  * 1 Foil-etched Rare/Mythic
  * 1 Traditional foil borderless Rare/Mythic or 1 textured foil mythic rare




DRAFT BOOSTERS
--------------
24 packs per box

Common and Uncommon that can be borderless, are, 2:1 (one third)
Same goes for the foil versions

(rare slot being borderless)
11% of boosters contain >= 1 non-foil borderless Rare/Mythic.
You can get 2 of them in a single pack.

(foil slot borderless Rare/Mythic)
Each foil slot has 1.25% chance to be traditional foil borderless borderless Rare/Mythic.
You can get 2 of them in a single pack.

Contents:
  * 8 Commons
  * 3 Uncommons
  * 2 Rares and/or mythic rares
  * 2 Traditional foil cards of any rarity
  * 1 Cryptic Spires
  * 1 Token or ad card
"""



class MyJSONEncoder(json.JSONEncoder):
  @staticmethod
  def roundDict(d: Dict[Any, Any]) -> Dict[Any, Any]:
    return {
      # k: f"{v:.2f}" if isinstance(v, float) else v
      k: round(v, 2) if isinstance(v, float) else v
      for k, v in d.items()
    }

  @staticmethod
  def stringifyObjsRecursive(d: Dict[Any, Any]) -> Dict[Any, Any]:
    out = {}
    for k, v in d.items():
      theK = k.CAT_NAME if isinstance(k, CardCategorizer) else k

      theV: Any
      if isinstance(v, dict):
        theV = MyJSONEncoder.stringifyObjsRecursive(v)
      elif isinstance(v, CardCategorizer):
        theV = v.CAT_NAME
      else:
        theV = v
      out[theK] = theV
    return out

  def default(self, o):
    # print(f"default(): {o}")
    if is_dataclass(o):
      return MyJSONEncoder.roundDict(asdict(o))
    elif isinstance(o, dict):
      return MyJSONEncoder.roundDict(o)
    else:
      return o

  def encode(self, o):
    # print(f"encode() input: {o}")
    if is_dataclass(o):
      theObj = MyJSONEncoder.roundDict(asdict(o))
    elif isinstance(o, dict):
      theObj = MyJSONEncoder.roundDict(o)
      theObj = MyJSONEncoder.stringifyObjsRecursive(theObj)
    else:
      theObj = o
    # print(f"\tencode() giving: {theObj}")
    return super().encode(theObj)


mtgSet = DoubleMasters2022Collectors

code = SetUtil.coerceToCode(mtgSet.NAME)
name = SetUtil.coerceToName(mtgSet.NAME)

cards = SetUtil.loadFromFile(setName=name)
print(f"{name} has {len(cards)} cards")

catToNameToPrice = mtgSet.categorizePrices(cards)
# Try also looking at it a bit of a different way
nameToCatToPrice = mtgSet.reorderCatToNameToPrice(catToNameToPrice)

ep = 5.0
catToDistinfo = mtgSet.getDistinfos(catToNameToPrice)
catToDistinfoEP = mtgSet.getDistinfos(catToNameToPrice, exclPrice=ep)

print("\n\nCategory to distribution info:")
print(json.dumps(catToDistinfo, indent=2, cls=MyJSONEncoder))
print(f"\n\nCategory to distribution info (exclusive price = ${ep}):")
print(json.dumps(catToDistinfoEP, indent=2, cls=MyJSONEncoder))

catToEV = {
  catstr: distInfo.ev
  for catstr, distInfo in catToDistinfo.items()
}
catToEVEP = {
  catstr: distInfo.ev
  for catstr, distInfo in catToDistinfoEP.items()
}
print("\n\nCategory to EV:")
print(json.dumps(catToEV, indent=2, cls=MyJSONEncoder))
print(f"\n\nCategory to EV (exclusive price = ${ep}):")
print(json.dumps(catToEVEP, indent=2, cls=MyJSONEncoder))

totalEV = round(sum(list(catToEV.values())), 2)
totalEVEP = round(sum(list(catToEVEP.values())), 2)
print(f"\n\nTotal EV: {totalEV}")
print(f"\n\nTotal EV (exclusive price = ${ep}): {totalEVEP}")



# TCGPlayerAPI.init()

# print("\nBearer token:")
# print(TCGPlayerAPI.bearerToken)
# print('')

# marketPrice = TCGPlayerAPI.getMarketPrice(1086072)
# print(f"Market price: {marketPrice}")






# nameToInfo: Dict[str, Dict[str, Any]] = {}

# N = 5
# for i, (name, s) in enumerate(SetUtil.sets.items()):
#   if i > N:
#     break
#   name = SetUtil.coerceToName(name)
#   code = SetUtil.coerceToCode(name)
#   skuID = int(s['skuID'])
#   price = TCGPlayerAPI.getMarketPrice(skuID)

#   nameToInfo[name] = {
#     'marketPrice': price,
#     'code': code,
#   }

# SetUtil.persistBoxPrices(nameToInfo)





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
