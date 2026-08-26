import re
import cv2
import time
import string
import logging
import numpy as np
from pathlib import Path
from difflib import SequenceMatcher, get_close_matches as getMatches
from collections import defaultdict

from scraping.utils import charactersID, weaponsID, definedText
from scraping.utils import (
    screenshot, convertToBlackWhite, imageToString,
    readTextBoxes, recognizeLine, WindowsInputController
)
from scraping.utils.common import loadFile

# user-editable corrections for stubborn OCR misreads (e.g. 秧秧 read as 秋秋)
nameAliases: dict = loadFile('./nameAliases.json')
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

def matchName(name: str, candidates, cutoffs=(0.9, 0.7)) -> str | None:
    """Resolve an OCR'd name against known names: alias table, exact match,
    fuzzy match, then unique-substring containment (OCR often drops chars)."""
    name = name.replace('-', 'ー')
    if name in nameAliases:
        return nameAliases[name]
    if name in candidates:
        return name
    for cutoff in cutoffs:
        result = getMatches(name, candidates, 1, cutoff)
        if result:
            return result[0]
    if len(name) >= 2:
        containing = [candidate for candidate in candidates if name in candidate]
        if len(containing) == 1:
            return containing[0]
    return None

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
        resonatorName = recognizeLine(resonatorNameImage).replace(' ', '').lower()
        if not resonatorName:
            # keep the crop so unreadable names can be diagnosed
            try:
                Path('logs/fail').mkdir(parents=True, exist_ok=True)
                cv2.imwrite(f'logs/fail/name_{abs(resonatorNameHash)}.png', resonatorNameImage)
            except Exception:
                pass
    
        result = matchName(resonatorName, charactersID)
        if result:
            resonatorName = result
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
        level = splitLevel(re.sub(r'[^0-9/]', '', recognizeLine(levelImage)))
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
        weaponName = recognizeLine(weaponNameImage).replace(' ', '').lower()
    
        result = matchName(weaponName, weaponsID, cutoffs=(0.9, 0.75, 0.6))
        if result:
            weaponName = result
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
        level = splitLevel(re.sub(r'[^0-9/]', '', recognizeLine(levelImage)))
        _cache[levelHash] = level

    rankImage = image[screenInfo.characters.weaponRank.y:screenInfo.characters.weaponRank.y + screenInfo.characters.weaponRank.h, screenInfo.characters.weaponRank.x:screenInfo.characters.weaponRank.x + screenInfo.characters.weaponRank.w]
    rankImage = convertToBlackWhite(rankImage)
    rankHash = hash(rankImage.tobytes())

    if rankHash in _cache:
        rank = _cache[rankHash]
    else:
        rank = re.sub(r'[^0-9]', '', recognizeLine(rankImage))
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

    # give the resonator screen time to finish its opening animation, or the
    # first character's sections are captured before they render
    controller.pressKey(cfg.get(cfg.resonatorKeybind), 3, False)

    xLeftSide, yLeftSide = screenInfo.characters.leftSide.x, screenInfo.characters.leftSide.y
    xRightSide, yRightSide = screenInfo.characters.rightSide.x, screenInfo.characters.rightSide.y

    # The list scrolls by less than one page per pass so consecutive passes
    # overlap; already-scanned resonators are skipped after reading their
    # name, and the scan ends once a full pass finds nothing new. This keeps
    # the scan correct even when the scroll distance is imprecise.
    emptyPasses = 0
    for _ in range(40):
        newCount = 0

        for resonatorIndex in range(6):
            controller.leftClick(xRightSide, yRightSide + (screenInfo.characters.offsets.rightSide.y * resonatorIndex), .7)
            resonatorID = str()

            for section in range(5):
                # the chain screen (section 4) plays a slide-in animation
                controller.leftClick(xLeftSide, yLeftSide + (screenInfo.characters.offsets.leftSide.y * section), 1.5 if section == 4 else .8)

                image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor, originX=screenInfo.originX, originY=screenInfo.originY)

                match(section):
                    case 0:
                        resonatorID, alreadyScanned = scrapeResonator(image, screenInfo, characters, _cache)
                        if resonatorID == '' and not alreadyScanned:
                            # likely captured mid-transition; retry once
                            time.sleep(.6)
                            image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor, originX=screenInfo.originX, originY=screenInfo.originY)
                            resonatorID, alreadyScanned = scrapeResonator(image, screenInfo, characters, _cache)
                        if alreadyScanned:
                            break
                        newCount += 1
                    case 1:
                        scrapeWeapon(image, screenInfo, characters, resonatorID, _cache)
                    case 2:
                        pass  # Skip echoes for now
                    case 3:
                        scrapeSkills(image, screenInfo, characters, resonatorID, _cache)
                    case 4:
                        scrapeChain(image, screenInfo, characters, resonatorID)
                time.sleep(.5)

        if newCount == 0:
            # a scroll occasionally fails to move the list, making a pass all
            # duplicates; only stop after two empty passes in a row
            emptyPasses += 1
            if emptyPasses >= 2:
                break
        else:
            emptyPasses = 0

        controller.moveMouse(xRightSide, yRightSide, .3)
        controller.mouseScroll(screenInfo.scroll.characters.y, 1.2)

    del _cache
    return dict(characters)
