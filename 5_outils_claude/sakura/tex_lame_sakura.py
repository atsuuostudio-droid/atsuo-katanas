# Texture de la lame Sakura (haute qualité) : vue de côté
#   u = longueur (habaki -> pointe), v = fraction de largeur locale (tranchant 0 -> dos 1)
# On dessine dans une grille PHYSIQUE (pixels carrés, hauteur absolue au-dessus du tranchant),
# puis chaque colonne est rééchantillonnée vers v (la lame s'affine vers la pointe : les fleurs restent rondes).
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/sakura/scripts')
from tex_common import *
from blade_params import *
rng=np.random.default_rng(77)
PX=0.00004                                   # 0,04 mm par pixel
GW=int(round(LB/PX)); GH=int(round(W0/PX))
OW,OH=8192,512
print('grille',GW,GH)
sc=(np.arange(GW)+0.5)*PX
wcol=np.array([wid(x) for x in sc],np.float32)
yy=np.arange(GH,dtype=np.float32)[:,None]; xx=np.arange(GW,dtype=np.float32)[None,:]
h=(GH-0.5-yy)*PX                             # hauteur physique au-dessus du tranchant
fl=(h/wcol[None,:]).astype(np.float32)       # fraction locale (0 tranchant, 1 dos)
inb=(fl<=1.0).astype(np.float32)             # dans la lame (au-dessus : hors lame à la pointe)
s=np.broadcast_to(sc[None,:],(GH,GW)).astype(np.float32)
def mm(x): return x/1000/PX
def gnoise(sx,sy,seed):
    r=np.random.default_rng(seed).normal(0,1,(GH,GW)).astype(np.float32)
    r=cv2.GaussianBlur(r,(0,0),sigmaX=sx,sigmaY=sy); return r/r.std()
def lerp(a,b,t): return a+(b-a)*t
def C(r,g,b): return np.array([r,g,b],np.float32)/255
# ---------------- fond : acier noir violacé poli ----------------
streak=gnoise(mm(9),mm(0.06),1)
base=lerp(C(20,11,24),C(34,18,38),np.clip(0.5+0.25*streak,0,1)[...,None])
col=np.broadcast_to(base,(GH,GW,3)).copy()
# ---------------- brume rose (nébuleuse) ----------------
n1=gnoise(mm(14),mm(1.6),2); n2=gnoise(mm(4),mm(0.6),3); n3=gnoise(mm(1.2),mm(0.25),4)
band=np.clip((fl-0.12)/0.08,0,1)*np.clip((0.80-fl)/0.10,0,1)
mist=np.clip(0.45*n1+0.30*n2+0.12*n3+0.12,0,None)**1.3*band*0.55
# plus dense vers la pointe et près du habaki
mist*=1.0+0.6*np.exp(-((s-LB)/0.09)**2)+0.3*np.exp(-(s/0.05)**2)
mist=np.clip(mist,0,0.85)
col=lerp(col,C(206,62,150)[None,None],mist[...,None])
# reflets diagonaux (éclats de lumière rose)
for k in range(9):
    x0=rng.uniform(0.03,LB-0.03)/PX; ang=math.radians(rng.uniform(55,75)); wdt=mm(rng.uniform(2,6))
    d=((xx-x0)*math.sin(ang)+(yy-GH/2)*math.cos(ang))
    g=np.exp(-(d/wdt)**2)*np.clip(gnoise(mm(3),mm(3),10+k)*0.5+0.6,0,1)*band*rng.uniform(0.15,0.3)
    col=lerp(col,C(240,120,200)[None,None],np.clip(g,0,1)[...,None])
# ---------------- ligne de trempe en vagues (hamon) ----------------
ph=rng.uniform(0,6.28,4)
hb=(0.215+0.028*np.sin(2*np.pi*sc/0.031+ph[0])+0.014*np.sin(2*np.pi*sc/0.0127+ph[1])
    +0.008*np.sin(2*np.pi*sc/0.0063+ph[2]))
