import bpy, sys
sys.path.insert(0,'/home/claude/sakura/scripts')
from load_sollumz import load
bpy.ops.wm.open_mainfile(filepath='/home/claude/sakura/out/Atsuo_Katana_Sakura.blend'); load()
bpy.ops.object.select_all(action='SELECT')
r=bpy.ops.sollumz.export_assets(directory='/home/claude/sakura/xmltest/', direct_export=True, use_custom_settings=True, target_formats={'CWXML'}, target_versions={'GEN8'})
print('EXPORT',r)
