# Tsuba ajouré (sukashi) Shikkoku : masque 2D (1 = fer, 0 = jour) dans le repère normalisé du disque.
# x -> Y monde / (TRY+D0), y -> (Z-zm) / (TRZ+D0), y vers le dos de la lame. Seppa ~ ellipse (0.35, 0.69).
import numpy as np, cv2, math
S=2048
RIN=0.95
SH=4; K=1<<SH
def P(x,y): return (int(round((x*0.5+0.5)*S*K)),int(round((0.5-y*0.5)*S*K)))
def build(return_parts=False):
    m=np.zeros((S,S),np.uint8); beads=[]; crest=np.zeros((S,S),np.uint8)
    yy,xx=np.mgrid[0:S,0:S].astype(np.float32)
    X=(xx+0.5)/S*2-1; Y=1-(yy+0.5)/S*2
    rho=np.sqrt(X*X+Y*Y)
    px=lambda w: max(1,int(round(w*S/2)))
    def poly(pts,w,img=None): cv2.polylines(m if img is None else img,[np.array([P(*p) for p in pts],np.int32)],False,1,px(w),cv2.LINE_AA,SH)
    def arcpts(cx,cy,r,a0,a1,n=160): return [(cx+math.cos(a)*r,cy+math.sin(a)*r) for a in np.linspace(math.radians(a0),math.radians(a1),n)]
    def disc(cx,cy,r,img=None): cv2.circle(m if img is None else img,P(cx,cy),int(r*S/2*K),1,-1,cv2.LINE_AA,SH)
    def curl(cx,cy,r,a0,sgn,w,turns=1.5):
        pts=[]
        for t in np.linspace(0,turns*2*math.pi,140):
            rr=r*(1-t/(turns*2*math.pi+1.2)); a=math.radians(a0)+sgn*t; pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr))
        poly(pts,w); return pts
    W=0.046
    # régions : U (haut, vagues), L (milieu bas, vagues), B (bas, seigaiha)
    yb=lambda x: -0.06+0.10*np.abs(x)       # frontière U/L
    YB=-0.50                                 # frontière L/B
    RU=(Y>yb(X)); RL=(Y<=yb(X))&(Y>YB); RB=(Y<=YB)
    fan=np.zeros((S,S),np.uint8); sea=np.zeros((S,S),np.uint8)
    for s in (-1,1):
        cx,cy=s*0.40,0.02
        for r in np.arange(0.13,1.0,0.078):
            pts=arcpts(cx,cy,r,-40,140,260) if True else None
            poly([(cx+(p[0]-cx)*s,p[1]) for p in pts],W,fan)
        cx,cy=s*0.44,-0.50
        for r in np.arange(0.10,0.9,0.078):
            pts=arcpts(cx,cy,r,-10,120,240)
            poly([(cx+(p[0]-cx)*s,p[1]) for p in pts],W,sea)
    side=(np.abs(X)>0.30)
    m|=(fan*RU*side).astype(np.uint8)
    m|=(sea*RL*side).astype(np.uint8)
    # échines (frontières pleines, comme les crêtes qui séparent les vagues)
    xs=np.linspace(0.30,1.0,60)
    for s in (-1,1):
        poly([(s*x,-0.06+0.10*x) for x in xs],W*1.2)
        poly([(s*x,YB) for x in xs],W*1.2)
        # perles le long des crêtes (relief dans la texture)
        for x in np.arange(0.50,0.95,0.065):
            beads.append((s*x,-0.06+0.10*x,0.020)); beads.append((s*x,YB,0.019))
        # volutes d'écume (crêtes enroulées) : on évide un rond puis on y trace la spirale
        for (vx,vy,vr,va,vs) in ((s*0.55,0.56,0.105,-90,-s),(s*0.62,-0.24,0.085,90,s)):
            c=np.zeros((S,S),np.uint8); disc(vx,vy,vr+0.020,c); m[c>0]=0
            cv2.circle(m,P(vx,vy),int((vr+0.020)*S/2*K),1,px(0.032),cv2.LINE_AA,SH)
            curl(vx,vy,vr-0.012,va,vs,0.034,1.35)
    # seigaiha : rangées peintes de haut en bas, chaque écaille recouvre celles de derrière
    sg=np.zeros((S,S),np.uint8); R0=0.125
    for k,yb_ in enumerate((-0.52,-0.62,-0.72,-0.82,-0.92,-1.02)):
        for xb in np.arange(-1.1+(0.115 if k%2 else 0),1.2,0.23):
            c=np.zeros((S,S),np.uint8); disc(xb,yb_,R0+0.016,c); sg[c>0]=0
            for r,w in ((R0,0.030),(0.072,0.028)):
                cv2.circle(sg,P(xb,yb_),int(r*S/2*K),1,px(w),cv2.LINE_AA,SH)
            disc(xb,yb_,0.024,sg)
            poly([(xb,yb_),(xb,yb_+R0)],0.022,sg)   # tenon qui relie les anneaux
    # chaque écaille cache celles de dessous : on remplit le dos des grandes écailles de la rangée du dessus
    m|=(sg*RB).astype(np.uint8)
    # ---- plaque centrale (cloche) autour de la seppa, dôme et lobes de nuage ----
    pl=np.zeros((S,S),np.uint8)
    cv2.ellipse(pl,P(0,0.0),(int(0.46*S/2*K),int(0.80*S/2*K)),0,0,360,1,-1,cv2.LINE_AA,SH)
    bell=[(-0.40,-0.30),(-0.40,-0.62),(-0.34,-0.80),(-0.24,-0.98),(0.24,-0.98),(0.34,-0.80),(0.40,-0.62),(0.40,-0.30)]
    cv2.fillPoly(pl,[np.array([P(*p) for p in bell],np.int32)],1,cv2.LINE_AA,SH)
    for (x,y,r) in ((0,0.80,0.15),(-0.17,0.86,0.11),(0.17,0.86,0.11),(-0.30,0.70,0.10),(0.30,0.70,0.10),(0,0.96,0.08)):
        disc(x,y,r,pl)
    # jours en forme de nuage dans le dôme (petits trous ronds)
    hole=np.zeros((S,S),np.uint8)
    for s in (-1,1):
        disc(s*0.17,0.86,0.045,hole); disc(s*0.30,0.70,0.038,hole)
    pl[hole>0]=0
    m|=pl
    # rebord intérieur (sous le rebord forgé)
    m[rho>RIN]=1; m[rho>0.995]=0
    # retirer les îlots de fer non reliés au rebord
    n,lab=cv2.connectedComponents(m,connectivity=8)
    keep=np.unique(lab[(rho>RIN+0.01)&(rho<0.99)&(m>0)])
    m=np.where(np.isin(lab,keep[keep>0]),m,0).astype(np.uint8)
    print('composantes',n-1,'gardées',len(keep[keep>0]))
    # jours trop petits -> bouchés
    inv=((1-m)*(rho<0.99)).astype(np.uint8)
    n2,lab2,st,_=cv2.connectedComponentsWithStats(inv,connectivity=4)
    for i in range(1,n2):
        if st[i,cv2.CC_STAT_AREA]<int((0.012*S/2)**2*3.14): m[lab2==i]=1
    if return_parts: return m,rho,beads
    return m,rho
if __name__=='__main__':
    m,rho=build()
    out=np.where(rho<=0.995,np.where(m>0,200,40),120).astype(np.uint8)
    out=cv2.cvtColor(out,cv2.COLOR_GRAY2BGR)
    cv2.ellipse(out,(S//2,S//2),(int(0.34*S/2),int(0.69*S/2)),0,0,360,(0,0,255),6)
    cv2.imwrite('/home/claude/shikkoku/renders/p_mask.png',cv2.resize(out,(700,700),interpolation=cv2.INTER_AREA))
