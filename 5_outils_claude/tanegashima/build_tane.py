# Tanegashima (hinawaju) procedural : X = le long de l'arme (bouche vers +X), Z = haut, Y = cote (platine en -Y)
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix
sys.path.insert(0,'/home/claude/tanegashima/scripts')
TEX='/home/claude/tanegashima/tex/'
bpy.ops.wm.read_factory_settings(use_empty=True)
K=0.000667
def P(px,py): return ((px-720)*K, -(py-237)*K)
def mk_mat(name,base,rough,metal):
    m=bpy.data.materials.new(name); nt=m.node_tree; N=nt.nodes; bs=N['Principled BSDF']
    def img(f,col):
        n=N.new('ShaderNodeTexImage'); n.image=bpy.data.images.load(TEX+f); n.image.colorspace_settings.name='sRGB' if col else 'Non-Color'; return n
    d=img(base+'_d.png',True); nt.links.new(d.outputs[0],bs.inputs['Base Color'])
    nn=img(base+'_n.png',False); nm=N.new('ShaderNodeNormalMap'); nt.links.new(nn.outputs[0],nm.inputs[1]); nt.links.new(nm.outputs[0],bs.inputs['Normal'])
    s=img(base+'_s.png',False); nt.links.new(s.outputs[0],bs.inputs['Specular IOR Level'])
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal; return m
M_BOIS=mk_mat('bois','bois',0.55,0.0); M_FER=mk_mat('fer','fer',0.45,0.85); M_CORD=mk_mat('cordon','cordon',0.8,0.0)
objs=[]
def link(o): bpy.context.collection.objects.link(o); objs.append(o); return o
def to_mesh(ob,mat,uvfun):
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    bpy.ops.object.convert(target='MESH'); ob=bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    me=ob.data; me.materials.clear(); me.materials.append(mat)
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=1e-6)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]); uvl=bm.loops.layers.uv.verify()
    for f in bm.faces:
        for l in f.loops: l[uvl].uv=uvfun(l.vert.co,f.normal)
    bm.to_mesh(me); bm.free(); me.update(); return ob
def boxuv(sc):
    def f(co,n):
        a=max(range(3),key=lambda i:abs(n[i])); p=[co[i] for i in range(3) if i!=a]; return (p[0]/sc,p[1]/sc)
    return f
def wooduv(co,n):   # veinage le long de X
    if abs(n.z)>0.7: return (co.x/0.6, 0.5+co.y/0.3)
    return (co.x/0.6, 0.5+co.z/0.3+ (0.15 if n.y>0 else 0.0))
XZ=Matrix(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))   # courbe 2D (x,y) -> monde (X,Z), extrusion locale Z -> monde -Y
# ---------------- CROSSE + FUT (bois) ----------------
outline=[(1850,252),(760,252),(724,236),(600,233),(450,248),(300,272),(150,318),(42,352),(30,468),(80,478),(150,470),(230,442),(300,402),(360,374),(480,348),(600,337),(760,314),(1100,303),(1850,300)]
cu=bpy.data.curves.new('crosse','CURVE'); cu.dimensions='2D'; cu.fill_mode='BOTH'
cu.extrude=0.012; cu.bevel_depth=0.007; cu.bevel_resolution=3; cu.offset=-0.007
sp=cu.splines.new('POLY'); sp.points.add(len(outline)-1); sp.use_cyclic_u=True
for i,(px,py) in enumerate(outline): x,z=P(px,py); sp.points[i].co=(x,z,0,1)
ob=link(bpy.data.objects.new('crosse',cu)); ob.matrix_world=XZ
crosse=to_mesh(ob,M_BOIS,wooduv)
# ---------------- CANON octogonal (fer) ----------------
bm=bmesh.new(); uvl=bm.loops.layers.uv.new('UVMap')
xb0,_=P(705,0); xm,_=P(1975,0)
R=0.0105; zc=P(0,237)[1]-0.002
prof=[(xb0,R*1.02),(xb0+0.01,R),(P(1878,0)[0],R*0.97),(P(1881,0)[0],R*1.45),(xm-0.004,R*1.45),(xm,R*1.32)]
rings=[]
for x,r in prof:
    rings.append([bm.verts.new((x,r*math.cos(2*math.pi*k/8+math.pi/8),zc+r*math.sin(2*math.pi*k/8+math.pi/8))) for k in range(8)])
