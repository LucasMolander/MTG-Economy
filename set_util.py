import sys
# import urllib
import urllib.parse
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
    def getSetToCode():
        return {
            setName: SetUtil.sets[setName]['code']
            for setName in SetUtil.sets.keys()
        }

    #
    # Assumes that the set of all codes AND names are unique with each other.
    #
    @staticmethod
    def coerceToCode(setCodeOrName):
        setToCode = SetUtil.getSetToCode()

        # Set name; return the code
        if setCodeOrName in setToCode:
            return setToCode[setCodeOrName]

        # Set code; return it
        if setCodeOrName in setToCode.values():
            return setCodeOrName

        raise Exception('Invalid set name or code: %s' % setCodeOrName)

    #
    # Assumes that the set of all codes AND names are unique with each other.
    # Also assumes that there's a 1:1 mapping between set names and codes.
    #
    @staticmethod
    def coerceToName(setCodeOrName):
        setToCode = SetUtil.getSetToCode()

        # Set name return it
        if setCodeOrName in setToCode:
            return setCodeOrName

        # Set code; return the name
        if setCodeOrName in setToCode.values():
            codeToSet = {setCode: setName for setName, setCode in setToCode.items()}
            return codeToSet[setCodeOrName]

        raise Exception('Invalid set name or code: %s' % setCodeOrName)


    @staticmethod
    def downloadCards(setCode):
        setName = SetUtil.coerceToName(setCode)

        print('Getting cards for %s' % setName)
        sys.stdout.flush()

        cards = []

        baseURL = 'https://api.scryfall.com/cards/search?q='
        # query = urllib.quote_plus('set=%s' % setCode)
        query = urllib.parse.quote('set=%s' % setCode)

        finalURL = baseURL + query

        r = requests.get(finalURL)

        if (r.status_code != 200):
            print('Bad return status (' + str(r.status_code) + ' != 200)! Returning none.')
            print('URL: %s' % str(finalURL))
            return None

        response = json.loads(r.text)
        cards.extend(response['data'])

        nCards = response['total_cards']

        # Might be pagified
        while (response['has_more'] == True):
            print('\tGetting more cards for %s...' % setName)
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
