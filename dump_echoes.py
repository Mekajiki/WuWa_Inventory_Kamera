import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
total = 0
for k, v in d.items():
    echoes = v.get('echoes', {})
    if not echoes:
        continue
    total += len(echoes)
    rows = []
    for slot in sorted(echoes):
        e = echoes[slot]
        subs = ' '.join(f'{n}={x}' for n, x in e['stats']['sub'].items())
        rows.append(f"  slot{slot}: {e['name']} +{e['level']} c{e['cost']} [{e['sonata']}] main={e['stats']['main']} sub({subs})")
    print(f"{k}: {len(echoes)} echoes")
    print('\n'.join(rows))
print(f'total equipped echoes: {total}')
