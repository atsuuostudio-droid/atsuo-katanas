import subprocess, os
T='/home/claude/kumo/tex/'; O='/home/claude/kumo/out/'
os.makedirs(O,exist_ok=True)
jobs=[('lame_d.png','kumo_lame_d.dds',None,'dxt1'),('lame_n.png','kumo_lame_n.dds',None,'dxt1'),('lame_s.png','kumo_lame_s.dds',None,'dxt1'),
 ('ito_d.png','kumo_ito_d.dds',None,'dxt1'),('ito_n.png','kumo_ito_n.dds',None,'dxt5'),('ito_s.png','kumo_ito_s.dds',(1024,512),'dxt1'),
 ('same_d.png','kumo_same_d.dds',None,'dxt1'),('same_n.png','kumo_same_n.dds',None,'dxt5'),('same_s.png','kumo_same_s.dds',256,'dxt1'),
 ('or_d.png','kumo_or_d.dds',None,'dxt1'),('or_n.png','kumo_or_n.dds',None,'dxt5'),('or_s.png','kumo_or_s.dds',512,'dxt1'),
 ('tsuba_d.png','kumo_tsuba_d.dds',None,'dxt1'),('tsuba_n.png','kumo_tsuba_n.dds',None,'dxt5'),('tsuba_s.png','kumo_tsuba_s.dds',512,'dxt1')]
for s,d,size,comp in jobs:
    a=['convert',T+s]
    if size: a+=['-resize','%dx%d!'%((size,size) if isinstance(size,int) else size)]
    a+=['-define',f'dds:compression={comp}','-define','dds:mipmaps=8',O+d]
    subprocess.run(a,check=True); print(d,os.path.getsize(O+d)//1024,'KB')
