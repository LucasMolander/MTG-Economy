from abc import abstractclassmethod, abstractmethod, abstractstaticmethod
from dataclasses import asdict, dataclass, is_dataclass
from pprint import pprint
import urllib.parse
import json
from enum import Enum, IntEnum
from typing import ClassVar, Optional, Tuple, Dict, Any, List, Type

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

class CardUtil(object):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "prices" in card and "usd" in card["prices"] and card["prices"]["usd"] is not None:
      return float(card["prices"]["usd"])
    else:
      return None

  @staticmethod
  def getFoilPrice(card: Dict[str, Any]) -> Optional[float]:
    if "prices" in card and "usd_foil" in card["prices"] and card["prices"]["usd_foil"] is not None:
      return float(card["prices"]["usd_foil"])
    else:
      return None

  @staticmethod
  def getEtchedPrice(card: Dict[str, Any]) -> Optional[float]:
    if "prices" in card and "usd_etched" in card["prices"] and card["prices"]["usd_etched"] is not None:
      return float(card["prices"]["usd_etched"])
    else:
      return None


# ------------------------------------------------------------------------------
#                                 CATEGORIZERS
# ------------------------------------------------------------------------------
from typing import Protocol, runtime_checkable

@dataclass
class CatInfoForSet:
  prob: float
  """Probability of encountering this category of card in a booster pack"""
  actualN: int
  """Actual number of cards of this category in the set"""

@runtime_checkable
class CardCategorizer(Protocol):
  CAT_NAME: ClassVar[str]
  """Name of this category"""

  @staticmethod
  @abstractmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    """Get the price of a card"""
    raise NotImplementedError

  @classmethod
  def updateCatToPrice(cls, catToPrice: Dict[Type["CardCategorizer"], float], card: Dict[str, Any]) -> None:
    """Convenience for simple logic elsewhere in `getCatToPriceForCard`"""
    p = cls.getPrice(card)
    if p is not None:
      catToPrice[cls] = p

class Uncategorizable(CardCategorizer):
  """
  Just a placeholder/dummy class
  """
  CAT_NAME = 'UNCATEGORIZABLE'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    return None


class TexturedCat(CardCategorizer):
  """
  These are ALL Mythic.
  """
  CAT_NAME = 'Textured Foil'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "promo_types" in card and "textured" in card["promo_types"]:
      return CardUtil.getFoilPrice(card)
    return None


#
# Commons
#
class CommonFoilCat(CardCategorizer):
  CAT_NAME = 'Common Foil'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "common":
      return CardUtil.getFoilPrice(card)
    return None

class CommonBorderlessCat(CardCategorizer):
  CAT_NAME = 'Common Borderless'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "common":
      if "border_color" in card and card["border_color"] == "borderless":
        return CardUtil.getPrice(card)
    return None

class CommonBorderlessFoilCat(CardCategorizer):
  CAT_NAME = 'Common Borderless Foil'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "common":
      if "border_color" in card and card["border_color"] == "borderless":
        return CardUtil.getFoilPrice(card)
    return None


#
# Uncommons
#
class UncommonFoilCat(CardCategorizer):
  CAT_NAME = 'Uncommon Foil'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "uncommon":
      return CardUtil.getFoilPrice(card)
    return None

class UncommonBorderlessCat(CardCategorizer):
  CAT_NAME = 'Uncommon Borderless'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "uncommon":
      if "border_color" in card and card["border_color"] == "borderless":
        return CardUtil.getPrice(card)
    return None

class UncommonBorderlessFoilCat(CardCategorizer):
  CAT_NAME = 'Uncommon Borderless Foil'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "uncommon":
      if "border_color" in card and card["border_color"] == "borderless":
        return CardUtil.getFoilPrice(card)
    return None


#
# Rares
#
class RareCat(CardCategorizer):
  CAT_NAME = 'Rare'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "rare":
      return CardUtil.getPrice(card)
    return None

class RareFoilCat(CardCategorizer):
  CAT_NAME = 'Rare Foil'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "rare":
      return CardUtil.getFoilPrice(card)
    return None

