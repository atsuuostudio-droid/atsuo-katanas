# Face du tsuba Akaguro : fer noirci (shakudo) patiné, incrustations de laiton vieilli (branches, feuilles, oiseaux).
# Centre (r<0.235, caché par la seppa) = décor du habaki. Coins = laiton uni (seppa, menuki, bagues).
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/akaguro/scripts')
from tex_common import *
import akaguro_draw2 as D
from akaguro_draw2 import Canvas, C
D.GOLD_LO,D.GOLD_MID,D.GOLD_HI=C(80,6,12),C(168,20,30),C(232,76,72)
rng=np.random.default_rng(57)
S=2048; c0=S/2; RR=S/2
yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
rr=np.sqrt((xx-c0)**2+(yy-c0)**2)/RR
n1=cv2.GaussianBlur(np.random.default_rng(2).normal(0,1,(S,S)).astype(np.float32),(0,0),40); n1/=n1.std()
n2=cv2.GaussianBlur(np.random.default_rng(3).normal(0,1,(S,S)).astype(np.float32),(0,0),6); n2/=n2.std()
pat=np.clip(0.5+0.35*n1,0,1)[...,None]
bg=(C(10,9,11)*(1-0.2*pat)+C(22,14,14)*0.2*pat)*(1+0.06*n2[...,None])
cv=Canvas(S,wrap=False,bg=bg.astype(np.float32)); cv.spec[:]=0.85
cv.h[:]=0.05*n2
def P(rn,ang): return c0+math.cos(ang)*rn*RR, c0+math.sin(ang)*rn*RR
BRASS=C(160,18,28)
def bird(cx,cy,sz,rot):
    for side in (-1,1):
        pts=[]
        for t in np.linspace(0,1,14):
            x=side*t*sz; y=-math.sin(t*math.pi)*sz*0.35+t*t*sz*0.15
            pts.append((cx+x*math.cos(rot)-y*math.sin(rot), cy+x*math.sin(rot)+y*math.cos(rot)))
        cv.branch(pts,sz*0.07,sz*0.02,BRASS)
# branches avec feuilles (incrustations)
for k in range(7):
    a0=k*2*math.pi/7+rng.uniform(-0.2,0.2); pts=[]
    for i in range(30):
        a=a0+i*0.035; rn=0.50+0.28*(i/30)+0.03*math.sin(i*0.5+k)
        pts.append(P(rn,a))
    cv.branch(pts,9,3,BRASS)
    for i in range(2,30,3):
        x,y=pts[i]; d=np.subtract(pts[min(i+1,29)],pts[i]); ang=math.atan2(d[1],d[0])+rng.choice([-1,1])*rng.uniform(0.6,1.1)
        cv.gold_leaf(x,y,rng.uniform(0.05,0.08)*RR,rng.uniform(0.016,0.024)*RR,ang,rng.uniform(-0.2,0.2))
# oiseaux en vol
for k in range(9):
    a=rng.uniform(0,6.28); rn=rng.uniform(0.52,0.80); x,y=P(rn,a)
    bird(x,y,rng.uniform(0.05,0.08)*RR,rng.uniform(-0.4,0.4))
# grains de laiton
for k in range(40):
    a=rng.uniform(0,6.28); rn=rng.uniform(0.47,0.8); x,y=P(rn,a)
    cv.gold_leaf(x,y,0.012*RR,0.006*RR,rng.uniform(0,6.28),0)
# ---- centre : décor du habaki (fer noirci + laiton gravé) ----
cz=np.clip((0.235-rr)*S/2,0,1)
cv.rgb=cv.rgb*(1-cz[...,None])+bg*cz[...,None]; cv.h*=(1-cz)
cv.rgb=cv.rgb*(1-cz[...,None])+C(8,7,9)*cz[...,None]; cv.spec=cv.spec*(1-cz)+0.9*cz   # habaki : noir uni
# ---- coins : laiton uni vieilli ----
corner=np.zeros((S,S),np.float32); q=int(S*0.11)
for (ys,xs) in ((slice(0,q),slice(0,q)),(slice(0,q),slice(S-q,S)),(slice(S-q,S),slice(0,q)),(slice(S-q,S),slice(S-q,S))): corner[ys,xs]=1
brass=(C(204,156,64)*(1+0.06*n2[...,None])).astype(np.float32)
cv.rgb=cv.rgb*(1-corner[...,None])+brass*corner[...,None]; cv.spec=cv.spec*(1-corner)+0.9*corner; cv.h*=(1-corner)
# coin bas-droit = laque noire (seppa)
cv.rgb[S-q:S,S-q:S]=C(8,7,9); cv.spec[S-q:S,S-q:S]=0.85
nrm=normal_from_height(cv2.GaussianBlur(cv.h,(0,0),1.0),6.0,wrap=False)
save_rgb('/home/claude/akaguro/tex/tsuba_d.png',np.clip(cv.rgb,0,1))
save_rgb('/home/claude/akaguro/tex/tsuba_n.png',nrm)
save_gray('/home/claude/akaguro/tex/tsuba_s.png',np.clip(cv.spec,0,1))
print('tsuba face ok')
