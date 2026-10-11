import bpy, sys
sys.path.insert(0,'/home/claude/kumo/scripts')
from load_sollumz import load
bpy.ops.wm.open_mainfile(filepath='/home/claude/kumo/out/Atsuo_Katana_Kumo.blend'); load()
src=open('/home/user/atsuo-katanas/3_scripts_blender/katana_comme_machette.py').read().replace('NOM_OBJET = "w_me_katana_XXX.model"','NOM_OBJET = "w_me_katana_kumo.model"')
exec(compile(src,'katana_comme_machette.py','exec'))
bpy.ops.wm.save_mainfile()
