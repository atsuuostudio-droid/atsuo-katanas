import bpy, sys, numpy as np
sys.path.insert(0,'/home/claude/kurogane/scripts')
from load_sollumz import load
bpy.ops.wm.open_mainfile(filepath='/home/claude/kurogane/out/Atsuo_Katana_Kurogane.blend'); load()
src=open('/home/user/atsuo-katanas/3_scripts_blender/katana_comme_reference.py').read()
ns={'np':np}; exec(src[src.index('def points_monde'):src.index('# ---------- 0.')],ns)
mo=bpy.data.objects['w_me_katana_kurogane.model']
P=ns['points_monde'](mo)
R=np.load('/home/claude/kurogane/ref/noir_pts.npy'); c0,u0,d0=ns['repere_katana'](R)
c=P.mean(0); a=np.linalg.svd(P-c,full_matrices=False)[2][0]; t=(P-c)@a
bins=np.linspace(t.min(),t.max(),241); w=np.zeros(240)
for i in range(240):
    s=(t>=bins[i])&(t<bins[i+1])
    if s.sum()>=3: Q=P[s]-c; Q=Q-np.outer(Q@a,a); w[i]=np.ptp(Q,axis=0).max()
k=int(np.argmax(w)); ts=(bins[k]+bins[k+1])/2
if (t.max()-ts)<(ts-t.min()): a=-a; ts=-ts
blade=P[(P-c)@a>ts+0.05]
nb=np.linalg.svd(blade-blade.mean(0),full_matrices=False)[2]
wdir=nb[1]                      # largeur de lame
guard_c=c+a*ts
print('garde',guard_c.round(4),'axe',a.round(3)); print('noir tsuba',c0.round(4),'axe',u0.round(3),'dos',d0.round(3))
print('ecart garde/tsuba cm %.2f  axe deg %.2f  plan de lame vs noir deg %.2f'%(np.linalg.norm(guard_c-c0)*100,np.degrees(np.arccos(np.clip(a@u0,-1,1))),np.degrees(np.arccos(np.clip(abs(wdir@d0),-1,1)))))
print('bbox',P.min(0).round(3),P.max(0).round(3))
