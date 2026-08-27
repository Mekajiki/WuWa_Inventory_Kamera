# 音骸詳細リーダーのオフライン検証(保存済みバッグ撮影に対して)
import sys
import cv2

from game.screenInfo import ScreenInfo
from scraping.echoesScraper import (
    cropROI, matchEchoName, readRarity, readStats, readLevel, gridColumns
)
from scraping.utils.common import recognizeLine

si = ScreenInfo(5120, 2160)

def check(name):
    img = cv2.cvtColor(cv2.imread(name), cv2.COLOR_BGR2RGB)
    raw = recognizeLine(cropROI(img, si.echoes.name))
    print(f'== {name} ==')
    print('name:', repr(raw), '->', repr(matchEchoName(raw)))
    print('level:', readLevel(img, si))
    print('cost:', repr(recognizeLine(cropROI(img, si.echoes.cost))))
    print('rarity:', readRarity(img, si))
    print('stats:', readStats(img, si))

print('grid columns @UW:', gridColumns(si))
print('grid columns @16:9:', gridColumns(ScreenInfo(2560, 1440)))
check('bag_echoes.png')
check('bag_echo_leveled.png')
