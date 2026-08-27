# 実際のスクレイパー関数を保存済みスクリーンショットで end-to-end 検証
import cv2
import json
from collections import defaultdict

from game.screenInfo import ScreenInfo
from scraping.charactersScraper import scrapeResonator, scrapeWeapon, scrapeSkills, scrapeChain

si = ScreenInfo(2560, 1440)

def load(name):
    return cv2.cvtColor(cv2.imread(name), cv2.COLOR_BGR2RGB)

characters = defaultdict(lambda: defaultdict(int, {
    'level': 0, 'ascension': 0,
    'weapon': defaultdict(int, {'id': 0, 'level': 1, 'ascension': 0, 'rank': 0}),
    'echoes': dict(),
    'skills': defaultdict(int, {'normal': 1, 'resonance': 1, 'forte': 1, 'liberation': 1, 'intro': 1,
                                'stats0': 0, 'stats1': 0, 'inherent': 0, 'stats3': 0, 'stats4': 0}),
    'chain': 0
}))
_cache = dict()

resonatorID, isDouble = scrapeResonator(load('section_0.png'), si, characters, _cache)
print('resonatorID:', repr(resonatorID), 'isDouble:', isDouble)
scrapeWeapon(load('section_1.png'), si, characters, resonatorID, _cache)
scrapeSkills(load('section_3.png'), si, characters, resonatorID, _cache)
scrapeChain(load('section_4.png'), si, characters, resonatorID)

print(json.dumps({k: dict(v, weapon=dict(v['weapon']), skills=dict(v['skills'])) for k, v in characters.items()},
                 ensure_ascii=False, indent=1))
