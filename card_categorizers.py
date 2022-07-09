from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, Protocol, Type, runtime_checkable

"""
These are used primarily by Set Handlers (see `set_handlers.py`).

Card Categorizers are used to get the categories for cards.
A card's JSON can represent multiple "cards" you can get from a pack.
For example, it could give you the foil version (usd_foil) and non-foil (usd).
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
