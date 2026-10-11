import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/shiden/scripts')
from tex_common import *
rng=np.random.default_rng(3)
# ---------- samegawa (galuchat) 512 seamless ----------
S=512
pts=[]
for t in range(20000):
    r=rng.uniform(9,26) if rng.random()<0.85 else rng.uniform(4,8)
    c=rng.uniform(0,S,2); ok=True
    for (c2,r2) in pts:
        d=np.abs(c-c2); d=np.minimum(d,S-d)
        if np.hypot(*d)<r+r2+1.0: ok=False;break
    if ok: pts.append((c,r))
h=np.zeros((S,S),np.float32)
yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
for (c,r) in pts:
    for dx in (-S,0,S):
        for dy in (-S,0,S):
            cx,cy=c[0]+dx,c[1]+dy
            if cx<-r or cx>S+r or cy<-r or cy>S+r: continue
            x0,x1=int(max(0,cx-r-1)),int(min(S,cx+r+2)); y0,y1=int(max(0,cy-r-1)),int(min(S,cy+r+2))
            d=np.sqrt((xx[y0:y1,x0:x1]-cx)**2+(yy[y0:y1,x0:x1]-cy)**2)/r
            v=np.sqrt(np.clip(1-d**2,0,1))
            h[y0:y1,x0:x1]=np.maximum(h[y0:y1,x0:x1],v)
h=blur_wrap(h,0.8)
nrm=normal_from_height(h,5.0)
nv=nrm.astype(np.float32)/127.5-1
shade=np.clip(0.8-nv[...,0]*0.3+nv[...,1]*0.3,0.4,1.2)
pearl=np.array([222,218,230],np.float32)/255
gap=np.array([110,104,122],np.float32)/255
m=np.clip(h*3,0,1)[...,None]
col=gap*(1-m)+pearl*m*(0.85+0.15*h[...,None])*shade[...,None]
save_rgb('/home/claude/shiden/tex/same_d.png',col); save_rgb('/home/claude/shiden/tex/same_n.png',nrm)
save_gray('/home/claude/shiden/tex/same_s.png',0.30+0.50*h)
print('same ok',len(pts))
# ---------- tsuba face 1024 ----------
S=1024; SS=2048; F=16; SH=4
c=SS/2; R=SS/2
yy,xx=np.mgrid[0:SS,0:SS].astype(np.float32)
rr=np.sqrt((xx-c)**2+(yy-c)**2)/R
ang=np.arctan2(yy-c,xx-c)
gold=np.zeros((SS,SS),np.uint8); petal=np.zeros((SS,SS),np.float32); carve=np.zeros((SS,SS),np.uint8)
def P(p): return tuple(int(v*F) for v in p)
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
TS_FL=[]
def kiku(cx,cy,r,rot): TS_FL.append((cx,cy,r,rot))
# couronne de 6 grandes fleurs + 6 petites, rinceaux circulaires entre
for i in range(6):
    a=i*math.pi/3+0.2
    kiku(c+math.cos(a)*R*0.62, c+math.sin(a)*R*0.62, R*0.17, rng.uniform(0,6))
    a2=a+math.pi/6
    kiku(c+math.cos(a2)*R*0.47, c+math.sin(a2)*R*0.47, R*0.085, rng.uniform(0,6))
