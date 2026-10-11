# Bord du tsuba Shikkoku : fer noir brut martelé, piqué, arêtes usées plus claires.
import numpy as np, cv2, sys
sys.path.insert(0,'/home/claude/shikkoku/scripts')
from tex_common import *
from iron_common import hammered, render_iron
from rim_params import *
rng=np.random.default_rng(21)
PX=0.00003; GW=int(round(TILE_W/PX)); GH=int(round(BAND_W/PX)); PXMM=1/(PX*1000)
H=hammered((GH,GW),PXMM*1.6,rng,pits=1.4)
# gros coups de marteau + entailles d'usure
for k in range(40):
    x=rng.uniform(0,GW); y=rng.uniform(0,GH); rr=rng.uniform(0.8,2.2)*PXMM
    m=np.zeros((GH,GW),np.float32); cv2.ellipse(m,(int(x),int(y)),(int(rr*1.6),int(rr)),rng.uniform(0,180),0,360,1.0,-1,cv2.LINE_AA)
    H-=cv2.GaussianBlur(m,(0,0),rr*0.4)*0.05
H=H+np.roll(H,GW//2,axis=1)*0 # (raccord : bruit indépendant, tuile répétée 4 fois)
c,nrm8,spec=render_iron(H,PXMM*1.6,base=(26,26,30),hi=(100,100,108),lo=(5,5,7),nstrength=1.1)
OW,OH=1024,512
save_rgb('/home/claude/shikkoku/tex/rim_d.png',cv2.resize(c,(OW,OH),interpolation=cv2.INTER_AREA))
save_rgb('/home/claude/shikkoku/tex/rim_n.png',cv2.resize(nrm8,(OW,OH),interpolation=cv2.INTER_AREA))
save_gray('/home/claude/shikkoku/tex/rim_s.png',cv2.resize(spec,(512,256),interpolation=cv2.INTER_AREA))
np.save('/home/claude/shikkoku/tex/rim_h.npy',np.zeros((128,1024),np.float32))
print('rim fer martelé ok')
