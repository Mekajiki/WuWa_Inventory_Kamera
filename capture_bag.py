# Bメニュー(バッグ)の各画面を撮影する — 音骸/武器/素材スキャンの3.6採寸用
# (ゲームがフィールドにいる状態で実行)
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

    controller = WindowsInputController(si.monitor, si.originX, si.originY)

    # バッグを開いて既定タブを撮影
    controller.pressKey(cfg.get(cfg.inventoryKeybind), 2.5, False)
    grab(si, 'bag_default.png')

    # 旧座標のカテゴリ位置を順にクリックして撮影(ズレていればスクショで分かる)
    sc = si.scrapers
    for name, pos in (('weapons', sc.weapons), ('echoes', sc.echoes),
                      ('devItems', sc.devItems), ('resources', sc.resources)):
        controller.leftClick(pos.x, pos.y, 1.5)
        grab(si, f'bag_{name}.png')

    # 音骸タブでグリッド先頭セル(旧座標)をクリックして詳細を撮影
    controller.leftClick(sc.echoes.x, sc.echoes.y, 1.5)
    start = si.echoes.start
    controller.leftClick(start.x + start.w / 2, start.y + start.h / 2, 1.2)
    grab(si, 'bag_echo_detail.png')

    controller.pressKey('esc', .5)
    print(f'done ({si.width}x{si.height} origin=({si.originX},{si.originY}))')

if __name__ == '__main__':
    main()
