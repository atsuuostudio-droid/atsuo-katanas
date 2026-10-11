import bpy, bmesh, math, sys, numpy as np
from mathutils import Vector
sys.path.insert(0,'/home/claude/sakura/scripts')
from params import *
TEX='/home/claude/sakura/tex/'
bpy.ops.wm.read_factory_settings(use_empty=True)
# ---------------- lame procédurale (Kumo) ----------------
from blade_params import *
NS=170
def section(s):
    """profil (f, y) côté +y, du tranchant au dos ; f = fraction de largeur"""
    T=ts(s); g=hi_depth(s)*HI_DEPTH*T
    pts=[(0.0,0.0)]
    for f in (0.03,0.08,0.16,0.27,0.40,0.54,0.66):
        u=f/F_SHIN; pts.append((f,T*(1-(1-u)**1.7)))
    pts.append((F_SHIN,T))
    yh=T*0.95
    pts+=[(F_HI0,yh),(F_HI0+0.012,yh-g*0.8),(F_HI0+0.035,yh-g),((F_HI0+F_HI1)/2,yh-g),(F_HI1-0.035,yh-g),(F_HI1-0.012,yh-g*0.8),(F_HI1,yh*0.97)]
    pts+=[(0.955,T*0.86),(1.0,0.0)]
    return pts
bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap')
ss=[LB*(1-(1-i/NS)**1.0) for i in range(NS+1)]
# resserrer près de la pointe
ss=sorted(set([LB*i/NS for i in range(NS)]+[LB-KL*(1-j/24) for j in range(25)]))
rings=[];ruv=[]
for s in ss:
    x=X_BASE-s; zb=zback(s); w=wid(s)
    top=zb; bot=zb-w; tsc=1.0
    if s>LB-KL:
        t_=(s-(LB-KL))/KL
        top=zb-0.18*WY*t_**2
        bot=zb-WY+WY*0.82*(1-math.sqrt(max(0.0,1-t_**2)))
        tsc=max(0.0,1-t_**2)**0.5
    prof=section(s)
    ring=[];uvr=[]
    if s>=LB-1e-9:
        v=bm.verts.new((x,0,top)); rings.append([v]*(2*len(prof)-2)); ruv.append([(1.0,1-(zb-top)/w)]*(2*len(prof)-2)); continue
    full=prof+[(f,-y) for (f,y) in prof[-2:0:-1]]
    for (f,y) in full:
        z=bot+(top-bot)*f
        ring.append(bm.verts.new((x,y*tsc,z)))
        uvr.append((s/LB, 1-(zb-z)/w))
    rings.append(ring); ruv.append(uvr)
n=len(rings[0])
for i in range(len(rings)-1):
    last=(i==len(rings)-2)
    for j in range(n):
        j2=(j+1)%n
        if last:
            vs=[rings[i][j],rings[i][j2],rings[i+1][0]]; uu=[ruv[i][j],ruv[i][j2],ruv[i+1][0]]
        else:
            vs=[rings[i][j],rings[i][j2],rings[i+1][j2],rings[i+1][j]]; uu=[ruv[i][j],ruv[i][j2],ruv[i+1][j2],ruv[i+1][j]]
        f=bm.faces.new(vs)
        for l,u_ in zip(f.loops,uu): l[uv].uv=u_
# fermer la base (cachée sous la seppa)
c=bm.verts.new((X_BASE,0,zback(0)-wid(0)/2))
for j in range(n):
    f=bm.faces.new([rings[0][(j+1)%n],rings[0][j],c])
    for l in f.loops: l[uv].uv=(0.0,0.5)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
bm.normal_update()
me=bpy.data.meshes.new('lame'); bm.to_mesh(me); bm.free()
lame=bpy.data.objects.new('lame',me); bpy.context.scene.collection.objects.link(lame)

