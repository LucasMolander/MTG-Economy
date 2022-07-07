from pprint import pprint
import urllib.parse
import json
from enum import Enum, IntEnum
from typing import Optional, Tuple, Dict, Any, List, Type

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
from typing import Protocol

class CardCategorizer(Protocol):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    """Get the price of a card"""
  
  @staticmethod
  def getCatName() -> str:
    """Get the name of this category"""

  @staticmethod
  def getProbability() -> float:
    """Get the probability of having this card in a pack"""

  # def __str__(self) -> str:
  #   return self.getCatName()

  # def __repr__(self) -> str:
  #   return self.getCatName()


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
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    return None

  @staticmethod
  def getCatName() -> str:
    return "UNCATEGORIZABLE"
  
  @staticmethod
  def getProbability() -> float:
    return 0.0


class TexturedCategorizer(CardCategorizer):
  """
  These are ALL Mythic.
  """
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "promo_types" in card and "textured" in card["promo_types"]:
      return CardUtil.getFoilPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Textured Foil"
  
  @staticmethod
  def getProbability() -> float:
    # "Three percent of Collector Boosters contain a textured foil mythic rare"
    return 0.03


#
# Commons
#
class CommonFoilCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "common":
      return CardUtil.getFoilPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Common Foil"
  
  @staticmethod
  def getProbability() -> float:
    # "5 Traditional foil commons"
    return 5.0


class CommonBorderlessCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "common":
      if "border_color" in card and card["border_color"] == "borderless":
        return CardUtil.getPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Common Borderless"
  
  @staticmethod
  def getProbability() -> float:
    # "2 Non-foil borderless commons and/or uncommons"
    return 2.0 * (9.0 / (9.0 + 21.0))


class CommonBorderlessFoilCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "common":
      if "border_color" in card and card["border_color"] == "borderless":
        return CardUtil.getFoilPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Common Borderless Foil"
  
  @staticmethod
  def getProbability() -> float:
    # "2 Traditional foil borderless commons and/or uncommons"
    return 2.0 * (9.0 / (9.0 + 21.0))


#
# Uncommons
#
class UncommonFoilCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "uncommon":
      return CardUtil.getFoilPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Uncommon Foil"
  
  @staticmethod
  def getProbability() -> float:
    # "2 Traditional foil uncommons"
    return 2.0


class UncommonBorderlessCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "uncommon":
      if "border_color" in card and card["border_color"] == "borderless":
        return CardUtil.getPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Uncommon Borderless"
  
  @staticmethod
  def getProbability() -> float:
    # "2 Non-foil borderless commons and/or uncommons"
    return 2.0 * (21.0 / (9.0 + 21.0))


class UncommonBorderlessFoilCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "uncommon":
      if "border_color" in card and card["border_color"] == "borderless":
        return CardUtil.getFoilPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Uncommon Borderless Foil"
  
  @staticmethod
  def getProbability() -> float:
    # "2 Traditional foil borderless commons and/or uncommons"
    return 2.0 * (21.0 / (9.0 + 21.0))


#
# Rares
#
class RareCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "rare":
      return CardUtil.getPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Rare"


class RareFoilCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "rare":
      return CardUtil.getFoilPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Rare Foil"
  
  @staticmethod
  def getProbability() -> float:
    # "1 Traditional foil Rare/Mythic"
    return 120.0 / (120.0 + 40.0)


class RareBorderlessCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "rare":
      if "border_color" in card and "borderless" in card["border_color"]:
        return CardUtil.getPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Rare Borderless"
  
  @staticmethod
  def getProbability() -> float:
    # "1 Non-foil borderless Rare/Mythic"
    return 30.0 / (30.0 + 20.0)


class RareFoilEtchedCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "rare":
      if "finishes" in card and "etched" in card["finishes"]:
        return CardUtil.getEtchedPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Rare Foil-etched"
  
  @staticmethod
  def getProbability() -> float:
    # "1 Foil-etched Rare/Mythic"
    return 120.0 / (120.0 + 40.0)


class RareFoilBorderlessCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "rare":
      if "border_color" in card and "borderless" in card["border_color"]:
        return CardUtil.getFoilPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Rare Foil Borderless"
  
  @staticmethod
  def getProbability() -> float:
    # "1 Traditional foil borderless Rare/Mythic"
    # This slot also has a 3% chance of being Textured
    return 0.97 * (30.0 / (30.0 + 20.0))


