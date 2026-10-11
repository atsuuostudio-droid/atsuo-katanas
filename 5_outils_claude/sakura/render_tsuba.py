import bpy, sys, math
sys.path.insert(0,'/home/claude/sakura/scripts')
from render_util import *
bpy.ops.wm.open_mainfile(filepath='/home/claude/sakura/katana_sakura_build.blend')
setup_render((1100,1300),48)
bpy.context.scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.30,0.32,0.36,1)
for m in bpy.data.materials:
    bs=m.node_tree.nodes['Principled BSDF']
    if m.name=='lame':
        nt=m.node_tree; bs.inputs['Metallic'].default_value=0.35
        nt.links.new(bs.inputs['Base Color'].links[0].from_node.outputs[0],bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value=0.35
    if m.name in ('tsuba','rim'): bs.inputs['Roughness'].default_value=0.22
    if m.name=='tsuba': bs.inputs['Metallic'].default_value=0.0
cam((0.13,-0.20,0.09),(0.20,0,0.056),lens=60,name='t1'); render('/home/claude/sakura/renders/tsuba_3q.png')
bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y=1300,1100
cam((0.20,-0.07,0.13),(0.20,0,0.045),lens=60,name='t2'); render('/home/claude/sakura/renders/tsuba_bord.png')
