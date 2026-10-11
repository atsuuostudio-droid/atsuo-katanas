import bpy, sys
sys.path.insert(0,'/home/claude/kin/scripts')
from load_sollumz import load
bpy.ops.wm.open_mainfile(filepath='/home/claude/kin/out/Atsuo_Katana_Kin.blend'); load()
for m in bpy.data.materials:
    if m.sollum_type!='sollumz_material_shader': continue
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image: n.texture_properties.embedded=True
    print(m.name,[n.texture_properties.embedded for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image])
d=bpy.data.objects['w_me_katana_kin']; mo=bpy.data.objects['w_me_katana_kin.model']
print('drawable loc',tuple(d.location),'model loc',tuple(mo.location), 'scene', bpy.context.scene.name, [s.name for s in bpy.data.scenes])
print('tris', sum(len(p.vertices)-2 for p in mo.data.polygons))
bpy.ops.wm.save_mainfile()
