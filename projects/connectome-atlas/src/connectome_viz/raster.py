"""Small deterministic raster companion for our own explicit SVG primitives.
No anatomy or connectivity is generated; every shape comes from figure records.
"""
import math,re,xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
FONT=Path('/System/Library/Fonts/Supplemental/Arial.ttf')
def raster_svg(path):
    root=ET.fromstring(path.read_text());w,h=map(int,[root.attrib['width'],root.attrib['height']]);im=Image.new('RGB',(w*2,h*2),'white');d=ImageDraw.Draw(im)
    def visit(e):
        tag=e.tag.split('}')[-1];a=e.attrib
        if tag=='defs':return
        if tag in ('svg','g'):
            for c in e:visit(c)
            return
        def num(k,default=0):return float(a.get(k,default))*2
        fill=a.get('fill');stroke=a.get('stroke');width=max(1,round(float(a.get('stroke-width',1))*2))
        if fill=='none':fill=None
        if tag=='rect':
            if '%' in a.get('width',''):return
            shape=(num('x'),num('y'),num('x')+num('width'),num('y')+num('height'));d.rounded_rectangle(shape,radius=num('rx'),fill=fill,outline=stroke,width=width)
        elif tag=='circle':
            x,y,r=num('cx'),num('cy'),num('r');d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=stroke,width=width)
        elif tag=='text':
            size=int(num('font-size',16));font=ImageFont.truetype(str(FONT),size) if FONT.exists() else ImageFont.load_default(size=size)
            x,y=num('x'),num('y');anchor={'middle':'ms','end':'rs'}.get(a.get('text-anchor'),'ls');d.text((x,y),e.text or '',font=font,fill=fill or '#173b46',anchor=anchor)
        elif tag=='path':
            coords=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',a['d'])));points=[(coords[i]*2,coords[i+1]*2) for i in range(0,len(coords),2)]
            if fill and not stroke:d.polygon(points,fill=fill)
            elif stroke and len(points)>=2:
                if a.get('stroke-dasharray'):
                    for p,q in zip(points,points[1:]):
                        length=math.dist(p,q);steps=max(1,int(length/12))
                        for k in range(0,steps,2):d.line([(p[0]+(q[0]-p[0])*k/steps,p[1]+(q[1]-p[1])*k/steps),(p[0]+(q[0]-p[0])*min(k+1,steps)/steps,p[1]+(q[1]-p[1])*min(k+1,steps)/steps)],fill=stroke,width=width)
                else:d.line(points,fill=stroke,width=width)
                if 'marker-end' in a:
                    p,q=points[-2:];angle=math.atan2(q[1]-p[1],q[0]-p[0]);d.polygon([q,(q[0]-11*math.cos(angle-.4),q[1]-11*math.sin(angle-.4)),(q[0]-11*math.cos(angle+.4),q[1]-11*math.sin(angle+.4))],fill=stroke)
    visit(root);dest=path.with_suffix('.png');im.save(dest);return dest
