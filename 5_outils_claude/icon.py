import bpy, sys
sys.path.insert(0,'/home/claude/kin/scripts')
from render_util import *
import math
bpy.ops.wm.open_mainfile(filepath='/home/claude/kin/katana_kin_build.blend')
setup_render((1600,1600),32)
bpy.context.scene.render.film_transparent=True
o=bpy.data.objects['katana_kin']

from mathutils import Matrix; o.data.transform(Matrix.Rotation(math.radians(35),4,'Y')); o.data.update()
cam((0,-1.6,0.07),(0,0,0.07),ortho=1.25,name='side'); render('/home/claude/kin/renders/icon_raw.png')
