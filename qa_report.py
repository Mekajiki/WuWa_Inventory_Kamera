# スキャン結果のQAレポート: 音骸欠け・Lv0音骸の洗い出し
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
for k, v in d.items():
    if v['level'] < 60:
        continue
    echoes = v.get('echoes', {})
    zeroLv = [f"slot{s}:{e['name']}" for s, e in echoes.items() if e['level'] == 0]
    flags = []
    if len(echoes) < 5:
        flags.append(f"echoes={len(echoes)} (slots: {sorted(echoes)})")
    if zeroLv:
        flags.append(f"Lv0: {', '.join(zeroLv)}")
    if flags:
        print(f"{k} (Lv{v['level']}): " + ' | '.join(flags))
