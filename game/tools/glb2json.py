# GLB -> glTF-JSON с буфером в base64 (платформа артефактов не раздаёт .glb). python3 glb2json.py in.glb out.json
import json, struct, base64, sys
b = open(sys.argv[1], 'rb').read()
length = struct.unpack('<I', b[8:12])[0]; off = 12; js = None; binc = None
while off < length:
    clen, ctype = struct.unpack('<II', b[off:off + 8]); data = b[off + 8:off + 8 + clen]; off += 8 + clen
    if ctype == 0x4E4F534A: js = json.loads(data)
    elif ctype == 0x004E4942: binc = data
js['buffers'][0]['uri'] = 'data:application/octet-stream;base64,' + base64.b64encode(binc).decode()
json.dump(js, open(sys.argv[2], 'w'), separators=(',', ':'))
