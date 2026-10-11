# =====================================================================
#  Katana Atsuo : place le katana EXACTEMENT comme la machette GTA
#  (repere + os de prise Gun_GripR mesures sur w_me_machette_lr.ydr)
#  Peut etre relance sans risque : le resultat est toujours le meme.
#  v2 : tranchant oriente vers le bas en jeu (corrige).
#  v3 : calcul du tranchant fiable (lame plus de travers sur les modeles low-poly).
#  Onglet Scripting > Open > ce fichier > Run Script (bouton lecture)
# =====================================================================
import bpy, numpy as np, mathutils

NOM_OBJET = "w_me_katana_XXX.model"   # <-- remplace XXX par le nom de l arme (ex. "w_me_katana_kin.model")
DIST_PRISE_SOUS_TSUBA = 0.11   # metres : centre de la main sous la tsuba (reglage Atsuo)
INVERSER_TRANCHANT = False     # mettre True si le tranchant est en haut en jeu

ob = bpy.data.objects[NOM_OBJET]
me = ob.data
# meme espace que l'export Sollumz : relatif au Drawable parent
root = ob
while root.parent is not None:
    root = root.parent
E = (root.matrix_world.inverted() @ ob.matrix_world) if root is not ob else ob.matrix_world.copy()
L = np.array(E)
V = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", V); V = V.reshape(-1, 3)
Vd = V @ L[:3, :3].T + L[:3, 3]          # sommets tels qu'exportes

# --- axe principal + position de la tsuba (section la plus large) ---
c = Vd.mean(0)
a = np.linalg.svd(Vd - c, full_matrices=False)[2][0]
t = (Vd - c) @ a
bins = np.linspace(t.min(), t.max(), 121); w = np.zeros(120)
for i in range(120):
    s = (t >= bins[i]) & (t < bins[i + 1])
    if s.sum() >= 3:
        Q = Vd[s] - c; Q = Q - np.outer(Q @ a, a); w[i] = np.ptp(Q, axis=0).max()
k = int(np.argmax(w)); ts = (bins[k] + bins[k + 1]) / 2
if (t.max() - ts) < (ts - t.min()):          # la lame est le cote le plus long
    a, t, ts = -a, -t, -ts
blade = Vd[t > ts + 0.03]; handle = Vd[t < ts - 0.02]

# --- axe exact du manche (centre des sections) ---
th = (handle - c) @ a; pts = []
for qv in np.linspace(th.min() + 0.01, th.max() - 0.01, 12):
    s = np.abs(th - qv) < 0.01
    if s.sum() > 5: pts.append(handle[s].mean(0))
pts = np.array(pts); hm = pts.mean(0)
b = np.linalg.svd(pts - hm)[2][0]
if b @ a < 0: b = -b

# --- cote du tranchant (v3 : plan reel de la lame, fiable meme sur lame low-poly) ---
# plan de la lame = les 2 grandes directions de ses sommets ; sa normale = epaisseur
n_lame = np.linalg.svd(blade - blade.mean(0), full_matrices=False)[2][2]
e = np.cross(n_lame, b); e /= np.linalg.norm(e)      # dans le plan de la lame, perpendiculaire au manche
tsb = hm + b * ((c + a * ts - hm) @ b)
pointe = blade[np.argmax((blade - tsb) @ b)]
if (pointe - tsb) @ e > 0:                            # la pointe remonte vers le dos...
    e = -e                                            # ...donc le tranchant est de l'autre cote

# --- point de prise sur l'axe du manche ---
tsuba = hm + b * ((c + a * ts - hm) @ b)
grip = tsuba - b * DIST_PRISE_SOUS_TSUBA

# --- nouveau repere : Z = lame, tranchant vers +X (= vers le bas en jeu) ---
X = -e if INVERSER_TRANCHANT else e; Z = b; Y = np.cross(Z, X); Y /= np.linalg.norm(Y); X = np.cross(Y, Z)
R = np.stack([X, Y, Z])                        # lignes = nouveaux axes
M = np.eye(4); M[:3, :3] = R; M[:3, 3] = -R @ grip

# --- os de prise de la machette (Gun_GripR, lu dans w_me_machette_lr.ydr) ---
# GTA place la main sur cet os ; notre katana n'a pas de squelette,
# donc on integre directement son inverse dans la geometrie.
GRIP_INV = np.array([
    [ 0.976847, -0.103742,  0.187105,  0.042457],
    [-0.158994,  0.233149,  0.959355, -0.019481],
    [-0.143148, -0.966892,  0.211256, -0.007166],
    [ 0.0,       0.0,       0.0,       1.0     ]])
M = GRIP_INV @ M

T = np.linalg.inv(L) @ M @ L                   # retour en coordonnees locales du mesh
me.transform(mathutils.Matrix(T.tolist())); me.update()
print("Katana cale comme la machette. Sauvegarde (Ctrl+S) puis reexporte.")
