# Textures tanegashima : bois (crosse/fut), fer (canon, platine, garnitures), cordon (meche)
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/tanegashima/scripts')
from tex_common import *
from iron_common import hammered, render_iron
T='/home/claude/tanegashima/tex/'
rng=np.random.default_rng(3)
def noise(shape,sx,sy,seed):
    g=np.random.default_rng(seed).normal(0,1,shape).astype(np.float32); g=cv2.GaussianBlur(g,(0,0),sigmaX=sx,sigmaY=sy); return g/(g.std()+1e-6)
# ---- BOIS : veinage le long de U (longueur de l'arme), 2048x1024 = 0.60 m x 0.30 m ----
H,W=1024,2048
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
warp=noise((H,W),220,40,1)*18+noise((H,W),60,12,2)*4
rings=np.sin((yy+warp)*0.30+noise((H,W),400,60,3)*3)
fine=noise((H,W),30,0.8,4)
fig=np.clip(rings*0.5+0.5,0,1)**1.6
base=np.array([92,44,28],np.float32)/255; dark=np.array([44,19,11],np.float32)/255; lite=np.array([126,64,38],np.float32)/255
c=base[None,None]+(dark-base)[None,None]*(fig**2*0.75)[...,None]
c=c+(lite-c)*(np.clip(noise((H,W),90,30,5)*0.4,0,1)*0.6)[...,None]
c=c*(1+0.07*fine)[...,None]
# usure : coups, rayures et patine sombre
dent=np.zeros((H,W),np.float32)
for i in range(500):
    cv2.ellipse(dent,(int(rng.uniform(0,W)),int(rng.uniform(0,H))),(int(rng.uniform(2,9)),int(rng.uniform(1,3))),float(rng.uniform(0,180)),0,360,1.0,-1,cv2.LINE_AA)
for i in range(600):
    x=rng.uniform(0,W); y=rng.uniform(0,H); L=rng.uniform(10,70); a=rng.uniform(-0.4,0.4)
    cv2.line(dent,(int(x),int(y)),(int(x+L*math.cos(a)),int(y+L*math.sin(a))),0.6,1,cv2.LINE_AA)
dent=cv2.GaussianBlur(dent,(0,0),0.8)
c=c*(1-0.35*dent[...,None])
Hh=fig*0.15+fine*0.04-dent*0.5
save_rgb(T+'bois_d.png',np.clip(c,0,1)); save_rgb(T+'bois_n.png',normal_from_height(Hh,3.0,wrap=True)); save_gray(T+'bois_s.png',np.clip(0.22+0.10*fig-0.2*dent,0,1))
# ---- FER : fer patine gris, piqure, rouille legere (tuile 12 cm) ----
S=1024; PXMM=S/120
Hf=hammered((S,S),PXMM*1.2,rng,pits=1.5)
c,n8,sp=render_iron(Hf,PXMM*1.2,base=(78,78,80),hi=(150,150,154),lo=(20,20,22),nstrength=0.9)
ru=np.clip(noise((S,S),8,8,11)*0.7-1.0,0,1); rust=np.array([96,62,40],np.float32)/255
c=c*(1-0.55*ru[...,None])+rust*(0.55*ru[...,None])
streak=np.clip(noise((S,S),2,40,12)*0.3,0,1)       # stries de polissage le long du canon
c=c*(1+0.10*streak[...,None])
save_rgb(T+'fer_d.png',np.clip(c,0,1)); save_rgb(T+'fer_n.png',n8); save_gray(T+'fer_s.png',np.clip(sp-0.3*ru,0,1))
# ---- CORDON (meche) ----
S=512; yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
t=(xx/S*6+yy/S*6)%1.0; prof=np.sin(np.pi*t)**0.7
col=np.array([150,120,70],np.float32)/255*(0.55+0.45*prof)[...,None]*(1+0.1*noise((S,S),2,2,21))[...,None]
save_rgb(T+'cordon_d.png',np.clip(col,0,1)); save_rgb(T+'cordon_n.png',normal_from_height(prof*0.8,5.0,wrap=True)); save_gray(T+'cordon_s.png',np.full((S,S),0.15,np.float32))
print('textures ok')
