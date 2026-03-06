"""
Thumbnail generator for Kenshin Anime Bot.
Layout (1280x720):
  - Full blurred + darkened background
  - Left: Phone mockup with character image (portrait)
  - Right: Anime panel with dark overlay + title + branding
  - Bottom: Two styled buttons (WATCH NOW | KENSHIN ANIME)
"""

import io
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 1280, 720

# ── Phone mockup ──────────────────────────────────────────────────────────────
PH_X, PH_Y = 30, 35
PH_W, PH_H = 310, 600
PH_R = 48          # corner radius

# ── Right panel ───────────────────────────────────────────────────────────────
RP_X, RP_Y = 370, 15
RP_W, RP_H = 885, 545
RP_R = 28

# ── Buttons ───────────────────────────────────────────────────────────────────
BTN_Y      = 600
BTN_H_PX   = 82
BTN_R      = 18
BTN1_X     = 395
BTN2_X     = 730
BTN_W      = 295

BRANDING = "KENSHIN ANIME"

# ── Fonts ─────────────────────────────────────────────────────────────────────
_FONT_CANDIDATES = [
    "fonts/BebasNeue-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _resize_crop(img: Image.Image, tw: int, th: int) -> Image.Image:
    """Center-crop resize to exactly tw×th."""
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    l = (nw - tw) // 2
    t = (nh - th) // 2
    return img.crop((l, t, l + tw, t + th))


def _round_mask(size: tuple, radius: int) -> Image.Image:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0]-1, size[1]-1],
                                        radius=radius, fill=255)
    return m


def _apply_round(img: Image.Image, radius: int) -> Image.Image:
    img = img.convert("RGBA")
    img.putalpha(_round_mask(img.size, radius))
    return img


def _shadow_text(draw: ImageDraw.ImageDraw, xy: tuple,
                 text: str, font: ImageFont.FreeTypeFont,
                 fill=(255, 255, 255, 255), shadow_offset: int = 4):
    sx, sy = xy
    draw.text((sx + shadow_offset, sy + shadow_offset), text,
              font=font, fill=(0, 0, 0, 200))
    draw.text(xy, text, font=font, fill=fill)


def _text_size(draw: ImageDraw.ImageDraw, text: str,
               font: ImageFont.FreeTypeFont) -> tuple:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]


# ── Main ──────────────────────────────────────────────────────────────────────
def create_thumbnail(anime_name: str,
                     bg_bytes: bytes,
                     right_bytes: bytes,
                     left_bytes: bytes) -> io.BytesIO:
    """
    Returns a BytesIO JPEG of the composed thumbnail.
    """
    bg_img    = Image.open(io.BytesIO(bg_bytes)).convert("RGB")
    right_img = Image.open(io.BytesIO(right_bytes)).convert("RGB")
    left_img  = Image.open(io.BytesIO(left_bytes)).convert("RGB")

    # ── Background ────────────────────────────────────────────────────────────
    bg = _resize_crop(bg_img, W, H)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=14))
    bg = ImageEnhance.Brightness(bg).enhance(0.40)
    canvas = bg.convert("RGBA")

    draw = ImageDraw.Draw(canvas)

    # ── Phone mockup ──────────────────────────────────────────────────────────
    # Outer bezel
    bezel = Image.new("RGBA", (PH_W, PH_H), (0, 0, 0, 0))
    bd    = ImageDraw.Draw(bezel)
    bd.rounded_rectangle([0, 0, PH_W-1, PH_H-1], radius=PH_R,
                          fill=(15, 15, 15, 255))
    # Subtle rim highlight
    bd.rounded_rectangle([1, 1, PH_W-2, PH_H-2], radius=PH_R,
                          outline=(90, 90, 90, 160), width=3)

    # Screen content
    screen_pad = 8
    screen_w   = PH_W - screen_pad * 2
    screen_h   = PH_H - screen_pad * 2
    screen     = _resize_crop(left_img, screen_w, screen_h)
    screen     = _apply_round(screen, PH_R - 4)
    bezel.paste(screen, (screen_pad, screen_pad), screen)

    canvas.paste(bezel, (PH_X, PH_Y), bezel)

    # Reflection (subtle, bottom)
    ref = bezel.copy().transpose(Image.FLIP_TOP_BOTTOM)
    ra  = ref.split()[3].point(lambda v: int(v * 0.12))
    ref.putalpha(ra)
    ref_crop_h = min(90, H - (PH_Y + PH_H + 4))
    if ref_crop_h > 0:
        canvas.paste(ref.crop((0, 0, PH_W, ref_crop_h)),
                     (PH_X, PH_Y + PH_H + 4),
                     ref.crop((0, 0, PH_W, ref_crop_h)))

    # ── Right panel ───────────────────────────────────────────────────────────
    panel = _resize_crop(right_img, RP_W, RP_H)
    panel = panel.convert("RGBA")

    # Dark overlay
    ov = Image.new("RGBA", (RP_W, RP_H), (0, 0, 0, 105))
    panel = Image.alpha_composite(panel, ov)
    panel = _apply_round(panel, RP_R)

    canvas.paste(panel, (RP_X, RP_Y), panel)

    # Panel border
    draw.rounded_rectangle([RP_X, RP_Y, RP_X+RP_W-1, RP_Y+RP_H-1],
                            radius=RP_R, outline=(60, 60, 60, 180), width=2)

    # ── Text on right panel ───────────────────────────────────────────────────
    font_title    = _load_font(80)
    font_brand    = _load_font(52)
    font_btn      = _load_font(36)

    # Wrap anime title if long
    words = anime_name.upper().split()
    if len(words) == 1:
        lines = [words[0]]
    elif len(words) <= 3:
        lines = [anime_name.upper()]
    else:
        mid   = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    tx = RP_X + 30
    ty = RP_Y + 28
    for line in lines:
        _shadow_text(draw, (tx, ty), line, font_title,
                     fill=(255, 255, 255, 255), shadow_offset=4)
        lw, lh = _text_size(draw, line, font_title)
        ty += lh + 8

    ty += 12
    _shadow_text(draw, (tx, ty), BRANDING, font_brand,
                 fill=(255, 220, 50, 255), shadow_offset=3)

    # ── Buttons ───────────────────────────────────────────────────────────────
    def _draw_btn(x: int, label: str):
        rect = [x, BTN_Y, x + BTN_W, BTN_Y + BTN_H_PX]
        draw.rounded_rectangle(rect, radius=BTN_R, fill=(25, 25, 25, 210))
        draw.rounded_rectangle(rect, radius=BTN_R,
                                outline=(75, 75, 75, 200), width=2)
        tw, th = _text_size(draw, label, font_btn)
        tx_ = x + (BTN_W - tw) // 2
        ty_ = BTN_Y + (BTN_H_PX - th) // 2
        _shadow_text(draw, (tx_, ty_), label, font_btn,
                     fill=(255, 255, 255, 255), shadow_offset=2)

    _draw_btn(BTN1_X, "WATCH NOW")
    _draw_btn(BTN2_X, BRANDING)

    # ── Output ────────────────────────────────────────────────────────────────
    out = io.BytesIO()
    canvas.convert("RGB").save(out, format="JPEG", quality=95)
    out.seek(0)
    return out
