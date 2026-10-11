import bpy, sys
sys.path.insert(0,'/home/claude/kin/scripts')
from render_util import *
bpy.ops.wm.open_mainfile(filepath=sys.argv[-2])
tag=sys.argv[-1]
setup_render((1600,700),32)
cam((0,-1.6,0.07),(0,0,0.07),ortho=1.05,name='side'); render(f'/home/claude/kin/renders/{tag}_side.png')
setup_render((1400,900),48)
cam((0.50,-0.22,0.13),(0.33,0,0.055),lens=50,name='c2'); render(f'/home/claude/kin/renders/{tag}_hilt.png')
cam((0.345,-0.16,0.06),(0.345,0,0.058),lens=60,name='c3'); render(f'/home/claude/kin/renders/{tag}_side_hilt.png')
