import statistics
import argparse
from time import sleep
from typing import Dict, Any

from set_util import SetUtil
from stats_util import StatsUtil
from print_util import PrintUtil
from file_util import FileUtil
from tcgplayer_api import TCGPlayerAPI


#
# Call one of:
#  - reportExpectedValues()
#  - reportSet(setName)
#  - reportMasterpieces()
#  - storeToFiles()
#
def main():
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers()

  #
  # Expected Values
  #
  parser_evs = subparsers.add_parser(
    'evs',
    help='Calculate Expected Value(s) of a set')

  parser_evs.add_argument(
    '-ep',
    '--exclPrice',
    type=float,
    default=0.0,
    help='Don\'t consider cards below this price in EV calculations')

  parser_evs.add_argument(
    '--set',
    type=str,
    default=None,
    help='Only calculate the EV for a specific set')

  parser_evs.add_argument(
    '-ss',
    '--showSkew',
    action='store_true',
    help='Show skew metrics (not super useful; takes up space)')

  parser_evs.add_argument(
    '-sa',
    '--sortByArbitrage',
    action='store_true',
    help='Sort by arbitrage opportunity (excl arbitrage if excl is enabled)')

  parser_evs.set_defaults(func=reportExpectedValues)

  #
  # Set Reporting
  #
  parser_set = subparsers.add_parser(
    'set',
    help='Report card prices in a set')

  parser_set.add_argument(
      '--set',
      type=str,
      required=True,
      help='Only report card prices for a specific set')

  parser_set.set_defaults(func=reportSet)

  #
  # Masterpieces Reporting
  #
  parser_masterpieces = subparsers.add_parser(
    'masterpieces',
    help='Report card prices for masterpieces')

  parser_masterpieces.set_defaults(func=reportMasterpieces)

  #
  # Store Card Prices
  #
  parser_storecards = subparsers.add_parser(
    'storecards',
    help='Store prices of cards in set(s)')

  parser_storecards.add_argument(
    '--set',
    type=str,
    help='Only store info for a specific set')

  parser_storecards.add_argument(
    '-mp',
    '--masterpieces',
    action='store_true',
    help='Only update masterpieces')

  parser_storecards.set_defaults(func=downloadCardsAndPersist)

  #
  # Store Box Prices
  #
  parser_storeboxes = subparsers.add_parser(
    'storeboxes',
    help='Store the market price of box(es)')

  parser_storeboxes.add_argument(
    '--set',
    type=str,
    help='Only store info for a specific set')

  parser_storeboxes.set_defaults(func=downloadBoxesAndPersist)

  args = parser.parse_args()
  args.func(args)



