# キャラリストのスクロール量校正: ホイールNノッチあたり何px動くか実測する
# (共鳴者画面を開いた状態で実行)
import time
import cv2
import numpy as np

from game.foreground import WindowManager
from scraping.utils.common import screenshot
from scraping.utils.mouse_keyboard import WindowsInputController

def grabList(si):
    img = screenshot(width=si.width, height=si.height, monitor=si.monitor,
                     originX=si.originX, originY=si.originY)
    # 右側アバターリストの帯 (1080p基準 x1780-1870, y250-1000 をスケール)
    sx, sy = si.width / 1920, si.height / 1080
    return img[int(250*sy):int(1000*sy), int(1780*sx):int(1870*sx)]

def shift(before, after):
    """after が before に対して何px下に(負なら上に)ずれたか"""
    bg = cv2.cvtColor(before, cv2.COLOR_RGB2GRAY)
    ag = cv2.cvtColor(after, cv2.COLOR_RGB2GRAY)
    tmpl = ag[200:-200, :]  # after の中央帯を before から探す
    res = cv2.matchTemplate(bg, tmpl, cv2.TM_CCOEFF_NORMED)
    _, maxVal, _, maxLoc = cv2.minMaxLoc(res)
    return 200 - maxLoc[1], maxVal

def main():
    wm = WindowManager()
    si = wm.getScreenInfo()
    wm.setForeground()
    time.sleep(1.0)

    controller = WindowsInputController(si.monitor, si.originX, si.originY)
    ch = si.characters
    controller.moveMouse(ch.rightSide.x, ch.rightSide.y, .3)

    before = grabList(si)
    for notches in (3, 6, 12):
        controller.mouseScroll(-notches, .4)
        time.sleep(1.2)
        after = grabList(si)
        px, conf = shift(before, after)
        print(f'after -{notches} more notches: total shift={px}px (conf={conf:.2f})')
        before = after

    print(f'scale: {si.width}x{si.height}, avatar pitch at this scale ≈ {int(134 * si.height / 1080)}px')

if __name__ == '__main__':
    main()
