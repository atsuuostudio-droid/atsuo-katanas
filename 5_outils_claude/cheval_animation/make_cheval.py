# Allures de CHEVAL (squelette cerf / draft_horse) avec sabots poses au sol (IK 2D par patte)
# Repere : avant = -Y, gauche = +X, haut = +Z. Sol au repos : z = -1.0
import sys, math
sys.path.insert(0,'/home/claude/cheval')
exec(open('/home/claude/cheval/gaits.py').read().split('def R(')[0])
def R(axis,deg): return Matrix.Rotation(math.radians(deg),3,axis)
CH={'F':['UpperArm','Forearm','Hand','Finger00','Finger01','PH_%s_Hand'],
    'H':['Thigh','Calf','Foot','Toe0','Toe1','PH_%s_Foot']}
def chain(side,fh):
    return [('SKEL_%s_'%side+n) if not n.startswith('PH') else n%side for n in CH[fh]]
def pts(side,fh): return [Vector((W0[n].translation.y,W0[n].translation.z)) for n in chain(side,fh)]
SEGANG=[0,1,2,3,3]   # angle utilise par chaque segment (Finger01/Toe1 suit le boulet)
# motifs de flexion (increments relatifs) : soutien (patte repliee) / appui (amorti)
PAT={('F','sw'):(-0.45,1.0,0.55), ('F','st'):(-0.2,0.05,-0.75),
     ('H','sw'):(0.55,-1.0,0.6),  ('H','st'):(0.45,-0.7,-0.35)}
def rot(v,a):
    c,s=math.cos(a),math.sin(a); return Vector((v.x*c-v.y*s, v.x*s+v.y*c))
def angles(a1,c,pat):
    a=[a1]; 
    for p in pat: a.append(a[-1]+p*c)
    return a
def fk(P,a):
    q=P[0].copy()
    for i in range(5): q=q+rot(P[i+1]-P[i],math.radians(a[SEGANG[i]]))
    return q
CMIN=-3.0
def solve(P,target,pat,init):
    def err(a1,c): return fk(P,angles(a1,c,pat))-target
    best=None
    for st in (init,(init[0],init[1]+25),(0.0,10.0),(0.0,50.0),(20.0,40.0),(-20.0,40.0)):
        a1,c=st; c=max(CMIN,c); lam=1e-3
        e=err(a1,c); E0=e.length_squared
        for _ in range(80):
            h=0.02
            J1=(err(a1+h,c)-e)/h; J2=(err(a1,c+h)-e)/h
            A11=J1.dot(J1)+lam; A22=J2.dot(J2)+lam; A12=J1.dot(J2)
            g1=J1.dot(e); g2=J2.dot(e); det=A11*A22-A12*A12
            da=( A22*g1-A12*g2)/det; dc=(-A12*g1+A11*g2)/det
            na,nc=a1-da,max(CMIN,c-dc); ne=err(na,nc)
            if ne.length_squared<E0: a1,c,e,E0=na,nc,ne,ne.length_squared; lam*=0.3
            else: lam*=10
            if E0<1e-12 or lam>1e8: break
        cost=E0+2e-6*a1*a1+1e-7*((a1-init[0])**2+(c-init[1])**2)
        if best is None or cost<best[0]-1e-9: best=(cost,a1,c)
    return best[1],best[2]
GROUND=-1.0
G={ # dur, appui, course du sabot S (m), lever avant/arriere, rebond, dephasages
 'walk':  dict(dur=1.05,duty=0.62,S=0.62,lift=(0.11,0.09),bob=(0.012,2,0.16),ph=dict(LH=0.0,LF=0.25,RH=0.5,RF=0.75),spine=1.5,neck=(6,2,0.1),tail=4,roll=2.0),
 'trot':  dict(dur=0.72,duty=0.45,S=0.72,lift=(0.24,0.17),bob=(0.030,2,0.22),ph=dict(LH=0.0,RF=0.0,RH=0.5,LF=0.5),spine=2.0,neck=(3,2,0.3),tail=6,roll=1.0),
 'canter':dict(dur=0.62,duty=0.36,S=0.85,lift=(0.26,0.20),bob=(0.050,1,0.40),ph=dict(LH=0.0,RH=0.22,LF=0.24,RF=0.46),spine=5.0,neck=(9,1,0.35),tail=8,roll=1.0),
 'gallop':dict(dur=0.50,duty=0.27,S=0.92,lift=(0.30,0.24),bob=(0.060,1,0.42),ph=dict(LH=0.0,RH=0.10,LF=0.40,RF=0.52),spine=7.0,neck=(12,1,0.35),tail=10,roll=0.8),
 'turn':  dict(dur=1.00,duty=0.62,S=0.22,lift=(0.08,0.06),bob=(0.006,2,0.16),ph=dict(LH=0.0,LF=0.25,RH=0.5,RF=0.75),spine=0.6,neck=(3,2,0.1),tail=4,roll=1.0),
}
LEGS=[('L','F'),('R','F'),('L','H'),('R','H')]
REST={(s,f):pts(s,f) for s,f in LEGS}
def base_drop(g):
    S=G[g]['S']; m=0.0
    for k,P in REST.items():
        d=(P[-1]-P[0]).length
        y0=P[0].x+(0.03 if k[1]=='F' else 0.06)
        for y in (y0-S/2,y0+S/2):
            dz=math.sqrt(max(0,d*d-(y-P[0].x)**2))-(P[0].y-GROUND)
            m=min(m,dz)
    return min(0.0,m+0.012)
