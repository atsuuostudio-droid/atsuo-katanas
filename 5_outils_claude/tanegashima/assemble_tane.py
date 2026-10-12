# Greffe le tanegashima sur le squelette du mousquet GTA (w_ar_musket) -> remplacement de modele
import bpy, sys, bmesh
from mathutils import Vector, Matrix
sys.path.insert(0,'/home/claude/tanegashima/scripts')
from load_sollumz import load
O='/home/claude/tanegashima/out/'
SHIFT=Vector((0.256,0.0,0.045))          # detente du tanegashima -> detente du mousquet
MUZZLE=Vector((0.837,0.0,-0.002))+SHIFT  # bouche du canon (repere mousquet)
bpy.ops.wm.open_mainfile(filepath='/home/claude/tanegashima/musket_import.blend'); load()
with bpy.data.libraries.load('/home/claude/tanegashima/tanegashima_build.blend') as (src,dst):
    dst.objects=['tanegashima']
tg=dst.objects[0]
arm=bpy.data.objects['w_ar_musket']; model=bpy.data.objects['Gun_Root']
print('model matrix', [list(r) for r in model.matrix_world])
me=tg.data.copy(); me.transform(Matrix.Translation(SHIFT))
old=model.data; model.data=me; bpy.data.meshes.remove(old)
model.vertex_groups.clear()
vg=model.vertex_groups.new(name='Gun_Main_Bone'); vg.add(list(range(len(me.vertices))),1.0,'REPLACE')
# textures DDS
def dds(name,color):
    im=bpy.data.images.load(O+name); im.colorspace_settings.name='sRGB' if color else 'Non-Color'; return im
for m in me.materials:
    nt=m.node_tree; bs=nt.nodes['Principled BSDF']; pre='tane_'+m.name
    bs.inputs['Base Color'].links[0].from_node.image=dds(pre+'_d.dds',True)
    bs.inputs['Specular IOR Level'].links[0].from_node.image=dds(pre+'_s.dds',False)
    bs.inputs['Normal'].links[0].from_node.inputs['Color'].links[0].from_node.image=dds(pre+'_n.dds',False)
# os : bouche du canon et talon deplaces sur le tanegashima
bpy.context.view_layer.objects.active=arm; bpy.ops.object.mode_set(mode='EDIT')
eb=arm.data.edit_bones
def move(name,pos):
    b=eb[name]; d=b.tail-b.head; b.head=pos; b.tail=pos+d
move('Gun_Muzzle',MUZZLE)
move('NM_Butt_Marker',Vector((-0.205,0.0,-0.075)))
bpy.ops.object.mode_set(mode='OBJECT')
# collisions (boites du mousquet) etirees sur la longueur du tanegashima + affichees en fil de fer
X0,X1=-0.2897,0.8242; N0,N1=-0.206,1.093
for o in bpy.data.objects:
    if o.sollum_type=='sollumz_bound_box':
        mw=o.matrix_world; inv=mw.inverted()
        for v in o.data.vertices:
            w=mw@v.co; w.x=N0+(w.x-X0)*(N1-N0)/(X1-X0); w.z=w.z+0.012; v.co=inv@w
        o.data.update(); o.display_type='WIRE'
# conversion des materiaux en shaders GTA
me.uv_layers[0].name='UVMap 0'
bpy.ops.object.select_all(action='DESELECT'); model.select_set(True); bpy.context.view_layer.objects.active=model
print('autoconvert', bpy.ops.sollumz.autoconvertmaterials())
print('colors', bpy.ops.sollumz.color_attrs_add_missing(), bpy.ops.sollumz.uv_maps_add_missing())
for m in model.data.materials:
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image: n.texture_properties.embedded=True
    print(m.name,m.sollum_type,[(n.name,n.image.name if n.image else None,n.texture_properties.embedded) for n in m.node_tree.nodes if n.type=='TEX_IMAGE'])
for im in list(bpy.data.images):
    if not im.filepath.endswith('.dds') and im.users==0: bpy.data.images.remove(im)
for o in list(bpy.data.objects):
    if o.name=='tanegashima': bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath=O+'Atsuo_Tanegashima_w_ar_musket.blend', relative_remap=True)
bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
print('ok', len(me.vertices),'verts')
