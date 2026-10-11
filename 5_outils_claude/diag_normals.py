import bpy, bmesh, sys, numpy as np
sys.path.insert(0,'/home/claude/kin/scripts')
from params import zc
path=sys.argv[-2]; objname=sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=path)
o=bpy.data.objects[objname]
bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
# îlots
import collections
parent=list(range(len(bm.verts)))
def f(i):
    while parent[i]!=i: parent[i]=parent[parent[i]]; i=parent[i]
    return i
for e in bm.edges:
    a,b=f(e.verts[0].index),f(e.verts[1].index)
    if a!=b: parent[a]=b
isl=collections.defaultdict(list)
for fc in bm.faces: isl[f(fc.verts[0].index)].append(fc)
mats=[m.name for m in o.data.materials]
for k,faces in sorted(isl.items(), key=lambda kv:-len(kv[1])):
    V=np.array([v.co[:] for fc in faces for v in fc.verts]); C=V.mean(0)
    bad=0; tot=0
    for fc in faces:
        F=np.array(fc.calc_center_median()[:]); N=np.array(fc.normal[:])
        if np.linalg.norm(N)<1e-9: continue
        ref=F-np.array([C[0],0.0,zc(C[0]) if V[:,0].min()>0.1 else C[2]])
        tot+=1; bad+= (N@ref<0)
    print(f'{mats[faces[0].material_index]:24s} faces={len(faces):5d} x[{V[:,0].min():.3f},{V[:,0].max():.3f}] inverses={bad}/{tot}')
