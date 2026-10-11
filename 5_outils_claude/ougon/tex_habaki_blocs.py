# Habaki Ougon : or poli, gravure ciselée de blocs arrondis empilés (idéogrammes anciens), volutes, petits carrés/cercles.
# u = x le long de l'arme (côté lame -> tsuba, 34 mm), v = z (0 = bas/tranchant, 1 = haut/dos, 50 mm)
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/ougon/scripts')
from tex_common import *
rng=np.random.default_rng(204)
PX=0.00002; WU,WV=0.034,0.050
GW=int(WU/PX); GH=int(WV/PX)
def mm(x): return x/1000/PX
F=16; SH=4
L=np.zeros((GH,GW),np.float32)
def pt(x,y): return (int(x*F),int(y*F))
def rrect_pts(cx,cy,w,h,r,rot):
    pts=[]
    for (ax,ay,a0) in ((w/2-r,-h/2+r,-math.pi/2),(w/2-r,h/2-r,0),(-w/2+r,h/2-r,math.pi/2),(-w/2+r,-h/2+r,math.pi)):
        for a in np.linspace(a0,a0+math.pi/2,8): pts.append((ax+math.cos(a)*r,ay+math.sin(a)*r))
    pts=np.array(pts); ca,sa=math.cos(rot),math.sin(rot)
    return np.stack([cx+pts[:,0]*ca-pts[:,1]*sa, cy+pts[:,0]*sa+pts[:,1]*ca],1)
TH=int(mm(0.32))
def block(cx,cy,w,h,rot):
    p=rrect_pts(cx,cy,w,h,min(w,h)*rng.uniform(0.18,0.35),rot)
    m=np.zeros((GH,GW),np.uint8); cv2.fillPoly(m,[(p*F).astype(np.int32)],1,cv2.LINE_AA,SH)
    L[m>0]=0                                                # le bloc du dessus cache les traits dessous
    cv2.polylines(L,[(p*F).astype(np.int32)],True,1.0,TH,cv2.LINE_AA,SH)
    k=rng.integers(0,4); ca,sa=math.cos(rot),math.sin(rot)
    def T(u,v): return (cx+u*ca-v*sa, cy+u*sa+v*ca)
    if k==0:   # trait intérieur
        a=rng.uniform(-.25,.25)*h; cv2.line(L,pt(*T(-w*0.32,a)),pt(*T(w*0.32,a)),1.0,TH,cv2.LINE_AA,SH)
    elif k==1: # petit cercle
        cv2.circle(L,pt(*T(rng.uniform(-.2,.2)*w,rng.uniform(-.2,.2)*h)),int(min(w,h)*0.18*F),1.0,TH,cv2.LINE_AA,SH)
    elif k==2: # crochet
        q=np.array([T(-w*0.25,-h*0.2),T(w*0.15,-h*0.2),T(w*0.15,h*0.25)])
        cv2.polylines(L,[(q*F).astype(np.int32)],False,1.0,TH,cv2.LINE_AA,SH)
def curl(cx,cy,R,rot,sgn):
    th=np.linspace(0,2.0*math.pi,50); rad=R*(1-th/(2.6*math.pi))
    q=np.stack([cx+np.cos(sgn*th+rot)*rad,cy+np.sin(sgn*th+rot)*rad],1)
    cv2.polylines(L,[(q*F).astype(np.int32)],False,1.0,TH,cv2.LINE_AA,SH)
def wave(cx,cy,Lw,rot):
    t=np.linspace(0,1,30); q=np.stack([(t-.5)*Lw,np.sin(t*math.pi*2)*Lw*0.12],1)
    ca,sa=math.cos(rot),math.sin(rot); q=np.stack([cx+q[:,0]*ca-q[:,1]*sa,cy+q[:,0]*sa+q[:,1]*ca],1)
    cv2.polylines(L,[(q*F).astype(np.int32)],False,1.0,TH,cv2.LINE_AA,SH)
# amas central (empilement : grands blocs d'abord, petits ensuite)
cxc,cyc=GW*0.56,GH*0.50
items=[]
for k in range(34):
    ang=rng.uniform(0,6.28); rr=math.sqrt(rng.uniform(0,1))
    x=cxc+math.cos(ang)*rr*GW*0.30; y=cyc+math.sin(ang)*rr*GH*0.33
    s=mm(rng.uniform(3.5,8.0))*(1.1-0.5*rr)
    items.append((s,x,y))
