# バッググリッドのセル位置を「+N」ラベルOCRから動的検出する検証
import re
import sys
import cv2

from scraping.utils.common import readTextBoxes

src = sys.argv[1] if len(sys.argv) > 1 else 'bag_echo_leveled.png'
img = cv2.cvtColor(cv2.imread(src), cv2.COLOR_BGR2RGB)
h, w = img.shape[:2]
grid = img[:, :int(w * 0.72)]

cells = []
for x0, y0, x1, y1, text in readTextBoxes(grid):
    if re.fullmatch(r'\+\d+', text.strip()):
        cells.append((int((x0 + x1) / 2), int((y0 + y1) / 2), text.strip()))

cells.sort(key=lambda c: (round(c[1] / 80), c[0]))
print(f'{len(cells)} cells found ({w}x{h})')
for cx, cy, t in cells:
    print(f'  ({cx},{cy}) {t}')
