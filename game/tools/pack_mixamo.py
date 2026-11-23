# Собирает персонажа Mixamo (Y Bot) и анимации (FBX «Without Skin») в один GLB для игры.
# Запуск: blender -b -P pack_mixamo.py -- <папка с fbx> <out.glb>
# В папке: ybot.fbx (персонаж) и <имя>.fbx — анимации; имя файла становится именем клипа.
import bpy, os, sys
argv = sys.argv[sys.argv.index('--') + 1:]
SRC, OUT = argv[0], argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)

bpy.ops.import_scene.fbx(filepath=os.path.join(SRC, 'ybot.fbx'), automatic_bone_orientation=False)
arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
arm.name = 'ybot'
if arm.animation_data and arm.animation_data.action:
    arm.animation_data.action = None
arm.animation_data_create()

# пальцы и «концевые» кости анимируются мелко — их дорожки убираем, чтобы файл был легче
def keep(path):
    return not any(f in path for f in ('Thumb', 'Index', 'Middle', 'Ring', 'Pinky', '_End'))

names = sorted(f[:-4] for f in os.listdir(SRC) if f.endswith('.fbx') and f != 'ybot.fbx')
for name in names:
    before = set(bpy.data.objects)
    acts_before = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=os.path.join(SRC, name + '.fbx'), automatic_bone_orientation=False)
    new_objs = [o for o in bpy.data.objects if o not in before]
    new_acts = [a for a in bpy.data.actions if a not in acts_before]
    if not new_acts:
        print('NO ACTION', name)
    else:
        act = new_acts[0]
        act.name = name
        for fc in list(act.fcurves):
            if not keep(fc.data_path):
                act.fcurves.remove(fc)
        act.use_fake_user = True
        tr = arm.animation_data.nla_tracks.new(); tr.name = name
        st = tr.strips.new(name, int(act.frame_range[0]), act); st.mute = False
        for a in new_acts[1:]:
            bpy.data.actions.remove(a)
    for o in new_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    print('ACTION', name)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_animation_mode='NLA_TRACKS',
                          export_optimize_animation_size=True, export_force_sampling=True, export_frame_step=2,
                          export_materials='EXPORT', export_yup=True, export_def_bones=True)
print('PACKED', OUT, os.path.getsize(OUT))
