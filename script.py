# script.py

import os
import random
import math
from PIL import Image, ImageDraw

# --- SETTINGS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(SCRIPT_DIR, 'A')
OUTPUT_FOLDER = os.path.join(SCRIPT_DIR, 'B')

# Output resolutions (width, height) in pixels
RESOLUTIONS = [
    (1920, 1080),   # Landscape
    (1080, 1920),   # Portrait
    (1920, 1920),   # Square
]

DPI = 600
NUM_PATTERNS = 5

def load_color_swatches():
    """Load 1–5 solid-color .png files from A/ as color swatches."""
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: Input folder 'A' not found at {INPUT_FOLDER}")
        return None

    png_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.png')]
    if not png_files:
        print("No .png files found in folder 'A'. Please add 1–5 solid-color swatches as PNGs.")
        return None

    if len(png_files) > 5:
        png_files = png_files[:5]
        print("More than 5 swatches found; using first 5.")

    colors = []
    for f in png_files:
        path = os.path.join(INPUT_FOLDER, f)
        try:
            with Image.open(path) as img:
                img = img.convert("RGB")
                # Sample center pixel as representative color
                w, h = img.size
                color = img.getpixel((w // 2, h // 2))
                colors.append(color)
        except Exception as e:
            print(f"Skipping invalid image {f}: {e}")
    
    if not colors:
        print("No valid color swatches loaded.")
        return None

    print(f"Loaded {len(colors)} color(s): {colors}")
    return colors

def generate_fractal_pattern(width, height, colors, seed):
    """Generate a randomized, highly detailed fractal-like pattern."""
    random.seed(seed)
    img = Image.new('RGB', (width, height), random.choice(colors))
    draw = ImageDraw.Draw(img)

    # Use multiple layers of recursive-like geometric noise
    num_layers = random.randint(3, 7)
    for layer in range(num_layers):
        layer_color = random.choice(colors)
        complexity = random.randint(50, 200)
        scale = random.uniform(0.5, 2.0)
        offset_x = random.randint(0, width)
        offset_y = random.randint(0, height)

        for _ in range(complexity):
            shape_type = random.choice(['circle', 'polygon', 'line'])
            x = (random.randint(-width // 2, width * 2) + offset_x) % width
            y = (random.randint(-height // 2, height * 2) + offset_y) % height
            size = random.randint(5, int(min(width, height) * 0.15))

            if shape_type == 'circle':
                draw.ellipse((x - size, y - size, x + size, y + size),
                             outline=layer_color, width=random.randint(1, 3))
            elif shape_type == 'polygon':
                sides = random.randint(3, 8)
                angle_step = 2 * math.pi / sides
                points = []
                for i in range(sides):
                    px = x + size * math.cos(i * angle_step + random.uniform(-0.3, 0.3))
                    py = y + size * math.sin(i * angle_step + random.uniform(-0.3, 0.3))
                    points.append((px, py))
                draw.polygon(points, outline=layer_color, width=random.randint(1, 2))
            elif shape_type == 'line':
                x2 = x + random.randint(-size, size)
                y2 = y + random.randint(-size, size)
                draw.line((x, y, x2, y2), fill=layer_color, width=random.randint(1, 2))

    # Optional: Add subtle noise or overlay
    if random.random() < 0.4:
        noise_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        noise_draw = ImageDraw.Draw(noise_img)
        for _ in range(random.randint(200, 800)):
            nx, ny = random.randint(0, width - 1), random.randint(0, height - 1)
            alpha = random.randint(10, 40)
            noise_draw.point((nx, ny), fill=(*random.choice(colors), alpha))
        img = Image.alpha_composite(img.convert('RGBA'), noise_img).convert('RGB')

    return img

def main():
    colors = load_color_swatches()
    if colors is None:
        return

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for pattern_id in range(1, NUM_PATTERNS + 1):
        print(f"\nGenerating pattern {pattern_id}/{NUM_PATTERNS}...")
        seed = random.randint(1000, 9999)

        for res_name, (w, h) in zip(['1920x1080', '1080x1920', '1920x1920'], RESOLUTIONS):
            print(f"  → Rendering {res_name}...")
            img = generate_fractal_pattern(w, h, colors, seed)

            # Save at 600 DPI
            filename = f"fractal_{pattern_id}_{res_name}.png"
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            img.save(output_path, "PNG", dpi=(DPI, DPI), optimize=True)
            print(f"    Saved: {filename}")

    print(f"\n✅ All {NUM_PATTERNS} patterns generated in {OUTPUT_FOLDER} at 600 DPI.")

if __name__ == "__main__":
    main()