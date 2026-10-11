# Fleurs de cerisier (5 pétales échancrés) pour les textures de monture : couleur, opacité, relief
import numpy as np, math
def C(r,g,b): return np.array([r,g,b],np.float32)/255
PINKS=[(C(252,206,228),C(222,88,158)),(C(255,228,240),C(236,128,184)),(C(246,176,210),C(204,62,140))]
def flowers(S,items,wrap=True,gold_rim=True):
    """items: liste (cx,cy,R,rot,palette). Renvoie rgb (S,S,3), alpha (S,S), height (S,S)."""
    rgb=np.zeros((S,S,3),np.float32); al=np.zeros((S,S),np.float32); hh=np.zeros((S,S),np.float32)
    offs=[(dx,dy) for dx in (-S,0,S) for dy in (-S,0,S)] if wrap else [(0,0)]
    for (cx0,cy0,R,rot,pal) in items:
        light,deep=PINKS[pal]
        for dx,dy in offs:
            cx,cy=cx0+dx,cy0+dy
            r=int(R*1.15)+3
            x1,x2=int(max(0,cx-r)),int(min(S,cx+r)); y1,y2=int(max(0,cy-r)),int(min(S,cy+r))
            if x2<=x1 or y2<=y1: continue
            X,Y=np.meshgrid(np.arange(x1,x2,dtype=np.float32)-cx,np.arange(y1,y2,dtype=np.float32)-cy)
            d=np.sqrt(X*X+Y*Y); th=np.arctan2(Y,X)-rot
            k=np.round(th/(2*math.pi/5)); phi=th-k*2*math.pi/5          # angle local dans le pétale
            # contour du pétale : arrondi, échancré au bout
            rb=R*(0.30+0.70*np.cos(np.clip(phi*2.5,-math.pi/2,math.pi/2))**0.45)
            rb=rb*(1-0.16*np.exp(-(phi/0.07)**2))
            sd=rb-d                                                     # >0 dedans
            a=np.clip(sd+0.5,0,1)
            t=np.clip(d/rb,0,1)
            c=deep[None,None]+(light-deep)[None,None]*(t**0.7)[...,None]
            # séparation entre pétales + nervures
            sep=np.exp(-((np.abs(phi)-math.pi/5)*d/1.2)**2)
            c=c*(1-0.35*sep[...,None])*(1-0.05*(0.5+0.5*np.cos(phi*24))[...,None]*(1-t)[...,None])
            # coeur
            core=np.clip(R*0.2-d+0.5,0,1)
            c=c*(1-core[...,None])+C(170,30,100)[None,None]*core[...,None]
            for j in range(7):
                aa=rot+j*2*math.pi/7+0.3; px,py=math.cos(aa)*R*0.28,math.sin(aa)*R*0.28
                st=np.clip(R*0.055-np.sqrt((X-px)**2+(Y-py)**2)+0.5,0,1)
                c=c*(1-st[...,None])+C(250,206,110)[None,None]*st[...,None]
            if gold_rim:   # liseré or (gravure)
                rim=np.clip(1.6-np.abs(sd),0,1)
                c=c*(1-rim[...,None])+C(214,168,80)[None,None]*rim[...,None]
                a=np.maximum(a,rim)
            dome=np.clip(sd/(R*0.25),0,1)**0.5*(0.7+0.3*(1-t))
            sl=(slice(y1,y2),slice(x1,x2))
            m=a>al[sl]
            rgb[sl]=np.where(m[...,None],c,rgb[sl]); al[sl]=np.maximum(al[sl],a); hh[sl]=np.maximum(hh[sl],dome*a)
    return rgb,al,hh
