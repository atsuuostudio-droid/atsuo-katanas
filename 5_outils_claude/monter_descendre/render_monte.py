import sys; OUT=sys.argv[1]
exec(open('/home/claude/monte/monte.py').read())
from PIL import Image, ImageDraw
from skel import world
names=[('mount',1),('dismount',1),('dismount_run',1)]; N=9
im=Image.new('RGB',(N*200,len(names)*2*230),'white'); d=ImageDraw.Draw(im)
SK=[b for b in B if b['name'].startswith('SKEL_')]
for ri,(nm,side) in enumerate(names):
    dur,frames=build(nm,side)
    for k in range(N):
        fr=frames[round(k*(len(frames)-1)/(N-1))]
        W=world(B,fr)
        for view in (0,1):
            ox=k*200+100; oy=(ri*2+view)*230+120
            # vue 0 = de cote (y horizontal), vue 1 = de face (x horizontal)
            Pp=lambda v:(ox+(v.y if view==0 else -v.x)*110, oy-v.z*110)
            for b in SK:
                if b['parent']<0: continue
                pn=byidx[b['parent']]['name']
                if not pn.startswith('SKEL_'): continue
                c=(200,0,0) if '_L_' in b['name'] else (0,0,200) if '_R_' in b['name'] else (0,0,0)
                d.line([Pp(W[pn].translation),Pp(W[b['name']].translation)],fill=c,width=2)
            d.text((ox-90,oy-115),'%s %s %.2f'%(nm,'cote' if view==0 else 'face',k/(N-1)),fill=(0,0,0))
im.save(OUT); print('ok')
