# Allures de CHEVAL pour le squelette DEER (draft_horse) : pas (4 temps), trot (diagonal), petit galop (3 temps), galop (4 temps)
# Repere squelette cerf : avant = -Y, gauche = +X, haut = +Z. Pattes avant : UpperArm/Forearm/Hand/Finger00, arriere : Thigh/Calf/Foot/Toe0.
import bpy, math, sys, xml.etree.ElementTree as ET
from mathutils import Vector, Quaternion, Matrix
sys.path.insert(0,'/home/claude/cheval')
from tools_jenk import jenk
r=ET.parse('/home/claude/cheval/a_c_deer.yft.xml').getroot()
B=[]
for b in r.find('Drawable').find('Skeleton').find('Bones'):
    g=lambda t,a: float(b.find(t).get(a))
    B.append(dict(name=b.find('Name').text,tag=int(b.find('Tag').get('value')),idx=int(b.find('Index').get('value')),parent=int(b.find('ParentIndex').get('value')),
        t=Vector((g('Translation','x'),g('Translation','y'),g('Translation','z'))),q=Quaternion((g('Rotation','w'),g('Rotation','x'),g('Rotation','y'),g('Rotation','z')))))
by={b['name']:b for b in B}; byidx={b['idx']:b for b in B}
W0={}
for b in B:
    M=Matrix.Translation(b['t'])@b['q'].to_matrix().to_4x4()
    W0[b['name']]=M if b['parent']<0 else W0[byidx[b['parent']]['name']]@M
def R(axis,deg): return Matrix.Rotation(math.radians(deg),3,axis)
LEGS={ # nom : (os haut, os 2, os 3, os 4, avant?)
 'LF':('SKEL_L_UpperArm','SKEL_L_Forearm','SKEL_L_Hand','SKEL_L_Finger00',True),
 'RF':('SKEL_R_UpperArm','SKEL_R_Forearm','SKEL_R_Hand','SKEL_R_Finger00',True),
 'LH':('SKEL_L_Thigh','SKEL_L_Calf','SKEL_L_Foot','SKEL_L_Toe0',False),
 'RH':('SKEL_R_Thigh','SKEL_R_Calf','SKEL_R_Foot','SKEL_R_Toe0',False)}
GAITS={
 # dur(s), duty (appui), amplitude membre, dephasages, flexions max (coude/grasset, genou/jarret, boulet), rebond, colonne, encolure
 'walk':  dict(dur=1.05,duty=0.62,A=18,ph=dict(LH=0.0,LF=0.25,RH=0.5,RF=0.75),fF=(14,55,30),fH=(14,38,28),bob=(0.018,2),spine=2.0,neck=(6,2),tail=4),
 'trot':  dict(dur=0.72,duty=0.45,A=22,ph=dict(LH=0.0,RF=0.0,RH=0.5,LF=0.5),fF=(22,85,40),fH=(18,55,38),bob=(0.040,2),spine=2.5,neck=(4,2),tail=6),
 'canter':dict(dur=0.62,duty=0.40,A=26,ph=dict(LH=0.0,RH=0.28,LF=0.30,RF=0.55),fF=(28,95,45),fH=(22,62,42),bob=(0.060,1),spine=6.0,neck=(10,1),tail=8),
 'gallop':dict(dur=0.50,duty=0.32,A=30,ph=dict(LH=0.0,RH=0.10,LF=0.42,RF=0.54),fF=(32,105,50),fH=(26,72,48),bob=(0.070,1),spine=8.0,neck=(13,1),tail=10),
}
def smooth(x): return x*x*(3-2*x)
def leg_deltas(G,phase,front,side):
    duty=G['duty']; A=G['A']
    if phase<duty:                       # appui : le sabot recule sous le corps
        s=phase/duty; th=A-2*A*s         # +A (devant) -> -A (derriere)
        flex=(0,0,-(G['fF'][2] if front else G['fH'][2])*0.45*math.sin(math.pi*s))   # boulet qui s'affaisse
        f1=f2=0.0
    else:                                # soutien : la jambe se replie et revient vers l'avant
        s=(phase-duty)/(1-duty); th=-A+2*A*smooth(s)
        lift=math.sin(math.pi*min(1,s*1.15))**1.2
        F=G['fF'] if front else G['fH']
        f1=F[0]*lift; f2=F[1]*lift; flex=(0,0,F[2]*lift)
    # angles cumules (Rx(-a) = vers l'avant)
    if front:
        a1=-th                       # epaule : protraction vers l'avant
        a2=a1-f1                     # coude : avant-bras vers l'avant
        a3=a2+f2                     # genou (carpe) : canon replie vers l'arriere
        a4=a3+flex[2]*0.6+ (f2*0.15)
    else:
        a1=-th+f1*0.6                # hanche
        a2=a1+f1                     # grasset : tibia vers l'arriere
        a3=a2-f2                     # jarret : canon vers l'avant
        a4=a3+flex[2]*0.6
    return [R('X',a1),R('X',a2),R('X',a3),R('X',a4)]
