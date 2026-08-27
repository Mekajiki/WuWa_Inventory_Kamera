# PP-OCRv5 (rapidocr 3.x) と現行 PP-OCRv4 japan (rapidocr_onnxruntime 1.2.3) の比較
import glob
import sys
import cv2

sys.stdout.reconfigure(encoding='utf-8')

from rapidocr import RapidOCR as RapidOCR5
from rapidocr.utils.typings import OCRVersion, ModelType, LangDet, LangRec

print('loading PP-OCRv5 server models...')
ocr5 = RapidOCR5(params={
    'Det.ocr_version': OCRVersion.PPOCRV5, 'Det.model_type': ModelType.SERVER, 'Det.lang_type': LangDet.CH,
    'Rec.ocr_version': OCRVersion.PPOCRV5, 'Rec.model_type': ModelType.SERVER, 'Rec.lang_type': LangRec.CH,
    'Global.use_cls': False,
})

from scraping.utils.common import recognizeLine as recOld, imageToString as strOld

def rec5(img):
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    result = ocr5(img, use_det=False, use_cls=False)
    texts = getattr(result, 'txts', None)
    return (texts[0] if texts else ''), result

print('== 難読名前クロップ (rec単体) ==')
for f in sorted(glob.glob('logs/fail/name_*.png')):
    img = cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2RGB)
    old = recOld(img)
    new, _ = rec5(img)
    print(f'{f.split(chr(92))[-1]}: old={old!r} new={new!r}')

print('== デバイスROI (det+rec) ==')
img = cv2.cvtColor(cv2.imread('smoke_terminal_roi.png'), cv2.COLOR_BGR2RGB)
r = ocr5(img)
print('v5 full:', list(zip(r.txts or [], [round(float(s), 2) for s in (r.scores or [])])))
print('v4 full:', repr(strOld(img, '')))
