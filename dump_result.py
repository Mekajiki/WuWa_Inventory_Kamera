import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
print('characters:', len(d))
for k, v in d.items():
    w = v['weapon']
    s = v['skills']
    print(f"{k}: Lv{v['level']}/asc{v['ascension']} chain{v['chain']} weapon={w['id']} Lv{w['level']} R{w['rank']} "
          f"skills={s['normal']}/{s['resonance']}/{s['forte']}/{s['liberation']}/{s['intro']}")
