import bpy
import xml.etree.ElementTree as ET, numpy as np
from mathutils import Quaternion, Vector, Matrix
X='/root/.config/blender/5.2/scripts/addons/sollumz/tools/BoneProperties.xml'
def load():
    B=[]
    for it in ET.parse(X).getroot().findall('Item'):
        g=lambda n,a: float(it.find(n).get(a))
        B.append(dict(name=it.find('Name').text, tag=int(it.find('Tag').get('value')), idx=int(it.find('Index').get('value')),
            parent=int(it.find('ParentIndex').get('value')),
            t=Vector((g('Translation','x'),g('Translation','y'),g('Translation','z'))),
            q=Quaternion((g('Rotation','w'),g('Rotation','x'),g('Rotation','y'),g('Rotation','z')))))
    return B
def world(B, local_q=None):
    byidx={b['idx']:b for b in B}; W={}
    def get(i):
        if i in W: return W[i]
        b=byidx[i]; q=(local_q or {}).get(b['name'], b['q'])
        M=Matrix.Translation(b['t'])@q.to_matrix().to_4x4()
        W[i]=M if b['parent']<0 else get(b['parent'])@M
        return W[i]
    for b in B: get(b['idx'])
    return {byidx[i]['name']:W[i] for i in W}
