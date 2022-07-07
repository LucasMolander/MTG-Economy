import requests
import json
import time
import os

from typing import List, Optional

from file_util import FileUtil


# TODO @nocommit Make this a singleton because there is state associated with it
class TCGPlayerAPI(object):
  """
  General workflow for onboarding new sets:
    1. Get the product ID from the URL manually via the page in TCGPlayer
    2. getProductSKUIDs(<the product ID you got from step 1>)
    3. Put the SKU ID into sets.json
    4. Run `python main.py storeboxes --set=<new set code or name>`
  """
  KEYS_PATH = 'keys.json'
  KEY_NAME = 'tcgplayer'

  GET_BEARER_TOKEN_URL = 'https://api.tcgplayer.com/token'
  GET_SKU_IDS_URL = 'https://api.tcgplayer.com/catalog/skus/skuIds'

  keyInfo = FileUtil.getJSONContents(KEYS_PATH)[KEY_NAME]
  USER_AGENT: str = keyInfo['user_agent_header']

  bearerToken = None

  @staticmethod
  def getMarketpriceURL(skuID: int):
    return f"https://api.tcgplayer.com/pricing/marketprices/{skuID}"

  @staticmethod
  def getSKUsURL(productID: int):
    return f"https://api.tcgplayer.com/catalog/products/{productID}/skus"

  @staticmethod
  def init():
    """
    Right now, this just gets the bearer token.
    """

    # Try getting the cached bearer token
    # TODO Factor this out into an abstract base class
    tokenFP = f"{FileUtil.TOKENS_FOLDER_PATH}{os.sep}{TCGPlayerAPI.KEY_NAME}.json"
    currTime = int(time.time())
    try:
      # Bearer tokens last 2 weeks so this shouldn't happen too often
      tokenInfo = FileUtil.getJSONContents(tokenFP)['bearer_token']
      tokenValue = tokenInfo['value']
      expireTime = int(tokenInfo['expires'])
      if expireTime >= (currTime + 180):
        TCGPlayerAPI.bearerToken = tokenValue
        haveToken = True
      else:
        haveToken = False
    except Exception as e:
      print("Exception getting bearer token info:")
      print(e)
      haveToken = False
      expireTime = currTime - 1

    if haveToken:
      print('Using cached bearer token for %s' % TCGPlayerAPI.KEY_NAME)
    else:
      print('Getting new bearer token for %s' % TCGPlayerAPI.KEY_NAME)
      r = requests.post(
        TCGPlayerAPI.GET_BEARER_TOKEN_URL,
        data={
          'grant_type': 'client_credentials',
          'client_id': TCGPlayerAPI.keyInfo['public'],
          'client_secret': TCGPlayerAPI.keyInfo['private'],
        }
      )
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

  @staticmethod
  def getRequestHeaders():
    return {
      'Accept': 'application/json',
      'User-Agent': TCGPlayerAPI.USER_AGENT,
      'Authorization': 'bearer %s' % TCGPlayerAPI.bearerToken,
    }

  @staticmethod
  def getMarketPrice(skuID: int) -> Optional[float]:
    r = requests.request(
      "GET",
      TCGPlayerAPI.getMarketpriceURL(skuID),
      headers=TCGPlayerAPI.getRequestHeaders()
    )
    response = json.loads(r.text)

    if 'results' not in response:
      print(f"'results' not in response: {response}")
      return None
    res: List = response['results']
    if len(res) == 0:
      print(f"Response results was empty")
      return None
    theRes = res[0]
    if 'price' not in theRes:
      print(f"'price' not in the result: {theRes}")
      return None

    return round(float(theRes['price']), 2)

  @staticmethod
  def getProductSKUIDs(productID: int) -> List[int]:
    r = requests.request(
      "GET",
      TCGPlayerAPI.getSKUsURL(productID),
      headers=TCGPlayerAPI.getRequestHeaders()
    )
    response = json.loads(r.text)
    return [int(sku['skuId']) for sku in response['results']]

  @staticmethod
  def getSKUIDs():
    r = requests.request(
      "GET",
      TCGPlayerAPI.GET_SKU_IDS_URL,
      headers=TCGPlayerAPI.getRequestHeaders()
    )
    response = json.loads(r.text)
    print(response)
