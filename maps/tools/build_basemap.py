"""Подложка карты лил для сайта: суша, озёра, реки Южной Азии (без современных границ — чтобы не было анахронизмов).

Источники (в maps/src/):
  natural-earth/ — Natural Earth 1:10m (общественное достояние): ne_10m_land, ne_10m_lakes, ne_10m_rivers_lake_centerlines;
  osm/ — реки Бенгалии из OpenStreetMap (© участники OpenStreetMap, ODbL): Бхагиратхи-Хугли (в Natural Earth её нет),
         Джаланги, Дамодар, Аджай — получены через Nominatim (polygon_geojson).
Результат: site/data/basemap.json (GeoJSON-слои land / lakes / rivers), упрощение ~1 км.
Запуск: python3 maps/tools/build_basemap.py  (нужен shapely)
"""
import json, os
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
NE = os.path.join(ROOT, 'maps', 'src', 'natural-earth')
OSM = os.path.join(ROOT, 'maps', 'src', 'osm')
OUT = os.path.join(ROOT, 'site', 'data', 'basemap.json')
BBOX = box(60, 0, 101, 37)         # Индия с запасом; карта на сайте не выходит за эти пределы
TOL = 0.008                        # упрощение, градусы (~0.9 км)

# русские названия рек для подписей
RIVER_RU = {
    'Ganges': 'Ганга', 'Yamuna': 'Ямуна', 'Godävari': 'Годавари', 'Cauvery': 'Кавери', 'Krishna': 'Кришна',
    'Narmada': 'Нармада', 'Mahäna Nadï': 'Маханади', 'Brahmani': 'Брахмани', 'Son': 'Шона', 'Gandak': 'Гандаки',
    'Ghäghara': 'Гхагхра (Сараю)', 'Brahmaputra': 'Брахмапутра', 'Tista': 'Тиста', 'Tapi': 'Тапти',
    'Tungabhadra': 'Тунгабхадра', 'Bhima': 'Бхима', 'Penner': 'Пеннар', 'Palar': 'Палар', 'Chambal': 'Чамбал',
    'Betwa': 'Бетва', 'Mahi': 'Махи', 'Kolidam': 'Колидам', 'Indus': 'Инд',
    'Hooghly': 'Бхагиратхи (Ганга)', 'Jalangi': 'Джаланги', 'Damodar': 'Дамодар', 'Ajay': 'Аджай',
}
RIVER_EN = {'Hooghly': 'Bhagirathi (Ganga)', 'Godävari': 'Godavari', 'Mahäna Nadï': 'Mahanadi', 'Ghäghara': 'Ghaghara (Sarayu)'}


def load(path):
    return json.load(open(path, encoding='utf-8'))['features']


def clip(g, tol=TOL):
    g = g.intersection(BBOX)
    return None if g.is_empty else g.simplify(tol, preserve_topology=True)


def rounded(geom):
    def r(c):
        if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
            return [round(c[0], 4), round(c[1], 4)]
        return [r(x) for x in c]
    m = mapping(geom)
    return {'type': m['type'], 'coordinates': r(m['coordinates'])}


def main():
    land = clip(unary_union([shape(f['geometry']) for f in load(os.path.join(NE, 'ne_10m_land.geojson'))
                             if shape(f['geometry']).intersects(BBOX)]))
    lakes = [clip(shape(f['geometry'])) for f in load(os.path.join(NE, 'ne_10m_lakes.geojson'))
             if shape(f['geometry']).intersects(BBOX)]
    rivers = []
    for f in load(os.path.join(NE, 'ne_10m_rivers_lake_centerlines.geojson')):
        g = shape(f['geometry'])
        if not g.intersects(BBOX): continue
        p = f['properties']; name = p.get('name') or ''
        g = clip(g)
        if g is None: continue
        rivers.append({'type': 'Feature', 'geometry': rounded(g),
                       'properties': {'name': RIVER_RU.get(name, name), 'name_en': RIVER_EN.get(name, name),
                                      'rank': p.get('scalerank') or 9}})
    for fn, key in (('Hooghly_River.json', 'Hooghly'), ('Jalangi_River.json', 'Jalangi'),
                    ('Damodar_River.json', 'Damodar'), ('Ajay_River.json', 'Ajay')):
        r = load_osm(os.path.join(OSM, fn))
        if r is None: continue
        rivers.append({'type': 'Feature', 'geometry': rounded(clip(shape(r), 0.0015)),   # реки Бенгалии — подробнее
                       'properties': {'name': RIVER_RU[key], 'name_en': RIVER_EN.get(key, key), 'rank': 3 if key == 'Hooghly' else 6,
                                      'src': 'osm'}})
    out = {
        'land': {'type': 'Feature', 'geometry': rounded(land), 'properties': {}},
        'lakes': {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': rounded(g), 'properties': {}} for g in lakes if g]},
        'rivers': {'type': 'FeatureCollection', 'features': rivers},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(OUT, os.path.getsize(OUT) // 1024, 'КБ;', len(rivers), 'рек')


def load_osm(path):
    if not os.path.exists(path): return None
    for r in json.load(open(path, encoding='utf-8')):
        if r.get('class') == 'waterway' and r['geojson']['type'] in ('LineString', 'MultiLineString'):
            return r['geojson']
    return None


if __name__ == '__main__':
    main()