# ---------------- matériaux ----------------
def mk_mat(name,base,rough,metal,nstr=1.0,spec_w=0.5):
    m=bpy.data.materials.new(name); nt=m.node_tree; N=nt.nodes
    bs=N['Principled BSDF']
    def img(f,col):
        n=N.new('ShaderNodeTexImage'); n.image=bpy.data.images.load(TEX+f); n.image.colorspace_settings.name='sRGB' if col else 'Non-Color'; return n
    d=img(base+'_d.png',True); nt.links.new(d.outputs[0],bs.inputs['Base Color'])
    nn=img(base+'_n.png',False); nm=N.new('ShaderNodeNormalMap'); nm.inputs[0].default_value=nstr
    nt.links.new(nn.outputs[0],nm.inputs[1]); nt.links.new(nm.outputs[0],bs.inputs['Normal'])
    s=img(base+'_s.png',False); nt.links.new(s.outputs[0],bs.inputs['Specular IOR Level'])
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
M_ITO=mk_mat('ito','ito',0.55,0.0,1.0)
M_SAME=mk_mat('same','same',0.45,0.0,1.0)
M_KIN=mk_mat('or','or',0.28,0.85,1.0)
M_LAME=mk_mat('lame','lame',0.18,0.9,1.0); lame.data.materials.append(M_LAME)
M_TSUBA=mk_mat('tsuba','tsuba',0.30,0.85,1.0)
# ---------------- utilitaires ----------------
def new_obj(name,bm,mats):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); return o
def ell(x,ry,rz,phi):  # phi=0 en haut (+z)
    return Vector((x, ry*math.sin(phi), zc(x)+rz*math.cos(phi)))
def lathe(name,prof,mat,n=64,tile=0.030,cap0=False,cap1=False,uvmode='cyl',plain=()):
    """prof: liste (x, ry, rz). UV cylindrique : u=phi*reps, v=longueur d'arc/tile"""
    bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap')
    circ=2*math.pi*math.sqrt((prof[0][1]**2+prof[0][2]**2)/2)
    reps=max(1,round(circ/tile))
    rings=[]; arc=[0.0]
    for i,(x,ry,rz) in enumerate(prof):
        if i>0:
            px,pry,prz=prof[i-1]; arc.append(arc[-1]+math.hypot(x-px,((ry+rz)-(pry+prz))/2))
        rings.append([bm.verts.new(ell(x,ry,rz,2*math.pi*j/n)) for j in range(n)])
    for i in range(len(rings)-1):
        for j in range(n):
            j2=(j+1)%n
            f=bm.faces.new([rings[i][j],rings[i][j2],rings[i+1][j2],rings[i+1][j]])
            for l,(ii,jj) in zip(f.loops,[(i,j),(i,j+1),(i+1,j+1),(i+1,j)]):
                if i in plain:
                    l[uv].uv=(0.5+0.08*math.cos(2*math.pi*jj/n),0.5+0.08*math.sin(2*math.pi*jj/n)+0.01*ii)
                else: l[uv].uv=(jj/n*reps, arc[ii]/tile)
            if i in plain: f.material_index=1
    for cap,ring in ((cap0,0),(cap1,len(rings)-1)):
        if cap:
            x,ry,rz=prof[ring]; c=bm.verts.new(Vector((x,0,zc(x))))
            for j in range(n):
                j2=(j+1)%n
                vs=[rings[ring][j],rings[ring][j2],c] if ring else [c,rings[ring][j2],rings[ring][j]]
                f=bm.faces.new(vs)
                for l in f.loops:
                    p=l.vert.co; l[uv].uv=(0.5+p.y/0.04*0.5,0.5+(p.z-zc(p.x))/0.04*0.5)
    bm.normal_update()
    return new_obj(name,bm,[mat,M_TSUBA])
# ---------------- tsuka : tresse ----------------
H=np.load(TEX+'ito_h.npy')
def hsamp(u,v):
    hh,ww=H.shape; x=(u*ww-0.5)%ww; y=(v*hh-0.5)%hh
    x0=int(x);y0=int(y);fx=x-x0;fy=y-y0;x1=(x0+1)%ww;y1=(y0+1)%hh
    return (H[y0,x0]*(1-fx)+H[y0,x1]*fx)*(1-fy)+(H[y1,x0]*(1-fx)+H[y1,x1]*fx)*fy
