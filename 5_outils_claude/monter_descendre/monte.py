# Animations MONTER / DESCENDRE / SAUTER du cheval (squelette humain GTA), recreees a la main
# Repere : avant = -Y, gauche = +X, haut = +Z
import sys, math
S='/tmp/claude-0/-home-user-atsuo-katanas/1d790993-5d56-5af0-a69e-ff68766c3d76/scratchpad/anim'
sys.path.insert(0,S); sys.argv=[sys.argv[0],'/dev/null']
src=open(S+'/make_ycd2.py').read()
exec(src[:src.index('DUR={}')])          # B, by, W0, R, dirrot, pos, frame_deltas, to_local, chan, anim_xml(DUR)
from mathutils import Vector, Quaternion, Matrix
RIDE=frame_deltas('idle','b',0.0)
SH={s:pos('SKEL_%s_UpperArm'%s) for s in 'LR'}
EL0={s:pos('SKEL_%s_Forearm'%s) for s in 'LR'}; HA0={s:pos('SKEL_%s_Hand'%s) for s in 'LR'}
def arm_ik(s, tgt, pole):
    sh=SH[s]; a=(EL0[s]-sh).length; b=(HA0[s]-EL0[s]).length
    v=tgt-sh; d=min(v.length, a+b-0.005); u=v.normalized(); T=sh+u*d
    c=(a*a+d*d-b*b)/(2*a*d); sn=math.sqrt(max(0,1-c*c))
    w=(pole-u*pole.dot(u)).normalized()
    el=sh+a*(c*u+sn*w)
    return dirrot(EL0[s]-sh, el-sh), dirrot(HA0[s]-EL0[s], T-el)
def pose(p, side):
    """p : parametres ; side = +1 monte par la GAUCHE du cheval (jambe proche = L), -1 par la droite"""
    near='L' if side>0 else 'R'; far='R' if side>0 else 'L'
    D={}
    lean=p.get('lean',0); roll=p.get('roll',0)*side; tw=p.get('twist',0)*side
    D['SKEL_Pelvis']=R('Z',tw*0.4)@R('Y',roll*0.4)@R('X',p.get('pel',0))
    for n,k in zip(SPINE,SPW): D[n]=R('Z',tw*(1-0.5*k))@R('Y',roll*(1-0.6*k))@R('X',lean*k)
    tor=D['SKEL_Spine3']
    hy=p.get('head',0)*side
    D['SKEL_Neck_1']=tor@R('Z',hy*0.5)@R('X',-lean*0.35)
    D['SKEL_Head']=R('Z',tw*0.3+hy)@R('X',-lean*0.1+p.get('nod',0))
    for who,s in ((near,None),(far,None)):
        L=p['near' if who==near else 'far']; sg=1 if who=='L' else -1
        th=R('Z',sg*L.get('rot',0))@R('Y',-sg*L.get('abd',0))@R('X',-L.get('flex',0))
        D['SKEL_%s_Thigh'%who]=th
        ca=th@R('X',L.get('knee',0))
        D['SKEL_%s_Calf'%who]=ca
        D['SKEL_%s_Foot'%who]=ca@R('X',-L.get('ankle',0))
    for who in (near,far):
        A=p.get('arm_'+('near' if who==near else 'far'))
        if A is None: continue
        sg=1 if who=='L' else -1
        out,fw,up=A[0],A[1],A[2]
        tgt=SH[who]+Vector((sg*out,-fw,up))
        pole=Vector((sg*0.6,0.5,-0.6))
        u,f=arm_ik(who,tgt,pole)
        D['SKEL_%s_UpperArm'%who]=tor@u; D['SKEL_%s_Forearm'%who]=tor@f
        D['SKEL_%s_Hand'%who]=tor@f@R('X',A[3] if len(A)>3 else 0)
    return D
STAND=dict(lean=2, near=dict(flex=0,knee=2), far=dict(flex=0,knee=2), arm_near=(0.10,0.05,-0.52), arm_far=(0.10,0.05,-0.52))
def P(**kw):
    d={k:(dict(v) if isinstance(v,dict) else v) for k,v in STAND.items()}
    for k,v in kw.items():
        if isinstance(v,dict): d[k].update(v)
        else: d[k]=v
    return d
