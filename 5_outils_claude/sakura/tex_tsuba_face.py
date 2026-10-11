# Face du tsuba Sakura : laque noire brillante, fleurs de cerisier peintes, boutons, feuilles d'or, hitsu-ana.
# Centre (r<0.235, caché par la seppa) = décor du habaki (bronze sombre fleuri). Coins = or uni (seppa, menuki).
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/sakura/scripts')
from tex_common import *
from sakura_draw2 import Canvas, C
rng=np.random.default_rng(31)
S=2048; c0=S/2; RR=S/2
yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
rr=np.sqrt((xx-c0)**2+(yy-c0)**2)/RR
lac=np.random.default_rng(2).normal(0,1,(S,S)).astype(np.float32); lac=cv2.GaussianBlur(lac,(0,0),12); lac/=lac.std()
bg=(C(12,9,11)[None,None]*(1+0.10*lac[...,None])).astype(np.float32)
cv=Canvas(S,wrap=False,bg=bg); cv.spec[:]=0.85
def P(rn,ang): return c0+math.cos(ang)*rn*RR, c0+math.sin(ang)*rn*RR
ha=0.0  # (ouverture ovale retirée à la demande)
# ---- branches (fines, brun-noir avec reflets or) ----
for k in range(3):
    a0=k*2.1+rng.uniform(0,0.5); pts=[]
    for i in range(40):
        a=a0+i*0.04; rn=0.66+0.12*math.sin(i*0.11+k*1.7)
        pts.append(P(rn,a))
    cv.branch(pts,7,2,C(70,48,30))
# ---- feuilles d'or ----
for k in range(26):
    a=rng.uniform(0,6.28); rn=rng.uniform(0.46,0.86); x,y=P(rn,a)
    cv.gold_leaf(x,y,rng.uniform(0.07,0.11)*RR,rng.uniform(0.022,0.032)*RR,rng.uniform(0,6.28),rng.uniform(-0.25,0.25))
# ---- fleurs (couronne irrégulière comme sur la photo) ----
placed=[]
tries=0
while len(placed)<23 and tries<4000:
    tries+=1
    a=rng.uniform(0,6.28); rn=rng.uniform(0.50,0.84); Rf=rng.uniform(0.095,0.15)
    x,y=P(rn,a)
    if any(math.hypot(x-px,y-py)<(Rf+pr)*RR*0.72 for px,py,pr in placed): continue
    placed.append((x,y,Rf))
for (x,y,Rf) in placed:
    cv.flower(x,y,Rf*RR,rng.uniform(0,6.28),int(rng.integers(3)),squash=rng.uniform(0.6,1.0),tilt=rng.uniform(0,3.14),rng=rng)
for k in range(10):
    a=rng.uniform(0,6.28); rn=rng.uniform(0.5,0.86); x,y=P(rn,a)
    cv.bud(x,y,rng.uniform(0.022,0.032)*RR,rng.uniform(0,6.28),int(rng.integers(3)))
# ---- centre : décor du habaki (bronze sombre, fleurs, feuilles d'or) ----
cz=np.clip((0.235-rr)*S/2,0,1)
bronze=C(46,32,24)[None,None]*(1+0.12*lac[...,None])
cv.rgb=cv.rgb*(1-cz[...,None])+bronze*cz[...,None]; cv.spec=cv.spec*(1-cz)+0.7*cz; cv.h*= (1-cz)
for k in range(12):
    a=rng.uniform(0,6.28); rn=rng.uniform(0.02,0.19); x,y=P(rn,a)
    cv.gold_leaf(x,y,rng.uniform(0.03,0.05)*RR,rng.uniform(0.010,0.015)*RR,rng.uniform(0,6.28))
for k in range(9):
    a=k*2*math.pi/9+rng.uniform(-.2,.2); rn=rng.uniform(0.06,0.18) if k else 0.0; x,y=P(rn,a)
    cv.flower(x,y,rng.uniform(0.040,0.055)*RR,rng.uniform(0,6.28),int(rng.integers(3)),squash=rng.uniform(0.75,1.0),tilt=rng.uniform(0,3),rng=rng)
cv.rgb=cv.rgb*(1-(rr>0.235)[...,None]*0)  # (rien)
# ---- coins : or uni (seppa, menuki) ----
corner=np.zeros((S,S),np.float32); q=int(S*0.11)
for (ys,xs) in ((slice(0,q),slice(0,q)),(slice(0,q),slice(S-q,S)),(slice(S-q,S),slice(0,q)),(slice(S-q,S),slice(S-q,S))): corner[ys,xs]=1
gn=cv2.GaussianBlur(np.random.default_rng(9).normal(0,1,(S,S)).astype(np.float32),(0,0),3)
goldc=C(192,140,52)[None,None]*(1+0.04*gn[...,None])
cv.rgb=cv.rgb*(1-corner[...,None])+goldc*corner[...,None]; cv.spec=cv.spec*(1-corner)+0.95*corner; cv.h*=(1-corner)
# ---- sorties ----
nrm=normal_from_height(cv2.GaussianBlur(cv.h,(0,0),1.0),6.0,wrap=False)
save_rgb('/home/claude/sakura/tex/tsuba_d.png',np.clip(cv.rgb,0,1))
save_rgb('/home/claude/sakura/tex/tsuba_n.png',nrm)
save_gray('/home/claude/sakura/tex/tsuba_s.png',np.clip(cv.spec,0,1))
print('tsuba face ok',len(placed),'fleurs')
