import sys; sys.path.insert(0,'.')
import pose
from pose import solve, byname
VARIANTS=[('ride_a',dict(flex=55,abd=38,shin_abd=10,shin_back=4,toe_out=12)),
          ('ride_b',dict(flex=52,abd=45,shin_abd=14,shin_back=4,toe_out=14)),
          ('ride_c',dict(flex=50,abd=52,shin_abd=18,shin_back=4,toe_out=16))]
BONES=['SKEL_Pelvis','SKEL_L_Thigh','SKEL_L_Calf','SKEL_L_Foot','SKEL_R_Thigh','SKEL_R_Calf','SKEL_R_Foot']
# le jeu cherche les os par recherche binaire : la liste DOIT etre triee (piste puis id d'os), comme Sollumz
BONES.sort(key=lambda n: byname[n]['tag'] | (1 << 16))
clips=[]; anims=[]
for name,P in VARIANTS:
    L=solve(P)
    L['SKEL_Pelvis']=byname['SKEL_Pelvis']['q'].copy()   # bassin verrouille droit (sinon le calque du haut du corps le tord)
    if L['SKEL_Pelvis'].w<0: L['SKEL_Pelvis'].negate()
    clips.append(f'''  <Item>
   <Hash>{name}</Hash>
   <Name>pack:/{name}.clip</Name>
   <Type value="Animation" />
   <Unknown30 value="0" />
   <Tags />
   <Properties />
   <AnimationHash>{name}_anim</AnimationHash>
   <StartTime value="0" />
   <EndTime value="1" />
   <Rate value="1" />
  </Item>''')
    bids=''.join(f'''
    <Item>
     <BoneId value="{byname[b]['tag']}" />
     <Track value="1" />
     <Unk0 value="1" />
    </Item>''' for b in BONES)
    seq=''.join(f'''
      <Item>
       <Channels>
        <Item>
         <Type value="StaticQuaternion" />
         <Value x="{L[b].x:.7f}" y="{L[b].y:.7f}" z="{L[b].z:.7f}" w="{L[b].w:.7f}" />
        </Item>
       </Channels>
      </Item>''' for b in BONES)
    anims.append(f'''  <Item>
   <Hash>{name}_anim</Hash>
   <Unknown10 value="0" />
   <FrameCount value="31" />
   <SequenceFrameLimit value="31" />
   <Duration value="1" />
   <Unknown1C>hash_00000000</Unknown1C>
   <BoneIds>{bids}
   </BoneIds>
   <Sequences>
    <Item>
     <Hash>hash_00000000</Hash>
     <FrameCount value="31" />
     <SequenceData>{seq}
     </SequenceData>
    </Item>
   </Sequences>
  </Item>''')
xml='<?xml version="1.0" encoding="UTF-8"?>\n<ClipDictionary>\n <Clips>\n'+'\n'.join(clips)+'\n </Clips>\n <Animations>\n'+'\n'.join(anims)+'\n </Animations>\n</ClipDictionary>\n'
if __name__=='__main__': open(sys.argv[1],'w').write(xml); print('xml ok')
