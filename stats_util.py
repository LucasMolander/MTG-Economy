import statistics
from scipy.stats import kurtosis
from scipy.stats import skew

from set_util import SetUtil
from print_util import PrintUtil

class StatsUtil(object):
    """
    Houses useful card/set stats methods.
    """

    @staticmethod
    def getCardsStats(cards, setName, exclPrice=0):
        packsPerFoil = SetUtil.sets[setName]['packsPerFoil']

        ret = {
            'mythic': {
                'all': {
                    'n': 0,
                    'prices': {},
                    'sum': 0.0,
                    'avg': 0.0,
                    'med': 0.0,
                    'avgValAdd': 0.0,
                    'medValAdd': 0.0,
                    'pricesFoil': {},
                    'sumFoil': 0.0,
                    'avgFoil': 0.0,
                    'medFoil': 0.0,
                    'avgValAddFoil': 0.0,
                    'medValAddFoil': 0.0
                },
                'exclusive': {
                    'n': 0,
                    'prices': {},
                    'sum': 0.0,
                    'avg': 0.0,
                    'med': 0.0,
                    'avgValAdd': 0.0,
                    'medValAdd': 0.0,
                    'pricesFoil': {},
                    'sumFoil': 0.0,
                    'avgFoil': 0.0,
                    'medFoil': 0.0,
                    'avgValAddFoil': 0.0,
                    'medValAddFoil': 0.0
                }
            },
            'rare': {
                'all': {
                    'n': 0,
                    'prices': {},
                    'sum': 0.0,
                    'avg': 0.0,
                    'med': 0.0,
                    'avgValAdd': 0.0,
                    'medValAdd': 0.0,
                    'pricesFoil': {},
                    'sumFoil': 0.0,
                    'avgFoil': 0.0,
                    'medFoil': 0.0,
                    'avgValAddFoil': 0.0,
                    'medValAddFoil': 0.0
                },
                'exclusive': {
                    'n': 0,
                    'prices': {},
                    'sum': 0.0,
                    'avg': 0.0,
                    'med': 0.0,
                    'avgValAdd': 0.0,
                    'medValAdd': 0.0,
                    'pricesFoil': {},
                    'sumFoil': 0.0,
                    'avgFoil': 0.0,
                    'medFoil': 0.0,
                    'avgValAddFoil': 0.0,
                    'medValAddFoil': 0.0
                }
            },
            'uncommon': {
                'all': {
                    'n': 0,
                    'prices': {},
                    'sum': 0.0,
                    'avg': 0.0,
                    'med': 0.0,
                    'avgValAdd': 0.0,
                    'medValAdd': 0.0,
                    'pricesFoil': {},
                    'sumFoil': 0.0,
                    'avgFoil': 0.0,
                    'medFoil': 0.0,
                    'avgValAddFoil': 0.0,
                    'medValAddFoil': 0.0
                },
                'exclusive': {
                    'n': 0,
                    'prices': {},
                    'sum': 0.0,
                    'avg': 0.0,
                    'med': 0.0,
                    'avgValAdd': 0.0,
                    'medValAdd': 0.0,
                    'pricesFoil': {},
                    'sumFoil': 0.0,
                    'avgFoil': 0.0,
                    'medFoil': 0.0,
                    'avgValAddFoil': 0.0,
                    'medValAddFoil': 0.0
                }
            },
            'common': {
                'all': {
                    'n': 0,
                    'prices': {},
                    'sum': 0.0,
                    'avg': 0.0,
                    'med': 0.0,
                    'avgValAdd': 0.0,
                    'medValAdd': 0.0,
                    'pricesFoil': {},
                    'sumFoil': 0.0,
                    'avgFoil': 0.0,
                    'medFoil': 0.0,
                    'avgValAddFoil': 0.0,
                    'medValAddFoil': 0.0
                },
                'exclusive': {
                    'n': 0,
                    'prices': {},
                    'sum': 0.0,
                    'avg': 0.0,
                    'med': 0.0,
                    'avgValAdd': 0.0,
                    'medValAdd': 0.0,
                    'pricesFoil': {},
                    'sumFoil': 0.0,
                    'avgFoil': 0.0,
                    'medFoil': 0.0,
                    'avgValAddFoil': 0.0,
                    'medValAddFoil': 0.0
                }
            }
        }

        for c in cards:
            name = c['name']
            prices = c['prices']
            price = float(prices['usd']) if ('usd' in prices and prices['usd'] != None) else 0.0
            priceFoil = float(prices['usd_foil']) if ('usd_foil' in prices and prices['usd_foil'] != None) else 0.0

            bucket = ret[c['rarity']]

            bucket['all']['n']               += 1
            bucket['all']['prices'][name]     = price
            bucket['all']['pricesFoil'][name] = priceFoil

            if (price >= exclPrice):
                bucket['exclusive']['n'] += 1
                bucket['exclusive']['prices'][name] = price
            else:
                bucket['exclusive']['prices'][name] = 0

            if (priceFoil >= exclPrice):
                bucket['exclusive']['n'] += 1
                bucket['exclusive']['pricesFoil'][name] = priceFoil
            else:
                bucket['exclusive']['pricesFoil'][name] = 0

        rarityToProb = {
            'mythic':   1.0 / 8.0,
            'rare':     7.0 / 8.0,
            'uncommon': 3.0,
            'common':   10.0
        }

        totalProb = sum(rarityToProb.values())

        rarityToNormalizedProb = {
            rarity: prob / totalProb
            for rarity, prob in rarityToProb.items()
        }

        for rarity in ret:
            bucket = ret[rarity]
            p = rarityToProb[rarity]
            normalizedP = rarityToNormalizedProb[rarity]

            # For 'all' and 'exclusive'
            for subset in bucket:
                innerBucket = bucket[subset]

                # Non-foil prices first
                priceValues = list(innerBucket['prices'].values())
                if (len(priceValues) > 0):
                    innerBucket['sum']       = sum(priceValues)
                    innerBucket['avg']       = statistics.mean(priceValues)
                    innerBucket['med']       = statistics.median(priceValues)
                    innerBucket['avgValAdd'] = innerBucket['avg'] * p
                    innerBucket['medValAdd'] = innerBucket['med'] * p
                else:
                    innerBucket['sum']       = 0.0
                    innerBucket['avg']       = 0.0
                    innerBucket['med']       = 0.0
                    innerBucket['avgValAdd'] = 0.0
                    innerBucket['medValAdd'] = 0.0

                # Foil prices now
                foilPriceValues = list(innerBucket['pricesFoil'].values())
                if (len(priceValues) > 0 and packsPerFoil > 0):
                    innerBucket['sumFoil']       = sum(foilPriceValues)
                    innerBucket['avgFoil']       = statistics.mean(foilPriceValues)
                    innerBucket['medFoil']       = statistics.median(foilPriceValues)
                    innerBucket['avgValAddFoil'] = innerBucket['avgFoil'] * normalizedP / packsPerFoil
                    innerBucket['medValAddFoil'] = innerBucket['medFoil'] * normalizedP / packsPerFoil
                else:
                    innerBucket['sumFoil']       = 0.0
                    innerBucket['avgFoil']       = 0.0
                    innerBucket['medFoil']       = 0.0
                    innerBucket['avgValAddFoil'] = 0.0
                    innerBucket['medValAddFoil'] = 0.0

        return ret


    @staticmethod
    def getSetStats(setName, cardsStats, exclPrice=0):
        ret = {}

        setCode = SetUtil.coerceToCode(setName)

        nPacks = SetUtil.sets[setName]['nPacks']

        #
        # Calculate overall expected values
        #
        if (exclPrice > 0):
            # Average of cards that meet minimum price
            totalVA = 0.0
            for rarity in cardsStats:
                bucket   = cardsStats[rarity]
                totalVA += bucket['exclusive']['avgValAdd']
                totalVA += bucket['exclusive']['avgValAddFoil']

            ret['exAvg'] = totalVA * nPacks
        else:
            ret['exAvg'] = None

        # Average of non-foil cards
        totalVA = 0.0
        for rarity in cardsStats:
            bucket = cardsStats[rarity]
            totalVA += bucket['all']['avgValAdd']
            totalVA += bucket['all']['avgValAddFoil']

        ret['allAvg'] = totalVA * nPacks

        # Median of all cards
        totalVA = 0.0
        for rarity in cardsStats:
            bucket = cardsStats[rarity]
            totalVA += bucket['all']['medValAdd']

        ret['allMed'] = totalVA * nPacks

        # Median and average for masterpieces, if they exist
        mpCode = SetUtil.sets[setName]['masterpieceCode']
        if (mpCode):
            mpNameToPrice = SetUtil.getMasterpieceNameToPriceForSet(mpCode, setName)
            mpPriceAvg = statistics.mean(mpNameToPrice.values())
            mpPriceMed = statistics.median(mpNameToPrice.values())
            ret['allAvg'] += mpPriceAvg * SetUtil.MASTERPIECE_PROBABILITY * nPacks
            ret['allMed'] += mpPriceMed * SetUtil.MASTERPIECE_PROBABILITY * nPacks


        # Skewness
        mythicPriceValues = list(cardsStats['mythic']['all']['prices'].values())
        rarePriceValues   = list(cardsStats['rare']['all']['prices'].values())
        ret['m kurt'] = kurtosis(mythicPriceValues)
        ret['m skew'] = skew(mythicPriceValues)
        ret['r kurt'] = kurtosis(rarePriceValues)
        ret['r skew'] = skew(rarePriceValues)

        return ret


    @staticmethod
    def printSetStats(setStats):
        sortedEVs = sorted(list(setStats.keys()))
        for ev in sortedEVs:
            val = setStats[ev]
            ds = '$' if (ev not in ['m kurt', 'm skew', 'r kurt', 'r skew']) else ''

            if (ev == 'exAvg' and val == None):
                continue
            else:
                print('%s\t%s%.2f' % (ev, ds, val))

        print('\n')
