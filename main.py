"""
╔══════════════════════════════════════════════╗
║         Luna the Fox  v3.0                   ║
║  2 Nivåer · Grottor · Fiender · Ljud · Dash  ║
╚══════════════════════════════════════════════╝
A/D eller ←/→  = rörelse
SPACE / W / ↑  = hopp  (dubbel-hopp tillåtet)
SHIFT          = dash
ESC            = meny
"""

import pygame, sys, math, random, json, os, array
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

SW, SH, FPS = 1280, 720, 60
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Luna the Fox")
clock  = pygame.time.Clock()

SAVE_FILE = "luna_save.json"

# ═══════════════════════════════════════════
#  LJUD  (procedurellt – ingen numpy behövs)
# ═══════════════════════════════════════════
SR = 44100

class _DummySound:
    """Tyst dummy när pygame.sndarray saknas."""
    def play(self, *a): pass
    def stop(self): pass
    def set_volume(self, v): pass

def _make_sound(samples):
    """Bygg Sound från Python-lista utan numpy."""
    buf = array.array('h')
    for s in samples:
        buf.append(int(max(-32767, min(32767, s))))
    # pygame.mixer.Sound kan läsa bytes direkt
    return pygame.mixer.Sound(buffer=buf)

def _synth(fn, dur):
    n = int(SR * dur)
    return _make_sound([fn(i, n) for i in range(n)])

def make_jump_sound():
    return _synth(lambda i,n: math.sin(2*math.pi*(400+1200*(1-i/n))*i/SR)*18000*(1-i/n), 0.18)

def make_double_jump_sound():
    return _synth(lambda i,n: math.sin(2*math.pi*(600+800*(1-i/n))*i/SR)*14000*(1-i/n), 0.14)

def make_coin_sound():
    return _synth(lambda i,n: math.sin(2*math.pi*(900+400*i/n)*i/SR)*16000*(1-i/n)**0.5, 0.12)

def make_land_sound():
    return _synth(lambda i,n: random.uniform(-1,1)*20000*(1-i/n)**2, 0.08)

def make_hit_sound():
    return _synth(lambda i,n: math.sin(2*math.pi*150*i/SR)*22000*(1-i/n)
                              + random.uniform(-1,1)*8000*(1-i/n), 0.22)

def make_dash_sound():
    return _synth(lambda i,n: math.sin(2*math.pi*(200+1800*i/n)*i/SR)*14000*(1-i/n), 0.10)

def make_death_sound():
    return _synth(lambda i,n: math.sin(2*math.pi*(300-250*i/n)*i/SR)*20000*(1-i/n)**0.3, 0.40)

def make_level_sound():
    notes=[523,659,784,1047]; spb=int(SR*0.13); wave=[]
    for ni,note in enumerate(notes):
        for i in range(spb):
            wave.append(math.sin(2*math.pi*note*i/SR)*22000*(1-i/spb*0.3))
    return _make_sound(wave)

def make_music():
    spb=int(SR*0.38)
    mel=[262,294,330,349,392,440,494,523,494,440,392,349,330,294,262,220]
    bass=[131,131,165,131,131,131,147,131]*2
    wave=[]
    for i in range(spb*16):
        beat=i//spb; t=i/SR
        mi=beat%len(mel); bi=beat%len(bass)
        m=math.sin(2*math.pi*mel[mi]*t)*7000
        b=math.sin(2*math.pi*bass[bi]*t)*4500
        sq=(1 if math.sin(2*math.pi*mel[mi]*2*t)>0 else -1)*2500
        wave.append(m+b+sq)
    return _make_sound(wave)

def make_cave_music():
    spb=int(SR*0.45)
    mel=[196,220,247,262,220,196,175,196,220,247,262,294,262,247,220,196]
    wave=[]
    for i in range(spb*16):
        beat=i//spb; t=i/SR; mi=beat%len(mel)
        env=1-(i%spb)/spb*0.6
        wave.append(math.sin(2*math.pi*mel[mi]*t)*9000*env
                   +math.sin(2*math.pi*mel[mi]*1.5*t)*3000*env)
    return _make_sound(wave)

def make_volcano_music():
    spb=int(SR*0.32)
    mel=[147,147,175,147,131,147,165,147,
         175,196,175,165,147,131,123,131]
    bass=[73,73,87,73,65,73,82,73]*2
    wave=[]
    for i in range(spb*16):
        beat=i//spb; t=i/SR; mi=beat%len(mel); bi=beat%len(bass)
        env=1-(i%spb)/spb*0.4
        m=math.sin(2*math.pi*mel[mi]*t)*10000*env
        b=math.sin(2*math.pi*bass[bi]*t)*6000*env
        rumble=math.sin(2*math.pi*40*t)*3000*(0.5+0.5*math.sin(t*0.7))
        wave.append(m+b+rumble)
    return _make_sound(wave)

def make_boss_music():
    spb=int(SR*0.28)
    mel=[220,220,261,220,196,220,246,220,
         261,293,261,246,220,196,174,196]
    wave=[]
    for i in range(spb*16):
        beat=i//spb; t=i/SR; mi=beat%len(mel)
        env=1-(i%spb)/spb*0.3
        m=math.sin(2*math.pi*mel[mi]*t)*12000*env
        sq=(1 if math.sin(2*math.pi*mel[mi]*0.5*t)>0 else -1)*5000*env
        thump=math.sin(2*math.pi*60*t)*4000*(1-(i%spb)/spb)**3
        wave.append(m+sq+thump)
    return _make_sound(wave)

print("Genererar ljud...", end=" ", flush=True)
try:
    SND_JUMP  = make_jump_sound()
    SND_DJUMP = make_double_jump_sound()
    SND_COIN  = make_coin_sound()
    SND_LAND  = make_land_sound()
    SND_HIT   = make_hit_sound()
    SND_DASH  = make_dash_sound()
    SND_DEATH = make_death_sound()
    SND_LEVEL = make_level_sound()
    MUS_1     = make_music()
    MUS_2     = make_cave_music()
    MUS_3     = make_volcano_music()
    MUS_BOSS  = make_boss_music()
    SND_JUMP.set_volume(0.55);  SND_DJUMP.set_volume(0.45)
    SND_COIN.set_volume(0.60);  SND_LAND.set_volume(0.30)
    SND_HIT.set_volume(0.70);   SND_DASH.set_volume(0.40)
    SND_DEATH.set_volume(0.65); SND_LEVEL.set_volume(0.75)
    MUS_1.set_volume(0.35);     MUS_2.set_volume(0.35)
    MUS_3.set_volume(0.40);     MUS_BOSS.set_volume(0.45)
    SOUND_OK = True
    print("OK")
except Exception as e:
    # Skapa tysta dummy-objekt så resten av koden fungerar
    _d = _DummySound()
    SND_JUMP=SND_DJUMP=SND_COIN=SND_LAND=_d
    SND_HIT=SND_DASH=SND_DEATH=SND_LEVEL=_d
    MUS_1=MUS_2=MUS_3=MUS_BOSS=_d
    SOUND_OK = False
    print(f"Ljud inaktiverat: {e}")

current_music = None
def play_music(snd):
    global current_music
    if snd is current_music: return
    if current_music: current_music.stop()
    current_music = snd
    try: snd.play(-1)
    except: pass

def stop_music():
    global current_music
    if current_music:
        try: current_music.stop()
        except: pass
    current_music = None

def play_sfx(snd):
    try: snd.play()
    except: pass

# ═══════════════════════════════════════════
#  SPARA / LADDA
# ═══════════════════════════════════════════
def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE) as f: return json.load(f)
        except: pass
    return {"high_scores":[], "last_player":""}

def write_save(d):
    with open(SAVE_FILE,"w") as f: json.dump(d,f,indent=2)

def add_score(sd, name, score, ticks):
    e = {"name":name,"score":score,"mins":ticks//(FPS*60),"secs":(ticks//FPS)%60}
    sd["high_scores"].append(e)
    sd["high_scores"].sort(key=lambda x:x["score"], reverse=True)
    sd["high_scores"] = sd["high_scores"][:10]
    sd["last_player"] = name
    write_save(sd)

# ═══════════════════════════════════════════
#  FONTS
# ═══════════════════════════════════════════
def mf(name,size,bold=False):
    try:    return pygame.font.SysFont(name,size,bold=bold)
    except: return pygame.font.SysFont(None,size,bold=bold)

ft = mf("Georgia",76,True)
fb = mf("Segoe UI",40,True)
fm = mf("Segoe UI",28,True)
fs = mf("Segoe UI",22)
fti= mf("Segoe UI",16)

# ═══════════════════════════════════════════
#  FÄRGPALETT
# ═══════════════════════════════════════════
# Nivå 1 – skog/dag
L1 = dict(
    sky_top=(15,20,60), sky_bot=(90,150,220),
    sun=(255,230,100),  cloud=(255,255,255),
    grass_d=(34,120,40),grass_l=(75,190,65),
    dirt=(110,75,45),   plat_edge=(45,85,25),
)
# Nivå 2 – grottor
L2 = dict(
    sky_top=(8,5,18),   sky_bot=(30,18,50),
    sun=(255,120,30),   cloud=(80,60,110),
    grass_d=(60,45,80), grass_l=(90,65,120),
    dirt=(50,38,60),    plat_edge=(35,25,55),
)
# Nivå 3 – vulkan
L3 = dict(
    sky_top=(25,5,5),    sky_bot=(80,20,5),
    sun=(255,80,10),     cloud=(140,50,20),
    grass_d=(120,30,10), grass_l=(180,60,15),
    dirt=(90,40,20),     plat_edge=(60,20,5),
)

FOX_BODY=(210,80,30); FOX_BELLY=(255,200,140); FOX_TIP=(255,255,255)
FOX_EAR =(240,130,80); EYE_PUP=(25,15,15)
GOLD=(255,210,50); WHITE=(255,255,255); RED=(220,50,50)
HUD_COL=(255,235,110)
PART_COLS=[(255,200,80),(255,160,40),(255,120,20),(255,240,180)]
CAVE_PART=[(100,200,255),(60,140,220),(140,220,255),(80,160,240)]
TORCH_COLS=[(255,200,50),(255,140,20),(255,80,10),(200,60,0)]
LAVA_PART=[(255,80,10),(255,140,20),(255,40,0),(200,20,0),(255,200,50)]
ROCK_COL=(80,60,50)


# ====================== LUNA SPRITE ANIMATION ======================

ANIMATIONS = {}
current_anim = "idle"
anim_frame = 0
anim_timer = 0
facing_right = True




def load_animation(folder, target_width=78, target_height=105):
    """Anpassad för dina exakta filnamn"""
    frames = []
    possible_patterns = [
        f"{folder}.png",        # idle.png, dash.png
        f"{folder}1.png",       # idle1.png, run1.png
        f"{folder}2.png",       # idle2.png
        f"{folder}3.png",       # run3.png
        f"{folder}4.png",
    ]
    
    print(f"Laddar {folder} animation...")
    
    for name in possible_patterns:
        path = f"bilder/{name}"
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (target_width, target_height))
                frames.append(img)
                print(f"   ✓ Laddade {name} ({img.get_width()}x{img.get_height()})")
            except Exception as e:
                print(f"   ✗ Kunde inte ladda {name} → {e}")
    
    print(f"   → Totalt {len(frames)} bilder för {folder}\n")
    return frames

