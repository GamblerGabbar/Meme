from flask import Flask, render_template, jsonify
import requests
import random
import io
import base64
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

MEME_API = "https://meme-api.com/gimme"

TOP_TEXTS = [
    "When the code works on the first try",
    "Me trying to debug at 3 AM",
    "That moment when tests finally pass",
    "Deploy day vibes",
    "It worked… on my machine"
]
BOTTOM_TEXTS = [
    "Ship it!",
    "Just one more print()",
    "We ball",
    "Refactor later",
    "Azure to the rescue"
]


def fetch_meme_from_api():
    """Return (title, image_url) from public meme API or raise Exception."""
    r = requests.get(MEME_API, timeout=8)
    r.raise_for_status()
    data = r.json()
    return data.get('title', 'Random Meme'), data.get('url')


def generate_simple_meme(width=800, height=800):
    """Generate a simple meme image locally using Pillow and return (title, data_url)."""
    bg_color = tuple(random.randint(64, 200) for _ in range(3))
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load a common font, fall back to default
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    except Exception:
        font = ImageFont.load_default()

    top = random.choice(TOP_TEXTS)
    bottom = random.choice(BOTTOM_TEXTS)

    # Helper to draw centered shadowed text
    def draw_centered(text, y):
        W, H = img.size
        # Wrap text to fit width
        max_w = int(W * 0.9)
        lines = []
        words = text.split()
        line = ''
        for w in words:
            trial = (line + ' ' + w).strip()
            bbox = draw.textbbox((0, 0), trial, font=font)
            if bbox[2] - bbox[0] <= max_w:
                line = trial
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        line_h = draw.textbbox((0,0), 'Ag', font=font)[3]
        total_h = len(lines) * (line_h + 8)
        current_y = y
        for l in lines:
            bbox = draw.textbbox((0,0), l, font=font)
            w = bbox[2] - bbox[0]
            x = (W - w) // 2
            # Shadow
            draw.text((x+2, current_y+2), l, font=font, fill=(0,0,0))
            draw.text((x, current_y), l, font=font, fill=(255,255,255))
            current_y += line_h + 8

    draw_centered(top.upper(), y=40)
    draw_centered(bottom.upper(), y=height - 200)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    data_url = f"data:image/png;base64,{b64}"
    title = f"{top} — {bottom}"
    return title, data_url


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/meme')
def get_meme():
    """Returns JSON: { title, url, source } where url can be remote URL or base64 data URL."""
    try:
        title, url = fetch_meme_from_api()
        return jsonify({"title": title, "url": url, "source": "api"})
    except Exception:
        title, data_url = generate_simple_meme()
        return jsonify({"title": title, "url": data_url, "source": "generated"})


if __name__ == '__main__':
    # For local development only. In Azure App Service, Gunicorn will be used automatically.
    app.run(host='0.0.0.0', port=5000, debug=True)
