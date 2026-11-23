# Автоматический риг модели из TRELLIS (картинка -> 3D) скелетом Mixamo (Y Bot): к модели подходят все клипы Mixamo.
# Запуск: blender -b -P autorig.py -- <ybot_anims.glb> <model.glb> <out.glb> [угол рук от вертикали, град; 18]
# Шаги: 1) Y Bot ставится в позу A (руки опущены), модель выравнивается по нему; 2) веса переносятся с тела Y Bot на
# ближайшие точки модели (сетки TRELLIS не замкнуты — «тепловые» веса Blender на них не работают); 3) обратный скиннинг
# переводит модель в позу T (позу покоя Mixamo); 4) привязка к скелету и экспорт GLB.
import bpy, sys, math
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index('--') + 1:]
YBOT, MODEL, OUT = argv[0], argv[1], argv[2]
ARM_DEG = float(argv[3]) if len(argv) > 3 else 18.0
bpy.ops.wm.read_factory_settings(use_empty=True)

bpy.ops.import_scene.gltf(filepath=YBOT)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
ymeshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
body = next(o for o in ymeshes if 'Surface' in o.name)
if arm.animation_data:
    arm.animation_data.action = None
    for t in list(arm.animation_data.nla_tracks): arm.animation_data.nla_tracks.remove(t)
for a in list(bpy.data.actions): bpy.data.actions.remove(a)
for pb in arm.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()

find = lambda suf: next(b.name for b in arm.pose.bones if b.name.endswith(suf))
W = arm.matrix_world
bw = lambda n, tail=False: W @ (arm.pose.bones[n].tail if tail else arm.pose.bones[n].head)
top = bw(find('HeadTop_End')).z
foot = min(bw(find('LeftToe_End')).z, bw(find('LeftFoot')).z) - 0.02
H = top - foot

# 1. поза A на исходном скелете
def swing_down(name):
    pb = arm.pose.bones[name]
    side = 1.0 if bw(name, True).x > bw(name).x else -1.0
    head = pb.head.copy(); d = (pb.tail - pb.head).normalized()
    t = W.to_3x3().inverted() @ Vector((side * math.sin(math.radians(ARM_DEG)), 0.0, -math.cos(math.radians(ARM_DEG))))
    q = d.rotation_difference(t.normalized())
    pb.matrix = Matrix.Translation(head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()
swing_down(find('LeftArm')); swing_down(find('RightArm'))

# модель: сводим трансформации, масштаб по росту, выравнивание по тазу и ступням
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=MODEL)
new = [o for o in bpy.data.objects if o not in before]
mesh = next(o for o in new if o.type == 'MESH')
mw = mesh.matrix_world.copy(); mesh.parent = None; mesh.matrix_world = mw
for o in new:
    if o is not mesh: bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT'); mesh.select_set(True); bpy.context.view_layer.objects.active = mesh
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
co = [v.co for v in mesh.data.vertices]
mn = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
mx = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
s = H / (mx.z - mn.z); hip = bw(find('Hips'))
mesh.scale = (s, s, s)
mesh.location = Vector((hip.x - (mn.x + mx.x) / 2 * s, hip.y - (mn.y + mx.y) / 2 * s, foot - mn.z * s))
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# 2. перенос весов с тела Y Bot (в позе A)
for g in body.vertex_groups:
    if g.name not in mesh.vertex_groups: mesh.vertex_groups.new(name=g.name)
dt = mesh.modifiers.new('wt', 'DATA_TRANSFER'); dt.object = body
dt.use_vert_data = True; dt.data_types_verts = {'VGROUP_WEIGHTS'}; dt.vert_mapping = 'POLYINTERP_NEAREST'
dt.layers_vgroup_select_src = 'ALL'; dt.layers_vgroup_select_dst = 'NAME'
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.modifier_apply(modifier=dt.name)
nw = sum(1 for v in mesh.data.vertices if any(g.weight > 0.01 for g in v.groups))
print('WEIGHTED', nw, 'of', len(mesh.data.vertices))

# 3. сглаживание весов (мягче переходы рука/тело) и поза A как поза покоя: клипы Mixamo задают локальные повороты костей
# целиком, поэтому привязка в позе A даёт тот же результат, что и в позе T, но без растяжений в покое
bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=3)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT'); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode='OBJECT')

# 4. привязка и экспорт (без мешей Y Bot)
for o in ymeshes: bpy.data.objects.remove(o, do_unlink=True)
mesh.parent = arm; mesh.matrix_parent_inverse = arm.matrix_world.inverted()
am = mesh.modifiers.new('Armature', 'ARMATURE'); am.object = arm
bpy.ops.export_scene.gltf(filepath=OUT, use_selection=False, export_skins=True, export_format='GLB', export_animations=False,
                          export_yup=True, export_materials='EXPORT', export_image_format='JPEG', export_jpeg_quality=88)
print('RIGGED', OUT)
