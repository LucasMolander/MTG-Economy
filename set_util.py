import sys
import urllib
import requests
import json

from file_util import FileUtil


class SetUtil(object):

    SETS_PATH = 'sets.json'
    CARDS_DIR = 'card_prices'

    sets = FileUtil.getJSONContents(SETS_PATH)

    #
    # TODO
    # Care about this later
    #
    # nameToCodeOld = {
    #     'Alpha':     'lea',
    #     'Beta':      'leb',
    #     'Unlimited': '2ed',
    #     'Collector\'s Edition': 'ced',
    #     'Arabian Nights': 'arn',
    #     'Antiquities': 'atq',
    #     'Revised': '3ed',
    #     'Legends': 'leg',
    #     'The Dark': 'drk',
    #     'Fallen Empires': 'fem',
    #     'Fourth Edition': '4ed',
    #     'Ice Age': 'ice'
    # }


    @staticmethod
    def downloadCards(setCode):
        print('Getting cards for %s' % setCode)
        sys.stdout.flush()

        cards = []

        baseURL = 'https://api.scryfall.com/cards/search?q='
        query = urllib.quote_plus('set=%s' % setCode)

        finalURL = baseURL + query

        r = requests.get(finalURL)

        if (r.status_code != 200):
            print('Bad return status (' + r.status_code + ' != 200)! Returning none.')
            return None

        response = json.loads(r.text)
        cards.extend(response['data'])

        nCards = response['total_cards']

        # Might be pagified
        while (response['has_more'] == True):
            print('\tGetting more cards for %s...' % setCode)
            sys.stdout.flush()

            url = response['next_page']
            r = requests.get(url)

            if (r.status_code != 200):
                print('Bad return status (' + r.status_code + ' != 200)! Returning none.')
                return None

            response = json.loads(r.text)
            cards.extend(response['data'])

        return cards


    @staticmethod
    def persist(setName, cards):
        filePath = '%s/%s' % (SetUtil.CARDS_DIR, setName)
        with open(filePath, 'w') as f:
            f.write(json.dumps(cards))


    @staticmethod
    def loadFromFiles(only=None):
        if (only):
            return FileUtil.getJSONContents('%s/%s' % (SetUtil.CARDS_DIR, only))

        return {
            name: FileUtil.getJSONContents('%s/%s' % (SetUtil.CARDS_DIR, name))
            for name in SetUtil.sets
        }