D=16; NA=N*D; NB=2*D
L=X_WRAP1-X_WRAP0
def shell_pos(a,b,depth=0.0,bulge=True):
    t=a/N; x=X_WRAP0+t*L; th=theta(b); s=scale(t)
    ry,rz=AY*s,AZ*s
    p=Vector((x,ry*math.sin(th),zc(x)+rz*math.cos(th)))
    nrm=Vector((0,math.sin(th)/ry,math.cos(th)/rz)).normalized()
    off=(hsamp(a/N,b/2)-0.25)*0.0012 if bulge else 0.0
    return p+nrm*(off-depth)
def in_window(a,b):
    p=a+b;q=a-b
    dp=abs(p-round(p)); dq=abs(q-round(q))
    if dp<HA-1e-9 and dq<HA-1e-9:
        bc=(round(p)-round(q))/2
        return abs(bc-round(bc))>0.25
    return False
bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap')
corner={}
for i in range(NA+1):
    for j in range(NB+1):
        corner[(i,j)]=bm.verts.new(shell_pos(i/D,j/D))
cent={}
for i in range(NA):
    for j in range(NB):
        cent[(i,j)]=bm.verts.new(shell_pos((i+.5)/D,(j+.5)/D))
for i in range(NA):
    for j in range(NB):
        C=cent[(i,j)]
        BL,BR,TR,TL=corner[(i,j)],corner[(i+1,j)],corner[(i+1,j+1)],corner[(i,j+1)]
        uvs={BL:(i,j),BR:(i+1,j),TR:(i+1,j+1),TL:(i,j+1)}
        keep=[]
        for (v1,v2) in ((BL,BR),(BR,TR),(TR,TL),(TL,BL)):
            ca=( (uvs[v1][0]+uvs[v2][0])/2 + (i+.5) + (i+.5) )/3/D
            cb=( (uvs[v1][1]+uvs[v2][1])/2 + (j+.5) + (j+.5) )/3/D
            keep.append(not in_window(ca,cb))
        if all(keep):
            for tri in ((BL,BR,TR),(BL,TR,TL)):
                f=bm.faces.new(tri)
                for l,vv in zip(f.loops,[uvs[v] for v in tri]): l[uv].uv=(vv[0]/D/N, vv[1]/D/2)
            continue
        for (v1,v2) in ((BL,BR),(BR,TR),(TR,TL),(TL,BL)):
            ca=( (uvs[v1][0]+uvs[v2][0])/2 + (i+.5) + (i+.5) )/3/D
            cb=( (uvs[v1][1]+uvs[v2][1])/2 + (j+.5) + (j+.5) )/3/D
            if in_window(ca,cb): continue
            f=bm.faces.new([v1,v2,C])
            for l,vv in zip(f.loops,[uvs[v1],uvs[v2],(i+.5,j+.5)]):
                l[uv].uv=(vv[0]/D/N, vv[1]/D/2)
# parois des fenêtres
for v in [v for v in cent.values() if not v.link_faces]: bm.verts.remove(v)
bm.edges.ensure_lookup_table()
seam_v=set(corner[(i,0)] for i in range(NA+1))|set(corner[(i,NB)] for i in range(NA+1))
end_v=set(corner[(0,j)] for j in range(NB+1))|set(corner[(NA,j)] for j in range(NB+1))
walls=[e for e in bm.edges if e.is_boundary and not (e.verts[0] in seam_v and e.verts[1] in seam_v) and not (e.verts[0] in end_v and e.verts[1] in end_v)]
inner={}
def inner_of(v):
    if v not in inner:
        p=v.co; d=Vector((0,p.y,p.z-zc(p.x))); 
        inner[v]=bm.verts.new(p-d.normalized()*ITO_T*1.25)
    return inner[v]
for e in walls:
    v1,v2=e.verts
    f0=e.link_faces[0]
    # ordre cohérent avec la face voisine
    lp=[l for l in f0.loops if l.edge==e][0]
    a_,b_=(lp.vert,lp.link_loop_next.vert)
    uva=lp[uv].uv.copy(); uvb=lp.link_loop_next[uv].uv.copy()
    f=bm.faces.new([b_,a_,inner_of(a_),inner_of(b_)])
    for l,u_ in zip(f.loops,[uvb,uva,uva,uvb]): l[uv].uv=u_