#
# Mythics
#
class MythicCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "mythic":
      return CardUtil.getPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Mythic"


class MythicFoilCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "mythic":
      return CardUtil.getFoilPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Mythic Foil"
  
  @staticmethod
  def getProbability() -> float:
    # "1 Traditional foil Rare/Mythic"
    return 40.0 / (120.0 + 40.0)


class MythicBorderlessCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "mythic":
      if "border_color" in card and "borderless" in card["border_color"]:
        return CardUtil.getPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Mythic Borderless"
  
  @staticmethod
  def getProbability() -> float:
    # "1 Non-foil borderless Rare/Mythic"
    return 20.0 / (30.0 + 20.0)


class MythicFoilEtchedCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "mythic":
      if "finishes" in card and "etched" in card["finishes"]:
        return CardUtil.getEtchedPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Mythic Foil-etched"
  
  @staticmethod
  def getProbability() -> float:
    # "1 Foil-etched Rare/Mythic"
    return 40.0 / (120.0 + 40.0)


class MythicFoilBorderlessCategorizer(CardCategorizer):
  @staticmethod
  def getPrice(card: Dict[str, Any]) -> Optional[float]:
    if "rarity" in card and card["rarity"] == "mythic":
      if "border_color" in card and "borderless" in card["border_color"]:
        return CardUtil.getFoilPrice(card)
    return None

  @staticmethod
  def getCatName() -> str:
    return "Mythic Foil Borderless"
  
  @staticmethod
  def getProbability() -> float:
    # "1 Traditional foil borderless Rare/Mythic"
    # This slot also has a 3% chance of being Textured
    return 0.97 * (20.0 / (30.0 + 20.0))



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
  def categorizePrices(cards: List[Dict[str, Any]]) -> Dict[Type[CardCategorizer], Dict[str, float]]:
    """
    Returns a map from category to card name to price.
    """
    catToNameToPrice: Dict[Type[CardCategorizer], Dict[str, float]] = {}

    # For each card, get the price of each category it is
    for card in cards:
      name = card["name"]
      catToPrice = DoubleMasters2022Collectors.getCatToPriceForCard(card)
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

  @staticmethod
  def getCatToPriceForCard(card: Dict[str, Any]) -> Dict[Type[CardCategorizer], float]:
    catToPrice: Dict[Type[CardCategorizer], float] = {}

    # Textured first (and if so, that's it)
    p = TexturedCategorizer.getPrice(card)
    if p is not None:
      catToPrice[TexturedCategorizer] = p
      return catToPrice
    
    # Commons
    CommonFoilCategorizer.updateCatToPrice(catToPrice, card)
    CommonBorderlessCategorizer.updateCatToPrice(catToPrice, card)
    CommonBorderlessFoilCategorizer.updateCatToPrice(catToPrice, card)

    # Uncommons
    UncommonFoilCategorizer.updateCatToPrice(catToPrice, card)
    UncommonBorderlessCategorizer.updateCatToPrice(catToPrice, card)
    UncommonBorderlessFoilCategorizer.updateCatToPrice(catToPrice, card)

    # Rares
    RareFoilCategorizer.updateCatToPrice(catToPrice, card)
    RareBorderlessCategorizer.updateCatToPrice(catToPrice, card)
    RareFoilEtchedCategorizer.updateCatToPrice(catToPrice, card)
    RareFoilBorderlessCategorizer.updateCatToPrice(catToPrice, card)

    # Mythics
    MythicFoilCategorizer.updateCatToPrice(catToPrice, card)
    MythicBorderlessCategorizer.updateCatToPrice(catToPrice, card)
    MythicFoilEtchedCategorizer.updateCatToPrice(catToPrice, card)
    MythicFoilBorderlessCategorizer.updateCatToPrice(catToPrice, card)

    return catToPrice



