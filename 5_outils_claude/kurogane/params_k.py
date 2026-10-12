# Kurogane (ōdachi, grand espadon) : X le long de l'arme (lame vers -X), Z = largeur de lame, Y = épaisseur
XG=0.192        # face de la garde côté lame
GT=0.034        # épaisseur de la garde (le long de X)
GH=0.236        # hauteur de la garde (Z)
GD=0.064        # profondeur de la garde (Y)
LB=1.25         # longueur de lame
W=0.158         # largeur de lame
KT=0.135        # longueur de la pointe
B=0.030         # largeur des biseaux (mesurée en Z)
TC=0.0115       # demi-épaisseur au centre
TE=0.0016       # demi-épaisseur au fil
X_FER0=XG+GT; X_FER1=X_FER0+0.024
X_GRIP0=X_FER1; X_GRIP1=X_GRIP0+0.31
X_POM0=X_GRIP1; X_POM1=X_POM0+0.064
R_GRIP=0.0195
TEXW,TEXH=4096,512
def hw(s):      # demi-largeur à la distance s de la garde
    if s<=LB-KT: return W/2
    return W/2*max(0.0,1-(s-(LB-KT))/KT)
