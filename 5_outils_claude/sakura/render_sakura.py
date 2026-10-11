import bpy, sys, math
sys.path.insert(0,'/home/claude/sakura/scripts')
from render_util import *
bpy.ops.wm.open_mainfile(filepath='/home/claude/sakura/katana_sakura_build.blend')
setup_render((2000,640),24)
for m in bpy.data.materials:
    if m.name=='lame':
        nt=m.node_tree; bs=nt.nodes['Principled BSDF']; bs.inputs['Metallic'].default_value=0.35
        nt.links.new(bs.inputs['Base Color'].links[0].from_node.outputs[0],bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value=0.35
bpy.context.scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.30,0.32,0.36,1)
cam((0.0,-1.6,0.06),(0.0,0,0.06),ortho=1.02,name='side'); render('/home/claude/sakura/renders/sakura_side.png')
bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y=1400,800
cam((0.30,-0.42,0.16),(0.30,0,0.055),lens=50,name='mont'); render('/home/claude/sakura/renders/sakura_monture.png')
cam((-0.40,-0.30,0.12),(-0.40,0,0.075),lens=50,name='pointe'); render('/home/claude/sakura/renders/sakura_pointe.png')
