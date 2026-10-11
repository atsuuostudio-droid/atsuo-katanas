# Animations de cavalier VIVANTES (une boucle par allure) : bassin, colonne, tete, bras, jambes.
# Repere squelette : avant = -Y, gauche = +X, haut = +Z.
import sys, math; sys.path.insert(0,'.')
from skel import *
from sys import float_info
B=load(); by={b['name']:b for b in B}; byidx={b['idx']:b for b in B}
W0=world(B)
def R(axis,deg): return Matrix.Rotation(math.radians(deg),3,axis)
def dirrot(a,b):
    return Vector(a).normalized().rotation_difference(Vector(b).normalized()).to_matrix()
def pos(n): return W0[n].translation
LEGS={'a':dict(flex=55,abd=38,shin_abd=10,shin_back=4,toe_out=12),
      'b':dict(flex=52,abd=45,shin_abd=14,shin_back=4,toe_out=14),
      'c':dict(flex=50,abd=52,shin_abd=18,shin_back=4,toe_out=16)}
# bras au repos : coude pres des cotes, avant-bras vers l'avant, mains devant le ventre (l'IK du script les ajuste)
ARM={}
for side,s in (('L',1),('R',-1)):
    sh=pos('SKEL_%s_UpperArm'%side); el=pos('SKEL_%s_Forearm'%side); ha=pos('SKEL_%s_Hand'%side)
    elT=Vector((s*0.215,-0.06,0.205)); haT=Vector((s*0.085,-0.31,0.165))
    ARM['SKEL_%s_UpperArm'%side]=dirrot(el-sh, elT-sh)
    fo=dirrot(el-sh, elT-sh)@(ha-el)
    ARM['SKEL_%s_Forearm'%side]=dirrot(ha-el, haT-elT)
GAITS={ # duree cycle, inclinaison buste, amplitudes
 'idle':  dict(dur=3.0, lean=3,  pitch=1.2, f=1, roll=0.0, yaw=0.0, legsw=0.0, knee=0.0, pel=0.0, crouch=0),
 'walk':  dict(dur=1.2, lean=4,  pitch=1.5, f=2, roll=3.5, yaw=3.0, legsw=3.0, knee=0.0, pel=1.5, crouch=0),
 'trot':  dict(dur=0.7, lean=6,  pitch=4.0, f=2, roll=1.0, yaw=1.0, legsw=1.0, knee=5.0, pel=3.0, crouch=3),
 'canter':dict(dur=0.75,lean=10, pitch=7.0, f=1, roll=1.5, yaw=1.0, legsw=1.5, knee=4.0, pel=6.0, crouch=5),
 'gallop':dict(dur=0.5, lean=18, pitch=4.5, f=1, roll=1.0, yaw=0.5, legsw=1.0, knee=6.0, pel=3.0, crouch=12),
}
SPINE=['SKEL_Spine_Root','SKEL_Spine0','SKEL_Spine1','SKEL_Spine2','SKEL_Spine3']
SPW=[0.0,0.15,0.35,0.65,1.0]
def frame_deltas(g,legs,ph):
    G=GAITS[g]; P=dict(LEGS[legs]); w=2*math.pi*ph
    c1=math.sin(w); cf=math.sin(G['f']*w)
    lean=G['lean']+G['pitch']*cf
    roll=G['roll']*c1; yaw=G['yaw']*math.sin(w+math.pi/2)
    D={}
    # bassin : roule / bascule avec le cheval
    D['SKEL_Pelvis']=R('Z',yaw)@R('Y',roll)@R('X',G['pel']*cf)
    # colonne : penchee vers l'avant + contre-roulis (le buste reste stable)
    for n,k in zip(SPINE,SPW):
        D[n]=R('Z',yaw*(1-k))@R('Y',roll*(1-1.6*k))@R('X',lean*k)
    tor=D['SKEL_Spine3']
    D['SKEL_Neck_1']=R('X',lean*0.55)@R('Y',-roll*0.3)
    D['SKEL_Head']=R('X',lean*0.25-G['pitch']*cf*0.4)   # la tete reste a l'horizon
    for n,m in ARM.items(): D[n]=tor@m
    # jambes : posture cavalier + balancement / amorti des genoux
    for side,s,sw in (('L',1,1),('R',-1,-1)):
        flex=P['flex']+G['crouch']*0.6+G['legsw']*sw*c1
        D['SKEL_%s_Thigh'%side]=R('Y',-s*P['abd'])@R('X',-flex)
        D['SKEL_%s_Calf'%side]=R('Y',-s*P['shin_abd'])@R('X',P['shin_back']+G['crouch']+G['knee']*max(0,cf))
        D['SKEL_%s_Foot'%side]=R('Z',s*P['toe_out'])
    return D