def smooth(x): return x*x*(3-2*x)
def leg_target(g,P,fh,ph,dz):
    Gg=G[g]; S=Gg['S']; duty=Gg['duty']; y0=P[0].x+(0.03 if fh=='F' else 0.06)
    if ph<duty:
        s=ph/duty; y=y0-S/2+S*s; z=GROUND; mode='st'
    else:
        s=(ph-duty)/(1-duty)
        y=y0+S/2-S*smooth(min(1,s*1.08))
        lift=Gg['lift'][0 if fh=='F' else 1]
        z=GROUND+lift*math.sin(math.pi*s)**0.9*(1.0 if s<0.5 else 1.0); mode='sw'
    return Vector((y,z-dz)),mode
STATE={}
def frame(g,p,turn=0.0):
    Gg=G[g]; w=2*math.pi*p; D={}
    _,f,ph0=Gg['bob']
    dz=base_drop(g)-Gg['bob'][0]*(0.5+0.5*math.cos(2*math.pi*f*(p-ph0)))
    hooves={}
    for side,fh in LEGS:
        P=REST[(side,fh)]
        ph=(p-Gg['ph'][side+fh])%1.0
        tgt,mode=leg_target(g,P,fh,ph,dz)
        pat=PAT[(fh,mode)]
        init=STATE.get((side,fh,mode),(0.0,5.0))
        a1,c=solve(P,tgt,pat,init); STATE[(side,fh,mode)]=(a1,c)
        a=angles(a1,c,pat)
        for i,n in enumerate(chain(side,fh)[:4]): D[n]=R('X',a[i])
        hooves[side+fh]=fk(P,a)+Vector((0,dz))
    sp=Gg['spine']*math.sin(w*Gg['bob'][1]+0.6)
    roll=Gg['roll']*math.sin(w)
    for i,n in enumerate(['SKEL_Spine0','SKEL_Spine1','SKEL_Spine2','SKEL_Spine3']):
        D[n]=R('Z',turn*(0.15+0.1*i))@R('Y',roll*(0.5+0.15*i))@R('X',sp*(0.4+0.2*i))
    na,nf,nph=Gg['neck']; nk=na*math.sin(2*math.pi*(nf*p+nph))
    D['SKEL_Neck_1']=R('Z',turn*0.9)@R('X',nk*0.6); D['SKEL_Neck_2']=R('Z',turn*1.3)@R('X',nk); D['SKEL_Head']=R('Z',turn*1.6)@R('X',nk*0.7)
    D['SKEL_Pelvis']=R('Z',-turn*0.3)
    for i,n in enumerate(['SKEL_Tail_01','SKEL_Tail_02','SKEL_Tail_03','SKEL_Tail_04','SKEL_Tail_05']):
        D[n]=R('Z',-turn*0.3*(i+1)+Gg['tail']*(i+1)*0.5*math.sin(w-0.7*i))@R('X',-Gg['tail']*0.12*(i+1))
    return D,dz,hooves
def idle_frame(p,turn=0.0):
    w=2*math.pi*p; D={}
    D['SKEL_Spine1']=R('X',0.8*math.sin(w)); D['SKEL_Spine2']=R('X',0.8*math.sin(w))
    D['SKEL_Neck_1']=R('X',2*math.sin(w+0.5)); D['SKEL_Head']=R('X',3*math.sin(w+1.0))@R('Z',4*math.sin(w))
    for i,n in enumerate(['SKEL_Tail_01','SKEL_Tail_02','SKEL_Tail_03','SKEL_Tail_04','SKEL_Tail_05']):
        D[n]=R('Z',5*(i+1)*0.4*math.sin(2*w-0.8*i))@R('X',-0.5*(i+1))
    return D,0.004*math.sin(w)-0.002,{}
def to_local_all(D):
    newW={}
    def wr(n):
        if n in newW: return newW[n]
        b=by[n]
        if n in D: r_=D[n]@W0[n].to_3x3()
        else:
            par=byidx[b['parent']]['name'] if b['parent']>=0 else None
            r_=(wr(par) if par else Matrix.Identity(3))@b['q'].to_matrix()
        newW[n]=r_; return r_
    out={}
    for b in B:
        n=b['name']
        if b['parent']<0: out[n]=b['q'].copy(); continue
        out[n]=(wr(byidx[b['parent']]['name']).inverted()@wr(n)).to_quaternion()
    return out
