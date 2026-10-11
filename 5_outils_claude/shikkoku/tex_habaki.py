# Habaki Shikkoku : fer noir martelé, grandes vagues sculptées (faisceaux de lignes, crêtes en griffes d'écume, gouttelettes)
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/shikkoku/scripts')
from tex_common import *
from iron_common import hammered, render_iron
rng=np.random.default_rng(77)
PX=0.000015; WU,WV=0.034,0.050
GW=int(WU/PX); GH=int(WV/PX)
def mm(x): return x/1000/PX
H=hammered((GH,GW),mm(1.0),rng,pits=0.35)
xx=np.arange(GW,dtype=np.float32)[None,:]; yy=np.arange(GH,dtype=np.float32)[:,None]
def put(mask,h):
    global H
    H=H*(1-mask)+h*mask
def wave_layer(y0,amp,lam,ph,thick,nlines,lift):
    """bande de vague : entre deux courbes, lignes parallèles gravées, lèvre supérieure en relief"""
    xs=np.arange(GW,dtype=np.float32)
    top=y0-amp*np.sin(2*np.pi*xs/lam+ph)-mm(4)*(xs/GW)                 # monte vers la droite
    bot=top+thick
    T=top[None,:]; B=bot[None,:]
    inside=np.clip(np.minimum(yy-T,B-yy)+0.7,0,1)
    f=np.clip((yy-T)/np.maximum(B-T,1),0,1)                            # 0 en haut de la bande, 1 en bas
    h=lift+0.18*(1-f)**0.6
    gro=np.abs(np.sin(np.pi*f*nlines))                                 # sillons parallèles
    h=h-0.12*np.exp(-(gro/0.18)**2)*(f>0.06)
    lip=np.exp(-((yy-T)/mm(0.25))**2)                                  # lèvre de la crête
    h=h+0.08*lip
    put(inside,h)
    return top
def curl(cx,cy,R,sgn,lift):
    """crête qui s'enroule : spirale en relief + griffes d'écume + gouttelettes"""
    th=np.linspace(0,2.3*math.pi,90); rad=R*(1-th/(2.8*math.pi))
    pts=np.stack([cx+np.cos(sgn*th)*rad,cy-np.sin(th)*rad],1)
    m=np.zeros((GH,GW),np.float32)
    for i in range(len(pts)-1):
        w=max(2,int(mm(0.55)*(1-th[i]/(2.6*math.pi))))
        cv2.line(m,tuple(np.int32(pts[i])),tuple(np.int32(pts[i+1])),1.0,w,cv2.LINE_AA)
    d=cv2.GaussianBlur(m,(0,0),mm(0.08))
    put(np.clip(m*1.5,0,1),lift+0.20+0.10*d)
    for k in range(5):                                                  # griffes d'écume
        a=-math.pi*0.15+k*0.32; x0=cx+math.cos(a)*R*1.05*sgn; y0=cy-math.sin(a)*R*1.05
        L=R*rng.uniform(0.35,0.55); ang=a+0.9*sgn
        q=[(x0+math.cos(ang)*L*t*sgn+math.sin(t*3)*L*0.15,y0-math.sin(ang)*L*t) for t in np.linspace(0,1,10)]
        mm_=np.zeros((GH,GW),np.float32)
        for i in range(9): cv2.line(mm_,tuple(np.int32(q[i])),tuple(np.int32(q[i+1])),1.0,max(2,int(mm(0.35)*(1-i/10))),cv2.LINE_AA)
        put(np.clip(mm_*1.5,0,1),lift+0.22)
    for k in range(7):                                                  # gouttelettes
        a=rng.uniform(-0.2,1.6); r=R*rng.uniform(1.3,2.0)
        x0=cx+math.cos(a)*r*sgn; y0=cy-math.sin(a)*r; rr=mm(rng.uniform(0.25,0.45))
        dd=np.sqrt((xx-x0)**2+(yy-y0)**2)
        put(np.clip(rr-dd+0.7,0,1),lift+0.05+0.20*np.sqrt(np.clip(1-(dd/rr)**2,0,1)))
# trois couches de vagues (de l'arrière vers l'avant)
t1=wave_layer(GH*0.34,mm(4.0),GW*1.1,0.4,mm(11),8,0.08)
t2=wave_layer(GH*0.54,mm(4.5),GW*0.9,1.6,mm(12),9,0.12)
t3=wave_layer(GH*0.75,mm(4.0),GW*1.0,2.9,mm(14),10,0.16)
for (top,lift) in ((t1,0.08),(t2,0.12),(t3,0.16)):
    d=np.diff(top); xs_=[i for i in range(1,len(d)) if d[i-1]<0<=d[i] and GW*0.08<i<GW*0.92]
    if d[-1]<0: xs_.append(int(GW*0.86))
    if d[0]>0: xs_.append(int(GW*0.14))
    for x in xs_: curl(x,top[x]+mm(2.6),mm(2.8),1,lift)
# cadre : léger chanfrein des bords
de=np.minimum(np.minimum(xx,GW-1-xx),np.minimum(yy,GH-1-yy))
H=H-0.05*np.exp(-(de/mm(0.5))**2)
c,nrm8,spec=render_iron(H,mm(1.0),base=(30,30,34),hi=(104,104,112),lo=(5,5,7),nstrength=0.9)
OS=2048
save_rgb('/home/claude/shikkoku/tex/habaki_d.png',cv2.resize(c,(OS,OS),interpolation=cv2.INTER_AREA))
save_rgb('/home/claude/shikkoku/tex/habaki_n.png',cv2.resize(nrm8,(OS,OS),interpolation=cv2.INTER_AREA))
save_gray('/home/claude/shikkoku/tex/habaki_s.png',cv2.resize(spec,(1024,1024),interpolation=cv2.INTER_AREA))
cv2.imwrite('/home/claude/shikkoku/renders/p_habaki_tex.png',cv2.cvtColor((cv2.resize(c,(GW//4,GH//4),interpolation=cv2.INTER_AREA)*255).astype(np.uint8),cv2.COLOR_RGB2BGR))
print('habaki vagues ok')
