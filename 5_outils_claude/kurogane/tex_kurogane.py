# Textures Kurogane : lame (biseaux d'acier martelé clair + centre noir rayé, rouille), fer (garde/pommeau), cuir (poignée)
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/kurogane/scripts')
from tex_common import *
from iron_common import hammered, render_iron
from params_k import *
T='/home/claude/kurogane/tex/'
rng=np.random.default_rng(7)
def noise(shape,s,seed):
    g=np.random.default_rng(seed).normal(0,1,shape).astype(np.float32); g=cv2.GaussianBlur(g,(0,0),s); return g/(g.std()+1e-6)
# ===================== LAME =====================
Wp,Hp=TEXW,TEXH
PX=Wp/LB                                   # px par metre (u)
PZ=Hp/W                                    # px par metre (v)
yy,xx=np.mgrid[0:Hp,0:Wp].astype(np.float32)
s=(xx+0.5)/PX                              # distance a la garde (m)
z=((Hp-1-yy)+0.5)/PZ-W/2                   # v=0 en bas de l'image
hwv=np.where(s<=LB-KT,W/2,W/2*np.clip(1-(s-(LB-KT))/KT,0,1))
inside=np.abs(z)<=hwv
# distance au bord (metres) : contour exact de la lame (cote + pointe en chanfrein)
out=np.zeros((Hp,Wp),np.uint8)
pts=[(0,0)]
for i in range(400):
    ss=LB*i/399; pts.append((ss*PX, (W/2-hw(ss))*PZ))
pts+= [(LB*PX,Hp/2)]+[(LB*(399-i)/399*PX, (W/2+hw(LB*(399-i)/399))*PZ) for i in range(400)]
mask=np.zeros((Hp,Wp),np.uint8)
cv2.fillPoly(mask,[np.array([(int(x),int(min(Hp-1,y))) for x,y in pts],np.int32)],1)
mask[:, :2]=1
mp=np.zeros((Hp+2,Wp+2),np.uint8); mp[1:-1,1:-1]=mask; mp[1:-1,0]=1      # bords haut/bas/pointe = fil ; cote garde ouvert
dist=cv2.distanceTransform(mp,cv2.DIST_L2,5)[1:-1,1:-1]/PZ   # m
bev=(dist<B*0.98).astype(np.float32)
bevs=np.clip((B-dist)/0.0015,0,1)                    # transition douce
# --- biseaux : acier clair martelé a facettes ---
cells=np.zeros((Hp,Wp),np.float32); n_c=int(Wp*Hp/900)
cx=rng.uniform(0,Wp,n_c).astype(np.float32); cy=rng.uniform(0,Hp,n_c).astype(np.float32)
sub=cv2.Subdiv2D((0,0,Wp,Hp))
for a,b in zip(cx,cy): sub.insert((float(min(a,Wp-1)),float(min(b,Hp-1))))
facets,centers=sub.getVoronoiFacetList([])
fac_h=np.zeros((Hp,Wp),np.float32); fac_c=np.zeros((Hp,Wp),np.float32)
for f,c in zip(facets,centers):
    gx,gy=rng.normal(0,1,2)*0.9; base=rng.uniform(-1,1)
    poly=np.array(f,np.int32)
    m=np.zeros((Hp,Wp),np.uint8); x0,y0,w_,h_=cv2.boundingRect(poly)
    x0=max(0,x0); y0=max(0,y0); x1=min(Wp,x0+w_+1); y1=min(Hp,y0+h_+1)
    if x1<=x0 or y1<=y0: continue
    sm=np.zeros((y1-y0,x1-x0),np.uint8); cv2.fillPoly(sm,[poly-[x0,y0]],1)
    X_,Y_=np.meshgrid(np.arange(x0,x1)-c[0],np.arange(y0,y1)-c[1])
    pl=(gx*X_+gy*Y_)*0.02
    fac_h[y0:y1,x0:x1]=np.where(sm>0,pl,fac_h[y0:y1,x0:x1]); fac_c[y0:y1,x0:x1]=np.where(sm>0,base,fac_c[y0:y1,x0:x1])
# --- rayures ---
scr=np.zeros((Hp,Wp),np.float32)
for i in range(3200):
    x=rng.uniform(0,Wp); y=rng.uniform(0,Hp); L=rng.uniform(8,90); a=rng.uniform(-0.6,0.6)+(math.pi/2 if rng.random()<0.2 else 0)
    cv2.line(scr,(int(x),int(y)),(int(x+L*math.cos(a)),int(y+L*math.sin(a))),float(rng.uniform(0.3,1)),1,cv2.LINE_AA)
scr=cv2.GaussianBlur(scr,(0,0),0.6)
# --- piqures et rouille ---
pits=np.zeros((Hp,Wp),np.float32)
for i in range(2600):
    cv2.circle(pits,(int(rng.uniform(0,Wp)),int(rng.uniform(0,Hp))),int(rng.uniform(1,3)),1.0,-1,cv2.LINE_AA)
