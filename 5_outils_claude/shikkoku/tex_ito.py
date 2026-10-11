import numpy as np, cv2, sys
sys.path.insert(0,'/home/claude/shikkoku/scripts')
from tex_common import *; from params import *
W,Hh=4096,2048
rng=np.random.default_rng(5)
yy,xx=np.mgrid[0:Hh,0:W].astype(np.float32)
a=(xx+0.5)/W*N; b=(yy+0.5)/Hh*2.0
def ribbon_fields(a,b):
    p=a+b; q=a-b
    fp=p-np.floor(p); fq=q-np.floor(q)
    dp=np.abs(fp-np.round(fp)); dq=np.abs(fq-np.round(fq))
    inA=dp>=HA; inB=dq>=HA
    w=1-2*HA
    sA=(fp-HA)/w; sB=(fq-HA)/w
    # parité du croisement
    par=((np.floor(p)+np.floor(q))%2==0)
    return p,q,dp,dq,inA,inB,sA,sB,par
p,q,dp,dq,inA,inB,sA,sB,par=ribbon_fields(a,b)
both=inA&inB
overA=both&par; overB=both&~par
showA=(inA&~inB)|overA
showB=(inB&~inA)|overB
neither=~inA&~inB
# fenêtre (côtés) vs pli de crête
bfrac=np.abs(((b+0.5)%1)-0.5)  # 0 aux côtés? -> b=0.5,1.5 donnent 0
side_win=neither&( np.abs((b%1)-0.5)<0.5-1e-6 )&(np.abs(np.round(b-0.5)-(b-0.5))<HA+0.02)
# plus simple: les fenêtres de côté sont centrées sur b demi-entier, les plis sur b entier
cen_b=(np.floor((p+0.0))-np.floor(q))  # pas utilisé
bn=np.round((p-q)/2*2)/2  # centre b approx
win=neither&(np.abs(((b-0.5)%1.0))<0.5)  # placeholder
# centre du losange contenant: p,q arrondis
pc=np.round(p); qc=np.round(q)
bcen=(pc-qc)/2
is_side=(np.abs(bcen-np.round(bcen))>0.25)   # b demi-entier -> côté
win=neither&is_side
fold=neither&~is_side
def rib(s,along):
    prof=np.sqrt(np.clip(1-(2*s-1)**2,0,1))
    fib=np.abs(np.sin(np.pi*s*26+0.6*np.sin(along*40)))**0.6
    tw=0.5+0.5*np.sin(2*np.pi*(along*34+np.abs(s-0.5)*7))
    return prof,fib,tw
profA,fibA,twA=rib(sA,q); profB,fibB,twB=rib(sB,p)
# hauteur
h=np.zeros_like(a)
h=np.where(showA,0.28*profA+0.07*fibA+0.06*twA,h)
h=np.where(showB,0.28*profB+0.07*fibB+0.06*twB,h)
h=np.where(overA|overB,h+0.22,h)
# plis de crête : bourrelet arrondi + pli central
fs=np.clip(np.maximum(dp,dq)/HA,0,1)
foldh=0.30+0.12*np.sqrt(np.clip(1-fs**2,0,1))
h=np.where(fold,foldh+0.03*np.sin(2*np.pi*(b*30)),h)
h=np.where(win,0.0,h)
# ombre portée de la nappe du dessus sur celle du dessous (près du croisement)
shadow=np.zeros_like(a)
# A visible seul, B passe dessus au croisement voisin : distance au bord de B
nearB=(inA&~inB)&(dq<HA)
shadow=np.where(nearB, np.exp(-(HA-dq)/0.035), shadow)
nearA=(inB&~inA)&(dp<HA)
shadow=np.maximum(shadow,np.where(nearA, np.exp(-(HA-dp)/0.035),0))
shadow=np.where(overA|overB|fold|win,0,shadow)
h=cv2.GaussianBlur(h.astype(np.float32),(0,0),1.1)
nrm=normal_from_height(h,7.0)
# couleur ivoire soie
base=np.array([16,16,19],np.float32)/255
dk=np.array([3,3,4],np.float32)/255
prof=np.where(showA,profA,np.where(showB,profB,0.8))
fib=np.where(showA,fibA,np.where(showB,fibB,0.5))
tw=np.where(showA,twA,np.where(showB,twB,0.5))
lum=0.76+0.26*prof+0.34*(fib-0.5)+0.12*(tw-0.5)
lum*=1-0.45*shadow
lum=np.where(fold,0.93+0.04*np.sin(2*np.pi*b*30),lum)
noise=cv2.GaussianBlur(rng.normal(0,1,a.shape).astype(np.float32),(0,0),3); noise/=noise.std()
lum*=1+0.015*noise
col=base[None,None]*lum[...,None]
col=np.where(win[...,None],dk[None,None]*0.6,col)
# bord des rubans légèrement grisé
edge=np.where(showA,np.abs(2*sA-1),np.where(showB,np.abs(2*sB-1),0))
col=col*(1-0.18*(edge[...,None]**6))
save_rgb('/home/claude/shikkoku/tex/ito_d.png',np.flipud(col))
nrm2=np.flipud(nrm).copy(); nrm2[...,1]=255-nrm2[...,1]
save_rgb('/home/claude/shikkoku/tex/ito_n.png',nrm2)
save_gray('/home/claude/shikkoku/tex/ito_s.png',np.flipud(0.08+0.07*fib*(~win)+0.05*prof))
np.save('/home/claude/shikkoku/tex/ito_h.npy',cv2.resize(h,(W//4,Hh//4),interpolation=cv2.INTER_AREA))
print('ito ok', win.mean(), fold.mean())
