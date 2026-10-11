import bpy, math, mathutils
def setup_render(res=(1600,700), samples=32):
    sc=bpy.context.scene
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=samples
    sc.cycles.use_denoising=True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent=False
    w=bpy.data.worlds.new('w'); sc.world=w
    w.use_nodes=True
    bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.35,0.36,0.38,1); bg.inputs[1].default_value=0.6
    for name,loc,energy,size in [('key',(1,-2,2.5),400,2),('fill',(-2,-1.5,1),150,3),('rim',(0,2.5,1.5),250,2)]:
        L=bpy.data.lights.new(name,'AREA'); L.energy=energy; L.size=size
        o=bpy.data.objects.new(name,L); sc.collection.objects.link(o); o.location=loc
        d=mathutils.Vector((0,0,0.07))-o.location; o.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
def cam(loc, target, lens=50, name='cam', ortho=None):
    sc=bpy.context.scene
    c=bpy.data.cameras.new(name); c.lens=lens; c.clip_start=0.001
    if ortho: c.type='ORTHO'; c.ortho_scale=ortho
    o=bpy.data.objects.new(name,c); sc.collection.objects.link(o)
    o.location=loc; d=mathutils.Vector(target)-mathutils.Vector(loc)
    o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); sc.camera=o
    return o
def render(path):
    bpy.context.scene.render.filepath=path; bpy.ops.render.render(write_still=True)
