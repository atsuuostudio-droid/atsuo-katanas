import bpy, sys, math
sys.path.insert(0,'/home/claude/kumo/scripts')
from render_util import *
bpy.ops.wm.open_mainfile(filepath='/home/claude/kumo/katana_kumo_build.blend')
setup_render((2000,640),24)
for m in bpy.data.materials:
    if m.name=='lame': m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=0.35
bpy.context.scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.30,0.32,0.36,1)
cam((0.0,-1.6,0.06),(0.0,0,0.06),ortho=1.02,name='side'); render('/home/claude/kumo/renders/kumo_side.png')
bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y=1400,800
cam((0.30,-0.42,0.16),(0.30,0,0.055),lens=50,name='mont'); render('/home/claude/kumo/renders/kumo_monture.png')
cam((-0.40,-0.30,0.12),(-0.40,0,0.075),lens=50,name='pointe'); render('/home/claude/kumo/renders/kumo_pointe.png')
