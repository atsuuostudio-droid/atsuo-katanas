import bpy, sys, math
sys.path.insert(0,'/home/claude/tanegashima/scripts')
from render_util import *
from mathutils import Matrix
bpy.ops.wm.open_mainfile(filepath='/home/claude/tanegashima/tanegashima_build.blend')
setup_render((1600,1600),32); bpy.context.scene.render.film_transparent=True
o=bpy.data.objects['tanegashima']
o.data.transform(Matrix.Translation((-0.19,0,0.05))); o.data.transform(Matrix.Rotation(math.radians(-30),4,'Y'))
cam((0,-2.2,0),(0,0,0),ortho=1.25,name='side'); render('/home/claude/tanegashima/renders/icon_raw.png')
