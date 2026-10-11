"""Предварительные координаты мест базы лил (lila-db/PLACES.md) по OpenStreetMap (Nominatim).

Это лишь КАНДИДАТЫ: каждая точка потом сверяется с топокартой AMS U502 1:250 000 (1955) и источниками;
до сверки status = "unverified". Неземные обители, области, реки и места внутри городов (дома, кунды) —
без автопоиска (type: realm/region/river/site). Запуск: python3 maps/tools/geocode_candidates.py
Правила Nominatim: не чаще 1 запроса в секунду, свой User-Agent; результат пишется в файл после каждого места.
"""
import json, os, re, time, urllib.parse, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'maps', 'places-candidates.json')

REALM = {'#goloka', '#shvetadvipa', '#kailasa', '#svarga', '#vaikuntha', '#brahmaloka', '#lanka'}
REGION = {'#east-bengal', '#radha-desha', '#jharikhanda', '#dravida', '#tailanga', '#karnata', '#travancore',
          '#mithila', '#chorananda'}
RIVER = {'#ganga', '#godavari', '#kaveri', '#tamraparni', '#suvarnarekha', '#padmavati', '#punahpuna'}
# места внутри города — координата берётся от «родителя», уточняется по плану города
SITE_PARENT = {
    '#house-jagannatha-mishra': '#navadvipa', '#house-srivasa': '#navadvipa', '#house-nandana-acharya': '#navadvipa',
    '#house-chandrashekhara': '#navadvipa', '#house-murari': '#navadvipa', '#house-kashi-mishra': '#puri',
    '#narendra-sarovara': '#puri', '#gundicha': '#puri', '#tota': '#puri', '#chataka-parvata': '#puri',
    '#vamshivata': '#vrindavana', '#gomatila': '#vrindavana', '#brahma-kunda': '#vrindavana',
    '#radha-kunda': '#govardhana', '#kusuma-sarovara': '#govardhana',
}
# запросы, где одно имя из PLACES.md неоднозначно (современное название + штат/страна)
QUERY = {
    '#navadvipa': 'Nabadwip, West Bengal', '#shantipura': 'Santipur, West Bengal', '#katwa': 'Katwa, West Bengal',
    '#gaya': 'Gaya, Bihar', '#puri': 'Puri, Odisha', '#vrindavana': 'Vrindavan, Uttar Pradesh',
    '#mathura': 'Mathura, Uttar Pradesh', '#kashi': 'Varanasi', '#prayaga': 'Prayagraj',
    '#shrikhanda': 'Srikhanda, Purba Bardhaman', '#shrihatta': 'Sylhet, Bangladesh', '#dvaraka': 'Dwarka, Gujarat',
    '#naimisharanya': 'Naimisharanya, Uttar Pradesh', '#mandara': 'Mandar Hill, Banka, Bihar',
    '#madhuvana': 'Madhuban, Mathura', '#tamluk': 'Tamluk, West Bengal', '#remuna': 'Remuna, Balasore',
    '#jajpur': 'Jajpur, Odisha', '#bhubaneshvara': 'Bhubaneswar', '#kurma-kshetra': 'Srikurmam, Andhra Pradesh',
    '#simhachala': 'Simhachalam, Visakhapatnam', '#kanchi': 'Kanchipuram, Tamil Nadu',
    '#panchavati': 'Panchavati, Nashik', '#ranga-kshetra': 'Srirangam, Tamil Nadu',
    '#setubandha': 'Rameswaram, Tamil Nadu', '#alalanatha': 'Brahmagiri, Puri, Odisha',
    '#kanai-natashala': 'Kanaiya Natshala, Sahibganj', '#gokula': 'Gokul, Mathura',
    '#govardhana': 'Govardhan, Mathura', '#kulia': 'Kuliya, Nadia', '#rajagriha': 'Rajgir, Bihar',
    '#phulia': 'Phulia, Nadia', '#ramakeli': 'Ramkeli, Malda', '#kulinagrama': 'Kulingram, Purba Bardhaman',
    '#nandagrama': 'Nandgaon, Mathura', '#varshana': 'Barsana, Mathura', '#ambika-kalna': 'Kalna, Purba Bardhaman',
    '#panihati': 'Panihati, West Bengal', '#saptagrama': 'Saptagram, Hooghly', '#badagachhi': 'Bargachhi, West Bengal',
    '#cuttack': 'Cuttack, Odisha', '#kamalapura': 'Kamalpur, Puri, Odisha', '#bhadraka': 'Bhadrak, Odisha',
    '#kumarahatta': 'Halisahar, West Bengal', '#gauda': 'Gaur, Malda', '#jayapura-shrihatta': 'Jaypur, Sylhet',
    '#ekachakra': 'Ekchakra, Birbhum', '#amaipura': 'Amaipur, Purba Bardhaman', '#burdwan': 'Bardhaman, West Bengal',
    '#medinipur': 'Medinipur, West Bengal', '#narayangarh': 'Narayangarh, Paschim Medinipur',
    '#jaleshvara': 'Jaleswar, Balasore', '#trimandal': 'Trimandal', '#vateshvara': 'Vateshvara',
    '#venkata': 'Tirumala, Andhra Pradesh', '#tirupati': 'Tirupati, Andhra Pradesh',
    '#mangalagiri': 'Mangalagiri, Andhra Pradesh', '#vishnu-kanchi': 'Vishnu Kanchi, Kanchipuram',
    '#pakshitirtha': 'Thirukazhukundram, Tamil Nadu', '#tanjore': 'Thanjavur, Tamil Nadu', '#padmakot': 'Padmakot',
    '#tripatra': 'Tripatra', '#rishabha-parvata': 'Alagar Kovil, Madurai', '#madhavi-vana': 'Madhavi vana',
    '#kanyakumari': 'Kanyakumari, Tamil Nadu', '#shringeri': 'Sringeri, Karnataka',
    '#chandapur-kaveri': 'Chandapur, Kodagu', '#pune': 'Pune, Maharashtra', '#jejuri': 'Jejuri, Maharashtra',
    '#nasik': 'Nashik, Maharashtra', '#baroda': 'Vadodara, Gujarat', '#ahmadabad': 'Ahmedabad, Gujarat',
    '#gogha': 'Ghogha, Gujarat', '#somnatha': 'Somnath, Gujarat', '#girnar': 'Girnar, Junagadh',
    '#prabhasa': 'Prabhas Patan, Gujarat', '#kukshi': 'Kukshi, Madhya Pradesh', '#devghar': 'Devghar',
    '#vidyanagara': 'Rajahmundry, Andhra Pradesh', '#rasalkunda': 'Aska, Ganjam', '#lauda': 'Laur, Sunamganj',
    '#purnavati': 'Purnavati', '#ayodhya': 'Ayodhya, Uttar Pradesh', '#badrikashrama': 'Badrinath, Uttarakhand',
    '#narayanapura': 'Narayanpur, Bangladesh', '#benapola': 'Benapole, Jessore', '#kharadaha': 'Khardaha, West Bengal',
    '#khardaha': 'Khardaha, West Bengal', '#chakhandi': 'Chakhandi, Purba Bardhaman', '#yajigrama': 'Jajigram, Purba Bardhaman',
    '#kheturi': 'Kheturi, Rajshahi', '#khanakul': 'Khanakul, Hooghly', '#belpukhuria': 'Belpukur, Nadia',
    '#talagadi': 'Talkhari, Jessore', '#javat': 'Jaav, Mathura', '#sanketa': 'Sanket, Mathura',
    '#vana-vishnupura': 'Bishnupur, Bankura', '#teliya-budhari': 'Budhpara, Rajshahi',
    '#gopivallabhapura': 'Gopiballavpur, Jhargram', '#dharenda': 'Dharenda, Paschim Medinipur',
    '#mahesh': 'Mahesh, Serampore', '#chilka': 'Chilika Lake, Odisha', '#mangalkot': 'Mangalkot, Purba Bardhaman',
    '#dhaka': 'Dhaka, Bangladesh', '#maldah': 'Old Malda, West Bengal', '#virachandrapura': 'Birchandrapur, Birbhum',
    '#bahulavana': 'Bati, Mathura', '#saligrama': 'Saligram, Nadia', '#ariadaha': 'Ariadaha, West Bengal',
    '#boraquli': 'Boraquli', '#kandra': 'Kandra, Purba Bardhaman', '#adaila': 'Arail, Prayagraj',
    '#bhandiravana': 'Bhandirvan, Mathura', '#gangasagara': 'Gangasagar, South 24 Parganas',
    '#kumaranagara': 'Kumarnagar', '#kanchanagaria': 'Kanchangaria', '#deuli': 'Deuli, Bankura',
    '#nrisimhapura': 'Nrusinghapur, Odisha', '#naihati': 'Naihati, West Bengal', '#chandradvipa': 'Barisal, Bangladesh',
    '#fatehabad': 'Faridpur, Bangladesh', '#umrao': 'Umrao, Mathura', '#dandeshvara': 'Dandeshwar',
    '#talakhaida': 'Talkhari, Jessore', '#gopalapura': 'Gopalpur, Rajshahi', '#gambhila': 'Gambhila',
    '#goas': 'Goas, Rajshahi', '#kumarapura': 'Kumarpur, Rajshahi', '#udupi': 'Udupi, Karnataka',
    '#pandharpur': 'Pandharpur, Maharashtra', '#madurai': 'Madurai, Tamil Nadu',
}


