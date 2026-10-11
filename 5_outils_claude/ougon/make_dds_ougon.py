import subprocess, os
T='/home/claude/ougon/tex/'; O='/home/claude/ougon/out/'
os.makedirs(O,exist_ok=True)
jobs=[('lame_d.png','ougon_lame_d.dds',None,'dxt1'),('lame_n.png','ougon_lame_n.dds',None,'dxt1'),('lame_s.png','ougon_lame_s.dds',None,'dxt1'),
 ('ito_d.png','ougon_ito_d.dds',None,'dxt1'),('ito_n.png','ougon_ito_n.dds',(2048,1024),'dxt5'),('ito_s.png','ougon_ito_s.dds',(1024,512),'dxt1'),
 ('same_d.png','ougon_same_d.dds',None,'dxt1'),('same_n.png','ougon_same_n.dds',None,'dxt5'),('same_s.png','ougon_same_s.dds',256,'dxt1'),
 ('or_d.png','ougon_or_d.dds',None,'dxt1'),('or_n.png','ougon_or_n.dds',None,'dxt5'),('or_s.png','ougon_or_s.dds',512,'dxt1'),
 ('tsuba_d.png','ougon_tsuba_d.dds',None,'dxt1'),('habaki_d.png','ougon_habaki_d.dds',None,'dxt1'),('habaki_n.png','ougon_habaki_n.dds',None,'dxt5'),('habaki_s.png','ougon_habaki_s.dds',None,'dxt1'),('tsuba_n.png','ougon_tsuba_n.dds',1024,'dxt5'),('tsuba_s.png','ougon_tsuba_s.dds',1024,'dxt1'),
 ('rim_d.png','ougon_rim_d.dds',None,'dxt1'),('rim_n.png','ougon_rim_n.dds',None,'dxt5'),('rim_s.png','ougon_rim_s.dds',None,'dxt1')]
for s,d,size,comp in jobs:
    a=['convert',T+s]
    if size: a+=['-resize','%dx%d!'%((size,size) if isinstance(size,int) else size)]
    a+=['-define',f'dds:compression={comp}','-define','dds:mipmaps=8',O+d]
    subprocess.run(a,check=True); print(d,os.path.getsize(O+d)//1024,'KB')
