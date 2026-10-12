import bpy, sys, math
sys.path.insert(0,'/home/claude/tanegashima/scripts')
from render_util import *
import os; f,out=os.environ['GLB'],os.environ['OUT']
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=f)
setup_render((500,500),12)
bpy.context.scene.view_settings.view_transform='Standard'
from PIL import Image
ims=[]
for i,(loc,tg) in enumerate([((0,-3,0.45),(0,0,0.45)),((3,0,0.45),(0,0,0.45)),((0,0.001,3),(0,0,0)),((2.2,-2.2,1.8),(0,0,0.4))]):
    cam(loc,tg,ortho=1.3,name='c%d'%i); p='/tmp/v%d.png'%i; render(p); ims.append(Image.open(p).convert('RGB'))
W=Image.new('RGB',(2000,500),'white')
for i,im in enumerate(ims): W.paste(im,(i*500,0))
W.save(out)
