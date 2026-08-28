# 育成計画セッション用の名前解決マップを Documents\wuwa に出力する
import sys, json
sys.stdout.reconfigure(encoding='utf-8')

chars = json.load(open('data/characters.json', encoding='utf-8'))
weapons = json.load(open('data/weapons.json', encoding='utf-8'))
echoes = json.load(open('data/echoes.json', encoding='utf-8'))

out = {
    'characters': {str(v): k for k, v in chars.items()},
    'weapons': {str(v['id']): v['name'] for v in weapons.values()},
    'echoes': {str(v): k for k, v in echoes.items()},
}
path = r'C:\Users\air_d\Documents\wuwa\names.json'
json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written', path)
for cid in ('1211', '1307', '1411', '1502', '1508'):
    print(cid, '=', out['characters'].get(cid, '?(DBに無し)'))
