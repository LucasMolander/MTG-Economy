import argparse
from pprint import pprint
import json

from set_util import SetUtil
from stats_util import StatsUtil



#
# Call one of:
#  - reportExpectedValues()
#  - reportSet(setName)
#  - storeToFiles()
#
def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_evs = subparsers.add_parser('evs')
    parser_evs.add_argument('--exclPrice', type=float, default=0.0)
    parser_evs.add_argument('--setName', type=str, default=None)
    parser_evs.set_defaults(func=reportExpectedValues)

    parser_set = subparsers.add_parser('set')
    parser_set.add_argument('--name', type=str, required=True)
    parser_set.set_defaults(func=reportSet)

    parser_store = subparsers.add_parser('store')
    parser_store.add_argument('--only', type=str)
    parser_store.set_defaults(func=storeToFiles)

    args = parser.parse_args()
    args.func(args)



def reportExpectedValues(args):
    exclPrice = args.exclPrice
    name = args.setName

    print('\nBoxes and their expected values:')
    if (exclPrice > 0):
        print('(EXCLUSIVE PRICE $%s)' % exclPrice)
    print('')

    if (name):
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
    setName = args.name

    cards = SetUtil.loadFromFiles(only=setName)
    stats = StatsUtil.getCardsStats(cards)

    for rarity in ['mythic', 'rare', 'uncommon', 'common']:
        bucket = stats[rarity]
        descStats = bucket['all']
        cardToPrice = descStats['prices']

        print('\n%s\n%s' % (rarity, ('-' * len(rarity))))
        print('(avg=%.2f, med=%.2f)' % (descStats['avg'], descStats['med']))

        # Sort by price descending
        for key, value in sorted(cardToPrice.iteritems(), reverse=True, key=lambda (k,v): (v,k)):
            print "%s: %s" % (key, value)

    print('')



def storeToFiles(args):
    if (args.only):
        setName = args.only
        s = SetUtil.sets[setName]
        setCode = s['code']

        cards = SetUtil.downloadCards(setCode)
        SetUtil.persist(setName, cards)
    else:
        for setName in SetUtil.sets:
            s = SetUtil.sets[setName]
            setCode = s['code']

            cards = SetUtil.downloadCards(setCode)
            SetUtil.persist(setName, cards)



main()

