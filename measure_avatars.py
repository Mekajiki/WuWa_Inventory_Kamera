# UWスクショの右側アバターリストの位置・間隔を実測する
import cv2

from scraping.utils.common import readTextBoxes

img = cv2.cvtColor(cv2.imread('section_0.png'), cv2.COLOR_BGR2RGB)
h, w = img.shape[:2]
x0 = int(w * 0.88)
strip = img[:, x0:]
for bx0, by0, bx1, by1, text in readTextBoxes(strip):
    print(f'({int(bx0) + x0},{int(by0)})-({int(bx1) + x0},{int(by1)}) {text!r}')
