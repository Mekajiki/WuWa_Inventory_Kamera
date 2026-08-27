# 音骸タブ: ソートメニューと育成済み音骸の詳細を撮影する
import time
import cv2

from properties.config import cfg
from game.foreground import WindowManager
from scraping.utils.common import screenshot
from scraping.utils.mouse_keyboard import WindowsInputController

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

    sx = si.width / 5120
    sy = si.height / 2160
    controller = WindowsInputController(si.monitor, si.originX, si.originY)

    controller.pressKey(cfg.get(cfg.inventoryKeybind), 2.5, False)
    controller.leftClick(si.scrapers.echoes.x, si.scrapers.echoes.y, 1.5)

    # ソートドロップダウン(獲得順)を開く
    controller.leftClick(886 * sx, 1976 * sy, 1.2)
    grab(si, 'bag_sort_options.png')
    controller.pressKey('esc', 1.0)

    # 昇順/降順トグルを押して古い(育成済みが多い)方から表示
    controller.leftClick(si.scrapers.echoes.x, si.scrapers.echoes.y, 1.5)
    controller.leftClick(1344 * sx, 1976 * sy, 1.5)
    start = si.echoes.start
    controller.leftClick(start.x + start.w / 2, start.y + start.h / 2, 1.2)
    grab(si, 'bag_echo_leveled.png')

    # トグルを元に戻す
    controller.leftClick(1344 * sx, 1976 * sy, 1.0)
    controller.pressKey('esc', .5)
    print(f'done ({si.width}x{si.height})')

if __name__ == '__main__':
    main()
