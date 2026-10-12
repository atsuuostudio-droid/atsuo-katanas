import bpy, bmesh, math, sys, numpy as np
from mathutils import Vector, Matrix
sys.path.insert(0,'/home/claude/kurogane/scripts')
from params_k import *
TEX='/home/claude/kurogane/tex/'
bpy.ops.wm.read_factory_settings(use_empty=True)
def mk_mat(name,base,rough,metal,nstr=1.0):
    m=bpy.data.materials.new(name); nt=m.node_tree; N=nt.nodes; bs=N['Principled BSDF']
    def img(f,col):
        n=N.new('ShaderNodeTexImage'); n.image=bpy.data.images.load(TEX+f); n.image.colorspace_settings.name='sRGB' if col else 'Non-Color'; return n
    d=img(base+'_d.png',True); nt.links.new(d.outputs[0],bs.inputs['Base Color'])
    nn=img(base+'_n.png',False); nm=N.new('ShaderNodeNormalMap'); nm.inputs[0].default_value=nstr
    nt.links.new(nn.outputs[0],nm.inputs[1]); nt.links.new(nm.outputs[0],bs.inputs['Normal'])
    s=img(base+'_s.png',False); nt.links.new(s.outputs[0],bs.inputs['Specular IOR Level'])
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
M_LAME=mk_mat('lame','lame',0.32,0.85); M_FER=mk_mat('fer','fer',0.40,0.85); M_CUIR=mk_mat('cuir','cuir',0.6,0.0)
def new_obj(name,bm,mats):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); return o
def luv(s,z): return ((s)/LB, (z+W/2)/W)
# ---------------- LAME ----------------
bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap')
NS=160
ss=sorted(set([ (LB-KT)*i/NS for i in range(NS+1)]+[LB-KT+KT*j/40 for j in range(41)]))
ss=[s for s in ss if s<LB-1e-6]+[LB]
def section(s):
    h=hw(s); c=max(0.0,h-B)
    # profil (z, y) du fil bas -> fil haut, face +y
    if c>0: zs=[-h,-c,c,h]; ys=[TE,TC,TC,TE]
    else:
        t=max(h,1e-5)/B; zs=[-h,0.0,h]; ys=[TE,TE+(TC-TE)*t,TE]
    return zs,ys
rings=[]
for s in ss:
    x=XG-s
    if s>=LB-1e-6:
        rings.append(('tip',bm.verts.new((x,0,0)))); continue
    zs,ys=section(s)
    top=[bm.verts.new((x,y,z)) for z,y in zip(zs,ys)]
    bot=[bm.verts.new((x,-y,z)) for z,y in zip(zs,ys)]
    rings.append(('ring',top,bot,zs))
def face(vs,uvs):
    f=bm.faces.new(vs)
    for l,u in zip(f.loops,uvs): l[uv].uv=u
    return f
