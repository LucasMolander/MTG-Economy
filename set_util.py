import sys
from typing import Any, Dict, List, Optional
import urllib.parse
import requests
import json
import os
from sanitize_filename import sanitize

from file_util import FileUtil


class SetUtil(object):

  SETS_PATH = 'sets.json'
  MP_PATH   = 'masterpieces.json'

  CARDS_DIR = 'card_prices'

  MASTERPIECE_PROBABILITY = 1.0 / 144.0

  sets: Dict[str, Any]         = FileUtil.getJSONContents(SETS_PATH)
  masterpieces: Dict[str, Any] = FileUtil.getJSONContents(MP_PATH)


  @staticmethod
  def getSetToCode() -> Dict[str, str]:
    return {
      setName: SetUtil.sets[setName]['code']
      for setName in SetUtil.sets.keys()
    }


  #
  # Assumes that the set of all codes AND names are unique with each other.
  #
  @staticmethod
  def coerceToCode(setCodeOrName: str) -> str:
    setToCode = SetUtil.getSetToCode()

    # Set name; return the code
    if setCodeOrName in setToCode:
      return setToCode[setCodeOrName]

    # Set code; return it
    if setCodeOrName in setToCode.values():
      return setCodeOrName

    raise Exception(f"Invalid set name or code: {setCodeOrName}")


  #
  # Assumes that the set of all codes AND names are unique with each other.
  # Also assumes that there's a 1:1 mapping between set names and codes.
  #
  @staticmethod
  def coerceToName(setCodeOrName: str) -> str:
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
  def isCollectorsEd(setCodeOrName: str) -> bool:
    setName = SetUtil.coerceToName(setCodeOrName)
    setInfo = SetUtil.sets[setName]
    return setInfo['collectorEdInfo'] is not None


  @staticmethod
  def getMasterpieceNameToPriceForSet(
    mpCode: str,
    setNameOrCode: str,
  ) -> Dict[str, float]:
    mp = SetUtil.masterpieces[mpCode]
    setCode = SetUtil.coerceToCode(setNameOrCode)

    # Get all masterpiece cards
    allMPCards = SetUtil.loadFromFile(mp['name'])
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
      str(mpNameToCard[mpName]['name']): float(
        mpNameToCard[mpName]['prices']['usd_foil']
      )
      for mpName in mpSubsetNames
    }


  @staticmethod
  def downloadCards(
    setCode: Optional[str] = None,
    mpCode: Optional[str] = None,
  ) -> List[Dict[str, Any]]:
    setName: Optional[str] = None
    mpName: Optional[str] = None
    if setCode is not None:
      setName: Optional[str] = SetUtil.coerceToName(setCode)
      print('Getting cards for %s' % setName)
    elif mpCode is not None:
      mpName: Optional[str] = SetUtil.masterpieces[mpCode]['name']
      print('Getting %s cards' % mpName)
    else:
      raise Exception("Must have a non-null setCode or mpCode!")

    sys.stdout.flush()

    cards = []

    baseURL = 'https://api.scryfall.com/cards/search?q='
    if mpCode is not None:
      query = urllib.parse.quote(f"set={mpCode}")
    else:
      query = urllib.parse.quote(f"set={setCode} unique:prints")

    finalURL = baseURL + query

    r = requests.get(finalURL)

    if (r.status_code != 200):
      print('Bad return status (' + str(r.status_code) + ' != 200)! Returning none.')
      print('URL: %s' % str(finalURL))
      return []

    response = json.loads(r.text)
    cards.extend(response['data'])

    # Might be pagified
    while (response['has_more'] == True):
      if mpCode is not None:
        print(f"\tGetting more {mpName} cards...")
      else:
        print(f"\tGetting more cards for {setName}..")
      sys.stdout.flush()

      url = response['next_page']
      r = requests.get(url)

      if (r.status_code != 200):
        raise Exception(f"Bad status ({r.status_code} != 200)!")

      response = json.loads(r.text)
      cards.extend(response['data'])

    return cards


  @staticmethod
  def loadFromFile(setName: str) -> List[Dict[str, Any]]:
    return FileUtil.getJSONContents(
      f"{SetUtil.CARDS_DIR}{os.sep}{sanitize(setName)}"
    )

  @staticmethod
  def loadAllFromFiles() -> Dict[str, List[Dict[str, Any]]]:
    return {
      setName: FileUtil.getJSONContents(
        f"{SetUtil.CARDS_DIR}{os.sep}{sanitize(setName)}"
      )
      for setName in SetUtil.sets
    }


  @staticmethod
  def persist(setName: str, cards: List[Dict[str, Any]]) -> None:
    sanitizedSetName = sanitize(setName)
    filePath = f"{SetUtil.CARDS_DIR}{os.sep}{sanitizedSetName}"
    with open(filePath, 'w', encoding='utf-8') as f:
      f.write(json.dumps(cards))
