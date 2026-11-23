# Пробная сцена: двор дома Джаганнатхи Мишры в сумерках пхалгуна-пурнимы (Blender 4.5, Cycles).
# Запуск: blender -b -P build_courtyard.py -- --assets <папка Poly Haven> --out probe.png [--res 50] [--samples 64]
# Ассеты — Poly Haven (CC0); постройки моделируются здесь процедурно.
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(name, default):
    return type(default)(argv[argv.index(name) + 1]) if name in argv else default
A = os.path.abspath(arg('--assets', 'assets'))
OUT = arg('--out', 'probe.png')
RES = arg('--res', 50)
SAMPLES = arg('--samples', 32)
SAVE = arg('--save', '')
random.seed(7)
YARD = (0.0, 2.2, 10.0, 8.4)   # центр и полуоси выметенного двора

# ---------------------------------------------------------------- сцена
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = SAMPLES
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.02
sc.cycles.use_denoising = True
sc.cycles.denoiser = 'OPENIMAGEDENOISE'
sc.cycles.max_bounces = 6
sc.cycles.diffuse_bounces = 3
sc.cycles.glossy_bounces = 2
sc.cycles.transparent_max_bounces = 8
sc.cycles.blur_glossy = 1.0
sc.cycles.sample_clamp_indirect = 6
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = RES
sc.render.film_transparent = False
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = arg('--exposure', 0.0)

