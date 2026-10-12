import bpy, sys
sys.path.insert(0,'/home/claude/tanegashima/scripts')
from load_sollumz import load
bpy.ops.wm.read_factory_settings(use_empty=True); load()
r=bpy.ops.sollumz.import_assets(directory='/home/claude/tanegashima/ref/', files=[{'name':'w_ar_musket.ydr.xml'}])
print('IMPORT',r)
for o in bpy.data.objects:
    print(o.name,o.type,o.sollum_type,o.parent.name if o.parent else None,[m.type for m in o.modifiers] if o.type=='MESH' else '', list(o.vertex_groups.keys())[:12] if o.type=='MESH' else '')
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/tanegashima/musket_import.blend')