hb=hb+0.010*cv2.GaussianBlur(np.random.default_rng(5).normal(0,1,(1,GW)).astype(np.float32),(0,0),mm(4))[0]*25
hbm=hb[None,:]
# zone du tranchant : rose -> blanc rosé au fil
t_edge=np.clip(fl/np.maximum(hbm,1e-3),0,1)
edge_col=lerp(C(255,222,240)[None,None],C(236,104,186)[None,None],(t_edge**1.3)[...,None])
edge_col=edge_col*(1+0.05*streak[...,None])
ez=np.clip((hbm-fl)*GH*wcol[None,:]/W0/2.0+0.5,0,1)          # bord net (≈2 px)
col=lerp(col,edge_col,ez[...,None])
# lueur au-dessus de la ligne + vagues secondaires (liserés blanc rosé)
glow_above=np.exp(-np.clip(fl-hbm,0,None)/0.035)*(1-ez)
col=lerp(col,C(225,85,170)[None,None],(glow_above*0.55)[...,None])
waves=np.zeros((GH,GW),np.float32)
for k,(off,amp,per,wid_mm,a) in enumerate([(0.0,0.0,1,0.10,1.0),(0.045,0.018,0.023,0.09,0.75),(0.09,0.022,0.017,0.08,0.55),(0.14,0.02,0.029,0.07,0.35)]):
    yk=hb+off+amp*np.sin(2*np.pi*sc/per+ph[3]*k)
    dk=np.abs(fl-yk[None,:])*wcol[None,:]/PX
    waves=np.maximum(waves,np.exp(-(dk/mm(wid_mm))**2)*a)
wglow=cv2.GaussianBlur(waves,(0,0),mm(0.35))
col=lerp(col,C(255,226,244)[None,None],np.clip(waves+0.6*wglow,0,1)[...,None])
# ---------------- pétales et fleurs de cerisier ----------------
alpha_all=np.zeros((GH,GW),np.float32)
PETAL_PINKS=[(C(250,196,222),C(226,92,160)),(C(255,226,238),C(238,138,188)),(C(246,168,206),C(208,58,138)),(C(255,240,246),C(244,170,206))]
def petal(cx,cy,L,W,rot,cols,alpha=1.0,notch=True,blur=0.0):
    """pétale : base en (cx,cy), axe selon rot ; L,W en px"""
    R=int(L+W)+4
    x1,x2=int(max(0,cx-R)),int(min(GW,cx+R)); y1,y2=int(max(0,cy-R)),int(min(GH,cy+R))
    if x2<=x1 or y2<=y1: return
    X=xx[:,x1:x2]-cx; Y=yy[y1:y2]-cy
    ca,sa=math.cos(rot),math.sin(rot)
    u=X*ca+Y*sa; v=-X*sa+Y*ca
    t=np.clip(u/L,0,1)
    prof=W*np.sin(np.pi*np.clip(t*0.92+0.04,0,1))**0.65
    d=prof-np.abs(v)
    if notch:   # encoche en V au bout du pétale
        d=np.where(u>L*0.84,np.minimum(d,np.abs(v)-(u-L*0.84)*0.9),d)
    d=np.where((u<0)|(u>L),-1e3,d)
    a=np.clip(d+0.5,0,1)
    if blur>0: a=cv2.GaussianBlur(a,(0,0),blur)
    a*=alpha
    light,deep=cols
    c=lerp(deep[None,None],light[None,None],(t**0.6)[...,None])
    vein=0.5+0.5*np.cos(np.clip(v/W,-1,1)*np.pi*4.5)
    c=c*(1-0.06*(vein*(1-t))[...,None])
    edge=np.clip(1-d/2.2,0,1)*(d>0)
    c=c*(1-0.25*edge[...,None])
    sl=(slice(y1,y2),slice(x1,x2))
    col[sl]=lerp(col[sl],c,a[...,None])
    alpha_all[sl]=np.maximum(alpha_all[sl],a)
