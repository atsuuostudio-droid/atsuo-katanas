# Habaki Ougon : or poli, fleurs ciselées en relief ton sur ton (chrysanthème, cerisiers, feuilles, boutons, branche).
# u = x le long de l'arme (34 mm), v = z (0 = bas, 1 = haut, 50 mm). Tout est calculé comme une carte de hauteur.
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/ougon/scripts')
from tex_common import *
rng=np.random.default_rng(311)
PX=0.000015; WU,WV=0.034,0.050
GW=int(WU/PX); GH=int(WV/PX)
def mm(x): return x/1000/PX
H=np.zeros((GH,GW),np.float32)          # relief
def patch(cx,cy,r):
    x1,x2=int(max(0,cx-r)),int(min(GW,cx+r)); y1,y2=int(max(0,cy-r)),int(min(GH,cy+r))
    if x2<=x1 or y2<=y1: return None
    X,Y=np.meshgrid(np.arange(x1,x2,dtype=np.float32)+0.5-cx,np.arange(y1,y2,dtype=np.float32)+0.5-cy)
    return (slice(y1,y2),slice(x1,x2)),X,Y
def put(sl,h,mask):
    # l'élément posé recouvre ce qu'il y a dessous (pas de max : un pétale du dessus cache celui du dessous)
    H[sl]=H[sl]*(1-mask)+np.maximum(h,0)*mask
def petal(cx,cy,L,W,rot,base,amp=0.35,notch=False,vein=True,tipw=0.35):
    p=patch(cx,cy,L+W+4)
    if p is None: return
    sl,X,Y=p
    ca,sa=math.cos(rot),math.sin(rot)
    u=X*ca+Y*sa; v=-X*sa+Y*ca
    t=np.clip(u/L,0,1)
    prof=W*np.clip(np.sin(np.pi*np.clip(t*0.85+0.08,0,1)),0,1)**0.55*(1-(1-tipw)*np.clip((t-0.7)/0.3,0,1)**2)
    d=prof-np.abs(v)
    if notch: d=np.where(u>L*0.86,np.minimum(d,np.abs(v)-(u-L*0.86)*1.1),d)
    inside=np.clip(d+0.7,0,1)*((u>0)&(u<L))
    q=np.clip(np.abs(v)/np.maximum(prof,1e-3),0,1)
    h=base+amp*np.sqrt(np.clip(1-q**2,0,1))*(0.55+0.45*np.sin(np.pi*t))
    h=h+0.10*amp*t   # le bout du pétale se relève
    if vein:
        h=h-0.22*amp*np.exp(-(v/mm(0.06))**2)*((t>0.08)&(t<0.85))
        for k in (-1,1):   # nervures secondaires
            vv=v-k*prof*0.45*np.sin(np.pi*t)
            h=h-0.10*amp*np.exp(-(vv/mm(0.04))**2)*((t>0.2)&(t<0.75))
    put(sl,h,inside)
def dome(cx,cy,R,base,amp,bumps=0):
    p=patch(cx,cy,R+3)
    if p is None: return
    sl,X,Y=p; d=np.sqrt(X*X+Y*Y)
    inside=np.clip(R-d+0.7,0,1)
    h=base+amp*np.sqrt(np.clip(1-(d/R)**2,0,1))
    if bumps:
        b=np.zeros_like(h)
        for k in range(bumps):
            a=rng.uniform(0,6.28); r=math.sqrt(rng.uniform(0,1))*R*0.85; br=R*rng.uniform(0.10,0.16)
            b=np.maximum(b,np.sqrt(np.clip(1-((X-math.cos(a)*r)**2+(Y-math.sin(a)*r)**2)/br**2,0,1)))
        h=h+0.25*amp*b
    put(sl,h,inside)
def leaf(cx,cy,L,W,rot,base,curv=0.15):
    p=patch(cx,cy,L+W+4)
    if p is None: return
    sl,X,Y=p
    ca,sa=math.cos(rot),math.sin(rot)
    u=X*ca+Y*sa; v=-X*sa+Y*ca
    v=v-curv*L*((u/L)**2-u/L)*4
    t=np.clip(u/L,0,1)
    prof=W*np.clip(np.sin(np.pi*t),0,1)**0.65*(1+0.09*np.abs(np.sin(t*math.pi*9)))   # bord dentelé
    d=prof-np.abs(v); inside=np.clip(d+0.7,0,1)*((u>0)&(u<L))
    q=np.clip(np.abs(v)/np.maximum(prof,1e-3),0,1)
    h=base+0.30*np.sqrt(np.clip(1-q**2,0,1))+0.06*np.sign(v)*q   # léger pli
    h=h-0.10*np.exp(-(v/mm(0.07))**2)*(t<0.95)                       # nervure centrale
    side=np.abs(np.sin((u*0.8-np.abs(v)*1.2)/max(L,1)*16))
    h=h-0.05*np.exp(-(side/0.10)**2)*(q<0.9)*(t>0.05)                # nervures latérales
    put(sl,h,inside)