# rinceaux: arcs ondulés
for ring_r,amp,ph,th in [(0.80,0.035,0,12),(0.47,0.03,1.3,9)]:
    t=np.linspace(0,2*np.pi,900)
    rad=(ring_r+amp*np.sin(t*12+ph))*R
    pts=np.stack([c+np.cos(t)*rad,c+np.sin(t)*rad],1)
    cv2.polylines(gold,[(pts*F).astype(np.int32)],True,255,th,cv2.LINE_AA,SH)
    for k in range(0,900,25):   # feuilles
        b=pts[k]; d=pts[(k+1)%900]-pts[k]; a0=math.atan2(d[1],d[0])+(1 if (k//25)%2 else -1)*0.9
        L=R*0.075; Wd=R*0.022
        tt=np.linspace(0,1,20); w=np.sin(np.pi*tt)**0.8*Wd
        poly=np.concatenate([np.stack([tt*L,w],1),np.stack([tt*L,-w],1)[::-1]])
        Rm=np.array([[math.cos(a0),-math.sin(a0)],[math.sin(a0),math.cos(a0)]])
        poly=poly@Rm.T+b
        cv2.fillPoly(gold,[(poly*F).astype(np.int32)],255,cv2.LINE_AA,SH)
        cv2.line(carve,P(b),P(b+Rm@np.array([L*0.85,0])),255,2,cv2.LINE_AA,SH)
TS_FL.append((c,c,R*0.05,0.3))
for k in range(7):
    a_=k*2*math.pi/7; q=0.135*R
    TS_FL.append((c+math.cos(a_)*q,c+math.sin(a_)*q,R*0.042,rng.uniform(0,6.28)))
g=gold.astype(np.float32)/255
dist=cv2.distanceTransform((gold>127).astype(np.uint8),cv2.DIST_L2,5)
h=np.sqrt(np.minimum(dist/9,1))*0.75*g+cv2.GaussianBlur(petal,(0,0),3)*0.45*g-cv2.GaussianBlur(carve.astype(np.float32)/255,(0,0),1.2)*0.55*g
# zones : centre or lisse (seppa) r<0.24, bord or (fukurin) r>0.9 avec cordelette
center=(rr<0.235).astype(np.float32); rim=(rr>0.905).astype(np.float32)
rope=0.5+0.5*np.sin(ang*180+ (rr-0.95)*300)
h=h*(1-center)*(1-rim)+center*0.62+rim*(0.55+0.25*np.sqrt(np.clip(1-((rr-0.952)/0.048)**2,0,1))+0.12*rope)
# fer : texture martelée (tsuchime)
ham=cv2.GaussianBlur(rng.normal(0,1,(SS,SS)).astype(np.float32),(0,0),6); ham/=ham.std()
h+= (1-g)*(1-center)*(1-rim)*ham*0.04
h=cv2.GaussianBlur(h.astype(np.float32),(0,0),1.0)
hs=cv2.resize(h,(S,S),interpolation=cv2.INTER_AREA)
gm=cv2.resize(np.maximum(np.maximum(g,center),rim),(S,S),interpolation=cv2.INTER_AREA)
cs=cv2.resize(cv2.GaussianBlur(carve.astype(np.float32)/255,(0,0),1),(S,S),interpolation=cv2.INTER_AREA)
nrm=normal_from_height(hs,9.0,wrap=False)
nv=nrm.astype(np.float32)/127.5-1
shade=np.clip(nv[...,0]*-0.35+nv[...,1]*0.35+0.75,0.3,1.25)
noise=cv2.resize(ham,(S,S))
iron=np.array([22,20,23],np.float32)/255*(1+0.07*noise[...,None])
gold_lo=np.array([150,104,38],np.float32)/255; gold_mid=np.array([206,160,72],np.float32)/255; gold_hi=np.array([246,214,140],np.float32)/255
t=np.clip((hs-0.15)/0.75,0,1)[...,None]
gcol=np.where(t<0.5,gold_lo+(gold_mid-gold_lo)*t*2,gold_mid+(gold_hi-gold_mid)*(t-0.5)*2)*shade[...,None]*(1-0.55*cs[...,None])
col=iron*(1-gm[...,None])+gcol*gm[...,None]
from shiden_draw import flowers as sk_flowers
SCL=S/SS
items=[(x*SCL,y*SCL,r*SCL*1.05,rot,int(rng.integers(3))) for (x,y,r,rot) in TS_FL]
frgb,fa,fh=sk_flowers(S,items,wrap=False)
nrm=normal_from_height(hs*(1-fa)+(0.35+0.55*fh)*fa,9.0,wrap=False)
col=col*(1-fa[...,None])+frgb*fa[...,None]
save_rgb('/home/claude/shiden/tex/tsuba_d.png',col); save_rgb('/home/claude/shiden/tex/tsuba_n.png',nrm)
save_gray('/home/claude/shiden/tex/tsuba_s.png',(0.4*(1-gm)+0.95*gm-0.35*cs)*(1-fa)+0.55*fa)
print('tsuba ok')
