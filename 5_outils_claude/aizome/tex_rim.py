# Bordure du tsuba Aizome : anneau de laiton vieilli, lisse (pas de relief), martelé et patiné dans les creux.
import numpy as np, cv2, sys
sys.path.insert(0,'/home/claude/aizome2/scripts')
from tex_common import *
W,H=1024,512
rng=np.random.default_rng(8)
n1=cv2.GaussianBlur(rng.normal(0,1,(H,W)).astype(np.float32),(0,0),18); n1/=n1.std()
n2=cv2.GaussianBlur(rng.normal(0,1,(H,W)).astype(np.float32),(0,0),2.5); n2/=n2.std()
v=(np.arange(H,dtype=np.float32)+0.5)/H
edge=np.exp(-((np.minimum(v,1-v))/0.06)**2)[:,None]          # bords intérieurs plus sombres (patine)
wear=np.clip(0.5+0.3*n1,0,1)
col=np.array([182,138,62],np.float32)/255*(0.85+0.2*wear[...,None])*(1-0.45*edge[...,None])
col=col*(1+0.05*n2[...,None])
save_rgb('/home/claude/aizome2/tex/rim_d.png',np.clip(col,0,1))
save_rgb('/home/claude/aizome2/tex/rim_n.png',normal_from_height(n2*0.08,1.0))
save_gray('/home/claude/aizome2/tex/rim_s.png',np.clip(0.85-0.3*edge+0.05*n2,0,1))
np.save('/home/claude/aizome2/tex/rim_h.npy',np.zeros((128,1024),np.float32))
print('rim ok')
