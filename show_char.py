import sys, json
sys.stdout.reconfigure(encoding='utf-8')
chars = json.load(open('data/characters.json', encoding='utf-8'))
name = sys.argv[1]
cid = str(chars.get(name))
d = json.load(open(sys.argv[2], encoding='utf-8'))
v = d.get(cid, {})
print(f'{name} id={cid} Lv{v.get("level")} chain{v.get("chain")} echoes={len(v.get("echoes", {}))}')
for s in sorted(v.get('echoes', {})):
    e = v['echoes'][s]
    print(f' slot{s}: {e["name"]} +{e["level"]} c{e["cost"]} [{e["sonata"]}] main={e["stats"]["main"]} sub={e["stats"]["sub"]}')
