# 共鳴者画面の音骸装備セクションを採寸用に撮影する
# (ゲームがフィールド or 共鳴者画面の状態で実行)
import re
import time
import cv2

from properties.config import cfg
from game.foreground import WindowManager
from scraping.utils.common import screenshot, readTextBoxes
from scraping.utils.mouse_keyboard import WindowsInputController

def grab(si, name):
    img = screenshot(width=si.width, height=si.height, monitor=si.monitor,
                     originX=si.originX, originY=si.originY)
    cv2.imwrite(name, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print(f'{name} saved')
    return img

def main():
    wm = WindowManager()
    si = wm.getScreenInfo()
    wm.setForeground()
    time.sleep(1.0)

    controller = WindowsInputController(si.monitor, si.originX, si.originY)
    ch = si.characters

    controller.pressKey(cfg.get(cfg.resonatorKeybind), 3, False)
    controller.leftClick(ch.leftSide.x, ch.leftSide.y + ch.offsets.leftSide.y * 2, 1.5)
    img = grab(si, 'equip_base.png')

    # 右側の装備スロットを「+N」ラベルで検出してクリック
    h, w = img.shape[:2]
    x0 = int(w * 0.55)
    slots = []
    for bx0, by0, bx1, by1, text in readTextBoxes(img[:, x0:]):
        if re.fullmatch(r'\+\d+', text.strip()):
            slots.append((int((bx0 + bx1) / 2) + x0, int((by0 + by1) / 2)))
    slots.sort(key=lambda s: s[1])
    print(f'{len(slots)} slot labels: {slots}')

    for i, (sx, sy) in enumerate(slots[:3]):
        controller.leftClick(sx - 40, sy - 40, 1.5)
        grab(si, f'equip_echo{i}.png')

    # ステータス「・・・」展開ボタン(左パネル、1080p基準 (384,629) を高さスケール)
    s = si.height / 1080
    controller.leftClick(384 * s, 629 * s, 1.5)
    grab(si, 'equip_stats.png')

    controller.pressKey('esc', .8)
    controller.pressKey('esc', .5)
    print(f'done ({si.width}x{si.height})')

if __name__ == '__main__':
    main()
