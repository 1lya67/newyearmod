#!/usr/bin/env python3
"""Генерирует текстуры, модели и данные мода (листва, ёлки, фонарики, иней на стёклах, наряды жителей).
Запускается из GitHub Actions перед сборкой: python tools/gen_assets.py
Локально:  python tools/gen_assets.py --preview  (сохранит картинки в папку preview/)"""
import os, sys, random, json, zlib, struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = ROOT + '/src/main/resources/assets'
DATA = ROOT + '/src/main/resources/data'
PREVIEW = '--preview' in sys.argv

# ================================================================ утилиты
def write_png(path, rows):
    h = len(rows); w = len(rows[0])
    raw = b''.join(b'\x00' + bytes(c for px in row for c in px) for row in rows)
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(data)

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def upscale(rows, scale):
    out = []
    for row in rows:
        r2 = [p for p in row for _ in range(scale)]
        out.extend([r2] * scale)
    return out

def over(src, dst):
    """alpha-композитинг src поверх dst (RGBA)."""
    sa = src[3] / 255.0; da = dst[3] / 255.0
    oa = sa + da * (1 - sa)
    if oa <= 0:
        return (0, 0, 0, 0)
    c = [int((src[i] * sa + dst[i] * da * (1 - sa)) / oa) for i in range(3)]
    return (c[0], c[1], c[2], int(oa * 255))

def preview_save(name, rows, scale):
    if PREVIEW:
        write_png(os.path.join(ROOT, 'preview', name), upscale(rows, scale))

# ================================================================ листва с шариками
SPECIES = {
    'oak':      [(46, 94, 30), (62, 120, 38), (80, 146, 48), (98, 168, 60)],
    'spruce':   [(30, 64, 44), (40, 82, 54), (52, 100, 66), (66, 118, 80)],
    'birch':    [(90, 124, 50), (108, 146, 58), (126, 166, 70), (146, 186, 84)],
    'jungle':   [(28, 104, 30), (38, 130, 36), (50, 154, 44), (66, 176, 56)],
    'acacia':   [(76, 104, 28), (96, 128, 34), (116, 150, 42), (136, 170, 54)],
    'dark_oak': [(30, 66, 28), (40, 86, 34), (52, 104, 42), (66, 124, 52)],
    'mangrove': [(56, 104, 38), (70, 124, 46), (86, 144, 54), (102, 162, 64)],
    'cherry':   [(214, 140, 172), (230, 162, 190), (244, 184, 208), (255, 208, 226)],
    'pale_oak': [(138, 150, 128), (156, 168, 146), (174, 186, 164), (192, 204, 182)],
}
# приглушённые цвета: (основной, блик, тень)
COL = {
    'red':    ((168, 44, 52),  (214, 120, 120), (104, 22, 32)),
    'gold':   ((196, 158, 62), (228, 205, 130), (130, 98, 34)),
    'blue':   ((62, 98, 176),  (130, 160, 214), (34, 56, 116)),
    'silver': ((176, 186, 200), (222, 228, 236), (104, 114, 134)),
    'pink':   ((186, 92, 148), (224, 150, 190), (116, 48, 92)),
    'orange': ((196, 112, 56), (228, 164, 110), (128, 64, 28)),
    'purple': ((116, 76, 160), (164, 132, 200), (70, 40, 106)),
    'teal':   ((52, 140, 140), (120, 190, 184), (28, 86, 92)),
    'cream':  ((216, 206, 180), (240, 234, 214), (148, 138, 112)),
}
COLOR_ORDER = ['red', 'gold', 'blue', 'silver', 'pink', 'orange', 'purple', 'teal', 'cream']
CAP = (190, 160, 70)
BALL = ["hb",     # совсем маленький шарик 2x2 + колпачок
        "bd"]
LAYOUTS = {
    'a': [(1, 2), (6, 1), (11, 2), (3, 7), (9, 7), (13, 8), (1, 12), (7, 12), (12, 12)],
    'b': [(3, 1), (9, 2), (14, 1), (0, 6), (6, 6), (12, 7), (2, 12), (8, 11), (13, 12)],
    'c': [(2, 3), (8, 1), (13, 4), (5, 7), (10, 8), (0, 10), (6, 12), (12, 12)],
    'd': [(1, 1), (5, 4), (10, 1), (14, 5), (2, 8), (8, 6), (12, 9), (5, 11), (10, 12)],
}
VARIANTS = {}
for k, (v, pos) in enumerate(LAYOUTS.items()):
    VARIANTS[v] = [(x, y, COLOR_ORDER[(i * 2 + k * 3) % len(COLOR_ORDER)]) for i, (x, y) in enumerate(pos)]

