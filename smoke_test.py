# フォーク改修のスモークテスト(ゲーム起動中に実行する)
# 1. ウィンドウ検出(鳴潮/Wuthering Waves どちらでも)
# 2. クライアント領域と原点の取得
# 3. ESCメニューの terminal ROI を切り出して PNG 保存 + OCR 結果表示
import cv2

from game.foreground import WindowManager
from scraping.utils.common import screenshot, imageToString, definedText
from properties.config import cfg, LANGUAGES

def main():
    wm = WindowManager()
    if not wm.window:
        print('NG: ゲームウィンドウが見つかりません')
        return

    print(f"OK: window found: title='{wm.window.title}'")
    width, height, originX, originY = wm.getClientArea()
    print(f"client area: {width}x{height} @ ({originX},{originY})")

    si = wm.getScreenInfo()
    print(f"screenInfo: {si.width}x{si.height} monitor={si.monitor} origin=({si.originX},{si.originY})")
    print(f"language: {cfg.get(cfg.gameLanguage)} -> {LANGUAGES.get(cfg.get(cfg.gameLanguage), 'en')}")
    print(f"terminal ROI: x={si.terminal.x} y={si.terminal.y} w={si.terminal.w} h={si.terminal.h}")

    wm.setForeground()
    import time; time.sleep(1.0)

    image = screenshot(si.terminal.x, si.terminal.y, si.terminal.w, si.terminal.h, si.monitor,
                       originX=si.originX, originY=si.originY)
    cv2.imwrite('smoke_terminal_roi.png', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    text = imageToString(image, '')
    print(f"OCR result: '{text}'")
    print(f"expected  : '{definedText['PrefabTextItem_1547656443_Text']}'")

if __name__ == '__main__':
    main()
