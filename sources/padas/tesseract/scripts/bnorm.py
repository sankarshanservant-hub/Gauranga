import re
# consonant-skeleton normalisation for noisy Bengali OCR
MAP = str.maketrans({
    'ণ': 'ন', 'ষ': 'স', 'শ': 'স', 'জ': 'য', 'ৰ': 'ব', 'ৎ': 'ত',
    'ঈ': 'ই', 'ঊ': 'উ', 'ঐ': 'এ', 'ঔ': 'ও', 'ঙ': 'ং', 'ঞ': 'ন', 'থ': 'ত', 'ধ': 'দ', 'ঘ': 'গ',
    'ভ': 'ব', 'ঠ': 'ট', 'ঢ': 'ড', 'ছ': 'চ', 'ঝ': 'য', 'ফ': 'প', 'খ': 'ক', 'ঃ': '',
})
DROP = re.compile('[া-ৌ্ঁ়ৗৢৣ]')
NONB = re.compile('[^অ-হড়-য়ৰৱং]')


def skel(s):
    s = s.replace('ড়', 'ড').replace('ঢ়', 'ঢ').replace('য়', 'য')
    s = DROP.sub('', s)
    s = NONB.sub('', s)
    return s.translate(MAP)


def grams(s, n=3):
    k = skel(s)
    return {k[i:i + n] for i in range(len(k) - n + 1)}


def sim(a, b):
    ga, gb = grams(a), grams(b)
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / min(len(ga), len(gb))
