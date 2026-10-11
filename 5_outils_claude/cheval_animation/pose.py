import sys, math
sys.path.insert(0,'.')
from skel import *
from mathutils import Euler
B=load(); byname={b['name']:b for b in B}; byidx={b['idx']:b for b in B}
W0=world(B)
def R(axis,deg): return Matrix.Rotation(math.radians(deg),3,axis)
A=[float(x) for x in sys.argv[1:5]] if __name__=='__main__' else []
A+= [58,32,14,4][len(A):]
P=dict(flex=A[0],abd=A[1],shin_abd=A[2],shin_back=A[3],toe_out=12)
def pose_deltas(P):
    D={}
    for side,s in (('L',1),('R',-1)):
        # avant = -Y, gauche = +X, haut = +Z (repere squelette)
        D['SKEL_%s_Thigh'%side]=R('Y',-s*P['abd'])@R('X',-P['flex'])
        D['SKEL_%s_Calf'%side]=R('Y',-s*P['shin_abd'])@R('X',P['shin_back'])
        D['SKEL_%s_Foot'%side]=R('Z',s*P['toe_out'])
    return D
def solve(P):
    D=pose_deltas(P)
    newW={}; local={}
    def wrot(name):
        if name in newW: return newW[name]
        b=byname[name]
        r0=W0[name].to_3x3()
        r=D[name]@r0 if name in D else None
        if r is None:
            # pas modifie : garde la rotation locale de repos
            par=byidx[b['parent']]['name'] if b['parent']>=0 else None
            r=(wrot(par) if par else Matrix.Identity(3))@b['q'].to_matrix()
        newW[name]=r; return r
    for n in D:
        b=byname[n]; par=byidx[b['parent']]['name']
        lq=(wrot(par).inverted()@wrot(n)).to_quaternion()
        if lq.w<0: lq.negate()
        local[n]=lq
    return local
if __name__=='__main__':
    L=solve(P)
    W=world(B,L)
    for n in ['SKEL_Pelvis','SKEL_L_Thigh','SKEL_L_Calf','SKEL_L_Foot','SKEL_L_Toe0','SKEL_R_Calf','SKEL_R_Foot']:
        print(n,[round(v,3) for v in W[n].translation])
