import bpy, sys
sys.path.insert(0,'/home/claude/kumo/scripts')
from load_sollumz import load
bpy.ops.wm.open_mainfile(filepath='/home/claude/kumo/out/Atsuo_Katana_Kumo.blend'); load()
bpy.ops.object.select_all(action='SELECT')
r=bpy.ops.sollumz.export_assets(directory='/home/claude/kumo/xmltest/', direct_export=True, use_custom_settings=True, target_formats={'CWXML'}, target_versions={'GEN8'})
print('EXPORT',r)
