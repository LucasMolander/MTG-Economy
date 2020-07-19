import sys
import urllib.parse
import requests
import json

from file_util import FileUtil


class SetUtil(object):

    SETS_PATH = 'sets.json'
    MP_PATH   = 'masterpieces.json'

    CARDS_DIR = 'card_prices'

    MASTERPIECE_PROBABILITY = 1.0 / 144.0

    sets         = FileUtil.getJSONContents(SETS_PATH)
    masterpieces = FileUtil.getJSONContents(MP_PATH)


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
    def getMasterpieceNameToPriceForSet(mpCode, setNameOrCode):
        mp = SetUtil.masterpieces[mpCode]
        setCode = SetUtil.coerceToCode(setNameOrCode)

        # Get all masterpiece cards
        allMPCards = SetUtil.loadFromFiles(only=mp['name'])
        mpNameToCard = {
            mpCard['name']: mpCard
            for mpCard in allMPCards
        }

        # Get the prices for the cards in the specific set
        mpSubsetNames = mp['setCodeToCards'][setCode]
        # return [
        #     float(mpNameToCard[mpName]['prices']['usd_foil'])
        #     for mpName in mpSubsetNames
        # ]
        return {
            mpNameToCard[mpName]['name']: float(mpNameToCard[mpName]['prices']['usd_foil'])
            for mpName in mpSubsetNames
        }



    @staticmethod
    def downloadCards(setCode, mpCode=None):
        if (not mpCode):
            setName = SetUtil.coerceToName(setCode)

        if (mpCode):
            mpName = SetUtil.masterpieces[mpCode]['name']
        else:
            mpName = None

        if (mpCode):
            print('Getting %s cards' % mpName)
        else:
            print('Getting cards for %s' % setName)
        sys.stdout.flush()

        cards = []

        baseURL = 'https://api.scryfall.com/cards/search?q='
        if (mpCode):
            query = urllib.parse.quote('set=%s' % mpCode)
        else:
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
            if (mpCode):
                print('\tGetting more %s cards...' % mpName)
            else:
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
    def loadFromFiles(only=None):
        if (only):
            return FileUtil.getJSONContents('%s/%s' % (SetUtil.CARDS_DIR, only))

        return {
            name: FileUtil.getJSONContents('%s/%s' % (SetUtil.CARDS_DIR, name))
            for name in SetUtil.sets
        }


    @staticmethod
    def persist(setName, cards):
        filePath = '%s/%s' % (SetUtil.CARDS_DIR, setName)
        with open(filePath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(cards))