bm.normal_update()
tresse=new_obj('tresse',bm,[M_ITO])
# ---------------- tsuka : âme en galuchat ----------------
bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap')
NC=64; NL=48; T_SAME=0.016
rings=[]
for i in range(NL+1):
    t=i/NL; x=X_WRAP0+t*L; s=scale(t)
    rings.append([bm.verts.new(ell(x,AY*s-ITO_T*1.1,AZ*s-ITO_T*1.1,2*math.pi*j/NC)) for j in range(NC)])
circ=2*math.pi*math.sqrt(((AY-ITO_T)**2+(AZ-ITO_T)**2)/2); reps=round(circ/T_SAME)
for i in range(NL):
    for j in range(NC):
        j2=(j+1)%NC
        f=bm.faces.new([rings[i][j],rings[i][j2],rings[i+1][j2],rings[i+1][j]])
        for l,(ii,jj) in zip(f.loops,[(i,j),(i,j+1),(i+1,j+1),(i+1,j)]):
            l[uv].uv=(jj/NC*reps, ii/NL*L/T_SAME)
bm.normal_update(); ame=new_obj('ame',bm,[M_SAME])
# ---------------- menuki (fleurs d'or) ----------------
def flower(center,normal,up,rf,hgt,mat_uvc=(0.5,0.5)):
    bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap')
    side=normal.cross(up).normalized(); up=side.cross(normal).normalized()
    NPh=32; NR=5; petals=16
    def Rphi(ph): return rf*(0.80+0.20*abs(math.cos(petals/2*ph))**0.6)
    c=bm.verts.new(center+normal*hgt*1.25)
    rings=[]
    for k in range(1,NR+1):
        rr=k/NR; ring=[]
        for j in range(NPh):
            ph=2*math.pi*j/NPh; R=Rphi(ph)*rr
            dome=math.sqrt(max(0,1-rr**2))
            bump=0.75+0.25*math.cos(petals*ph) if rr>0.3 else 1.0
            hh=hgt*(0.25+0.75*dome*bump) if k<NR else hgt*0.05
            if rr<0.3: hh=hgt*(1.0+0.25*(1-rr/0.3))
            ring.append(bm.verts.new(center+side*math.cos(ph)*R+up*math.sin(ph)*R+normal*hh))
        rings.append(ring)
    def uvof(v):
        d=v.co-center; return (mat_uvc[0]+d.dot(side)/rf*0.10, mat_uvc[1]+d.dot(up)/rf*0.10)
    faces=[]
    for j in range(NPh):
        faces.append(bm.faces.new([c,rings[0][j],rings[0][(j+1)%NPh]]))
    for k in range(NR-1):
        for j in range(NPh):
            j2=(j+1)%NPh
            faces.append(bm.faces.new([rings[k][j],rings[k+1][j],rings[k+1][j2],rings[k][j2]]))
    for f in faces:
        for l in f.loops: l[uv].uv=uvof(l.vert)
    bm.normal_update(); return bm
menuki_win=list(range(N))
objs_menuki=[]
for k in menuki_win:
    for bside in (0.5,1.5):
        a=k+0.5; t=a/N; x=X_WRAP0+t*L; th=theta(bside); s=scale(t)
        ry,rz=AY*s-ITO_T*1.1,AZ*s-ITO_T*1.1
        p=Vector((x,ry*math.sin(th),zc(x)+rz*math.cos(th)))
        nrm=Vector((0,math.sin(th),0)).normalized()
        big = False
        bmf=flower(p-nrm*0.0003,nrm,Vector((0,0,1)),0.0050,0.0012 if big else 0.0010)
        objs_menuki.append(new_obj(f'menuki_{k}_{bside}',bmf,[M_TSUBA]))
# ---------------- fuchi ----------------
s0=scale(0)
f_ry,f_rz=AY*s0+0.0009,AZ*s0+0.0009
fuchi=lathe('fuchi',[(X_FUCHI1,AY*s0-0.001,AZ*s0-0.001),(X_FUCHI1,f_ry,f_rz),(X_FUCHI1-0.0015,f_ry+0.0003,f_rz+0.0003),
        (X_FUCHI0+0.0025,f_ry+0.0006,f_rz+0.0006),(X_FUCHI0+0.0008,f_ry+0.0012,f_rz+0.0012),(X_FUCHI0,f_ry+0.0009,f_rz+0.0009)],M_KIN,n=72,cap1=False,plain=(0,1,3,4))
