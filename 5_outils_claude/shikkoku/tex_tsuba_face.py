# Face du tsuba Shikkoku : fer noir martelé, face creusée sculptée d'arcs de vagues emboîtés (seigaiha) en couronne.
# Coins = fer sombre uni (seppa, menuki, bagues).
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/shikkoku/scripts')
from tex_common import *
from iron_common import hammered, render_iron
from rim_params import TRY, D0
rng=np.random.default_rng(5)
S=2048; c0=S/2; RR=S/2
PXMM=RR/(TRY*1000)                       # pixels par mm
yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
r=np.sqrt((xx-c0)**2+(yy-c0)**2)/RR
th=np.arctan2(yy-c0,xx-c0)
H=hammered((S,S),PXMM*1.0,rng,pits=0.5)
r0,r1=0.44,(TRY+D0)/TRY-0.01             # couronne visible (seppa -> rebord)
rm=(r0+r1)/2
u=th*rm*RR/PXMM                          # mm le long du tour
v=(r-r0)*RR/PXMM                         # mm depuis le bord intérieur
s=6.2                                    # pas des écailles (mm) : grands arcs comme la référence
circ=2*math.pi*rm*RR/PXMM
n=int(round(circ/(2*s))); s=circ/(2*n)   # raccord parfait sur le tour
band=(r>r0)&(r<r1)
W=np.zeros((S,S),np.float32); best=np.full((S,S),-1.0,np.float32)
nrows=int((r1-r0)*RR/PXMM/s)+2
for j in range(nrows):                    # rangées de l'intérieur vers l'extérieur ; la rangée suivante recouvre
    vj=j*s
    off=(j%2)*s
    k=np.round((u-off)/(2*s))
    cu=k*2*s+off
    d=np.sqrt((u-cu)**2+(v-vj)**2)
    m=(d<2*s*0.98)&(v>=vj-0.2)&band
    R=2*s
    f=d/R*4.0                             # 4 arcs emboîtés
    ridge=np.clip(1-np.abs(f-np.round(f))/0.34,0,1)**0.6*(f>0.5)
    ridge=np.maximum(ridge,(d<R*0.12)*1.0)
    # bout des arcs qui s'enroule (petite volute)
    W=np.where(m,ridge,W)
H=H+np.where(band,0.38*W-0.08,0)        # arcs en relief dans le fond creusé
# filets : bord intérieur et rebord extérieur de la couronne
H=H+0.18*np.exp(-((r-r0)*RR/PXMM/0.35)**2)
c,nrm8,spec=render_iron(H,PXMM*1.0,base=(24,24,28),hi=(110,110,118),lo=(4,4,6),nstrength=1.0)
# coins : fer sombre uni
q=int(S*0.11); corner=np.zeros((S,S),bool)
corner[:q,:q]=corner[:q,S-q:]=corner[S-q:,:q]=corner[S-q:,S-q:]=True
c[corner]=np.array([40,40,46],np.float32)/255; spec[corner]=0.7
nrm8[corner]=(128,128,255)
save_rgb('/home/claude/shikkoku/tex/tsuba_d.png',c)
save_rgb('/home/claude/shikkoku/tex/tsuba_n.png',nrm8)
save_gray('/home/claude/shikkoku/tex/tsuba_s.png',spec)
print('tsuba face vagues ok',n,'motifs/rangée')
