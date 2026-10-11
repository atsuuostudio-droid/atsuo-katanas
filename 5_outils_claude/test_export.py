import bpy, sys
sys.path.insert(0,'/home/claude/kin/scripts')
from load_sollumz import load
bpy.ops.wm.open_mainfile(filepath='/home/claude/kin/out/Atsuo_Katana_Kin.blend'); load()
bpy.ops.object.select_all(action='SELECT')
r=bpy.ops.sollumz.export_assets(directory='/home/claude/kin/xmltest/', direct_export=True, use_custom_settings=True, target_formats={'CWXML'}, target_versions={'GEN8'})
print('EXPORT',r)