for i in range(len(rings)-1):
    for k in range(8): bm.faces.new([rings[i][k],rings[i][(k+1)%8],rings[i+1][(k+1)%8],rings[i+1][k]])
bm.faces.new(rings[0][::-1])
# bouche creuse (ame octogonale)
outer=rings[-1]
inner=[bm.verts.new((xm,R*0.55*math.cos(2*math.pi*k/8+math.pi/8),zc+R*0.55*math.sin(2*math.pi*k/8+math.pi/8))) for k in range(8)]
innerb=[bm.verts.new((xm-0.05,R*0.55*math.cos(2*math.pi*k/8+math.pi/8),zc+R*0.55*math.sin(2*math.pi*k/8+math.pi/8))) for k in range(8)]
for k in range(8):
    k2=(k+1)%8
    bm.faces.new([outer[k],outer[k2],inner[k2],inner[k]])
    bm.faces.new([inner[k],inner[k2],innerb[k2],innerb[k]])
bm.faces.new(innerb[::-1])
def box(bm,c,s):
    r=bmesh.ops.create_cube(bm,size=1.0)
    for v in r['verts']: v.co=Vector((c[0]+v.co.x*s[0],c[1]+v.co.y*s[1],c[2]+v.co.z*s[2]))
# guidon + hausse
box(bm,(P(1915,0)[0],0,zc+R*1.45+0.009),(0.014,0.006,0.020))          # guidon haut sur la bouche
box(bm,(P(1010,0)[0],0,zc+R+0.003),(0.010,0.008,0.006))                 # hausse
box(bm,((P(605,0)[0]+P(765,0)[0])/2,0,P(0,240)[1]),(P(765,0)[0]-P(605,0)[0],0.022,0.012))   # queue de culasse (fer sur la poignee)
box(bm,((P(1310,0)[0]+P(1370,0)[0])/2,-0.0192,P(0,272)[1]),(P(1370,0)[0]-P(1310,0)[0],0.0012,0.010))   # plaquette du fut
box(bm,((P(1310,0)[0]+P(1370,0)[0])/2, 0.0192,P(0,272)[1]),(P(1370,0)[0]-P(1310,0)[0],0.0012,0.010))
# capucines (bandes) autour canon+fut
for px,w,top,bot in ((1015,0.024,222,302),(1866,0.020,222,312)):
    x,_=P(px,0); zt=P(0,top)[1]; zb=P(0,bot)[1]; box(bm,(x,0,(zt+zb)/2),(w,0.041,zt-zb))
# plaque de couche (talon) et embout du fut
box(bm,(P(40,0)[0],0,P(0,414)[1]),(0.020,0.041,0.088))   # talon ferre
# platine (cote -Y)
plate=[(285,330),(300,312),(560,282),(745,268),(750,300),(560,312),(300,345)]
for (a,b) in [(0,0)]:
    pass
bm.normal_update()
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
for f in bm.faces:
    a=max(range(3),key=lambda i:abs(f.normal[i]))
    for l in f.loops:
        co=l.vert.co; p=[co[i] for i in range(3) if i!=a]; l[uvl].uv=(p[0]/0.12,p[1]/0.12)
