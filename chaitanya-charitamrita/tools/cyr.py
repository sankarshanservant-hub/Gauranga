import re,unicodedata
M=[('ṭh','т̣х'),('ḍh','д̣х'),('kh','кх'),('gh','гх'),('ch','чх'),('jh','джх'),('th','тх'),('dh','дх'),('ph','пх'),('bh','бх'),
('ai','аи'),('au','ау'),
('ā','а̄'),('ī','ӣ'),('ū','ӯ'),('ṝ','р̣̄'),('ṛ','р̣'),('ḷ','л̣'),('ṅ','н̇'),('ñ','н̃'),('ṭ','т̣'),('ḍ','д̣'),('ṇ','н̣'),('ś','ш́'),('ṣ','ш̣'),('ṁ','м̇'),('ḥ','х̣'),
('a','а'),('i','и'),('u','у'),('e','е'),('o','о'),('k','к'),('g','г'),('c','ч'),('j','дж'),('t','т'),('d','д'),('n','н'),('p','п'),('b','б'),('m','м'),('y','й'),('r','р'),('l','л'),('v','в'),('s','с'),('h','х'),('ẏ','й'),('ṙ','р')]
def bn_nasals(bn):
    return [ch for ch in bn if ch in 'ঙঁ']
def conv(tr,bn=''):
    tr=unicodedata.normalize('NFC',tr)
    # mark candrabindu ṅ
    seq=bn_nasals(bn); out=[]; i=0
    cnt=tr.count('ṅ')
    use=len(seq)==cnt
    for ch in tr:
        if ch=='ṅ':
            if use: out.append('ṅ' if seq[i]=='ঙ' else '̐')
            else: out.append('ṅ')
            i+=1
        else: out.append(ch)
    tr=''.join(out)
    res=''; j=0
    while j<len(tr):
        for a,b in M:
            if tr.startswith(a,j):
                res+=b; j+=len(a); break
        else:
            res+=tr[j]; j+=1
    # initial e -> э
    res=re.sub(r'(^|[\s\-—‘“’( ])е',lambda m:m.group(1)+'э',res)
    return res,use
