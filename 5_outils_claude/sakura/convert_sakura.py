import bpy, sys, os
sys.path.insert(0,'/home/claude/sakura/scripts')
from load_sollumz import load
O='/home/claude/sakura/out/'
bpy.ops.wm.open_mainfile(filepath='/home/claude/sakura/katana_sakura_build.blend')
load()
obj=bpy.data.objects['katana_sakura']
# --- images DDS ---
def dds(name,color):
    im=bpy.data.images.load(O+name); im.colorspace_settings.name='sRGB' if color else 'Non-Color'; return im
mapping={'lame':'sakura_lame','ito':'sakura_ito','same':'sakura_same','or':'sakura_or','tsuba':'sakura_tsuba'}
for m in obj.data.materials:
    pre=mapping[m.name]
    nt=m.node_tree; N=nt.nodes
    if m.name=='lame':   # reconstruire proprement
        for n in list(N):
            if n.type not in ('BSDF_PRINCIPLED','OUTPUT_MATERIAL'): N.remove(n)
        bs=N['Principled BSDF']
        d=N.new('ShaderNodeTexImage'); nt.links.new(d.outputs[0],bs.inputs['Base Color'])
        nn=N.new('ShaderNodeTexImage'); nm=N.new('ShaderNodeNormalMap'); nt.links.new(nn.outputs[0],nm.inputs[1]); nt.links.new(nm.outputs[0],bs.inputs['Normal'])
        s=N.new('ShaderNodeTexImage'); nt.links.new(s.outputs[0],bs.inputs['Specular IOR Level'])
        bs.inputs['Metallic'].default_value=0.9; bs.inputs['Roughness'].default_value=0.18
    bs=N['Principled BSDF']
    bs.inputs['Base Color'].links[0].from_node.image=dds(pre+'_d.dds',True)
    bs.inputs['Specular IOR Level'].links[0].from_node.image=dds(pre+'_s.dds',False)
    bs.inputs['Normal'].links[0].from_node.inputs['Color'].links[0].from_node.image=dds(pre+'_n.dds',False)
for im in list(bpy.data.images):
    if not im.filepath.endswith('.dds'): bpy.data.images.remove(im)
# --- UV / sélection ---
obj.data.uv_layers[0].name='UVMap 0'
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
print('autoconvert', bpy.ops.sollumz.autoconvertmaterials())
print('mats', [m.name for m in obj.data.materials], [getattr(m,'shader_properties',None) and m.shader_properties.name for m in obj.data.materials])
print('drawable', bpy.ops.sollumz.converttodrawable())
print('colors', bpy.ops.sollumz.color_attrs_add_missing(), bpy.ops.sollumz.uv_maps_add_missing())
dr=[o for o in bpy.data.objects if o.sollum_type=='sollumz_drawable'][0]
dr.name='w_me_katana_sakura'
model=[o for o in dr.children][0]; model.name='w_me_katana_sakura.model'
print('embed', bpy.ops.sollumz.setallembedded())
print('UV',[u.name for u in model.data.uv_layers],'COL',[(a.name,a.domain,a.data_type) for a in model.data.color_attributes])
for m in model.data.materials:
    print(m.name, m.sollum_type, [ (n.name, n.image.name if getattr(n,'image',None) else None, getattr(n,'texture_properties',None) and n.texture_properties.embedded) for n in m.node_tree.nodes if n.type=='TEX_IMAGE'])
# chemins relatifs + sauvegarde à côté des DDS
bpy.ops.wm.save_as_mainfile(filepath=O+'Atsuo_Katana_Sakura.blend', relative_remap=True)
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_mainfile()
print('saved', [im.filepath for im in bpy.data.images])
