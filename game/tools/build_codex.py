# Собирает кодекс «Быт» игры из карточек исторической базы material-culture/items/*.yaml.
# python3 build_codex.py <папка material-culture> <codex.json игры> <папка для картинок веб-версии>
# Предметы сцены (hs_*) -> карточки базы (первая — основная, остальные — «см. также»). Черновики игры остаются там,
# где карточки нет. Изображения — только свободные (лицензия и автор показываются в карточке).
import json, sys, os, glob
import yaml
from PIL import Image

MC, CODEX, IMG_OUT = sys.argv[1], sys.argv[2], sys.argv[3]
MAP = {
    'hs_tulasi': ['mc-tulasi-mancha', 'mc-tulasi-in-worship'], 'hs_alpana': ['mc-alpana'], 'hs_diya': ['mc-clay-lamp'],
    'hs_handi': ['mc-handi'], 'hs_brass': ['mc-metal-ware'], 'hs_kitchen': ['mc-rannaghar'], 'hs_woodpile': ['mc-fuel'],
    'hs_chala': ['mc-chala-hut', 'mc-courtyard'], 'hs_dung': ['mc-cowdung-plaster', 'mc-fuel'], 'hs_pond': ['mc-pond-and-ghat'],
    'hs_sari': ['mc-sari'], 'hs_banana': ['mc-banana-tree', 'mc-banana-leaf-plate'], 'hs_bananas': ['mc-fruits-offering'],
    'hs_palm': ['mc-coconut-palm'], 'hs_bamboo': ['mc-bamboo'], 'hs_shed': ['mc-cowshed'], 'hs_stool': ['mc-guest-reception', 'mc-pidi-mat'],
    # интерьеры
    'hs_chula_in': ['mc-chula'], 'hs_leaf': ['mc-banana-leaf-plate', 'mc-leaf-cups'], 'hs_offer': ['mc-cooking-for-vishnu'],
    'hs_kalasi': ['mc-water-jar'], 'hs_shilnora': ['mc-shil-nora'], 'hs_kula': ['mc-kula'], 'hs_ricebasket': ['mc-rice-dal'],
    'hs_altar': ['mc-thakur-ghar', 'mc-shodasha-upachara'], 'hs_conch': ['mc-conch-and-bells'], 'hs_bed': ['mc-bed-cradle'],
    'hs_chest': ['mc-grain-baskets-chests'], 'hs_gdoor': ['mc-doors-bolts'],
}
RUB = {'home': 'Быт · дом', 'kitchen': 'Быт · кухня', 'dress': 'Быт · одежда', 'rites': 'Быт · обряды', 'town': 'Быт · город',
       'music': 'Быт · музыка', 'nature': 'Быт · природа', 'puri': 'Быт · Пури', 'travel': 'Быт · дорога'}
EV = {'epoch': 'Засвидетельствовано в источниках эпохи', 'hagiography': 'Известно из житий',
      'later-reconstruction': 'Реконструкция по более поздним данным'}

cards = {}
for f in sorted(glob.glob(os.path.join(MC, 'items', '*.yaml'))):
    for x in yaml.safe_load(open(f)) or []:
        cards[x['id']] = x
codex = json.load(open(CODEX))
items = codex['items']
os.makedirs(IMG_OUT, exist_ok=True)
used = []
for hs, ids in MAP.items():
    ids = [i for i in ids if i in cards]
    if not ids:
        continue
    c = cards[ids[0]]
    e = items.get(hs, {})
    e['title'] = c['title']['ru']
    e['kind'] = RUB.get(c.get('rubric'), 'Быт')
    e['text'] = c['text']['ru'].strip()
    e['evidence'] = EV.get(c.get('era_evidence'), '') + ('. ' + c['evidence_note']['ru'].strip() if c.get('evidence_note') else '')
    e['refs'] = c.get('hagiography', [])
    e['sources'] = c.get('sources', [])
    e['card'] = c['id']
    e['also'] = [{'title': cards[i]['title']['ru'], 'text': cards[i]['text']['ru'].strip(), 'refs': cards[i].get('hagiography', [])} for i in ids[1:]]
    e['status'] = 'ok'
    e.pop('divya', None) if False else None
    img = next((im for i in ids for im in (cards[i].get('images') or []) if im.get('file')), None)
    if img:
        src = os.path.join(os.path.dirname(MC), img['file'])
        if os.path.exists(src):
            name = os.path.splitext(os.path.basename(src))[0] + '.jpg'
            out = os.path.join(IMG_OUT, name)
            if not os.path.exists(out):
                im = Image.open(src).convert('RGB'); im.thumbnail((560, 560), Image.LANCZOS); im.save(out, quality=84)
            e['photo'] = {'file': name, 'license': img.get('license', ''), 'author': img.get('author', ''), 'url': img.get('url', ''),
                          'caption': img.get('caption', img.get('title', ''))}
    items[hs] = e
    used.append((hs, c['id']))
codex['_note'] = ('Кодекс «Быт» собран из исторической базы material-culture (game/tools/build_codex.py); '
                  'карточки без пометки status=draft — проверенные базой.')
json.dump(codex, open(CODEX, 'w'), ensure_ascii=False, indent=1)
print('cards used:', len(used))
for u in used: print(' ', *u)