def reportExpectedValues(args):
  exclPrice = args.exclPrice
  name      = args.set
  showSkew  = args.showSkew
  sortByArbitrage = args.sortByArbitrage

  print('\nBoxes and their expected values:')
  if (exclPrice > 0):
    print('(EXCLUSIVE PRICE ${0:.2f})'.format(exclPrice))
  print('')

  nameToPriceInfo = FileUtil.getJSONContents(SetUtil.BOX_MARKET_PRICES_PATH)

  # Only report one set
  if (name):
    name = SetUtil.coerceToName(name)
    code = SetUtil.coerceToCode(name)
    cards = SetUtil.loadFromFile(name)
    cardsStats = StatsUtil.getCardsStats(cards, name, exclPrice=exclPrice)
    setStats = StatsUtil.getSetStats(name, cardsStats, exclPrice=exclPrice)
    marketPrice = nameToPriceInfo[name]['marketPrice']

    print(name)
    print('-' * len(name))
    print('Market\t${0:.2f}'.format(marketPrice))
    StatsUtil.printSetStats(setStats)
    return

  # Report ALL the sets!
  setNameToSetCards = SetUtil.loadAllFromFiles()
  setNameToBoxEVs = {}
  setNamesSorted = sorted(list(setNameToSetCards.keys()))

  for setName in setNamesSorted:
    cards = setNameToSetCards[setName]
    cardsStats = StatsUtil.getCardsStats(cards, setName, exclPrice=exclPrice)
    setStats = StatsUtil.getSetStats(setName, cardsStats, exclPrice=exclPrice)
    setNameToBoxEVs[setName] = setStats

  tableHeader = [
    ('Set', 'l'),
    ('EV',  'r'),
  ]

  if (exclPrice > 0):
    tableHeader.append(('EV (excl ${0:.2f})'.format(exclPrice), 'r'))

  arbitrageColName = 'Arbitrage (EV-MP)'
  tableHeader.extend([
    ('Market Price',   'r'),
    (arbitrageColName, 'r')
  ])


  if (exclPrice > 0):
    arbitrageColName = 'Arbitrage (excl ${0:.2f})'.format(exclPrice)
    tableHeader.append((arbitrageColName, 'r'))

  if (exclPrice == 0):
    tableHeader.append(('EV (median-based)', 'r'))

  if (showSkew):
    tableHeader.extend([
      ('Rare kurtosis',     'r'),
      ('Rare skew',         'r'),
      ('Mythic kurtosis',   'r'),
      ('Mythic skew',       'r'),
    ])

  tableRows = []

  for setName in setNamesSorted:
    if setName not in nameToPriceInfo:
      print(f"Set '{setName}' not in nameToPriceInfo")
      continue
    marketPrice = nameToPriceInfo[setName]['marketPrice']
    if marketPrice is None:
      print(f"Set '{setName}' has a null market price")
      continue
    evs = setNameToBoxEVs[setName]

    vals = [
      setName,
      round(evs['allAvg'], 2),
    ]

    if (exclPrice > 0):
      vals.append(round(evs['exAvg'], 2))

    vals.extend([
      round(marketPrice, 2),
      round(evs['allAvg'] - marketPrice, 2),
    ])

    if (exclPrice > 0):
      vals.append(round(evs['exAvg'] - marketPrice, 2))

    if (exclPrice == 0):
      vals.append(round(evs['allMed'], 2))

    if (showSkew):
      vals.extend([
        round(evs['r kurt'], 2),
        round(evs['r skew'], 2),
        round(evs['m kurt'], 2),
        round(evs['m skew'], 2),
      ])

    tableRows.append(vals)

  if (sortByArbitrage):
    sortby = arbitrageColName
    reverse = True
  else:
    sortby = None
    reverse = False

  print(PrintUtil.getTable(tableHeader, tableRows, sortby=sortby, reversesort=reverse))


def reportSet(args):
  setName = SetUtil.coerceToName(args.set)

  cards = SetUtil.loadFromFile(setName)
  stats = StatsUtil.getCardsStats(cards, setName)

  tableHeader = [
    ('Card', 'l'),
    ('Price', 'r'),
    ('Price (foil)', 'r')
  ]

  for rarity in ['common', 'uncommon', 'rare', 'mythic']:
    bucket = stats[rarity]
    descStats = bucket['all']
    cardToPrice = descStats['prices']
    cardToPriceFoil = descStats['pricesFoil']

    print('\n%s\n%s' % (rarity, ('-' * len(rarity))))
    print('(avg=%.2f, med=%.2f)' % (descStats['avg'], descStats['med']))

    tableRows = [
      [card, '{0:.2f}'.format(value), '{0:.2f}'.format(cardToPriceFoil[card])]
      for card, value in sorted(
        cardToPrice.items(),
        reverse=True,
        key=lambda cardAndPrice: cardAndPrice[1]
      )
    ]

    print(PrintUtil.getTable(tableHeader, tableRows))

  # If there are masterpieces, print those too
  mpCode = SetUtil.sets[setName]['masterpieceCode']
  if (mpCode):
    mpName = SetUtil.masterpieces[mpCode]['name']
    mpNameToPrice = SetUtil.getMasterpieceNameToPriceForSet(mpCode, setName)

    tableHeader = [
      ('Card', 'l'),
      ('Price', 'r')
    ]

    tableRows = [
      [name, '{0:.2f}'.format(value)]
      for name, value in sorted(
        mpNameToPrice.items(),
        reverse=True,
        key=lambda cardAndPrice: cardAndPrice[1]
      )
    ]

    mpPriceAvg = statistics.mean(mpNameToPrice.values())
    mpPriceMed = statistics.median(mpNameToPrice.values())

    mpFullName = 'masterpieces (%s)' % mpName
    print('\n%s\n%s' % (mpFullName, ('-' * len(mpFullName))))
    print('(avg=%.2f, med=%.2f)' % (mpPriceAvg, mpPriceMed))

    print(PrintUtil.getTable(tableHeader, tableRows))

  print('')


