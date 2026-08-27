# 実キャラの音骸装備スロットのポップアップを撮影する
import time
import cv2

from properties.config import cfg
from game.foreground import WindowManager
from scraping.utils.common import screenshot
from scraping.utils.mouse_keyboard import WindowsInputController

# 1080p基準・中央アンカーのスロット中心(暫定採寸値)
SLOTS = [(1460, 275), (1527, 495), (1517, 635), (1487, 775), (1415, 905)]

def grab(si, name):
    img = screenshot(width=si.width, height=si.height, monitor=si.monitor,
                     originX=si.originX, originY=si.originY)
    cv2.imwrite(name, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print(f'{name} saved')

def main():
    wm = WindowManager()
    si = wm.getScreenInfo()
    wm.setForeground()
    time.sleep(1.0)

    controller = WindowsInputController(si.monitor, si.originX, si.originY)
    ch = si.characters
    s = si.height / 1080

    controller.pressKey(cfg.get(cfg.resonatorKeybind), 3, False)
    # 2番目のアバター(実キャラ)を選択してから音骸セクションへ
    controller.leftClick(ch.rightSide.x, ch.rightSide.y + ch.offsets.rightSide.y, 1.2)
    controller.leftClick(ch.leftSide.x, ch.leftSide.y + ch.offsets.leftSide.y * 2, 1.5)
    grab(si, 'equip2_base.png')

    for i, (x1080, y1080) in enumerate(SLOTS[:3]):
        x = si.width / 2 + (x1080 - 960) * s
        y = y1080 * s
        controller.leftClick(x, y, 1.5)
        grab(si, f'equip2_echo{i}.png')

    controller.pressKey('esc', .8)
    controller.pressKey('esc', .5)
    print(f'done ({si.width}x{si.height})')

if __name__ == '__main__':
    main()