me=bpy.data.meshes.new('canon'); bm.to_mesh(me); bm.free(); me.materials.append(M_FER)
canon=link(bpy.data.objects.new('canon',me))
# ---------------- PLATINE (plaque de fer sur le flanc) ----------------
cu=bpy.data.curves.new('platine','CURVE'); cu.dimensions='2D'; cu.fill_mode='BOTH'; cu.extrude=0.0012; cu.bevel_depth=0.0006
sp=cu.splines.new('POLY'); pts=[(282,333),(300,312),(560,282),(752,266),(756,300),(560,314),(300,348)]
sp.points.add(len(pts)-1); sp.use_cyclic_u=True
for i,(px,py) in enumerate(pts): x,z=P(px,py); sp.points[i].co=(x,z,0,1)
ob=link(bpy.data.objects.new('platine',cu)); ob.matrix_world=Matrix.Translation((0,-0.0195,0))@XZ
platine=to_mesh(ob,M_FER,boxuv(0.12))
# ---------------- pieces en tube (serpentin, pontet, detente, baguette) ----------------
def tube(name,pts,r,mat,y=0.0,res=3):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=res; cu.use_fill_caps=True
    sp=cu.splines.new('NURBS' if len(pts)>3 else 'POLY'); sp.points.add(len(pts)-1)
    for i,p in enumerate(pts): sp.points[i].co=(p[0],p[1],p[2],1)
    if sp.type=='NURBS': sp.use_endpoint_u=True; sp.order_u=3
    ob=link(bpy.data.objects.new(name,cu)); return to_mesh(ob,mat,boxuv(0.05))
Y_SIDE=-0.021
serp=[P(375,318),P(470,265),P(560,215),P(630,186),P(680,182),P(695,195)]
serpentin=tube('serpentin',[(x,Y_SIDE,z) for x,z in serp],0.0028,M_FER)
pivot=tube('pivot',[(P(375,318)[0],Y_SIDE,P(375,318)[1]),(P(375,318)[0],Y_SIDE-0.004,P(375,318)[1])],0.006,M_FER)
detente=tube('detente',[(x,0,z) for x,z in (P(398,345),P(405,365),P(395,382),P(385,384))],0.0025,M_FER)
pontet=tube('pontet',[(x,0,z) for x,z in (P(350,372),P(375,385),P(430,388),P(470,375),P(480,350))],0.0022,M_FER)
baguette=tube('baguette',[(P(1250,298)[0],0,P(0,298)[1]),(P(1912,298)[0],0,P(0,298)[1])],0.0034,M_BOIS)
bout=tube('bout_baguette',[(P(1905,298)[0],0,P(0,298)[1]),(P(1946,298)[0],0,P(0,298)[1])],0.0043,M_FER)
# bassinet (godet) + couvercle
bm=bmesh.new(); r_=bmesh.ops.create_cone(bm,cap_ends=True,segments=14,radius1=0.006,radius2=0.0095,depth=0.012)
for v in r_['verts']: v.co=v.co+Vector((P(698,0)[0],Y_SIDE-0.004,P(0,226)[1]))
me=bpy.data.meshes.new('bassinet'); bm.to_mesh(me); bm.free(); me.materials.append(M_FER)
bassinet=link(bpy.data.objects.new('bassinet',me))
# rivets de platine + mon (disque perce)
bm=bmesh.new()
for px,py in ((300,330),(560,298),(735,282)):
    r_=bmesh.ops.create_uvsphere(bm,u_segments=10,v_segments=6,radius=0.003)
    x,z=P(px,py)
    for v in r_['verts']: v.co=Vector((x,Y_SIDE-0.0005+min(0,v.co.y)*0.5,z))+Vector((v.co.x,0,v.co.z))
