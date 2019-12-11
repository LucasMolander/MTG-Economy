import argparse
from pprint import pprint
import json
from time import sleep

from set_util import SetUtil
from stats_util import StatsUtil
from print_util import PrintUtil


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
        '--set',
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
            '--set',
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
        '--set',
        type=str,
        help='Only store info for a specific set')

    parser_store.set_defaults(func=storeToFiles)

    args = parser.parse_args()
    args.func(args)



def reportExpectedValues(args):
    exclPrice = args.exclPrice
    name      = args.set

    print('\nBoxes and their expected values:')
    if (exclPrice > 0):
        print('(EXCLUSIVE PRICE $%s)' % exclPrice)
    print('')

    # Only report one set
    if (name):
        name  = SetUtil.coerceToName(name)
        cards = SetUtil.loadFromFiles(only=name)
        cardsStats = StatsUtil.getCardsStats(cards, name, exclPrice=exclPrice)
        setStats = StatsUtil.getSetStats(name, cardsStats, exclPrice=exclPrice)

        print(name)
        print('-' * len(name))
        StatsUtil.printSetStats(setStats)
        return

    # Report ALL the sets!
    setNameToSetCards = SetUtil.loadFromFiles()
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
        tableHeader.append(('EV (excl $%s)' % exclPrice, 'r'))

    tableHeader.extend([
        ('EV (median-based)', 'r'),
        ('Rare kurtosis',     'r'),
        ('Rare skew',         'r'),
        ('Mythic kurtosis',   'r'),
        ('Mythic skew',       'r'),
    ])

    tableRows = []

    for setName in setNamesSorted:
        evs = setNameToBoxEVs[setName]

        vals = [
            setName,
            '{0:.2f}'.format(evs['allAvg']),
        ]

        if (exclPrice > 0):
            vals.append('{0:.2f}'.format(evs['exAvg']))

        vals.extend([
            '{0:.2f}'.format(evs['allMed']),
            '{0:.2f}'.format(evs['r kurt']),
            '{0:.2f}'.format(evs['r skew']),
            '{0:.2f}'.format(evs['m kurt']),
            '{0:.2f}'.format(evs['m skew']),
        ])

        tableRows.append(vals)

    print(PrintUtil.getTable(tableHeader, tableRows))


def reportSet(args):
    setName = SetUtil.coerceToName(args.set)

    cards = SetUtil.loadFromFiles(only=setName)
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

    print('')



def storeToFiles(args):
    if (args.set):
        setCode = SetUtil.coerceToCode(args.set)
        setName = SetUtil.coerceToName(args.set)

        cards = SetUtil.downloadCards(setCode)
        SetUtil.persist(setName, cards)
    else:
        for i, setName in enumerate(SetUtil.sets):
            s = SetUtil.sets[setName]
            setCode = s['code']

            cards = SetUtil.downloadCards(setCode)
            SetUtil.persist(setName, cards)

            # Let's hope to not get rate-limited
            if (i + 1 < len(SetUtil.sets)):
                sleep(0.5)


if __name__ == '__main__':
    main()

