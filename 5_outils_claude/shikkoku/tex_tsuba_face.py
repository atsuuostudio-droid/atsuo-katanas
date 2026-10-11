# Face du tsuba Shikkoku AJOURÉ (sukashi) : fer noir forgé martelé, arêtes arrondies et usées autour des jours,
# perles le long des crêtes de vague. Le masque (tsuba_mask.py) est aussi utilisé par build pour percer la géométrie.
# UV : u=0.5+0.5*Y/TRY, v=0.5+0.5*(Z-zm)/TRZ  (ligne 0 de l'image = v=1). Coins = fer sombre uni (seppa, parois).
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/shikkoku/scripts')
from tex_common import *
from iron_common import hammered, render_iron
from rim_params import TRY, TRZ, D0
import tsuba_mask as TM
rng=np.random.default_rng(5)
S=2048; RR=S/2
PXMM=RR/(TRY*1000)
m,rho,beads=TM.build(return_parts=True)
MS=m.shape[0]
yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
u=(xx+0.5)/S; v=1-(yy+0.5)/S
xn=(2*u-1)*TRY/(TRY+D0); yn=(2*v-1)*TRZ/(TRZ+D0)
mapx=((xn+1)/2*MS-0.5).astype(np.float32); mapy=((1-yn)/2*MS-0.5).astype(np.float32)
metal=cv2.remap(m.astype(np.float32),mapx,mapy,cv2.INTER_LINEAR,borderValue=1.0)
inside=(xn**2+yn**2)<1.0
mb=(metal>0.5).astype(np.uint8)
dist=cv2.distanceTransform(mb,cv2.DIST_L2,5)/PXMM          # mm jusqu'au jour le plus proche
dout=cv2.distanceTransform(1-mb,cv2.DIST_L2,5)/PXMM
# relief : martelage + arrondi des arêtes (0,5 mm) + perles
H=hammered((S,S),PXMM*1.0,rng,pits=0.6)
R_ED=0.40
H+=0.12*np.sqrt(np.clip(dist/R_ED,0,1))-0.12
bead=np.zeros((S,S),np.float32)
for (bx,by,br) in beads:
    cx=(bx*(TRY+D0)/TRY+1)/2*S; cy=(1-by*(TRZ+D0)/TRZ)/2*S; r=br*(TRY+D0)/TRY*S/2
    x1,x2=int(cx-r-3),int(cx+r+3); y1,y2=int(cy-r*1.1-3),int(cy+r*1.1+3)
    X,Y=np.meshgrid(np.arange(x1,x2)+0.5-cx,np.arange(y1,y2)+0.5-cy)
    d=np.sqrt(X*X+Y*Y)/r
    bead[y1:y2,x1:x2]=np.maximum(bead[y1:y2,x1:x2],np.sqrt(np.clip(1-d*d,0,1)))
H+=0.22*bead
# léger creux (gravure) au milieu des bandes de vague larges : accentue le mouvement
pass
c,nrm8,spec=render_iron(H,PXMM*1.0,base=(22,22,26),hi=(118,118,126),lo=(3,3,5),nstrength=1.0)
# arêtes usées plus claires, fond des jours (parois) sombres
wear=np.exp(-(dist/0.12)**2)*(mb>0)
c=c+(np.array([96,96,104],np.float32)/255-c)*(0.35*wear)[...,None]
spec=np.clip(spec+0.20*wear,0,1)
# perles : sommet poli
c=c+(np.array([120,120,128],np.float32)/255-c)*(0.45*np.clip(bead-0.6,0,1)/0.4)[...,None]
# hors métal (jours) : couleur de la paroi pour éviter les bavures de mipmap
wall=np.array([30,30,34],np.float32)/255
c[mb==0]=wall; spec[mb==0]=0.6; nrm8[mb==0]=(128,128,255)
# coins : fer sombre uni (seppa, parois, menuki)
q=int(S*0.11); corner=np.zeros((S,S),bool)
corner[:q,:q]=corner[:q,S-q:]=corner[S-q:,:q]=corner[S-q:,S-q:]=True
c[corner]=np.array([40,40,46],np.float32)/255; spec[corner]=0.7; nrm8[corner]=(128,128,255)
save_rgb('/home/claude/shikkoku/tex/tsuba_d.png',c)
save_rgb('/home/claude/shikkoku/tex/tsuba_n.png',nrm8)
save_gray('/home/claude/shikkoku/tex/tsuba_s.png',spec)
np.save('/home/claude/shikkoku/tex/tsuba_mask.npy',m)
prev=(np.clip(c,0,1)*255).astype(np.uint8); prev[~inside]=(90,60,60)
cv2.imwrite('/home/claude/shikkoku/renders/p_tsuba_face.png',cv2.cvtColor(cv2.resize(prev,(900,900),interpolation=cv2.INTER_AREA),cv2.COLOR_RGB2BGR))
print('tsuba ajouré ok, perles',len(beads))
