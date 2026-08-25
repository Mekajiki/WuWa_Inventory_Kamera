import re
import cv2
import time
import string
import logging
import numpy as np
from difflib import SequenceMatcher, get_close_matches as getMatches
from collections import defaultdict

from scraping.utils import charactersID, weaponsID, definedText
from scraping.utils import (
    screenshot, convertToBlackWhite, imageToString,
    readTextBoxes, WindowsInputController
)
from game.screenInfo import ScreenInfo
from properties.config import cfg

logger = logging.getLogger('CharacterScraper')

# Constants
SKILL_LEGENDS = {
    0: 'normal',
    1: 'resonance',
    2: 'forte',
    3: 'liberation',
    4: 'intro'
}
ASCENSION_LEVELS = [20, 40, 50, 60, 70, 80, 90]

def splitLevel(text: str) -> list[str]:
    """Split an OCR'd "level/cap" string; the slash is often lost, in which
    case the last two digits are the (always two-digit) ascension cap."""
    text = text.strip()
    if '/' in text:
        return text.split('/')
    if len(text) > 2:
        return [text[:-2], text[-2:]]
    return [text]

def scrapeResonator(image: np.ndarray, screenInfo: ScreenInfo, characters: dict, _cache: dict) -> tuple[str, bool]:
    resonatorNameImage = image[screenInfo.characters.resonatorName.y:screenInfo.characters.resonatorName.y + screenInfo.characters.resonatorName.h, screenInfo.characters.resonatorName.x:screenInfo.characters.resonatorName.x + screenInfo.characters.resonatorName.w]
    resonatorNameImage = convertToBlackWhite(resonatorNameImage)
    resonatorNameHash = hash(resonatorNameImage.tobytes())

    if resonatorNameHash in _cache:
        return None, True
    else:
        resonatorName = imageToString(resonatorNameImage, '', bannedChars=' ').lower()
    
        result = getMatches(resonatorName, charactersID, 1, 0.9) or getMatches(resonatorName, charactersID, 1, 0.7)
        if result:
            resonatorName = result[0]
        else:
            logger.debug(f'Unmatched resonator name: {resonatorName!r}')
        
        roverName = cfg.get(cfg.roverName).replace(' ', '').lower()
        # OCR sometimes drops a trailing kana, so match the Rover name fuzzily
        isRover = resonatorName == roverName or SequenceMatcher(None, resonatorName, roverName).ratio() >= .7
        resonatorID = '1502' if isRover else charactersID.get(resonatorName, resonatorName)
        _cache[resonatorNameHash] = resonatorID

    if resonatorID in characters:
        return resonatorID, True

    # keep the level crop in color: the gray "/90" cap is lost by binarization
    levelImage = image[screenInfo.characters.resonatorLevel.y:screenInfo.characters.resonatorLevel.y + screenInfo.characters.resonatorLevel.h, screenInfo.characters.resonatorLevel.x:screenInfo.characters.resonatorLevel.x + screenInfo.characters.resonatorLevel.w]
    levelHash = hash(levelImage.tobytes())

    if levelHash in _cache:
        level = _cache[levelHash]
    else:
        level = splitLevel(imageToString(levelImage, '', allowedChars=string.digits + '/'))
        _cache[levelHash] = level

    try: ascensionLvl = ASCENSION_LEVELS.index(int(level[1]))
    except: ascensionLvl = 0

    try: characterLvl = int(level[0])
    except: characterLvl = 1

    characters[resonatorID]['level'] = characterLvl
    characters[resonatorID]['ascension'] = ascensionLvl

    return resonatorID, False