def places():
    rows = []
    for ln in open(os.path.join(ROOT, 'lila-db/PLACES.md'), encoding='utf-8'):
        m = re.match(r'^\|\s*(#[a-z0-9-]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$', ln)
        if m: rows.append(dict(tag=m.group(1), ru=m.group(2), en=m.group(3), note=m.group(4)))
    return rows


def nominatim(q):
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(
        {'q': q, 'format': 'json', 'limit': 1, 'countrycodes': 'in,bd,np,lk', 'accept-language': 'en'})
    req = urllib.request.Request(url, headers={'User-Agent': 'Gauranga-lila-map/0.1 (research; github.com/sankarshanservant-hub/Gauranga)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    return res[0] if res else None


def main():
    out = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
    for p in places():
        t = p['tag']
        if t in out and out[t].get('done'): continue
        d = {'ru': p['ru'], 'en': p['en'], 'note': p['note'], 'status': 'unverified', 'done': True}
        if t in REALM: d['type'] = 'realm'
        elif t in REGION: d['type'] = 'region'
        elif t in RIVER: d['type'] = 'river'
        elif t in SITE_PARENT: d.update(type='site', parent=SITE_PARENT[t])
        else:
            d['type'] = 'point'
            q = QUERY.get(t) or p['en'].split('(')[0].strip() + ', India'
            d['query'] = q
            try:
                r = nominatim(q)
            except Exception as e:
                d['error'] = str(e); d['done'] = False; r = None
            if r:
                d.update(lat=round(float(r['lat']), 5), lon=round(float(r['lon']), 5),
                         osm=r.get('display_name', '')[:160], osm_class=f"{r.get('class')}/{r.get('type')}")
            elif 'error' not in d:
                d['found'] = False
            time.sleep(1.2)
        out[t] = d
        json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    pts = [v for v in out.values() if v['type'] == 'point']
    print(f"мест: {len(out)}; точек: {len(pts)}; найдено: {sum(1 for v in pts if 'lat' in v)}; "
          f"не найдено: {sum(1 for v in pts if v.get('found') is False)}; ошибок: {sum(1 for v in pts if 'error' in v)}")


if __name__ == '__main__':
    main()