SPINE=['SKEL_Spine0','SKEL_Spine1','SKEL_Spine2','SKEL_Spine3']
TAIL=['SKEL_Tail_01','SKEL_Tail_02','SKEL_Tail_03','SKEL_Tail_04','SKEL_Tail_05']
def frame(gname,p):
    G=GAITS[gname]; D={}
    for leg,(b1,b2,b3,b4,front) in LEGS.items():
        ph=(p-G['ph'][leg])%1.0
        for bn,m in zip((b1,b2,b3,b4),leg_deltas(G,ph,front,leg[0])): D[bn]=m
    f=G['bob'][1]; w=2*math.pi*p
    sp=G['spine']*math.sin(w*f+0.6)
    roll=(2.0 if gname=='walk' else 1.0)*math.sin(w)
    for i,n in enumerate(SPINE): D[n]=R('Y',roll*(0.5+0.15*i))@R('X',sp*(0.4+0.2*i))
    na,nf=G['neck']
    nk=na*math.sin(w*nf+1.2)
    D['SKEL_Neck_1']=R('X',nk*0.6); D['SKEL_Neck_2']=R('X',nk); D['SKEL_Head']=R('X',nk*0.7)
    for i,n in enumerate(TAIL):
        D[n]=R('Z',G['tail']*(i+1)*0.5*math.sin(w-0.7*i))@R('X',-G['tail']*0.4*(i+1)*0.3)
    dz=G['bob'][0]*(0.5+0.5*math.cos(w*f*2*math.pi/ (2*math.pi)))  # rebond (haut quand les membres sont sous le corps)
    dz=G['bob'][0]*math.cos(w*f)
    return D,dz
def idle_frame(p):
    w=2*math.pi*p; D={}
    D['SKEL_Spine1']=R('X',0.8*math.sin(w)); D['SKEL_Spine2']=R('X',0.8*math.sin(w))
    D['SKEL_Neck_1']=R('X',2*math.sin(w+0.5)); D['SKEL_Head']=R('X',3*math.sin(w+1.0))@R('Z',4*math.sin(w*0.5))
    for i,n in enumerate(TAIL): D[n]=R('Z',6*(i+1)*0.4*math.sin(w*2-0.8*i))
    for leg,(b1,b2,b3,b4,front) in LEGS.items():
        for bn in (b1,b2,b3,b4): D[bn]=Matrix.Identity(3)
    return D,0.004*math.sin(w)
def to_local(D):
    newW={}
    def wr(n):
        if n in newW: return newW[n]
        b=by[n]
        if n in D: r_=D[n]@W0[n].to_3x3()
        else:
            par=byidx[b['parent']]['name'] if b['parent']>=0 else None
            r_=(wr(par) if par else Matrix.Identity(3))@b['q'].to_matrix()
        newW[n]=r_; return r_
    return {n:(wr(byidx[by[n]['parent']]['name']).inverted()@wr(n)).to_quaternion() for n in D}
