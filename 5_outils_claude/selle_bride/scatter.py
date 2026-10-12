import bpy, os, numpy as np
from PIL import Image, ImageDraw
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=os.environ['GLB'])
o=[o for o in bpy.data.objects if o.type=='MESH'][0]
M=np.array(o.matrix_world)
V=np.array([v.co[:] for v in o.data.vertices]); V=(np.c_[V,np.ones(len(V))]@M.T)[:,:3]
np.save(os.environ['OUT']+'.npy',V)
im=Image.new('RGB',(1500,520),'white'); d=ImageDraw.Draw(im)
for k,(a,b,name) in enumerate([(0,2,'X vers droite / Z haut'),(0,1,'X vers droite / Y haut'),(1,2,'Y vers droite / Z haut')]):
    ox=k*500+250; oy=260
    for v in V[::3]: d.point((ox+v[a]*230, oy-(v[b]-(0.45 if b==2 else 0))*230),fill=(0,0,0))
    for t in np.arange(-1,1.01,0.25):
        d.text((ox+t*230-8,500),'%.2f'%t,fill=(200,0,0)); d.line([(ox+t*230,490),(ox+t*230,495)],fill=(200,0,0))
    d.text((ox-240,5),name,fill=(0,0,200))
im.save(os.environ['OUT'])