CLIPS={
 # MONTER : debout face au flanc, pied gauche a l'etrier, main sur le pommeau, impulsion, jambe droite par-dessus la croupe, on se pose
 # MONTER avec de VRAIS APPUIS : pied gauche dans l'etrier, main gauche sur le pommeau, main droite sur le troussequin,
 # impulsion de la jambe droite, debout sur l'etrier, la jambe droite passe par-dessus la croupe, on s'assoit
 'mount': (2.0, [
   (0.00, P()),
   (0.14, P(lean=8, head=-6, arm_near=(0.00,0.30,0.00), arm_far=(-0.10,0.30,0.04),
            near=dict(flex=72,knee=104,abd=16,ankle=-4), far=dict(flex=2,knee=6))),
   (0.30, P(lean=14, pel=-4, head=-6, arm_near=(0.00,0.28,-0.06), arm_far=(-0.10,0.28,-0.02),
            near=dict(flex=76,knee=112,abd=16,ankle=-4), far=dict(flex=26,knee=46,ankle=22))),
   (0.48, P(lean=24, head=-4, arm_near=(0.04,0.26,-0.26), arm_far=(-0.06,0.26,-0.24),
            near=dict(flex=12,knee=16,abd=10,ankle=-6), far=dict(flex=-6,knee=12,ankle=18))),
   (0.66, P(lean=26, twist=-16, head=0, roll=-6, arm_near=(0.06,0.28,-0.32), arm_far=(-0.02,0.28,-0.30),
            near=dict(flex=18,knee=30,abd=22), far=dict(flex=-34,knee=30,abd=70,rot=10))),
   (0.83, P(lean=10, twist=-5, arm_near=(0.06,0.32,-0.36), arm_far=(0.06,0.32,-0.36),
            near=dict(flex=34,knee=50,abd=40), far=dict(flex=28,knee=52,abd=46))),
   (1.00, 'RIDE')]),
 # DESCENDRE (arret) : on se penche, jambe droite par-dessus la croupe, on glisse le long du flanc, reception souple
 'dismount': (1.45, [
   (0.00, 'RIDE'),
   (0.16, P(lean=24, head=6, arm_near=(0.04,0.30,-0.32), arm_far=(-0.04,0.30,-0.30),
            near=dict(flex=45,knee=55,abd=40), far=dict(flex=30,knee=30,abd=45,ankle=-10))),
   (0.38, P(lean=28, twist=-20, head=16, roll=-6, arm_near=(0.04,0.28,-0.26), arm_far=(-0.06,0.28,-0.24),
            near=dict(flex=32,knee=42,abd=28), far=dict(flex=-30,knee=50,abd=62,rot=10))),
   (0.58, P(lean=10, head=12, arm_near=(0.02,0.24,0.10), arm_far=(-0.12,0.26,0.16),
            near=dict(flex=4,knee=8), far=dict(flex=6,knee=10))),
   (0.78, P(lean=16, pel=-4, head=6, arm_near=(0.06,0.22,-0.20), arm_far=(-0.04,0.24,-0.18),
            near=dict(flex=42,knee=72,ankle=28), far=dict(flex=38,knee=66,ankle=26))),
   (1.00, P())]),
 # SAUTER EN MARCHE : les deux jambes passent du cote, petit saut, reception en courant
 'dismount_run': (0.85, [
   (0.00, 'RIDE'),
   (0.30, P(lean=-6, head=14, twist=-14, arm_near=(0.10,0.30,-0.28), arm_far=(0.02,0.30,-0.25),
            near=dict(flex=55,knee=55,abd=20), far=dict(flex=70,knee=50,abd=-5,rot=-10))),
   (0.60, P(lean=6, head=8, arm_near=(0.40,0.10,-0.05), arm_far=(0.35,0.12,-0.10),
            near=dict(flex=28,knee=36,ankle=10), far=dict(flex=22,knee=40,ankle=10))),
   (0.80, P(lean=22, pel=-6, arm_near=(0.22,0.18,-0.30), arm_far=(0.20,0.22,-0.32),
            near=dict(flex=50,knee=86,ankle=30), far=dict(flex=20,knee=50,ankle=20))),
   (1.00, P(lean=12, arm_near=(0.12,0.12,-0.45), arm_far=(0.12,0.10,-0.45),
            near=dict(flex=-10,knee=20), far=dict(flex=35,knee=55)))]),
}
def keyD(k, side):
    if k=='RIDE':
        if side>0: return dict(RIDE)
        return mirror(RIDE)
    return pose(k, side)
MX=Matrix.Diagonal((-1,1,1))
def mirror(D):
    out={}
    for n,m in D.items():
        n2=n.replace('_L_','_X_').replace('_R_','_L_').replace('_X_','_R_')
        out[n2]=MX@m@MX
    return out
def logq(m):
    q=m.to_quaternion()
    if q.w<0: q.negate()
    a=2*math.acos(max(-1,min(1,q.w))); s=math.sqrt(max(1e-12,1-q.w*q.w))
    return Vector((q.x,q.y,q.z))*(a/s) if a>1e-6 else Vector((0,0,0))
def expv(v):
    a=v.length
    if a<1e-9: return Matrix.Identity(3)
    return Quaternion(v/a,a).to_matrix()
def hermite(ts, vs, t):
    n=len(ts)
    if t<=ts[0]: return vs[0]
    if t>=ts[-1]: return vs[-1]
    i=max(j for j in range(n-1) if ts[j]<=t)
    def m(j):
        if j==0 or j==n-1: return vs[j]*0
        return (vs[j+1]-vs[j-1])/(ts[j+1]-ts[j-1])
    h=ts[i+1]-ts[i]; u=(t-ts[i])/h
    h00=2*u**3-3*u**2+1; h10=u**3-2*u**2+u; h01=-2*u**3+3*u**2; h11=u**3-u**2
    return vs[i]*h00+m(i)*h*h10+vs[i+1]*h01+m(i+1)*h*h11
def build(name, side):
    dur,keys=CLIPS[name]
    Ds=[keyD(k,side) for _,k in keys]; ts=[t for t,_ in keys]
    bones=sorted(set().union(*[set(d) for d in Ds]))
    def delta(d,b):
        while b not in d:
            pi=by[b]['parent']
            if pi<0: return Matrix.Identity(3)
            b=byidx[pi]['name']
        return d[b]
    Ds=[{b:delta(d,b) for b in bones} for d in Ds]
    logs={b:[logq(d.get(b,Matrix.Identity(3))) for d in Ds] for b in bones}
    for b in bones:   # continuite des vecteurs de rotation
        for i in range(1,len(logs[b])):
            v=logs[b][i]; p=logs[b][i-1]
            if v.length>1e-6:
                alt=v-v.normalized()*2*math.pi
                if (alt-p).length<(v-p).length: logs[b][i]=alt
    n=int(round(dur*30))+1; frames=[]
    for i in range(n):
        t=i/(n-1)
        D={b:expv(hermite(ts,logs[b],t)) for b in bones}
        frames.append(to_local(D))
    return dur,frames