def reportMasterpieces(args):
  mps = SetUtil.masterpieces
  for mpCode in mps:
    mp = mps[mpCode]
    mpCards = SetUtil.loadFromFile(mp['name'])

    mpNameToPrice = {
      mpCard['name']: float(mpCard['prices']['usd_foil'])
      for mpCard in mpCards
    }

    mpPriceAvg = statistics.mean(mpNameToPrice.values())
    mpPriceMed = statistics.median(mpNameToPrice.values())

    tableHeader = [
      ('Card', 'l'),
      ('Price', 'r')
    ]

    tableRows = [
      [name, '{0:.2f}'.format(value)]
      for name, value in sorted(
        mpNameToPrice.items(),
        reverse=True,
        key=lambda cardAndPrice: cardAndPrice[1]
      )
    ]

    mpPriceTot = sum(mpNameToPrice.values())
    mpPriceAvg = statistics.mean(mpNameToPrice.values())
    mpPriceMed = statistics.median(mpNameToPrice.values())

    print('\n%s\n%s' % (mp['name'], ('-' * len(mp['name']))))
    print('(n=%d, avg=%.2f, med=%.2f, total=%.2f)' % (len(mpNameToPrice), mpPriceAvg, mpPriceMed, mpPriceTot))

    print(PrintUtil.getTable(tableHeader, tableRows))

def downloadCardsAndPersist(args):
  if (args.masterpieces):
    for i, mpCode in enumerate(SetUtil.masterpieces):
      mp = SetUtil.masterpieces[mpCode]
      mpCards = SetUtil.downloadCards(None, mpCode)
      SetUtil.persistSetCards(mp['name'], mpCards)

      # Let's hope to not get rate-limited
      if (i + 1 < len(SetUtil.masterpieces)):
        sleep(0.1)
    return

  if (args.set):
    setCode = SetUtil.coerceToCode(args.set)
    setName = SetUtil.coerceToShortestName(args.set)

    cards = SetUtil.downloadCards(setCode)
    SetUtil.persistSetCards(setName, cards)

    # Get masterpieces if necessary
    mpCode = SetUtil.sets[setName]['masterpieceCode']
    if (mpCode):
      mpName  = SetUtil.masterpieces[mpCode]['name']
      mpCards = SetUtil.downloadCards(None, mpCode)
      SetUtil.persistSetCards(mpName, mpCards)
  else:
    for i, setName in enumerate(SetUtil.sets):
      s = SetUtil.sets[setName]
      setCode = s['code']

      cards = SetUtil.downloadCards(setCode)
      SetUtil.persistSetCards(setName, cards)

      # Let's hope to not get rate-limited
      if (i + 1 < len(SetUtil.sets)):
        sleep(0.1)

    # Get all masterpieces
    for i, mpCode in enumerate(SetUtil.masterpieces):
      mp = SetUtil.masterpieces[mpCode]
      mpCards = SetUtil.downloadCards(None, mpCode)
      SetUtil.persistSetCards(mp['name'], mpCards)

      # Let's hope to not get rate-limited
      if (i + 1 < len(SetUtil.masterpieces)):
        sleep(0.1)

# TODO @nocommit Pick back up here!
def downloadBoxesAndPersist(args):
  TCGPlayerAPI.init()

  nameToInfo: Dict[str, Dict[str, Any]] = SetUtil.readBoxPrices()

  def getInfoForSet(name: str, setInfo: Dict[str, Any]):
    names = SetUtil.coerceToNames(name)
    name = list(names)[0]
    code = SetUtil.coerceToCode(name)
    skuID = int(setInfo['skuID'])
    price = TCGPlayerAPI.getMarketPrice(skuID)
    return {
      'marketPrice': price,
      'code': code,
    }

  if (args.set):
    names = SetUtil.coerceToNames(args.set)
    for name in names:
      print(f"Getting price for a box of {name}...")
      nameToInfo[name] = getInfoForSet(
        name,
        SetUtil.sets[name],
      )
  else:
    for i, (name, setInfo) in enumerate(SetUtil.sets.items()):
      print(f"Getting price for a box of {name}...")
      nameToInfo[name] = getInfoForSet(name, setInfo)
      # Let's hope to not get rate-limited
      if (i + 1 < len(SetUtil.sets)):
        sleep(0.1)

  SetUtil.persistBoxPrices(nameToInfo)


if __name__ == '__main__':
  main()
