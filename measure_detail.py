# 音骸詳細パネル(右側)のテキスト位置を採寸する
import sys
import cv2

from scraping.utils.common import readTextBoxes

src = sys.argv[1] if len(sys.argv) > 1 else 'bag_echoes.png'
img = cv2.cvtColor(cv2.imread(src), cv2.COLOR_BGR2RGB)
h, w = img.shape[:2]
x0 = int(w * 0.72)
panel = img[:, x0:]
for bx0, by0, bx1, by1, text in readTextBoxes(panel):
    rx0, rx1 = int(bx0) + x0, int(bx1) + x0
    # 1080p右アンカー換算: x1080 = 1920 - (5120 - x)/2
    ax0, ax1 = 1920 - (5120 - rx0) // 2, 1920 - (5120 - rx1) // 2
    print(f'real({rx0},{int(by0)})-({rx1},{int(by1)}) 1080pR({ax0},{int(by0)//2})-({ax1},{int(by1)//2}) {text!r}')
