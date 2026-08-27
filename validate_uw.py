# ウルトラワイド投影ROIの検証(fullshot_1=ESCメニュー, fullshot_2=ステータス画面)
import cv2
import string

from game.screenInfo import ScreenInfo
from scraping.utils.common import imageToString, recognizeLine

si = ScreenInfo(5120, 2160)
ch = si.characters

def load(name):
    return cv2.cvtColor(cv2.imread(name), cv2.COLOR_BGR2RGB)

def crop(img, roi):
    return img[roi.y:roi.y + roi.h, roi.x:roi.x + roi.w]

m = load('fullshot_1.png')
print('terminal ROI:', (si.terminal.x, si.terminal.y, si.terminal.w, si.terminal.h))
print('terminal OCR:', repr(imageToString(crop(m, si.terminal), '')))

s = load('fullshot_2.png')
print('name ROI:', (ch.resonatorName.x, ch.resonatorName.y, ch.resonatorName.w, ch.resonatorName.h))
print('name OCR:', repr(recognizeLine(crop(s, ch.resonatorName))))
print('level OCR:', repr(imageToString(crop(s, ch.resonatorLevel), '', allowedChars=string.digits + '/')))
print('rightSide click:', (int(ch.rightSide.x), int(ch.rightSide.y)), 'offset', int(ch.offsets.rightSide.y))
print('leftSide click:', (int(ch.leftSide.x), int(ch.leftSide.y)), 'offset', int(ch.offsets.leftSide.y))
print('chain0:', (int(ch.chainPositions[0].x), int(ch.chainPositions[0].y)))
print('skill strip:', (ch.skillStrip.x, ch.skillStrip.y, ch.skillStrip.w, ch.skillStrip.h))