class RareBorderlessCat(CardCategorizer):
  CAT_NAME = 'Rare Borderless'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "rare":
      if "border_color" in card and "borderless" in card["border_color"]:
        return CardUtil.getPrice(card)
    return None

class RareFoilEtchedCat(CardCategorizer):
  CAT_NAME = 'Rare Foil-etched'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "rare":
      if "finishes" in card and "etched" in card["finishes"]:
        return CardUtil.getEtchedPrice(card)
    return None

class RareFoilBorderlessCat(CardCategorizer):
  CAT_NAME = 'Rare Foil Borderless'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "rare":
      if "border_color" in card and "borderless" in card["border_color"]:
        return CardUtil.getFoilPrice(card)
    return None


#
# Mythics
#
class MythicCat(CardCategorizer):
  CAT_NAME = 'Mythic'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "mythic":
      return CardUtil.getPrice(card)
    return None

class MythicFoilCat(CardCategorizer):
  CAT_NAME = 'Mythic Foil'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "mythic":
      return CardUtil.getFoilPrice(card)
    return None

class MythicBorderlessCat(CardCategorizer):
  CAT_NAME = 'Mythic Borderless'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "mythic":
      if "border_color" in card and "borderless" in card["border_color"]:
        return CardUtil.getPrice(card)
    return None

class MythicFoilEtchedCat(CardCategorizer):
  CAT_NAME = 'Mythic Foil-etched'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "mythic":
      if "finishes" in card and "etched" in card["finishes"]:
        return CardUtil.getEtchedPrice(card)
    return None

class MythicFoilBorderlessCat(CardCategorizer):
  CAT_NAME = 'Mythic Foil Borderless'

  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "mythic":
      if "border_color" in card and "borderless" in card["border_color"]:
        return CardUtil.getFoilPrice(card)
    return None


# ------------------------------------------------------------------------------
#                    SET LOGIC USING CATEGORIZERS
# ------------------------------------------------------------------------------
CatNamePrice = Dict[Type[CardCategorizer], Dict[str, float]]
CatstrNamePrice = Dict[str, Dict[str, float]]
NameCatPrice = Dict[str, Dict[Type[CardCategorizer], float]]
NameCatstrPrice = Dict[str, Dict[str, float]]

@dataclass
class DistInfo:
  prob: float
  n: int
  n_exp: int
  ev: float
  sum: float
  med: float
  avg: float

  @staticmethod
  def fromPrices(prices: List[float], catinfo: CatInfoForSet) -> "DistInfo":
    return DistInfo(
      prob=catinfo.prob,
      n=len(prices),
      n_exp=catinfo.actualN,
      ev=mean(prices) * catinfo.prob,
      sum=sum(prices),
      med=median(prices),
      avg=mean(prices),
    )


@dataclass
class DistInfoEP(DistInfo):
  """n, ev, etc. will be for EP. These will be for ep=0"""
  orig_n: int
  orig_ev: float
  orig_sum: float
  orig_med: float
  orig_avg: float

  @staticmethod
  def fromRegular(ep: DistInfo, allPrices: List[float]) -> "DistInfoEP":
    return DistInfoEP(
      prob=ep.prob,
      n=ep.n,
      n_exp=ep.n_exp,
      ev=ep.ev,
      sum=ep.sum,
      med=ep.med,
      avg=ep.avg,
      orig_n=len(allPrices),
      orig_ev=mean(allPrices) * ep.prob,
      orig_sum=sum(allPrices),
      orig_med=median(allPrices),
      orig_avg=mean(allPrices),
    )


CatDistinfo = Dict[Type[CardCategorizer], DistInfo]


