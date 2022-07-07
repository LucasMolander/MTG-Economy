from pprint import pprint
import urllib.parse
import json
from enum import Enum, IntEnum
from typing import Optional, Tuple, Dict, Any, List, Type

from tcgplayer_api import TCGPlayerAPI
from set_util import SetUtil
from file_util import FileUtil



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
  * (5 Traditional foil commons
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



NEW (getting finishes correctly now)
------------------------------------
{
  "booster": true,
  "border_color": "black",
  "finishes": [
    "nonfoil",
    "foil"
  ],
  "foil": true,
  "frame": "2015",
  "full_art": false,
  "name": "Liliana, the Last Hope",
  "nonfoil": true,
  "prices": {
    "eur": "9.69",
    "eur_foil": "23.82",
    "tix": "1.67",
    "usd": "19.20",
    "usd_etched": null,
    "usd_foil": "35.25"
  },
  "rarity": "mythic",
  "reserved": false,
  "set_type": "masters",
  "textless": false,
  "variation": false
},

{
  "booster": false,
  "border_color": "borderless",
  "finishes": [
    "nonfoil",
    "foil"
  ],
  "foil": true,
  "frame": "2015",
  "frame_effects": [
    "inverted"
  ],
  "full_art": false,
  "name": "Liliana, the Last Hope",
  "nonfoil": true,
  "prices": {
    "eur": null,
    "eur_foil": null,
    "tix": null,
    "usd": "41.17",
    "usd_etched": null,
    "usd_foil": "46.35"
  },
  "promo_types": [
    "boosterfun"
  ],
  "rarity": "mythic",
  "reserved": false,
  "set_type": "masters",
  "textless": false,
  "variation": false
},

{
  "booster": false,
  "border_color": "black",
  "finishes": [
    "etched"
  ],
  "foil": false,
  "frame": "2015",
  "frame_effects": [
    "inverted"
  ],
  "full_art": false,
  "name": "Liliana, the Last Hope",
  "nonfoil": false,
  "prices": {
    "eur": null,
    "eur_foil": null,
    "tix": null,
    "usd": null,
    "usd_etched": "73.33",
    "usd_foil": null
  },
  "promo_types": [
    "boosterfun"
  ],
  "rarity": "mythic",
  "reserved": false,
  "set_type": "masters",
  "textless": false,
  "variation": false
},

{
  "booster": false,
  "border_color": "borderless",
  "finishes": [
    "foil"
  ],
  "foil": true,
  "frame": "2015",
  "frame_effects": [
    "inverted"
  ],
  "full_art": false,
  "name": "Liliana, the Last Hope",
  "nonfoil": false,
  "prices": {
    "eur": null,
    "eur_foil": null,
    "tix": null,
    "usd": null,
    "usd_etched": null,
    "usd_foil": "770.71"
  },
  "promo_types": [
    "textured",
    "boosterfun"
  ],
  "rarity": "mythic",
  "reserved": false,
  "set_type": "masters",
  "textless": false,
  "variation": false
},





OLD (before getting finishes correctly)
---------------------------------------
{
  "booster": true,
  "border_color": "black",
  "foil": true,
  "frame": "2015",
  "full_art": false,
  "name": "Liliana, the Last Hope",
  "nonfoil": true,
  "prices": {
    "eur": "9.69",
    "eur_foil": "23.82",
    "tix": "1.67",
    "usd": "19.20",
    "usd_etched": null,
    "usd_foil": "35.25"
  },
  "rarity": "mythic",
  "reserved": false,
  "set_type": "masters",
  "textless": false,
  "variation": false
},

{
  "booster": false,
  "border_color": "borderless",
  "foil": true,
  "frame": "2015",
  "frame_effects": [
    "inverted"
  ],
  "full_art": false,
  "name": "Liliana, the Last Hope",
  "nonfoil": true,
  "prices": {
    "eur": null,
    "eur_foil": null,
    "tix": null,
    "usd": "41.17",
    "usd_etched": null,
    "usd_foil": "46.35"
  },
  "rarity": "mythic",
  "reserved": false,
  "set_type": "masters",
  "textless": false,
  "variation": false
},


{
  "booster": false,
  "border_color": "black",
  "foil": false,
  "frame": "2015",
  "frame_effects": [
    "inverted"
  ],
  "full_art": false,
  "name": "Liliana, the Last Hope",
  "nonfoil": false,
  "prices": {
    "eur": null,
    "eur_foil": null,
    "tix": null,
    "usd": null,
    "usd_etched": "73.33",
    "usd_foil": null
  },
  "rarity": "mythic",
  "reserved": false,
  "set_type": "masters",
  "textless": false,
  "variation": false
},

{
  "booster": false,
  "border_color": "borderless",
  "foil": true,
  "frame": "2015",
  "frame_effects": [
    "inverted"
  ],
  "full_art": false,
  "name": "Liliana, the Last Hope",
  "nonfoil": false,
  "prices": {
    "eur": null,
    "eur_foil": null,
    "tix": null,
    "usd": null,
    "usd_etched": null,
    "usd_foil": "770.71"
  },
  "rarity": "mythic",
  "reserved": false,
  "set_type": "masters",
  "textless": false,
  "variation": false
},

"""


# ------------------------------------------------------------------------------
#                                 CATEGORIZERS
# ------------------------------------------------------------------------------
from typing import Protocol

class CardCategorizer(Protocol):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    """Get the price of a card"""
  
  @staticmethod
  def getCatName() -> str:
    """Get the name of this category"""

  @classmethod
  def updateCatToPrice(cls, catToPrice: Dict[str, float], card: Dict[str, Any]) -> None:
    """Convenience for simple logic elsewhere in `getCatToPriceForCard`"""
    p = cls.getPrice(card)
    if p is not None:
      catToPrice[cls.getCatName()] = p


class TexturedCategorizer(CardCategorizer):
  """
  These are ALL Mythic.
  """
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "promo_types" in card and "textured" in card["promo_types"]:
      if "prices" in card and "usd_foil" in card["prices"]:
        return card["prices"]["usd_foil"]
    return None

  @staticmethod
  def getCatName() -> str:
    return "Textured Foil"

#
# Commons
#
class CommonFoilCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "common":
      if "prices" in card and "usd_foil" in card["prices"]:
        return card["prices"]["usd_foil"]
    return None

  @staticmethod
  def getCatName() -> str:
    return "Common Foil"


class CommonBorderlessCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "common":
      if "border_color" in card and card["border_color"] == "borderless":
        if "prices" in card and "usd" in card["prices"]:
          return card["prices"]["usd"]
    return None

  @staticmethod
  def getCatName() -> str:
    return "Common Borderless"


class CommonBorderlessFoilCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "common":
      if "border_color" in card and card["border_color"] == "borderless":
        if "prices" in card and "usd_foil" in card["prices"]:
          return card["prices"]["usd_foil"]
    return None

  @staticmethod
  def getCatName() -> str:
    return "Common Borderless Foil"


#
# Uncommons
#
class UncommonFoilCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "uncommon":
      if "prices" in card and "usd_foil" in card["prices"]:
        return card["prices"]["usd_foil"]
    return None

  @staticmethod
  def getCatName() -> str:
    return "Uncommon Foil"


class UncommonBorderlessCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "uncommon":
      if "border_color" in card and card["border_color"] == "borderless":
        if "prices" in card and "usd" in card["prices"]:
          return card["prices"]["usd"]
    return None

  @staticmethod
  def getCatName() -> str:
    return "Uncommon Borderless"


class UncommonBorderlessFoilCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "uncommon":
      if "border_color" in card and card["border_color"] == "borderless":
        if "prices" in card and "usd_foil" in card["prices"]:
          return card["prices"]["usd_foil"]
    return None

  @staticmethod
  def getCatName() -> str:
    return "Uncommon Borderless Foil"


# ------------------------------------------------------------------------------
#                  CATEGORY LOGIC FOR DOUBLE MASTERS 2022
# ------------------------------------------------------------------------------

class DoubleMasters2022Collectors(object):
  """
  Double Masters 2022 Collector's edition boster boxes have these contents:
    * 5 Traditional foil commons
    * 2 Traditional foil uncommons
    * 2 Non-foil borderless commons and/or uncommons
    * 2 Traditional foil borderless commons and/or uncommons
    * 1 Traditional foil Rare/Mythic
    * 1 Non-foil borderless Rare/Mythic
    * 1 Foil-etched Rare/Mythic
    * 1 Traditional foil borderless Rare/Mythic or 1 textured foil mythic rare
      - NOTE: 3% chance to be textured
  """
  @staticmethod
  def categorizePrices(cards: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Returns a map from category to card name to price.
    """
    catToNameToPrice: Dict[str, Dict[str, Any]] = {}

    # For each card, get the price of each category it is
    for card in cards:
      name = card["name"]
      catToPrice = DoubleMasters2022Collectors.getCatToPriceForCard(card)
      for cat, price in catToPrice.items():
        if cat not in catToNameToPrice:
          catToNameToPrice[cat] = {}
        catToNameToPrice[cat][name] = price

    return catToNameToPrice

  @staticmethod
  def getCatToPriceForCard(card: Dict[str, Any]) -> Dict[str, float]:
    catToPrice: Dict[str, float] = {}

    # Textured first (and if so, that's it)
    p = TexturedCategorizer.getPrice(card)
    if p is not None:
      catToPrice[TexturedCategorizer.getCatName()] = p
      return catToPrice
    
    # Commons
    CommonFoilCategorizer.updateCatToPrice(catToPrice, card)
    CommonBorderlessCategorizer.updateCatToPrice(catToPrice, card)
    CommonBorderlessFoilCategorizer.updateCatToPrice(catToPrice, card)

    # Uncommons
    UncommonFoilCategorizer.updateCatToPrice(catToPrice, card)
    UncommonBorderlessCategorizer.updateCatToPrice(catToPrice, card)
    UncommonBorderlessFoilCategorizer.updateCatToPrice(catToPrice, card)

    return catToPrice



name = "2x2"
code = SetUtil.coerceToCode(name)
name = SetUtil.coerceToName(name)

cards = SetUtil.loadFromFile(setName=name)

print(f"{name} has {len(cards)} cards")

categorized = DoubleMasters2022Collectors.categorizePrices(cards)

pprint(categorized)








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
