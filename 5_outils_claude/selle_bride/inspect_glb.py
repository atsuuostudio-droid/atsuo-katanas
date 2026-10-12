import bpy, sys
from mathutils import Vector
for f in sys.argv[sys.argv.index('--')+1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f)
    print('=====',f)
    tot=0
    for o in bpy.context.scene.objects:
        if o.type=='MESH':
            me=o.data; tot+=len(me.polygons)
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]
            mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
            print(o.name, len(me.vertices),'v',len(me.polygons),'f','mats',[m.name for m in me.materials],'bb',[round(x,3) for x in mn],[round(x,3) for x in mx])
        else: print(o.name,o.type)
    print('total faces',tot)
    for im in bpy.data.images: print('img',im.name,im.size[:])
