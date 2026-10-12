# Bois PHOTO-REALISTE : texture construite a partir du bois de la photo de reference (fut + crosse)
import numpy as np, cv2, sys
sys.path.insert(0,'/home/claude/tanegashima/scripts')
from tex_common import *
T='/home/claude/tanegashima/tex/'
ref=cv2.cvtColor(cv2.imread('/home/claude/tanegashima/ref/ref_tanegashima.png'),cv2.COLOR_BGR2RGB).astype(np.float32)/255
rng=np.random.default_rng(5)
# bandes de bois pur (veines horizontales) : fut entre les bagues, sans la plaquette de fer
strips=[]
def take(y0,y1,x0,x1):
    s=ref[y0:y1,x0:x1].copy()
    strips.append(s)
take(262,289,1045,1300); take(262,289,1385,1840); take(262,292,780,985); take(262,289,1385,1840)
# retirer l'eclairage de la photo (garder la couleur moyenne + le veinage)
target=np.median(np.concatenate([s.reshape(-1,3) for s in strips]),axis=0)
def flatten(s):
    p=60
    sp=cv2.copyMakeBorder(s,p,p,p,p,cv2.BORDER_REFLECT)
    low=cv2.GaussianBlur(sp,(0,0),sigmaX=40,sigmaY=12)[p:-p,p:-p]
    f=s/np.maximum(low,1e-3)*target
    return np.clip(f,0,1)
strips=[flatten(s) for s in strips]
W,H=2048,1024; SC=2.3
out=np.zeros((H,W,3),np.float32); wsum=np.zeros((H,W,1),np.float32)
y=0
while y<H:
    s=strips[rng.integers(len(strips))]
    s=cv2.resize(s,(int(s.shape[1]*SC),int(s.shape[0]*SC)),interpolation=cv2.INTER_CUBIC)
    if rng.random()<0.5: s=s[:,::-1]
    if rng.random()<0.5: s=s[::-1]
    h=s.shape[0]
    # remplir la largeur en repetant la bande avec fondu
    row=np.zeros((h,W+400,3),np.float32); x=0
    while x<W+400:
        seg=s[:,rng.integers(0,max(1,s.shape[1]//3)):]
        n=min(seg.shape[1],W+400-x)
        a=np.ones((1,n,1),np.float32)
        f=min(80,n//4)
        if x>0: a[:, :f,0]=np.linspace(0,1,f)
        row[:,x:x+n]=row[:,x:x+n]*(1-a)+seg[:,:n]*a
        x+=n-f
    row=row[:, :W+200]
    # raccord horizontal parfait (tuile)
    f=200; blend=np.linspace(0,1,f)[None,:,None]
    row[:, :f]=row[:, :f]*blend+row[:,W:W+f]*(1-blend); row=row[:, :W]
    wy=np.ones((h,1,1),np.float32); fy=min(14,h//3)
    wy[:fy,0,0]=np.linspace(0.05,1,fy); wy[-fy:,0,0]=np.linspace(1,0.05,fy)
    y1=min(H,y+h); out[y:y1]+=row[:y1-y]*wy[:y1-y]; wsum[y:y1]+=wy[:y1-y]
    y+=h-2*fy
out=out/np.maximum(wsum,1e-4)
# raccord vertical
f=40; b=np.linspace(0,1,f)[:,None,None]
out[:f]=out[:f]*b+out[-f:][::-1]*(1-b)
lum=out.mean(2)
hp=lum-cv2.GaussianBlur(lum,(0,0),3)
save_rgb(T+'bois_d.png',np.clip(out,0,1))
save_rgb(T+'bois_n.png',normal_from_height(hp*6.0,2.5,wrap=True))
save_gray(T+'bois_s.png',np.clip(0.18+hp*2+0.10*(lum/lum.mean()-1),0.05,0.5))
cv2.imwrite('/home/claude/tanegashima/renders/p_bois.png',cv2.cvtColor((np.clip(out[:400,:1400],0,1)*255).astype(np.uint8),cv2.COLOR_RGB2BGR))
print('bois photo ok', (out.reshape(-1,3).mean(0)*255).round())