# ---------------------------------------------------------------- материалы
def tex_mat(name, tdir, scale=1.0, tint=(1, 1, 1), hue=0.5, sat=1.0, val=1.0, bump=0.5, rough_add=0.0,
            box=True, crop_v=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    bsdf = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    L.new((tc.outputs['Object'] if box else tc.outputs['UV']), mp.inputs['Vector'])
    def img(key, colorspace):
        p = None
        for ext in ('.jpg', '.png'):
            q = os.path.join(A, tdir, key + ext)
            if os.path.exists(q): p = q
        if not p: return None
        n = N.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(p, check_existing=True)
        n.image.colorspace_settings.name = colorspace
        if box:
            n.projection = 'BOX'; n.projection_blend = 0.25
        L.new(mp.outputs['Vector'], n.inputs['Vector'])
        return n
    d = img('diff', 'sRGB')
    hsv = N.new('ShaderNodeHueSaturation')
    hsv.inputs['Hue'].default_value = hue
    hsv.inputs['Saturation'].default_value = sat
    hsv.inputs['Value'].default_value = val
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0
    mix.inputs[7].default_value = (*tint, 1)
    L.new(d.outputs['Color'], hsv.inputs['Color'])
    L.new(hsv.outputs['Color'], mix.inputs[6])
    L.new(mix.outputs[2], bsdf.inputs['Base Color'])
    r = img('rough', 'Non-Color')
    if r:
        ra = N.new('ShaderNodeMath'); ra.operation = 'ADD'; ra.inputs[1].default_value = rough_add
        L.new(r.outputs['Color'], ra.inputs[0]); L.new(ra.outputs[0], bsdf.inputs['Roughness'])
    nrm = img('nor', 'Non-Color')
    if nrm:
        nm = N.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.0
        L.new(nrm.outputs['Color'], nm.inputs['Color'])
        dsp = img('disp', 'Non-Color')
        if dsp and bump > 0:
            bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump
            bp.inputs['Distance'].default_value = 0.05
            L.new(dsp.outputs['Color'], bp.inputs['Height']); L.new(nm.outputs['Normal'], bp.inputs['Normal'])
            L.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
        else:
            L.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Specular IOR Level'].default_value = 0.25
    return m

def flat_mat(name, color, rough=0.8, emit=None, strength=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = strength
    return m

M = {
    'wall': tex_mat('mud_wall', 'patterned_clay_plaster', scale=0.6, tint=(0.80, 0.60, 0.42), sat=1.2, val=0.85),
    'plinth': tex_mat('plinth', 'clay_floor_001', scale=0.5, tint=(0.95, 0.80, 0.62), val=0.9),
    'yard': tex_mat('yard', 'clay_floor_001', scale=0.25, tint=(0.95, 0.85, 0.70), val=0.95),
    'ground': tex_mat('ground', 'brown_mud_dry', scale=0.35, tint=(0.85, 0.75, 0.62)),
    'leaves': tex_mat('leaf_litter', 'forest_leaves_02', scale=0.4, tint=(0.8, 0.75, 0.6), val=0.8),
    'thatch': tex_mat('thatch', 'reed_roof_04', scale=1.0, tint=(0.95, 0.82, 0.62), sat=0.9, val=0.85,
                      bump=1.0, box=False),
    'bamboo': tex_mat('bamboo_fence', 'bamboo_wall', scale=0.7, tint=(0.95, 0.85, 0.65), box=True),
    'pole': tex_mat('bamboo_pole', 'bamboo_wall', scale=2.0, tint=(0.75, 0.62, 0.45)),
    'whitewash': tex_mat('tulasi_white', 'patterned_clay_plaster', scale=0.8, tint=(1.0, 0.96, 0.9), val=1.05,
                         sat=0.4),
    'ochre': flat_mat('ochre_band', (0.28, 0.08, 0.04), 0.95),
    'dark': flat_mat('interior_dark', (0.02, 0.015, 0.01), 1.0),
    'flame': flat_mat('flame', (1, 0.6, 0.2), 0.5, emit=(1.0, 0.55, 0.18), strength=40.0),
    'door': tex_mat('door_wood', 'bark_brown_02', scale=1.5, tint=(0.45, 0.32, 0.22), sat=0.5),
    'clay_lamp': tex_mat('clay_lamp', 'clay_floor_001', scale=4, tint=(0.75, 0.45, 0.3)),
}

def link(obj, coll=None):
    (coll or sc.collection).objects.link(obj)
    return obj

def mesh_obj(name, bm, mat):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); link(o)
    if mat: o.data.materials.append(mat)
    return o

def box(name, c, size, mat, bevel=0.0, rot=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    o = mesh_obj(name, bm, mat)
    o.location = Vector(c); o.rotation_euler.z = rot
    if bevel:
        mod = o.modifiers.new('bev', 'BEVEL'); mod.width = bevel; mod.segments = 3
    for p in o.data.polygons: p.use_smooth = False
    return o

def cyl(name, c, r, h, mat, verts=12, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r if r2 is None else r2, depth=h)
    o = mesh_obj(name, bm, mat); o.location = Vector(c)
    for p in o.data.polygons: p.use_smooth = True
    return o

# ---------------------------------------------------------------- бенгальская хижина (чар-чала)
def roof_charchala(name, cx, cy, W, D, z_eave, rise, sag=0.35, thick=0.28, rot=0.0):
    """Четырёхскатная соломенная кровля с изогнутыми, как у бенгальских чала, карнизами и коньком."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new('UVMap')
    hw, hd = W / 2, D / 2
    ridge_half = max(hw - hd, 0.15)
    ridge_z = z_eave + rise
    def eave(x, y):   # карниз провисает к углам
        k = max(abs(x) / hw, abs(y) / hd)
        f = (x / hw) ** 2 if abs(y) >= hd - 1e-6 else (y / hd) ** 2
        return Vector((x, y, z_eave - sag * f))
    def ridge(x):
        return Vector((x, 0, ridge_z - 0.25 * sag * (x / max(ridge_half, 1e-3)) ** 2))
    NS, NT = 16, 8
    def slope(ea, eb, ra, rb, length):
        grid = []
        for i in range(NS + 1):
            s = i / NS
            e = ea.lerp(eb, s); e = eave(e.x, e.y)
            r = ra.lerp(rb, s); r = ridge(r.x)
            row = []
            for j in range(NT + 1):
                t = j / NT
                p = e.lerp(r, t)
                # лёгкая «пухлость» соломы: выпуклость посередине ската
                p.z += 0.10 * math.sin(math.pi * t)
                row.append(bm.verts.new(p))
            grid.append(row)
        sl = (ra - ea).length + 1e-3
        for i in range(NS):
            for j in range(NT):
                f = bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
                for lp, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                    lp[uv].uv = (a / NS * length / 1.6, -b / NT * sl / 1.6)
    R0, R1 = Vector((-ridge_half, 0, 0)), Vector((ridge_half, 0, 0))
    slope(Vector((-hw, -hd, 0)), Vector((hw, -hd, 0)), R0, R1, W)     # передний скат
    slope(Vector((hw, hd, 0)), Vector((-hw, hd, 0)), R1, R0, W)       # задний
    slope(Vector((hw, -hd, 0)), Vector((hw, hd, 0)), R1, R1, D)       # торцы (треугольники)
    slope(Vector((-hw, hd, 0)), Vector((-hw, -hd, 0)), R0, R0, D)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    o = mesh_obj(name, bm, M['thatch'])
    for p in o.data.polygons: p.use_smooth = True
    so = o.modifiers.new('thick', 'SOLIDIFY'); so.thickness = thick; so.offset = -1
    o.location = (cx, cy, 0); o.rotation_euler.z = rot
    return o

def hut(name, cx, cy, W, D, rot=0.0, wall_h=2.3, plinth_h=0.55, veranda=1.3, door=True, glow=None,
        roof_rise=None, lamp_on_veranda=False):
    """Хижина на глиняном цоколе: стены из глины, веранда (дава) на бамбуковых столбах, чар-чала."""
    objs = []
    rotm = Matrix.Rotation(rot, 4, 'Z')
    def P(x, y, z=0):
        v = rotm @ Vector((x, y, z)); return Vector((cx + v.x, cy + v.y, v.z))
    # цоколь (с верандой спереди, -Y локально)
    pd = D + veranda
    objs.append(box(name + '_plinth', P(0, -veranda / 2, plinth_h / 2), (W + 0.5, pd + 0.5, plinth_h), M['plinth'],
                    bevel=0.12, rot=rot))
    t = 0.35   # толщина глиняной стены
    z0 = plinth_h + wall_h / 2
    objs.append(box(name + '_wall_back', P(0, D / 2 - t / 2, z0), (W, t, wall_h), M['wall'], 0.05, rot))
    objs.append(box(name + '_wall_l', P(-W / 2 + t / 2, 0, z0), (t, D, wall_h), M['wall'], 0.05, rot))
    objs.append(box(name + '_wall_r', P(W / 2 - t / 2, 0, z0), (t, D, wall_h), M['wall'], 0.05, rot))
    dw, dh = 0.95, 1.75
    seg = (W - dw) / 2
    if door:
        objs.append(box(name + '_wall_fl', P(-W / 2 + seg / 2, -D / 2 + t / 2, z0), (seg, t, wall_h), M['wall'], 0.05, rot))
        objs.append(box(name + '_wall_fr', P(W / 2 - seg / 2, -D / 2 + t / 2, z0), (seg, t, wall_h), M['wall'], 0.05, rot))
        objs.append(box(name + '_lintel', P(0, -D / 2 + t / 2, plinth_h + dh + (wall_h - dh) / 2),
                        (dw, t, wall_h - dh), M['wall'], 0.03, rot))
        # створки двери (дерево), распахнуты внутрь
        for sg in (-1, 1):
            leaf = box(name + '_door', P(sg * (dw / 2 - 0.05), -D / 2 + t + 0.22, plinth_h + dh / 2), (0.06, 0.45, dh),
                       M['door'], 0.01, rot)
        objs.append(box(name + '_frame', P(0, -D / 2 - 0.01, plinth_h + dh + 0.06), (dw + 0.2, 0.08, 0.12), M['door'], 0.01, rot))
        # тёмное нутро
        objs.append(box(name + '_inside', P(0, 0, plinth_h + 0.02), (W - 2 * t, D - 2 * t, 0.02), M['plinth'], 0, rot))
        objs.append(box(name + '_ceil', P(0, 0, plinth_h + wall_h - 0.02), (W - 2 * t, D - 2 * t, 0.04), M['dark'], 0, rot))
    else:
        objs.append(box(name + '_wall_f', P(0, -D / 2 + t / 2, z0), (W, t, wall_h), M['wall'], 0.05, rot))
    # охристая полоса по низу стен (обмазка)
    objs.append(box(name + '_band', P(0, -D / 2 - 0.005, plinth_h + 0.12), (W - 0.02, 0.02, 0.24), M['ochre'], 0, rot))
    # столбы веранды
    for x in (-W / 2 + 0.2, -W / 6, W / 6, W / 2 - 0.2):
        c = P(x, -D / 2 - veranda + 0.25, plinth_h + wall_h / 2 + 0.1)
        objs.append(cyl(name + '_post', c, 0.07, wall_h + 0.2, M['pole'], 10))
    # кровля
    ex, ey = W + 0.9, pd + 0.9
    rise = roof_rise if roof_rise else 0.55 * ey
    rc = P(0, -veranda / 2)
    objs.append(roof_charchala(name + '_roof', rc.x, rc.y, ex, ey, plinth_h + wall_h + 0.15, rise, rot=rot))
    # свет внутри (лампада/очаг) — тёплое свечение дверного проёма
    if glow:
        L = bpy.data.lights.new(name + '_glow', 'POINT'); L.energy = glow; L.color = (1.0, 0.55, 0.22)
        L.shadow_soft_size = 0.3
        lo = bpy.data.objects.new(name + '_glow', L); lo.location = P(0, 0.2, plinth_h + 0.9); link(lo)
    if lamp_on_veranda:
        diya(P(dw * 0.9, -D / 2 - 0.35, plinth_h), 25)
    return objs

def diya(pos, energy=15, color=(1.0, 0.5, 0.15)):
    """Глиняная масляная лампада с огоньком."""
    b = cyl('diya', pos + Vector((0, 0, 0.03)), 0.06, 0.05, M['clay_lamp'], 12, r2=0.075)
    f = cyl('flame', pos + Vector((0.03, 0, 0.09)), 0.012, 0.05, M['flame'], 8, r2=0.002)
    L = bpy.data.lights.new('diya_light', 'POINT'); L.energy = energy; L.color = color; L.shadow_soft_size = 0.05
    lo = bpy.data.objects.new('diya_light', L); lo.location = pos + Vector((0.03, 0, 0.14)); link(lo)
    return b

def tulasi_mancha(pos):
    x, y = pos
    box('tm_base', (x, y, 0.15), (1.5, 1.5, 0.3), M['whitewash'], 0.04)
    box('tm_step', (x, y, 0.45), (1.1, 1.1, 0.3), M['whitewash'], 0.04)
    box('tm_band', (x, y, 0.62), (1.12, 1.12, 0.05), M['ochre'], 0.01)
    p = cyl('tm_pillar', (x, y, 1.05), 0.36, 0.9, M['whitewash'], 4, r2=0.42)
    p.rotation_euler.z = math.pi / 4
    for po in p.data.polygons: po.use_smooth = False
    cyl('tm_bowl', (x, y, 1.58), 0.42, 0.16, M['whitewash'], 4, r2=0.5).rotation_euler.z = math.pi / 4
    diya(Vector((x, y - 0.78, 0.30)), 30)
    diya(Vector((x + 0.25, y - 0.62, 0.60)), 12)

# ---------------------------------------------------------------- импорт моделей Poly Haven
def load_model(aid):
    coll = bpy.data.collections.new('src_' + aid)
    sc.collection.children.link(coll)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(A, aid, aid + '.gltf'))
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        for c in o.users_collection: c.objects.unlink(o)
        coll.objects.link(o)
    # габариты
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    for o in new:
        if o.type != 'MESH': continue
        for v in o.bound_box:
            w = o.matrix_world @ Vector(v)
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    coll['height'] = (mx.z - mn.z)
    sc.view_layers[0].layer_collection.children[coll.name].exclude = True
    return coll

def place(coll, pos, height=None, scale=1.0, rot=None, tilt=0.0):
    e = bpy.data.objects.new('inst_' + coll.name, None)
    e.instance_type = 'COLLECTION'; e.instance_collection = coll
    s = (height / coll['height']) if height else scale
    e.scale = (s, s, s)
    e.location = Vector(pos)
    e.rotation_euler = (tilt, 0, random.uniform(0, 6.28) if rot is None else rot)
    link(e)
    return e

def tex_bsdf(nt, tdir, scale, tint=(1, 1, 1), sat=1.0, val=1.0, coord=None):
    N, L = nt.nodes, nt.links
    b = N.new('ShaderNodeBsdfPrincipled')
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale,) * 3
    L.new(coord, mp.inputs['Vector'])
    def img(key, cs):
        q = os.path.join(A, tdir, key + '.jpg')
        if not os.path.exists(q): return None
        n = N.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(q, check_existing=True)
        n.image.colorspace_settings.name = cs; L.new(mp.outputs['Vector'], n.inputs['Vector']); return n
    d = img('diff', 'sRGB'); h = N.new('ShaderNodeHueSaturation')
    h.inputs['Saturation'].default_value = sat; h.inputs['Value'].default_value = val
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
    mx.inputs[7].default_value = (*tint, 1)
    L.new(d.outputs['Color'], h.inputs['Color']); L.new(h.outputs['Color'], mx.inputs[6]); L.new(mx.outputs[2], b.inputs['Base Color'])
    r = img('rough', 'Non-Color')
    if r: L.new(r.outputs['Color'], b.inputs['Roughness'])
    n = img('nor', 'Non-Color')
    if n:
        nm = N.new('ShaderNodeNormalMap'); L.new(n.outputs['Color'], nm.inputs['Color']); L.new(nm.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Specular IOR Level'].default_value = 0.2
    return b

def alpana(nt, coord, c):
    N, L = nt.nodes, nt.links
    def m(op, a, b=None):
        n = N.new('ShaderNodeMath'); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs[0]
    sep = N.new('ShaderNodeSeparateXYZ'); L.new(coord, sep.inputs['Vector'])
    x = m('SUBTRACT', sep.outputs['X'], c[0]); y = m('SUBTRACT', sep.outputs['Y'], c[1])
    r = m('SQRT', m('ADD', m('MULTIPLY', x, x), m('MULTIPLY', y, y)))
    th = m('ARCTAN2', y, x)
    def line(val, w):   # 1 на тонкой линии |val|<w
        return m('LESS_THAN', m('ABSOLUTE', val), w)
    ring1 = line(m('SUBTRACT', r, 1.05), 0.025)
    ring2 = line(m('SUBTRACT', r, 2.05), 0.03)
    ring3 = line(m('SUBTRACT', r, 2.2), 0.015)
    # 8 лепестков между r=1.05 и 1.95: контур |phi| = k*sin(pi*t)
    n = 8.0
    fr = m('FRACT', m('MULTIPLY', m('ADD', th, 3.14159), n / 6.28318))
    phi = m('MULTIPLY', m('SUBTRACT', fr, 0.5), 6.28318 / n)
    t = m('DIVIDE', m('SUBTRACT', r, 1.05), 0.9)
    inside = m('MULTIPLY', m('GREATER_THAN', t, 0.0), m('LESS_THAN', t, 1.0))
    wdt = m('MULTIPLY', m('POWER', m('SINE', m('MULTIPLY', m('MINIMUM', m('MAXIMUM', t, 0.0), 1.0), 3.14159)), 0.8), 0.33)
    petal = m('MULTIPLY', line(m('SUBTRACT', m('ABSOLUTE', phi), wdt), m('DIVIDE', 0.022, m('MAXIMUM', r, 0.5))), inside)
    # средняя жилка и точка в лепестке
    vein = m('MULTIPLY', m('MULTIPLY', line(phi, m('DIVIDE', 0.012, m('MAXIMUM', r, 0.5))), inside), m('LESS_THAN', t, 0.7))
    # точки на внешнем кольце: 32 шт
    fr2 = m('FRACT', m('MULTIPLY', m('ADD', th, 3.14159), 32 / 6.28318))
    arc = m('MULTIPLY', m('MULTIPLY', m('SUBTRACT', fr2, 0.5), 6.28318 / 32), r)
    rad = m('SUBTRACT', r, 2.38)
    dots = m('LESS_THAN', m('SQRT', m('ADD', m('MULTIPLY', arc, arc), m('MULTIPLY', rad, rad))), 0.05)
    tot = m('MINIMUM', m('ADD', m('ADD', m('ADD', ring1, ring2), m('ADD', ring3, petal)), m('ADD', vein, dots)), 1.0)
    # рисовая паста ложится неровно
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 18; L.new(coord, nz.inputs['Vector'])
    br = N.new('ShaderNodeMapRange'); L.new(nz.outputs['Fac'], br.inputs['Value'])
    br.inputs['From Min'].default_value = 0.3; br.inputs['From Max'].default_value = 0.55
    return m('MULTIPLY', tot, br.outputs[0])

def ground_mix():
    """Чисто выметенный, обмазанный глиной двор, переходящий в траву по неровной границе."""
    m = bpy.data.materials.new('ground_mix'); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    N.remove(N['Principled BSDF'])
    tc = N.new('ShaderNodeTexCoord')
    yard = tex_bsdf(nt, 'clay_floor_001', 0.25, (0.95, 0.84, 0.68), 1.0, 0.95, tc.outputs['Object'])
    path = tex_bsdf(nt, 'brown_mud_dry', 0.35, (0.80, 0.70, 0.58), 1.0, 0.9, tc.outputs['Object'])
    grass = tex_bsdf(nt, 'leafy_grass', 0.3, (0.75, 0.95, 0.55), 1.3, 0.8, tc.outputs['Object'])
    # алпана — узор рисовой пастой вокруг туласи-манчи: лепестки лотоса, кольца, точки
    bc = yard.inputs['Base Color'].links[0].from_socket
    alp = alpana(nt, tc.outputs['Object'], (0.3, 0.6))
    mw = N.new('ShaderNodeMix'); mw.data_type = 'RGBA'; L.new(alp, mw.inputs['Factor'])
    L.new(bc, mw.inputs[6]); mw.inputs[7].default_value = (0.92, 0.9, 0.84, 1)
    L.new(mw.outputs[2], yard.inputs['Base Color'])
    # маска двора: эллипс + шум
    sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs['Vector'])
    def math_(op, a, b=None, v=None):
        n = N.new('ShaderNodeMath'); n.operation = op
        if isinstance(a, float): n.inputs[0].default_value = a
        else: L.new(a, n.inputs[0])
        if b is not None:
            if isinstance(b, float): n.inputs[1].default_value = b
            else: L.new(b, n.inputs[1])
        return n.outputs[0]
    x = math_('MULTIPLY', math_('SUBTRACT', sep.outputs['X'], YARD[0]), 1 / YARD[2])
    y = math_('MULTIPLY', math_('SUBTRACT', sep.outputs['Y'], YARD[1]), 1 / YARD[3])
    r = math_('SQRT', math_('ADD', math_('MULTIPLY', x, x), math_('MULTIPLY', y, y)))
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.35; nz.inputs['Detail'].default_value = 6
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    r2 = math_('ADD', r, math_('MULTIPLY', math_('SUBTRACT', nz.outputs['Fac'], 0.5), 0.45))
    ramp = N.new('ShaderNodeMapRange'); L.new(r2, ramp.inputs['Value'])
    ramp.inputs['From Min'].default_value = 0.88; ramp.inputs['From Max'].default_value = 1.05
    ramp2 = N.new('ShaderNodeMapRange'); L.new(r2, ramp2.inputs['Value'])
    ramp2.inputs['From Min'].default_value = 1.0; ramp2.inputs['From Max'].default_value = 1.25
    m1 = N.new('ShaderNodeMixShader'); L.new(ramp.outputs[0], m1.inputs[0]); L.new(yard.outputs[0], m1.inputs[1]); L.new(path.outputs[0], m1.inputs[2])
    m2 = N.new('ShaderNodeMixShader'); L.new(ramp2.outputs[0], m2.inputs[0]); L.new(m1.outputs[0], m2.inputs[1]); L.new(grass.outputs[0], m2.inputs[2])
    L.new(m2.outputs[0], N['Material Output'].inputs['Surface'])
    return m

def leaf_mat(name, color, trans=0.35):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = 0.5
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB'); L.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].color = (color[0] * 0.6, color[1] * 0.7, color[2] * 0.5, 1)
    ramp.color_ramp.elements[1].color = (color[0] * 1.3, color[1] * 1.15, color[2] * 1.1, 1)
    L.new(ramp.outputs['Color'], b.inputs['Base Color'])
    tr = N.new('ShaderNodeBsdfTranslucent'); L.new(ramp.outputs['Color'], tr.inputs['Color'])
    mx = N.new('ShaderNodeMixShader'); mx.inputs[0].default_value = trans
    L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], N['Material Output'].inputs['Surface'])
    return m

M['palm_leaf'] = leaf_mat('palm_leaf', (0.10, 0.20, 0.05))
M['banana_leaf'] = leaf_mat('banana_leaf', (0.14, 0.30, 0.05), 0.45)
M['banana_stem'] = leaf_mat('banana_stem', (0.20, 0.24, 0.08), 0.1)
M['palm_bark'] = tex_mat('palm_bark', 'bark_willow', scale=1.2, tint=(0.75, 0.68, 0.6), sat=0.6)

def tube(bm, pts, radii, nseg=8):
    rings = []
    for i, (p, r) in enumerate(zip(pts, radii)):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        a = d.orthogonal().normalized(); b = d.cross(a)
        rings.append([bm.verts.new(p + (a * math.cos(k / nseg * 6.283) + b * math.sin(k / nseg * 6.283)) * r) for k in range(nseg)])
    for i in range(len(rings) - 1):
        for k in range(nseg):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % nseg], rings[i + 1][(k + 1) % nseg], rings[i + 1][k]))

def coconut_palm(pos, H=8.0, seed=0):
    rnd = random.Random(seed)
    base = Vector(pos); az = rnd.uniform(0, 6.283); lean = rnd.uniform(0.8, 2.0)
    ld = Vector((math.cos(az), math.sin(az), 0))
    pts = [base + ld * lean * (t / 12) ** 1.6 + Vector((0, 0, H * t / 12)) for t in range(13)]
    bm = bmesh.new(); tube(bm, pts, [0.2 - 0.07 * t / 12 for t in range(13)], 10)
    o = mesh_obj('palm_trunk', bm, M['palm_bark'])
    for p in o.data.polygons: p.use_smooth = True
    top = pts[-1]
    bm = bmesh.new()
    nf = 16
    for f in range(nf):
        a = f / nf * 6.283 + rnd.uniform(-0.15, 0.15)
        d = Vector((math.cos(a), math.sin(a), 0))
        elev = rnd.uniform(-0.2, 0.9); Lf = rnd.uniform(3.2, 4.2)
        side = d.cross(Vector((0, 0, 1)))
        def rach(s):
            return top + d * (Lf * s * math.cos(elev * 0.5)) + Vector((0, 0, Lf * (math.sin(elev) * 0.6 * s - 0.55 * s * s)))
        bm2 = []
        for i in range(1, 36):
            s = i / 36
            p = rach(s); t = (rach(min(s + 0.02, 1)) - p).normalized()
            ll = 0.95 * math.sin(math.pi * min(s * 1.15, 1)) ** 0.6 + 0.12
            for sg in (-1, 1):
                out = (side * sg * 0.75 + Vector((0, 0, -0.65)) + t * 0.45).normalized()
                w = t * 0.035
                v = [bm.verts.new(p - w), bm.verts.new(p + w), bm.verts.new(p + out * ll + t * 0.12)]
                bm.faces.new(v)
    o = mesh_obj('palm_crown', bm, M['palm_leaf'])
    # кокосы
    for k in range(5):
        a = k / 5 * 6.283
        cyl('coconut', top + Vector((0.22 * math.cos(a), 0.22 * math.sin(a), -0.25)), 0.12, 0.22, M['palm_bark'], 8)

def banana(pos, H=2.2, seed=0):
    rnd = random.Random(seed)
    base = Vector(pos)
    o = cyl('banana_stem', base + Vector((0, 0, H / 2)), 0.13, H, M['banana_stem'], 10, r2=0.09)
    top = base + Vector((0, 0, H))
    bm = bmesh.new()
    for f in range(8):
        a = f / 8 * 6.283 + rnd.uniform(-0.3, 0.3)
        d = Vector((math.cos(a), math.sin(a), 0)); side = d.cross(Vector((0, 0, 1)))
        elev = rnd.uniform(0.6, 1.2); Lb = rnd.uniform(1.5, 2.1); pet = 0.5
        p0 = top + Vector((0, 0, rnd.uniform(-0.3, 0.1)))
        def mid(s):
            return p0 + d * ((pet + Lb * s) * math.cos(elev * (1 - s))) + Vector((0, 0, (pet + Lb * s) * math.sin(elev) * (1 - s) * 0.9 - 0.4 * s * s))
        n = 16
        for i in range(n):
            s0, s1 = i / n, (i + 1) / n
            w0 = 0.42 * math.sin(math.pi * (0.05 + 0.9 * s0)) ** 0.5; w1 = 0.42 * math.sin(math.pi * (0.05 + 0.9 * s1)) ** 0.5
            gap = 0.03 if rnd.random() < 0.45 else 0.0   # ветер рвёт лист полосами
            for sg in (-1, 1):
                a0, a1 = mid(s0 + gap / 2), mid(s1 - gap / 2)
                droop = Vector((0, 0, -0.12))
                v = [bm.verts.new(a0), bm.verts.new(a1), bm.verts.new(a1 + side * sg * w1 + droop), bm.verts.new(a0 + side * sg * w0 + droop)]
                bm.faces.new(v)
    mesh_obj('banana_leaves', bm, M['banana_leaf'])

# ---------------------------------------------------------------- планировка двора
# земля
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=30)
GROUND = mesh_obj('ground', bm, ground_mix())

# главный дом (север), кухня (запад), родильная хижина у нима (северо-восток), коровник (восток)
hut('ghar', -0.5, 7.2, 7.0, 4.0, rot=0.0, glow=60, lamp_on_veranda=True)
hut('kitchen', -7.4, 0.5, 5.0, 3.4, rot=math.pi / 2, glow=140)          # фасад на восток
hut('sutika', 6.2, 6.6, 3.4, 2.8, rot=math.radians(-20), wall_h=2.0, veranda=0.8, glow=45)
# коровник — навес без стен
for x, yy in ((7.2, -1.5), (9.4, -1.5), (7.2, 1.7), (9.4, 1.7)):
    cyl('shed_post', (x, yy, 1.1), 0.08, 2.2, M['pole'], 10)
roof_charchala('shed_roof', 8.3, 0.1, 3.4, 4.4, 2.2, 1.3, sag=0.25)

# туласи-манча посередине двора
tulasi_mancha((0.3, 0.6))

# бамбуковая плетёная ограда по заднему краю
def fence(a, b, h=1.7):
    a, b = Vector(a), Vector(b)
    d = b - a; L = d.length; ang = math.atan2(d.y, d.x)
    box('fence', ((a + b) / 2).to_3d() + Vector((0, 0, h / 2)), (L, 0.06, h), M['bamboo'], 0, ang)
    n = int(L / 1.5)
    for i in range(n + 1):
        p = a.lerp(b, i / n)
        cyl('fpost', (p.x, p.y, h / 2 + 0.1), 0.05, h + 0.2, M['pole'], 8)
fence((-10.5, 10.5), (10.5, 10.5))
fence((-10.5, -6.0), (-10.5, 10.5))

# растения и предметы
tree = load_model('tree_small_02')        # «ним» у родильной хижины
palm = load_model('island_tree_02')
shrub = load_model('shrub_04')
pach = load_model('pachira_aquatica_01')
cal = load_model('calathea_orbifolia_01')
pot = load_model('ceramic_pot')
cpot = load_model('planter_pot_clay')
basket = load_model('wicker_basket_01')
brass = load_model('brass_pot_01')
lantern = load_model('brass_diya_lantern')
stool = load_model('wooden_stool_02')
bananas = load_model('bananas')

place(tree, (9.0, 8.8, 0), height=9.0, rot=0.6)
place(palm, (-6.0, 12.5, 0), height=7.5)          # манговое дерево за оградой
place(load_model('island_tree_01'), (13.5, 2.0, 0), height=8.0)
for i, p in enumerate(((-12.0, 8.0), (-13.0, -1.5), (-6.5, 16.5), (3.5, 13.0), (-2.0, 14.5), (14.0, 9.5), (-13.5, 12.5))):
    coconut_palm((*p, 0), H=random.uniform(7.5, 10.5), seed=i)
for i, p in enumerate(((-9.8, 7.0), (-11.2, 6.0), (-10.4, 4.4), (-11.8, 3.0), (9.6, -4.0), (11.0, -3.0), (10.2, -6.0),
                       (2.0, 11.6), (5.5, 11.8), (-12.4, -4.5), (-9.2, -7.5))):
    banana((*p, 0), H=random.uniform(1.6, 2.6), seed=10 + i)
place(shrub, (0.3, 0.6, 1.66), height=0.55)                 # туласи на алтаре
for p in ((-4.2, 9.8), (3.8, 9.9), (-9.6, 5.2), (10.2, 4.5), (-10.0, -5.0), (4.6, 4.2)):
    place(pach if random.random() < 0.5 else cal, (*p, 0), height=random.uniform(0.9, 1.6))
for i in range(22):   # подлесок за краем двора (сзади)
    ang = random.uniform(0.3, 3.0); r = random.uniform(11.5, 15.0)
    place(random.choice((pach, cal, shrub)), (r * math.cos(ang) * 1.05, 1.5 + r * math.sin(ang), 0),
          height=random.uniform(0.4, 1.2))
# кухонная утварь на веранде кухни
for i, (dx, dy) in enumerate(((-5.6, 2.0), (-5.7, 1.4), (-5.6, -0.8), (-5.4, -1.3))):
    place(pot if i % 2 else cpot, (dx, dy, 0.55), height=random.uniform(0.32, 0.42), tilt=math.pi / 2 if i % 2 == 0 and False else 0)
place(brass, (-5.5, 0.4, 0.55), height=0.25)
place(basket, (-5.2, -2.6, 0.02), height=0.35)
place(stool, (-1.8, 4.8, 0.55), height=0.22)
place(bananas, (1.3, 4.6, 0.56), height=0.18)
lan = place(lantern, (-0.5, 4.25, 2.55), height=0.45, rot=0)
Ll = bpy.data.lights.new('lantern', 'POINT'); Ll.energy = 35; Ll.color = (1, 0.55, 0.2); Ll.shadow_soft_size = 0.1
lo = bpy.data.objects.new('lantern', Ll); lo.location = (-0.5, 4.25, 2.4); link(lo)
for p in ((-2.5, -3.0), (3.4, -2.2), (-3.6, 3.4), (2.8, 3.6)):
    diya(Vector((p[0], p[1], 0.02)), 10)

# ---------------------------------------------------------------- бытовые детали
M['straw'] = tex_mat('straw', 'reed_roof_04', scale=1.3, tint=(1.0, 0.86, 0.6), val=0.95)
M['dung'] = tex_mat('dung', 'brown_mud_dry', scale=3, tint=(0.45, 0.34, 0.24), val=0.7)
M['wood'] = tex_mat('firewood', 'bark_brown_02', scale=2, tint=(0.6, 0.48, 0.36))
M['sari'] = flat_mat('sari', (0.85, 0.80, 0.70), 0.9)
M['sari_border'] = flat_mat('sari_border', (0.55, 0.05, 0.04), 0.9)
M['water'] = bpy.data.materials.new('water'); M['water'].use_nodes = True
wb = M['water'].node_tree.nodes['Principled BSDF']
wb.inputs['Base Color'].default_value = (0.012, 0.02, 0.012, 1); wb.inputs['Roughness'].default_value = 0.1
wb.inputs['Specular IOR Level'].default_value = 0.6
wn_ = M['water'].node_tree.nodes; wnz = wn_.new('ShaderNodeTexNoise'); wnz.inputs['Scale'].default_value = 6
wbp = wn_.new('ShaderNodeBump'); wbp.inputs['Strength'].default_value = 0.08
M['water'].node_tree.links.new(wnz.outputs['Fac'], wbp.inputs['Height']); M['water'].node_tree.links.new(wbp.outputs['Normal'], wb.inputs['Normal'])

def haystack(pos, r=1.1, h=2.6):
    """Стог рисовой соломы вокруг шеста (кхер-гада)."""
    bm = bmesh.new()
    pts = [Vector((0, 0, h * t / 10)) for t in range(11)]
    prof = [r * (0.85 + 0.15 * math.sin(math.pi * t / 10 * 0.9)) * (1 - (t / 10) ** 2.2) + 0.03 for t in range(11)]
    tube(bm, pts, prof, 20)
    o = mesh_obj('haystack', bm, M['straw']); o.location = Vector(pos)
    for p in o.data.polygons: p.use_smooth = True
    d = o.modifiers.new('d', 'DISPLACE'); tx = bpy.data.textures.new('hay', 'CLOUDS'); tx.noise_scale = 0.25; d.texture = tx; d.strength = 0.12
    cyl('hay_pole', Vector(pos) + Vector((0, 0, h * 0.6)), 0.04, h * 1.2, M['pole'], 8)

def dung_cakes(p0, along, n=8, z0=1.0):
    """Лепёшки кизяка, налепленные сушиться на стену."""
    for i in range(n):
        c = Vector(p0) + along * (i * 0.32 + random.uniform(-0.05, 0.05)) + Vector((0, 0, z0 + random.uniform(-0.35, 0.35)))
        o = cyl('dung', c, 0.11, 0.03, M['dung'], 10)
        o.rotation_euler = (math.pi / 2, 0, math.atan2(along.y, along.x))

def woodpile(pos, rot=0.0):
    for i in range(18):
        layer = i // 6; k = i % 6
        o = cyl('log', Vector(pos) + Matrix.Rotation(rot, 3, 'Z') @ Vector((k * 0.13 - 0.33 + layer * 0.06, 0, 0.07 + layer * 0.12)),
                0.06, random.uniform(0.9, 1.1), M['wood'], 8)
        o.rotation_euler = (math.pi / 2, 0, rot + random.uniform(-0.05, 0.05))

def clothesline(a, b, sag=0.25, h=1.9):
    a, b = Vector(a), Vector(b)
    for p in (a, b): cyl('line_post', (p.x, p.y, h / 2), 0.04, h, M['pole'], 8)
    # сари, перекинутое через верёвку: полотно с провисом
    bm = bmesh.new(); n = 24; d = b - a
    side = Vector((-d.y, d.x, 0)).normalized()
    top = []; bot_f = []; bot_b = []
    for i in range(n + 1):
        t = i / n
        p = a.lerp(b, t).to_3d(); p.z = h - sag * 4 * t * (1 - t)
        top.append(bm.verts.new(p))
        if 0.15 < t < 0.85:
            wav = 0.04 * math.sin(t * 40)
            bot_f.append((i, bm.verts.new(p + side * (0.05 + wav) + Vector((0, 0, -1.0)))))
            bot_b.append((i, bm.verts.new(p - side * (0.05 - wav) + Vector((0, 0, -1.05)))))
    for lst in (bot_f, bot_b):
        for (i, v), (j, w) in zip(lst, lst[1:]):
            bm.faces.new((top[i], top[j], w, v))
    edges = [[v.co.copy() for _, v in lst] for lst in (bot_f, bot_b)]
    o = mesh_obj('sari', bm, M['sari'])
    # кайма
    bm = bmesh.new()
    for lst in edges:
        prev = None
        for q in lst:
            r = q + Vector((0, 0, 0.12))
            cur = (bm.verts.new(q + side * 0.003), bm.verts.new(r + side * 0.003))
            if prev: bm.faces.new((prev[0], cur[0], cur[1], prev[1]))
            prev = cur
    mesh_obj('sari_border', bm, M['sari_border'])

def pond(c, rx=4.2, ry=3.0):
    """Пруд-пукур с кирпичным гхатом."""
    def wob(v):
        a = math.atan2(v.co.y, v.co.x); k = 1 + 0.07 * math.sin(3 * a + 1) + 0.05 * math.sin(5 * a + 2) + 0.03 * math.sin(9 * a)
        v.co.x *= k; v.co.y *= k
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=40, radius=1.0)
    for v in bm.verts: wob(v)
    o = mesh_obj('pond', bm, M['water']); o.location = (c[0], c[1], 0.012); o.scale = (rx, ry, 1)
    # берег — тёмная кромка, проваленная вниз
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=False, segments=40, radius=0.97)
    for v in bm.verts: wob(v)
    ring = list(bm.verts); outer = [bm.verts.new(v.co * 1.22 + Vector((0, 0, 0.0))) for v in ring]
    for v in ring: v.co.z = 0.02
    for i in range(40):
        bm.faces.new((ring[i], ring[(i + 1) % 40], outer[(i + 1) % 40], outer[i]))
    o = mesh_obj('bank', bm, M['ground_bank']); o.location = (c[0], c[1], 0.004); o.scale = (rx, ry, 1)
    for k in range(4):   # ступени гхата
        box('ghat', (c[0] + rx * 0.62 + k * 0.32, c[1] + ry * 0.55, 0.03 + k * 0.08), (1.6, 0.4, 0.12), M['plinth'], 0.02, math.radians(-35))

M['ground_bank'] = tex_mat('bank', 'mud_forest', scale=0.6, tint=(0.8, 0.75, 0.6))
haystack((12.0, -2.8, 0), 1.0, 2.5)
haystack((11.0, 4.6, 0), 1.2, 2.8)
dung_cakes((-9.15, -1.4, 0.55), Vector((0, 1, 0)), 9, 1.3)       # задняя (западная) стена кухни
dung_cakes((2.6, 9.45, 0.55), Vector((1, 0, 0)), 6, 1.4)
woodpile((-5.6, -3.4, 0.0), 0.2)
clothesline((3.6, -2.4), (6.6, -0.6), 0.2, 1.9)
pond((-2.5, -9.8), 3.6, 2.4)
place(load_model('wicker_basket_02') if os.path.exists(os.path.join(A, 'wicker_basket_02')) else basket, (-1.2, 4.9, 0.56), height=0.3)

# ---------------------------------------------------------------- трава (geometry nodes) и бамбук
M['grass'] = leaf_mat('grass_blades', (0.16, 0.28, 0.06), 0.3)

def grass_clump():
    bm = bmesh.new(); rnd = random.Random(3)
    for k in range(16):
        a = rnd.uniform(0, 6.283); r0 = rnd.uniform(0, 0.08); h = rnd.uniform(0.18, 0.42); lean = rnd.uniform(0.05, 0.25)
        d = Vector((math.cos(a), math.sin(a), 0)); side = d.cross(Vector((0, 0, 1))) * 0.012
        b = d * r0
        mid = b + d * lean * 0.5 + Vector((0, 0, h * 0.6)); tip = b + d * lean + Vector((0, 0, h))
        v = [bm.verts.new(b - side), bm.verts.new(b + side), bm.verts.new(mid + side * 0.6), bm.verts.new(mid - side * 0.6), bm.verts.new(tip)]
        bm.faces.new((v[0], v[1], v[2], v[3])); bm.faces.new((v[3], v[2], v[4]))
    o = mesh_obj('grass_clump', bm, M['grass'])
    c = bpy.data.collections.new('src_grass'); sc.collection.children.link(c)
    sc.collection.objects.unlink(o); c.objects.link(o)
    sc.view_layers[0].layer_collection.children[c.name].exclude = True
    return o

def scatter_grass(ground, clump, density=30.0):
    ng = bpy.data.node_groups.new('grass_scatter', 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = ng.nodes, ng.links
    gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput')
    dist = N.new('GeometryNodeDistributePointsOnFaces'); dist.inputs['Density'].default_value = density
    L.new(gi.outputs[0], dist.inputs['Mesh'])
    pos = N.new('GeometryNodeInputPosition'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0], sep.inputs[0])
    def m(op, a, b=None):
        n = N.new('ShaderNodeMath'); n.operation = op
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs[0]
    x = m('DIVIDE', m('SUBTRACT', sep.outputs[0], YARD[0]), YARD[2]); y = m('DIVIDE', m('SUBTRACT', sep.outputs[1], YARD[1]), YARD[3])
    r = m('SQRT', m('ADD', m('MULTIPLY', x, x), m('MULTIPLY', y, y)))
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.35; nz.inputs['Detail'].default_value = 6
    L.new(pos.outputs[0], nz.inputs['Vector'])
    r2 = m('ADD', r, m('MULTIPLY', m('SUBTRACT', nz.outputs['Fac'], 0.5), 0.45))
    # пруд — без травы
    px = m('DIVIDE', m('SUBTRACT', sep.outputs[0], -2.5), 3.6 * 1.12); py = m('DIVIDE', m('SUBTRACT', sep.outputs[1], -9.8), 2.4 * 1.12)
    pr = m('ADD', m('MULTIPLY', px, px), m('MULTIPLY', py, py))
    # проплешины
    nz2 = N.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 1.5; L.new(pos.outputs[0], nz2.inputs['Vector'])
    kill = m('MAXIMUM', m('MAXIMUM', m('LESS_THAN', r2, 1.04), m('LESS_THAN', pr, 1.0)), m('LESS_THAN', nz2.outputs['Fac'], 0.38))
    dele = N.new('GeometryNodeDeleteGeometry'); dele.domain = 'POINT'
    L.new(dist.outputs['Points'], dele.inputs['Geometry']); L.new(kill, dele.inputs['Selection'])
    oi = N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value = clump
    inst = N.new('GeometryNodeInstanceOnPoints')
    L.new(dele.outputs[0], inst.inputs['Points']); L.new(oi.outputs['Geometry'], inst.inputs['Instance'])
    rr = N.new('FunctionNodeRandomValue'); rr.data_type = 'FLOAT_VECTOR'
    rr.inputs['Max'].default_value = (0, 0, 6.283)
    L.new(rr.outputs['Value'], inst.inputs['Rotation'])
    rs = N.new('FunctionNodeRandomValue'); rs.data_type = 'FLOAT'; rs.inputs[2].default_value = 0.6; rs.inputs[3].default_value = 1.8
    L.new(rs.outputs[1], inst.inputs['Scale'])
    join = N.new('GeometryNodeJoinGeometry')
    L.new(gi.outputs[0], join.inputs[0]); L.new(inst.outputs[0], join.inputs[0])
    L.new(join.outputs[0], go.inputs[0])
    mod = ground.modifiers.new('grass', 'NODES'); mod.node_group = ng

def bamboo_clump(pos, n=22, H=11.0, seed=0):
    rnd = random.Random(seed); base = Vector(pos)
    bm = bmesh.new(); lb = bmesh.new()
    for k in range(n):
        a = rnd.uniform(0, 6.283); r0 = rnd.uniform(0, 0.9)
        d = Vector((math.cos(a), math.sin(a), 0)); h = H * rnd.uniform(0.7, 1.05); bend = rnd.uniform(1.0, 3.2)
        pts = [base + d * (r0 + bend * (t / 10) ** 2) + Vector((0, 0, h * t / 10)) for t in range(11)]
        tube(bm, pts, [0.06 - 0.03 * t / 10 for t in range(11)], 6)
        for t in range(4, 11):   # веточки с листьями
            p = pts[t]
            for j in range(5):
                aa = rnd.uniform(0, 6.283); dd = Vector((math.cos(aa), math.sin(aa), rnd.uniform(-0.6, 0.1))).normalized()
                q = p + dd * rnd.uniform(0.2, 0.7)
                sd = dd.cross(Vector((0, 0, 1))).normalized() * 0.035
                lb.faces.new((lb.verts.new(q - sd), lb.verts.new(q + sd), lb.verts.new(q + dd * 0.28 + Vector((0, 0, -0.08)))))
    o = mesh_obj('bamboo_culms', bm, M['bamboo_culm'])
    for p in o.data.polygons: p.use_smooth = True
    mesh_obj('bamboo_leaves', lb, M['bamboo_leaf'])

M['bamboo_culm'] = leaf_mat('bamboo_culm', (0.30, 0.36, 0.10), 0.05)
M['bamboo_leaf'] = leaf_mat('bamboo_leaf', (0.18, 0.30, 0.06), 0.4)
for i, p in enumerate(((-13.5, 6.0), (8.5, 13.5), (15.5, 3.0), (-11.0, 13.5))):
    bamboo_clump((*p, 0), seed=40 + i)
for i, p in enumerate(((-12.5, 0.5), (-12.0, -2.2), (9.0, 11.0), (11.5, 10.0), (12.8, 7.4), (-7.5, 11.5),
                       (-8.0, -6.5),)):
    banana((*p, 0), H=random.uniform(1.6, 2.6), seed=60 + i)

# ---------------------------------------------------------------- свет: сумерки, восходящая луна в затмении
w = bpy.data.worlds.new('world'); sc.world = w; w.use_nodes = True
wn = w.node_tree.nodes; wl = w.node_tree.links
env = wn.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load(os.path.join(A, arg('--hdri', 'qwantani_dusk_2'), arg('--hdri', 'qwantani_dusk_2') + '.exr'))
mpw = wn.new('ShaderNodeMapping'); tcw = wn.new('ShaderNodeTexCoord')
mpw.inputs['Rotation'].default_value = (0, 0, math.radians(arg('--hdri_rot', 200.0)))
wl.new(tcw.outputs['Generated'], mpw.inputs['Vector']); wl.new(mpw.outputs['Vector'], env.inputs['Vector'])
wl.new(env.outputs['Color'], wn['Background'].inputs['Color'])
wn['Background'].inputs['Strength'].default_value = arg('--sky', 1.0)

moon = bpy.data.lights.new('moon', 'SUN'); moon.energy = arg('--moon', 0.25); moon.color = (0.62, 0.72, 1.0)
moon.angle = math.radians(1.5)
mo = bpy.data.objects.new('moon', moon); link(mo)
mo.rotation_euler = (math.radians(62), 0, math.radians(-120))

# ---------------------------------------------------------------- изометрическая камера
cam = bpy.data.cameras.new('cam'); cam.type = 'ORTHO'; cam.ortho_scale = arg('--ortho', 28.0)
co = bpy.data.objects.new('cam', cam); link(co); sc.camera = co
pitch, yaw = math.radians(arg('--pitch', 50.0)), math.radians(arg('--yaw', 38.0))
co.rotation_euler = (pitch, 0, yaw)
target = Vector((arg('--tx', 0.5), arg('--ty', 3.0), 0.0))
fwd = co.rotation_euler.to_matrix() @ Vector((0, 0, -1))
co.location = target - fwd * 40
cam.clip_end = 200

sc.use_nodes = True
ct = sc.node_tree; rl = ct.nodes.new('CompositorNodeRLayers'); comp = ct.nodes['Composite'] if 'Composite' in ct.nodes else ct.nodes.new('CompositorNodeComposite')
gl = ct.nodes.new('CompositorNodeGlare'); gl.glare_type = 'BLOOM'; gl.quality = 'HIGH'
try:
    gl.threshold = 1.5; gl.size = 6; gl.mix = -0.75
except Exception:
    pass
ct.links.new(rl.outputs['Image'], gl.inputs['Image']); ct.links.new(gl.outputs['Image'], comp.inputs['Image'])

scatter_grass(GROUND, grass_clump(), arg('--grass', 40.0))

if SAVE:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(SAVE))
sc.render.filepath = os.path.abspath(OUT)
bpy.ops.render.render(write_still=True)
print('RENDERED', OUT)