def scrapeWeapon(image: np.ndarray, screenInfo: ScreenInfo, characters: dict, resonatorID: str, _cache: dict):
    weaponNameImage = image[screenInfo.characters.weaponName.y:screenInfo.characters.weaponName.y + screenInfo.characters.weaponName.h, screenInfo.characters.weaponName.x:screenInfo.characters.weaponName.x + screenInfo.characters.weaponName.w]
    weaponNameImage = convertToBlackWhite(weaponNameImage)
    weaponNameHash = hash(weaponNameImage.tobytes())

    if weaponNameHash in _cache:
        weaponID = _cache[weaponNameHash]
    else:
        weaponName = imageToString(weaponNameImage, '', bannedChars=' ').lower()
    
        result = (getMatches(weaponName, weaponsID, 1, 0.9)
                  or getMatches(weaponName, weaponsID, 1, 0.75)
                  or getMatches(weaponName, weaponsID, 1, 0.6))
        if result:
            weaponName = result[0]
        else:
            logger.debug(f'Unmatched weapon name: {weaponName!r}')

        weaponID = weaponsID.get(weaponName, {'id': weaponName})['id']
        _cache[weaponNameHash] = weaponID
    
    # keep the level crop in color: the gray "/90" cap is lost by binarization
    levelImage = image[screenInfo.characters.weaponLevel.y:screenInfo.characters.weaponLevel.y + screenInfo.characters.weaponLevel.h, screenInfo.characters.weaponLevel.x:screenInfo.characters.weaponLevel.x + screenInfo.characters.weaponLevel.w]
    levelHash = hash(levelImage.tobytes())
    
    if levelHash in _cache:
        level = _cache[levelHash]
    else:
        level = splitLevel(imageToString(levelImage, '', allowedChars=string.digits + '/'))
        _cache[levelHash] = level

    rankImage = image[screenInfo.characters.weaponRank.y:screenInfo.characters.weaponRank.y + screenInfo.characters.weaponRank.h, screenInfo.characters.weaponRank.x:screenInfo.characters.weaponRank.x + screenInfo.characters.weaponRank.w]
    rankImage = convertToBlackWhite(rankImage)
    rankHash = hash(rankImage.tobytes())

    if rankHash in _cache:
        rank = _cache[rankHash]
    else:
        rank = imageToString(rankImage, '', allowedChars=string.digits)
        _cache[rankHash] = rank

    try:
        rankValue = int(rank)
        if rankValue > 5:
            # OCR sometimes appends stray digits from the description below
            rankValue = int(rank[0])

        characters[resonatorID]['weapon']['id'] = weaponID
        characters[resonatorID]['weapon']['level'] = int(level[0])
        characters[resonatorID]['weapon']['ascension'] = ASCENSION_LEVELS.index(int(level[1]))
        characters[resonatorID]['weapon']['rank'] = min(5, max(0, rankValue))
    except:
        logger.debug('Failed scraping the weapon')

def scrapeSkills(image: np.ndarray, screenInfo: ScreenInfo, characters: dict, resonatorID: str, _cache: dict):
    # Since 3.6 the skill screen shows every level directly on the tree
    # ("Lv.X/10" under each node), so no clicking is needed. OCR one band
    # containing all five labels and assign each to the nearest column —
    # cropping the labels individually makes the OCR much less reliable.
    strip = screenInfo.characters.skillStrip
    stripImage = image[strip.y:strip.y + strip.h, strip.x:strip.x + strip.w]
    stripHash = hash(stripImage.tobytes())

    if stripHash in _cache:
        levels = _cache[stripHash]
    else:
        columns = [column.x for column in screenInfo.characters.skillColumns]
        levels = {}
        for x0, y0, x1, y1, text in readTextBoxes(stripImage):
            found = re.search(r'(\d+)\s*/\s*10', text)
            if not found:
                continue
            xCenter = strip.x + (x0 + x1) / 2
            index = min(range(len(columns)), key=lambda i: abs(columns[i] - xCenter))
            levels[index] = int(found.group(1))
        _cache[stripHash] = levels

    for index in range(5):
        if index not in levels:
            logger.debug(f'Failed scraping skill level for column {index}')
        characters[resonatorID]['skills'][SKILL_LEGENDS[index]] = levels.get(index, 1)

