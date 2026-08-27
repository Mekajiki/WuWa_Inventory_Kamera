# レアリティ色の実測: 詳細パネルの区切り線と、グリッドセルの背景色
import cv2
import numpy as np

from game.screenInfo import ScreenInfo

si = ScreenInfo(5120, 2160)

img = cv2.cvtColor(cv2.imread('bag_echoes.png'), cv2.COLOR_BGR2RGB)

r = si.echoes.rarityLine
for dy in (-10, 0, 10, 20):
    line = img[int(r.y + dy):int(r.y + dy + 6), int(r.x):int(r.x + r.w)]
    print(f'divider y+{dy}: {line.reshape(-1,3).mean(axis=0).astype(int)}')

# グリッドセルの下端グラデーション帯(ラベル行の少し上)を各セルでサンプル
grid = si.echoes.grid
for col in range(9):
    cx = int(grid.x + grid.w * col)
    cy = int(grid.y)          # ラベル中心の高さ
    band = img[cy - 60:cy - 30, cx - 120:cx + 40]
    print(f'row0 col{col}: {band.reshape(-1,3).mean(axis=0).astype(int)}')
