# Selle + bride -> drawables FiveM (Sollumz), 5 tailles chacune
import bpy, os, sys, math
from mathutils import Matrix, Vector
sys.path.insert(0,'/home/claude/tanegashima/scripts')
from load_sollumz import load
S='/tmp/claude-0/-home-user-atsuo-katanas/1d790993-5d56-5af0-a69e-ff68766c3d76/scratchpad/selle'
load()
KS=[int(x) for x in os.environ.get('KS','100,120,140,160,180').split(',')]
ONLY=os.environ.get('ONLY')
# selle : PLUS LARGE (cheval de trait), moins haute, un peu plus courte -> elle epouse le dos
SADDLE_FIT=Matrix.Diagonal((1.32,0.95,0.80,1.0))
ITEMS={
 # nom, glb, texture, echelle de base (k=1), point d'origine (modele), rotation de mise en place
 'selle':('saddle','edo_selle_d.dds',0.62,Vector((0.0,0.0,0.691)),Matrix.Rotation(math.radians(-90),4,'Z')),
 'bride':('bridle','edo_bride_d.dds',0.2546/0.555,Vector((-0.286,0.0,0.605)),
          Matrix(((0,1,0,0),(0,0,-1,0),(-1,0,0,0),(0,0,0,1)))),
}
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
for item,(glb,tex,s0,orig,rot) in ITEMS.items():
    if ONLY and item!=ONLY: continue
    for k in KS:
        for o in list(bpy.data.objects): bpy.data.objects.remove(o)
        bpy.ops.import_scene.gltf(filepath=f'{S}/in/{glb}.glb')
        ob=[o for o in bpy.data.objects if o.type=='MESH'][0]
        ob.data.transform(ob.matrix_world); ob.parent=None; ob.matrix_world=Matrix.Identity(4)
        for o in list(bpy.data.objects):
            if o!=ob: bpy.data.objects.remove(o)
        s=s0*k/100.0
        fit=SADDLE_FIT if item=='selle' else Matrix.Identity(4)
        ob.data.transform(fit@Matrix.Scale(s,4)@rot@Matrix.Translation(-orig))
        name=f'edo_{item}2_k{k}' if item=='selle' else f'edo_{item}_k{k}'
        ob.name=name; ob.data.name=name
        # materiau : une seule texture diffuse (DDS)
        m=ob.data.materials[0]; m.name=f'edo_{item}'
        N=m.node_tree.nodes; bs=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]
        for n in list(N):
            if n.type not in ('BSDF_PRINCIPLED','OUTPUT_MATERIAL'): N.remove(n)
        t=N.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(f'{S}/tex/{tex}'); t.image.colorspace_settings.name='sRGB'
        m.node_tree.links.new(t.outputs[0],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value=0.55; bs.inputs['Metallic'].default_value=0.0
        ob.data.uv_layers[0].name='UVMap 0'
        bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
        bpy.ops.sollumz.autoconvertmaterials()
        bpy.ops.sollumz.converttodrawable()
        bpy.ops.sollumz.color_attrs_add_missing(); bpy.ops.sollumz.uv_maps_add_missing()
        dr=[o for o in bpy.data.objects if o.sollum_type=='sollumz_drawable'][0]; dr.name=name
        md=[o for o in dr.children][0]; md.name=name+'.model'
        for mt in md.data.materials:
            for n in mt.node_tree.nodes:
                if n.type=='TEX_IMAGE' and hasattr(n,'texture_properties'): n.texture_properties.embedded=False
        bpy.ops.object.select_all(action='SELECT')
        r=bpy.ops.sollumz.export_assets(directory=f'{S}/xml/', direct_export=True, use_custom_settings=True, target_formats={'CWXML'}, target_versions={'GEN8'})
        bb=[dr.matrix_world@Vector(c) for c in md.bound_box]
        print('EXPORT',name,r,'bb',[round(min(v[i] for v in bb),3) for i in range(3)],[round(max(v[i] for v in bb),3) for i in range(3)])