# def load_animation(folder, target_width=78, target_height=105):
#     """Laddar bilder från din 'bilder/' mapp"""
#     frames = []
#     i = 0
#     while True:
#         # Testar flera möjliga filnamn
#         possible_names = [
#             f"{folder}{i}.png",      # t.ex. idle0.png, run1.png
#             f"{folder}{i+1}.png",    # idle1.png, run2.png
#             f"{folder}.png",         # idle.png, jump.png
#             f"{folder}1.png",        # idle1.png, run1.png
#         ]
#         loaded = False
#         for name in possible_names:
#             path = f"bilder/{name}"
#             if os.path.exists(path):
#                 try:
#                     img = pygame.image.load(path).convert_alpha()
#                     img = pygame.transform.scale(img, (target_width, target_height))
#                     frames.append(img)
#                     loaded = True
#                     break
#                 except:
#                     pass
#         if not loaded:
#             break
#         i += 1
#     return frames


def load_all_animations():
    global ANIMATIONS
    ANIMATIONS = {}
    
    print("=== Laddar Luna animationer ===\n")
    
    ANIMATIONS["idle"]        = load_animation("idle")
    ANIMATIONS["run"]         = load_animation("run")
    ANIMATIONS["jump"]        = load_animation("jump")
    ANIMATIONS["double_jump"] = load_animation("djump")
    ANIMATIONS["dash"]        = load_animation("dash", 85, 105)
    ANIMATIONS["hit"]         = load_animation("hit")
    ANIMATIONS["landing"]     = load_animation("landing")
    
    total = sum(len(v) for v in ANIMATIONS.values())
    print(f"✅ KLAR! Totalt {total} bilder laddade.")







def lerp(a,b,t): return a+(b-a)*t
def lerp_col(c1,c2,t):
    return tuple(int(lerp(c1[i],c2[i],t)) for i in range(3))

# ═══════════════════════════════════════════
#  GRADIENT-YTOR  (pre-render)
# ═══════════════════════════════════════════
def make_sky(top,bot):
    s = pygame.Surface((SW,SH))
    for y in range(SH):
        t=y/SH
        pygame.draw.line(s,lerp_col(top,bot,t),(0,y),(SW,y))
    return s

sky1 = make_sky(L1["sky_top"], L1["sky_bot"])
sky2 = make_sky(L2["sky_top"], L2["sky_bot"])
sky3 = make_sky(L3["sky_top"], L3["sky_bot"])

# ═══════════════════════════════════════════
#  NIVÅDATA
# ═══════════════════════════════════════════
# (x, y, w, h)
PLATS_1 = [
    (0,   555, 880,200),
    (940, 455, 360, 22),
    (1360,355, 300, 22),
    (1750,440, 380, 22),
    (2210,350, 290, 22),
    (2575,440, 330, 22),
    (2985,345, 270, 22),
    (3340,415, 340, 22),
    (3760,315, 250, 22),
    (4080,415, 310, 22),
    (4450,555,1100,200),
]
# Checkpoints: x-position (världskoord) som aktiveras
CHECKS_1 = [2000, 3500]

PLATS_2 = [
    (0,   540, 760,200),
    (820, 440, 280, 22),
    (1170,340, 260, 22),
    (1530,440, 300, 22),
    (1920,330, 240, 22),
    (2260,430, 280, 22),
    (2640,320, 260, 22),
    (2990,420, 300, 22),
    (3380,310, 240, 22),
    (3710,400, 280, 22),
    (4080,535,1000,200),
]
CHECKS_2 = [1700, 3100]

# Nivå 3 – Vulkan (rörliga plattformar markerade med move_*)
# Format statisk: (x, y, w, h)
# Format rörlig:  (x, y, w, h, "h"|"v", amplitude, speed)  → hanteras separat
PLATS_3_STATIC = [
    (0,   540, 700, 200),   # start-mark
    (4600, 520, 900, 200),  # slutmark + boss-arena
]
PLATS_3_MOVING = [
    # (x, y, w, h, axis, amp, speed)
    (780,  440, 200, 22, "h", 100, 1.4),
    (1120, 350, 180, 22, "v",  70, 1.2),
    (1480, 430, 200, 22, "h", 120, 1.8),
    (1860, 320, 160, 22, "v",  80, 1.5),
    (2200, 420, 200, 22, "h", 140, 2.0),
    (2600, 310, 180, 22, "v",  90, 1.3),
    (2950, 400, 200, 22, "h", 110, 1.9),
    (3320, 290, 160, 22, "v",  80, 1.6),
    (3680, 380, 200, 22, "h", 130, 2.2),
    (4080, 300, 180, 22, "v",  70, 1.4),
    (4380, 440, 200, 22, "h",  80, 1.7),
]
CHECKS_3 = [1800, 3400]

# Lava-pooler på golvet (x, w) – dödar vid beröring
LAVA_POOLS = [
    (720, 380),(1080,320),(1440,360),(1820,300),
    (2160,380),(2560,320),(2900,360),(3280,300),
    (3640,360),(4040,300),(4350,200),
]

# Meteorer: slumpmässigt spawnar under spel – inga fasta positioner
METEOR_SPAWN_RATE = 90   # frames mellan spawns (lägre = tätare)

ENEMIES_3 = [
    (1000, 425, 160, 3.0, 4.5),
    (1650, 335, 140, 3.2, 4.8),
    (2380, 405, 160, 3.5, 5.0),
    (3050, 385, 140, 3.8, 5.2),
    (3800, 365, 160, 4.0, 5.5),
    (4200, 285, 140, 4.2, 5.8),
]

# Boss-data
BOSS_START_X = 4900.0
BOSS_Y       = 430

# Facklor i grottnivån (x, y)
TORCHES = [
    (850,400),(1200,300),(1570,400),(1950,290),
    (2290,390),(2670,280),(3020,380),(3410,270),(3740,360),
]

# Fiender per nivå: (x, y, patrol_w, speed_min, speed_max)
ENEMIES_1 = [
    (1100,440,200, 1.5,2.5),
    (1900,425,250, 1.8,2.8),
    (2800,420,220, 2.0,3.2),
    (3500,400,280, 2.2,3.5),
    (4100,400,200, 2.5,3.8),
]
ENEMIES_2 = [
    (900, 425,180, 2.0,3.0),
    (1600,425,220, 2.2,3.2),
    (2000,315,160, 1.8,2.8),
    (2700,305,200, 2.5,3.5),
    (3050,405,200, 2.8,3.8),
    (3450,295,180, 2.5,3.5),
    (3770,385,220, 3.0,4.2),
]

