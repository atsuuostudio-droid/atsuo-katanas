# position du pied PROCHE (boule du pied, sous la semelle) a chaque cle de montee, repere entite (avant +Y, gauche -X)
import sys; exec(open('/home/claude/monte/monte.py').read())
from skel import world
dur,keys=CLIPS['mount']
for t,k in keys:
    D=keyD(k,1); full=dict(D)
    W=world(B,to_local(full)); r=W['SKEL_ROOT'].translation
    f=W['SKEL_L_Foot'].translation; to=W['SKEL_L_Toe0'].translation; ball=f.lerp(to,0.6)-r
    print('{ %.2f, %.3f, %.3f, %.3f },'%(t,-ball.x,-ball.y,ball.z-0.05))
