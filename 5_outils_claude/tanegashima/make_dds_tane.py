import subprocess, os
T='/home/claude/tanegashima/tex/'; O='/home/claude/tanegashima/out/'
os.makedirs(O,exist_ok=True)
jobs=[('bois_d.png','tane_bois_d.dds',None,'dxt1'),('bois_n.png','tane_bois_n.dds',None,'dxt5'),('bois_s.png','tane_bois_s.dds',(1024,512),'dxt1'),
 ('fer_d.png','tane_fer_d.dds',None,'dxt1'),('fer_n.png','tane_fer_n.dds',None,'dxt5'),('fer_s.png','tane_fer_s.dds',512,'dxt1'),
 ('cordon_d.png','tane_cordon_d.dds',None,'dxt1'),('cordon_n.png','tane_cordon_n.dds',None,'dxt5'),('cordon_s.png','tane_cordon_s.dds',256,'dxt1')]
for s,d,size,comp in jobs:
    a=['convert',T+s]
    if size: a+=['-resize','%dx%d!'%((size,size) if isinstance(size,int) else size)]
    a+=['-define',f'dds:compression={comp}','-define','dds:mipmaps=8',O+d]
    subprocess.run(a,check=True)
print('dds ok')
