# 既知コストの音骸で intensity 数値→コストの対応を実証する
import sys, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

req = urllib.request.Request('https://static.nanoka.cc/ww/3.6/echo.json',
                             headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())

known = {
    '闇鬣狼': 3, '燎原の炎騎': 4, '封庭の械囿': 3, 'クラトスクス': 3,
    'メカファルコン': 3, 'ビリリ': 1, 'サケルドス': 1, '狂信者の血肉': 1,
    'シギルム': 4, '千傀の重楼': 4, 'フシュシュ': 1, '巨岩の闘士': 3,
    'ナイトメア・トゲバラタケ': 3, '響き渡る共鳴・フルールドリス': 4,
    '霽息の獣尊': 3, '熄えぬ狩人': 1, 'グローモス': 3, '遊弋蝶': 1,
}
byName = {str(v.get('ja', '')): (k, v.get('intensity')) for k, v in data.items()}
mapping = {}
for name, cost in known.items():
    if name in byName:
        eid, intensity = byName[name]
        mapping.setdefault(intensity, set()).add(cost)
        print(f'{name}: intensity={intensity} cost={cost}')
print('mapping:', {k: sorted(v) for k, v in sorted(mapping.items())})
