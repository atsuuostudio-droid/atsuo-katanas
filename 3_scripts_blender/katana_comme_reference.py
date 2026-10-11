# =====================================================================
#  ATSUO RP - Placement d'un nouveau katana dans la main
#  Copie EXACTEMENT le placement d'un katana deja valide en jeu
#  (ex. le Katana Oni) : meme prise, meme tranchant, meme position.
#
#  Utilisation (Blender 5.x) :
#   1. Ouvre le .blend du NOUVEAU katana (ex. Atsuo_Katana_Kin.blend)
#   2. Onglet "Scripting" > Open > ce fichier
#   3. Clique sur  ▶ (Run Script)  -- rien a modifier, le script
#      cherche tout seul le .blend de ton Katana Oni sur le PC
#   4. Regarde la console : "PLACEMENT OK" = c'est bon, tu peux exporter
# =====================================================================

# ---------------------- REGLAGES ------------------------------------
# Laisse "" : le script cherche tout seul (Oni en priorite, sinon Noir...).
# Sinon tu peux mettre le chemin complet, ex. r"C:\...\Atsuo_Katana_Oni_Aura_v12.blend"
FICHIER_REFERENCE = ""

# Nom de l'objet .model du NOUVEAU katana
NOM_OBJET = "w_me_katana_kin.model"

# Mets True seulement si, en jeu, le tranchant est en haut
INVERSER_TRANCHANT = False
# ---------------------------------------------------------------------

import bpy
import os
import numpy as np
from mathutils import Matrix, Vector


