# GUIなしでスキャンを実行するCLIランナー。
# ゲームを前面化し、ESCメニューが開いていなければ開いてからスキャンする。
import sys
import time

from game.menu import MainMenuController
from game.foreground import WindowManager
from scraping.utils.mouse_keyboard import WindowsInputController
from scraping.scraperExectuter import startScraper

def main() -> int:
    wm = WindowManager()
    if not wm.window:
        print('RESULT: game window not found')
        return 1

    wm.setForeground()
    time.sleep(.8)

    menu = MainMenuController()
    if not menu.isMenu():
        WindowsInputController.pressKey('esc', 1.5)
        if not menu.isMenu():
            print('RESULT: could not reach the ESC menu (close any open screens in-game)')
            return 1

    result = startScraper()
    print(f'RESULT: {result}')
    return 0 if result and result[0] == 'success' else 1

if __name__ == '__main__':
    sys.exit(main())