def flower(cx,cy,Rf,rot,cols,alpha=1.0):
    for k in range(5):
        petal(cx,cy,Rf,Rf*0.47,rot+k*2*math.pi/5,cols,alpha)
    # coeur : rose foncé + étamines
    r=int(Rf*0.9)+3
    x1,x2=int(max(0,cx-r)),int(min(GW,cx+r)); y1,y2=int(max(0,cy-r)),int(min(GH,cy+r))
    if x2<=x1 or y2<=y1: return
    X=xx[:,x1:x2]-cx; Y=yy[y1:y2]-cy; d=np.sqrt(X*X+Y*Y)
    sl=(slice(y1,y2),slice(x1,x2))
    core=np.clip(Rf*0.20-d+0.5,0,1)*alpha
    col[sl]=lerp(col[sl],C(176,30,104)[None,None],core[...,None])
    halo=np.exp(-(d/(Rf*0.32))**2)*0.5*alpha
    col[sl]=lerp(col[sl],C(214,60,140)[None,None],halo[...,None])
    for k in range(9):
        a=rot+k*2*math.pi/9+0.2; rr=Rf*0.30
        px,py=cx+math.cos(a)*rr,cy+math.sin(a)*rr
        dd=np.sqrt((X+cx-px)**2+(Y+cy-py)**2)
        st=np.clip(Rf*0.045-dd+0.5,0,1)*alpha
        col[sl]=lerp(col[sl],C(255,214,120)[None,None],st[...,None])
        # filet de l'étamine
        seg=np.abs((X)*math.sin(a)-(Y)*math.cos(a))
        along=(X*math.cos(a)+Y*math.sin(a))
        fil=np.clip(1.2-seg,0,1)*((along>Rf*0.12)&(along<rr))*alpha*0.8
        col[sl]=lerp(col[sl],C(250,190,215)[None,None],fil[...,None])
def yfrac(frac,sx): return GH-0.5-frac*wid(sx)/PX
# densité : plus de pétales vers la pointe et près du habaki (comme l'image)
def density(x): return 0.6+1.4*math.exp(-((x-LB*0.93)/0.09)**2)+0.8*math.exp(-((x-0.05)/0.06)**2)+0.4*math.exp(-((x-LB*0.55)/0.08)**2)
items=[]
x=0.006
while x<LB-0.015:
    if rng.random()<0.085*density(x):
        items.append(('flower',x))
    x+=0.004/density(x)*rng.uniform(0.6,1.4)
    items.append(('petal',x))
# pétales flous en arrière-plan (profondeur), puis pétales nets, puis fleurs
for kind,x in items:
    if kind!='petal' or rng.random()>0.45: continue
    fr=rng.uniform(0.25,0.80); cx=x/PX; cy=yfrac(fr,x)
    L=mm(rng.uniform(2.0,3.5)); petal(cx,cy,L,L*0.42,rng.uniform(0,6.28),PETAL_PINKS[rng.integers(4)],alpha=rng.uniform(0.35,0.6),blur=mm(rng.uniform(0.25,0.5)))
# traînées de lumière (pétales emportés par le vent vers la pointe)
trail=np.zeros((GH,GW),np.float32)
for kind,x in items:
    if rng.random()>0.35: continue
    fr=rng.uniform(0.3,0.75); cx=x/PX; cy=yfrac(fr,x); Lt=mm(rng.uniform(6,16)); ang=math.radians(rng.uniform(-12,12))
    x1,x2=int(max(0,cx-Lt-6)),int(min(GW,cx+6)); y1,y2=int(max(0,cy-Lt*0.3-8)),int(min(GH,cy+Lt*0.3+8))
    if x2<=x1 or y2<=y1: continue
    X=xx[:,x1:x2]-cx; Y=yy[y1:y2]-cy
    u=-(X*math.cos(ang)+Y*math.sin(ang)); v=-X*math.sin(ang)+Y*math.cos(ang)
    a=np.exp(-(v/mm(0.25))**2)*np.clip(1-u/Lt,0,1)*(u>0)*rng.uniform(0.3,0.6)
    trail[y1:y2,x1:x2]=np.maximum(trail[y1:y2,x1:x2],a)
col=lerp(col,C(250,170,220)[None,None],cv2.GaussianBlur(trail,(0,0),mm(0.15))[...,None])
for kind,x in items:
    fr=rng.uniform(0.28,0.78); cx=x/PX; cy=yfrac(fr,x)
    if kind=='petal':
        L=mm(rng.uniform(2.6,5.0)); W=L*rng.uniform(0.38,0.48)
        petal(cx,cy,L,W,rng.uniform(0,6.28),PETAL_PINKS[rng.integers(4)],alpha=rng.uniform(0.85,1.0))
    else:
        fr=rng.uniform(0.35,0.68); cy=yfrac(fr,x)
        Rf=mm(rng.uniform(3.0,4.6)); Rf=min(Rf,wid(x)/PX*0.30)
        flower(cx,cy,Rf,rng.uniform(0,6.28),PETAL_PINKS[rng.integers(4)])