# ---------------- kashira ----------------
s1=scale(1)
k_ry,k_rz=AY*s1+0.0010,AZ*s1+0.0010
kas=lathe('kashira',[(X_KASHI0,AY*s1-0.001,AZ*s1-0.001),(X_KASHI0,k_ry,k_rz),(X_KASHI0+0.0012,k_ry+0.0006,k_rz+0.0006),
      (X_END-0.006,k_ry+0.0004,k_rz+0.0004),(X_END-0.0035,k_ry*0.97,k_rz*0.97),(X_END-0.0018,k_ry*0.86,k_rz*0.86),(X_END-0.0006,k_ry*0.62,k_rz*0.62),(X_END,k_ry*0.30,k_rz*0.30)],M_KIN,n=72,cap1=True,plain=(0,1,3))
# ---------------- seppa ----------------
def seppa(name,x0):
    return lathe(name,[(x0,0.0172,0.0228),(x0+SEP_T,0.0172,0.0228)],M_TSUBA,n=72,cap0=True,cap1=True,plain=(0,))
sp0=seppa('seppa0',X_SEP0); sp1=seppa('seppa1',X_SEP1)
for o in (sp0,sp1):  # UV vers le centre or lisse de la texture tsuba
    for l in o.data.uv_layers[0].data: pass
def remap_planar(o,ry,rz,scale_uv):
    me=o.data; uvl=me.uv_layers[0]
    for poly in me.polygons:
        for li in poly.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv=(0.5+v.y/ry*scale_uv,0.5+(v.z-zc(v.x))/rz*scale_uv)
remap_planar(sp0,0.0172,0.0228,0.10); remap_planar(sp1,0.0172,0.0228,0.10)
# ---------------- tsuba ----------------
TRY,TRZ=0.0400,0.0430
bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap')
NP=96
prof=[(0.0,0.5),(0.12,0.5),(0.24,0.5),(0.40,0.5),(0.55,0.5),(0.70,0.5),(0.85,0.5),(0.90,0.5),(0.905,0.56),(0.93,0.62),(0.965,0.64),(0.99,0.60),(1.0,0.5)]
def tpos(rf,side,ph,thick):
    xm=X_TSUBA0+TSUBA_T/2
    x=xm+side*thick*TSUBA_T
    return Vector((x,TRY*rf*math.sin(ph),zc(xm)+TRZ*rf*math.cos(ph)))
faces_info=[]
grid={}
for side in (-1,1):
    for ri,(rf,th) in enumerate(prof):
        if rf==0: grid[(side,ri,0)]=bm.verts.new(tpos(0,side,0,th)); continue
        for j in range(NP): grid[(side,ri,j)]=bm.verts.new(tpos(rf,side,2*math.pi*j/NP,th))
def fuv(rf,ph,side):
    return (0.5+side*0.5*rf*math.sin(ph), 0.5+0.5*rf*math.cos(ph))
for side in (-1,1):
    for ri in range(len(prof)-1):
        r0,r1=prof[ri][0],prof[ri+1][0]
        for j in range(NP):
            j2=(j+1)%NP; p0=2*math.pi*j/NP; p1=2*math.pi*(j+1)/NP
            if r0==0:
                vs=[grid[(side,0,0)],grid[(side,1,j)],grid[(side,1,j2)]]; uvs=[fuv(0,0,side),fuv(r1,p0,side),fuv(r1,p1,side)]
            else:
                vs=[grid[(side,ri,j)],grid[(side,ri+1,j)],grid[(side,ri+1,j2)],grid[(side,ri,j2)]]
                uvs=[fuv(r0,p0,side),fuv(r1,p0,side),fuv(r1,p1,side),fuv(r0,p1,side)]
            if side==-1: vs=vs[::-1]; uvs=uvs[::-1]
            f=bm.faces.new(vs)
            for l,u_ in zip(f.loops,uvs): l[uv].uv=u_
