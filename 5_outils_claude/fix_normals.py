# Oriente toutes les faces vers l'extérieur (GTA n'affiche qu'un côté des faces)
import bmesh, math, numpy as np, collections
from mathutils import Vector
from params import *
def _theta_inv(t):
    lo,hi=0.0,1.0
    for _ in range(40):
        m=(lo+hi)/2
        if theta(m)<t: lo=m
        else: hi=m
    return (lo+hi)/2
def b_of(th):
    th=th%(2*math.pi)
    return _theta_inv(th) if th<=math.pi else 2-_theta_inv(2*math.pi-th)
def fix(obj):
    me=obj.data; mats=[m.name for m in me.materials]
    bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
    parent=list(range(len(bm.verts)))
    def f(i):
        while parent[i]!=i: parent[i]=parent[parent[i]]; i=parent[i]
        return i
    for e in bm.edges:
        a,b=f(e.verts[0].index),f(e.verts[1].index)
        if a!=b: parent[a]=b
    isl=collections.defaultdict(list)
    for fc in bm.faces: isl[f(fc.verts[0].index)].append(fc)
    flipped=0
    L=X_WRAP1-X_WRAP0
    for faces in isl.values():
        mat=mats[faces[0].material_index]
        V=np.array([v.co[:] for fc in faces for v in fc.verts]); C=V.mean(0)
        if mat=='lame':
            bmesh.ops.recalc_face_normals(bm,faces=faces)
            s=sum(1 if fc.normal.y*fc.calc_center_median().y>0 else -1 for fc in faces if abs(fc.normal.y)>0.6)
            if s<0:
                bmesh.ops.reverse_faces(bm,faces=faces); flipped+=len(faces)
            continue
        small = (V[:,0].max()-V[:,0].min())<0.02 and abs(C[1])>0.005 and C[0]>X_WRAP0   # menuki
        for fc in faces:
            F=np.array(fc.calc_center_median()[:]); N=np.array(fc.normal[:])
            if np.linalg.norm(N)<1e-9: continue
            r=np.array([0.0,F[1],F[2]-zc(F[0])]); rn=np.linalg.norm(r); r=r/rn if rn>1e-9 else r
            if small:
                base=C-np.array([0.0,np.sign(C[1])*0.002,0.0]); ref=F-base
            elif mat=='ito' and abs(N@r)<0.5:   # paroi de fenêtre -> vers le centre de la fenêtre
                a=(F[0]-X_WRAP0)/L*N_; th=math.atan2(F[1],F[2]-zc(F[0])); b=b_of(th)
                ac=math.floor(a)+0.5; bc=0.5 if b<1 else 1.5
                t=ac/N_; x=X_WRAP0+t*L; s_=scale(t); thc=theta(bc)
                Wc=np.array([x,(AY*s_-ITO_T/2)*math.sin(thc),zc(x)+(AZ*s_-ITO_T/2)*math.cos(thc)])
                ref=Wc-F
            elif abs(N@r)>=abs(N[0]): ref=r
            else: ref=np.array([F[0]-C[0],0.0,0.0])
            if N@ref<0:
                fc.normal_flip(); flipped+=1
    bm.to_mesh(me); bm.free(); me.update()
    return flipped
N_=N
