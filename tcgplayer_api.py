import requests
import json
import time

from file_util import FileUtil


class TCGPlayerAPI(object):
    KEYS_PATH = 'keys.json'
    KEY_NAME = 'tcgplayer'

    GET_BEARER_TOKEN_URL = 'https://api.tcgplayer.com/token'
    GET_MARKETPRICE_URL = 'https://api.tcgplayer.com/pricing/marketprices/%d'

    keyInfo = FileUtil.getJSONContents(KEYS_PATH)[KEY_NAME]
    USER_AGENT = keyInfo['user_agent_header']

    bearerToken = None

    @staticmethod
    def init():
        """
        Right now, this just gets the bearer token.
        """

        # Try getting the cached bearer token
        # TODO Factor this out into an abstract base class
        tokenFP = "%s/%s.json" % (FileUtil.TOKENS_FOLDER_PATH, TCGPlayerAPI.KEY_NAME)
        tokenInfo = FileUtil.getJSONContents(tokenFP)['bearer_token']
        tokenValue = tokenInfo['value']
        expireTime = tokenInfo['expires']
        currTime = int(time.time())

        # Give ourselves 3 minutes of leeway for any given run
        if (currTime + 180) >= expireTime:
            print('Getting new bearer token for %s' % TCGPlayerAPI.KEY_NAME)
            r = requests.post(
                TCGPlayerAPI.GET_BEARER_TOKEN_URL,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': TCGPlayerAPI.keyInfo['public'],
                    'client_secret': TCGPlayerAPI.keyInfo['private'],
                }
            )
            response = json.loads(r.text)
            # TODO: Make this not clobber everything else in the file
            # It's fine for now because there's nothing else, though
            FileUtil.writeJSONContents(
                tokenFP,
                {
                    'bearer_token': {
                        'value': response['access_token'],
                        'expires': response['expires_in'] + currTime
                    }
                }
            )
            TCGPlayerAPI.bearerToken = response['access_token']
        else:
            print('Using cached bearer token for %s' % TCGPlayerAPI.KEY_NAME)
            TCGPlayerAPI.bearerToken = tokenValue

    @staticmethod
    def getRequestHeaders():
        return {
            'Accept': 'application/json',
            'User-Agent': TCGPlayerAPI.USER_AGENT,
            'Authorization': 'bearer %s' % TCGPlayerAPI.bearerToken,
        }

    @staticmethod
    def doStuff():
        skuID = 2999708
        url = TCGPlayerAPI.GET_MARKETPRICE_URL % skuID

        r = requests.request("GET", url, headers=TCGPlayerAPI.getRequestHeaders())
        response = json.loads(r.text)

        print(response)