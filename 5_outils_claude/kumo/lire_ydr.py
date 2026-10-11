# Lecteur minimal de .ydr natif (RSC7, Gen8) : extrait les sommets d un katana deja en jeu.
# Usage : exec(open("lire_ydr.py").read()) avec sys.argv[1] = chemin du .ydr, puis geoms().
# Sert a comparer le placement en main avec une arme validee (check_kumo.py, noir_pts.npy = Katana Noir).
import struct,zlib,sys
def pagesize(v):
    s=[(v>>27)&1,((v>>26)&1)<<1,((v>>25)&1)<<2,((v>>24)&1)<<3,((v>>17)&0x7f)<<4,((v>>11)&0x3f)<<5,((v>>7)&0xf)<<6,((v>>5)&3)<<7,((v>>4)&1)<<8]
    return (0x200<<(v&0xf))*sum(s)
d=open(sys.argv[1],'rb').read()
_,ver,vf,pf=struct.unpack('<4sIII',d[:16])
raw=zlib.decompress(d[16:],-15)
vs=pagesize(vf);ps=pagesize(pf)
print('ver',ver,'virt',vs,'phys',ps,'raw',len(raw))
V=raw[:vs];P=raw[vs:vs+ps]
def rd(p,n):
    seg=p>>28;o=p&0x0fffffff
    return (V if seg==5 else P)[o:o+n]
def u64(p):return struct.unpack('<Q',rd(p,8))[0]
def u32(p):return struct.unpack('<I',rd(p,4))[0]
def u16(p):return struct.unpack('<H',rd(p,2))[0]
SZ={0:0,1:4,2:4,3:8,5:8,6:12,7:16,8:4,9:4,10:4}
NAMES=['pos','bw','bi','nrm','col0','col1']+['uv%d'%i for i in range(8)]+['tan','bin']
def geoms():
    out=[]
    mp=u64(0x50000050); n=u16(mp+8); arr=u64(mp)
    for mi in range(n):
        m=u64(arr+8*mi); gp=u64(m+8); gn=u16(m+0x10)
        for gi in range(gn):
            g=u64(gp+8*gi); vb=u64(g+0x18); ib=u64(g+0x38)
            stride=u16(vb+8); vc=u32(vb+0x18); dp=u64(vb+0x10); info=u64(vb+0x30)
            flags=u32(info); types=u64(info+8)
            ic=u32(ib+8); ip=u64(ib+0x10)
            comps=[];off=0
            for b in range(16):
                if flags>>b&1:
                    t=types>>(4*b)&0xf; comps.append((NAMES[b],t,off)); off+=SZ[t]
            data=rd(dp,stride*vc); idx=struct.unpack('<%dH'%ic,rd(ip,2*ic))
            out.append(dict(model=mi,geom=gi,stride=stride,vc=vc,ic=ic,comps=comps,data=data,idx=idx,sh=u16(m+0x20) if 0 else None,geomptr=g))
    return out
