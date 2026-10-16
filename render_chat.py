from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib

OUT = Path("/tmp/generated")
OUT.mkdir(exist_ok=True)
WIDTH = 900
BG = (26, 29, 31)
HEADER = (20, 22, 24)
BUBBLE = (55, 63, 66)
USER_BUBBLE = (0, 104, 126)
WHITE = (232, 237, 239)
MUTED = (155, 165, 170)

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap_words(draw, text, fnt, max_width):
    lines, line = [], ""
    for word in text.split():
        test = word if not line else line + " " + word
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
            line = test
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines or [""]

def avatar_color(name):
    colors = [(126,90,170),(63,137,113),(176,104,68),(74,118,166),(159,83,103)]
    return colors[int(hashlib.md5(name.encode("utf-8")).hexdigest(),16) % len(colors)]

def render_chapter(story, chapter, number):
    path = OUT / f"{story['id']}_{number}.png"
    rows = chapter["messages"]
    body_font, name_font = font(25), font(20, True)
    dummy = Image.new("RGB", (WIDTH, 100), BG)
    d = ImageDraw.Draw(dummy)
    prepared, total_h = [], 118
    for msg in rows:
        lines = wrap_words(d, msg["text"], body_font, 650)
        bubble_h = 28 + len(lines) * 36
        prepared.append((msg, lines, bubble_h))
        total_h += 30 + 22 + bubble_h + 18
    img = Image.new("RGB", (WIDTH, min(total_h + 35, 4200)), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0,0,WIDTH,86), fill=HEADER)
    draw.text((32,24),"‹",font=font(42),fill=WHITE)
    draw.text((90,20),story["title"],font=font(27,True),fill=WHITE)
    draw.text((WIDTH-74,24),"•••",font=font(24,True),fill=MUTED)
    y = 106
    for msg, lines, bubble_h in prepared:
        is_user = msg.get("side") == "right"
        name = msg["name"]
        color = avatar_color(name)
        bubble_w = min(690, max(260, max(draw.textbbox((0,0), line, font=body_font)[2] for line in lines) + 42))
        bubble_x = WIDTH - 34 - bubble_w if is_user else 112
        cx, cy, r = (WIDTH-42 if is_user else 52), y+28, 27
        draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=color)
        initials = "".join(p[0] for p in name.split()[:2]).upper()
        ib = draw.textbbox((0,0),initials,font=font(18,True))
        draw.text((cx-(ib[2]-ib[0])/2,cy-(ib[3]-ib[1])/2-2),initials,font=font(18,True),fill=(255,255,255))
        draw.text((bubble_x+4,y),name,font=name_font,fill=color)
        by = y+28
        draw.rounded_rectangle((bubble_x,by,bubble_x+bubble_w,by+bubble_h),radius=26,fill=USER_BUBBLE if is_user else BUBBLE)
        ty = by+14
        for line in lines:
            draw.text((bubble_x+22,ty),line,font=body_font,fill=WHITE)
            ty += 36
        y = by+bubble_h+24
    img.save(path)
    return str(path)
