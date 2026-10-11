# Outils de fabrication des katanas Atsuo (pour Claude)

Ces scripts ont fabriqué le **Katana Kin** (10/10/2026) : lame Tripo gardée telle quelle,
monture entièrement reconstruite en 3D procédurale + textures générées, conversion Sollumz,
placement en main, brillance/lueur. Les chemins sont codés en dur (`/home/claude/kin/...`) :
recopier dans le même arborescence ou adapter.

## Environnement (conteneur Linux, sans GUI)
- `pip install --break-system-packages bpy==5.2.2` (Blender 5.2 en module Python 3.13 ; l'utilisateur a Blender 5.2.1)
- Sollumz **v2.9.0** : `git clone --depth 1 --branch v2.9.0 https://github.com/Skylumz/Sollumz.git /home/claude/addons/sollumz`
  puis lien `ln -s /home/claude/addons/sollumz ~/.config/blender/5.2/scripts/addons/sollumz`
  et `pip install --break-system-packages "szio==1.3.0.dev9"` ; activer via `addon_utils.enable('sollumz')` (load_sollumz.py)
- Export natif .ydr impossible ici (pymateria = Windows) : on teste en CWXML (test_export.py) ; l'utilisateur exporte en Native/Gen8
- DDS : ImageMagick `convert ... -define dds:compression=dxt1|dxt5 -define dds:mipmaps=8`
- Piège : ne jamais nommer un script `inspect.py` (masque le module standard, plante bpy)

## Pipeline (ordre)
1. `params.py` : dimensions (X le long de l'arme, lame vers -X, Z = dos/courbure ; tsuka x 0.222→0.478, tsuba 0.194, habaki 0.158-0.192), N losanges=9, HA=5/16
2. Textures : `tex_kin.py` (gravure or tuilable), `tex_ito.py` (tresse soie, espace (a,b) ; image retournée verticalement car UV Blender v=0 en bas), `tex_same_tsuba.py` (galuchat + face de tsuba)
3. `build.py` : importe le .glb Tripo, garde les 2 morceaux de lame (min x < -0.4), construit habaki/seppa/tsuba/fuchi/tresse (grille a,b pas 1/16 avec sommet central → bords de losanges propres, parois des fenêtres), âme galuchat, menuki fleurs, kashira ; joint tout → `katana_kin_build.blend`
   - theta(b) = 0.25πb + 0.75·acos(1-2b) : côtés plats → rubans droits vus de côté
4. `render_kin.py` : rendus Cycles de contrôle
5. `make_dds.py` → DDS ; `convert_sollumz.py` (autoconvert → normal_spec, converttodrawable, UV "UVMap 0", Color 1, renommage w_me_<nom>) ; `embed_fix.py` (setallembedded n'intègre que le 1er matériau → forcer embedded sur chaque noeud)
6. Placement : `katana_comme_machette.py` **v3** (dossier 3_scripts_blender). La v2 se trompait sur les lames low-poly (lame de travers ~27°, tranchant en haut).
7. `finitions_lame.py` : reflets (specularIntensityMult 2.5 / falloff 400 / fresnel 0.97) + lueur `normal_spec_emissive.sps` emissiveMultiplier 1.5
8. `icon.py` : icône ox_inventory 256x256 fond transparent
9. Ressource : copier `4_modele_ressource/atsuo_katana_kin_EXEMPLE`, remplacer KIN/kin partout, OrderNumber SlotNavigate (192) et SlotBest (422) par les suivants

## Leçons
- **GTA n'affiche qu'un côté des faces** : Cycles/Blender montre les deux, donc un rendu Cycles ne prouve rien.
  `build.py` appelle `fix_normals.py` (oriente chaque face vers l'extérieur : radial, ou selon X pour les faces planes,
  parois de fenêtres vers le centre de la fenêtre, menuki depuis leur base, lame via recalc + test du côté Y).
  Toujours vérifier avec `render_cull.py` (Workbench + show_backface_culling = comme en jeu) avant de livrer.
  Le 1er Kin livré avait l'âme, la tsuba, le kashira, les menuki, seppa et habaki invisibles en jeu à cause de ça.
- Tripo : objets longs/fins → lame écrasée, ornements grumeleux ; mode texte = résultat absurde. Monture seule recadrée = mieux, mais la reconstruction procédurale est la plus propre.
- Le Kin fait ~29k triangles (ok en jeu).
