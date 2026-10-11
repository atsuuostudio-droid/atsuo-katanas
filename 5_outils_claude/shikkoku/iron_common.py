# Fer noir martelé / piqué : outils communs (relief, rendu)
import numpy as np, cv2
from tex_common import *
def hammered(shape,px_mm,rng,pits=1.0):
    """relief de fer forgé : cupules de martelage + piqûres + grain"""
    H,W=shape
    h=np.zeros(shape,np.float32)
    n=int(H*W/(px_mm*1.4)**2*0.5)
    ys=rng.integers(0,H,n); xs=rng.integers(0,W,n); rs=rng.uniform(0.5,1.4,n)*px_mm
    for y,x,r in zip(ys,xs,rs):
        cv2.circle(h,(int(x),int(y)),int(max(r,1)),float(rng.uniform(0.4,1.0)),-1,cv2.LINE_AA)
    h=-cv2.GaussianBlur(h,(0,0),px_mm*0.35)*0.06
    m=int(H*W/(px_mm*3)**2*pits)
    ys=rng.integers(0,H,m); xs=rng.integers(0,W,m)
    p=np.zeros(shape,np.float32)
    for y,x in zip(ys,xs): cv2.circle(p,(int(x),int(y)),int(max(1,rng.uniform(0.08,0.25)*px_mm)),1.0,-1,cv2.LINE_AA)
    h-=cv2.GaussianBlur(p,(0,0),1.0)*0.08
    g=cv2.GaussianBlur(rng.normal(0,1,shape).astype(np.float32),(0,0),1.2); h+=0.006*g/g.std()
    return h
def render_iron(H,px_mm,base=(26,26,30),hi=(92,92,100),lo=(6,6,8),nstrength=1.0):
    Hs=cv2.GaussianBlur(H,(0,0),0.8)
    cav=np.clip(cv2.GaussianBlur(Hs,(0,0),px_mm*0.4)-Hs,0,None); cav=np.clip(cav/0.05,0,1)
    edge=np.clip(Hs-cv2.GaussianBlur(Hs,(0,0),px_mm*0.25),0,None); edge=np.clip(edge/0.03,0,1)   # arêtes usées, plus claires
    nrm8=normal_from_height(Hs,px_mm*nstrength,wrap=False)
    n=nrm8.astype(np.float32)/127.5-1
    light=np.clip(0.85-n[...,0]*0.30+n[...,1]*0.35,0.45,1.3)
    b=np.array(base,np.float32)/255; h_=np.array(hi,np.float32)/255; l_=np.array(lo,np.float32)/255
    c=b[None,None]*light[...,None]
    c=c+(h_-b)[None,None]*edge[...,None]*0.8
    c=c*(1-cav[...,None])+l_[None,None]*cav[...,None]
    spec=np.clip(0.55+0.35*edge-0.35*cav,0,1)
    return np.clip(c,0,1),nrm8,spec
