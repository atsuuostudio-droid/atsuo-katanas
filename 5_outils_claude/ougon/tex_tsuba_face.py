# Face du tsuba Ougon : laque noire, incrustations d'or (idéogrammes, blasons mon, volutes, grains),
# centre = habaki en or massif gravé (motif géométrique), coins = or uni (seppa, menuki, bagues).
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/ougon/scripts')
from tex_common import *
import ougon_draw2 as D
from ougon_draw2 import Canvas, C
D.GOLD_LO,D.GOLD_MID,D.GOLD_HI=C(120,80,20),C(212,160,58),C(252,224,140)
rng=np.random.default_rng(91)
S=2048; c0=S/2; RR=S/2
yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
rr=np.sqrt((xx-c0)**2+(yy-c0)**2)/RR
n1=cv2.GaussianBlur(np.random.default_rng(2).normal(0,1,(S,S)).astype(np.float32),(0,0),40); n1/=n1.std()
n2=cv2.GaussianBlur(np.random.default_rng(3).normal(0,1,(S,S)).astype(np.float32),(0,0),5); n2/=n2.std()
bg=(C(12,11,10)*(1+0.10*n1[...,None]+0.04*n2[...,None])).astype(np.float32)
cv=Canvas(S,wrap=False,bg=bg); cv.spec[:]=0.85
GOLD=C(214,162,60)
def P(rn,ang): return c0+math.cos(ang)*rn*RR, c0+math.sin(ang)*rn*RR
def stroke(pts,w0,w1): cv.branch(pts,w0,w1,GOLD)
def glyph(cx,cy,sz,rot):
    """idéogramme stylisé : traits sur une grille 4x4, pinceau qui s'affine"""
    ca,sa=math.cos(rot),math.sin(rot)
    def T(u,v): return (cx+(u*ca-v*sa)*sz, cy+(u*sa+v*ca)*sz)
    n=rng.integers(4,7)
    for _ in range(n):
        kind=rng.integers(0,4); a=rng.uniform(-0.45,0.45); b=rng.uniform(-0.45,0.45)
        if kind==0: pts=[T(-0.45+0.9*t,a+0.05*math.sin(t*3)) for t in np.linspace(0,1,8)]
        elif kind==1: pts=[T(a+0.04*math.sin(t*3),-0.45+0.9*t) for t in np.linspace(0,1,8)]
        elif kind==2: pts=[T(a+0.4*t,b+0.4*t) for t in np.linspace(0,1,6)]
        else: pts=[T(a-0.4*t,b+0.45*t*t) for t in np.linspace(0,1,6)]
        stroke(pts,sz*0.075,sz*0.035)
    if rng.random()<0.6: cv.gold_leaf(*T(rng.uniform(-.3,.3),rng.uniform(-.3,.3)),sz*0.18,sz*0.06,rot+rng.uniform(0,6),0)
def mon(cx,cy,R):
    """blason : anneau + 5 pétales + point central"""
    pts=[(cx+math.cos(t)*R,cy+math.sin(t)*R) for t in np.linspace(0,2*math.pi,60)]
    stroke(pts,R*0.09,R*0.09)
    a0=rng.uniform(0,6.28)
    for k in range(5):
        a=a0+k*2*math.pi/5; cv.gold_leaf(cx+math.cos(a)*R*0.12,cy+math.sin(a)*R*0.12,R*0.62,R*0.22,a,0)
    cv.gold_leaf(cx-R*0.08,cy,R*0.16,R*0.08,0,0)
def scroll(cx,cy,R,rot,sgn):
    th=np.linspace(0,2.4*math.pi,40); rad=R*(1-th/(2.9*math.pi))
    stroke([(cx+math.cos(sgn*t+rot)*r,cy+math.sin(sgn*t+rot)*r) for t,r in zip(th,rad)],R*0.16,R*0.05)
# composition : couronne de blasons + idéogrammes entre, volutes et grains
for k in range(6):
    a=k*math.pi/3+0.25; x,y=P(0.66,a); mon(x,y,0.085*RR)
    for j in (-1,1):
        x,y=P(0.66+0.02*j,a+j*0.30); glyph(x,y,0.11*RR,a+math.pi/2)
    x,y=P(0.50,a+math.pi/6); scroll(x,y,0.05*RR,a,1)
    x,y=P(0.79,a+math.pi/6); scroll(x,y,0.045*RR,a,-1)
for k in range(90):
    a=rng.uniform(0,6.28); rn=rng.uniform(0.46,0.82); x,y=P(rn,a)
    cv.gold_leaf(x,y,0.010*RR,0.006*RR,rng.uniform(0,6.28),0)
# filets d'or concentriques
for rn,w in ((0.455,5),(0.815,6)):
    stroke([P(rn,t) for t in np.linspace(0,2*math.pi,240)],w,w)
# ---- centre : habaki en or massif, gravure géométrique sombre ----
cz=np.clip((0.235-rr)*S/2,0,1)
goldbg=(C(206,156,56)*(1+0.05*n2[...,None])).astype(np.float32)
eng=np.zeros((S,S),np.float32)
for k in range(220):
    a=rng.uniform(0,6.28); rn=np.sqrt(rng.uniform(0,1))*0.2; x,y=P(rn,a); s=rng.uniform(0.012,0.02)*RR; rot=rng.uniform(0,3.14)
    cs_,sn=math.cos(rot),math.sin(rot)
    poly=np.array([[x+cs_*s,y+sn*s],[x-sn*s*0.6,y+cs_*s*0.6],[x-cs_*s,y-sn*s],[x+sn*s*0.6,y-cs_*s*0.6]],np.float32)
    cv2.polylines(eng,[(poly*16).astype(np.int32)],True,1.0,3,cv2.LINE_AA,4)
    if rng.random()<0.5: cv2.circle(eng,(int(x*16),int(y*16)),int(s*0.35*16),1.0,3,cv2.LINE_AA,4)
eng=cv2.GaussianBlur(eng,(0,0),0.8)
habaki=goldbg*(1-0.6*eng[...,None])
cv.rgb=cv.rgb*(1-cz[...,None])+habaki*cz[...,None]; cv.spec=cv.spec*(1-cz)+(0.95-0.4*eng)*cz; cv.h=cv.h*(1-cz)+(0.5-0.35*eng)*cz
# ---- coins : or uni ----
corner=np.zeros((S,S),np.float32); q=int(S*0.11)
for (ys,xs) in ((slice(0,q),slice(0,q)),(slice(0,q),slice(S-q,S)),(slice(S-q,S),slice(0,q)),(slice(S-q,S),slice(S-q,S))): corner[ys,xs]=1
gold=(C(214,164,66)*(1+0.05*n2[...,None])).astype(np.float32)
cv.rgb=cv.rgb*(1-corner[...,None])+gold*corner[...,None]; cv.spec=cv.spec*(1-corner)+0.95*corner; cv.h*=(1-corner)
nrm=normal_from_height(cv2.GaussianBlur(cv.h,(0,0),1.0),7.0,wrap=False)
save_rgb('/home/claude/ougon/tex/tsuba_d.png',np.clip(cv.rgb,0,1))
save_rgb('/home/claude/ougon/tex/tsuba_n.png',nrm)
save_gray('/home/claude/ougon/tex/tsuba_s.png',np.clip(cv.spec,0,1))
print('tsuba face ok')