def to_local(D):
    newW={}
    def wr(n):
        if n in newW: return newW[n]
        b=by[n]
        if n in D: r=D[n]@W0[n].to_3x3()
        else:
            par=byidx[b['parent']]['name'] if b['parent']>=0 else None
            r=(wr(par) if par else Matrix.Identity(3))@b['q'].to_matrix()
        newW[n]=r; return r
    out={}
    for n in D:
        par=byidx[by[n]['parent']]['name']
        q=(wr(par).inverted()@wr(n)).to_quaternion()
        out[n]=q
    return out
# ---------- ecriture XML (meme encodage que Sollumz) ----------
def quant(vals):
    mn=min(vals); mx=max(vals); md=float_info.max; last=0
    for v in vals:
        if v!=last: md=min(md,abs(v-last))
        last=v
    if md==float_info.max: md=0
    q=max(md,(mx-mn)/1048576)
    if q==0: q=1e-6
    return mn,q
def chan(vals):
    vals=[round(v,6) for v in vals]
    if max(vals)-min(vals)<2e-5:
        vals=[sum(vals)/len(vals)]*len(vals)
        return f'''        <Item>
         <Type value="StaticFloat" />
         <Value value="{vals[0]:.7f}" />
        </Item>'''
    mn=min(vals); q=max((max(vals)-mn)/1048575.0, 1e-6)   # 20 bits max, pas de debordement
    return f'''        <Item>
         <Type value="QuantizeFloat" />
         <Quantum value="{q:.9g}" />
         <Offset value="{mn:.9g}" />
         <Values>{' '.join('%.7f'%v for v in vals)}</Values>
        </Item>'''
from tools_jenk import jenk
def anim_xml(name,frames):
    bones=sorted(frames[0].keys(), key=lambda n: by[n]['tag'] | (1<<16))
    n=len(frames)
    bid=''.join(f'''
    <Item>
     <BoneId value="{by[b]['tag']}" />
     <Track value="1" />
     <Unk0 value="1" />
    </Item>''' for b in bones)
    seq=''
    for b in bones:
        qs=[]
        prev=None
        for fr in frames:
            q=fr[b].copy()
            if prev is not None and q.dot(prev)<0: q.negate()
            if prev is None and q.w<0: q.negate()
            qs.append(q); prev=q
        if all((q-qs[0]).magnitude<1e-6 for q in qs):
            q=qs[0]
            if q.w<0: q.negate()
            ch=f'''        <Item>
         <Type value="StaticQuaternion" />
         <Value x="{q.x:.7f}" y="{q.y:.7f}" z="{q.z:.7f}" w="{q.w:.7f}" />
        </Item>'''
        else:
            ch='\n'.join(chan([getattr(q,c) for q in qs]) for c in 'xyzw')
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
   <Duration value="{DUR[name]:.6f}" />
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
DUR={}
clips=[]; anims=[]
for legs in ('a','b','c'):
    for g,G in GAITS.items():
        name=f'ride_{legs}_{g}'
        n=int(round(G['dur']*30))+1
        frames=[to_local(frame_deltas(g,legs,i/(n-1))) for i in range(n)]
        DUR[name]=G['dur']
        anims.append(anim_xml(name,frames))
        clips.append(f'''  <Item>
   <Hash>{name}</Hash>
   <Name>pack:/{name}.clip</Name>
   <Type value="Animation" />
   <Unknown30 value="0" />
   <Tags />
   <Properties />
   <AnimationHash>{name}_anim</AnimationHash>
   <StartTime value="0" />
   <EndTime value="{G['dur']:.6f}" />
   <Rate value="1" />
  </Item>''')
xml='<?xml version="1.0" encoding="UTF-8"?>\n<ClipDictionary>\n <Clips>\n'+'\n'.join(clips)+'\n </Clips>\n <Animations>\n'+'\n'.join(anims)+'\n </Animations>\n</ClipDictionary>\n'
open(sys.argv[1],'w').write(xml); print('xml ok', len(clips),'clips')