for i in range(len(rings)-1):
    A=rings[i]; Bn=rings[i+1]; sa=ss[i]; sb=ss[i+1]
    if Bn[0]=='tip':
        tv=Bn[1]
        for side in (1,2):
            ring=A[side]; zs=A[3]
            for j in range(len(ring)-1):
                face([ring[j],ring[j+1],tv] if side==2 else [ring[j+1],ring[j],tv],
                     [luv(sa,zs[j]),luv(sa,zs[j+1]),luv(LB,0)] if side==2 else [luv(sa,zs[j+1]),luv(sa,zs[j]),luv(LB,0)])
        continue
    na=len(A[1]); nb=len(Bn[1])
    for side in (1,2):
        ra=A[side]; rb=Bn[side]
        if na==nb:
            for j in range(na-1):
                vs=[ra[j],ra[j+1],rb[j+1],rb[j]]; uu=[luv(sa,A[3][j]),luv(sa,A[3][j+1]),luv(sb,Bn[3][j+1]),luv(sb,Bn[3][j])]
                if side==1: vs=vs[::-1]; uu=uu[::-1]
                face(vs,uu)
        else:   # 4 -> 3 (fin du plat central)
            m=[0,1,1,2]
            for j in range(na-1):
                if m[j]==m[j+1]:
                    vs=[ra[j],ra[j+1],rb[m[j]]]; uu=[luv(sa,A[3][j]),luv(sa,A[3][j+1]),luv(sb,Bn[3][m[j]])]
                else:
                    vs=[ra[j],ra[j+1],rb[m[j+1]],rb[m[j]]]; uu=[luv(sa,A[3][j]),luv(sa,A[3][j+1]),luv(sb,Bn[3][m[j+1]]),luv(sb,Bn[3][m[j]])]
                if side==1: vs=vs[::-1]; uu=uu[::-1]
                face(vs,uu)
    # fils (relient face +y et -y)
    for e in (0,-1):
        va,vb=A[1][e],Bn[1][e]; wa,wb=A[2][e],Bn[2][e]
        za,zb=A[3][e],Bn[3][e]
        vs=[va,vb,wb,wa]; uu=[luv(sa,za),luv(sb,zb),luv(sb,zb),luv(sa,za)]
        if e==0: vs=vs[::-1]; uu=uu[::-1]
        face(vs,uu)
# fermeture cote garde (cachee)
A=rings[0]; c0=bm.verts.new((XG,0,0))
loop=A[1]+A[2][::-1]
for j in range(len(loop)):
    face([loop[j],loop[(j+1)%len(loop)],c0],[(0,0.5)]*3)
bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=1e-7)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
lame=new_obj('lame',bm,[M_LAME])
# ---------------- helpers fer ----------------
def boxuv(bm,uvl,scale=0.12):
    for f in bm.faces:
        n=f.normal; a=max(range(3),key=lambda i:abs(n[i]))
        for l in f.loops:
            co=l.vert.co; p=[co[i] for i in range(3) if i!=a]
            l[uvl].uv=(p[0]/scale,p[1]/scale)
def add_box(bm,c,size,bev=0.0):
    r=bmesh.ops.create_cube(bm,size=1.0)
    vs=r['verts']
    for v in vs: v.co=Vector((c[0]+v.co.x*size[0],c[1]+v.co.y*size[1],c[2]+v.co.z*size[2]))
    if bev>0:
        es=list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm,geom=es+vs,offset=bev,segments=2,affect='EDGES',profile=0.5)
    return vs
def add_rivet(bm,c,r,axis):
    res=bmesh.ops.create_uvsphere(bm,u_segments=10,v_segments=6,radius=r)
    for v in res['verts']:
        p=v.co.copy()
        # demi-sphere aplatie
        if axis=='y':
            s=1 if c[1]>0 else -1
            p.y=abs(p.y)*0.55*s
        elif axis=='x':
            s=1 if c[0]>XG else -1
            p.x=abs(p.x)*0.55*s
        v.co=Vector(c)+p
def octa_lathe(bm,prof,n=8,rot=math.pi/8):
    rings=[]
    for x,r in prof:
        rings.append([bm.verts.new((x,r*math.cos(2*math.pi*k/n+rot),r*math.sin(2*math.pi*k/n+rot))) for k in range(n)])
    for i in range(len(rings)-1):
        for k in range(n):
            bm.faces.new([rings[i][k],rings[i][(k+1)%n],rings[i+1][(k+1)%n],rings[i+1][k]])
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
# ---------------- GARDE + demi-lune + rivets ----------------
bm=bmesh.new(); uvl=bm.loops.layers.uv.new('UVMap')
gx=XG+GT/2
add_box(bm,(gx,0,0),(GT,GD,GH),bev=0.003)
# bandes de renfort (haut / bas)
for zz in (GH/2-0.012,-GH/2+0.012):
    add_box(bm,(gx,0,zz),(GT+0.006,GD+0.006,0.016),bev=0.0015)