def check_layout(balls):
    cells = []
    for bx, by, _ in balls:
        assert 0 <= bx and bx + 1 <= 15 and by - 1 >= 0 and by + 1 <= 15, (bx, by)
        cells.append(set((bx + i, by + j) for i in range(2) for j in range(-1, 2)))
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            assert not (cells[i] & cells[j]), ('overlap', balls[i], balls[j])
for b in VARIANTS.values():
    check_layout(b)

def make_leaf(pal, balls, seed):
    rnd = random.Random(seed)
    weights = [0.22, 0.36, 0.28, 0.14]
    px = [[pal[rnd.choices(range(4), weights)[0]] + (255,) for _ in range(16)] for _ in range(16)]
    for _ in range(9):
        px[rnd.randrange(16)][rnd.randrange(16)] = (0, 0, 0, 0)
    ball = {}
    for bx, by, col in balls:
        m = dict(zip('bhd', COL[col]))
        for j, row in enumerate(BALL):
            for i, ch in enumerate(row):
                ball[(bx + i, by + j)] = m[ch] + (255,)
        ball[(bx, by - 1)] = CAP + (255,)
    shade = tuple(int(c * 0.6) for c in pal[0]) + (255,)
    for (x, y) in list(ball):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 16 and 0 <= ny < 16 and (nx, ny) not in ball:
                px[ny][nx] = shade
    for (x, y), c in ball.items():
        px[y][x] = c
    placed = 0
    while placed < 3:
        x, y = rnd.randrange(16), rnd.randrange(16)
        if (x, y) in ball or px[y][x][3] == 0 or px[y][x] == shade:
            continue
        px[y][x] = (206, 222, 232, 255)
        placed += 1
    return px

previews = {}
for sp, pal in SPECIES.items():
    name = f'{sp}_leaves'
    for k, (v, balls) in enumerate(VARIANTS.items()):
        tex = make_leaf(pal, balls, 100 * (k + 1) + len(sp))
        write_png(f'{RES}/newyear/textures/block/{name}_{v}.png', tex)
        previews[(sp, v)] = tex
        write_json(f'{RES}/newyear/models/block/{name}_{v}.json', {
            "parent": "minecraft:block/cube_all", "textures": {"all": f"newyear:block/{name}_{v}"}})
    write_json(f'{RES}/minecraft/models/block/{name}.json', {
        "parent": "minecraft:block/cube_all", "textures": {"all": f"newyear:block/{name}_a"}})
    variants = []
    for v in VARIANTS:
        for y in (0, 90, 180, 270):
            e = {"model": f"newyear:block/{name}_{v}"}
            if y:
                e["y"] = y
            variants.append(e)
    write_json(f'{RES}/minecraft/blockstates/{name}.json', {"variants": {"": variants}})

if PREVIEW:
    bg = (28, 28, 34, 255); rows = []
    for ty in range(2):
        for y in range(16):
            row = []
            for v in VARIANTS:
                for tx in range(2):
                    for x in range(16):
                        p = previews[('oak', v)][y][x]
                        row.append(p if p[3] else bg)
                row.extend([bg] * 4)
            rows.append(row)
    preview_save('leaves.png', rows, 5)

# ================================================================ ёлки
def box(name, frm, to, side, top=None, bottom=None, skip=()):
    faces = {"north": {"texture": "#" + side}, "east": {"texture": "#" + side},
             "south": {"texture": "#" + side}, "west": {"texture": "#" + side},
             "up": {"texture": "#" + (top or side)}, "down": {"texture": "#" + (bottom or side)}}
    for s in skip:
        faces.pop(s)
    return {"name": name, "from": frm, "to": to, "faces": faces}

TREE_TEXTURES = {
    "particle": "newyear:block/spruce_leaves_c", "leaves": "newyear:block/spruce_leaves_c",
    "log": "minecraft:block/spruce_log", "log_top": "minecraft:block/spruce_log_top",
    "star": "minecraft:block/gold_block",
    "red": "minecraft:block/red_wool", "blue": "minecraft:block/blue_wool",
    "green": "minecraft:block/lime_wool", "white": "minecraft:block/white_wool"}

