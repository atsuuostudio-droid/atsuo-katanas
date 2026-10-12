import bpy, sys
sys.path.insert(0,'/home/claude/tanegashima/scripts')
from load_sollumz import load
bpy.ops.wm.open_mainfile(filepath='/home/claude/tanegashima/out/Atsuo_Tanegashima_w_ar_musket.blend'); load()
print('images',[ (i.name,i.users) for i in bpy.data.images])
bpy.ops.object.select_all(action='SELECT')
r=bpy.ops.sollumz.export_assets(directory='/home/claude/tanegashima/xmltest/', direct_export=True, use_custom_settings=True, target_formats={'CWXML'}, target_versions={'GEN8'})
print('EXPORT',r)
