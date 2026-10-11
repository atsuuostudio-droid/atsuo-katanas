# Fleurs de cerisier "peintes" (laque maki-e) : naturelles, SANS contour or.
# Dégradé rose, nervures, échancrure, étamines dorées, perspective (fleurs inclinées), boutons, feuilles d'or.
import numpy as np, math
def C(r,g,b): return np.array([r,g,b],np.float32)/255
PAL=[ # (centre, milieu, bord)
 (C(84,30,150),C(150,84,226),C(214,180,255)),
 (C(100,40,170),C(170,110,240),C(228,206,255)),
 (C(70,24,130),C(128,64,210),C(196,156,250)),
]
GOLD_LO,GOLD_MID,GOLD_HI=C(80,80,92),C(168,168,182),C(236,236,248)
class Canvas:
    def __init__(s,S,wrap=True,bg=None):
        s.S=S; s.wrap=wrap
        s.rgb=np.zeros((S,S,3),np.float32) if bg is None else bg.copy()
        s.h=np.zeros((S,S),np.float32); s.spec=np.zeros((S,S),np.float32); s.mask=np.zeros((S,S),np.float32)
    def _patches(s,cx,cy,r):
        offs=[(dx,dy) for dx in (-s.S,0,s.S) for dy in (-s.S,0,s.S)] if s.wrap else [(0,0)]
        for dx,dy in offs:
            x,y=cx+dx,cy+dy
            x1,x2=int(max(0,x-r)),int(min(s.S,x+r)); y1,y2=int(max(0,y-r)),int(min(s.S,y+r))
            if x2<=x1 or y2<=y1: continue
            X,Y=np.meshgrid(np.arange(x1,x2,dtype=np.float32)+0.5-x,np.arange(y1,y2,dtype=np.float32)+0.5-y)
            yield (slice(y1,y2),slice(x1,x2)),X,Y
    def paint(s,sl,c,a,h=None,sp=None):
        s.rgb[sl]=s.rgb[sl]*(1-a[...,None])+c*a[...,None]
        if h is not None: s.h[sl]=s.h[sl]*(1-a)+h*a
        if sp is not None: s.spec[sl]=s.spec[sl]*(1-a)+sp*a
        s.mask[sl]=np.maximum(s.mask[sl],a)
    def flower(s,cx,cy,R,rot,pal=0,squash=1.0,tilt=0.0,rng=None):
        rng=rng or np.random.default_rng(int(cx*7+cy*13)%99991)
        cen,mid,edg=PAL[pal]
        sizes=rng.uniform(0.88,1.08,5); jit=rng.uniform(-0.12,0.12,5)
        for sl,X,Y in s._patches(cx,cy,R*1.25+3):
            # perspective : écrasement selon l'axe "tilt"
            ct,st=math.cos(tilt),math.sin(tilt)
            Xa=X*ct+Y*st; Ya=(-X*st+Y*ct)/squash
            d=np.sqrt(Xa*Xa+Ya*Ya); th=np.arctan2(Ya,Xa)-rot
            k=np.round(th/(2*math.pi/5)).astype(np.int32)%5
            phi=th-np.round(th/(2*math.pi/5))*2*math.pi/5-jit[k]
            Rk=R*sizes[k]
            rb=Rk*(0.28+0.72*np.cos(np.clip(phi*2.45,-math.pi/2,math.pi/2))**0.42)
            rb=rb*(1-0.17*np.exp(-(phi/0.075)**2))
            sd=(rb-d)*squash
            a=np.clip(sd+0.6,0,1)
            t=np.clip(d/rb,0,1)
            c=np.where((t<0.45)[...,None],cen+(mid-cen)*np.clip(t/0.45,0,1)[...,None]**0.8,mid+(edg-mid)*np.clip((t-0.45)/0.55,0,1)[...,None]**0.9)
            # nervures rayonnantes plus foncées vers le coeur
            vein=np.abs(np.sin(phi*11+0.4*np.sin(phi*3)))**8
            c=c*(1-0.16*(vein*(1-t)**0.7)[...,None])
            # reflet clair sur le haut du pétale
            hl=np.exp(-((phi-0.15)/0.22)**2)*np.exp(-((t-0.62)/0.18)**2)*0.35
            c=c+(1-c)*hl[...,None]
            # ombre entre pétales qui se chevauchent + bord légèrement plus foncé
            sep=np.exp(-((np.abs(phi)-math.pi/5+0.02)*d/1.4)**2)
            c=c*(1-0.30*sep[...,None])
            rim=np.clip(1.4-sd,0,1)*(sd>0)
            c=c*(1-0.22*rim[...,None])
            h=0.25+0.25*np.clip(sd/(R*0.3),0,1)
            s.paint(sl,c,a,h,np.full_like(a,0.55))
            # coeur + étamines dorées
            core=np.clip(R*0.17-d+0.6,0,1)
            s.paint(sl,np.broadcast_to(C(60,20,110),c.shape),core,0.4,np.full_like(a,0.4))
            for j in range(14):
                aa=rot+j*2*math.pi/14+0.11*math.sin(j*3.7); L=R*(0.30+0.08*math.sin(j*2.3))
                along=Xa*math.cos(aa)+Ya*math.sin(aa); perp=np.abs(-Xa*math.sin(aa)+Ya*math.cos(aa))
                fil=np.clip(0.9-perp,0,1)*((along>R*0.08)&(along<L))*0.85
                s.paint(sl,np.broadcast_to(C(220,220,235),c.shape),fil,0.5,np.full_like(a,0.8))
                dd=np.sqrt((Xa-math.cos(aa)*L)**2+(Ya-math.sin(aa)*L)**2)
                anth=np.clip(R*0.045+0.4-dd,0,1)
                s.paint(sl,np.broadcast_to(C(240,240,255),c.shape),anth,0.6,np.full_like(a,0.9))
    def bud(s,cx,cy,R,rot,pal=0):
        cen,mid,edg=PAL[pal]
        for sl,X,Y in s._patches(cx,cy,R*2.2+3):
            u=X*math.cos(rot)+Y*math.sin(rot); v=-X*math.sin(rot)+Y*math.cos(rot)
            d=np.sqrt((u/1.0)**2+(v/0.72)**2)
            a=np.clip((R-d)+0.6,0,1)*(u>-R*1.0)
            t=np.clip((u+R)/(2*R),0,1)
            c=mid+(edg-mid)*t[...,None]
            s.paint(sl,c,a,0.4+0.2*np.clip((R-d)/R,0,1),np.full_like(a,0.55))
            # calice
            cal=np.clip(0.8-np.abs(v)*0.9-(u+R*1.1)*0.0,0,1)*((u<-R*0.55)&(u>-R*1.6))
            s.paint(sl,np.broadcast_to(C(90,40,40),c.shape),cal*0.9)
    def gold_leaf(s,cx,cy,L,W,rot,curv=0.15):
        for sl,X,Y in s._patches(cx,cy,L+W+3):
            u=X*math.cos(rot)+Y*math.sin(rot); v=-X*math.sin(rot)+Y*math.cos(rot)
            v=v-curv*L*((u/L)**2-u/L)*4
            t=np.clip(u/L,0,1)
            prof=W*np.clip(np.sin(np.pi*t),0,1)**0.75
            sd=prof-np.abs(v)
            a=np.clip(sd+0.6,0,1)*((u>0)&(u<L))
            dome=np.clip(sd/max(W,1),0,1)**0.5
            vein=np.clip(1-np.abs(v)/1.0,0,1)*(t<0.95)
            side=np.abs(np.sin((u*1.2-np.abs(v)*1.6)/max(L,1)*18))**6*np.clip(sd/2,0,1)
            g=np.where((dome<0.5)[...,None],GOLD_LO+(GOLD_MID-GOLD_LO)*np.clip(dome*2,0,1)[...,None],GOLD_MID+(GOLD_HI-GOLD_MID)*np.clip(dome*2-1,0,1)[...,None])
            g=g*(1-0.45*vein[...,None])*(1-0.25*side[...,None])
            s.paint(sl,g,a,0.5+0.45*dome-0.2*vein,np.full_like(a,0.95))
    def branch(s,pts,w0,w1,col=None):
        col=C(46,30,26) if col is None else col
        pts=np.asarray(pts,np.float32); n=len(pts)
        for i in range(n-1):
            p,q=pts[i],pts[i+1]; w=w0+(w1-w0)*i/(n-1)
            c=(p+q)/2; L=np.linalg.norm(q-p)/2+w+2
            for sl,X,Y in s._patches(c[0],c[1],L):
                P=np.stack([X+c[0],Y+c[1]],-1); d_=q-p; ll=max(float(d_@d_),1e-6)
                tt=np.clip(((P-p)@d_)/ll,0,1); proj=p+tt[...,None]*d_
                dist=np.linalg.norm(P-proj,axis=-1)
                a=np.clip(w-dist+0.6,0,1)
                g=col*(0.8+0.4*np.clip(1-dist/max(w,1),0,1))[...,None]
                s.paint(sl,g,a,0.3+0.2*np.clip(1-dist/max(w,1),0,1),np.full_like(a,0.6))
