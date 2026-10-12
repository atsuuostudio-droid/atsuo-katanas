# retire le "faux corps de cheval" (cylindre + bouts) a l'interieur de la selle -> glb nettoye
import bpy, bmesh, os, math
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=os.environ['GLB'])
ob=[o for o in bpy.data.objects if o.type=='MESH'][0]
bm=bmesh.new(); bm.from_mesh(ob.data)
M=ob.matrix_world
R=float(os.environ.get('RCUT','0.235'))
dead=[]
for f in bm.faces:
    c=M@f.calc_center_median(); r=math.hypot(c.y,c.z-0.45)
    if r<R and c.z<0.66: dead.append(f)                                  # interieur du corps
    elif c.z<0.45 and abs(c.y)<R and r<0.27: dead.append(f)              # dessous (ventre)
    else:
        n=(M.to_3x3()@f.normal).normalized()
        radial=abs(n.y*c.y+n.z*(c.z-0.45))/max(r,1e-6)              # normale dirigee vers l'axe du corps
        if c.z<0.42 and r<0.34 and radial>0.75 and abs(n.z)>0.3: dead.append(f)   # peau du ventre (anneau)
        elif c.z<0.28 and abs(c.y)<0.27 and abs(n.y)<0.55: dead.append(f)    # arc restant sous le ventre (pas les quartiers)
        elif abs(n.x)>0.6 and r<0.37 and c.z<0.62 and abs(c.y)<0.30: dead.append(f)  # bouts de l'anneau (avant / arriere)
print('faces retirees',len(dead),'sur',len(bm.faces))
bmesh.ops.delete(bm,geom=dead,context='FACES')
bm.to_mesh(ob.data); ob.data.update()
bpy.ops.export_scene.gltf(filepath=os.environ['OUT'], export_format='GLB')
