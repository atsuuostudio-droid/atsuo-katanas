# Texture de la lame Kumo : vue de côté (u = longueur habaki -> pointe, v = tranchant -> dos)
# Nuages noirs à liseré argenté au milieu de la lame, tranchant miroir, shinogi-ji sombre + gorge (bo-hi)
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/kumo/scripts')
from tex_common import *
from blade_params import *
rng=np.random.default_rng(23)
PX=0.00006                       # 0,06 mm par pixel (espace physique uniforme)
GW=int(round(LB/PX)); GH=int(round(W0/PX))
print('grille',GW,GH)
yy,xx=np.mgrid[0:GH,0:GW].astype(np.float32)
s=(xx+0.5)*PX                    # m depuis le habaki
f=1-(yy+0.5)/GH                  # 0 tranchant, 1 dos (fraction de largeur)
wfrac=np.array([wid(si)/W0 for si in (np.arange(GW)+0.5)*PX],np.float32)[None,:]
# position physique au-dessus du tranchant, en m, à largeur locale
hz=f*W0                          # hauteur dans la grille (largeur nominale)
fl=hz/(wfrac*W0)                 # fraction de largeur locale (texture suit l'effilement)
def mm(x): return x/1000/PX       # mm -> pixels
# ---------------- nuages ----------------
dark=np.zeros((GH,GW),np.float32)     # masque nuage (couches)
shade=np.zeros((GH,GW),np.float32)    # éclairage interne
rim=np.zeros((GH,GW),np.float32)      # liserés blancs
def yof(frac,sx):  # fraction locale -> ligne pixel
    return (1-frac*wid(sx)/W0)*GH
x=mm(6)
clouds=[]
while x<GW-mm(55):
    L=mm(rng.uniform(38,80)); clouds.append((x,L)); x+=L+mm(rng.uniform(-6,10))
for (x0,L) in clouds:
    sx=(x0+L/2)*PX
    base_f=rng.uniform(0.27,0.30); top_f=rng.uniform(0.70,0.76)
    yb=yof(base_f,sx); yt=yof(top_f,sx); hh=yb-yt
    puffs=[]
    def env(cx): return math.sin(math.pi*min(max((cx-x0)/L,0.0),1.0))**0.5
    # rangée basse (petits moutons) d'abord, puis le coeur, puis la rangée haute (gros moutons)
    cx=x0+hh*0.15
    while cx<x0+L-hh*0.15:
        e=env(cx); r=hh*rng.uniform(0.20,0.28)*(0.6+0.4*e)
        puffs.append((cx, yb-r*0.85, r)); cx+=r*rng.uniform(1.1,1.5)
    for k in range(int(L/(hh*0.4))+1):
        cx=x0+L*(k+0.5)/(int(L/(hh*0.4))+1); e=env(cx)
        puffs.append((cx,(yt+yb)/2+hh*0.08,hh*0.33*(0.5+0.5*e)))
    top=[]
    cx=x0+hh*0.1
    while cx<x0+L-hh*0.1:
        e=env(cx); r=hh*rng.uniform(0.30,0.46)*(0.45+0.55*e)
        top.append((cx, yt+r*0.95+hh*(1-e)*0.45, r)); cx+=r*rng.uniform(0.9,1.3)
    rng.shuffle(top); puffs+=top
    for (cx,cy,r) in puffs:
        x1,x2=int(max(0,cx-1.6*r-3)),int(min(GW,cx+1.6*r+4)); y1,y2=int(max(0,cy-r-3)),int(min(GH,cy+r+4))
        if x2<=x1 or y2<=y1: continue
        X=xx[y1:y2,x1:x2]; Y=yy[y1:y2,x1:x2]
        d=np.sqrt(((X-cx)/1.55)**2+(Y-cy)**2)/r
        inside=np.clip((1-d)*r/1.2,0,1)                 # anti-crénelage
        # liseré : anneau fin, plus marqué en haut du mouton (lumière venant du dos)
        ang=np.arctan2(Y-cy,X-cx)                       # -pi/2 = haut
        topw=np.clip(0.35+0.65*(-np.sin(ang)),0,1)
        ring=np.exp(-((1-d)*r/mm(0.32))**2)*(d<1.02)*topw**1.5
        lit=np.clip(1-d,0,1)**0.5*np.clip(-(Y-cy)/r,0,1)
        old=dark[y1:y2,x1:x2]
        dark[y1:y2,x1:x2]=np.maximum(old,inside)
        # le nouveau mouton recouvre les liserés précédents
        rim[y1:y2,x1:x2]=np.clip(rim[y1:y2,x1:x2]*(1-inside)+ring,0,1)
        shade[y1:y2,x1:x2]=shade[y1:y2,x1:x2]*(1-inside)+lit*inside
