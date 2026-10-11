# Tranche du tsuba Ougon : laque noire + motifs d'or (idéogrammes, feuilles, petits blasons) entre deux filets d'or.
import numpy as np, cv2, math, sys
sys.path.insert(0,'/home/claude/ougon/scripts')
from tex_common import *
from rim_params import *
rng=np.random.default_rng(12)
PX=0.00003
GW=int(round(TILE_W/PX)); GH=int(round(BAND_W/PX))
F=16; SH=4
def P(x,y): return (int(x*F),int(y*F))
mask=np.zeros((GH,GW),np.uint8)
def stroke(pts,w):
    pts=np.array(pts,np.float32)
    for dx in (-GW,0,GW):
        q=pts+[dx,0]
        for i in range(len(q)-1): cv2.line(mask,P(*q[i]),P(*q[i+1]),255,max(1,int(w)),cv2.LINE_AA,SH)
def glyph(cx,cy,sz):
    for _ in range(rng.integers(4,7)):
        k=rng.integers(0,4); a=rng.uniform(-.4,.4); b=rng.uniform(-.4,.4)
        if k==0: pts=[(cx+(-.45+.9*t)*sz,cy+(a+.05*math.sin(t*3))*sz) for t in np.linspace(0,1,8)]
        elif k==1: pts=[(cx+(a+.04*math.sin(t*3))*sz,cy+(-.45+.9*t)*sz) for t in np.linspace(0,1,8)]
        elif k==2: pts=[(cx+(a+.4*t)*sz,cy+(b+.4*t)*sz) for t in np.linspace(0,1,6)]
        else: pts=[(cx+(a-.4*t)*sz,cy+(b+.45*t*t)*sz) for t in np.linspace(0,1,6)]
        stroke(pts,sz*0.09)
def leaf(cx,cy,L,W,rot):
    t=np.linspace(0,1,20); w=np.sin(np.pi*t)**0.7*W
    poly=np.concatenate([np.stack([t*L,w],1),np.stack([t*L,-w],1)[::-1]])
    R=np.array([[math.cos(rot),-math.sin(rot)],[math.sin(rot),math.cos(rot)]])
    poly=poly@R.T+[cx,cy]
    for dx in (-GW,0,GW): cv2.fillPoly(mask,[((poly+[dx,0])*F).astype(np.int32)],255,cv2.LINE_AA,SH)
def mon(cx,cy,R):
    for dx in (-GW,0,GW): cv2.circle(mask,P(cx+dx,cy),int(R*F),255,max(1,int(R*0.18)),cv2.LINE_AA,SH)
    for k in range(5):
        a=k*2*math.pi/5; leaf(cx+math.cos(a)*R*0.1,cy+math.sin(a)*R*0.1,R*0.65,R*0.22,a)
yc=GH*0.5; band=GH*0.30
x=GW*0.04
while x<GW:
    r=rng.random()
    if r<0.5: glyph(x,yc+rng.uniform(-.15,.15)*band,band*rng.uniform(0.7,0.95)); x+=band*rng.uniform(0.9,1.2)
    elif r<0.8:
        for j in range(3): leaf(x+j*band*0.25,yc+rng.uniform(-.2,.2)*band,band*rng.uniform(.4,.6),band*0.13,rng.uniform(-2.6,-0.5) if j%2 else rng.uniform(0.5,2.6))
        x+=band*1.0
    else: mon(x+band*0.35,yc,band*0.38); x+=band*1.0
m=mask.astype(np.float32)/255
v=(np.arange(GH,dtype=np.float32)+0.5)/GH
edgeg=((v<0.13)|(v>0.87)).astype(np.float32)[:,None]*np.ones((1,GW),np.float32)
fil=(np.exp(-((v-0.16)/0.008)**2)+np.exp(-((v-0.84)/0.008)**2))[:,None]*np.ones((1,GW),np.float32)
gm=np.clip(np.maximum(np.maximum(m,edgeg),fil),0,1)
dist=cv2.distanceTransform((gm>0.5).astype(np.uint8),cv2.DIST_L2,5)
h=np.sqrt(np.minimum(dist/6,1))*gm
h=cv2.GaussianBlur(h,(0,0),1.0)
n=normal_from_height(h,8.0,wrap=False).astype(np.float32)/127.5-1
shade=np.clip(0.75-n[...,0]*0.45+n[...,1]*0.45,0.35,1.35)
noise=cv2.GaussianBlur(rng.normal(0,1,(GH,GW)).astype(np.float32),(0,0),20); noise/=noise.std()
black=np.array([12,11,10],np.float32)/255*(1+0.1*noise[...,None])
gold=np.array([212,162,62],np.float32)/255*shade[...,None]
col=black*(1-gm[...,None])+gold*gm[...,None]
OW,OH=1024,512
save_rgb('/home/claude/ougon/tex/rim_d.png',cv2.resize(np.clip(col,0,1),(OW,OH),interpolation=cv2.INTER_AREA))
save_rgb('/home/claude/ougon/tex/rim_n.png',cv2.resize(normal_from_height(h,8.0,wrap=False),(OW,OH),interpolation=cv2.INTER_AREA))
save_gray('/home/claude/ougon/tex/rim_s.png',cv2.resize(np.clip(0.8*(1-gm)+0.95*gm,0,1),(512,256),interpolation=cv2.INTER_AREA))
np.save('/home/claude/ougon/tex/rim_h.npy',np.zeros((128,1024),np.float32))
cv2.imwrite('/home/claude/ougon/renders/p_rim.png',cv2.cvtColor((np.clip(cv2.resize(col,(GW//2,GH//2)),0,1)*255).astype(np.uint8),cv2.COLOR_RGB2BGR))
print('rim ok')
