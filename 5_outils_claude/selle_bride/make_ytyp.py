import re,glob,sys,os
os.chdir(sys.argv[1]); NAME=sys.argv[2]
items=[]
for f in sorted(glob.glob('edo_bride_k*.ydr.xml')+glob.glob('edo_selle3_k*.ydr.xml')):
    s=open(f).read(3000)
    g=lambda t:[float(v) for v in re.search(r'<%s x="([^"]+)" y="([^"]+)" z="([^"]+)"'%t,s).groups()]
    mn,mx,c=g('BoundingBoxMin'),g('BoundingBoxMax'),g('BoundingSphereCenter'); r=float(re.search(r'<BoundingSphereRadius value="([^"]+)"',s).group(1))
    n=f.split('.')[0]
    items.append(f'''  <Item type="CBaseArchetypeDef">
   <lodDist value="120" />
   <flags value="32" />
   <specialAttribute value="0" />
   <bbMin x="{mn[0]}" y="{mn[1]}" z="{mn[2]}" />
   <bbMax x="{mx[0]}" y="{mx[1]}" z="{mx[2]}" />
   <bsCentre x="{c[0]}" y="{c[1]}" z="{c[2]}" />
   <bsRadius value="{r}" />
   <hdTextureDist value="60" />
   <name>{n}</name>
   <textureDictionary>edo_sellerie</textureDictionary>
   <clipDictionary />
   <drawableDictionary />
   <physicsDictionary />
   <assetType>ASSET_TYPE_DRAWABLE</assetType>
   <assetName>{n}</assetName>
   <extensions />
  </Item>''')
open(NAME+'.ytyp.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<CMapTypes>\n <extensions />\n <archetypes>\n'+'\n'.join(items)+'\n </archetypes>\n <name>'+NAME+'</name>\n <dependencies />\n <compositeEntityTypes />\n</CMapTypes>\n')
print(len(items),'archetypes')
