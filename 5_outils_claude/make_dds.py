import subprocess, cv2, numpy as np, os, sys
sys.path.insert(0,'/home/claude/kin/scripts')
from tex_common import *
T='/home/claude/kin/tex/'; O='/home/claude/kin/out/'
# lame : diffuse d'origine réduite + spec dérivée + normal plat
src=cv2.imread('/home/claude/kin/lame_basecolor.png')
d=cv2.resize(src,(2048,2048),interpolation=cv2.INTER_AREA); cv2.imwrite(T+'lame_d.png',d)
g=cv2.cvtColor(cv2.resize(src,(1024,1024),interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2GRAY).astype(np.float32)/255
save_gray(T+'lame_s.png',np.clip(0.55+0.45*g,0,1))
save_rgb(T+'lame_n.png',np.full((256,256,3),(128,128,255),np.uint8))
jobs=[ # (src, dst, size, compression)
 ('lame_d.png','kin_lame_d.dds',2048,'dxt1'),('lame_n.png','kin_lame_n.dds',256,'dxt1'),('lame_s.png','kin_lame_s.dds',1024,'dxt1'),
 ('ito_d.png','kin_ito_d.dds',None,'dxt1'),('ito_n.png','kin_ito_n.dds',None,'dxt5'),('ito_s.png','kin_ito_s.dds',(1024,512),'dxt1'),
 ('same_d.png','kin_same_d.dds',None,'dxt1'),('same_n.png','kin_same_n.dds',None,'dxt5'),('same_s.png','kin_same_s.dds',256,'dxt1'),
 ('kin_d.png','kin_or_d.dds',None,'dxt1'),('kin_n.png','kin_or_n.dds',None,'dxt5'),('kin_s.png','kin_or_s.dds',512,'dxt1'),
 ('tsuba_d.png','kin_tsuba_d.dds',None,'dxt1'),('tsuba_n.png','kin_tsuba_n.dds',None,'dxt5'),('tsuba_s.png','kin_tsuba_s.dds',512,'dxt1'),
]
for s,dname,size,comp in jobs:
    args=['convert',T+s]
    if size: args+=['-resize','%dx%d!'%((size,size) if isinstance(size,int) else size)]
    args+=['-define',f'dds:compression={comp}','-define','dds:mipmaps=fromlist' if False else 'dds:mipmaps=8',O+dname]
    subprocess.run(args,check=True)
    print(dname, os.path.getsize(O+dname)//1024,'KB')
