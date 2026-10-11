import bpy, sys, numpy as np
sys.path.insert(0,'/home/claude/kumo/scripts')
from load_sollumz import load
bpy.ops.wm.open_mainfile(filepath='/home/claude/kumo/out/Atsuo_Katana_Kumo.blend'); load()
for m in bpy.data.materials:
    print(m.name, m.sollum_type, [(n.image.name,n.texture_properties.embedded) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image])
src=open('/home/user/atsuo-katanas/3_scripts_blender/katana_comme_reference.py').read()
ns={'np':np}; exec(src[src.index('def points_monde'):src.index('# ---------- 0.')],ns)
mo=bpy.data.objects['w_me_katana_kumo.model']
P=ns['points_monde'](mo)
c1,u1,d1=ns['repere_katana'](P)
R=np.load('/home/claude/kumo/ref/noir_pts.npy')
c0,u0,d0=ns['repere_katana'](R)
print('Kumo tsuba',c1.round(4),'axe',u1.round(3),'dos',d1.round(3))
print('Noir tsuba',c0.round(4),'axe',u0.round(3),'dos',d0.round(3))
print('ecart tsuba cm %.2f  axe deg %.2f  dos deg %.2f'%(np.linalg.norm(c1-c0)*100,np.degrees(np.arccos(np.clip(u1@u0,-1,1))),np.degrees(np.arccos(np.clip(d1@d0,-1,1)))))
print('bbox kumo',P.min(0).round(3),P.max(0).round(3)); print('bbox noir',R.min(0).round(3),R.max(0).round(3))
