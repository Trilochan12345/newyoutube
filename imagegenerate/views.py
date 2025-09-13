from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
import textwrap, os

# Try a few common fonts; fallback to PIL default
FONT_CANDIDATES = [
    # supply your own in project root or static/fonts
    "DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "arial.ttf",
]

def _load_font(font_name: str | None, size: int):
    # If user asked for a specific font, try that first (safe, relative paths only)
    paths = []
    if font_name:
        # prevent directory traversal
        if os.path.sep in font_name or ".." in font_name:
            font_name = None
        else:
            paths.append(font_name)
    paths.extend(FONT_CANDIDATES)

    for p in paths:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    # fallback bitmap font
    return ImageFont.load_default()

def _hex_to_rgb(h: str, default=(255, 255, 255)):
    if not h:
        return default
    h = h.strip().lstrip("#")
    if len(h) == 3:  # e.g. "fff"
        h = "".join([c*2 for c in h])
    if len(h) != 6:
        return default
    try:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    except Exception:
        return default

def form_page(request):
    return render(request, "form.html")

def text_image(request):
    text = request.GET.get("text", "man").strip()
    if not text:
        return HttpResponseBadRequest("Missing ?text=...")

    # Params (with sensible defaults)
    size = int(request.GET.get("size", 96))            # font size
    padding = int(request.GET.get("padding", 40))      # px padding around text
    max_width = int(request.GET.get("max_width", 1600))
    bg = _hex_to_rgb(request.GET.get("bg", "000000"))  # background color
    fg = _hex_to_rgb(request.GET.get("fg", "ffffff"))  # text color
    align = request.GET.get("align", "center")         # left|center|right
    wrap = int(request.GET.get("wrap", 0))             # wrap width (0 = auto)
    font_name = request.GET.get("font")                # font filename or system path
    antialias = request.GET.get("aa", "1") != "0"      # enable resize AA trick

    # Load font
    font = _load_font(font_name, size)

    # Optional wrapping; auto-wrap to fit max_width roughly
    wrapper_width = wrap
    if wrapper_width <= 0:
        # use character width heuristic from font metrics
        avg_char_w = font.getlength("ABCDEFGHIJKLMNOPQRSTUVWXYZ") / 26 or size * 0.6
        wrapper_width = max(1, int((max_width - 2*padding) / avg_char_w))

    lines = []
    for raw_line in text.split("\n"):
        if wrapper_width:
            lines.extend(textwrap.wrap(raw_line, width=wrapper_width)) if raw_line else lines.append("")
        else:
            lines.append(raw_line)

    # Measure text block
    draw_img = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(draw_img)
    line_heights = []
    line_widths = []
    spacing = int(size * 0.35)

    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        line_widths.append(w)
        line_heights.append(h)

    text_w = max(line_widths) if line_widths else 0
    text_h = sum(line_heights) + spacing * (len(lines)-1 if lines else 0)

    img_w = max(text_w + 2 * padding, 2)
    img_h = max(text_h + 2 * padding, 2)

    # Create image
    img = Image.new("RGB", (img_w, img_h), bg)
    draw = ImageDraw.Draw(img)

    # Draw each line based on alignment
    y = padding
    for i, line in enumerate(lines):
        w = line_widths[i]
        h = line_heights[i]
        if align == "left":
            x = padding
        elif align == "right":
            x = img_w - padding - w
        else:
            x = (img_w - w) // 2

        draw.text((x, y), line, fill=fg, font=font)
        y += h + spacing

    # Optional antialiasing via downscale (render 2x then resize) – here we
    # emulate it by upscaling canvas if requested. Simpler: if aa=2x, upscale then shrink
    if antialias and request.GET.get("aa") in ("2", "2x"):
        big = img.resize((img_w*2, img_h*2), Image.NEAREST)
        img = big.resize((img_w, img_h), Image.LANCZOS)

    # Stream as PNG
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    resp = HttpResponse(buf.getvalue(), content_type="image/png")
    # Basic cache headers (tune as needed)
    resp["Cache-Control"] = "public, max-age=86400"
    return resp
