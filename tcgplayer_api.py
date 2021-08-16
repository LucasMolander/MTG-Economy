import requests
import json
import time
import os

from file_util import FileUtil


class TCGPlayerAPI(object):
    KEYS_PATH = 'keys.json'
    KEY_NAME = 'tcgplayer'

    GET_BEARER_TOKEN_URL = 'https://api.tcgplayer.com/token'

    keyInfo = FileUtil.getJSONContents(KEYS_PATH)[KEY_NAME]
    USER_AGENT = keyInfo['user_agent_header']

    bearerToken = None

    @staticmethod
    def getMarketpriceURL(skuID: int):
        return f"https://api.tcgplayer.com/pricing/marketprices/{skuID}"

    @staticmethod
    def init():
        """
        Right now, this just gets the bearer token.
        """

        # Try getting the cached bearer token
        # TODO Factor this out into an abstract base class
        currTime = int(time.time())
        try:
            tokenFP = f"{FileUtil.TOKENS_FOLDER_PATH}{os.sep}{TCGPlayerAPI.KEY_NAME}.json"
            tokenInfo = FileUtil.getJSONContents(tokenFP)['bearer_token']
            tokenValue = tokenInfo['value']
            expireTime = tokenInfo['expires']
        except Exception as e:
            expireTime = currTime - 1

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
            print(f"Request ({r.status_code}):\n{r.text}")
            respJSON = json.loads(r.text)
            # TODO: Make this not clobber everything else in the file
            # It's fine for now because there's nothing else, though
            FileUtil.writeJSONContents(
                tokenFP,
                {
                    'bearer_token': {
                        'value': respJSON['access_token'],
                        'expires': respJSON['expires_in'] + currTime
                    }
                }
            )
            TCGPlayerAPI.bearerToken = respJSON['access_token']
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
        marketpriceURL = getMarketpriceURL(skuID)

        r = requests.request("GET", marketpriceURL, headers=TCGPlayerAPI.getRequestHeaders())
        response = json.loads(r.text)

        print(response)