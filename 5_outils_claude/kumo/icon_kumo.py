import bpy, sys
sys.path.insert(0,'/home/claude/kumo/scripts')
from render_util import *
import math
bpy.ops.wm.open_mainfile(filepath='/home/claude/kumo/katana_kumo_build.blend')
setup_render((1600,1600),32)
bpy.context.scene.render.film_transparent=True
o=bpy.data.objects['katana_kumo']
for m in bpy.data.materials:
    if m.name=='lame': m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=0.35

from mathutils import Matrix; o.data.transform(Matrix.Rotation(math.radians(35),4,'Y')); o.data.update()
cam((0,-1.6,0.07),(0,0,0.07),ortho=1.25,name='side'); render('/home/claude/kumo/renders/icon_raw.png')
