
"""
These Set Handlers will use Card Categorizers to categorize the JSON cards and
get distribution information (including EV).
"""

from math import sqrt
from typing import Any, Dict, List, Type

from card_categorizers import *
from set_handler_util import CatInfoForSet, MTGSetHandler

class Util:
  @staticmethod
  def getQuadZeroes(a: float, b: float, c: float) -> List[float]:
    """
    For y = a*x^2 + b*x + c.
    Returns the root(s) in ascending order.
    """
    det = (b*b) - (4*a*c)
    base = -b
    if det == 0.0:
      # One zero with multiplicity 2
      return [base/(2*a)]
    elif det > 0.0:
      sqrtDet = sqrt(det)
      return [(base - sqrtDet)/(2*a), (base + sqrtDet)/(2*a)]
    else:
      # Imaginary roots only. No zeroes
      return []


class DoubleMasters2022(MTGSetHandler):
  """
  See magic.wizards.com/en/articles/archive/feature/collecting-double-masters-2022-and-product-overview-2022-06-16

  Double Masters 2022 boster boxes have these contents:
  * 8 Commons
  * 3 Uncommons
  * 2 Rares and/or mythic rares
  * 2 Traditional foil cards of any rarity
  * 1 Cryptic Spires
  * 1 Token or ad card
  """
  NAME = "Double Masters 2022"
  CODE = "2x2"

  # Regular, borderless, foil-etched
  n_c =  92; n_bl_c =  9
  n_u =  80; n_bl_u = 21
  n_r = 120; n_bl_r = 30; n_fe_r = 120
  n_m =  40; n_bl_m = 20; n_fe_m =  40

  n_regular_c = n_c - n_bl_c
  n_regular_u = n_u - n_bl_u
  n_regular_r = n_r - n_bl_r
  n_regular_m = n_m - n_bl_m

  # p = probability of a given Rare/Mythic being borderless:
  # Probability of neither = (1-p)*(1-p) = 0.89
  # I know that this assumes independence.
  # We can do math to figure out 1*p^2 - 2*p + 0.11 = 0.0.
  # Turns out to be ~5.66% for either one.
  # Fun fact: both borderless is about 1/312
  zeroes = [
    z
    for z in Util.getQuadZeroes(1.0, -2.0, 0.11)
    if 0.0 <= z and z <= 1.0
  ]
  p_rm_bl = zeroes[0] if len(zeroes) > 0 else 0.0566

  # Regular = regular-only + bl-potential*regular-rate
  # Borderless = bl-potential*bl-rate
  c = (n_regular_c + (n_bl_c * 2/3)) / n_c
  u = (n_regular_u + (n_bl_u * 2/3)) / n_u
  bl_c = (n_bl_c * 1/3) / n_c
  bl_u = (n_bl_u * 1/3) / n_u

  # Rare and Mythic are probably 7:1
  # Rare = not-borderless * rare
  # Borderless Rare = borderless * rare
  r = (1 - p_rm_bl) * 7/8
  m = (1 - p_rm_bl) * 1/8
  bl_r = p_rm_bl * 7/8
  bl_m = p_rm_bl * 1/8

  # Foil Common/Uncommon is 23/24
  # Foil Rare/Mythic is 1/24
  # Foil Common:Uncommon are probably 3:1
  # Foil Rare:Mythic is probably 7:1
  p_f_c = (23/24) * 3/4
  p_f_u = (23/24) * 1/4
  p_f_r = (1/24)  * 7/8
  p_f_m = (1/24)  * 1/8

  # TODO Check these
  f_c = p_f_c * (n_regular_c + (n_bl_c * 2/3)) / n_c
  f_u = p_f_u * (n_regular_u + (n_bl_u * 2/3)) / n_u
  f_r = p_f_r * (n_regular_r + (n_bl_r * 2/3)) / n_r
  f_m = p_f_m * (n_regular_m + (n_bl_m * 2/3)) / n_m

  # TODO Check these too
  f_bl_c = p_f_c * (n_bl_c * 1/3) / n_c
  f_bl_u = p_f_u * (n_bl_u * 1/3) / n_u
  f_bl_r = p_f_r * (n_bl_r * 1/3) / n_r
  f_bl_m = p_f_m * (n_bl_m * 1/3) / n_m


  CAT_TO_INFO = {
    # Regular
    CommonCat:   CatInfoForSet(prob=8*c, actualN=n_c),
    UncommonCat: CatInfoForSet(prob=3*u, actualN=n_u),
    RareCat:     CatInfoForSet(prob=2*r, actualN=n_r),
    MythicCat:   CatInfoForSet(prob=2*m, actualN=n_m),

    # Borderless
    CommonBorderlessCat:   CatInfoForSet(prob=8*bl_c, actualN=n_bl_c),
    UncommonBorderlessCat: CatInfoForSet(prob=3*bl_u, actualN=n_bl_u),
    RareBorderlessCat:     CatInfoForSet(prob=2*bl_r, actualN=n_bl_r),
    MythicBorderlessCat:   CatInfoForSet(prob=2*bl_m, actualN=n_bl_m),

    # Foil
    CommonFoilCat:   CatInfoForSet(prob=2*f_c, actualN=n_c),
    UncommonFoilCat: CatInfoForSet(prob=2*f_u, actualN=n_u),
    RareFoilCat:     CatInfoForSet(prob=2*f_r, actualN=n_r),
    MythicFoilCat:   CatInfoForSet(prob=2*f_m, actualN=n_m),

    # Borderless Foil
    CommonBorderlessFoilCat:   CatInfoForSet(prob=2*f_bl_c, actualN=n_bl_c),
    UncommonBorderlessFoilCat: CatInfoForSet(prob=2*f_bl_u, actualN=n_bl_u),
    RareBorderlessFoilCat:     CatInfoForSet(prob=2*f_bl_r, actualN=n_bl_r),
    MythicBorderlessFoilCat:   CatInfoForSet(prob=2*f_bl_m, actualN=n_bl_m),
  }

  @staticmethod
  def getCatToPriceForCard(card: Dict[str, Any]) -> Dict[Type[CardCategorizer], float]:
    catToPrice: Dict[Type[CardCategorizer], float] = {}

    cats = list(DoubleMasters2022.CAT_TO_INFO.keys())
    for cat in cats:
      cat.updateCatToPrice(catToPrice, card)

    return catToPrice


