import sys; exec(open('/home/claude/cheval/make_cheval.py').read())
from PIL import Image, ImageDraw
def fk3(Lq,dz):
    Wm={}
    for b in B:
        t=body_trans(b['name'],dz) if b['name'] in BODYROOTS else b['t']
        M=Matrix.Translation(t)@Lq[b['name']].to_matrix().to_4x4()
        Wm[b['name']]=M if b['parent']<0 else Wm[byidx[b['parent']]['name']]@M
    return {n:m.translation for n,m in Wm.items()}
gs=['walk','trot','canter','gallop','turn']; N=8
im=Image.new('RGB',(N*230,len(gs)*260),'white'); d=ImageDraw.Draw(im)
for gi,g in enumerate(gs):
    for k in range(N):
        D,dz,_=frame(g,k/N); pos=fk3(to_local_all(D),dz)
        ox=k*230+130; oy=gi*260+40
        P=lambda v:(ox+v.y*100, oy-(v.z-0.6)*100)
        d.line([(ox-110,P(Vector((0,0,-1)))[1]),(ox+110,P(Vector((0,0,-1)))[1])],fill=(150,150,150))
        for b in B:
            if b['parent']<0 or b['name'].startswith('FB_'): continue
            col=(200,0,0) if '_L_' in b['name'] else (0,0,200) if '_R_' in b['name'] else (0,0,0)
            d.line([P(pos[byidx[b['parent']]['name']]),P(pos[b['name']])],fill=col,width=2)
        d.text((ox-100,oy-30),'%s %.2f'%(g,k/N),fill=(0,0,0))
im.save(sys.argv[1]); print('ok')