items.sort(reverse=True)
for s,x,y in items:
    block(x,y,s*rng.uniform(0.8,1.3),s*rng.uniform(0.6,1.0),rng.uniform(-0.45,0.45))
for k in range(9):
    ang=rng.uniform(0,6.28); x=cxc+math.cos(ang)*GW*rng.uniform(.1,.32); y=cyc+math.sin(ang)*GH*rng.uniform(.1,.36)
    (curl if k%2 else wave)(x,y,mm(rng.uniform(2.0,3.5)) if k%2 else mm(rng.uniform(5,8)),rng.uniform(0,6.28),*( (1 if k%4==1 else -1,) if k%2 else ()))
for k in range(14):  # petits carrés / cercles autour
    ang=rng.uniform(0,6.28); x=cxc+math.cos(ang)*GW*rng.uniform(.30,.42); y=cyc+math.sin(ang)*GH*rng.uniform(.33,.45)
    if rng.random()<0.5: block(x,y,mm(rng.uniform(1.5,2.4)),mm(rng.uniform(1.5,2.4)),rng.uniform(-.4,.4))
    else: cv2.circle(L,pt(x,y),int(mm(rng.uniform(0.7,1.1))*F),1.0,TH,cv2.LINE_AA,SH)
# filet de bordure gravé
b=mm(1.3); cv2.rectangle(L,pt(b,b),pt(GW-b,GH-b),1.0,int(mm(0.25)),cv2.LINE_AA,SH)
# ---------------- rendu : sillons ciselés dans l'or poli ----------------
depth=cv2.GaussianBlur(L,(0,0),mm(0.06))
h=-depth*1.0
yy=(np.arange(GH,dtype=np.float32)/GH)[:,None]; xx=(np.arange(GW,dtype=np.float32)/GW)[None,:]
brushed=cv2.GaussianBlur(rng.normal(0,1,(GH,GW)).astype(np.float32),(0,0),sigmaX=mm(3),sigmaY=mm(0.02)); brushed/=brushed.std()
h=h+0.004*brushed
gy,gx=np.gradient(cv2.GaussianBlur(depth,(0,0),mm(0.05)))
bev=np.clip((gx*0.6-gy)*mm(0.3)*1.5,-1,1)          # lumière venant du haut-gauche
# or poli : bande de reflet + assombrissement des bords
refl=0.80+0.38*np.exp(-((yy-0.62)/0.16)**2)+0.10*np.exp(-((yy-0.25)/0.08)**2)
refl=refl*(0.92+0.08*np.cos((xx-0.5)*math.pi))
gold=np.array([212,158,58],np.float32)/255
col=gold[None,None]*refl[...,None]*(1+0.025*brushed[...,None])
groove=np.array([96,62,16],np.float32)/255
col=col*(1-0.75*depth[...,None])+groove[None,None]*0.75*depth[...,None]
col=col+np.clip(bev,0,1)[...,None]*np.array([0.30,0.25,0.12],np.float32)-np.clip(-bev,0,1)[...,None]*np.array([0.25,0.18,0.06],np.float32)
OW,OH=1024,1024
save_rgb('/home/claude/ougon/tex/habaki_d.png',cv2.resize(np.clip(col,0,1),(OW,OH),interpolation=cv2.INTER_AREA))
save_rgb('/home/claude/ougon/tex/habaki_n.png',cv2.resize(normal_from_height(h,mm(0.2),wrap=False),(OW,OH),interpolation=cv2.INTER_AREA))
save_gray('/home/claude/ougon/tex/habaki_s.png',cv2.resize(np.clip(0.95-0.45*depth,0,1),(512,512),interpolation=cv2.INTER_AREA))
cv2.imwrite('/home/claude/ougon/renders/p_habaki_tex.png',cv2.cvtColor((np.clip(cv2.resize(col,(GW//3,GH//3),interpolation=cv2.INTER_AREA),0,1)*255).astype(np.uint8),cv2.COLOR_RGB2BGR))
print('habaki ok',GW,GH)