# ═══════════════════════════════════════════
#  HJÄLPFUNKTIONER – RITA
# ═══════════════════════════════════════════
def draw_cloud(surf, cx, cy, w, col=(255,255,255)):
    for dx,dy,r in [(0,0,w//5),(-w//4,w//12,w//6),(w//4,w//12,w//6),
                    (-w//8,-w//14,w//7),(w//8,-w//14,w//7)]:
        r=max(r,4)
        pygame.draw.ellipse(surf,col,(int(cx-r+dx),int(cy-r//2+dy),r*2,r))

def draw_platform(surf,p,cam_x,lvl=1):
    d=p.copy(); d.x-=int(cam_x)
    if d.right<-30 or d.left>SW+30: return
    pal = L1 if lvl==1 else (L2 if lvl==2 else L3)
    # skugga
    ss=pygame.Surface((d.w+8,d.h+8),pygame.SRCALPHA)
    pygame.draw.rect(ss,(0,0,0,50),ss.get_rect(),border_radius=7)
    surf.blit(ss,(d.x-2,d.y+5))
    pygame.draw.rect(surf,pal["dirt"],d,border_radius=7)
    gh=min(16,d.h)
    pygame.draw.rect(surf,pal["grass_d"],(d.x,d.y,d.w,gh),border_radius=7)
    if d.w>20:
        pygame.draw.rect(surf,pal["grass_l"],(d.x+5,d.y+3,d.w-10,5),border_radius=3)
    pygame.draw.rect(surf,pal["plat_edge"],d,2,border_radius=7)

def draw_torch(surf, tx, ty, cam_x, tick):
    sx=int(tx-cam_x); sy=int(ty)
    if sx<-20 or sx>SW+20: return
    # Pinne
    pygame.draw.rect(surf,(100,70,40),(sx-3,sy,6,22))
    # Flamma (animerad)
    flicker=math.sin(tick*0.25+tx)*3
    for i,col in enumerate(TORCH_COLS):
        r=8-i*1.5+flicker*(0.5-i*0.1)
        if r>0:
            pygame.draw.circle(surf,col,(sx,int(sy-i*4)),int(r))
    # Ljus-glöd
    glow=pygame.Surface((80,80),pygame.SRCALPHA)
    pygame.draw.circle(glow,(255,150,30,40),(40,40),40)
    surf.blit(glow,(sx-40,sy-40))




def draw_fox(surf, prect, cam_x, invincible=False):
    if invincible and (atick // 4) % 2 == 1:
        return

    frames = ANIMATIONS.get(current_anim)
    if not frames or anim_frame >= len(frames):
        return

    img = frames[anim_frame]

    if not facing_right:
        img = pygame.transform.flip(img, True, False)

    # 🎯 Perfekt position (centrerad + står på marken)
    draw_x = int(prect.centerx - cam_x - img.get_width() // 2)
    draw_y = int(prect.bottom - img.get_height())

    surf.blit(img, (draw_x, draw_y))

    # 🧪 DEBUG (ta bort sen)
    # pygame.draw.rect(
    #     surf,
    #     (255, 0, 0),
    #     (
    #         int(prect.x - cam_x),
    #         int(prect.y),
    #         prect.width,
    #         prect.height
    #     ),
    #     2
    # )



   








def draw_enemy(surf, e, cam_x, tick):
    sx = int(e["x"] - cam_x)
    sy = int(e["y"])
    if sx < -60 or sx > SW + 60:
        return

    flip = 1 if e["dir"] > 0 else -1
    col = (140, 60, 180) if e.get("lvl", 1) == 2 else (80, 130, 60)
    dark = tuple(max(0, c - 40) for c in col)

    # Kropp
    pygame.draw.ellipse(surf, col, (sx - 18, sy - 24, 36, 28))
    pygame.draw.ellipse(surf, dark, (sx - 18, sy - 24, 36, 10))

    # Ben
    ls = math.sin(tick * 0.22) * 8
    for lx, la in [(sx - 8, ls), (sx + 8, -ls)]:
        pygame.draw.rect(surf, dark, (lx - 3, sy + 4, 7, 14 + int(abs(la))), border_radius=3)

    # Huvud
    pygame.draw.ellipse(surf, col, (sx - 14, sy - 48, 28, 26))

    # Ögon
    ex2 = sx - 4 + flip * 3
    ey2 = sy - 40
    pygame.draw.circle(surf, (220, 30, 30), (ex2, ey2), 5)
    pygame.draw.circle(surf, (255, 255, 255), (ex2 + flip, ey2 - 1), 2)

    # Tänder
    for ti in range(3):
        tx2 = sx - 6 + ti * 6
        pygame.draw.rect(surf, WHITE, (tx2, sy - 28, 4, 6), border_radius=2)











def update_animation():
    global current_anim, anim_frame, anim_timer, facing_right

    anim_timer += 1 / FPS

    # Välj rätt animation
    if dashing:
        new_anim = "dash"
    elif invincible > 0:
        new_anim = "hit"
    elif not on_gnd:
        new_anim = "double_jump" if not djump_avail else "jump"
    elif abs(vx) > 2.0:
        new_anim = "run"
    else:
        new_anim = "idle"

    # Byt animation om nödvändigt
    if new_anim != current_anim:
        current_anim = new_anim
        anim_frame = 0
        anim_timer = 0

    # Uppdatera bildruta
    if current_anim in ANIMATIONS and ANIMATIONS[current_anim]:
        speed = 0.07 if current_anim == "run" else 0.16
        if anim_timer >= speed:
            anim_timer = 0
            anim_frame = (anim_frame + 1) % len(ANIMATIONS[current_anim])

    facing_right = fright











# def draw_fox(surf,rx,ry,face_right,squash,stretch,tick,vx,invincible=False):
#     if invincible and (tick//4)%2==1: return   # blinkar vid skada
#     sw=int(44*(2-stretch)*squash)
#     sh=int(52*stretch/squash)
#     ox=rx+(44-sw)//2; oy=ry+(52-sh)
#     flip=1 if face_right else -1

#     # Svans
#     tbx=ox+(sw-4 if face_right else 4); tby=oy+sh-14
#     ctx=tbx-flip*30; cty=tby-30
#     tpx=tbx-flip*50; tpy=tby-10+int(math.sin(tick*0.05)*5)
#     pts=[(int((1-t)**2*tbx+2*(1-t)*t*ctx+t**2*tpx),
#           int((1-t)**2*tby+2*(1-t)*t*cty+t**2*tpy))
#          for t in [i/11 for i in range(12)]]
#     if len(pts)>=2:
#         pygame.draw.lines(surf,FOX_BODY,False,pts,9)
#         pygame.draw.lines(surf,FOX_BELLY,False,pts,4)
#     pygame.draw.circle(surf,FOX_TIP,(tpx,tpy),7)

#     pygame.draw.ellipse(surf,FOX_BODY,(ox,oy+8,sw,sh-8))
#     pygame.draw.ellipse(surf,FOX_BELLY,(ox+7,oy+18,sw-14,sh-22))

#     leg=math.sin(tick*0.28)*7 if abs(vx)>0.8 else 0
#     for lx,ls in [(ox+5,leg),(ox+sw-15,-leg)]:
#         pygame.draw.rect(surf,FOX_BODY,(lx,oy+sh-16,10,16+int(abs(ls))),border_radius=4)

#     hx=ox+(sw-36)//2; hy=oy-20
#     pygame.draw.ellipse(surf,FOX_BODY,(hx,hy,36,30))
#     for edx in [4,20]:
#         ep=[(hx+edx,hy+6),(hx+edx-5,hy-14),(hx+edx+10,hy-2)]
#         pygame.draw.polygon(surf,FOX_EAR,ep)
#         pygame.draw.polygon(surf,(240,150,100),[(x+flip,y+2)for x,y in ep])

#     nx=hx+(27 if face_right else 5)
#     pygame.draw.ellipse(surf,(40,25,25),(nx,hy+18,9,6))
#     ex=hx+(21 if face_right else 11); ey=hy+11
#     pygame.draw.circle(surf,WHITE,(ex,ey),7)
#     pygame.draw.circle(surf,EYE_PUP,(ex+flip,ey+1),4)
#     pygame.draw.circle(surf,WHITE,(ex+flip+1,ey-1),1)

# def draw_enemy(surf, e, cam_x, tick):
#     sx=int(e["x"]-cam_x); sy=int(e["y"])
#     if sx<-60 or sx>SW+60: return
#     flip=1 if e["dir"]>0 else -1
#     # Kropp – lila/grå monster
#     col=(140,60,180) if e.get("lvl",1)==2 else (80,130,60)
#     dark=tuple(max(0,c-40) for c in col)
#     pygame.draw.ellipse(surf,col,(sx-18,sy-24,36,28))   # kropp
#     pygame.draw.ellipse(surf,dark,(sx-18,sy-24,36,10))  # rygg-rand

#     # Ben (animerat)
#     ls=math.sin(tick*0.22)*8
#     for lx,la in [(sx-8,ls),(sx+8,-ls)]:
#         pygame.draw.rect(surf,dark,(lx-3,sy+4,7,14+int(abs(la))),border_radius=3)

#     # Huvud
#     pygame.draw.ellipse(surf,col,(sx-14,sy-48,28,26))
#     # Ögon (röda)
#     ex2=sx-4+flip*3; ey2=sy-40
#     pygame.draw.circle(surf,(220,30,30),(ex2,ey2),5)
#     pygame.draw.circle(surf,(255,255,255),(ex2+flip,ey2-1),2)
#     # Tänder
#     for ti in range(3):
#         tx2=sx-6+ti*6
#         pygame.draw.rect(surf,WHITE,(tx2,sy-28,4,6),border_radius=2)







def draw_hud(surf, name, sc, t, lives, lvl, dash_cd, djump):
    # Vänster panel
    hud=pygame.Surface((480,70),pygame.SRCALPHA); hud.fill((8,8,35,155))
    surf.blit(hud,(14,12))
    pygame.draw.rect(surf,GOLD,(14,12,480,70),2,border_radius=8)
    mins=t//(FPS*60); secs=(t//FPS)%60
    txt=fs.render(f"{name}  {mins:02d}:{secs:02d}  Poang:{sc}  Niva:{lvl}",True,HUD_COL)
    surf.blit(txt,(24,30))

    # Liv-hjärtan
    for i in range(3):
        col=RED if i<lives else (60,30,30)
        hx2=24+i*36; hy2=55
        # enkel hjärta via cirklar + polygon
        pygame.draw.circle(surf,col,(hx2+6,hy2),7)
        pygame.draw.circle(surf,col,(hx2+18,hy2),7)
        pygame.draw.polygon(surf,col,[(hx2,hy2+4),(hx2+12,hy2+16),(hx2+24,hy2+4)])

    # Dash-bar
    bar_x=490; bar_y=16; bar_w=160; bar_h=18
    pygame.draw.rect(surf,(30,30,60),(bar_x,bar_y,bar_w,bar_h),border_radius=5)
    fill=int(bar_w*(1-dash_cd/45)) if dash_cd>0 else bar_w
    dcol=(80,200,255) if dash_cd==0 else (50,100,180)
    pygame.draw.rect(surf,dcol,(bar_x,bar_y,fill,bar_h),border_radius=5)
    pygame.draw.rect(surf,GOLD,(bar_x,bar_y,bar_w,bar_h),2,border_radius=5)
    dt=fti.render("DASH",True,WHITE); surf.blit(dt,(bar_x+bar_w//2-dt.get_width()//2,bar_y+1))

    # Dubbel-hopp-indikator
    djc=GOLD if djump else (60,50,20)
    pygame.draw.circle(surf,djc,(bar_x+bar_w+24,bar_y+9),10)
    pygame.draw.circle(surf,WHITE,(bar_x+bar_w+24,bar_y+9),10,2)
    jt=fti.render("2x",True,WHITE if djump else (80,70,40))
    surf.blit(jt,(bar_x+bar_w+16,bar_y+2))

def draw_checkpoint(surf,cx,cy,cam_x,active):
    sx=int(cx-cam_x)
    if sx<-20 or sx>SW+20: return
    pcol=GOLD if active else (100,80,30)
    pygame.draw.rect(surf,(80,60,20),(sx-3,cy-40,6,50))
    pygame.draw.polygon(surf,pcol,[(sx+3,cy-40),(sx+28,cy-28),(sx+3,cy-16)])

def draw_lava(surf, pools, cam_x, tick):
    for lx,lw in pools:
        sx=int(lx-cam_x)
        if sx>SW+20 or sx+lw<-20: continue
        # Lava-kropp
        pygame.draw.rect(surf,(180,30,5),(sx,SH-110,lw,120))
        # Animerad yta
        for i in range(0,lw,18):
            bub=int(math.sin(tick*0.12+i*0.4)*5)
            pygame.draw.ellipse(surf,(255,100,10),(sx+i,SH-118+bub,16,12))
            pygame.draw.ellipse(surf,(255,200,30),(sx+i+3,SH-115+bub,8,6))
        # Glöd-overlay
        glow=pygame.Surface((lw,40),pygame.SRCALPHA)
        for gy in range(40):
            al=int((1-gy/40)*60)
            pygame.draw.line(glow,(255,80,10,al),(0,gy),(lw,gy))
        surf.blit(glow,(sx,SH-130))

def draw_meteor(surf, m, cam_x):
    sx=int(m["x"]-cam_x); sy=int(m["y"])
    if sx<-60 or sx>SW+60: return
    # Svans
    tpts=[]
    for i in range(8):
        t=i/7; tx2=sx-int(m["vx"]*t*4); ty2=sy-int(m["vy"]*t*4)
        tpts.append((tx2,ty2))
    if len(tpts)>=2:
        for i in range(len(tpts)-1):
            a=int((1-i/len(tpts))*200)
            col=(min(255,255-i*20),max(0,120-i*15),0,a)
            ps=pygame.Surface((6,6),pygame.SRCALPHA)
            pygame.draw.circle(ps,col,(3,3),3-i//3)
            surf.blit(ps,(tpts[i][0]-3,tpts[i][1]-3))
    # Kärna
    pygame.draw.circle(surf,(255,220,80),(sx,sy),7)
    pygame.draw.circle(surf,(255,140,20),(sx,sy),5)
    pygame.draw.circle(surf,(200,60,0),(sx,sy),3)

def draw_boss(surf, boss, cam_x, tick):
    if not boss["alive"]: return
    bx=int(boss["x"]-cam_x); by=int(boss["y"])
    if bx<-120 or bx>SW+120: return
    phase=boss["phase"]  # 0,1,2 baserat på liv
    # Färg mörknar med fas
    base_col=[(180,40,200),(220,30,30),(255,80,0)][phase]
    dark_col=tuple(max(0,c-50) for c in base_col)
    shake=int(math.sin(tick*0.4)*phase*3)














    # Kropp (stor ellips)
    pygame.draw.ellipse(surf,dark_col,(bx-44+shake,by-10,88,70))
    pygame.draw.ellipse(surf,base_col,(bx-38+shake,by-4,76,58))
    # Mage-mönster
    pygame.draw.ellipse(surf,(255,200,50,150),(bx-20+shake,by+10,40,28))

    # Ben (4 st, animerade)
    for li,loff in enumerate([-28,-12,12,28]):
        ls=math.sin(tick*0.15+li)*12
        pygame.draw.rect(surf,dark_col,(bx+loff-4+shake,by+58,8,20+int(abs(ls))),border_radius=4)

    # Huvud
    pygame.draw.ellipse(surf,base_col,(bx-34+shake,by-56,68,52))
    # Horn
    pygame.draw.polygon(surf,(255,200,50),[
        (bx-20+shake,by-56),(bx-30+shake,by-80),(bx-8+shake,by-56)])
    pygame.draw.polygon(surf,(255,200,50),[
        (bx+20+shake,by-56),(bx+30+shake,by-80),(bx+8+shake,by-56)])
    # Ögon (glödande)
    ec1=(255,50,0) if phase<2 else (255,255,0)
    for ex3,ey3 in [(bx-12+shake,by-38),(bx+12+shake,by-38)]:
        pygame.draw.circle(surf,ec1,(ex3,ey3),10)
        pygame.draw.circle(surf,(255,255,200),(ex3,ey3),5)
        pygame.draw.circle(surf,(0,0,0),(ex3+1,ey3+1),3)
    # Tänder
    for ti in range(5):
        tx3=bx-20+ti*10+shake
        pygame.draw.polygon(surf,WHITE,[(tx3,by-24),(tx3+4,by-24),(tx3+2,by-14)])

    # HP-bar
    hp_frac=boss["hp"]/boss["max_hp"]
    bar_w=160; bar_x=bx-80+shake
    pygame.draw.rect(surf,(40,0,0),(bar_x,by-80,bar_w,12),border_radius=4)
    hpcol=(0,220,0) if hp_frac>0.5 else (220,180,0) if hp_frac>0.25 else (220,30,0)
    pygame.draw.rect(surf,hpcol,(bar_x,by-80,int(bar_w*hp_frac),12),border_radius=4)
    pygame.draw.rect(surf,WHITE,(bar_x,by-80,bar_w,12),2,border_radius=4)
    ht=fti.render("BOSS",True,WHITE)
    surf.blit(ht,(bar_x+bar_w//2-ht.get_width()//2,by-97))

# ═══════════════════════════════════════════
#  PARTIKLAR
# ═══════════════════════════════════════════
def spawn_parts(parts,x,y,count=10,cols=None):
    c=cols or PART_COLS
    for _ in range(count):
        a=random.uniform(-math.pi,0); spd=random.uniform(2,5.5)
        parts.append({"x":float(x),"y":float(y),
                      "vx":math.cos(a)*spd,"vy":math.sin(a)*spd-1.5,
                      "life":1.0,"decay":random.uniform(0.035,0.07),
                      "r":random.randint(3,8),"col":random.choice(c)})

def spawn_dash_parts(parts,x,y,vx):
    for _ in range(14):
        parts.append({"x":float(x),"y":float(y),
                      "vx":-vx*random.uniform(0.1,0.4)+random.uniform(-1,1),
                      "vy":random.uniform(-2,2),
                      "life":0.7,"decay":random.uniform(0.06,0.12),
                      "r":random.randint(4,9),
                      "col":random.choice([(80,200,255),(50,150,220),(140,220,255)])})

def update_parts(surf,parts,cam_x):
    for p in parts[:]:
        p["x"]+=p["vx"]; p["y"]+=p["vy"]
        p["vy"]+=0.20; p["vx"]*=0.96; p["life"]-=p["decay"]
        if p["life"]<=0: parts.remove(p); continue
        r=max(1,p["r"])
        ps=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
        pygame.draw.circle(ps,p["col"]+(int(p["life"]*230),),(r,r),r)
        surf.blit(ps,(int(p["x"]-cam_x)-r,int(p["y"])-r))

# ═══════════════════════════════════════════
#  MYNT
# ═══════════════════════════════════════════
def make_coins(plat_data):
    coins=[]
    for i,(px,py,pw,_) in enumerate(plat_data[1:-1],1):
        coins.append({"x":px+pw//2,"y":py-30,"r":10,"collected":False})
    return coins

def draw_coins(surf,coins,cam_x,tick):
    for c in coins:
        if c["collected"]: continue
        sx=int(c["x"]-cam_x); sy=int(c["y"]+math.sin(tick*0.06)*4)
        if sx<-30 or sx>SW+30: continue
        pygame.draw.circle(surf,GOLD,(sx,sy),c["r"])
        pygame.draw.circle(surf,(255,240,140),(sx-2,sy-2),c["r"]//2)
        pygame.draw.circle(surf,(180,140,20),(sx,sy),c["r"],2)

# ═══════════════════════════════════════════
#  MOLN & STJÄRNOR
# ═══════════════════════════════════════════
def make_clouds(n=20):
    return [{"x":float(random.randint(-200,5500)),"y":float(random.randint(50,220)),
             "w":random.randint(100,280),"speed":random.uniform(0.08,0.30)} for _ in range(n)]

def make_stars(n=80):
    return [{"x":random.randint(0,5500),"y":random.randint(5,350),
             "r":random.uniform(0.6,2.5),"bright":random.randint(140,255),
             "twinkle":random.uniform(0,math.pi*2)} for _ in range(n)]

def draw_stars(surf,stars,cam_x,tick,bright_base=1.0):
    for st in stars:
        t2=math.sin(tick*0.04+st["twinkle"])*0.3+0.7
        sx=int(st["x"]-cam_x*0.04)%SW
        b=int(st["bright"]*t2*bright_base)
        b=max(0,min(255,b))
        pygame.draw.circle(surf,(b,b,b),(sx,st["y"]),int(st["r"]))

# ═══════════════════════════════════════════
#  KNAPP
# ═══════════════════════════════════════════
class Button:
    def __init__(self,text,cx,cy,w=320,h=58):
        self.text=text; self._a=0.0
        self.rect=pygame.Rect(cx-w//2,cy-h//2,w,h)
    def update(self,mx,my):
        self._a=lerp(self._a,1.0 if self.rect.collidepoint(mx,my) else 0.0,0.15)
    def draw(self,surf):
        a=self._a
        bg=pygame.Surface((self.rect.w,self.rect.h),pygame.SRCALPHA)
        bg.fill((int(lerp(40,80,a)),int(lerp(30,60,a)),int(lerp(80,140,a)),int(lerp(160,225,a))))
        surf.blit(bg,self.rect)
        pygame.draw.rect(surf,(int(lerp(160,255,a)),int(lerp(160,230,a)),int(lerp(60,100,a))),
                         self.rect,3,border_radius=12)
        lbl=fm.render(self.text,True,GOLD if a>0.5 else WHITE)
        surf.blit(lbl,lbl.get_rect(center=self.rect.center))
    def clicked(self,ev):
        return ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1 and self.rect.collidepoint(ev.pos)

# ═══════════════════════════════════════════
#  TILLSTÅND
# ═══════════════════════════════════════════
S_MENU,S_NAME,S_SCORES,S_PLAY,S_DEAD,S_WIN,S_TRANS,S_BOSS_WIN = range(8)

# ═══════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════
def main():
    save_data=load_save()
    state=S_MENU
    pname=[""]   # mutable för inre funktion

    ni=save_data.get("last_player","")
    nc=len(ni); blink=0

    cx=SW//2
    btn_play  =Button("Spela",cx,360)
    btn_scores=Button("Topplista",cx,435)
    btn_quit  =Button("Avsluta",cx,510)
    btn_back  =Button("Tillbaka",cx,630,w=220,h=48)
    mbtns=[btn_play,btn_scores,btn_quit]

    # Meny-räv
    mfx=float(-80); mtick=0

    # Spelvariabler
    GRAV=0.72; JUMP=-19.5; SPEED=9.8; ACC=0.26; FRIC=0.78
    DASH_POWER=16; DASH_DUR=10; DASH_CD=45

    plats=[]; moving_plats=[]; coins=[]; parts=[]; enemies=[]
    checks=[]; check_active=[]
    meteors=[]; meteor_timer=0
    boss=None; boss_fight=False
    cam_x=0.0
    prect=pygame.Rect(150,380,44,52)


    # Animation
    current_anim = "idle"
    anim_frame = 0
    anim_timer = 0
    facing_right = True

    # Ändra storlek på spelaren till den nya större räven
    prect = pygame.Rect(150, 380, 78, 105)   # ← uppdaterad storlek



    # ====================== ANIMATION FUNKTION ======================
    def update_animation():
        nonlocal current_anim, anim_frame, anim_timer, facing_right

        anim_timer += 1 / FPS

        if dashing:
            new_anim = "dash"
        elif invincible > 0:
            new_anim = "hit"
        elif not on_gnd:
            new_anim = "double_jump" if not djump_avail else "jump"
        elif abs(vx) > 2.0:
            new_anim = "run"
        else:
            new_anim = "idle"

        if new_anim != current_anim:
            current_anim = new_anim
            anim_frame = 0
            anim_timer = 0

        if current_anim in ANIMATIONS and ANIMATIONS[current_anim]:
            speed = 0.07 if current_anim == "run" else 0.16
            if anim_timer >= speed:
                anim_timer = 0
                anim_frame = (anim_frame + 1) % len(ANIMATIONS[current_anim])

        facing_right = fright
    # ================================================================










    vx=vy=0.0; on_gnd=False; fright=True
    atick=0; jsq=1.0; jst=1.0
    score=0; gtime=0; lives=3; lvl=1
    djump_avail=True
    jheld=False; jht=0
    dash_cd=0; dash_dur=0; dashing=False
    invincible=0; coyote=0; jbuf=0
    clouds=make_clouds(); stars=make_stars()
    trans_alpha=0; trans_dir=0; trans_target=None
    checkpoint_pos=None
    lava_wave=0.0

    def reset(level=1, from_checkpoint=False):
        nonlocal plats,moving_plats,coins,parts,enemies,checks,check_active
        nonlocal meteors,meteor_timer,boss,boss_fight
        nonlocal cam_x,prect,vx,vy,on_gnd,fright
        nonlocal atick,jsq,jst,score,gtime,lives,lvl
        nonlocal djump_avail,jheld,jht,dash_cd,dash_dur,dashing
        nonlocal invincible,coyote,jbuf,clouds,stars,checkpoint_pos,lava_wave

        lvl=level
        if lvl==1:   pd,ed,chk = PLATS_1,ENEMIES_1,CHECKS_1
        elif lvl==2: pd,ed,chk = PLATS_2,ENEMIES_2,CHECKS_2
        else:        pd,ed,chk = PLATS_3_STATIC,ENEMIES_3,CHECKS_3

        plats=[pygame.Rect(x,y,w,h) for x,y,w,h in pd]
        moving_plats=[]
        if lvl==3:
            for mx3,my3,mw,mh,axis,amp,spd3 in PLATS_3_MOVING:
                mp={"rect":pygame.Rect(mx3,my3,mw,mh),
                    "ox":float(mx3),"oy":float(my3),
                    "axis":axis,"amp":float(amp),"spd":float(spd3),
                    "phase":random.uniform(0,math.pi*2)}
                moving_plats.append(mp)

        all_plat_data = pd if lvl<3 else pd+[(m[0],m[1],m[2],m[3]) for m in PLATS_3_MOVING]
        coins=make_coins(all_plat_data)
        parts=[]; enemies=[]; meteors=[]; meteor_timer=0
        boss=None; boss_fight=False; lava_wave=0.0
        checks=chk; check_active=[False]*len(chk)
        clouds=make_clouds(); stars=make_stars()

        if from_checkpoint and checkpoint_pos:
            sx,sy=checkpoint_pos
        else:
            sx,sy=150,380; checkpoint_pos=None

        cam_x=max(0.0,float(sx-SW//3))
        prect=pygame.Rect(sx,sy,78,105)
        vx=vy=0.0; on_gnd=False; fright=True
        atick=0; jsq=1.0; jst=1.0
        if not from_checkpoint: score=0; gtime=0; lives=3
        djump_avail=True; jheld=False; jht=0
        dash_cd=0; dash_dur=0; dashing=False; invincible=0
        coyote=0; jbuf=0

        for (ex,ey,pw,smin,smax) in ed:
            spd=random.uniform(smin,smax)
            enemies.append({"x":float(ex),"y":float(ey)-22,
                            "w":36,"h":54,"dir":1.0,
                            "patrol_x":float(ex),"patrol_w":pw,
                            "spd":spd,"tick":0,"lvl":lvl,"knockback":0})

        if lvl==1:   play_music(MUS_1)
        elif lvl==2: play_music(MUS_2)
        else:        play_music(MUS_3)

    

    reset(1)
    load_all_animations()   # ← lägg till denna rad




    # Fade-overlay
    fade_surf=pygame.Surface((SW,SH)); fade_surf.fill((0,0,0))

    running=True
    while running:
        clock.tick(FPS)
        mtick+=1; blink+=1; atick+=1
        mx,my=pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False

            # TRANSITION: blockera input
            if state==S_TRANS: continue

            if state==S_MENU:
                for b in mbtns: b.update(mx,my)
                if btn_play.clicked(ev):
                    state=S_NAME; ni=save_data.get("last_player",""); nc=len(ni)
                if btn_scores.clicked(ev): state=S_SCORES
                if btn_quit.clicked(ev): running=False
                if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE: running=False

            elif state==S_NAME:
                if ev.type==pygame.KEYDOWN:
                    if ev.key==pygame.K_RETURN and ni.strip():
                        pname[0]=ni.strip()
                        save_data["last_player"]=pname[0]; write_save(save_data)
                        reset(1); state=S_PLAY
                    elif ev.key==pygame.K_ESCAPE: state=S_MENU
                    elif ev.key==pygame.K_BACKSPACE:
                        if nc>0: ni=ni[:nc-1]+ni[nc:]; nc-=1
                    elif ev.key==pygame.K_LEFT:  nc=max(0,nc-1)
                    elif ev.key==pygame.K_RIGHT: nc=min(len(ni),nc+1)
                    elif len(ni)<18 and ev.unicode.isprintable() and ev.unicode:
                        ni=ni[:nc]+ev.unicode+ni[nc:]; nc+=1

            elif state==S_SCORES:
                btn_back.update(mx,my)
                if btn_back.clicked(ev) or (ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE):
                    state=S_MENU

            elif state==S_PLAY:
                if ev.type==pygame.KEYDOWN:
                    if ev.key==pygame.K_ESCAPE: state=S_MENU
                    if ev.key in(pygame.K_SPACE,pygame.K_w,pygame.K_UP):
                        jbuf=10   # jump buffer
                if ev.type==pygame.KEYUP:
                    if ev.key in(pygame.K_SPACE,pygame.K_w,pygame.K_UP): jheld=False

            elif state in(S_DEAD,S_WIN):
                if ev.type==pygame.KEYDOWN:
                    if ev.key==pygame.K_r:
                        if state==S_DEAD and checkpoint_pos:
                            reset(lvl,from_checkpoint=True)
                        else:
                            reset(lvl)
                        state=S_PLAY
                    if ev.key==pygame.K_ESCAPE: state=S_MENU

        # ═════════════════════════════════════
        #  SPEL-UPPDATERING
        # ═════════════════════════════════════
        if state==S_PLAY:
            gtime+=1; lava_wave+=0.04
            if dash_cd>0: dash_cd-=1
            if invincible>0: invincible-=1
            if jbuf>0: jbuf-=1
            if coyote>0: coyote-=1

            keys=pygame.key.get_pressed()
            tx=0.0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:  tx-=SPEED; fright=False
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: tx+=SPEED; fright=True

            # Dash
            if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and dash_cd==0 and not dashing:
                dashing=True; dash_dur=DASH_DUR; dash_cd=DASH_CD
                play_sfx(SND_DASH)
                spawn_dash_parts(parts,prect.centerx,prect.centery,vx)

            if dashing:
                dash_dur-=1
                vx=DASH_POWER*(1 if fright else -1)
                vy=min(vy,2)
                if dash_dur<=0:
                    dashing=False
                    spawn_dash_parts(parts,prect.centerx,prect.centery,vx)
            else:
                vx+=(tx-vx)*ACC; vx*=FRIC

            # Hopp (coyote + buffer)
            can_jump = on_gnd or coyote>0
            if jbuf>0 and (can_jump or djump_avail):
                if can_jump:
                    vy=JUMP; jbuf=0; jheld=True; jht=0; djump_avail=True
                    play_sfx(SND_JUMP)
                    pcols=LAVA_PART if lvl==3 else PART_COLS
                    spawn_parts(parts,prect.centerx,prect.bottom,12,cols=pcols)
                elif djump_avail:
                    vy=JUMP*0.88; jbuf=0; jheld=False; djump_avail=False
                    play_sfx(SND_DJUMP)
                    pcols=CAVE_PART if lvl==2 else (LAVA_PART if lvl==3 else PART_COLS)
                    spawn_parts(parts,prect.centerx,prect.centery,10,cols=pcols)

            if jheld:
                jht+=1
                if jht<14 and vy<0: vy-=0.62
                else: jheld=False

            keys2=pygame.key.get_pressed()
            if not any(keys2[k] for k in (pygame.K_SPACE,pygame.K_w,pygame.K_UP)): jheld=False

            vy=min(vy+GRAV,24)
            prect.x+=int(vx); prect.y+=int(vy)

            # ── Rörliga plattformar (nivå 3) ──
            all_collidable = list(plats)
            if lvl==3:
                for mp in moving_plats:
                    t2=atick*0.016*mp["spd"]+mp["phase"]
                    if mp["axis"]=="h":
                        mp["rect"].x=int(mp["ox"]+math.sin(t2)*mp["amp"])
                    else:
                        mp["rect"].y=int(mp["oy"]+math.sin(t2)*mp["amp"])
                    all_collidable.append(mp["rect"])

            # Kollision
            was_on=on_gnd; on_gnd=False
            for p in all_collidable:
                if prect.colliderect(p):
                    if vy>0 and prect.bottom-vy<=p.top+16:
                        prect.bottom=p.top; vy=0; on_gnd=True
                        coyote=6; djump_avail=True
                        if jst>1.05: jsq=0.68; play_sfx(SND_LAND)
                    elif vy<0: prect.top=p.bottom; vy=0
                    elif vx>0 and prect.right-abs(vx)<=p.left+8: prect.right=p.left; vx=0
                    elif vx<0 and prect.left+abs(vx)>=p.right-8: prect.left=p.right; vx=0

            if was_on and not on_gnd: coyote=6

            jsq+=(1.0-jsq)*0.20; jst+=(1.0-jst)*0.15


            # Animation uppdatering
            update_animation()


            # ── Lava-pooler (nivå 3) ──
            if lvl==3:
                lava_y=SH-60
                for lx,lw in LAVA_POOLS:
                    lr=pygame.Rect(lx,lava_y,lw,80)
                    if prect.colliderect(lr) and invincible==0:
                        lives-=1; invincible=90; play_sfx(SND_HIT)
                        spawn_parts(parts,prect.centerx,prect.bottom,16,cols=LAVA_PART)
                        if lives<=0:
                            play_sfx(SND_DEATH); stop_music()
                            add_score(save_data,pname[0],score,gtime); state=S_DEAD
                        else:
                            if checkpoint_pos: prect.topleft=checkpoint_pos
                            else: prect.topleft=(150,380)
                            vx=vy=0

            # ── Meteorer (nivå 3) ──
            if lvl==3 and not boss_fight:
                meteor_timer+=1
                if meteor_timer>=METEOR_SPAWN_RATE:
                    meteor_timer=0
                    mx3=int(cam_x)+random.randint(100,SW-100)
                    meteors.append({"x":float(mx3),"y":-30.0,
                                    "vx":random.uniform(-1.5,1.5),"vy":3.5,
                                    "r":random.randint(8,16),"warned":False})
                for m in meteors[:]:
                    m["x"]+=m["vx"]; m["y"]+=m["vy"]; m["vy"]+=0.12
                    mr=pygame.Rect(int(m["x"]-m["r"]),int(m["y"]-m["r"]),m["r"]*2,m["r"]*2)
                    # Krockar med plattform → exploderar
                    hit_plat=any(mr.colliderect(p) for p in all_collidable)
                    if hit_plat or m["y"]>SH:
                        spawn_parts(parts,m["x"],m["y"],10,cols=LAVA_PART)
                        meteors.remove(m); continue
                    # Krockar med spelare
                    if mr.colliderect(prect) and invincible==0:
                        lives-=1; invincible=90; play_sfx(SND_HIT)
                        spawn_parts(parts,prect.centerx,prect.centery,14,cols=LAVA_PART)
                        meteors.remove(m)
                        if lives<=0:
                            play_sfx(SND_DEATH); stop_music()
                            add_score(save_data,pname[0],score,gtime); state=S_DEAD
                        continue

            # ── Boss (nivå 3, slutet) ──
            if lvl==3:
                lp=plats[-1]
                # Starta boss när spelaren når sista plattformen
                if on_gnd and prect.right>lp.left+50 and not boss_fight and boss is None:
                    boss_fight=True; meteors.clear()
                    boss={"x":float(BOSS_START_X),"y":float(BOSS_Y),
                          "hp":3,"dir":-1.0,"spd":2.5,"tick":0,
                          "phase":0,"atk_timer":0,"hurt":0,
                          "charge":False,"charge_spd":0.0}
                    play_music(MUS_BOSS)

                if boss is not None and boss["hp"]>0:
                    boss["tick"]+=1; boss["atk_timer"]+=1
                    if boss["hurt"]>0: boss["hurt"]-=1

                    # Fas-baserat beteende
                    spd_mult=1.0+((3-boss["hp"])*0.4)
                    if not boss["charge"]:
                        boss["x"]+=boss["spd"]*boss["dir"]*spd_mult
                        # Vänd vid kanter av sista plattform
                        if boss["x"]>lp.right-60: boss["dir"]=-1.0
                        if boss["x"]<lp.left+60:  boss["dir"]=1.0
                        # Periodicisk laddning mot spelaren
                        if boss["atk_timer"]>int(120/spd_mult):
                            boss["atk_timer"]=0
                            boss["charge"]=True
                            dx=prect.centerx-boss["x"]
                            boss["charge_spd"]=8.0*spd_mult*(1 if dx>0 else -1)
                            # Kasta meteor vid fas 2+
                            if boss["hp"]<=2:
                                for _ in range(boss["hp"]):
                                    meteors.append({"x":boss["x"]+random.uniform(-40,40),
                                        "y":boss["y"]-20,"vx":random.uniform(-2,2),
                                        "vy":-4.0,"r":10,"warned":False})
                    else:
                        boss["x"]+=boss["charge_spd"]
                        if abs(boss["x"]-prect.centerx)<20 or boss["x"]<lp.left or boss["x"]>lp.right:
                            boss["charge"]=False

                    # Boss kolliderar med spelare
                    br=pygame.Rect(int(boss["x"]-40),int(boss["y"]-60),80,80)
                    if br.colliderect(prect) and invincible==0:
                        if prect.bottom<br.centery and vy>0:
                            # Studsa på boss → skada
                            boss["hp"]-=1; boss["hurt"]=40; vy=-15
                            spawn_parts(parts,boss["x"],boss["y"],18,cols=LAVA_PART)
                            play_sfx(SND_HIT)
                            if boss["hp"]<=0:
                                score+=500
                                play_sfx(SND_LEVEL); stop_music()
                                add_score(save_data,pname[0],score,gtime)
                                state=S_WIN
                        else:
                            lives-=1; invincible=90; play_sfx(SND_HIT)
                            spawn_parts(parts,prect.centerx,prect.centery,15)
                            if lives<=0:
                                play_sfx(SND_DEATH); stop_music()
                                add_score(save_data,pname[0],score,gtime); state=S_DEAD

            # ── Fiender ──
            for e in enemies[:]:
                e["tick"]+=1
                if e["knockback"]>0: e["knockback"]-=1; continue
                e["x"]+=e["spd"]*e["dir"]
                if e["x"]>e["patrol_x"]+e["patrol_w"] or e["x"]<e["patrol_x"]: e["dir"]*=-1
                er=pygame.Rect(int(e["x"]-e["w"]//2),int(e["y"]),e["w"],e["h"])
                if prect.colliderect(er) and invincible==0:
                    if prect.bottom<er.centery and vy>0:
                        enemies.remove(e); vy=-12; score+=30
                        ec=LAVA_PART if lvl==3 else ([(140,60,180),(180,80,220)] if lvl==2 else [(80,130,60),(120,180,80)])
                        spawn_parts(parts,e["x"],e["y"],12,cols=ec)
                        play_sfx(SND_COIN)
                    else:
                        lives-=1; invincible=90; play_sfx(SND_HIT)
                        spawn_parts(parts,prect.centerx,prect.centery,15)
                        if lives<=0:
                            play_sfx(SND_DEATH); stop_music()
                            add_score(save_data,pname[0],score,gtime); state=S_DEAD

            # Mynt
            for c in coins:
                if not c["collected"]:
                    cr=pygame.Rect(c["x"]-c["r"],c["y"]-c["r"],c["r"]*2,c["r"]*2)
                    if prect.colliderect(cr):
                        c["collected"]=True; score+=20
                        play_sfx(SND_COIN); spawn_parts(parts,c["x"],c["y"],8)

            # Checkpoints
            for i,cx2 in enumerate(checks):
                if prect.x>cx2 and not check_active[i]:
                    check_active[i]=True; checkpoint_pos=(prect.x,prect.y)

            # Fall ur banan
            if prect.top>SH+300:
                lives-=1; invincible=90; play_sfx(SND_HIT)
                if lives<=0:
                    play_sfx(SND_DEATH); stop_music()
                    add_score(save_data,pname[0],score,gtime); state=S_DEAD
                else:
                    prect.topleft=checkpoint_pos if checkpoint_pos else (150,380); vx=vy=0

            # Nivå-övergång (1→2→3) – bara om inte boss-nivå slutad
            if not boss_fight:
                lp=plats[-1]
                if on_gnd and prect.right>lp.left and prect.left<lp.right:
                    if lvl==1:
                        play_sfx(SND_LEVEL); stop_music()
                        score+=max(0,(300-gtime//FPS))*2
                        trans_dir=1; trans_alpha=0; trans_target=2
                        state=S_TRANS; checkpoint_pos=None
                    elif lvl==2:
                        play_sfx(SND_LEVEL); stop_music()
                        score+=max(0,(400-gtime//FPS))*2
                        trans_dir=1; trans_alpha=0; trans_target=3
                        state=S_TRANS; checkpoint_pos=None

            # Kamera
            tc=prect.centerx-SW//3
            cam_x+=(tc-cam_x)*0.11; cam_x=max(0.0,cam_x)

            # Moln
            for c in clouds:
                c["x"]-=c["speed"]
                if c["x"]+c["w"]<-20: c["x"]=float(SW+60); c["y"]=float(random.randint(50,220))

        # ─── Transition ───────────────────────────────
        if state==S_TRANS:
            if trans_dir==1:
                trans_alpha=min(255,trans_alpha+8)
                if trans_alpha>=255:
                    reset(trans_target); state=S_PLAY
                    trans_dir=-1
            else:
                trans_alpha=max(0,trans_alpha-8)

        # Meny-räv
        mfx+=2.5
        if mfx>SW+100: mfx=-80.0

        # ═════════════════════════════════════
        #  RITA
        # ═════════════════════════════════════
        if state==S_MENU:
            screen.blit(sky1,(0,0))
            pygame.draw.circle(screen,L1["sun"],(SW-130,100),56)
            pygame.draw.circle(screen,(255,245,160),(SW-130,100),70,7)
            pygame.draw.rect(screen,L1["grass_d"],(0,SH-110,SW,110))
            pygame.draw.rect(screen,L1["grass_l"],(0,SH-110,SW,14))
            for c in clouds: draw_cloud(screen,int(c["x"]-0),int(c["y"]),c["w"])
            # draw_fox(screen,int(mfx),SH-170,True,1.0,1.0,mtick,3)
            img = ANIMATIONS["idle"][0]
            screen.blit(img, (int(mfx), SH - 170))

            ov=pygame.Surface((680,260),pygame.SRCALPHA); ov.fill((10,8,40,178))
            screen.blit(ov,(SW//2-340,78))
            pygame.draw.rect(screen,GOLD,(SW//2-340,78,680,260),3,border_radius=16)
            sh2=ft.render("Luna the Fox",True,(70,35,0))
            tl=ft.render("Luna the Fox",True,GOLD)
            screen.blit(sh2,sh2.get_rect(center=(SW//2+3,183)))
            screen.blit(tl,tl.get_rect(center=(SW//2,180)))
            sub=fs.render("Hopp, mynt, fiender – 3 nivåer + boss!",True,(200,200,255))
            screen.blit(sub,sub.get_rect(center=(SW//2,290)))
            for b in mbtns: b.update(mx,my); b.draw(screen)
            ht=fti.render("A/D=ror  SPACE=hopp(2x)  SHIFT=dash  ESC=avsluta",True,(140,140,190))
            screen.blit(ht,ht.get_rect(center=(SW//2,SH-28)))

        elif state==S_NAME:
            screen.blit(sky1,(0,0))
            pygame.draw.circle(screen,L1["sun"],(SW-130,100),56)
            pygame.draw.rect(screen,L1["grass_d"],(0,SH-110,SW,110))
            pygame.draw.rect(screen,L1["grass_l"],(0,SH-110,SW,14))
            # draw_fox(screen,int(mfx),SH-170,True,1.0,1.0,mtick,3)
            # draw_fox(screen, int(mfx), SH-170)
            img = ANIMATIONS["idle"][0]
            screen.blit(img, (int(mfx), SH - 170))

            pn=pygame.Surface((640,300),pygame.SRCALPHA); pn.fill((10,8,45,190))
            px,py=SW//2-320,SH//2-170
            screen.blit(pn,(px,py))
            pygame.draw.rect(screen,GOLD,(px,py,640,300),3,border_radius=14)
            t1=fb.render("Vad heter du?",True,GOLD)
            screen.blit(t1,t1.get_rect(center=(SW//2,py+55)))
            fr=pygame.Rect(SW//2-230,py+105,460,58)
            pygame.draw.rect(screen,(18,18,55),fr,border_radius=10)
            pygame.draw.rect(screen,GOLD,fr,2,border_radius=10)
            disp=ni[:nc]+("_" if blink//30%2==0 else " ")+ni[nc:]
            ts=fm.render(disp,True,WHITE)
            screen.blit(ts,ts.get_rect(midleft=(fr.left+14,fr.centery)))
            h1=fs.render("Skriv ditt namn och tryck ENTER",True,(180,180,230))
            h2=fs.render("ESC = tillbaka",True,(130,130,180))
            screen.blit(h1,h1.get_rect(center=(SW//2,py+210)))
            screen.blit(h2,h2.get_rect(center=(SW//2,py+244)))
            if not ni.strip():
                w=fti.render("Ange ett namn for att fortsatta",True,(255,150,70))
                screen.blit(w,w.get_rect(center=(SW//2,py+274)))

        elif state==S_SCORES:
            screen.blit(sky1,(0,0))
            pygame.draw.circle(screen,L1["sun"],(SW-130,100),56)
            pygame.draw.rect(screen,L1["grass_d"],(0,SH-110,SW,110))
            pygame.draw.rect(screen,L1["grass_l"],(0,SH-110,SW,14))
            pn=pygame.Surface((720,510),pygame.SRCALPHA); pn.fill((8,8,38,192))
            px,py=SW//2-360,SH//2-265
            screen.blit(pn,(px,py))
            pygame.draw.rect(screen,GOLD,(px,py,720,510),3,border_radius=16)
            t1=fb.render("Topplista",True,GOLD)
            screen.blit(t1,t1.get_rect(center=(SW//2,py+44)))
            pygame.draw.line(screen,GOLD,(px+30,py+82),(px+690,py+82),2)
            hs=save_data.get("high_scores",[])
            meds=["Guld","Silver","Brons"]
            mcols=[GOLD,(200,200,200),(180,120,60)]
            for i,e in enumerate(hs[:8]):
                ry2=py+100+i*48
                mc=meds[i] if i<3 else f"{i+1}."
                cc=mcols[i] if i<3 else (170,170,200)
                row=f"{mc:<8}  {e['name']:<14}  {e['score']:<7}  {e['mins']:02d}:{e['secs']:02d}"
                screen.blit(fs.render(row,True,cc),(px+38,ry2))
            if not hs:
                ns=fs.render("Inga resultat – spela och satt rekord!",True,(160,160,210))
                screen.blit(ns,ns.get_rect(center=(SW//2,py+220)))
            btn_back.update(mx,my); btn_back.draw(screen)

        elif state in(S_PLAY,S_TRANS):
            pal=L1 if lvl==1 else (L2 if lvl==2 else L3)
            sky=sky1 if lvl==1 else (sky2 if lvl==2 else sky3)
            screen.blit(sky,(0,0))

            # Sol / måne / vulkan-glöd
            if lvl==1:
                pygame.draw.circle(screen,pal["sun"],(SW-130,95),54)
                pygame.draw.circle(screen,(255,245,160),(SW-130,95),68,7)
            elif lvl==2:
                pygame.draw.circle(screen,pal["sun"],(SW-130,95),38)
                pygame.draw.circle(screen,(30,20,50),(SW-115,80),38)
            else:
                # Vulkan: glödande röd sol med puls
                rpulse=int(54+math.sin(atick*0.05)*6)
                pygame.draw.circle(screen,(255,60,0),(SW-130,95),rpulse+10)
                pygame.draw.circle(screen,pal["sun"],(SW-130,95),rpulse)

            # Stjärnor
            bright=0.4 if lvl==1 else (1.4 if lvl==2 else 1.8)
            draw_stars(screen,stars,cam_x,atick,bright_base=bright)

            # Bakgrundsmoln / rök
            for c in clouds:
                col=pal["cloud"]
                draw_cloud(screen,int(c["x"]-cam_x*0.22),int(c["y"]),c["w"],col)

            # Nivå 2: fackle-glöd
            if lvl==2:
                for tx2,ty2 in TORCHES:
                    sx2=int(tx2-cam_x)
                    if -60<sx2<SW+60:
                        glow=pygame.Surface((140,140),pygame.SRCALPHA)
                        a2=int(70+math.sin(atick*0.18+tx2)*20)
                        pygame.draw.circle(glow,(255,140,30,a2),(70,70),70)
                        screen.blit(glow,(sx2-70,int(ty2)-70))

            # Nivå 3: lava-ljus-glöd underifrån
            if lvl==3:
                lava_overlay=pygame.Surface((SW,SH),pygame.SRCALPHA)
                pulse=int(30+math.sin(lava_wave)*15)
                pygame.draw.rect(lava_overlay,(255,60,0,pulse),(0,SH-120,SW,120))
                screen.blit(lava_overlay,(0,0))

            # Plattformar (statiska)
            for p in plats: draw_platform(screen,p,cam_x,lvl)

            # Rörliga plattformar (nivå 3) med glöd-kant
            if lvl==3:
                for mp in moving_plats:
                    draw_platform(screen,mp["rect"],cam_x,3)
                    # Extra glödkant på rörliga
                    dr=mp["rect"].copy(); dr.x-=int(cam_x)
                    if -30<dr.x<SW+30:
                        pygame.draw.rect(screen,(255,120,0),dr,3,border_radius=7)

            # Nivå 3: lava-pooler
            if lvl==3:
                lava_y=SH-60
                for lx,lw in LAVA_POOLS:
                    sx2=int(lx-cam_x)
                    if sx2>SW+20 or sx2+lw<-20: continue
                    # Animerad lava-yta
                    for xi in range(0,lw,12):
                        wave_h=int(math.sin(lava_wave+xi*0.3)*6)
                        col=LAVA_PART[xi%len(LAVA_PART)]
                        pygame.draw.rect(screen,col,(sx2+xi,lava_y+wave_h,12,60-wave_h))
                    # Glödlinje ovanpå
                    pygame.draw.line(screen,(255,230,80),(sx2,lava_y),(sx2+lw,lava_y),3)
                    # Lava-bubblor
                    if atick%20==int(lx)%20:
                        spawn_parts(parts,lx+random.randint(0,lw),lava_y,2,cols=LAVA_PART)

            # Facklor (nivå 2)
            if lvl==2:
                for tx2,ty2 in TORCHES: draw_torch(screen,tx2,ty2,cam_x,atick)

            # Checkpoints
            for i,cx2 in enumerate(checks):
                draw_checkpoint(screen,cx2-10,SH-140,cam_x,check_active[i])

            # Mynt
            draw_coins(screen,coins,cam_x,atick)

            # Meteorer (nivå 3)
            if lvl==3:
                for m in meteors:
                    sx2=int(m["x"]-cam_x); sy2=int(m["y"])
                    if -40<sx2<SW+40:
                        # Varnings-linje uppifrån om nära skärmen
                        if sy2<80:
                            pygame.draw.line(screen,(255,80,0),(sx2,0),(sx2,min(sy2,80)),2)
                        # Meteor-kropp
                        pygame.draw.circle(screen,ROCK_COL,(sx2,sy2),m["r"])
                        pygame.draw.circle(screen,(255,120,0),(sx2,sy2),m["r"],3)
                        # Eld-svans
                        for ti in range(4):
                            tx3=sx2-int(m["vx"])*(ti+1)*2
                            ty3=sy2-int(m["vy"])*(ti+1)*2
                            pygame.draw.circle(screen,LAVA_PART[ti%len(LAVA_PART)],(tx3,ty3),max(1,m["r"]-ti*2))

            # Fiender
            for e in enemies: draw_enemy(screen,e,cam_x,e["tick"])

            # Boss (nivå 3)
            if lvl==3 and boss is not None and boss["hp"]>0:
                bsx=int(boss["x"]-cam_x); bsy=int(boss["y"])
                if -100<bsx<SW+100:
                    # Blinkar när skadad
                    show_boss = not (boss["hurt"]>0 and (boss["tick"]//4)%2==1)
                    if show_boss:
                        # Boss-kropp – stor eldvardagsdemon
                        bcol=(220,40,0) if boss["hp"]==3 else ((180,20,0) if boss["hp"]==2 else (140,0,0))
                        # Kropp
                        pygame.draw.ellipse(screen,bcol,(bsx-40,bsy-55,80,70))
                        pygame.draw.ellipse(screen,(255,100,20),(bsx-30,bsy-40,60,40))
                        # Horn
                        pygame.draw.polygon(screen,bcol,[(bsx-20,bsy-55),(bsx-35,bsy-85),(bsx-10,bsy-60)])
                        pygame.draw.polygon(screen,bcol,[(bsx+20,bsy-55),(bsx+35,bsy-85),(bsx+10,bsy-60)])
                        # Ögon (glödande)
                        pygame.draw.circle(screen,(255,230,0),(bsx-12,bsy-40),8)
                        pygame.draw.circle(screen,(255,230,0),(bsx+12,bsy-40),8)
                        pygame.draw.circle(screen,(255,80,0),(bsx-12,bsy-40),4)
                        pygame.draw.circle(screen,(255,80,0),(bsx+12,bsy-40),4)
                        # Armar
                        pygame.draw.line(screen,bcol,(bsx-40,bsy-30),(bsx-70,bsy-10),12)
                        pygame.draw.line(screen,bcol,(bsx+40,bsy-30),(bsx+70,bsy-10),12)
                        # Klor
                        for cx3,cy3,dx3,dy3 in [(bsx-70,bsy-10,-8,8),(bsx-70,bsy-10,-14,4),(bsx-70,bsy-10,-6,-2)]:
                            pygame.draw.line(screen,bcol,(cx3,cy3),(cx3+dx3,cy3+dy3),3)
                        for cx3,cy3,dx3,dy3 in [(bsx+70,bsy-10,8,8),(bsx+70,bsy-10,14,4),(bsx+70,bsy-10,6,-2)]:
                            pygame.draw.line(screen,bcol,(cx3,cy3),(cx3+dx3,cy3+dy3),3)
                        # Ben
                        pygame.draw.rect(screen,bcol,(bsx-28,bsy+15,20,30),border_radius=5)
                        pygame.draw.rect(screen,bcol,(bsx+8,bsy+15,20,30),border_radius=5)
                    # Boss HP-bar
                    bw=200; bh=18
                    bx3=bsx-bw//2; by3=bsy-100
                    pygame.draw.rect(screen,(40,10,10),(bx3,by3,bw,bh),border_radius=5)
                    hfill=int(bw*boss["hp"]/3)
                    hcol=(220,40,0) if boss["hp"]==3 else ((180,20,0) if boss["hp"]==2 else (255,80,0))
                    pygame.draw.rect(screen,hcol,(bx3,by3,hfill,bh),border_radius=5)
                    pygame.draw.rect(screen,(255,120,0),(bx3,by3,bw,bh),2,border_radius=5)
                    bt=fti.render("BOSS",True,(255,200,50))
                    screen.blit(bt,(bsx-bt.get_width()//2,by3-18))
                    # Hop-hint
                    hh=fti.render("Hoppa pa bossen 3 ganger!",True,(255,220,100))
                    screen.blit(hh,hh.get_rect(center=(SW//2,SH-70)))

            # Partiklar
            update_parts(screen,parts,cam_x)


            # Räven
            # draw_fox(screen, prect.x - int(cam_x), prect.y, invincible > 0)
           
            menu_rect = pygame.Rect(int(mfx), SH - 170, 78, 105)
            draw_fox(screen, menu_rect, 0)

            # # Räven
            # draw_fox(screen,prect.x-int(cam_x),prect.y,
            #          fright,jsq,jst,atick,vx,invincible>0)

            # HUD
            draw_hud(screen,pname[0],score,gtime,lives,lvl,dash_cd,djump_avail)

            # Dash-text
            if dash_cd>0:
                dc=fs.render(f"DASH {dash_cd//10+1}s",True,(80,180,255))
                screen.blit(dc,(SW//2-dc.get_width()//2,SH-42))

            # Fade overlay (transition)
            if state==S_TRANS and trans_alpha>0:
                fade_surf.set_alpha(trans_alpha)
                screen.blit(fade_surf,(0,0))
                if trans_alpha>200:
                    lbl="NIVA 3 – VULKANEN!" if trans_target==3 else f"NIVA {trans_target}!"
                    msg=fb.render(lbl,True,GOLD)
                    screen.blit(msg,msg.get_rect(center=(SW//2,SH//2)))

        elif state==S_DEAD:
            screen.blit(sky1 if lvl==1 else (sky2 if lvl==2 else sky3),(0,0))
            ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,155)); screen.blit(ov,(0,0))
            t1=ft.render("Game Over",True,(230,60,60))
            screen.blit(t1,t1.get_rect(center=(SW//2,220)))
            t2=fb.render(f"Poang: {score}",True,GOLD)
            screen.blit(t2,t2.get_rect(center=(SW//2,325)))
            msg="R = Fran checkpoint" if checkpoint_pos else "R = Forsok igen"
            t3=fm.render(f"{msg}    ESC = Meny",True,WHITE)
            screen.blit(t3,t3.get_rect(center=(SW//2,410)))
            t4=fs.render(f"Liv kvar: {lives}",True,(200,200,200))
            screen.blit(t4,t4.get_rect(center=(SW//2,465)))

        elif state==S_WIN:
            screen.blit(sky1 if lvl==1 else (sky2 if lvl==2 else sky3),(0,0))
            ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,30,0,140)); screen.blit(ov,(0,0))
            t1=ft.render("Du klarade det!",True,GOLD)
            screen.blit(t1,t1.get_rect(center=(SW//2,190)))
            t2=fb.render(f"Poang: {score}",True,GOLD)
            screen.blit(t2,t2.get_rect(center=(SW//2,295)))
            t3=fm.render(f"Tid: {gtime//(FPS*60):02d}:{(gtime//FPS)%60:02d}",True,WHITE)
            screen.blit(t3,t3.get_rect(center=(SW//2,360)))
            # Mynt-statistik
            tot=len(coins); got=sum(1 for c in coins if c["collected"])
            t4=fm.render(f"Mynt: {got}/{tot}",True,GOLD)
            screen.blit(t4,t4.get_rect(center=(SW//2,415)))
            t5=fm.render("R = Spela igen    ESC = Meny",True,WHITE)
            screen.blit(t5,t5.get_rect(center=(SW//2,480)))
            # Stjärnor runt text
            for _ in range(2):
                sx2=random.randint(0,SW); sy2=random.randint(0,SH)
                pygame.draw.circle(screen,GOLD,(sx2,sy2),random.randint(2,5))

        pygame.display.flip()

    pygame.quit(); sys.exit()

if __name__=="__main__":
    main()