import bpy, sys, math, mathutils
sys.path.insert(0,'/home/claude/kin/scripts')
from render_util import cam
bpy.ops.wm.open_mainfile(filepath=sys.argv[-2]); tag=sys.argv[-1]
sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading; sh.light='STUDIO'; sh.color_type='TEXTURE'; sh.show_backface_culling=True
sh.background_type='VIEWPORT' if hasattr(sh,'background_type') else None
sc.render.resolution_x, sc.render.resolution_y = 900, 600
sc.world = sc.world or bpy.data.worlds.new('w')
views={
 'pommeau':((0.62,-0.02,0.07),(0.49,0,0.062),35),
 'tsuba_avant':((0.05,-0.12,0.12),(0.196,0,0.055),35),
 'tsuba_arriere':((0.32,0.10,0.10),(0.196,0,0.056),35),
 'poignee_dessus':((0.35,-0.03,0.20),(0.35,0,0.058),35),
 'poignee_cote_y':((0.35,0.17,0.06),(0.35,0,0.058),35),
 'lame_cote_a':((-0.17,-0.9,0.09),(-0.17,0,0.08),35),
 'lame_cote_b':((-0.17,0.9,0.09),(-0.17,0,0.08),35),
}
for n,(loc,tg,lens) in views.items():
    cam(loc,tg,lens=lens,name=n); sc.render.filepath=f'/home/claude/kin/renders/cull_{tag}_{n}.png'; bpy.ops.render.render(write_still=True)
