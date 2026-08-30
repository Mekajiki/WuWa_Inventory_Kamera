# QA v2: 音骸欠け・Lv0・コスト合計>12/不正値 の検査
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
names = json.load(open(r'C:\Users\air_d\Documents\wuwa\names.json', encoding='utf-8'))['characters']
issues = 0
for k, v in d.items():
    echoes = v.get('echoes', {})
    label = f"{names.get(k, k)}({k}) Lv{v['level']}"
    flags = []
    if v['level'] >= 60 and len(echoes) < 5:
        flags.append(f"echoes={len(echoes)}")
    zeroLv = [e['name'] for e in echoes.values() if e['level'] == 0]
    if v['level'] >= 90 and zeroLv:
        flags.append(f"Lv0: {','.join(zeroLv)}")
    costs = [e['cost'] for e in echoes.values()]
    bad = [c for c in costs if c not in (1, 3, 4)]
    if bad:
        flags.append(f"invalid cost: {bad}")
    # loadouts may total anything up to the 12-cost cap; only >12 is impossible
    if echoes and sum(costs) > 12:
        flags.append(f"cost sum {sum(costs)}>12")
    if flags:
        issues += 1
        print(f"{label}: " + ' | '.join(flags))
print(f"characters: {len(d)}, flagged: {issues}")