rust=np.clip(noise((Hp,Wp),6,3)*0.6+noise((Hp,Wp),1.5,4)*0.5-1.1,0,1)
rust=np.maximum(rust,cv2.GaussianBlur(pits,(0,0),2)*0.6*(noise((Hp,Wp),10,5)>0.3))
cloud=noise((Hp,Wp),25,6)
# couleurs
steel=np.array([142,140,139],np.float32)/255
steel_dk=np.array([92,90,90],np.float32)/255
black=np.array([30,30,32],np.float32)/255
grey_cl=np.array([70,70,72],np.float32)/255
rustc=np.array([92,58,40],np.float32)/255
cb=steel[None,None]*(1+0.10*fac_c[...,None])
cb=cb*(1-0.55*np.clip(cloud*0.55-0.05,0,1))[...,None]
cb=cb*(1-0.55*cv2.GaussianBlur(pits,(0,0),0.8))[...,None]
cc=black[None,None]+(grey_cl-black)[None,None]*np.clip(cloud*0.22+0.18,0,1)[...,None]
cc=cc+0.10*scr[...,None]
col=cc*(1-bevs[...,None])+cb*bevs[...,None]
col=col+(steel_dk-col)*(np.exp(-((dist-B)/0.0012)**2)*0.6)[...,None]      # filet sombre a la jonction
col=col*(1-rust[...,None]*0.75)+rustc*(rust[...,None]*0.75)
col=col+0.12*scr[...,None]*bevs[...,None]
H=fac_h*bevs*1.0 - 0.6*cv2.GaussianBlur(pits,(0,0),0.7) - 0.15*scr + 0.05*noise((Hp,Wp),1.2,8)
nrm=normal_from_height(H,3.0,wrap=False)
spec=np.clip(0.30+0.50*bevs+0.15*scr-0.6*rust,0.05,1)
col[~inside]=col[inside].mean(0)
save_rgb(T+'lame_d.png',np.clip(col,0,1)); save_rgb(T+'lame_n.png',nrm); save_gray(T+'lame_s.png',spec)
cv2.imwrite('/home/claude/kurogane/renders/p_lame.png',cv2.cvtColor((np.clip(col[:, :2048],0,1)*255).astype(np.uint8),cv2.COLOR_RGB2BGR))
print('lame ok')
# ===================== FER (garde, virole, pommeau, rivets) =====================
S=1024; PXMM=S/120.0                       # tuile 12 cm
Hf=hammered((S,S),PXMM*1.6,rng,pits=1.2)
c,n8,sp=render_iron(Hf,PXMM*1.6,base=(52,52,56),hi=(150,150,156),lo=(10,10,12),nstrength=1.0)
ru=np.clip(noise((S,S),8,11)*0.7-0.9,0,1)
c=c*(1-0.6*ru[...,None])+rustc*(0.6*ru[...,None]); sp=np.clip(sp-0.4*ru,0,1)
save_rgb(T+'fer_d.png',c); save_rgb(T+'fer_n.png',n8); save_gray(T+'fer_s.png',sp)
print('fer ok')
# ===================== CUIR (poignee enroulee) =====================
S=1024; yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
# u = tour (1 tuile = 1 tour), v = longueur (1 tuile = 1 circonference) ; bandes en helice a ~38 deg, 3 bandes par tour
NB=4; t=(xx/S*NB + yy/S*NB)%1.0           # raccord parfait (u et v entiers)
prof=np.sin(np.pi*t)**0.55                                # bombe de chaque bande
over=np.clip((t-0.82)/0.18,0,1)                            # recouvrement (bord de la bande suivante)
H=prof*0.8-0.5*np.exp(-((t-0.0)/0.05)**2)-0.5*np.exp(-((t-1.0)/0.05)**2)+0.25*over
grain=noise((S,S),1.0,21)*0.06+noise((S,S),3,22)*0.05
H=H+grain
brown=np.array([62,40,26],np.float32)/255; dark=np.array([22,14,9],np.float32)/255; hi=np.array([104,72,46],np.float32)/255
k=np.clip(prof,0,1)
c=dark[None,None]+(brown-dark)[None,None]*k[...,None]
c=c+(hi-c)*(np.clip(prof-0.85,0,1)*3*np.clip(noise((S,S),12,23)*0.5+0.5,0,1))[...,None]
c=c*(1+0.08*noise((S,S),20,24))[...,None]
save_rgb(T+'cuir_d.png',np.clip(c,0,1)); save_rgb(T+'cuir_n.png',normal_from_height(H,6.0,wrap=True)); save_gray(T+'cuir_s.png',np.clip(0.25+0.25*prof,0,1))
print('cuir ok')
