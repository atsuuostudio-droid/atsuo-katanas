import sys; OUT=sys.argv[1]
exec(open('/home/claude/monte/monte.py').read())
from tools_jenk import jenk
DUR={}
clips=[];anims=[]
for name in CLIPS:
    for side,suf in ((1,'_l'),(-1,'_r')):
        cn=name+suf; dur,frames=build(name,side); DUR[cn]=dur
        anims.append(anim_xml(cn,frames))
        clips.append(f'''  <Item>
   <Hash>{cn}</Hash>
   <Name>pack:/{cn}.clip</Name>
   <Type value="Animation" />
   <Unknown30 value="0" />
   <Tags />
   <Properties />
   <AnimationHash>{cn}_anim</AnimationHash>
   <StartTime value="0" />
   <EndTime value="{dur:.6f}" />
   <Rate value="1" />
  </Item>'''); print(cn,len(frames))
open(OUT,'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<ClipDictionary>\n <Clips>\n'+'\n'.join(clips)+'\n </Clips>\n <Animations>\n'+'\n'.join(anims)+'\n </Animations>\n</ClipDictionary>\n')
print('xml ok')