# tranche (bord) : texture kin cylindrique
last=len(prof)-1
circ=2*math.pi*math.sqrt((TRY**2+TRZ**2)/2); reps=round(circ/0.03)
for j in range(NP):
    j2=(j+1)%NP
    vs=[grid[(-1,last,j)],grid[(1,last,j)],grid[(1,last,j2)],grid[(-1,last,j2)]]
    f=bm.faces.new(vs[::-1])
    for l,u_ in zip(f.loops,[(j2/NP*reps,0),(j2/NP*reps,0.2),(j/NP*reps,0.2),(j/NP*reps,0)]): l[uv].uv=u_
bm.normal_update()
tsuba=new_obj('tsuba',bm,[M_TSUBA,M_KIN])
# faces de tranche -> matériau kin
for p in tsuba.data.polygons:
    xs=[tsuba.data.vertices[v].co.x for v in p.vertices]
    if len(p.vertices)==4 and max(xs)-min(xs)>TSUBA_T*0.9: p.material_index=1
# ---------------- habaki ----------------
def hab_section(x,grow):
    pts=[]
    zlo,zhi=0.0322,0.0768; zm=(zlo+zhi)/2; hh=(zhi-zlo)/2*grow
    for j in range(40):
        ph=2*math.pi*j/40
        c,s_=math.cos(ph),math.sin(ph)
        zz=zm+hh*math.copysign(abs(c)**0.5,c)
        frac=(zz-zlo)/(zhi-zlo)
        hw=(0.0042+(0.0060-0.0042)*frac)*grow
        yy=hw*math.copysign(abs(s_)**0.5,s_)
        pts.append(Vector((x,yy,zz+(zc(x)-zc(0.19)))))
    return pts
bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap')
xs=[X_HAB0,X_HAB0+0.0015,X_HAB1-0.002,X_HAB1]; gr=[0.93,0.98,1.0,1.03]
rings=[[bm.verts.new(p) for p in hab_section(x,g)] for x,g in zip(xs,gr)]
for i in range(len(rings)-1):
    for j in range(40):
        j2=(j+1)%40
        f=bm.faces.new([rings[i][j],rings[i][j2],rings[i+1][j2],rings[i+1][j]])
        for l in f.loops: l[uv].uv=(0.5+(l.vert.co.x-X_HAB0-0.017)/0.017*0.09,0.5+(l.vert.co.z-0.0545)/0.022*0.09)
for ring,flip in ((rings[0],True),(rings[-1],False)):
    c=bm.verts.new(sum((v.co for v in ring),Vector())/len(ring))
    for j in range(40):
        vs=[ring[j],ring[(j+1)%40],c]
        if flip: vs=vs[::-1]
        f=bm.faces.new(vs)
        for l in f.loops: l[uv].uv=(0.5+l.vert.co.y/0.006*0.05,0.5+(l.vert.co.z-0.0545)/0.022*0.09)
bm.normal_update(); habaki=new_obj('habaki',bm,[M_TSUBA])
# ---------------- assemblage ----------------
parts=[tresse,ame,fuchi,kas,sp0,sp1,tsuba,habaki]+objs_menuki
for o in parts:
    o.data.shade_smooth()
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active=tresse
bpy.ops.object.join(); monture=bpy.context.view_layer.objects.active; monture.name='monture'
monture.data.set_sharp_from_angle(angle=math.radians(40))
lame.data.shade_smooth(); lame.data.set_sharp_from_angle(angle=math.radians(40))
bpy.ops.object.select_all(action='DESELECT'); lame.select_set(True); monture.select_set(True)
bpy.context.view_layer.objects.active=lame; bpy.ops.object.join()
k=bpy.context.view_layer.objects.active; k.name='katana_sakura'; k.data.name='katana_sakura'
from fix_normals import fix
print('FACES RETOURNEES', fix(k))
# nettoyer matériaux / images inutiles
for img in bpy.data.images: 
    if img.users==0: bpy.data.images.remove(img)
tris=sum(len(p.vertices)-2 for p in k.data.polygons)
print('TRIS',tris,'VERTS',len(k.data.vertices),'MATS',[m.name for m in k.data.materials])
bpy.ops.wm.save_as_mainfile(filepath='/home/claude/sakura/katana_sakura_build.blend')
