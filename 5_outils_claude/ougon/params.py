import math
N=9             # losanges par côté
HA=5/16         # demi-taille fenêtre (unités a/b, K=1)
X_HAB0,X_HAB1=0.158,0.192
X_SEP0=0.192; SEP_T=0.0016
X_TSUBA0=X_SEP0+SEP_T; TSUBA_T=0.0060
X_SEP1=X_TSUBA0+TSUBA_T
X_FUCHI0=X_SEP1+SEP_T; X_FUCHI1=X_FUCHI0+0.020
X_WRAP0=X_FUCHI1; X_KASHI0=0.478; X_WRAP1=X_KASHI0; X_END=0.502
AY,AZ=0.0150,0.0186   # demi-axes extérieurs de la tresse
ITO_T=0.0021          # épaisseur de la tresse
def zc(x): return 0.0545+(x-0.19)*0.021
def _f(b): return 0.25*math.pi*b+0.75*math.acos(max(-1.0,min(1.0,1-2*b)))
def theta(b):
    b=b%2.0
    return _f(b) if b<=1 else 2*math.pi-_f(2-b)
def scale(t): return 1.0-0.055*math.sin(math.pi*t)-0.02*t
