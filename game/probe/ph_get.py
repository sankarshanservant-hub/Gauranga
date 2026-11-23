# download Poly Haven assets: python3 ph_get.py <outdir> tex:id ... mod:id ... hdri:id
import json, os, sys, urllib.request
opener=urllib.request.build_opener(); opener.addheaders=[('User-Agent','asset-fetch/1.0')]; urllib.request.install_opener(opener)
out = sys.argv[1]
def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0: return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    urllib.request.urlretrieve(url, path)
for spec in sys.argv[2:]:
    kind, aid = spec.split(':')
    files = json.load(urllib.request.urlopen(f'https://api.polyhaven.com/files/{aid}'))
    d = os.path.join(out, aid)
    try:
        if kind == 'tex':
            for m, key in [('Diffuse','diff'),('nor_gl','nor'),('Rough','rough'),('Displacement','disp')]:
                if m in files:
                    f = files[m]['2k']['jpg'] if 'jpg' in files[m]['2k'] else files[m]['2k']['png']
                    get(f['url'], os.path.join(d, key + os.path.splitext(f['url'])[1]))
        elif kind == 'mod':
            g = files['gltf']['1k']['gltf']
            get(g['url'], os.path.join(d, aid + '.gltf'))
            for rel, f in g['include'].items():
                get(f['url'], os.path.join(d, rel))
        elif kind == 'hdri':
            get(files['hdri']['2k']['exr']['url'], os.path.join(d, aid + '.exr'))
        print('ok', spec)
    except Exception as e:
        print('FAIL', spec, e)

# Ассеты пробной сцены:
# python3 ph_get.py assets tex:reed_roof_04 tex:patterned_clay_plaster tex:clay_floor_001 tex:brown_mud_dry \
#   tex:forest_leaves_02 tex:bark_brown_02 tex:bamboo_wall tex:leafy_grass tex:bark_willow tex:mud_forest \
#   tex:dirt_floor tex:clay_plaster hdri:qwantani_moonrise hdri:qwantani_dusk_2 mod:tree_small_02 \
#   mod:island_tree_01 mod:island_tree_02 mod:shrub_04 mod:pachira_aquatica_01 mod:calathea_orbifolia_01 \
#   mod:brass_diya_lantern mod:ceramic_pot mod:planter_pot_clay mod:wicker_basket_01 mod:brass_pot_01 \
#   mod:wooden_stool_02 mod:bananas
