# Géométrie de la bordure en relief du tsuba Shikkoku
import math
from params import TSUBA_T
TRY,TRZ=0.0410,0.0440          # demi-axes extérieurs du tsuba (Y, Z)
RING_W=0.0028                  # rebord épais du tsuba sur chaque face
HALF=TSUBA_T/2                 # rayon de la tranche arrondie
BAND_W=2*RING_W+math.pi*HALF   # largeur développée de la bande
REPS=4                         # répétitions de la tuile sur le tour
CIRC=2*math.pi*math.sqrt((TRY**2+TRZ**2)/2)
TILE_W=CIRC/REPS
V_APEX=0.5
AMP=0.0013                     # hauteur max du relief or (1,3 mm)
D0=-HALF-RING_W                # décalage du bord intérieur de l'anneau