def stem(pts,w0,w1,base):
    pts=np.asarray(pts,np.float32)
    for i in range(len(pts)-1):
        p0,p1=pts[i],pts[i+1]; w=w0+(w1-w0)*i/(len(pts)-1); c=(p0+p1)/2
        pp=patch(c[0],c[1],np.linalg.norm(p1-p0)/2+w+3)
        if pp is None: continue
        sl,X,Y=pp; P=np.stack([X+c[0],Y+c[1]],-1); dd=p1-p0; ll=max(float(dd@dd),1e-6)
        tt=np.clip(((P-p0)@dd)/ll,0,1); dist=np.linalg.norm(P-(p0+tt[...,None]*dd),axis=-1)
        inside=np.clip(w-dist+0.7,0,1)
        h=base+0.22*np.sqrt(np.clip(1-(dist/w)**2,0,1))+0.03*np.sin(tt*40+i)
        H[sl]=np.maximum(H[sl],h*inside)
def kiku(cx,cy,R):
    rot0=rng.uniform(0,6.28)
    for ring,(n,Lf,Wf,base) in enumerate([(22,1.0,0.13,0.10),(18,0.78,0.15,0.30),(14,0.52,0.17,0.48)]):
        for k in range(n):
            a=rot0+k*2*math.pi/n+ring*0.13+rng.uniform(-0.04,0.04)
            petal(cx+math.cos(a)*R*0.10,cy+math.sin(a)*R*0.10,R*Lf*rng.uniform(0.93,1.05),R*Wf,a,base,0.30,False,True,0.55)
    dome(cx,cy,R*0.24,0.62,0.22,bumps=26)
def sakura(cx,cy,R):
    rot0=rng.uniform(0,6.28)
    for k in range(5):
        a=rot0+k*2*math.pi/5
        petal(cx+math.cos(a)*R*0.05,cy+math.sin(a)*R*0.05,R,R*0.46,a,0.12,0.32,True,True,0.8)
    dome(cx,cy,R*0.18,0.40,0.10)
    for k in range(11):    # étamines
        a=rot0+k*2*math.pi/11+0.15; r=R*0.32
        stem([(cx+math.cos(a)*R*0.12,cy+math.sin(a)*R*0.12),(cx+math.cos(a)*r,cy+math.sin(a)*r)],mm(0.06),mm(0.05),0.42)
        dome(cx+math.cos(a)*r,cy+math.sin(a)*r,mm(0.16),0.46,0.08)
def bud(cx,cy,R,rot):
    for s in (-1,1): leaf(cx,cy,R*0.9,R*0.28,rot+math.pi+s*0.5,0.12,0.1)
    petal(cx,cy,R*1.6,R*0.62,rot,0.10,0.34,False,False,0.5)
# ---------------- composition ----------------
W_,H_=GW,GH
stem([(W_*0.05,H_*0.86),(W_*0.22,H_*0.74),(W_*0.38,H_*0.66),(W_*0.52,H_*0.56),(W_*0.66,H_*0.44),(W_*0.80,H_*0.30),(W_*0.92,H_*0.18)],mm(0.55),mm(0.25),0.05)
stem([(W_*0.38,H_*0.66),(W_*0.30,H_*0.50),(W_*0.27,H_*0.34),(W_*0.30,H_*0.20)],mm(0.35),mm(0.18),0.05)
stem([(W_*0.66,H_*0.44),(W_*0.78,H_*0.55),(W_*0.86,H_*0.70)],mm(0.30),mm(0.16),0.05)
MAIN=[(0.05,0.86),(0.22,0.74),(0.38,0.66),(0.52,0.56),(0.66,0.44),(0.80,0.30),(0.92,0.18)]
SUB1=[(0.38,0.66),(0.30,0.50),(0.27,0.34),(0.30,0.20)]
SUB2=[(0.66,0.44),(0.78,0.55),(0.86,0.70)]
def on(path,s):
    P=np.array(path,np.float32)*[W_,H_]; seg=np.linalg.norm(np.diff(P,axis=0),axis=1); cum=np.concatenate([[0],np.cumsum(seg)])
    d=s*cum[-1]; i=min(int(np.searchsorted(cum,d))-1,len(seg)-1); i=max(i,0); f=(d-cum[i])/max(seg[i],1e-6)
    p=P[i]+(P[i+1]-P[i])*f; ang=math.atan2(*(P[i+1]-P[i])[::-1]); return p,ang
