import argparse
from pprint import pprint
import json

from set_util import SetUtil
from stats_util import StatsUtil
from print_util import PrintUtil







# MASSIVE TODO
# Take into account the fact that the new prices are stored as
# usd, usd_foil, etc

# ALSO
# Print stuff out in those nice table things :D










#
# Call one of:
#  - reportExpectedValues()
#  - reportSet(setName)
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
        '--exclPrice',
        type=float,
        default=0.0,
        help='Don\'t consider cards below this price in EV calculations')

    parser_evs.add_argument(
        '--setName',
        type=str,
        default=None,
        help='Only calculate the EV for a specific set')

    parser_evs.set_defaults(func=reportExpectedValues)

    #
    # Set Reporting
    #
    parser_set = subparsers.add_parser(
        'set',
        help='Report card prices in a set')

    parser_set.add_argument(
            '--name',
            type=str,
            required=True,
            help='Only report card prices for a specific set')

    parser_set.set_defaults(func=reportSet)

    #
    # Storing Set Information
    #
    parser_store = subparsers.add_parser(
        'store',
        help='Locally price info from the internet')

    parser_store.add_argument(
        '--only',
        type=str,
        help='Only store info for a specific set')

    parser_store.set_defaults(func=storeToFiles)

    args = parser.parse_args()
    args.func(args)



def reportExpectedValues(args):
    exclPrice = args.exclPrice
    name      = args.setName

    print('\nBoxes and their expected values:')
    if (exclPrice > 0):
        print('(EXCLUSIVE PRICE $%s)' % exclPrice)
    print('')

    if (name):
        name  = SetUtil.coerceToName(name)
        cards = SetUtil.loadFromFiles(only=name)
        cardsStats = StatsUtil.getCardsStats(cards, exclPrice=exclPrice)
        setStats = StatsUtil.getSetStats(name, cardsStats, exclPrice=exclPrice)

        print(name)
        print('-' * len(name))
        StatsUtil.printSetStats(setStats)
        return

    setNameToSetCards = SetUtil.loadFromFiles()
    setNameToBoxEVs = {}
    setNamesSorted = sorted(list(setNameToSetCards.keys()))

    for setName in setNamesSorted:
        cards = setNameToSetCards[setName]
        cardsStats = StatsUtil.getCardsStats(cards, exclPrice=exclPrice)
        setStats = StatsUtil.getSetStats(setName, cardsStats, exclPrice=exclPrice)
        setNameToBoxEVs[setName] = setStats

    # pprint(setNameToBoxEVs)
    for setName in setNamesSorted:
        evs = setNameToBoxEVs[setName]

        print(setName)
        print('-' * len(setName))
        StatsUtil.printSetStats(evs)



def reportSet(args):
    setName = SetUtil.coerceToName(args.name)

    cards = SetUtil.loadFromFiles(only=setName)
    stats = StatsUtil.getCardsStats(cards)

    tableHeader = [('Card', 'l'), ('Price', 'r'), ('Price (foil)', 'r')]

    for rarity in ['mythic', 'rare', 'uncommon', 'common']:
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

    print('')



def storeToFiles(args):
    if (args.only):
        setCode = SetUtil.coerceToCode(args.only)
        setName = SetUtil.coerceToName(args.only)

        cards = SetUtil.downloadCards(setCode)
        SetUtil.persist(setName, cards)
    else:
        for setName in SetUtil.sets:
            s = SetUtil.sets[setName]
            setCode = s['code']

            cards = SetUtil.downloadCards(setCode)
            SetUtil.persist(setName, cards)



main()

