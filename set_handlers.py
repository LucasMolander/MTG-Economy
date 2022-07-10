
"""
These Set Handlers will use Card Categorizers to categorize the JSON cards and
get distribution information (including EV).
"""

from typing import Any, Dict, Type

from card_categorizers import *
from set_handler_util import CatInfoForSet, MTGSetHandler


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