def gift(name, x, z, w, h, d, tex):
    return [box(name, [x, 0, z], [x + w, h, z + d], tex),
            box(name + "_r1", [x + w / 2 - 0.5, 0, z - 0.1], [x + w / 2 + 0.5, h + 0.1, z + d + 0.1], "white"),
            box(name + "_r2", [x - 0.1, 0, z + d / 2 - 0.5], [x + w + 0.1, h + 0.1, z + d / 2 + 0.5], "white")]

# --- маленькая (1 блок)
small = [box("trunk", [7, 0, 7], [9, 3, 9], "log", "log_top", "log_top"),
         box("tier1", [2, 2, 2], [14, 5, 14], "leaves"), box("tier2", [3.5, 5, 3.5], [12.5, 8, 12.5], "leaves"),
         box("tier3", [5, 8, 5], [11, 11, 11], "leaves"), box("tier4", [6.5, 11, 6.5], [9.5, 14, 9.5], "leaves"),
         box("star", [7, 14, 7], [9, 16, 9], "star")]
small += gift("gift_red", 1, 1, 3, 2.5, 3, "red") + gift("gift_blue", 11.5, 1.5, 3, 2, 3, "blue") \
         + gift("gift_green", 10, 11, 3, 3, 3, "green")
write_json(f'{RES}/newyear/models/block/new_year_tree.json',
           {"parent": "minecraft:block/block", "textures": TREE_TEXTURES, "elements": small})
write_json(f'{RES}/newyear/blockstates/new_year_tree.json', {"variants": {"": {"model": "newyear:block/new_year_tree"}}})
write_json(f'{RES}/newyear/items/new_year_tree.json', {"model": {"type": "minecraft:model", "model": "newyear:block/new_year_tree"}})

# --- большая (2 блока, ~1.9 блока в высоту: ниже стойки для брони)
BIG_BOXES = [  # name, from, to, side, top, bottom
    ("trunk", [7, 0, 7], [9, 4, 9], "log", "log_top", "log_top"),
    ("tier1", [1, 3, 1], [15, 7, 15], "leaves", None, None),
    ("tier2", [2.5, 7, 2.5], [13.5, 11, 13.5], "leaves", None, None),
    ("tier3", [4, 11, 4], [12, 15, 12], "leaves", None, None),
    ("tier4", [5, 15, 5], [11, 19, 11], "leaves", None, None),
    ("tier5", [6, 19, 6], [10, 23, 10], "leaves", None, None),
    ("tier6", [7, 23, 7], [9, 27, 9], "leaves", None, None),
    ("star", [6.5, 27, 6.5], [9.5, 30, 9.5], "star", None, None)]
lower, upper, full = [], [], []
for (n, f, t, side, top, bot) in BIG_BOXES:
    full.append(box(n, f, t, side, top, bot))
    if f[1] < 16:
        lower.append(box(n, f, [t[0], min(t[1], 16), t[2]], side, top, bot, skip=("up",) if t[1] > 16 else ()))
    if t[1] > 16:
        upper.append(box(n, [f[0], max(f[1], 16) - 16, f[2]], [t[0], t[1] - 16, t[2]], side, top, bot,
                         skip=("down",) if f[1] < 16 else ()))
gifts_big = gift("gift_red", 0.5, 0.5, 4, 3, 4, "red") + gift("gift_blue", 11, 1, 4, 2.5, 4, "blue") \
            + gift("gift_green", 10.5, 11, 4, 3.5, 4, "green")
lower += gifts_big
full += gifts_big
write_json(f'{RES}/newyear/models/block/new_year_tree_big_lower.json',
           {"parent": "minecraft:block/block", "textures": TREE_TEXTURES, "elements": lower})
write_json(f'{RES}/newyear/models/block/new_year_tree_big_upper.json',
           {"parent": "minecraft:block/block", "textures": TREE_TEXTURES, "elements": upper})
write_json(f'{RES}/newyear/models/item/new_year_tree_big.json', {
    "parent": "minecraft:block/block", "textures": TREE_TEXTURES, "elements": full,
    "display": {
        "gui": {"rotation": [30, 225, 0], "translation": [0, -2.6, 0], "scale": [0.33, 0.33, 0.33]},
        "ground": {"rotation": [0, 0, 0], "translation": [0, 1.5, 0], "scale": [0.2, 0.2, 0.2]},
        "fixed": {"rotation": [0, 0, 0], "translation": [0, -2.3, 0], "scale": [0.3, 0.3, 0.3]},
        "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 1.5, 0], "scale": [0.2, 0.2, 0.2]},
        "thirdperson_lefthand": {"rotation": [75, 45, 0], "translation": [0, 1.5, 0], "scale": [0.2, 0.2, 0.2]},
        "firstperson_righthand": {"rotation": [0, 45, 0], "translation": [0, 0, 0], "scale": [0.22, 0.22, 0.22]},
        "firstperson_lefthand": {"rotation": [0, 225, 0], "translation": [0, 0, 0], "scale": [0.22, 0.22, 0.22]}}})
