import sys; exec(open('/home/claude/cheval/make_cheval.py').read())
from tools_jenk import jenk
def chan(vals):
    vals=[round(v,6) for v in vals]
    if max(vals)-min(vals)<2e-5:
        return f'''        <Item>
         <Type value="StaticFloat" />
         <Value value="{sum(vals)/len(vals):.7f}" />
        </Item>'''
    mn=min(vals); q=max((max(vals)-mn)/1048575.0,1e-6)
    return f'''        <Item>
         <Type value="QuantizeFloat" />
         <Quantum value="{q:.9g}" />
         <Offset value="{mn:.9g}" />
         <Values>{' '.join('%.7f'%v for v in vals)}</Values>
        </Item>'''
POSB=['SKEL_Spine_Root','SKEL_PelvisRoot']
ROOTR=by['SKEL_ROOT']['q'].to_matrix()
def anim_xml(name,dur,frames,dzs):
    n=len(frames)
    tracks=[(by[b]['tag'],0,b) for b in POSB]+[(b['tag'],1,b['name']) for b in B]
    tracks.sort(key=lambda t: t[0]|(t[1]<<16))
    bid=''.join(f'''
    <Item>
     <BoneId value="{t}" />
     <Track value="{tr}" />
     <Unk0 value="{0 if tr==0 else 1}" />
    </Item>''' for t,tr,_ in tracks)
    seq=''
    for t,tr,b in tracks:
        if tr==0:
            off=ROOTR.inverted()@Vector((0,0,1))
            vs=[by[b]['t']+off*dz for dz in dzs]
            ch='\n'.join(chan([v[i] for v in vs]) for i in range(3))
        else:
            qs=[]; prev=None
            for fr in frames:
                q=fr[b].copy()
                if prev is None and q.w<0: q.negate()
                if prev is not None and q.dot(prev)<0: q.negate()
                qs.append(q); prev=q
            if all((q-qs[0]).magnitude<1e-6 for q in qs):
                q=qs[0]
                ch=f'''        <Item>
         <Type value="StaticQuaternion" />
         <Value x="{q.x:.7f}" y="{q.y:.7f}" z="{q.z:.7f}" w="{q.w:.7f}" />
        </Item>'''
            else: ch='\n'.join(chan([getattr(q,c) for q in qs]) for c in 'xyzw')
        seq+=f'''
      <Item>
       <Channels>
{ch}
       </Channels>
      </Item>'''
    return f'''  <Item>
   <Hash>{name}_anim</Hash>
   <Unknown10 value="0" />
   <FrameCount value="{n}" />
   <SequenceFrameLimit value="{n+30}" />
   <Duration value="{dur:.6f}" />
   <Unknown1C>hash_{(jenk(name+'_anim')+1)&0xFFFFFFFF:08X}</Unknown1C>
   <BoneIds>{bid}
   </BoneIds>
   <Sequences>
    <Item>
     <Hash>hash_00000000</Hash>
     <FrameCount value="{n}" />
     <SequenceData>{seq}
     </SequenceData>
    </Item>
   </Sequences>
  </Item>'''
def clip_xml(name,dur):
    return f'''  <Item>
   <Hash>{name}</Hash>
   <Name>pack:/{name}.clip</Name>
   <Type value="Animation" />
   <Unknown30 value="0" />
   <Tags />
   <Properties />
   <AnimationHash>{name}_anim</AnimationHash>
   <StartTime value="0" />
   <EndTime value="{dur:.6f}" />
   <Rate value="1" />
  </Item>'''
TURN=10.0
JOBS=[('idle',3.0,lambda p:idle_frame(p))]
for g in ('walk','trot','canter','gallop'):
    JOBS.append((g,G[g]['dur'],(lambda g: lambda p: frame(g,p))(g)))
    JOBS.append((g+'_turn_l',G[g]['dur'],(lambda g: lambda p: frame(g,p,TURN))(g)))
    JOBS.append((g+'_turn_r',G[g]['dur'],(lambda g: lambda p: frame(g,p,-TURN))(g)))
JOBS.append(('idle_turn_l',G['turn']['dur'],lambda p: frame('turn',p,14.0)))
JOBS.append(('idle_turn_r',G['turn']['dur'],lambda p: frame('turn',p,-14.0)))
clips=[];anims=[]
for name,dur,fn in JOBS:
    n=int(round(dur*30))+1; frames=[];dzs=[]
    for i in range(n):
        D,dz,_=fn((i%(n-1))/(n-1)); frames.append(to_local_all(D)); dzs.append(dz)
    anims.append(anim_xml(name,dur,frames,dzs)); clips.append(clip_xml(name,dur)); print(name,n)
xml='<?xml version="1.0" encoding="UTF-8"?>\n<ClipDictionary>\n <Clips>\n'+'\n'.join(clips)+'\n </Clips>\n <Animations>\n'+'\n'.join(anims)+'\n </Animations>\n</ClipDictionary>\n'
open(sys.argv[1],'w').write(xml); print('xml ok')
