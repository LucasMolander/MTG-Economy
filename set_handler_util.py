from abc import abstractmethod
from dataclasses import dataclass
import random
from statistics import mean, median
from typing import Any, ClassVar, Dict, List, Protocol, Type, runtime_checkable

from card_categorizers import CardCategorizer, Uncategorizable


"""
The Set Handlers themselves are in `set_handlers.py`.
This just has the abstract classes, util classes, etc. that make them
nice and easy to work with.
"""


@dataclass
class CatInfoForSet:
  prob: float
  """Probability of encountering this category of card in a booster pack"""
  actualN: int
  """Actual number of cards of this category in the set"""


CatNamePrice = Dict[Type[CardCategorizer], Dict[str, float]]
CatstrNamePrice = Dict[str, Dict[str, float]]
CatPrices = Dict[Type[CardCategorizer], List[float]]
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
    ratio = ep.n / len(allPrices)
    return DistInfoEP(
      prob=ep.prob,
      n=ep.n,
      n_exp=ep.n_exp,
      ev=ep.ev * ratio,
      sum=ep.sum * ratio,
      med=ep.med * ratio,
      avg=ep.avg * ratio,
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

  PACKS_PER_BOX: ClassVar[int]

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

  @classmethod
  def randomPackVal(cls, catToPrices: CatPrices, exclPrice: float = 0.0) -> float:
    total = 0.0
    for cat, info in cls.CAT_TO_INFO.items():
      if random.random() < info.prob:
        p = random.choice(catToPrices[cat])
        total += p if p >= exclPrice else 0.0
    return round(total, 2)

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
