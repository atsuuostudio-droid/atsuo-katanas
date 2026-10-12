import bpy, sys
sys.path.insert(0,'/home/claude/tanegashima/scripts')
from render_util import *
bpy.ops.wm.open_mainfile(filepath='/home/claude/tanegashima/tanegashima_build.blend')
setup_render((2400,800),24)
bpy.context.scene.world.node_tree.nodes['Background'].inputs[0].default_value=(0.75,0.75,0.76,1)
for o in bpy.data.objects:
    if o.type=='LIGHT': o.data.energy*=0.5
bpy.context.scene.view_settings.view_transform='Standard'
cam((0.19,-2.2,-0.05),(0.19,0,-0.05),ortho=1.42,name='side'); render('/home/claude/tanegashima/renders/tane_side.png')
bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y=1400,900
cam((-0.05,-0.42,0.12),(-0.12,0,-0.03),lens=50,name='platine'); render('/home/claude/tanegashima/renders/tane_platine.png')