write_json(f'{RES}/newyear/blockstates/new_year_tree_big.json', {"variants": {
    "half=lower": {"model": "newyear:block/new_year_tree_big_lower"},
    "half=upper": {"model": "newyear:block/new_year_tree_big_upper"}}})
write_json(f'{RES}/newyear/items/new_year_tree_big.json', {"model": {"type": "minecraft:model", "model": "newyear:item/new_year_tree_big"}})

# ================================================================ фонарики
LANTERNS = {  # цвет: (основной, блик, тёмный, краситель)
    'red':   ((200, 42, 52),  (255, 130, 120), (120, 18, 28), 'red_dye',    'красный',  'Red'),
    'blue':  ((56, 108, 214), (150, 200, 255), (28, 56, 130), 'blue_dye',   'синий',    'Blue'),
    'green': ((46, 154, 84),  (140, 230, 150), (22, 94, 48),  'green_dye',  'зелёный',  'Green'),
    'gold':  ((236, 184, 54), (255, 236, 150), (150, 100, 20), 'yellow_dye', 'золотой', 'Gold'),
}
GOLD = [(222, 178, 66), (240, 204, 96), (176, 132, 40), (132, 96, 28)]

def lantern_texture(base, hi, dark, seed):
    rnd = random.Random(seed)
    img = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
    for y in range(8):          # золотой металл (0..7, 0..7)
        for x in range(8):
            c = GOLD[0]
            if (x + y) % 5 == 0: c = GOLD[1]
            if x in (0, 7) or y in (0, 7): c = GOLD[2]
            if x == 7 and y == 7: c = GOLD[3]
            img[y][x] = c + (255,)
    for y in range(7):          # стекло фонарика (8..14, 0..6)
        for x in range(7):
            dx = abs(x - 3) / 3.0; dy = abs(y - 3) / 3.0
            k = 1.0 - 0.55 * max(dx, dy) ** 1.5
            c = tuple(min(255, int(base[i] * (0.62 + 0.55 * k) + hi[i] * 0.15 * k)) for i in range(3))
            if x in (0, 6) or y in (0, 6): c = dark
            img[y][8 + x] = c + (255,)
    flake = [(3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (1, 3), (2, 3), (4, 3), (5, 3), (2, 2), (4, 2), (2, 4), (4, 4)]
    for (x, y) in flake:
        img[y][8 + x] = (250, 244, 232, 255)
    for _ in range(4):          # искорки
        x, y = rnd.randrange(1, 6), rnd.randrange(1, 6)
        if img[y][8 + x] != (250, 244, 232, 255):
            img[y][8 + x] = tuple(min(255, c + 60) for c in hi) + (255,)
    return img

def lantern_elements(dy, hanging):
    def el(name, frm, to, side_uv, cap_uv):
        faces = {s: {"uv": side_uv, "texture": "#tex"} for s in ("north", "east", "south", "west")}
        faces["up"] = {"uv": cap_uv, "texture": "#tex"}; faces["down"] = {"uv": cap_uv, "texture": "#tex"}
        return {"name": name, "from": [frm[0], frm[1] + dy, frm[2]], "to": [to[0], to[1] + dy, to[2]], "faces": faces}
    els = [el("cap_bottom", [5.5, 0, 5.5], [10.5, 1, 10.5], [0, 0, 5, 1], [0, 0, 5, 5]),
           el("glass", [4.5, 1, 4.5], [11.5, 8, 11.5], [8, 0, 15, 7], [0, 0, 7, 7]),
           el("cap_top", [5.5, 8, 5.5], [10.5, 9, 10.5], [0, 0, 5, 1], [0, 0, 5, 5]),
           el("knob", [7, 9, 7], [9, 10, 9], [0, 0, 2, 1], [0, 0, 2, 2]),
           el("ring", [7.25, 10, 7.25], [8.75, 11, 8.75], [0, 0, 2, 1], [0, 0, 2, 2])]
    if hanging:
        els.append({"name": "hook", "from": [7.5, 15, 7.5], "to": [8.5, 16, 8.5],
                    "faces": {s: {"uv": [0, 0, 1, 1], "texture": "#tex"} for s in ("north", "east", "south", "west", "up", "down")}})
    return els

lantern_tex_prev = []
for i, (c, (base, hi, dark, dye, ru, en)) in enumerate(LANTERNS.items()):
    name = f'new_year_lantern_{c}'
    tex = lantern_texture(base, hi, dark, 7 + i)
    lantern_tex_prev.append(tex)
    write_png(f'{RES}/newyear/textures/block/{name}.png', tex)
    for suffix, dy, hang in (('', 0, False), ('_hanging', 4, True)):
        write_json(f'{RES}/newyear/models/block/{name}{suffix}.json', {
            "parent": "minecraft:block/block", "textures": {"tex": f"newyear:block/{name}", "particle": f"newyear:block/{name}"},
            "elements": lantern_elements(dy, hang)})
    write_json(f'{RES}/newyear/blockstates/{name}.json', {"variants": {
        "hanging=false": {"model": f"newyear:block/{name}"}, "hanging=true": {"model": f"newyear:block/{name}_hanging"}}})
    write_json(f'{RES}/newyear/items/{name}.json', {"model": {"type": "minecraft:model", "model": f"newyear:block/{name}"}})
    write_json(f'{DATA}/newyear/recipe/{name}.json', {
        "type": "minecraft:crafting_shapeless", "category": "misc",
        "ingredients": ["minecraft:lantern", f"minecraft:{dye}"],
        "result": {"id": f"newyear:{name}", "count": 1}})

# ================================================================ лут, рецепты, перевод
def loot_simple(name):
    write_json(f'{DATA}/newyear/loot_table/blocks/{name}.json', {
        "type": "minecraft:block",
        "pools": [{"rolls": 1.0, "bonus_rolls": 0.0,
                   "entries": [{"type": "minecraft:item", "name": f"newyear:{name}"}],
                   "conditions": [{"condition": "minecraft:survives_explosion"}]}],
        "random_sequence": f"newyear:blocks/{name}"})

loot_simple('new_year_tree')
for c in LANTERNS:
    loot_simple(f'new_year_lantern_{c}')
write_json(f'{DATA}/newyear/loot_table/blocks/new_year_tree_big.json', {
    "type": "minecraft:block",
    "pools": [{"rolls": 1.0, "bonus_rolls": 0.0,
               "entries": [{"type": "minecraft:item", "name": "newyear:new_year_tree_big"}],
               "conditions": [{"condition": "minecraft:block_state_property", "block": "newyear:new_year_tree_big",
                               "properties": {"half": "lower"}},
                              {"condition": "minecraft:survives_explosion"}]}],
    "random_sequence": "newyear:blocks/new_year_tree_big"})

write_json(f'{DATA}/newyear/recipe/new_year_tree.json', {
    "type": "minecraft:crafting_shapeless", "category": "misc",
    "ingredients": ["minecraft:spruce_sapling", "minecraft:red_dye", "minecraft:blue_dye", "minecraft:yellow_dye"],
    "result": {"id": "newyear:new_year_tree", "count": 1}})
write_json(f'{DATA}/newyear/recipe/new_year_tree_big.json', {
    "type": "minecraft:crafting_shaped", "category": "misc",
    "pattern": ["T", "T"], "key": {"T": "newyear:new_year_tree"},
    "result": {"id": "newyear:new_year_tree_big", "count": 1}})

ru = {"new_year_tree": "Новогодняя ёлка", "new_year_tree_big": "Новогодняя ёлка (большая)"}
en = {"new_year_tree": "New Year Tree", "new_year_tree_big": "New Year Tree (Big)"}
for c, (_, _, _, _, rn, en_n) in LANTERNS.items():
    ru[f"new_year_lantern_{c}"] = f"Новогодний фонарик ({rn})"
    en[f"new_year_lantern_{c}"] = f"New Year Lantern ({en_n})"
for lang, d in (('ru_ru', ru), ('en_us', en)):
    out = {}
    for k, v in d.items():
        out[f"block.newyear.{k}"] = v
        out[f"item.newyear.{k}"] = v
    write_json(f'{RES}/newyear/lang/{lang}.json', out)

# ================================================================ наряды жителей
def faces(u, v, w, h, d):
    return {'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d),
            'right': (u, v + d, d, h), 'front': (u + d, v + d, w, h),
            'left': (u + d + w, v + d, d, h), 'back': (u + 2 * d + w, v + d, w, h)}

JACKET = faces(0, 38, 8, 18, 6); ARM = faces(44, 22, 4, 8, 4); HAND = faces(40, 38, 8, 4, 4)
HAT = faces(32, 0, 8, 10, 8); LEG = faces(0, 22, 4, 12, 4)

def O(coat, coat2, trim, belt, buckle, hat, hat2, scarf, scarf2, pattern, accent):
    return dict(coat=coat, coat2=coat2, trim=trim, belt=belt, buckle=buckle, hat=hat, hat2=hat2,
                scarf=scarf, scarf2=scarf2, pattern=pattern, accent=accent)

W = (246, 246, 246); RED = (196, 36, 44); GOLDC = (232, 200, 80)
OUTFITS = {
 'armorer':      O((98,104,116), (78,84,96),  (226,230,238), (40,40,46),  GOLDC, RED, (236,240,246), RED, (236,240,246), 'studs', (196,202,214)),
 'butcher':      O((176,34,44),  (140,22,34), W, (60,36,30),  GOLDC, W, RED, (40,130,70), W, 'apron', W),
 'cartographer': O((44,76,150),  (30,56,120), (244,238,214), (110,76,44), (232,196,76), (44,76,150), (232,196,76), (244,238,214), RED, 'stars', (236,200,80)),
 'cleric':       O((112,52,152), (84,36,122), (236,200,84), (236,200,84), (255,240,170), (112,52,152), (236,200,84), (236,200,84), (112,52,152), 'stars', (255,236,150)),
 'farmer':       O((188,42,42),  (110,24,24), W, (92,60,36), GOLDC, (46,128,64), W, (46,128,64), W, 'plaid', W),
 'fisherman':    O((30,92,128),  (22,70,104), W, (230,150,40), W, (230,128,40), W, W, (52,130,190), 'waves', (120,190,235)),
 'fletcher':     O((44,112,60),  (30,86,44),  (240,236,214), (100,66,36), GOLDC, (44,112,60), RED, RED, (240,236,214), 'dots', (240,236,214)),
 'leatherworker':O((122,74,42),  (96,56,30),  (238,226,196), (50,34,24), (210,180,90), (176,96,48), (238,226,196), RED, (238,226,196), 'stitch', (238,226,196)),
 'librarian':    O((214,228,248),(170,196,232), W, (40,64,128), GOLDC, (60,100,180), W, (40,64,128), W, 'snow', (70,110,190)),
 'mason':        O((138,138,144),(108,108,116), W, (70,70,76), (210,210,220), (212,98,40), W, (212,98,40), W, 'bricks', (108,108,116)),
 'nitwit':       O((44,150,72),  RED, W, RED, (255,230,90), RED, W, (255,214,70), RED, 'stripes', W),
 'shepherd':     O((244,240,226),(196,176,150), W, (110,76,44), GOLDC, RED, W, RED, W, 'wool', (176,150,120)),
 'toolsmith':    O((206,112,44), (168,84,30), (240,230,205), (50,50,56), (210,210,220), (70,70,78), (206,112,44), (70,70,78), (206,112,44), 'studs', (236,160,90)),
 'weaponsmith':  O((52,52,62),   (36,36,44),  RED, (120,24,24), GOLDC, (40,40,48), RED, RED, (40,40,48), 'dots', (236,120,40)),
}
# "базовый" праздничный наряд для безработных жителей по типам биомов (слой type/)
TYPE_OUTFITS = {
 'plains':  O((190,40,48),  (150,28,38), W, (40,30,30), GOLDC, RED, W, (46,140,70), W, 'plain', W),
 'desert':  O((206,156,62), (170,120,44), (250,240,220), (90,60,30), GOLDC, RED, W, RED, (250,240,220), 'dots', (250,240,220)),
 'jungle':  O((50,140,70),  (36,110,54), (240,236,214), (90,60,30), GOLDC, RED, W, (240,200,60), RED, 'dots', (240,236,214)),
 'savanna': O((210,120,50), (176,92,34), (240,230,205), (80,50,30), GOLDC, RED, W, (110,70,40), W, 'plain', W),
 'snow':    O((70,110,190), (50,84,150), W, (40,40,60), (210,210,225), W, (70,110,190), RED, W, 'snow', (170,200,240)),
 'swamp':   O((50,120,110), (36,92,86), (230,240,226), (50,40,30), GOLDC, (36,92,86), RED, (130,70,150), W, 'dots', (230,240,226)),
 'taiga':   O((130,86,52),  (100,64,38), (238,226,196), (50,34,24), GOLDC, RED, W, (46,130,64), W, 'stitch', (238,226,196)),
}

def pattern(sp, x, y, w, h):
    c, c2, ac, p = sp['coat'], sp['coat2'], sp['accent'], sp['pattern']
    if p == 'plain': return c
    if p == 'plaid':
        col = c2 if ((x % 4) < 2) != ((y % 4) < 2) else c
        return ac if (x % 8 == 0 or y % 8 == 0) else col
    if p == 'stripes': return c if (x % 4) < 2 else c2
    if p == 'waves': return c if (y % 4) < 2 else c2 if (y % 4) == 2 else ac if (x + y) % 3 == 0 else c2
    if p == 'studs': return ac if (x % 3 == 1 and y % 4 == 1) else (c if (y % 2) else c2)
    if p == 'dots': return ac if (x * 7 + y * 13) % 11 == 0 else c
    if p == 'stitch': return ac if (y % 3 != 2 and (x % 4) == 0) else c
    if p == 'bricks':
        off = 3 if (y // 3) % 2 else 0
        return ac if (y % 3 == 2 or (x + off) % 6 == 0) else c
    if p == 'wool': return ac if (x * 5 + y * 3) % 9 == 0 else c
    if p in ('stars', 'snow'):
        cy = (y // 6) * 6 + 3; shift = 2 if (y // 6) % 2 else 0
        cx = ((x + shift) // 5) * 5 + 2 - shift
        if abs(x - cx) + abs(y - cy) <= 1: return ac
        return c if (x + y) % 5 else c2
    if p == 'apron':
        if 1 <= x <= w - 2 and y >= 4: return sp['trim'] if (x + y) % 5 else (232, 214, 214)
        return c
    return c

def rect_iter(r):
    x0, y0, w, h = r
    for yy in range(h):
        for xx in range(w):
            yield x0 + xx, y0 + yy, xx, yy

def paint_outfit(sp):
    img = [[(0, 0, 0, 0)] * 64 for _ in range(64)]
    def put(px, py, col): img[py][px] = tuple(col) + (255,)
    for fname, r in JACKET.items():
        w, h = r[2], r[3]
        for px, py, x, y in rect_iter(r):
            col = pattern(sp, x, y, w, h)
            if fname in ('right', 'front', 'left', 'back'):
                if y >= h - 2: col = sp['trim']
                if y in (9, 10): col = sp['belt']
                if fname == 'front' and x in (w // 2 - 1, w // 2):
                    if y in (9, 10): col = sp['buckle']
                    elif y >= 2: col = sp['trim']
                if y in (0, 1): col = sp['scarf'] if ((x // 2) % 2 == 0) else sp['scarf2']
            put(px, py, col)
    for fname, r in ARM.items():
        w, h = r[2], r[3]
        for px, py, x, y in rect_iter(r):
            col = pattern(sp, x, y, w, h)
            if fname in ('right', 'front', 'left', 'back') and y >= h - 2: col = sp['trim']
            put(px, py, col)
    for fname, r in HAND.items():
        for px, py, x, y in rect_iter(r):
            put(px, py, sp['trim'] if (x + y) % 4 else (225, 225, 235))
    for fname, r in HAT.items():
        if fname == 'bottom': continue
        for px, py, x, y in rect_iter(r):
            if fname == 'top':
                put(px, py, (255, 255, 255) if (3 <= x <= 4 and 3 <= y <= 4) else sp['hat']); continue
            limit = {'front': 3, 'left': 4, 'right': 4, 'back': 6}[fname]
            if y < limit - 1:
                put(px, py, sp['hat'] if ((x + y) % 4 > 1 or sp['pattern'] != 'stripes') else sp['hat2'])
            elif y == limit - 1:
                put(px, py, sp['hat2'])
    for fname, r in LEG.items():
        if fname in ('top', 'bottom'): continue
        for px, py, x, y in rect_iter(r):
            if y >= 9: put(px, py, sp['belt'])
            elif y >= 6: put(px, py, sp['coat2'])
    return img

for name, sp in OUTFITS.items():
    write_png(f'{RES}/minecraft/textures/entity/villager/profession/{name}.png', paint_outfit(sp))
for name, sp in TYPE_OUTFITS.items():
    write_png(f'{RES}/minecraft/textures/entity/villager/type/{name}.png', paint_outfit(sp))

if PREVIEW:
    names = list(OUTFITS) + ['type:' + n for n in TYPE_OUTFITS]
    cols = 7; cell = 68; nrows = (len(names) + cols - 1) // cols
    canvas = [[(40, 40, 48, 255)] * (cols * cell) for _ in range(nrows * cell)]
    for i, n in enumerate(names):
        img = paint_outfit(TYPE_OUTFITS[n[5:]] if n.startswith('type:') else OUTFITS[n])
        ox = (i % cols) * cell; oy = (i // cols) * cell
        for y in range(64):
            for x in range(64):
                if img[y][x][3]: canvas[oy + y][ox + x] = img[y][x]
    preview_save('villagers.png', canvas, 2)

# ================================================================ иней на стёклах
GLASS = {'white': (240, 240, 240), 'orange': (216, 127, 51), 'magenta': (178, 76, 216), 'light_blue': (102, 153, 216),
         'yellow': (229, 229, 51), 'lime': (127, 204, 25), 'pink': (242, 127, 165), 'gray': (76, 76, 76),
         'light_gray': (153, 153, 153), 'cyan': (76, 127, 153), 'purple': (127, 63, 178), 'blue': (51, 76, 178),
         'brown': (102, 76, 51), 'green': (102, 127, 51), 'red': (153, 51, 51), 'black': (25, 25, 25)}
FROST = [(238, 250, 255), (214, 236, 250), (192, 222, 244)]

def frosted_glass(tint, seed):
    rnd = random.Random(seed)
    img = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
    if tint:
        img = [[tuple(tint) + (150,) for _ in range(16)] for _ in range(16)]
    def blend(x, y, rgba):
        if 0 <= x < 16 and 0 <= y < 16:
            img[y][x] = over(rgba, img[y][x])
    for y in range(16):
        for x in range(16):
            d = min(x, y, 15 - x, 15 - y)
            if d == 0: a = 255
            elif d == 1: a = 215
            elif d == 2: a = 150 if rnd.random() < 0.8 else 80
            elif d == 3: a = 90 if rnd.random() < 0.5 else 0
            else: a = 60 if rnd.random() < 0.16 else 0
            if a:
                blend(x, y, rnd.choice(FROST) + (a,))
    for (cx, cy, sx, sy) in ((0, 0, 1, 1), (15, 0, -1, 1), (0, 15, 1, -1), (15, 15, -1, -1)):
        for i in range(1, 5):                       # ветка инея из угла
            blend(cx + sx * i, cy + sy * i, (250, 254, 255, 255))
            if i in (2,):
                blend(cx + sx * (i + 1), cy + sy * (i - 1), (240, 250, 255, 235))
                blend(cx + sx * (i - 1), cy + sy * (i + 1), (240, 250, 255, 235))
                blend(cx + sx * (i + 2), cy + sy * (i - 1), (225, 244, 252, 190))
                blend(cx + sx * (i - 1), cy + sy * (i + 2), (225, 244, 252, 190))
    for _ in range(6):                              # блёстки
        blend(rnd.randrange(3, 13), rnd.randrange(3, 13), (255, 255, 255, 150))
    return img

def frosted_pane_top(tint, seed):
    rnd = random.Random(seed)
    img = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
    for y in range(16):
        for x in (7, 8):
            base = tuple(tint) + (255,) if tint else (200, 214, 224, 255)
            img[y][x] = over(rnd.choice(FROST) + (225 if rnd.random() < 0.75 else 150,), base)
    return img

TEX = f'{RES}/minecraft/textures/block'
write_png(f'{TEX}/glass.png', frosted_glass(None, 1))
write_png(f'{TEX}/glass_pane_top.png', frosted_pane_top(None, 2))
glass_prev = [frosted_glass(None, 1)]
for i, (c, rgb) in enumerate(GLASS.items()):
    write_png(f'{TEX}/{c}_stained_glass.png', frosted_glass(rgb, 10 + i))
    write_png(f'{TEX}/{c}_stained_glass_pane_top.png', frosted_pane_top(rgb, 40 + i))
    if c in ('red', 'light_blue', 'green'):
        glass_prev.append(frosted_glass(rgb, 10 + i))
if PREVIEW:
    bg = (70, 120, 70, 255); rows = []
    for y in range(16):
        row = []
        for t in glass_prev:
            for x in range(16):
                row.append(over(t[y][x], bg))
            row.extend([(30, 30, 30, 255)] * 2)
        rows.append(row)
    preview_save('glass.png', rows, 8)
    rows = []
    for y in range(16):
        row = []
        for t in lantern_tex_prev:
            row.extend(t[y]); row.extend([(30, 30, 30, 255)] * 2)
        rows.append([p if p[3] else (30, 30, 30, 255) for p in row])
    preview_save('lanterns.png', rows, 6)

print('assets generated')
