# Lame Kumo (procédurale) dans le repère du Kin : X le long de l'arme (lame vers -X), Z = dos
import math
X_BASE=0.192          # départ de la lame (sous la seppa / habaki)
LB=0.670              # longueur de la lame
W0=0.0350             # largeur au habaki (motohaba)
WY=0.0240             # largeur au yokote (sakihaba)
KL=0.050              # longueur du kissaki
Z_BACK0=0.0720        # dos au habaki
SLOPE=0.021           # même pente que le manche (zc)
SORI=0.090            # courbure (z = c*s^2)
TS0,TS1=0.0034,0.0022 # demi-épaisseur au shinogi (base -> pointe)
F_SHIN=0.72           # shinogi à 72 % de la largeur
F_HI0,F_HI1=0.765,0.905   # gorge (bo-hi)
HI_DEPTH=0.45         # profondeur relative de la gorge
def wid(s):           # largeur nominale (sans la courbe du kissaki)
    return W0+(WY-W0)*min(s/(LB-KL),1.0)
def zback(s): return Z_BACK0-SLOPE*s+SORI*s*s
def ts(s): return TS0+(TS1-TS0)*s/LB
def hi_depth(s):      # gorge : pleine jusqu'à 12 cm de la pointe, s'arrête à 7 cm
    a,b=LB-0.12,LB-0.07
    if s<=a: return 1.0
    if s>=b: return 0.0
    t=(s-a)/(b-a); return 1-t*t*(3-2*t)
