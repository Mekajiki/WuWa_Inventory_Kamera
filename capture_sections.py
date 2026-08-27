# 共鳴者画面の各セクションを自動巡回してRAWスクリーンショットを保存する
# (3.6 UI の座標測定用。共鳴者画面を開いた状態で実行)
import time
import cv2

from game.foreground import WindowManager
from scraping.utils.common import screenshot
from scraping.utils.mouse_keyboard import WindowsInputController

def main():
    wm = WindowManager()
    si = wm.getScreenInfo()
    wm.setForeground()
    time.sleep(1.0)

    controller = WindowsInputController(si.monitor, si.originX, si.originY)
    ch = si.characters

    for section in range(5):
        controller.leftClick(ch.leftSide.x, ch.leftSide.y + ch.offsets.leftSide.y * section, 1.5)
        img = screenshot(width=si.width, height=si.height, monitor=si.monitor,
                         originX=si.originX, originY=si.originY)
        cv2.imwrite(f'section_{section}.png', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        print(f'section {section} saved')

    print(f'done ({si.width}x{si.height} origin=({si.originX},{si.originY}))')

if __name__ == '__main__':
    main()