# demi-lune sur chaque face de la lame (plaque rivetee)
for s_ in (1,-1):
    R=0.046; n=24
    vs_f=[];vs_b=[]
    yb=s_*TC; yf=s_*(TC+0.004)
    cen_f=bm.verts.new((XG,yf,0)); cen_b=bm.verts.new((XG,yb,0))
    for k in range(n+1):
        a=-math.pi/2+math.pi*k/n
        x=XG-R*math.cos(a); z=R*math.sin(a)
        vs_f.append(bm.verts.new((x,yf,z))); vs_b.append(bm.verts.new((x,yb,z)))
    for k in range(n):
        f=bm.faces.new([cen_f,vs_f[k],vs_f[k+1]] if s_>0 else [cen_f,vs_f[k+1],vs_f[k]])
        q=[vs_f[k],vs_f[k+1],vs_b[k+1],vs_b[k]]
        bm.faces.new(q if s_>0 else q[::-1])
    add_rivet(bm,(XG-0.020,yf,0),0.008,'y')
    for k in range(5):
        a=-math.pi/2+math.pi*(k+0.5)/5
        add_rivet(bm,(XG-0.038*math.cos(a),yf,0.038*math.sin(a)),0.0035,'y')
# rivets sur la garde (faces avant et arriere)
for xf in (XG-0.0005,XG+GT+0.0005):
    for zz in (GH/2-0.03,0.055,-0.055,-GH/2+0.03):
        add_rivet(bm,(xf,0,zz),0.0055,'x')
# ---------------- virole + pommeau ----------------
octa_lathe(bm,[(X_FER0-0.001,0.026),(X_FER0+0.004,0.028),(X_FER1-0.006,0.026),(X_FER1-0.002,0.022),(X_FER1+0.004,0.021)])
octa_lathe(bm,[(X_POM0-0.004,0.021),(X_POM0+0.002,0.022),(X_POM0+0.008,0.020),(X_POM0+0.012,0.026),(X_POM0+0.018,0.034),(X_POM1-0.016,0.035),(X_POM1-0.008,0.031),(X_POM1-0.001,0.022),(X_POM1,0.012)])
bm.normal_update(); bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]); boxuv(bm,uvl)
fer=new_obj('fer',bm,[M_FER])
# ---------------- POIGNEE (cuir) ----------------
bm=bmesh.new(); uvl=bm.loops.layers.uv.new('UVMap')
NA=40; NL=60; circ=2*math.pi*R_GRIP
rings=[]
for i in range(NL+1):
    x=X_GRIP0+(X_GRIP1-X_GRIP0)*i/NL
    r=R_GRIP*(1+0.04*math.sin(math.pi*i/NL))
    rings.append([bm.verts.new((x,r*math.cos(2*math.pi*k/NA),r*math.sin(2*math.pi*k/NA))) for k in range(NA)])
for i in range(NL):
    for k in range(NA):
        k2=(k+1)%NA
        f=bm.faces.new([rings[i][k],rings[i][k2],rings[i+1][k2],rings[i+1][k]])
        for l,(ii,kk) in zip(f.loops,[(i,k),(i,k+1),(i+1,k+1),(i+1,k)]):
            l[uvl].uv=(kk/NA,(X_GRIP1-X_GRIP0)*ii/NL/circ)
bm.normal_update(); bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
cuir=new_obj('cuir',bm,[M_CUIR])
# ---------------- assemblage ----------------
for o in (lame,fer,cuir):
    o.data.shade_smooth(); o.data.set_sharp_from_angle(angle=math.radians(35))
bpy.ops.object.select_all(action='DESELECT')
for o in (lame,fer,cuir): o.select_set(True)
bpy.context.view_layer.objects.active=lame; bpy.ops.object.join()
k=bpy.context.view_layer.objects.active; k.name='katana_kurogane'; k.data.name='katana_kurogane'
tris=sum(len(p.vertices)-2 for p in k.data.polygons)
print('TRIS',tris,'VERTS',len(k.data.vertices),'MATS',[m.name for m in k.data.materials])
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/kurogane/katana_kurogane_build.blend')