@runtime_checkable
class MTGSetHandler(Protocol):
  NAME: ClassVar[str]
  CODE: ClassVar[str]

  CAT_TO_INFO: ClassVar[Dict[Type[CardCategorizer], CatInfoForSet]]

  @staticmethod
  @abstractmethod
  def getCatToPriceForCard(card: Dict[str, Any]) -> Dict[Type[CardCategorizer], float]:
    raise NotImplementedError

  @classmethod
  def categorizePrices(cls, cards: List[Dict[str, Any]]) -> CatNamePrice:
    """
    Returns a map from category to card name to price.
    To make the map more readable (`str` instead of `Type[CardCategorizer]`),
    pass the result into
    """
    catToNameToPrice: CatNamePrice = {}

    # For each card, get the price of each category it is
    for card in cards:
      name = card["name"]
      catToPrice = cls.getCatToPriceForCard(card)
      for cat, price in catToPrice.items():
        if cat not in catToNameToPrice:
          catToNameToPrice[cat] = {}
        catToNameToPrice[cat][name] = price

      if len(catToPrice) == 0:
        cat = Uncategorizable
        if cat not in catToNameToPrice:
          catToNameToPrice[cat] = {}
        catToNameToPrice[cat][name] = 0.0

    return catToNameToPrice

  @classmethod
  def getDistinfos(cls, catToNameToPrice: CatNamePrice, exclPrice: float = 0.0) -> CatDistinfo:
    catToDistInfo = {}

    catToPrices: Dict[Type[CardCategorizer], List[float]] = {
      cat: list(nameToPrice.values())
      for cat, nameToPrice in catToNameToPrice.items()
    }
    for cat, prices in catToPrices.items():
      if cat not in cls.CAT_TO_INFO:
        continue
      pricesFilt: List[float] = [
        p for p in prices if p >= exclPrice
      ]
      if len(pricesFilt) == 0:
        continue
      catinfo = cls.CAT_TO_INFO[cat]

      distinfo = DistInfo.fromPrices(pricesFilt, catinfo)
      if exclPrice > 0.0:
        distinfo = DistInfoEP.fromRegular(distinfo, prices)

      catToDistInfo[cat] = distinfo

    return catToDistInfo


  # ----------------------------
  #   RANDOM UTILITY FUNCTIONS
  # ----------------------------
  @staticmethod
  def stringifyCatToNameToPrice(catToNameToPrice: CatNamePrice) -> CatstrNamePrice:
    """
    Takes the result from `categorizePrices` and stringifies the Categorizer.
    """
    return {
      cat.CAT_NAME: nameToPrice
      for cat, nameToPrice in catToNameToPrice.items()
    }

  @staticmethod
  def reorderCatToNameToPrice(catToNameToPrice: CatNamePrice) -> NameCatPrice:
    """
    Takes the result from `categorizePrices` and swaps the order of the first
    two keys to make it nameToCatToPrice
    """
    nameToCatToPrice: NameCatPrice = {}
    for cat, nameToPrice in catToNameToPrice.items():
      for name, price in nameToPrice.items():
        if name not in nameToCatToPrice:
          nameToCatToPrice[name] = {}
        nameToCatToPrice[name][cat] = price
    return nameToCatToPrice

  @staticmethod
  def stringifyNameToCatToPrice(nameToCatToPrice: NameCatPrice) -> NameCatstrPrice:
    nameToCatstrToPrice: NameCatstrPrice = {}
    for name, catToPrice in nameToCatToPrice.items():
      nameToCatstrToPrice[name] = {
        cat.CAT_NAME: price
        for cat, price in catToPrice.items()
      }
    return nameToCatstrToPrice