for path,s,side,L,Wd in [(MAIN,0.14,1,6.0,1.9),(MAIN,0.24,-1,5.2,1.7),(MAIN,0.72,1,5.5,1.8),(MAIN,0.84,-1,4.6,1.5),
                         (SUB1,0.45,1,4.8,1.5),(SUB1,0.75,-1,4.2,1.3),(SUB2,0.55,1,4.4,1.4),(MAIN,0.95,1,3.8,1.2)]:
    p,ang=on(path,s); leaf(p[0],p[1],mm(L),mm(Wd),ang+side*rng.uniform(0.7,1.0),0.08,0.15*side)
kiku(W_*0.56,H_*0.52,mm(9.0))
sakura(W_*0.28,H_*0.26,mm(5.0))
sakura(W_*0.80,H_*0.74,mm(4.4))
sakura(W_*0.20,H_*0.86,mm(3.2))
bud(W_*0.86,H_*0.86,mm(1.6),-1.0); bud(W_*0.34,H_*0.12,mm(1.4),1.2); bud(W_*0.92,H_*0.14,mm(1.3),0.4)
# filet de bordure en relief (moulure)
b=mm(1.1)
yy=np.arange(GH,dtype=np.float32)[:,None]; xx=np.arange(GW,dtype=np.float32)[None,:]
de=np.minimum(np.minimum(xx,GW-1-xx),np.minimum(yy,GH-1-yy))
H=np.maximum(H,0.18*np.exp(-((de-b)/mm(0.18))**2))
# ---------------- rendu ----------------
Hs=cv2.GaussianBlur(H,(0,0),0.8)
cav=np.clip(cv2.GaussianBlur(Hs,(0,0),mm(0.35))-Hs,0,None)          # creux -> occlusion
cav=np.clip(cav/0.06,0,1)
rel=np.clip(Hs/0.75,0,1)
nrm8=normal_from_height(Hs,mm(0.9),wrap=False)
n=nrm8.astype(np.float32)/127.5-1
light=np.clip(0.80-n[...,0]*0.35+n[...,1]*0.40,0.40,1.30)                # lumière douce venant du haut-gauche
vv=yy/GH
refl=0.86+0.30*np.exp(-((vv-0.62)/0.17)**2)+0.08*np.exp(-((vv-0.22)/0.08)**2)
brushed=cv2.GaussianBlur(rng.normal(0,1,(GH,GW)).astype(np.float32),(0,0),sigmaX=mm(3),sigmaY=mm(0.02)); brushed/=brushed.std()
flat=(Hs<0.02).astype(np.float32)
gold=np.array([214,160,60],np.float32)/255; gold_hi=np.array([250,218,130],np.float32)/255
c=gold[None,None]*refl[...,None]*(1+0.02*brushed[...,None]*flat[...,None])
c=c*(light[...,None]*(1-flat[...,None])+flat[...,None])
c=c+(gold_hi-gold)[None,None]*np.clip(rel-0.55,0,1)[...,None]*0.6
c=np.clip(c*(1-0.55*cav[...,None]),0,1)
spec=np.clip(0.95-0.5*cav,0,1)
OS=2048
save_rgb('/home/claude/ougon/tex/habaki_d.png',cv2.resize(c,(OS,OS),interpolation=cv2.INTER_AREA))
save_rgb('/home/claude/ougon/tex/habaki_n.png',cv2.resize(nrm8,(OS,OS),interpolation=cv2.INTER_AREA))
save_gray('/home/claude/ougon/tex/habaki_s.png',cv2.resize(spec,(1024,1024),interpolation=cv2.INTER_AREA))
cv2.imwrite('/home/claude/ougon/renders/p_habaki_tex.png',cv2.cvtColor((cv2.resize(c,(GW//4,GH//4),interpolation=cv2.INTER_AREA)*255).astype(np.uint8),cv2.COLOR_RGB2BGR))
print('habaki fleurs ok',GW,GH)