me=bpy.data.meshes.new('garnitures'); bm.to_mesh(me); bm.free(); me.materials.append(M_FER)
garn=link(bpy.data.objects.new('garnitures',me))
# bloc a fente (karakuri) en relief sur la platine
bmk=bmesh.new()
box(bmk,((P(578,0)[0]+P(672,0)[0])/2,Y_SIDE-0.0035,P(0,284)[1]),(P(672,0)[0]-P(578,0)[0],0.006,P(0,270)[1]-P(0,298)[1]))
box(bmk,((P(598,0)[0]+P(655,0)[0])/2,Y_SIDE-0.0068,P(0,284)[1]),(P(655,0)[0]-P(598,0)[0],0.0012,0.006))
for px,py in ((760,282),(600,316)):
    r_=bmesh.ops.create_uvsphere(bmk,u_segments=10,v_segments=6,radius=0.0035); x,z=P(px,py)
    for v in r_['verts']: v.co=Vector((x+v.co.x,Y_SIDE-0.001+min(0,v.co.y)*0.5,z+v.co.z))
me=bpy.data.meshes.new('karakuri'); bmk.to_mesh(me); bmk.free(); me.materials.append(M_FER); link(bpy.data.objects.new('karakuri',me))
ressort=tube('ressort',[(P(365,316)[0],Y_SIDE-0.004,P(0,316)[1]),(P(592,316)[0],Y_SIDE-0.004,P(0,312)[1])],0.0022,M_FER)
levier=tube('levier',[(x,Y_SIDE-0.004,z) for x,z in (P(682,265),P(682,238),P(690,232))],0.0018,M_FER)
couvercle=tube('couvercle',[(x,Y_SIDE-0.004,z) for x,z in (P(678,212),P(722,212))],0.0016,M_FER)
# mon : disque de fer perce de 5 trous (fleur)
cu=bpy.data.curves.new('mon','CURVE'); cu.dimensions='2D'; cu.fill_mode='BOTH'; cu.extrude=0.0009; cu.resolution_u=4
cx,cz=P(172,386)
def circ(sp,r,ox,oz,n=24):
    sp.points.add(n-1); sp.use_cyclic_u=True
    for k in range(n): a=2*math.pi*k/n; sp.points[k].co=(ox+r*math.cos(a),oz+r*math.sin(a),0,1)
circ(cu.splines.new('POLY'),0.0148,cx,cz,40)
circ(cu.splines.new('POLY'),0.0026,cx,cz,12)
for k in range(5):
    a=math.pi/2+2*math.pi*k/5; circ(cu.splines.new('POLY'),0.0027,cx+0.0072*math.cos(a),cz+0.0072*math.sin(a),12)
ob=link(bpy.data.objects.new('mon',cu)); ob.matrix_world=Matrix.Translation((0,-0.0197,0))@XZ
mon=to_mesh(ob,M_FER,boxuv(0.05))
# noeud de meche (cordon)
noeud=tube('noeud',[(x,Y_SIDE,z) for x,z in (P(680,186),P(700,170),P(715,182),P(700,196),P(683,180),P(700,165))],0.0032,M_CORD)
ring=[]
cx,cz=P(466,300)
for k in range(13):
    a=2*math.pi*k/12; ring.append((cx+0.0085*math.cos(a),Y_SIDE-0.004+0.004*math.sin(a),cz+0.0085*math.sin(a)))
noeud2=tube('noeud2',ring,0.0026,M_CORD)
# ---------------- assemblage ----------------
for o in list(bpy.data.objects):
    if o.type=='MESH':
        for m in o.data.materials: pass
mesh_objs=[o for o in bpy.data.objects if o.type=='MESH']
for o in mesh_objs:
    for p in o.data.polygons: p.use_smooth=True
    o.data.set_sharp_from_angle(angle=math.radians(40))
    if not o.data.uv_layers: o.data.uv_layers.new(name='UVMap')
bpy.ops.object.select_all(action='DESELECT')
for o in mesh_objs: o.select_set(True)
bpy.context.view_layer.objects.active=crosse; bpy.ops.object.join()
g=bpy.context.view_layer.objects.active; g.name='tanegashima'; g.data.name='tanegashima'
print('TRIS',sum(len(p.vertices)-2 for p in g.data.polygons),'MATS',[m.name for m in g.data.materials])
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/tanegashima/tanegashima_build.blend')
