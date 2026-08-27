# 現在のゲーム画面を1枚キャプチャする(クリック操作なし)
# 実行のたびに fullshot_1.png, fullshot_2.png ... と連番で保存
import time
import cv2

from game.foreground import WindowManager
from scraping.utils.common import screenshot
from pathlib import Path

def main():
    wm = WindowManager()
    if not wm.window:
        print('game not found')
        return
    si = wm.getScreenInfo()
    wm.setForeground()
    time.sleep(1.0)

    n = 1
    while Path(f'fullshot_{n}.png').exists():
        n += 1
    img = screenshot(width=si.width, height=si.height, monitor=si.monitor,
                     originX=si.originX, originY=si.originY)
    cv2.imwrite(f'fullshot_{n}.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print(f'saved fullshot_{n}.png ({si.width}x{si.height} origin=({si.originX},{si.originY}))')

if __name__ == '__main__':
    main()
