# Finitions appliquées au Kin APRES convert_sollumz.py + embed_fix.py :
#  - reflets plus forts (lame + or)  - lame entière lumineuse (normal_spec_emissive)
# Lancer : python3 finitions_lame.py  (chemins à adapter)
import bpy, sys
sys.path.insert(0,'/home/claude/sakura/scripts')
from load_sollumz import load
BLEND='/home/claude/sakura/out/Atsuo_Katana_Sakura.blend'; MODEL='w_me_katana_sakura.model'
EMISSIVE=1.5   # lueur rose douce (0 = aucune, 5 = forte)
bpy.ops.wm.open_mainfile(filepath=BLEND); load()
from sollumz.ydr.shader_materials import create_shader
def setp(mn,i,f,fr):
    N=bpy.data.materials[mn].node_tree.nodes
    N['specularIntensityMult'].set_float(i); N['specularFalloffMult'].set_float(f); N['specularFresnel'].set_float(fr)
setp('lame_normal_spec',2.5,400.0,0.97); setp('or_normal_spec',1.6,200.0,0.90); setp('tsuba_normal_spec',1.6,200.0,0.90)
if EMISSIVE>0:
    old=bpy.data.materials['lame_normal_spec']; O=old.node_tree.nodes
    new=create_shader('normal_spec_emissive.sps'); N=new.node_tree.nodes
    for t in ('DiffuseSampler','BumpSampler','SpecSampler'):
        N[t].image=O[t].image; N[t].texture_properties.embedded=True
    for p in ('bumpiness','specularIntensityMult','specularFalloffMult','specularFresnel'): N[p].set_float(O[p].get_float())
    N['specMapIntMask'].set_vec3(tuple(O['specMapIntMask'].get_vec3())); N['emissiveMultiplier'].set_float(EMISSIVE)
    new.name='lame_normal_spec_emissive'
    for s in bpy.data.objects[MODEL].material_slots:
        if s.material==old: s.material=new
    bpy.data.materials.remove(old)
bpy.ops.wm.save_mainfile()
