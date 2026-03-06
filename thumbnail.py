from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

def round_corner(img, radius):

    circle = Image.new('L',(radius*2,radius*2),0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0,0,radius*2,radius*2),fill=255)

    alpha = Image.new('L',img.size,255)
    w,h = img.size

    alpha.paste(circle.crop((0,0,radius,radius)),(0,0))
    alpha.paste(circle.crop((0,radius,radius,radius*2)),(0,h-radius))
    alpha.paste(circle.crop((radius,0,radius*2,radius)),(w-radius,0))
    alpha.paste(circle.crop((radius,radius,radius*2,radius*2)),(w-radius,h-radius))

    img.putalpha(alpha)

    return img

def create_thumbnail(bg_bytes,right_bytes,left_bytes,name):

    bg = Image.open(BytesIO(bg_bytes)).resize((1920,1080)).convert("RGBA")

    blur = bg.filter(ImageFilter.GaussianBlur(12))
    bg = Image.blend(bg,blur,0.4)

    right = Image.open(BytesIO(right_bytes)).resize((900,500)).convert("RGBA")
    left = Image.open(BytesIO(left_bytes)).resize((600,900)).convert("RGBA")

    right = round_corner(right,40)
    left = round_corner(left,40)

    bg.paste(left,(80,120),left)

    overlay = Image.new("RGBA",(900,500),(0,0,0,140))

    bg.paste(right,(950,160),right)
    bg.paste(overlay,(950,160),overlay)

    draw = ImageDraw.Draw(bg)

    font_big = ImageFont.truetype("assets/font.ttf",90)
    font_mid = ImageFont.truetype("assets/font.ttf",60)

    draw.text((980,200),name.upper(),(255,255,255),font_big)

    draw.text((980,320),"KENSHIN ANIME",(230,230,230),font_mid)

    btn1 = Image.new("RGBA",(450,110),(0,0,0,190))
    btn2 = Image.new("RGBA",(450,110),(0,0,0,190))

    btn1 = round_corner(btn1,30)
    btn2 = round_corner(btn2,30)

    bg.paste(btn1,(500,880),btn1)
    bg.paste(btn2,(980,880),btn2)

    draw.text((590,905),"WATCH NOW",(255,255,255),font_mid)
    draw.text((1050,905),"KENSHIN ANIME",(255,255,255),font_mid)

    path = "thumbnail.jpg"

    bg.convert("RGB").save(path,quality=95)

    return path
