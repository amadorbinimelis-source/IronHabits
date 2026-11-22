"""Recorta logo.png (fondo blanco) a PNG transparente (logo-a.png) y en sus 4 piezas (logo-p1..4.png) para la pantalla de carga.
Las piezas conservan sus píxeles originales; solo el fondo y la sombra pasan a transparencia (color-to-alpha sobre blanco).
Uso: python gen/cut_logo.py 6"""
import numpy as np, json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
from PIL import Image
from scipy import ndimage as nd
ER=int(sys.argv[1])
src=Image.open(str(ROOT/'logo.png')).convert('RGB')
im=np.asarray(src).astype(np.float32)/255
bg=np.array([254,254,255])/255
d=(255-im*255).max(2)
m=d>25; m=nd.binary_fill_holes(nd.binary_closing(m,iterations=3)); m=nd.binary_opening(m,iterations=2)
core=nd.binary_erosion(m,iterations=ER)
a=np.clip(((bg-im)/bg).max(2),0,1)
a=np.where(core,1.0,a); a[a<0.012]=0
col=np.where(core[...,None],im,np.clip((im-bg*(1-a[...,None]))/np.maximum(a[...,None],1e-4),0,1))
rgba=np.dstack([col,a])
out=Image.fromarray((rgba*255+.5).astype(np.uint8),'RGBA')
lab,n=nd.label(m)
_,(iy,ix)=nd.distance_transform_edt(lab==0,return_indices=True); own=lab[iy,ix]
S=768
out.resize((S,S),Image.LANCZOS).save(str(ROOT/'logo-a.png'),optimize=True)
meta=[]
for k in range(1,n+1):
    r=rgba.copy();r[...,3]*=(own==k)
    pi=Image.fromarray((r*255+.5).astype(np.uint8),'RGBA').resize((S,S),Image.LANCZOS)
    bb=pi.getchannel('A').point(lambda v:255 if v>2 else 0).getbbox()
    pi.crop(bb).save(str(ROOT/f'logo-p{k}.png'),optimize=True); meta.append([round(v/S*100,3) for v in bb])
print(meta)
