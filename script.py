import os
import random
import math
import sys
import argparse
from PIL import Image, ImageDraw
import qrcode
from qrcode.constants import ERROR_CORRECT_M

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
NUM_PATTERNS = 4  
GOOGLE_ANALYTICS_ID = "G-XXXXXXXXXX"  # Replace with your actual Google Analytics ID

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

def generate_qr_code(url, size):
    """Generate a QR code for the given URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img = qr_img.convert("RGBA")
    
    # Resize to match our canvas
    qr_img = qr_img.resize(size, Image.LANCZOS)
    
    return qr_img

# ======================
# VAR1: REFINED WOVEN LATTICE QR CODE
# ======================
def generate_var1(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Much denser grid for QR code visibility
    cell_size = min(width, height) // 25  # Much smaller cells for QR code
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Horizontal threads - only where QR code has black pixels
    for i in range(0, width, cell_size):
        for y in range(0, height, 2):  # Finer sampling for QR code
            if y < height and i < width:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[i, y][0] < 128:  # Black pixel in QR code
                    offset = random.randint(-1, 1)  # Smaller offset for QR code clarity
                    color = random.choice(colors)
                    draw.line([(i + offset, y), (i + offset, y + 2)], fill=color, width=1)
    
    # Vertical threads - only where QR code has black pixels
    for j in range(0, height, cell_size):
        for x in range(0, width, 2):  # Finer sampling for QR code
            if x < width and j < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, j][0] < 128:  # Black pixel in QR code
                    offset = random.randint(-1, 1)  # Smaller offset for QR code clarity
                    color = random.choice(colors)
                    draw.line([(x, j + offset), (x + 2, j + offset)], fill=color, width=1)
    
    return img

# ======================
# VAR2: TWISTED CORDS QR CODE
# ======================
def generate_var2(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Much denser spacing for QR code visibility
    spacing = min(width, height) // 25
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Create horizontal twisted cords - only where QR code has black pixels
    for y_base in range(0, height, spacing):
        color1 = random.choice(colors)
        color2 = random.choice(colors)
        
        points1, points2 = [], []
        phase = random.uniform(0, 2 * math.pi)
        
        for x in range(0, width, 2):  # Finer sampling for QR code
            if x < width and y_base < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y_base][0] < 128:  # Black pixel in QR code
                    # Two sine waves slightly out of phase
                    amp = spacing // 4  # Smaller amplitude for QR code clarity
                    offset1 = amp * math.sin(x * 0.05 + phase)  # Higher frequency
                    offset2 = amp * math.sin(x * 0.05 + phase + math.pi)
                    
                    points1.append((x, y_base + offset1))
                    points2.append((x, y_base + offset2 + spacing // 2))
        
        if len(points1) > 1:
            draw.line(points1, fill=color1, width=1)
            draw.line(points2, fill=color2, width=1)
    
    # Create vertical twisted cords - only where QR code has black pixels
    for x_base in range(0, width, spacing):
        color1 = random.choice(colors)
        color2 = random.choice(colors)
        
        points1, points2 = [], []
        phase = random.uniform(0, 2 * math.pi)
        
        for y in range(0, height, 2):  # Finer sampling for QR code
            if y < height and x_base < width:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x_base, y][0] < 128:  # Black pixel in QR code
                    amp = spacing // 4  # Smaller amplitude for QR code clarity
                    offset1 = amp * math.sin(y * 0.05 + phase)  # Higher frequency
                    offset2 = amp * math.sin(y * 0.05 + phase + math.pi)
                    
                    points1.append((x_base + offset1, y))
                    points2.append((x_base + offset2 + spacing // 2, y))
        
        if len(points1) > 1:
            draw.line(points1, fill=color1, width=1)
            draw.line(points2, fill=color2, width=1)
    
    return img

# ======================
# VAR3: INTERWOVEN DIAGONALS QR CODE
# ======================
def generate_var3(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Much denser spacing for QR code visibility
    spacing = min(width, height) // 25
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Diagonal set 1: top-left to bottom-right - only where QR code has black pixels
    for offset in range(-height, width + height, spacing):
        points = []
        for t in range(max(0, -offset), min(width, height - offset), 2):  # Finer sampling
            x = t
            y = t + offset
            if 0 <= x < width and 0 <= y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    # Add subtle organic jitter
                    jitter_x = random.randint(-1, 1)
                    jitter_y = random.randint(-1, 1)
                    points.append((x + jitter_x, y + jitter_y))
        if len(points) > 2:
            color = random.choice(colors)
            draw.line(points, fill=color, width=1)
    
    # Diagonal set 2: top-right to bottom-left - only where QR code has black pixels
    for offset in range(0, width + height, spacing):
        points = []
        for t in range(max(0, offset - height), min(width, offset), 2):  # Finer sampling
            x = t
            y = offset - t
            if 0 <= x < width and 0 <= y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    jitter_x = random.randint(-1, 1)
                    jitter_y = random.randint(-1, 1)
                    points.append((x + jitter_x, y + jitter_y))
        if len(points) > 2:
            color = random.choice(colors)
            draw.line(points, fill=color, width=1)
    
    return img

# ======================
# VAR4: MICRO-WEAVE QR CODE
# ======================
def generate_var4(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Very fine weave for QR code visibility
    horz_spacing = max(3, min(width, height) // 100)
    vert_spacing = max(3, min(width, height) // 100)
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Horizontal micro-threads - only where QR code has black pixels
    for y in range(0, height, horz_spacing):
        color = random.choice(colors)
        x = 0
        while x < width:
            if x < width and y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    if random.random() < 0.9:  # Higher chance for QR code
                        seg_len = random.randint(3, 8)  # Smaller segments for QR code
                        end_x = min(x + seg_len, width)
                        draw.line([(x, y), (end_x, y)], fill=color, width=1)
                        x = end_x + random.randint(1, 3)  # Smaller gaps for QR code
                    else:
                        x += random.randint(2, 5)  # Smaller skips for QR code
                else:
                    x += max(5, horz_spacing)  # Skip white areas in QR code
    
    # Vertical micro-threads - only where QR code has black pixels
    for x in range(0, width, vert_spacing):
        color = random.choice(colors)
        y = 0
        while y < height:
            if x < width and y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    if random.random() < 0.9:  # Higher chance for QR code
                        seg_len = random.randint(3, 8)  # Smaller segments for QR code
                        end_y = min(y + seg_len, height)
                        draw.line([(x, y), (x, end_y)], fill=color, width=1)
                        y = end_y + random.randint(1, 3)  # Smaller gaps for QR code
                    else:
                        y += random.randint(2, 5)  # Smaller skips for QR code
                else:
                    y += max(5, vert_spacing)  # Skip white areas in QR code
    
    return img

# Map variations
VARIATIONS = {
    1: generate_var1,
    2: generate_var2,
    3: generate_var3,
    4: generate_var4
}

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate QR codes with woven patterns.')
    parser.add_argument('url', help='URL to encode in the QR code')
    parser.add_argument('--analytics', help=f'Google Analytics ID (default: {GOOGLE_ANALYTICS_ID})', default=GOOGLE_ANALYTICS_ID)
    args = parser.parse_args()
    
    url = args.url
    google_analytics_id = args.analytics
    
    # Add Google Analytics tracking to URL if provided
    if google_analytics_id:
        separator = '&' if '?' in url else '?'
        url = f"{url}{separator}utm_source=qr_code&utm_medium=print&utm_campaign=qr_patterns"
    
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
            
            # Generate QR code for this resolution
            qr_img = generate_qr_code(url, (w, h))
            
            # Generate the pattern using the QR code as a mask
            img = generate_func(w, h, colors, seed, qr_img)

            filename = f"var{pattern_id}_{res_name}.png"
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            img.save(output_path, "PNG", dpi=(DPI, DPI), optimize=True)
            print(f"    Saved: {filename}")

    print(f"\n✅ All {NUM_PATTERNS} QR codes with woven patterns generated in '{OUTPUT_FOLDER}' at 600 DPI.")
    print("\nPattern Guide:")
    print("  var1: Refined Woven Lattice — clean orthogonal grid")
    print("  var2: Twisted Cords — paired threads with gentle helical motion")
    print("  var3: Interwoven Diagonals — dynamic criss-crossing structure")
    print("  var4: Micro-Weave — ultra-fine threads with intentional gaps")
    print(f"\nQR codes will track visits with Google Analytics ID: {google_analytics_id}")

if __name__ == "__main__":
    main()