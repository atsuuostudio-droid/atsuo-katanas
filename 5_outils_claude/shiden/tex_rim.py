# Bordure du tsuba : ornements d'or en RELIEF (rinceau, feuilles, petites fleurs, volutes) sur laque noire.
# Bande : u = tour (4 répétitions), v = travers (face avant -> tranche arrondie -> face arrière).
# Sorties : rim_d/n/s.png + rim_h.npy (hauteur 0..1 utilisée par build pour déplacer la géométrie).
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/shiden/scripts')
from tex_common import *
from params import TSUBA_T
from rim_params import *
rng=np.random.default_rng(41)
PX=0.00003
GW=int(round(TILE_W/PX)); GH=int(round(BAND_W/PX))
print('grille',GW,GH,'bande',BAND_W)
def mm(x): return x/1000/PX
h=np.zeros((GH,GW),np.float32); gold=np.zeros((GH,GW),np.float32); dark=np.zeros((GH,GW),np.float32)
xx=np.arange(GW,dtype=np.float32)[None,:]; yy=np.arange(GH,dtype=np.float32)[:,None]
def patch(cx,cy,r):
    for dx in (-GW,0,GW):
        x=cx+dx; x1,x2=int(max(0,x-r)),int(min(GW,x+r)); y1,y2=int(max(0,cy-r)),int(min(GH,cy+r))
        if x2<=x1 or y2<=y1: continue
        X,Y=np.meshgrid(np.arange(x1,x2,dtype=np.float32)+0.5-x,np.arange(y1,y2,dtype=np.float32)+0.5-cy)
        yield (slice(y1,y2),slice(x1,x2)),X,Y
def put(sl,a,hv,engr=None):
    h[sl]=np.maximum(h[sl],hv*a); gold[sl]=np.maximum(gold[sl],a)
    if engr is not None: dark[sl]=np.maximum(dark[sl],engr*a)
def tube(pts,w0,w1,hgt=0.55):
    pts=np.asarray(pts,np.float32)
    for i in range(len(pts)-1):
        p,q=pts[i],pts[i+1]; w=w0+(w1-w0)*i/(len(pts)-1); c=(p+q)/2
        for sl,X,Y in patch(c[0],c[1],np.linalg.norm(q-p)/2+w+2):
            P=np.stack([X+c[0],Y+c[1]],-1); d=q-p; ll=max(float(d@d),1e-6)
            t=np.clip(((P-p)@d)/ll,0,1); dist=np.linalg.norm(P-(p+t[...,None]*d),axis=-1)
            a=np.clip(w-dist+0.6,0,1); prof=np.sqrt(np.clip(1-(dist/max(w,1))**2,0,1))
            put(sl,a,hgt*prof)
def leaf(cx,cy,L,W,rot,curv):
    for sl,X,Y in patch(cx,cy,L+W+4):
        u=X*math.cos(rot)+Y*math.sin(rot); v=-X*math.sin(rot)+Y*math.cos(rot)
        v=v-curv*L*((u/L)**2-u/L)*4
        t=np.clip(u/L,0,1)
        # feuille dentelée (acanthe stylisée) : lobes sur le bord
        prof=W*np.clip(np.sin(np.pi*t),0,1)**0.6*np.clip(1-t,0,1)**0.35*(1+0.14*np.sin(t*np.pi*7)**2)
        sd=prof-np.abs(v)
        a=np.clip(sd+0.6,0,1)*((u>0)&(u<L))
        dome=np.sqrt(np.clip(sd/max(W,1),0,1))
        vein=np.exp(-(v/1.4)**2)*(t<0.92)
        side=np.abs(np.sin((u*0.9-np.abs(v)*1.3)/max(L,1)*14))**8*np.clip(sd/3,0,1)
        put(sl,a,0.35+0.65*dome-0.25*vein-0.12*side,np.clip(0.8*vein+0.5*side,0,1))
def flower5(cx,cy,R,rot):
    for sl,X,Y in patch(cx,cy,R+4):
        d=np.sqrt(X*X+Y*Y); th=np.arctan2(Y,X)-rot
        phi=th-np.round(th/(2*math.pi/5))*2*math.pi/5
        rb=R*(0.35+0.65*np.cos(np.clip(phi*2.4,-math.pi/2,math.pi/2))**0.5)
        sd=rb-d; a=np.clip(sd+0.6,0,1)
        dome=np.sqrt(np.clip(sd/(R*0.5),0,1))
        core=np.exp(-(d/(R*0.22))**2)
        sep=np.exp(-((np.abs(phi)-math.pi/5)*d/1.2)**2)
        put(sl,a,0.45+0.4*dome+0.25*core-0.2*sep,np.clip(0.6*sep,0,1))
def curl(cx,cy,R,rot,sgn):
    th=np.linspace(0,2.2*math.pi,60); rad=R*(1-th/(2.7*math.pi))
    pts=np.stack([cx+np.cos(sgn*th+rot)*rad,cy+np.sin(sgn*th+rot)*rad],1)
    tube(pts,mm(0.35),mm(0.15),0.5)