def points_monde(obj):
    """Sommets de l'objet en coordonnees monde (numpy Nx3)."""
    me = obj.data
    co = np.empty(len(me.vertices) * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    M = np.array(obj.matrix_world)
    return co @ M[:3, :3].T + M[:3, 3]


def repere_katana(P):
    """Retourne (centre de la tsuba, axe vers la pointe, direction du dos)."""
    c = P.mean(0)
    # axe general de l'arme
    _, _, vt = np.linalg.svd(P - c, full_matrices=False)
    a = vt[0]
    t = (P - c) @ a
    # la tsuba = tranche la plus large
    nb = 200
    bords = np.linspace(t.min(), t.max(), nb + 1)
    larg = np.zeros(nb)
    for i in range(nb):
        m = (t >= bords[i]) & (t < bords[i + 1])
        if m.sum() < 3:
            continue
        Q = P[m] - np.outer(t[m], a)
        larg[i] = np.linalg.norm(Q.max(0) - Q.min(0))
    i_ts = int(np.argmax(larg))
    t_ts = 0.5 * (bords[i_ts] + bords[i_ts + 1])
    m_ts = (t >= bords[max(0, i_ts - 1)]) & (t < bords[min(nb, i_ts + 2)])
    # cote lame = le cote le plus long
    signe = 1.0 if (t.max() - t_ts) > (t_ts - t.min()) else -1.0
    # axe de la poignee (de la tsuba vers le pommeau)
    poignee = (signe * (t - t_ts)) < -0.01
    if poignee.sum() < 10:
        poignee = (signe * (t - t_ts)) < 0
    H = P[poignee]
    _, _, vh = np.linalg.svd(H - H.mean(0), full_matrices=False)
    u = vh[0]
    if np.dot(u, a * signe) < 0:
        u = -u                      # u pointe vers la pointe
    # centre de la tsuba (sur l'axe de la poignee)
    T = P[m_ts]
    centre_ts = H.mean(0) + u * np.dot(T.mean(0) - H.mean(0), u)
    # pointe = sommet le plus loin de la tsuba
    pointe = P[np.argmax((P - centre_ts) @ u)]
    d = pointe - centre_ts
    dos = d - u * np.dot(d, u)      # la courbure va vers le dos
    if np.linalg.norm(dos) < 1e-6:
        raise RuntimeError("Impossible de trouver la courbure de la lame")
    dos /= np.linalg.norm(dos)
    return centre_ts, u, dos


def matrice(centre, u, dos):
    w = np.cross(u, dos)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = u, dos, w, centre
    return Matrix(M.tolist())


# ---------- 0. trouver le .blend de reference ----------
def chercher_reference():
    actuel = os.path.normcase(os.path.abspath(bpy.data.filepath)) if bpy.data.filepath else ""
    home = os.path.expanduser("~")
    dossiers = []
    if bpy.data.filepath:
        d = os.path.dirname(bpy.data.filepath)
        dossiers += [d, os.path.dirname(d), os.path.dirname(os.path.dirname(d))]
    for n in ("Desktop", "Bureau", "Documents", "Downloads", "Telechargements"):
        dossiers.append(os.path.join(home, n))
    try:
        for n in os.listdir(home):
            if n.lower().startswith("onedrive"):
                for m in ("Desktop", "Bureau", "Documents", ""):
                    dossiers.append(os.path.join(home, n, m))
    except OSError:
        pass
    for lettre in "CDEFG":
        dossiers.append(lettre + ":\\")
    trouves = []
    vus = set()
    for racine in dossiers:
        if not os.path.isdir(racine) or racine in vus:
            continue
        vus.add(racine)
        prof0 = racine.rstrip("\\/").count(os.sep)
        for dp, dns, fns in os.walk(racine):
            if dp.count(os.sep) - prof0 >= (2 if len(racine) <= 3 else 6):
                dns[:] = []
            dns[:] = [x for x in dns if not x.startswith(("$", ".")) and x.lower() not in
                      ("windows", "program files", "program files (x86)", "appdata", "programdata", "node_modules")]
            for f in fns:
                fl = f.lower()
                if fl.endswith(".blend") and "katana" in fl and "kin" not in fl:
                    chemin = os.path.join(dp, f)
                    if os.path.normcase(os.path.abspath(chemin)) != actuel:
                        trouves.append(chemin)
    if not trouves:
        return None
    def score(c):
        n = os.path.basename(c).lower()
        return (0 if "oni" in n else 1 if "noir" in n else 2, -os.path.getmtime(c))
    trouves.sort(key=score)
    return trouves[0]

if not FICHIER_REFERENCE:
    FICHIER_REFERENCE = chercher_reference()
    if not FICHIER_REFERENCE:
        raise RuntimeError("Aucun .blend de katana trouve. Mets le chemin dans FICHIER_REFERENCE.")
print("Fichier de reference :", FICHIER_REFERENCE)

# ---------- 1. katana de reference ----------
with bpy.data.libraries.load(FICHIER_REFERENCE, link=False) as (src, dst):
    candidats = [n for n in src.objects if n.endswith(".model")]
    dst.objects = candidats
refs = [o for o in dst.objects if o is not None and o.type == "MESH"]
if not refs:
    raise RuntimeError("Aucun objet .model trouve dans " + FICHIER_REFERENCE)
ref = max(refs, key=lambda o: len(o.data.vertices))   # le katana (pas les auras)
nom_ref = ref.name
print("Reference :", nom_ref)
c_ref, u_ref, d_ref = repere_katana(points_monde(ref))
for o in refs:
    me = o.data
    bpy.data.objects.remove(o)
    if me.users == 0:
        bpy.data.meshes.remove(me)

# ---------- 2. nouveau katana ----------
obj = bpy.data.objects.get(NOM_OBJET)
if obj is None:
    raise RuntimeError("Objet introuvable : " + NOM_OBJET)
c_new, u_new, d_new = repere_katana(points_monde(obj))
if INVERSER_TRANCHANT:
    d_new = -d_new

# ---------- 3. alignement tsuba sur tsuba ----------
M_map = matrice(c_ref, u_ref, d_ref) @ matrice(c_new, u_new, d_new).inverted()
obj.data.transform(obj.matrix_world.inverted() @ M_map @ obj.matrix_world)
obj.data.update()

# verification
c_chk, u_chk, d_chk = repere_katana(points_monde(obj))
ecart = np.linalg.norm(c_chk - c_ref) * 100
angle = np.degrees(np.arccos(np.clip(np.dot(u_chk, u_ref), -1, 1)))
print(f"Ecart tsuba : {ecart:.2f} cm | ecart axe : {angle:.2f} deg")
if ecart < 0.5 and angle < 1.0:
    print("PLACEMENT OK - meme prise que", nom_ref)
else:
    print("ATTENTION : verifie le placement")
