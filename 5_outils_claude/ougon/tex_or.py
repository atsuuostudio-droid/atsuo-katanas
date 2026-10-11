# Tuile gravure or (seamless) : fleurs de kiku, rinceaux, feuilles sur fond shakudo nanako
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/ougon/scripts')
from tex_common import *
rng=np.random.default_rng(11)
S=2048; OUT=1024
gold=np.zeros((S,S),np.uint8)      # masque or
petal=np.zeros((S,S),np.float32)   # relief fleurs
carve=np.zeros((S,S),np.uint8)     # traits gravés
SH=4; F=1<<SH
def P(pts): return (np.array(pts)*F).astype(np.int32)
def wrapdraw(fn):
    for dx in (-S,0,S):
        for dy in (-S,0,S): fn(dx,dy)
# --- fleurs (poisson) ---
flowers=[]
tries=0
while len(flowers)<11 and tries<5000:
    tries+=1
    r=rng.uniform(120,175); c=rng.uniform(0,S,2)
    ok=True
    for (c2,r2) in flowers:
        d=np.abs(c-c2); d=np.minimum(d,S-d)
        if np.hypot(*d) < r+r2+60: ok=False;break
    if ok: flowers.append((c,r))
def curl_shape(cx,cy,r,rot,gold,petal,carve,P,F,SH):
    # volute de nuage (kumo) : spirale dorée épaisse qui s'enroule, gravée au centre
    th=np.linspace(0,2.4*math.pi,160)
    rad=r*(1-th/(2.9*math.pi))
    pts=np.stack([cx+np.cos(th+rot)*rad,cy+np.sin(th+rot)*rad],1)
    wid=r*0.30*(1-th/(3.2*math.pi))
    for i in range(len(pts)-1):
        cv2.line(gold,tuple(P(pts[i])),tuple(P(pts[i+1])),255,max(2,int(wid[i])),cv2.LINE_AA,SH)
        cv2.line(petal,tuple(P(pts[i])),tuple(P(pts[i+1])),1.0,max(1,int(wid[i]*0.6)),cv2.LINE_AA,SH)
    cv2.polylines(carve,[P(pts[10:])],False,255,3,cv2.LINE_AA,SH)
    # second enroulement plus petit (volute double)
    th2=np.linspace(0,1.8*math.pi,90); r2=r*0.45
    c2=(cx+math.cos(rot+math.pi*0.9)*r*1.25, cy+math.sin(rot+math.pi*0.9)*r*1.25)
    rad2=r2*(1-th2/(2.6*math.pi))
    pts2=np.stack([c2[0]+np.cos(-th2+rot)*rad2,c2[1]+np.sin(-th2+rot)*rad2],1)
    for i in range(len(pts2)-1):
        cv2.line(gold,tuple(P(pts2[i])),tuple(P(pts2[i+1])),255,max(2,int(r2*0.32*(1-th2[i]/(3.4*math.pi)))),cv2.LINE_AA,SH)
def kiku(c,r,dx,dy): return   # emplacement réservé aux fleurs de cerisier
fstate=[]
for (c,r) in flowers:
    st=rng.bit_generator.state
    wrapdraw(lambda dx,dy: (rng.bit_generator.__setattr__('state',st), kiku(c,r,dx,dy)))
# --- rinceaux ---
def vine():
    p=rng.uniform(0,S,2); ang=rng.uniform(0,6.28); pts=[p.copy()]
    curv=rng.uniform(-0.03,0.03)
    for i in range(70):
        curv+=rng.normal(0,0.012); curv=np.clip(curv,-0.05,0.05)
        ang+=curv; p=p+np.array([math.cos(ang),math.sin(ang)])*14; pts.append(p.copy())
    return np.array(pts)
def leaf(base,ang,L,W,dx,dy):
    t=np.linspace(0,1,24)
    w=np.sin(np.pi*t)**0.8*W
    left=np.stack([t*L, w],1); right=np.stack([t*L,-w],1)[::-1]
    poly=np.concatenate([left,right])
    R=np.array([[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]])
    poly=poly@R.T+base+np.array([dx,dy])
    cv2.fillPoly(gold,[P(poly)],255,cv2.LINE_AA,SH)
    vein=np.stack([t*L*0.9,np.zeros_like(t)],1)@R.T+base+np.array([dx,dy])
    cv2.polylines(carve,[P(vein)],False,255,2,cv2.LINE_AA,SH)
def flower_clear(pt):
    for (c,r) in flowers:
        d=np.abs(pt-c); d=np.minimum(d,S-d)
        if np.hypot(*d)<r*1.05: return False
    return True
