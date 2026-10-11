# Face du tsuba Shikkoku : laque noire, incrustations d'or (idéogrammes, blasons mon, volutes, grains),
# centre = habaki en or massif gravé (motif géométrique), coins = or uni (seppa, menuki, bagues).
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/shikkoku/scripts')
from tex_common import *
import shikkoku_draw2 as D
from shikkoku_draw2 import Canvas, C
D.GOLD_LO,D.GOLD_MID,D.GOLD_HI=C(22,22,26),C(52,52,58),C(92,92,102)
rng=np.random.default_rng(91)
S=2048; c0=S/2; RR=S/2
yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
rr=np.sqrt((xx-c0)**2+(yy-c0)**2)/RR
n1=cv2.GaussianBlur(np.random.default_rng(2).normal(0,1,(S,S)).astype(np.float32),(0,0),40); n1/=n1.std()
n2=cv2.GaussianBlur(np.random.default_rng(3).normal(0,1,(S,S)).astype(np.float32),(0,0),5); n2/=n2.std()
bg=(C(9,9,11)*(1+0.10*n1[...,None]+0.04*n2[...,None])).astype(np.float32)
cv=Canvas(S,wrap=False,bg=bg); cv.spec[:]=0.85
GOLD=C(54,54,60)
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
goldbg=(C(218,170,70)*(1+0.015*n2[...,None])).astype(np.float32)
eng=np.zeros((S,S),np.float32)
FF=16
def rrect(x,y,w,h,r,th):
    pts=[]
    for (cx,cy,a0) in ((x+w-r,y+r,-math.pi/2),(x+w-r,y+h-r,0),(x+r,y+h-r,math.pi/2),(x+r,y+r,math.pi)):
        for a in np.linspace(a0,a0+math.pi/2,6): pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r))
    cv2.polylines(eng,[(np.array(pts)*FF).astype(np.int32)],True,1.0,th,cv2.LINE_AA,4)
# gravure : blocs arrondis, carrés, courbes, cercles (idéogrammes anciens), groupés au centre
for k in range(70):
    a=rng.uniform(0,6.28); rn=np.sqrt(rng.uniform(0,1))*0.16; x,y=P(rn,a)
    s=rng.uniform(0.018,0.034)*RR; kind=rng.integers(0,4)
    if kind==0: rrect(x-s/2,y-s/2,s*rng.uniform(.7,1.2),s*rng.uniform(.6,1.1),s*0.2,3)
    elif kind==1: cv2.ellipse(eng,(int(x*FF),int(y*FF)),(int(s*0.5*FF),int(s*0.4*FF)),rng.uniform(0,180),rng.uniform(0,90),rng.uniform(180,330),1.0,3,cv2.LINE_AA,4)
    elif kind==2: cv2.circle(eng,(int(x*FF),int(y*FF)),int(s*0.22*FF),1.0,3,cv2.LINE_AA,4)
    else:
        pts=np.array([(x+(t-.5)*s*1.4,y+math.sin(t*math.pi*1.5)*s*0.3) for t in np.linspace(0,1,10)])
        cv2.polylines(eng,[(pts*FF).astype(np.int32)],False,1.0,3,cv2.LINE_AA,4)
eng=cv2.GaussianBlur(eng,(0,0),0.7)
# biseau : lumière d'un côté du trait, ombre de l'autre (gravure ciselée)
gy,gx=np.gradient(cv2.GaussianBlur(eng,(0,0),1.2))
bev=np.clip((gx-gy)*6,-1,1)
habaki=goldbg*(1-0.32*eng[...,None])*(1+0.35*bev[...,None])
cv.rgb=cv.rgb*(1-cz[...,None])+habaki*cz[...,None]; cv.spec=cv.spec*(1-cz)+(0.95-0.4*eng)*cz; cv.h=cv.h*(1-cz)+(0.5-0.35*eng)*cz
# ---- coins : or uni ----
corner=np.zeros((S,S),np.float32); q=int(S*0.11)
for (ys,xs) in ((slice(0,q),slice(0,q)),(slice(0,q),slice(S-q,S)),(slice(S-q,S),slice(0,q)),(slice(S-q,S),slice(S-q,S))): corner[ys,xs]=1
gold=(C(58,58,64)*(1+0.05*n2[...,None])).astype(np.float32)
cv.rgb=cv.rgb*(1-corner[...,None])+gold*corner[...,None]; cv.spec=cv.spec*(1-corner)+0.95*corner; cv.h*=(1-corner)
nrm=normal_from_height(cv2.GaussianBlur(cv.h,(0,0),1.0),7.0,wrap=False)
save_rgb('/home/claude/shikkoku/tex/tsuba_d.png',np.clip(cv.rgb,0,1))
save_rgb('/home/claude/shikkoku/tex/tsuba_n.png',nrm)
save_gray('/home/claude/shikkoku/tex/tsuba_s.png',np.clip(cv.spec,0,1))
print('tsuba face ok')