class DoubleMasters2022Collectors(MTGSetHandler):
  """
  See magic.wizards.com/en/articles/archive/feature/collecting-double-masters-2022-and-product-overview-2022-06-16

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

  # Based on this post from reddit:
  # /r/mtgfinance/comments/vqj904/2x2_collector_mythic_pull_rates/
  # The raios for Mythic / Rare are:
  #   * Foil: 7:1
  #   * Foil-etched: 7:1
  #   * Borderless: 4:1
  #   * Borderless Foil: 4:1

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
  f_r = 6 / 7
  f_m = 1 / 7

  # 1 Foil-etched Rare/Mythic
  fe_r = 6 / 7
  fe_m = 1 / 7

  # 1 Non-foil borderless Rare/Mythic
  bl_r = 3 / 4
  bl_m = 1 / 4

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
    RareBorderlessFoilCat:     CatInfoForSet(prob=f_bl_r, actualN=n_bl_r),
    MythicFoilCat:             CatInfoForSet(prob=f_m, actualN=n_m),
    MythicBorderlessCat:       CatInfoForSet(prob=bl_m, actualN=n_bl_m),
    MythicFoilEtchedCat:       CatInfoForSet(prob=fe_m, actualN=n_fe_m),
    MythicBorderlessFoilCat:   CatInfoForSet(prob=f_bl_m, actualN=n_bl_m),
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
