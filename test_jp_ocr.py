# 日本語OCRモデルの単体検証(ゲーム不要)
# 1. ModelScope から japan モデルをDL(config.py の _createOCR と同じ経路)
# 2. モデルに文字辞書が埋め込まれているか確認
# 3. PIL で「デバイス」等を描画した画像をOCRして読めるか確認
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from properties.config import ocr, basePATH

def renderText(text: str, size: int = 40) -> np.ndarray:
    font = ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc', size)
    img = Image.new('RGB', (size * len(text) + 60, size + 40), (40, 40, 40))
    draw = ImageDraw.Draw(img)
    draw.text((20, 15), text, font=font, fill=(230, 230, 230))
    return np.array(img)

def main():
    rec = ocr.text_recognizer
    print(f"model keys embedded: {rec.session.have_key()}")
    print(f"charset size: {len(rec.postprocess_op.character)}")
    kana = [c for c in ('デ', 'バ', 'イ', 'ス', 'あ', 'の') if c in rec.postprocess_op.character]
    print(f"kana in charset: {kana}")

    for text in ['デバイス', '端末', '漂泊者', 'クリティカル率 8.1%', 'Terminal']:
        result = ocr(renderText(text))[0]
        got = ' / '.join(r[1] for r in result) if result else '(nothing)'
        print(f"'{text}' -> '{got}'")

if __name__ == '__main__':
    main()