# lueur rose autour des pétales
pg=cv2.GaussianBlur(alpha_all,(0,0),mm(0.9))
col=lerp(col,C(236,110,190)[None,None],(np.clip(pg-alpha_all,0,1)*0.55)[...,None])
# ---------------- shinogi-ji (dos) + gorge ----------------
shin=np.clip((fl-F_SHIN)*wcol[None,:]/PX/1.5+0.5,0,1)
shin_col=lerp(C(14,8,17),C(30,16,34),np.clip(0.5+0.3*streak,0,1)[...,None])
# reflet rose étiré le long du dos
refl=np.exp(-((fl-0.83)/0.035)**2)*np.clip(0.5+0.5*gnoise(mm(25),mm(2),20),0,1)*0.35
shin_col=lerp(shin_col,C(170,60,140)[None,None],refl[...,None])
col=lerp(col,shin_col,shin[...,None])
hid=np.array([hi_depth(x) for x in sc],np.float32)[None,:]
gv=((fl>F_HI0)&(fl<F_HI1)).astype(np.float32)*hid
gedge=(np.exp(-((fl-F_HI0)*wcol[None,:]/PX/mm(0.12))**2)+np.exp(-((fl-F_HI1)*wcol[None,:]/PX/mm(0.12))**2))*hid
col=col*(1-0.35*gv[...,None])
col=lerp(col,C(220,110,190)[None,None],(gedge*0.5)[...,None])
# ligne du shinogi (arête) : fin liseré clair
sl_=np.exp(-((fl-F_SHIN)*wcol[None,:]/PX/mm(0.08))**2)
col=lerp(col,C(200,120,180)[None,None],(sl_*0.5)[...,None])
# kissaki plus lumineux
kis=np.clip((s-(LB-KL-0.01))/0.03,0,1)*(1-shin)*0.35
col=lerp(col,C(246,150,210)[None,None],kis[...,None])
# hors lame (au-dessus du dos à la pointe) : recopier la dernière ligne valide (évite les bavures)
col=np.where(inb[...,None]>0,col,C(20,11,24)[None,None])
# ---------------- brillance ----------------
spec=0.80+0.15*ez+0.10*waves-0.05*alpha_all+0.1*shin
# ---------------- rééchantillonnage vers la vue UV (v = fraction locale) ----------------
vv=(np.arange(OH,dtype=np.float32)+0.5)/OH          # v image : ligne 0 = haut = dos
uu=(np.arange(OW,dtype=np.float32)+0.5)/OW
sx_=uu*LB; wl=np.array([wid(x) for x in sx_],np.float32)
map_x=np.broadcast_to((sx_/PX-0.5)[None,:],(OH,OW)).astype(np.float32)
hrow=(1-vv)[:,None]*wl[None,:]                       # hauteur physique
map_y=(GH-0.5-hrow/PX).astype(np.float32)
# antialias : réduire d'abord la grille horizontale
out=cv2.remap(cv2.GaussianBlur(col.astype(np.float32),(0,0),sigmaX=GW/OW*0.5,sigmaY=0.6),map_x,map_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
outs=cv2.remap(spec.astype(np.float32),map_x,map_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
save_rgb('/home/claude/sakura/tex/lame_d.png',np.clip(out,0,1))
save_gray('/home/claude/sakura/tex/lame_s.png',cv2.resize(np.clip(outs,0,1),(4096,256),interpolation=cv2.INTER_AREA))
save_rgb('/home/claude/sakura/tex/lame_n.png',np.full((256,256,3),(128,128,255),np.uint8))
# aperçus physiques (habaki et pointe)
def prev(a,b,name):
    p=col[:,int(a/PX):int(b/PX)]; p=cv2.resize(p,(int(p.shape[1]*0.25),int(p.shape[0]*0.25)),interpolation=cv2.INTER_AREA)
    cv2.imwrite('/home/claude/sakura/renders/'+name,cv2.cvtColor((np.clip(p,0,1)*255).astype(np.uint8),cv2.COLOR_RGB2BGR))
prev(0,0.16,'lame_habaki.png'); prev(LB-0.16,LB,'lame_pointe.png')
print('lame ok',len(items),'éléments')