# halo extérieur vaporeux autour des nuages
outer=cv2.GaussianBlur(dark,(0,0),mm(0.5))
halo=np.clip(outer-dark,0,1)*1.6
wisp_noise=cv2.GaussianBlur(rng.normal(0,1,(GH,GW)).astype(np.float32),(0,0),mm(0.6)); wisp_noise/=wisp_noise.std()
halo*=np.clip(0.7+0.5*wisp_noise,0,1.5)
# volutes de fumée argentée entre et autour des nuages
smoke=cv2.GaussianBlur(rng.normal(0,1,(GH,GW)).astype(np.float32),(0,0),sigmaX=mm(6),sigmaY=mm(0.5)); smoke/=smoke.std()
band=np.exp(-((f-0.47)/0.17)**2)
smoke=np.clip(smoke-0.6,0,1)*band*0.55
# ---------------- zones de la lame ----------------
# ligne de trempe (bord bas des nuages) : zone miroir du tranchant, ondulée
ham=0.235+0.022*np.sin(s/0.034*2*np.pi+1.3)+0.012*np.sin(s/0.013*2*np.pi)+0.012*cv2.GaussianBlur(rng.normal(0,1,(1,GW)).astype(np.float32),(0,0),mm(3))[0]*30
edge_zone=np.clip((ham-fl)/0.035+0.5,0,1)
shin=np.clip((fl-F_SHIN)*400+0.5,0,1)   # shinogi-ji
groove=((fl>F_HI0)&(fl<F_HI1)).astype(np.float32)*np.array([hi_depth(si) for si in (np.arange(GW)+0.5)*PX],np.float32)[None,:]
streak=cv2.GaussianBlur(rng.normal(0,1,(GH,GW)).astype(np.float32),(0,0),sigmaX=mm(8),sigmaY=mm(0.08)); streak/=streak.std()
mid=np.array([150,153,158],np.float32)/255
edgec=np.array([228,231,235],np.float32)/255
shinc=np.array([72,74,78],np.float32)/255
cloudc=np.array([22,23,26],np.float32)/255
cloudl=np.array([78,80,86],np.float32)/255
rimc=np.array([244,246,250],np.float32)/255
col=mid[None,None]*(1+0.05*streak[...,None])
# dégradé doux vers le haut de la zone médiane
col=col*(1-0.25*np.clip((fl-0.5)/0.2,0,1))[...,None]
col=col*(1-edge_zone[...,None])+edgec[None,None]*(1+0.025*streak[...,None])*edge_zone[...,None]
col=col*(1-smoke[...,None])+np.array([205,208,214],np.float32)[None,None]/255*smoke[...,None]
col=col*(1-halo[...,None]*0.8)+rimc[None,None]*halo[...,None]*0.8
cl=cloudc+(cloudl-cloudc)*np.clip(shade,0,1)[...,None]*0.3
col=col*(1-dark[...,None])+cl*dark[...,None]
col=col*(1-rim[...,None])+rimc[None,None]*rim[...,None]
col=col*(1-shin[...,None])+shinc[None,None]*(1+0.04*streak[...,None])*shin[...,None]
col=col*(1-0.45*groove[...,None])
spec=0.78+0.15*edge_zone-0.12*dark+0.2*rim
spec=np.where(shin>0.5,0.85,spec)
# ---------------- sortie ----------------
OW,OH=4096,512
img=cv2.resize(col.astype(np.float32),(OW,OH),interpolation=cv2.INTER_AREA)
save_rgb('/home/claude/kumo/tex/lame_d.png',img)
save_gray('/home/claude/kumo/tex/lame_s.png',cv2.resize(spec.astype(np.float32),(2048,256),interpolation=cv2.INTER_AREA))
save_rgb('/home/claude/kumo/tex/lame_n.png',np.full((256,256,3),(128,128,255),np.uint8))
cv2.imwrite('/home/claude/kumo/renders/lame_phys.png',cv2.cvtColor((np.clip(cv2.resize(col[:, :4200],(2100,292),interpolation=cv2.INTER_AREA),0,1)*255).astype(np.uint8),cv2.COLOR_RGB2BGR))
print('lame ok',len(clouds),'nuages')