class DoubleMasters2022Collectors(MTGSetHandler):
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
  NAME = "Double Masters 2022"
  CODE = "2x2"

  # Regular, borderless, foil-etched
  n_c =  92; n_bl_c =  9
  n_u =  80; n_bl_u = 21
  n_r = 120; n_bl_r = 30; n_fe_r = 120
  n_m =  40; n_bl_m = 20; n_fe_m =  40

  # 2 Non-foil borderless Common/Uncommon
  # and 2 Foil borderless Common/Uncommon
  two_bl_c = 2.0 * (n_bl_c / (n_bl_c + n_bl_u))
  two_bl_u = 2.0 * (n_bl_u / (n_bl_c + n_bl_u))

  # 1 Foil Rare/Mythic
  f_r = n_r / (n_r + n_m)
  f_m = n_m / (n_r + n_m)

  # 1 Foil-etched Rare/Mythic
  fe_r = n_fe_r / (n_fe_r + n_fe_m)
  fe_m = n_fe_m / (n_fe_r + n_fe_m)

  # 1 Non-foil borderless Rare/Mythic
  bl_r = n_bl_r / (n_bl_r + n_bl_m)
  bl_m = n_bl_m / (n_bl_r + n_bl_m)

  # 1 Foil borderless Rare/Mythic
  # This slot also has a 3% chance of being Textured
  f_bl_r = 0.97 * bl_r
  f_bl_m = 0.97 * bl_m

  CAT_TO_INFO = {
    TexturedCat:               CatInfoForSet(prob=0.03, actualN=5),
    CommonFoilCat:             CatInfoForSet(prob=5.0, actualN=n_c),
    CommonBorderlessCat:       CatInfoForSet(prob=two_bl_c, actualN=n_bl_c),
    CommonBorderlessFoilCat:   CatInfoForSet(prob=two_bl_c, actualN=n_bl_c),
    UncommonFoilCat:           CatInfoForSet(prob=2.0, actualN=n_u),
    UncommonBorderlessCat:     CatInfoForSet(prob=two_bl_u, actualN=n_bl_u),
    UncommonBorderlessFoilCat: CatInfoForSet(prob=two_bl_u, actualN=n_bl_u),
    RareFoilCat:               CatInfoForSet(prob=f_r, actualN=n_r),
    RareBorderlessCat:         CatInfoForSet(prob=bl_r, actualN=n_bl_r),
    RareFoilEtchedCat:         CatInfoForSet(prob=fe_r, actualN=n_fe_r),
    RareFoilBorderlessCat:     CatInfoForSet(prob=f_bl_r, actualN=n_bl_r),
    MythicFoilCat:             CatInfoForSet(prob=f_m, actualN=n_m),
    MythicBorderlessCat:       CatInfoForSet(prob=bl_m, actualN=n_bl_m),
    MythicFoilEtchedCat:       CatInfoForSet(prob=fe_m, actualN=n_fe_m),
    MythicFoilBorderlessCat:   CatInfoForSet(prob=f_bl_m, actualN=n_bl_m),
  }

  @staticmethod
  def getCatToPriceForCard(card: Dict[str, Any]) -> Dict[Type[CardCategorizer], float]:
    catToPrice: Dict[Type[CardCategorizer], float] = {}

    # Textured first (and if so, that's it)
    p = TexturedCat.getPrice(card)
    if p is not None:
      catToPrice[TexturedCat] = p
      return catToPrice

    # Commons
    CommonFoilCat.updateCatToPrice(catToPrice, card)
    CommonBorderlessCat.updateCatToPrice(catToPrice, card)
    CommonBorderlessFoilCat.updateCatToPrice(catToPrice, card)

    # Uncommons
    UncommonFoilCat.updateCatToPrice(catToPrice, card)
    UncommonBorderlessCat.updateCatToPrice(catToPrice, card)
    UncommonBorderlessFoilCat.updateCatToPrice(catToPrice, card)

    # Rares
    RareFoilCat.updateCatToPrice(catToPrice, card)
    RareBorderlessCat.updateCatToPrice(catToPrice, card)
    RareFoilEtchedCat.updateCatToPrice(catToPrice, card)
    RareFoilBorderlessCat.updateCatToPrice(catToPrice, card)

    # Mythics
    MythicFoilCat.updateCatToPrice(catToPrice, card)
    MythicBorderlessCat.updateCatToPrice(catToPrice, card)
    MythicFoilEtchedCat.updateCatToPrice(catToPrice, card)
    MythicFoilBorderlessCat.updateCatToPrice(catToPrice, card)

    return catToPrice


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
      # if k is Type[CardCategorizer]:
      # # if isinstance(k, Type[CardCategorizer]):
      # a = k is CardCategorizer
      # b = k is Type[CardCategorizer]
      # c = isinstance(k, CardCategorizer)
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

# print("\nCategory to name to price:")
# print(json.dumps(catToNameToPrice, indent=2, cls=MyJSONEncoder))
# print("\nName to category to price:")
# print(json.dumps(nameToCatToPrice, indent=2, cls=MyJSONEncoder))

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
