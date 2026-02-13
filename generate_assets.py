"""
Generate all 18 game assets for Darkwing Duck using Pillow.
Creates stylized, atmospheric pixel/painted art.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import random
import math
import os

OUT = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(OUT, exist_ok=True)

random.seed(42)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def draw_stars(draw, w, h, count=80, seed=42):
    rng = random.Random(seed)
    for _ in range(count):
        x, y = rng.randint(0,w), rng.randint(0, h//2)
        b = rng.randint(150, 255)
        s = rng.choice([1,1,1,2])
        draw.ellipse([x,y,x+s,y+s], fill=(b,b,b+min(255-b,30)))

def gradient_rect(draw, x, y, w, h, top_color, bot_color):
    for row in range(h):
        t = row / max(h-1, 1)
        c = lerp_color(top_color, bot_color, t)
        draw.line([(x, y+row), (x+w, y+row)], fill=c)

def draw_building(draw, x, y, w, h, color, window_color, rng):
    draw.rectangle([x, y, x+w, y+h], fill=color)
    # Windows
    for wy in range(y+8, y+h-8, 14):
        for wx in range(x+5, x+w-5, 10):
            if rng.random() > 0.3:
                draw.rectangle([wx, wy, wx+5, wy+7], fill=window_color)

def draw_moon(draw, cx, cy, r, glow_r=None):
    if glow_r:
        for gr in range(glow_r, r, -1):
            a = int(40 * (1 - (gr-r)/(glow_r-r)))
            draw.ellipse([cx-gr, cy-gr, cx+gr, cy+gr], fill=(200, 200, 255, a))
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(240, 235, 200))
    # Craters
    draw.ellipse([cx-r//3, cy-r//4, cx-r//3+r//4, cy-r//4+r//4], fill=(220, 215, 185))
    draw.ellipse([cx+r//5, cy+r//6, cx+r//5+r//5, cy+r//6+r//5], fill=(225, 220, 190))

def make_cityscape(w, h, sky_top, sky_bot, building_colors, window_color, has_moon=True, has_stars=True):
    img = Image.new("RGBA", (w, h))
    draw = ImageDraw.Draw(img)
    gradient_rect(draw, 0, 0, w, h, sky_top, sky_bot)
    if has_stars:
        draw_stars(draw, w, h)
    if has_moon:
        draw_moon(draw, w*3//4, h//6, 35)
    rng = random.Random(123)
    # Far buildings
    for i in range(0, w, 60):
        bh = rng.randint(80, 200)
        bc = lerp_color(building_colors[0], (0,0,0), 0.6)
        draw.rectangle([i, h-bh, i+55, h], fill=bc)
    # Near buildings
    for i in range(0, w, 70):
        bh = rng.randint(100, 280)
        bc = building_colors[rng.randint(0, len(building_colors)-1)]
        draw_building(draw, i, h-bh, 60, bh, bc, window_color, rng)
    return img

# ===== BACKGROUNDS =====

def gen_titleBg():
    img = make_cityscape(1024, 576, (12, 8, 40), (30, 15, 60),
        [(25,20,50),(30,25,60),(20,15,45)], (255,220,100,180))
    # Purple glow from below
    glow = Image.new("RGBA", (1024,576), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for y in range(450, 576):
        t = (y-450)/126
        a = int(60*t)
        gd.line([(0,y),(1024,y)], fill=(123,47,247,a))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    img = img.convert("RGB")
    img = img.filter(ImageFilter.GaussianBlur(1))
    img.save(os.path.join(OUT, "titleBg.png"))
    print("✓ titleBg")

def gen_bgRooftops():
    img = make_cityscape(1024, 576, (10, 10, 42), (25, 20, 55),
        [(35,30,65),(40,35,75),(28,22,52)], (255,220,80,150))
    draw = ImageDraw.Draw(img)
    # Rooftop platforms in foreground
    for x in range(0, 1024, 150):
        rng = random.Random(x)
        ry = 350 + rng.randint(0, 120)
        rw = rng.randint(80, 140)
        draw.rectangle([x, ry, x+rw, ry+15], fill=(55,55,90))
        draw.rectangle([x, ry, x+rw, ry+3], fill=(80,80,130))
    img.save(os.path.join(OUT, "bgRooftops.png"))
    print("✓ bgRooftops")

def gen_bgFunhouse():
    img = Image.new("RGB", (1024, 576))
    draw = ImageDraw.Draw(img)
    # Colorful striped background
    colors = [(180,40,100),(200,80,40),(180,160,40),(40,160,80),(40,80,180),(120,40,180)]
    stripe_w = 80
    for i in range(0, 1024+200, stripe_w):
        c = colors[i//stripe_w % len(colors)]
        # Angled stripes
        pts = [(i-100,0),(i+stripe_w-100,0),(i+stripe_w-200,576),(i-200,576)]
        draw.polygon(pts, fill=c)
    # Darken
    overlay = Image.new("RGBA", (1024,576), (40,10,45,140))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)
    # Balloons
    rng = random.Random(77)
    for _ in range(15):
        bx, by = rng.randint(50,974), rng.randint(30, 250)
        bc = (rng.randint(180,255), rng.randint(50,200), rng.randint(100,255))
        draw.ellipse([bx-12,by-15,bx+12,by+15], fill=bc)
        draw.line([(bx,by+15),(bx+rng.randint(-5,5),by+50)], fill=(200,200,200), width=1)
    # Checkered floor
    for x in range(0, 1024, 40):
        for y in range(480, 576, 40):
            c = (60,30,60) if (x//40+y//40)%2==0 else (40,20,40)
            draw.rectangle([x,y,x+40,y+40], fill=c)
    img.save(os.path.join(OUT, "bgFunhouse.png"))
    print("✓ bgFunhouse")

def gen_bgGreenhouse():
    img = Image.new("RGB", (1024, 576))
    draw = ImageDraw.Draw(img)
    gradient_rect(draw, 0, 0, 1024, 576, (15, 50, 15), (10, 35, 10))
    # Glass ceiling structure
    for x in range(0, 1024, 120):
        draw.line([(x, 0), (x+60, 100)], fill=(60,100,60), width=3)
        draw.line([(x+120, 0), (x+60, 100)], fill=(60,100,60), width=3)
    for y in range(0, 120, 30):
        draw.line([(0,y),(1024,y)], fill=(50,90,50), width=2)
    # Light beams
    for i in range(5):
        bx = 100 + i*200
        pts = [(bx, 0), (bx+30, 0), (bx+60, 576), (bx-30, 576)]
        beam = Image.new("RGBA", (1024,576), (0,0,0,0))
        bd = ImageDraw.Draw(beam)
        bd.polygon(pts, fill=(100,200,100,25))
        img = Image.alpha_composite(img.convert("RGBA"), beam)
    draw = ImageDraw.Draw(img)
    # Vines and plants
    rng = random.Random(55)
    for x in range(0, 1024, 50):
        vine_h = rng.randint(80, 300)
        draw.line([(x, 0), (x + rng.randint(-20,20), vine_h)], fill=(30,80,30), width=rng.randint(2,4))
        for ly in range(20, vine_h, 25):
            lx = x + rng.randint(-15, 15)
            draw.ellipse([lx-8, ly-4, lx+8, ly+4], fill=(40,100+rng.randint(0,50),30))
    # Ground plants
    for x in range(0, 1024, 30):
        ph = rng.randint(20, 80)
        draw.polygon([(x,576),(x+8,576-ph),(x+16,576)], fill=(30,80+rng.randint(0,40),25))
    img.save(os.path.join(OUT, "bgGreenhouse.png"))
    print("✓ bgGreenhouse")

def gen_bgDam():
    img = Image.new("RGB", (1024, 576))
    draw = ImageDraw.Draw(img)
    gradient_rect(draw, 0, 0, 1024, 576, (10, 25, 55), (15, 35, 75))
    # Dam wall structure
    draw.rectangle([0, 200, 1024, 576], fill=(50, 60, 80))
    # Metal panels
    for x in range(0, 1024, 80):
        draw.rectangle([x+2, 202, x+78, 574], fill=(55, 65, 85))
        draw.line([(x, 200), (x, 576)], fill=(40, 50, 70), width=3)
    # Horizontal lines
    for y in range(200, 576, 60):
        draw.line([(0,y),(1024,y)], fill=(45, 55, 75), width=2)
    # Rivets
    for x in range(20, 1024, 80):
        for y in range(220, 576, 60):
            draw.ellipse([x-3,y-3,x+3,y+3], fill=(65,75,95))
    # Water at bottom
    for y in range(480, 576):
        t = (y-480)/96
        c = lerp_color((30,80,160), (20,50,120), t)
        draw.line([(0,y),(1024,y)], fill=c)
    # Water ripples
    rng = random.Random(33)
    for _ in range(40):
        rx, ry = rng.randint(0,1024), rng.randint(485,570)
        rw = rng.randint(15,40)
        draw.arc([rx,ry,rx+rw,ry+6], 0, 180, fill=(80,150,220), width=1)
    # Pipes
    for py in [250, 350, 450]:
        draw.rectangle([0, py, 1024, py+12], fill=(70,80,100))
        draw.rectangle([0, py, 1024, py+3], fill=(90,100,120))
    img.save(os.path.join(OUT, "bgDam.png"))
    print("✓ bgDam")

def gen_bgFortress():
    img = Image.new("RGB", (1024, 576))
    draw = ImageDraw.Draw(img)
    gradient_rect(draw, 0, 0, 1024, 576, (25, 8, 8), (50, 18, 18))
    # Stone walls
    rng = random.Random(66)
    for y in range(0, 576, 35):
        offset = 20 if (y//35)%2 else 0
        for x in range(-20+offset, 1024, 65):
            c = rng.randint(35,55)
            draw.rectangle([x,y,x+60,y+30], fill=(c+10, c-5, c-5))
            draw.rectangle([x,y,x+60,y+30], outline=(c-10,c-15,c-15), width=1)
    # Torches
    for tx in [150, 400, 650, 900]:
        # Bracket
        draw.rectangle([tx-3, 180, tx+3, 230], fill=(80,60,30))
        draw.rectangle([tx-8, 175, tx+8, 185], fill=(90,70,35))
        # Flame
        for fr in range(25, 3, -2):
            fa = int(255 * (1 - fr/25))
            fc = lerp_color((255,60,0), (255,200,50), 1-fr/25)
            draw.ellipse([tx-fr//2, 150-fr, tx+fr//2, 155], fill=fc)
        # Glow
        glow = Image.new("RGBA", (1024,576), (0,0,0,0))
        gd = ImageDraw.Draw(glow)
        for gr in range(80, 5, -5):
            a = int(20*(1-gr/80))
            gd.ellipse([tx-gr, 155-gr, tx+gr, 155+gr], fill=(255,100,20,a))
        img = Image.alpha_composite(img.convert("RGBA"), glow)
        draw = ImageDraw.Draw(img)
    # Chains
    for cx in [250, 550, 800]:
        for cy in range(0, 400, 15):
            draw.ellipse([cx-3,cy,cx+3,cy+12], outline=(100,100,110), width=2)
    # Red glow from floor
    glow = Image.new("RGBA", (1024,576), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for y in range(500, 576):
        t = (y-500)/76
        a = int(50*t)
        gd.line([(0,y),(1024,y)], fill=(255,30,0,a))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    img = img.convert("RGB")
    img.save(os.path.join(OUT, "bgFortress.png"))
    print("✓ bgFortress")

# ===== PORTRAITS =====

def draw_circle_bg(draw, w, h, color, accent):
    gradient_rect(draw, 0, 0, w, h, color, lerp_color(color, (0,0,0), 0.4))
    # Radial highlight
    cx, cy = w//2, h//2
    for r in range(min(w,h)//2, 10, -3):
        a = int(30 * (1 - r/(min(w,h)//2)))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*accent, a))

def gen_portraitDarkwing():
    img = Image.new("RGBA", (256, 256))
    draw = ImageDraw.Draw(img)
    draw_circle_bg(draw, 256, 256, (50, 20, 80), (123, 47, 247))
    cx, cy = 128, 140
    # Cape
    draw.polygon([(cx-50,cy-20),(cx-80,cy+90),(cx+80,cy+90),(cx+50,cy-20)], fill=(100,30,160))
    # Body
    draw.rounded_rectangle([cx-30, cy-10, cx+30, cy+60], radius=8, fill=(123, 47, 247))
    # Head
    draw.ellipse([cx-35, cy-70, cx+35, cy-10], fill=(245, 222, 179))
    # Hat brim
    draw.ellipse([cx-45, cy-58, cx+45, cy-38], fill=(123, 47, 247))
    # Hat top
    draw.rounded_rectangle([cx-18, cy-85, cx+18, cy-50], radius=5, fill=(123, 47, 247))
    # Mask
    draw.rectangle([cx-38, cy-52, cx+38, cy-38], fill=(123, 47, 247))
    # Eyes
    draw.ellipse([cx-18, cy-52, cx-6, cy-38], fill="white")
    draw.ellipse([cx+6, cy-52, cx+18, cy-38], fill="white")
    draw.ellipse([cx-14, cy-48, cx-8, cy-40], fill="black")
    draw.ellipse([cx+10, cy-48, cx+16, cy-40], fill="black")
    # Bill
    draw.ellipse([cx-20, cy-35, cx+25, cy-20], fill=(244, 164, 96))
    # Gas gun
    draw.rectangle([cx+30, cy+5, cx+65, cy+15], fill=(140,140,140))
    draw.rectangle([cx+60, cy, cx+70, cy+20], fill=(170,170,170))
    # Confident smirk on bill
    draw.arc([cx-8, cy-30, cx+15, cy-22], 0, 180, fill=(200,130,70), width=2)
    img.save(os.path.join(OUT, "portraitDarkwing.png"))
    print("✓ portraitDarkwing")

def gen_villain_portrait(name, size, bg_color, accent, draw_fn):
    img = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(img)
    draw_circle_bg(draw, size, size, bg_color, accent)
    draw_fn(draw, size//2, int(size*0.55), size)
    img.save(os.path.join(OUT, f"portrait{name}.png"))
    print(f"✓ portrait{name}")

def draw_megavolt(draw, cx, cy, s):
    # Body - yellow jumpsuit
    draw.rounded_rectangle([cx-30,cy-10,cx+30,cy+55], radius=6, fill=(255,220,0))
    # Battery pack
    draw.rectangle([cx-35,cy-5,cx-25,cy+40], fill=(130,130,140))
    draw.rectangle([cx+25,cy-5,cx+35,cy+40], fill=(130,130,140))
    # Head
    draw.ellipse([cx-30,cy-65,cx+30,cy-10], fill=(245,222,179))
    # Goggles
    draw.ellipse([cx-25,cy-55,cx-5,cy-35], fill=(255,50,50))
    draw.ellipse([cx+5,cy-55,cx+25,cy-35], fill=(255,50,50))
    draw.rectangle([cx-5,cy-50,cx+5,cy-40], fill=(100,100,110))
    # Lightning bolts
    pts = [(cx-45,cy-80),(cx-30,cy-55),(cx-38,cy-55),(cx-20,cy-30)]
    draw.line(pts, fill=(255,255,0), width=3)
    pts2 = [(cx+45,cy-80),(cx+30,cy-55),(cx+38,cy-55),(cx+20,cy-30)]
    draw.line(pts2, fill=(255,255,0), width=3)
    # Legs
    draw.rectangle([cx-18,cy+50,cx-8,cy+75], fill=(220,190,0))
    draw.rectangle([cx+8,cy+50,cx+18,cy+75], fill=(220,190,0))

def draw_quackerjack(draw, cx, cy, s):
    # Body
    draw.rounded_rectangle([cx-28,cy-10,cx+28,cy+50], radius=6, fill=(255,68,170))
    # Buttons
    for by in range(cy, cy+45, 15):
        draw.ellipse([cx-4,by,cx+4,by+8], fill=(255,170,0))
    # Head
    draw.ellipse([cx-28,cy-65,cx+28,cy-12], fill=(245,222,179))
    # Jester hat
    draw.polygon([(cx-30,cy-55),(cx-50,cy-100),(cx-10,cy-60)], fill=(255,68,170))
    draw.polygon([(cx+30,cy-55),(cx+50,cy-100),(cx+10,cy-60)], fill=(255,170,0))
    draw.ellipse([cx-55,cy-108,cx-43,cy-93], fill=(255,238,0))
    draw.ellipse([cx+43,cy-108,cx+55,cy-93], fill=(255,238,0))
    # Crazy eyes
    draw.ellipse([cx-18,cy-50,cx-4,cy-32], fill="white")
    draw.ellipse([cx+4,cy-50,cx+18,cy-32], fill="white")
    draw.ellipse([cx-14,cy-44,cx-6,cy-36], fill="black")
    draw.ellipse([cx+8,cy-44,cx+16,cy-36], fill="black")
    # Wide grin
    draw.arc([cx-15,cy-30,cx+18,cy-15], 0, 180, fill=(200,100,50), width=3)
    # Bill
    draw.ellipse([cx-15,cy-30,cx+20,cy-18], fill=(244,164,96))

def draw_bushroot(draw, cx, cy, s):
    # Body - plant-like
    draw.polygon([(cx-25,cy+60),(cx+25,cy+60),(cx+20,cy-15),(cx+10,cy-40),(cx,cy-45),(cx-10,cy-40),(cx-20,cy-15)], fill=(50,135,50))
    # Leaves on head
    for angle in [-60,-30,0,30,60]:
        lx = cx + int(30*math.cos(math.radians(angle-90)))
        ly = cy - 50 + int(20*math.sin(math.radians(angle-90)))
        draw.ellipse([lx-15,ly-8,lx+15,ly+8], fill=(68,170,68))
    # Face
    draw.ellipse([cx-22,cy-50,cx+22,cy-10], fill=(60,150,60))
    # Eyes - red
    draw.ellipse([cx-14,cy-40,cx-4,cy-28], fill=(255,60,60))
    draw.ellipse([cx+4,cy-40,cx+14,cy-28], fill=(255,60,60))
    draw.ellipse([cx-11,cy-36,cx-7,cy-30], fill=(180,0,0))
    draw.ellipse([cx+7,cy-36,cx+11,cy-30], fill=(180,0,0))
    # Roots at bottom
    for rx in range(-25,26,10):
        draw.line([(cx+rx,cy+60),(cx+rx+random.randint(-8,8),cy+80)], fill=(80,60,30), width=3)

def draw_liquidator(draw, cx, cy, s):
    # Watery body - translucent blue
    body_color = (68, 170, 255)
    # Body shape - wavy
    pts = []
    for i in range(0, 50):
        x = cx - 25 + int(5*math.sin(i*0.3))
        pts.append((x, cy-10+i))
    for i in range(50, 0, -1):
        x = cx + 25 + int(5*math.sin(i*0.3+1))
        pts.append((x, cy-10+i))
    draw.polygon(pts, fill=body_color)
    # Head
    draw.ellipse([cx-25,cy-60,cx+25,cy-12], fill=(80,180,255))
    # Eyes
    draw.ellipse([cx-15,cy-48,cx-5,cy-32], fill="white")
    draw.ellipse([cx+5,cy-48,cx+15,cy-32], fill="white")
    draw.ellipse([cx-12,cy-43,cx-7,cy-35], fill=(0,50,100))
    draw.ellipse([cx+8,cy-43,cx+13,cy-35], fill=(0,50,100))
    # Sinister smile
    draw.arc([cx-15,cy-28,cx+15,cy-15], 0, 180, fill=(0,80,150), width=2)
    # Water drips
    for dx in [-20, -5, 15, 25]:
        dy = random.randint(40, 70)
        draw.ellipse([cx+dx-2,cy+dy,cx+dx+2,cy+dy+8], fill=(100,190,255))

def draw_negaduck(draw, cx, cy, s):
    # Red cape
    draw.polygon([(cx-45,cy-15),(cx-55,cy+80),(cx+55,cy+80),(cx+45,cy-15)], fill=(140,0,0))
    # Body - red/yellow
    draw.rounded_rectangle([cx-28,cy-8,cx+28,cy+50], radius=6, fill=(200,30,30))
    draw.rectangle([cx-28,cy-8,cx+28,cy+5], fill=(255,200,0))
    # Head
    draw.ellipse([cx-30,cy-65,cx+30,cy-10], fill=(245,222,179))
    # Red hat brim
    draw.ellipse([cx-40,cy-55,cx+40,cy-35], fill=(200,30,30))
    # Hat top
    draw.rounded_rectangle([cx-15,cy-82,cx+15,cy-48], radius=4, fill=(200,30,30))
    # Mask
    draw.rectangle([cx-33,cy-50,cx+33,cy-38], fill=(200,30,30))
    # Angry eyes
    draw.ellipse([cx-18,cy-50,cx-6,cy-38], fill="white")
    draw.ellipse([cx+6,cy-50,cx+18,cy-38], fill="white")
    draw.ellipse([cx-14,cy-47,cx-8,cy-40], fill=(255,0,0))
    draw.ellipse([cx+10,cy-47,cx+16,cy-40], fill=(255,0,0))
    # Angry eyebrows
    draw.line([(cx-20,cy-55),(cx-5,cy-50)], fill=(100,20,20), width=3)
    draw.line([(cx+20,cy-55),(cx+5,cy-50)], fill=(100,20,20), width=3)
    # Bill with snarl
    draw.ellipse([cx-18,cy-35,cx+22,cy-20], fill=(244,164,96))
    draw.line([(cx-10,cy-22),(cx+12,cy-22)], fill=(180,100,50), width=2)
    # Chainsaw
    draw.rectangle([cx+30,cy+5,cx+70,cy+15], fill=(140,140,140))
    draw.polygon([(cx+65,cy),(cx+85,cy+10),(cx+65,cy+20)], fill=(200,200,200))
    # Teeth on chainsaw
    for tx in range(cx+32, cx+68, 6):
        draw.polygon([(tx,cy+2),(tx+3,cy-3),(tx+6,cy+2)], fill=(200,200,200))

# ===== ALLY PORTRAITS (128x128) =====

def gen_portraitLaunchpad():
    img = Image.new("RGBA", (128,128))
    draw = ImageDraw.Draw(img)
    draw_circle_bg(draw, 128, 128, (60,30,15), (255,100,50))
    cx, cy = 64, 72
    # Body - brown jacket
    draw.rounded_rectangle([cx-22,cy-5,cx+22,cy+35], radius=5, fill=(140,90,40))
    # Head - big
    draw.ellipse([cx-25,cy-50,cx+25,cy-5], fill=(245,222,179))
    # Pilot cap
    draw.ellipse([cx-22,cy-48,cx+22,cy-28], fill=(120,75,30))
    draw.rectangle([cx-18,cy-48,cx+18,cy-38], fill=(120,75,30))
    # Goggles on cap
    draw.ellipse([cx-12,cy-42,cx-2,cy-32], fill=(180,200,220))
    draw.ellipse([cx+2,cy-42,cx+12,cy-32], fill=(180,200,220))
    # Big friendly eyes
    draw.ellipse([cx-15,cy-32,cx-5,cy-20], fill="white")
    draw.ellipse([cx+5,cy-32,cx+15,cy-20], fill="white")
    draw.ellipse([cx-12,cy-28,cx-7,cy-22], fill="black")
    draw.ellipse([cx+8,cy-28,cx+13,cy-22], fill="black")
    # Big bill with goofy grin
    draw.ellipse([cx-15,cy-20,cx+18,cy-6], fill=(244,164,96))
    draw.arc([cx-10,cy-14,cx+12,cy-4], 0, 180, fill=(200,130,70), width=2)
    img.save(os.path.join(OUT, "portraitLaunchpad.png"))
    print("✓ portraitLaunchpad")

def gen_portraitGosalyn():
    img = Image.new("RGBA", (128,128))
    draw = ImageDraw.Draw(img)
    draw_circle_bg(draw, 128, 128, (50,20,60), (200,50,150))
    cx, cy = 64, 72
    # Body - purple
    draw.rounded_rectangle([cx-18,cy-5,cx+18,cy+30], radius=4, fill=(140,50,160))
    # Head
    draw.ellipse([cx-22,cy-48,cx+22,cy-8], fill=(245,222,179))
    # Red hair - wild
    draw.ellipse([cx-25,cy-55,cx+25,cy-20], fill=(220,50,30))
    draw.ellipse([cx-28,cy-45,cx-10,cy-25], fill=(220,50,30))
    draw.ellipse([cx+10,cy-45,cx+28,cy-25], fill=(220,50,30))
    # Ponytail
    draw.polygon([(cx+15,cy-40),(cx+35,cy-55),(cx+30,cy-35)], fill=(220,50,30))
    # Eyes - bright, energetic
    draw.ellipse([cx-14,cy-35,cx-4,cy-22], fill="white")
    draw.ellipse([cx+4,cy-35,cx+14,cy-22], fill="white")
    draw.ellipse([cx-11,cy-31,cx-6,cy-25], fill=(0,150,0))
    draw.ellipse([cx+7,cy-31,cx+12,cy-25], fill=(0,150,0))
    # Bill - small
    draw.ellipse([cx-10,cy-22,cx+12,cy-12], fill=(244,164,96))
    # Determined expression
    draw.arc([cx-6,cy-16,cx+8,cy-10], 0, 180, fill=(200,130,70), width=2)
    img.save(os.path.join(OUT, "portraitGosalyn.png"))
    print("✓ portraitGosalyn")

def gen_portraitMorgana():
    img = Image.new("RGBA", (128,128))
    draw = ImageDraw.Draw(img)
    draw_circle_bg(draw, 128, 128, (40,15,50), (180,60,255))
    cx, cy = 64, 72
    # Dark elegant dress
    draw.polygon([(cx-25,cy),(cx-35,cy+45),(cx+35,cy+45),(cx+25,cy)], fill=(60,20,80))
    # Body
    draw.rounded_rectangle([cx-18,cy-8,cx+18,cy+20], radius=4, fill=(80,30,100))
    # Head
    draw.ellipse([cx-20,cy-48,cx+20,cy-10], fill=(240,218,175))
    # Dark hair - flowing
    draw.ellipse([cx-24,cy-55,cx+24,cy-25], fill=(30,0,50))
    draw.polygon([(cx-24,cy-35),(cx-30,cy+10),(cx-18,cy-20)], fill=(30,0,50))
    draw.polygon([(cx+24,cy-35),(cx+30,cy+10),(cx+18,cy-20)], fill=(30,0,50))
    # Mysterious eyes
    draw.ellipse([cx-14,cy-38,cx-4,cy-26], fill=(200,150,255))
    draw.ellipse([cx+4,cy-38,cx+14,cy-26], fill=(200,150,255))
    draw.ellipse([cx-10,cy-34,cx-7,cy-29], fill=(100,0,180))
    draw.ellipse([cx+7,cy-34,cx+10,cy-29], fill=(100,0,180))
    # Magical aura particles
    for i in range(8):
        ax = cx + int(30*math.cos(i*math.pi/4))
        ay = cy - 20 + int(25*math.sin(i*math.pi/4))
        draw.ellipse([ax-2,ay-2,ax+2,ay+2], fill=(180,100,255))
    img.save(os.path.join(OUT, "portraitMorgana.png"))
    print("✓ portraitMorgana")

def gen_portraitGizmoduck():
    img = Image.new("RGBA", (128,128))
    draw = ImageDraw.Draw(img)
    draw_circle_bg(draw, 128, 128, (30,40,60), (100,150,220))
    cx, cy = 64, 72
    # Armor body - rounded
    draw.rounded_rectangle([cx-25,cy-10,cx+25,cy+30], radius=10, fill=(180,190,200))
    draw.rounded_rectangle([cx-22,cy-7,cx+22,cy+27], radius=8, fill=(200,210,220))
    # Wheel base
    draw.ellipse([cx-15,cy+25,cx+15,cy+48], fill=(100,110,120))
    draw.ellipse([cx-12,cy+28,cx+12,cy+45], fill=(140,150,160))
    # Head dome
    draw.ellipse([cx-20,cy-45,cx+20,cy-8], fill=(190,200,210))
    # Visor
    draw.rounded_rectangle([cx-16,cy-35,cx+16,cy-18], radius=4, fill=(60,60,70))
    # Eyes in visor
    draw.ellipse([cx-12,cy-32,cx-4,cy-22], fill=(100,200,255))
    draw.ellipse([cx+4,cy-32,cx+12,cy-22], fill=(100,200,255))
    # Arm cannons
    draw.rounded_rectangle([cx-38,cy-5,cx-22,cy+15], radius=3, fill=(160,170,180))
    draw.rounded_rectangle([cx+22,cy-5,cx+38,cy+15], radius=3, fill=(160,170,180))
    img.save(os.path.join(OUT, "portraitGizmoduck.png"))
    print("✓ portraitGizmoduck")

# ===== GAME OVER / VICTORY =====

def gen_gameOver():
    img = Image.new("RGB", (800, 450))
    draw = ImageDraw.Draw(img)
    gradient_rect(draw, 0, 0, 800, 450, (20, 5, 10), (40, 10, 20))
    # Rain
    rng = random.Random(99)
    for _ in range(200):
        rx, ry = rng.randint(0,800), rng.randint(0,450)
        rl = rng.randint(5,15)
        draw.line([(rx,ry),(rx-2,ry+rl)], fill=(60,60,80), width=1)
    # City silhouette
    for i in range(0, 800, 50):
        bh = rng.randint(60,180)
        draw.rectangle([i, 450-bh, i+45, 450], fill=(15,5,10))
    # Defeated hero silhouette
    cx, cy = 400, 320
    draw.ellipse([cx-20,cy-50,cx+20,cy-15], fill=(10,3,5))  # head
    draw.rectangle([cx-25,cy-20,cx+25,cy+30], fill=(10,3,5))  # body
    # Kneeling pose
    draw.rectangle([cx-30,cy+25,cx-10,cy+55], fill=(10,3,5))  # leg
    draw.rectangle([cx+5,cy+15,cx+35,cy+55], fill=(10,3,5))  # leg
    # Purple tint
    overlay = Image.new("RGBA", (800,450), (80,20,40,40))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    img.save(os.path.join(OUT, "gameOver.png"))
    print("✓ gameOver")

def gen_victory():
    img = Image.new("RGB", (800, 450))
    draw = ImageDraw.Draw(img)
    gradient_rect(draw, 0, 0, 800, 450, (10, 10, 40), (20, 15, 50))
    # City
    rng = random.Random(88)
    for i in range(0, 800, 55):
        bh = rng.randint(80,200)
        c = rng.randint(20,40)
        draw_building(draw, i, 450-bh, 50, bh, (c,c,c+15), (255,220,80,120), rng)
    # Fireworks
    fw_colors = [(255,50,50),(50,255,50),(50,50,255),(255,255,50),(255,50,255),(50,255,255)]
    for i in range(8):
        fx, fy = rng.randint(50,750), rng.randint(30,200)
        fc = fw_colors[i%len(fw_colors)]
        for j in range(20):
            angle = j * math.pi * 2 / 20
            r = rng.randint(15,50)
            ex = fx + int(r*math.cos(angle))
            ey = fy + int(r*math.sin(angle))
            draw.line([(fx,fy),(ex,ey)], fill=fc, width=2)
            draw.ellipse([ex-2,ey-2,ex+2,ey+2], fill=(255,255,200))
    # Golden glow
    overlay = Image.new("RGBA", (800,450), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    for r in range(200, 10, -5):
        a = int(15*(1-r/200))
        od.ellipse([400-r,200-r,400+r,200+r], fill=(255,200,50,a))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    img.save(os.path.join(OUT, "victory.png"))
    print("✓ victory")


# ===== GENERATE ALL =====
if __name__ == "__main__":
    print("Generating Darkwing Duck game assets...")
    print(f"Output: {OUT}\n")
    
    # Backgrounds
    gen_titleBg()
    gen_bgRooftops()
    gen_bgFunhouse()
    gen_bgGreenhouse()
    gen_bgDam()
    gen_bgFortress()
    
    # Villain portraits (256x256)
    gen_portraitDarkwing()
    gen_villain_portrait("Megavolt", 256, (60,50,10), (255,238,68), draw_megavolt)
    gen_villain_portrait("Quackerjack", 256, (60,15,40), (255,68,170), draw_quackerjack)
    gen_villain_portrait("Bushroot", 256, (15,50,15), (68,187,68), draw_bushroot)
    gen_villain_portrait("Liquidator", 256, (10,30,60), (68,170,255), draw_liquidator)
    gen_villain_portrait("Negaduck", 256, (50,10,10), (255,34,68), draw_negaduck)
    
    # Ally portraits (128x128)
    gen_portraitLaunchpad()
    gen_portraitGosalyn()
    gen_portraitMorgana()
    gen_portraitGizmoduck()
    
    # Game over / Victory
    gen_gameOver()
    gen_victory()
    
    print(f"\n✅ All 18 assets generated in {OUT}")
