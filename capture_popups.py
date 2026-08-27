# スキルのボーナスノードとチェーンノードのポップアップを撮影する
# (共鳴者画面を開いた状態で実行。クリック座標は 2560x1440 クライアント基準)
import time
import cv2

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

    sx = si.width / 2560
    sy = si.height / 1440
    controller = WindowsInputController(si.monitor, si.originX, si.originY)
    ch = si.characters

    # スキルセクションへ → 列1のボーナスノード(下段)をクリック
    controller.leftClick(ch.leftSide.x, ch.leftSide.y + ch.offsets.leftSide.y * 3, 1.5)
    controller.leftClick(1015 * sx, 838 * sy, 1.5)
    grab(si, 'popup_skill_bonus1.png')
    # 列1のボーナスノード(上段)
    controller.leftClick(1015 * sx, 545 * sy, 1.5)
    grab(si, 'popup_skill_bonus2.png')
    controller.pressKey('esc', 1.0)

    # チェーンセクションへ → チェーンノード1(最上部)をクリック
    controller.leftClick(ch.leftSide.x, ch.leftSide.y + ch.offsets.leftSide.y * 4, 1.5)
    grab(si, 'chain_closed.png')
    controller.leftClick(2058 * sx, 384 * sy, 1.5)
    grab(si, 'popup_chain1.png')
    controller.pressKey('esc', 1.0)

    print(f'done ({si.width}x{si.height} origin=({si.originX},{si.originY}))')

if __name__ == '__main__':
    main()