def scrapeChain(image: np.ndarray, screenInfo: ScreenInfo, characters: dict, resonatorID: str):
    # Activated chain nodes glow cyan on the 3.6 chain screen; classify each
    # node by the amount of saturated cyan around its center.
    for position in screenInfo.characters.chainPositions:
        x, y = int(position.x), int(position.y)
        patch = image[max(0, y - 14):y + 14, max(0, x - 14):x + 14]
        hsv = cv2.cvtColor(patch, cv2.COLOR_RGB2HSV)
        glow = cv2.inRange(hsv, (75, 60, 140), (115, 255, 255)).mean()
        logger.debug(f'Chain node at ({x},{y}): glow={glow:.1f}')

        if glow < 8:
            break

        characters[resonatorID]['chain'] += 1

def resonatorScraper(controller: WindowsInputController, screenInfo: ScreenInfo):
    characters = defaultdict(
        lambda: defaultdict(
            int,
            {
                'level': 0,
                'ascension': 0,
                'weapon': defaultdict(
                    int,
                    {
                        'id': 0,
                        'level': 1,
                        'ascension': 0,
                        'rank': 0
                    }
                ),
                'echoes': dict(),
                'skills': defaultdict(
                    int,
                    {
                        'normal': 1,
                        'resonance': 1,
                        'forte': 1,
                        'liberation': 1,
                        'intro': 1,
                        'stats0': 0,
                        'stats1': 0,
                        'inherent': 0,
                        'stats3': 0,
                        'stats4': 0
                    }
                ),
                'chain': 0
            }
        )
    )
    _cache = dict()

    controller.pressKey(cfg.get(cfg.resonatorKeybind), 2, False)

    isDouble = False
    xLeftSide, yLeftSide = screenInfo.characters.leftSide.x, screenInfo.characters.leftSide.y
    xRightSide, yRightSide = screenInfo.characters.rightSide.x, screenInfo.characters.rightSide.y

    while not isDouble:
        for resonatorIndex in range(6):
            controller.leftClick(xRightSide, yRightSide + (screenInfo.characters.offsets.rightSide.y * resonatorIndex), .7)
            resonatorID = str()

            for section in range(5):
                # the chain screen (section 4) plays a slide-in animation
                controller.leftClick(xLeftSide, yLeftSide + (screenInfo.characters.offsets.leftSide.y * section), 1.5 if section == 4 else .8)

                image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor, originX=screenInfo.originX, originY=screenInfo.originY)

                match(section):
                    case 0:
                        resonatorID, isDouble = scrapeResonator(image, screenInfo, characters, _cache)
                        if isDouble:
                            break
                    case 1:
                        scrapeWeapon(image, screenInfo, characters, resonatorID, _cache)
                    case 2:
                        pass  # Skip echoes for now
                    case 3:
                        scrapeSkills(image, screenInfo, characters, resonatorID, _cache)
                    case 4:
                        scrapeChain(image, screenInfo, characters, resonatorID)
                time.sleep(.5)

            if isDouble:
                break

        if isDouble:
            break

        controller.moveMouse(xRightSide, yRightSide, .3)
        controller.mouseScroll(screenInfo.scroll.characters.y, .5)
    
    # Process last page
    for resonatorIndex in range(5, -1, -1):
        controller.leftClick(xRightSide, yRightSide + (screenInfo.characters.offsets.rightSide.y * resonatorIndex), .7)
        resonatorID = str()

        for section in range(5):
            controller.leftClick(xLeftSide, yLeftSide + (screenInfo.characters.offsets.leftSide.y * section), .8)

            image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor, originX=screenInfo.originX, originY=screenInfo.originY)

            match(section):
                case 0:
                    resonatorID, isDouble = scrapeResonator(image, screenInfo, characters, _cache)
                    del _cache
                    return dict(characters)
                case 1:
                    scrapeWeapon(image, screenInfo, characters, resonatorID, _cache)
                case 2:
                    pass  # Skip echoes for now
                case 3:
                    scrapeSkills(image, screenInfo, characters, resonatorID, _cache)
                case 4:
                    scrapeChain(image, screenInfo, characters, resonatorID)

            time.sleep(.5)
        
        if isDouble:
            break
    
    del _cache
    return dict(characters)
