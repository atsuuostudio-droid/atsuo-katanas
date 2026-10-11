# Contrôle "comme en jeu" sans GPU : toute face vue de dos devient transparente (Cycles)
import bpy, sys
sys.path.insert(0,'/home/claude/sakura/scripts')
from render_util import setup_render, cam
bpy.ops.wm.open_mainfile(filepath='/home/claude/sakura/katana_sakura_build.blend')
setup_render((900,600),8)
sc=bpy.context.scene; sc.world.node_tree.nodes['Background'].inputs[0].default_value=(0.9,0.1,0.6,1)
for m in bpy.data.materials:
    nt=m.node_tree; N=nt.nodes; out=N['Material Output']; bs=N['Principled BSDF']
    geo=N.new('ShaderNodeNewGeometry'); tr=N.new('ShaderNodeBsdfTransparent'); mix=N.new('ShaderNodeMixShader')
    nt.links.new(geo.outputs['Backfacing'],mix.inputs[0]); nt.links.new(bs.outputs[0],mix.inputs[1]); nt.links.new(tr.outputs[0],mix.inputs[2])
    nt.links.new(mix.outputs[0],out.inputs[0]); bs.inputs['Metallic'].default_value=0.0
views={
 'pommeau':((0.62,-0.02,0.07),(0.49,0,0.062),35),
 'tsuba_avant':((0.05,-0.12,0.12),(0.196,0,0.055),35),
 'tsuba_arriere':((0.32,0.10,0.10),(0.196,0,0.056),35),
 'poignee_dessus':((0.35,-0.03,0.20),(0.35,0,0.058),35),
 'poignee_cote_y':((0.35,0.17,0.06),(0.35,0,0.058),35),
 'lame_cote_a':((-0.17,-0.9,0.09),(-0.17,0,0.08),35),
 'lame_cote_b':((-0.17,0.9,0.09),(-0.17,0,0.08),35),
 'pointe_dessous':((-0.43,-0.08,-0.05),(-0.46,0,0.07),35),
}
for n,(loc,tg,lens) in views.items():
    cam(loc,tg,lens=lens,name=n); sc.render.filepath=f'/home/claude/sakura/renders/cull_{n}.png'; bpy.ops.render.render(write_still=True)
