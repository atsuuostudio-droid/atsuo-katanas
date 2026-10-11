import numpy as np, cv2
def normal_from_height(h, strength, wrap=True):
    hp = np.pad(h.astype(np.float32),2,mode='wrap' if wrap else 'reflect')
    hx = cv2.Sobel(hp, cv2.CV_32F, 1, 0, ksize=3)[2:-2,2:-2]/8.0
    hy = cv2.Sobel(hp, cv2.CV_32F, 0, 1, ksize=3)[2:-2,2:-2]/8.0
    nx, ny, nz = -hx*strength, hy*strength, np.ones_like(hx)   # OpenGL-style (green up) for Blender
    l = np.sqrt(nx*nx+ny*ny+nz*nz)
    n = np.stack([nx/l, ny/l, nz/l], -1)
    return ((n*0.5+0.5)*255).clip(0,255).astype(np.uint8)
def save_rgb(path, rgb):  # rgb float 0..1 or uint8, RGB order
    if rgb.dtype != np.uint8: rgb = (np.clip(rgb,0,1)*255+0.5).astype(np.uint8)
    cv2.imwrite(path, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
def save_gray(path, g):
    if g.dtype != np.uint8: g = (np.clip(g,0,1)*255+0.5).astype(np.uint8)
    cv2.imwrite(path, cv2.merge([g,g,g]))
def blur_wrap(x, s):
    if s<=0: return x.astype(np.float32)
    p=int(s*4)+2
    xp=np.pad(x.astype(np.float32),p,mode='wrap')
    return cv2.GaussianBlur(xp,(0,0),s)[p:-p,p:-p]