for v in range(30):
    pts=vine(); n=len(pts)
    leaves=[]
    for i in range(5,n-2,7):
        d=pts[i+1]-pts[i]; a=math.atan2(d[1],d[0])+rng.choice([-1,1])*rng.uniform(0.6,1.1)
        leaves.append((pts[i].copy(),a,rng.uniform(70,105),rng.uniform(20,28)))
    curl_a=math.atan2(*(pts[-1]-pts[-2])[::-1])
    def drawv(dx,dy,pts=pts,leaves=leaves,curl_a=curl_a):
        for i in range(n-1):
            if not flower_clear(pts[i]%S): continue
            th=max(3,int(14*(1-i/n)+4))
            cv2.line(gold,tuple(P(pts[i]+[dx,dy])),tuple(P(pts[i+1]+[dx,dy])),255,th,cv2.LINE_AA,SH)
        for (b,a,L,W) in leaves:
            if flower_clear(b%S): leaf(b,a,L,W,dx,dy)
        # vrille finale
        c=pts[-1]; a=curl_a
        sp=[c+[dx,dy]]
        rr=34
        for k in range(30):
            a+=0.33; rr*=0.93; sp.append(sp[-1]+np.array([math.cos(a),math.sin(a)])*rr*0.33)
        cv2.polylines(gold,[P(np.array(sp))],False,255,6,cv2.LINE_AA,SH)
    wrapdraw(drawv)
# --- composition ---
g=gold.astype(np.float32)/255
# dôme : distance au bord du motif
dist=cv2.distanceTransform((gold>127).astype(np.uint8),cv2.DIST_L2,5)
dist=np.minimum(dist/9.0,1.0)
h=np.sqrt(dist)*0.75*g + blur_wrap(petal,3)*0.45*g
h-= (blur_wrap(carve.astype(np.float32)/255,1.2))*0.55*g
# nanako (grains de poisson) sur le fond
yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
sp=16.0
gx=(xx/sp)%1-0.5; gy=((yy/sp + ((xx//sp)%2)*0.5)%1)-0.5
nan=np.clip(1-np.sqrt(gx**2+gy**2)/0.33,0,1)**0.6
h+= nan*0.18*(1-g)
h=blur_wrap(h,1.0)
# réduction
hs=cv2.resize(h,(OUT,OUT),interpolation=cv2.INTER_AREA)
gs=cv2.resize(g,(OUT,OUT),interpolation=cv2.INTER_AREA)
cs=cv2.resize(blur_wrap(carve.astype(np.float32)/255,1.0),(OUT,OUT),interpolation=cv2.INTER_AREA)
ns=cv2.resize(nan,(OUT,OUT),interpolation=cv2.INTER_AREA)
nrm=normal_from_height(hs,9.0)
# couleurs (sRGB)
noise=blur_wrap(rng.normal(0,1,(OUT,OUT)).astype(np.float32),2.0); noise/=noise.std()
dark=np.array([204,154,58],np.float32)/255
dark_hi=np.array([70,66,62],np.float32)/255
gold_lo=np.array([60,38,8],np.float32)/255
gold_mid=np.array([96,64,16],np.float32)/255
gold_hi=np.array([140,98,30],np.float32)/255
# lumière factice (dessus-gauche) pour donner du relief dans la diffuse
nv=nrm.astype(np.float32)/127.5-1
shade=np.clip(nv[...,0]*-0.35+nv[...,1]*0.35+0.75,0.3,1.25)
bg=dark[None,None]*(1+0.06*noise[...,None]) + (dark_hi-dark)[None,None]*ns[...,None]*0.7
t=np.clip((hs-0.15)/0.75,0,1)[...,None]
gcol=np.where(t<0.5, gold_lo+(gold_mid-gold_lo)*(t*2), gold_mid+(gold_hi-gold_mid)*((t-0.5)*2))
gcol=gcol*(1+0.04*noise[...,None])*shade[...,None]
gcol=gcol*(1-0.55*cs[...,None])
col=bg*(1-gs[...,None])+gcol*gs[...,None]
# légère usure dorée dans le fond (rehauts)
from ougon_draw2 import Canvas
SC=OUT/S
cvs=Canvas(OUT,wrap=True,bg=col.astype(np.float32)); cvs.h[:]=hs
for (c_,r_) in flowers:
    pass
fa=cvs.mask
nrm=normal_from_height(cvs.h,9.0)
col=cvs.rgb
save_rgb('/home/claude/ougon/tex/or_d.png',col)
save_rgb('/home/claude/ougon/tex/or_n.png',nrm)
spec=0.42*(1-gs)+0.95*gs - 0.4*cs*gs + 0.08*ns*(1-gs)
save_gray('/home/claude/ougon/tex/or_s.png',spec*(1-fa)+0.55*fa)
print('kin ok')
