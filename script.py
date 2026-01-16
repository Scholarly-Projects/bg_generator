# script.py

import os
import random
import math
from PIL import Image, ImageDraw

# --- SETTINGS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(SCRIPT_DIR, 'A')
OUTPUT_FOLDER = os.path.join(SCRIPT_DIR, 'B')

RESOLUTIONS = [
    (1920, 1080),   # Landscape
    (1080, 1920),   # Portrait
    (1920, 1920),   # Square
]

DPI = 600
NUM_PATTERNS = 4  # var1 (refined lattice) + 3 new variations

def load_color_swatches():
    """Load 1–5 solid-color .png files from A/ as color swatches."""
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: Input folder 'A' not found at {INPUT_FOLDER}")
        return None

    png_files = sorted([f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.png')])
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

# ======================
# VAR1: REFINED WOVEN LATTICE (your favorite, cleaned up)
# Delicate grid with organic thread jitter — NO CIRCLES
# ======================
def generate_var1(width, height, colors, seed):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    base_density = min(width, height) // 100
    cell_size = max(10, base_density)
    
    # Horizontal threads
    for i in range(0, width, cell_size):
        offset = random.randint(-3, 3)
        points = []
        for y in range(0, height, 3):  # finer sampling for smoothness
            jitter = random.randint(-2, 2)
            points.append((i + jitter, y + offset))
        if len(points) > 1:
            color = random.choice(colors) + (255,)
            draw.line(points, fill=color, width=1)
    
    # Vertical threads
    for j in range(0, height, cell_size):
        offset = random.randint(-3, 3)
        points = []
        for x in range(0, width, 3):
            jitter = random.randint(-2, 2)
            points.append((x + offset, j + jitter))
        if len(points) > 1:
            color = random.choice(colors) + (255,)
            draw.line(points, fill=color, width=1)
    
    return img

# ======================
# VAR2: TWISTED CORDS
# Paired threads that gently twist around each other
# ======================
def generate_var2(width, height, colors, seed):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    base_density = min(width, height) // 120
    spacing = max(12, base_density)
    
    # Create horizontal twisted cords
    for y_base in range(0, height, spacing * 2):
        color1 = random.choice(colors) + (255,)
        color2 = random.choice(colors) + (255,)
        
        points1, points2 = [], []
        phase = random.uniform(0, 2 * math.pi)
        
        for x in range(0, width, 4):
            # Two sine waves slightly out of phase
            amp = spacing // 3
            offset1 = amp * math.sin(x * 0.02 + phase)
            offset2 = amp * math.sin(x * 0.02 + phase + math.pi)
            
            points1.append((x, y_base + offset1))
            points2.append((x, y_base + offset2 + spacing))
        
        if len(points1) > 1:
            draw.line(points1, fill=color1, width=1)
            draw.line(points2, fill=color2, width=1)
    
    # Create vertical twisted cords
    for x_base in range(0, width, spacing * 2):
        color1 = random.choice(colors) + (255,)
        color2 = random.choice(colors) + (255,)
        
        points1, points2 = [], []
        phase = random.uniform(0, 2 * math.pi)
        
        for y in range(0, height, 4):
            amp = spacing // 3
            offset1 = amp * math.sin(y * 0.02 + phase)
            offset2 = amp * math.sin(y * 0.02 + phase + math.pi)
            
            points1.append((x_base + offset1, y))
            points2.append((x_base + offset2 + spacing, y))
        
        if len(points1) > 1:
            draw.line(points1, fill=color1, width=1)
            draw.line(points2, fill=color2, width=1)
    
    return img

# ======================
# VAR3: INTERWOVEN DIAGONALS
# Criss-crossing diagonal threads with variable density
# ======================
def generate_var3(width, height, colors, seed):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    base_density = min(width, height) // 90
    spacing = max(10, base_density)
    
    # Diagonal set 1: top-left to bottom-right
    for offset in range(-height, width + height, spacing):
        if random.random() < 0.85:  # 85% density
            color = random.choice(colors) + (255,)
            points = []
            for t in range(max(0, -offset), min(width, height - offset), 3):
                x = t
                y = t + offset
                if 0 <= x < width and 0 <= y < height:
                    # Add subtle organic jitter
                    jitter_x = random.randint(-1, 1)
                    jitter_y = random.randint(-1, 1)
                    points.append((x + jitter_x, y + jitter_y))
            if len(points) > 2:
                draw.line(points, fill=color, width=1)
    
    # Diagonal set 2: top-right to bottom-left
    for offset in range(0, width + height, spacing):
        if random.random() < 0.85:
            color = random.choice(colors) + (255,)
            points = []
            for t in range(max(0, offset - height), min(width, offset), 3):
                x = t
                y = offset - t
                if 0 <= x < width and 0 <= y < height:
                    jitter_x = random.randint(-1, 1)
                    jitter_y = random.randint(-1, 1)
                    points.append((x + jitter_x, y + jitter_y))
            if len(points) > 2:
                draw.line(points, fill=color, width=1)
    
    return img

# ======================
# VAR4: MICRO-WEAVE
# Ultra-fine grid with randomized thread breaks (like aged fabric)
# ======================
def generate_var4(width, height, colors, seed):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Very fine weave
    horz_spacing = max(6, min(width, height) // 180)
    vert_spacing = max(6, min(width, height) // 180)
    
    # Horizontal micro-threads (with gaps)
    for y in range(0, height, horz_spacing):
        color = random.choice(colors) + (255,)
        x = 0
        while x < width:
            if random.random() < 0.7:  # 70% chance to draw segment
                seg_len = random.randint(8, 25)
                end_x = min(x + seg_len, width)
                draw.line([(x, y), (end_x, y)], fill=color, width=1)
                x = end_x + random.randint(3, 12)  # gap
            else:
                x += random.randint(5, 15)  # skip segment
    
    # Vertical micro-threads (with gaps)
    for x in range(0, width, vert_spacing):
        color = random.choice(colors) + (255,)
        y = 0
        while y < height:
            if random.random() < 0.7:
                seg_len = random.randint(8, 25)
                end_y = min(y + seg_len, height)
                draw.line([(x, y), (x, end_y)], fill=color, width=1)
                y = end_y + random.randint(3, 12)
            else:
                y += random.randint(5, 15)
    
    return img

# Map variations
VARIATIONS = {
    1: generate_var1,
    2: generate_var2,
    3: generate_var3,
    4: generate_var4
}

def main():
    colors = load_color_swatches()
    if colors is None:
        return

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for pattern_id in range(1, NUM_PATTERNS + 1):
        print(f"\nGenerating variation {pattern_id}/{NUM_PATTERNS}...")
        seed = random.randint(100000, 999999)
        generate_func = VARIATIONS[pattern_id]

        for res_name, (w, h) in zip(['1920x1080', '1080x1920', '1920x1920'], RESOLUTIONS):
            print(f"  → Rendering {res_name}...")
            img = generate_func(w, h, colors, seed)

            filename = f"var{pattern_id}_{res_name}.png"
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            img.save(output_path, "PNG", dpi=(DPI, DPI), optimize=True)
            print(f"    Saved: {filename}")

    print(f"\n✅ All {NUM_PATTERNS} transparent woven patterns generated in '{OUTPUT_FOLDER}' at 600 DPI.")
    print("\nPattern Guide:")
    print("  var1: Refined Woven Lattice — clean orthogonal grid (your favorite)")
    print("  var2: Twisted Cords — paired threads with gentle helical motion")
    print("  var3: Interwoven Diagonals — dynamic criss-crossing structure")
    print("  var4: Micro-Weave — ultra-fine threads with intentional gaps")

if __name__ == "__main__":
    main()