# --- rinceau principal (2 ondulations par tuile, raccord parfait) ---
A=mm(2.0); lam=GW/2; yc=GH*V_APEX
xs=np.arange(-20,GW+20,6,dtype=np.float32)
vine=np.stack([xs,yc+A*np.sin(2*np.pi*xs/lam)],1)
tube(vine,mm(0.55),mm(0.55),0.6)
# --- feuilles alternées, qui débordent sur les faces ---
for k in range(12):
    x=(k+0.5)*GW/12; side=1 if k%2 else -1
    y=yc+A*math.sin(2*np.pi*x/lam)
    for j,(Lm,Wm,da) in enumerate([(6.5,2.3,0.0),(4.2,1.6,0.85),(3.6,1.4,-0.8)]):
        rot=(-math.pi/2 if side<0 else math.pi/2)+da*side+rng.uniform(-0.15,0.15)+0.35
        leaf(x+mm(0.3)*j,y,mm(Lm*rng.uniform(0.9,1.1)),mm(Wm),rot,rng.uniform(-0.2,0.2)*side)
# --- petites fleurs d'or sur les crêtes + volutes dans les creux ---
for k in range(4):
    x=(k+0.25)*GW/4; y=yc+A*math.sin(2*np.pi*x/lam)
    flower5(x+mm(3.2),y-mm(1.5)*(1 if k%2 else -1),mm(1.8),rng.uniform(0,6.28))
    curl(x-mm(3.5),y+mm(2.6)*(1 if k%2 else -1),mm(1.4),rng.uniform(0,6.28),1 if k%2 else -1)
# --- grains d'or (nanako) le long des bords de la bande ---
for k in range(0):
    x=rng.uniform(0,GW); y=rng.choice([GH*0.2,GH*0.8])+rng.normal(0,mm(0.8))
    for sl,X,Y in patch(x,y,mm(0.6)):
        d=np.sqrt(X*X+Y*Y); a=np.clip(mm(0.35)-d+0.6,0,1); put(sl,a,0.35*np.sqrt(np.clip(1-d/mm(0.35),0,1)))
# atténuer vers l'intérieur des faces (les ornements restent près du bord)
fade=np.clip((np.minimum(yy,GH-1-yy)/GH-0.03)/0.10,0,1)
gold*=fade; h*=fade; dark*=fade
h=cv2.GaussianBlur(h,(0,0),1.2)
# ---------------- couleurs ----------------
lac=cv2.GaussianBlur(np.random.default_rng(3).normal(0,1,(GH,GW)).astype(np.float32),(0,0),mm(2)); lac/=lac.std()
black=np.array([13,10,11],np.float32)/255
g_lo=np.array([62,60,72],np.float32)/255; g_mid=np.array([150,148,164],np.float32)/255; g_hi=np.array([236,234,248],np.float32)/255
nrm_full=normal_from_height(h,14.0,wrap=False).astype(np.float32)/127.5-1
shade=np.clip(0.70-nrm_full[...,0]*0.55+nrm_full[...,1]*0.55,0.25,1.4)
t=np.clip(h/0.9,0,1)
gc=np.where((t<0.5)[...,None],g_lo+(g_mid-g_lo)*(t*2)[...,None],g_mid+(g_hi-g_mid)*np.clip(t*2-1,0,1)[...,None])
gc=gc*shade[...,None]*(1-0.5*dark[...,None])
col=black[None,None]*(1+0.08*lac[...,None])
col=col*(1-gold[...,None])+gc*gold[...,None]
spec=0.80*(1-gold)+(0.95-0.4*dark)*gold
# ---------------- sorties ----------------
OW,OH=1024,512
save_rgb('/home/claude/shiden/tex/rim_d.png',cv2.resize(np.clip(col,0,1),(OW,OH),interpolation=cv2.INTER_AREA))
# normal map : seulement le détail fin (le relief principal est dans la géométrie)
detail=h-cv2.GaussianBlur(h,(0,0),mm(0.6))
save_rgb('/home/claude/shiden/tex/rim_n.png',cv2.resize(normal_from_height(detail+0.6*dark*gold*-0.15,10.0,wrap=False),(OW,OH),interpolation=cv2.INTER_AREA))
save_gray('/home/claude/shiden/tex/rim_s.png',cv2.resize(np.clip(spec,0,1),(512,256),interpolation=cv2.INTER_AREA))
np.save('/home/claude/shiden/tex/rim_h.npy',cv2.resize(h,(1024,int(1024*GH/GW)),interpolation=cv2.INTER_AREA))
prev=cv2.resize(np.clip(col,0,1),(GW//2,GH//2),interpolation=cv2.INTER_AREA)
cv2.imwrite('/home/claude/shiden/renders/p_rim.png',cv2.cvtColor((prev*255).astype(np.uint8),cv2.COLOR_RGB2BGR))
print('rim ok')
