import subprocess, os
T='/home/claude/sakura/tex/'; O='/home/claude/sakura/out/'
os.makedirs(O,exist_ok=True)
jobs=[('lame_d.png','sakura_lame_d.dds',None,'dxt1'),('lame_n.png','sakura_lame_n.dds',None,'dxt1'),('lame_s.png','sakura_lame_s.dds',None,'dxt1'),
 ('ito_d.png','sakura_ito_d.dds',None,'dxt1'),('ito_n.png','sakura_ito_n.dds',None,'dxt5'),('ito_s.png','sakura_ito_s.dds',(1024,512),'dxt1'),
 ('same_d.png','sakura_same_d.dds',None,'dxt1'),('same_n.png','sakura_same_n.dds',None,'dxt5'),('same_s.png','sakura_same_s.dds',256,'dxt1'),
 ('or_d.png','sakura_or_d.dds',None,'dxt1'),('or_n.png','sakura_or_n.dds',None,'dxt5'),('or_s.png','sakura_or_s.dds',512,'dxt1'),
 ('tsuba_d.png','sakura_tsuba_d.dds',None,'dxt1'),('tsuba_n.png','sakura_tsuba_n.dds',1024,'dxt5'),('tsuba_s.png','sakura_tsuba_s.dds',1024,'dxt1'),
 ('rim_d.png','sakura_rim_d.dds',None,'dxt1'),('rim_n.png','sakura_rim_n.dds',None,'dxt5'),('rim_s.png','sakura_rim_s.dds',None,'dxt1')]
for s,d,size,comp in jobs:
    a=['convert',T+s]
    if size: a+=['-resize','%dx%d!'%((size,size) if isinstance(size,int) else size)]
    a+=['-define',f'dds:compression={comp}','-define','dds:mipmaps=8',O+d]
    subprocess.run(a,check=True); print(d,os.path.getsize(O+d)//1024,'KB')