class DistUtil(object):
  @staticmethod
  def getDistInfo(catToPrices: Dict[Type[CardCategorizer], List[float]], exclPrice: float = 0.0) -> Dict[Type[CardCategorizer], Any]:
    catToDistInfo = {}
    for cat, prices in catToPrices.items():
      pricesFiltered: List[float] = [
        p
        for p in prices
        if p >= exclPrice
      ]
      if len(pricesFiltered) > 0:
        # n = len(pricesFiltered)
        # total = sum(pricesFiltered)
        # med = median(pricesFiltered)
        # avg = mean(pricesFiltered)
        # prob = cat.getProbability()
        # ev = prob * avg

        # if exclPrice == 0.0:
        #   catToDistInfo[cat] = {
        #     "n": n,
        #     "prob": round(prob, 5),
        #     "ev": round(ev, 2),
        #     "sum": round(total, 2),
        #     "med": round(med, 2),
        #     "avg": round(avg, 2),
        #   }
        # else:
        #   orig_n = len(prices)
        #   orig_total = sum(prices)
        #   orig_med = median(prices)
        #   orig_avg = mean(prices)
        #   orig_ev = prob * orig_avg
        #   catToDistInfo[cat] = {
        #     "orig_n": orig_n,
        #     "orig_ev": round(orig_ev, 2),
        #     "orig_sum": round(orig_total, 2),
        #     "orig_med": round(orig_med, 2),
        #     "orig_avg": round(orig_avg, 2),
        #   }

        orig_n = len(prices)
        n = len(pricesFiltered)
        total = sum(pricesFiltered)
        med = median(pricesFiltered)
        avg = mean(pricesFiltered)
        avg_ep = total / orig_n
        prob = cat.getProbability()
        ev = prob * avg_ep

        catToDistInfo[cat] = {
          "n": n,
          "prob": round(prob, 5),
          "ev": round(ev, 2),
          "sum": round(total, 2),
          "med": round(med, 2),
          "avg": round(avg, 2),
        }

        if exclPrice > 0.0:
          orig_total = sum(prices)
          orig_med = median(prices)
          orig_avg = mean(prices)
          orig_ev = prob * orig_avg
          catToDistInfo[cat].update({
            "orig_n": orig_n,
            "orig_ev": round(orig_ev, 2),
            "orig_sum": round(orig_total, 2),
            "orig_med": round(orig_med, 2),
            "orig_avg": round(orig_avg, 2),
          })

    return catToDistInfo
    


name = "2x2"
code = SetUtil.coerceToCode(name)
name = SetUtil.coerceToName(name)

cards = SetUtil.loadFromFile(setName=name)

print(f"{name} has {len(cards)} cards")

catToNameToPrice = DoubleMasters2022Collectors.categorizePrices(cards)

# Try also looking at it a bit of a different way
nameToCatToPrice: Dict[str, Dict[Type[CardCategorizer], float]] = {}
for cat, nameToPrice in catToNameToPrice.items():
  for name, price in nameToPrice.items():
    if name not in nameToCatToPrice:
      nameToCatToPrice[name] = {}
    nameToCatToPrice[name][cat] = price

print("\nCategory to name to price:\n")
# print(json.dumps(catToNameToPrice, indent=2))
print(catToNameToPrice)
print("\nName to category to price:\n")
# print(json.dumps(nameToCatToPrice, indent=2))
print(nameToCatToPrice)

catToPrices: Dict[Type[CardCategorizer], List[float]] = {
  cat: list(nameToPrice.values())
  for cat, nameToPrice in catToNameToPrice.items()
}
catToDistInfo = DistUtil.getDistInfo(catToPrices)
ep = 5.0
catToDistInfoEP = DistUtil.getDistInfo(catToPrices, exclPrice=ep)

print("\n\nCategory to distribution info:\n")
pprint(catToDistInfo)
print(f"\n\nCategory to distribution info (exclusive price = ${ep}):\n")
pprint(catToDistInfoEP)

catnameToEV = {
  cat.getCatName(): distInfo['ev']
  for cat, distInfo in catToDistInfo.items()
}
catnameToEVEP = {
  cat.getCatName(): distInfo['ev']
  for cat, distInfo in catToDistInfoEP.items()
}
print("\n\nCategory to EV:\n")
pprint(catnameToEV)
print(f"\n\nCategory to EV (exclusive price = ${ep}):\n")
pprint(catnameToEVEP)

totalEV = round(sum(list(catnameToEV.values())), 2)
totalEVEP = round(sum(list(catnameToEVEP.values())), 2)
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
