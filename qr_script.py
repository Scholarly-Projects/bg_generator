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

RESOLUTION = (1920, 1920)  # Only square resolution

DPI = 600
NUM_PATTERNS = 8  # Increased to include serape variations
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

def get_color_at_position(y, height, colors, seed):
    """Get color based on vertical position for serape effect."""
    random.seed(seed)
    num_colors = len(colors)
    if num_colors < 2:
        return colors[0] if colors else (0, 0, 0)
    
    # Create color bands
    band_height = height // num_colors
    
    # Determine which band we're in
    band = min(y // band_height, num_colors - 1)
    
    # Add some randomness to band edges for a more organic feel
    if random.random() < 0.1:  # 10% chance to use adjacent color
        if band > 0 and random.random() < 0.5:
            band = band - 1
        elif band < num_colors - 1:
            band = band + 1
    
    return colors[band]

def blend_colors(color1, color2, ratio):
    """Blend two colors by a given ratio (0-1)."""
    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
    return (r, g, b)

def get_blended_color_at_position(y, height, colors, seed):
    """Get blended color based on vertical position for smooth transitions."""
    random.seed(seed)
    num_colors = len(colors)
    if num_colors < 2:
        return colors[0] if colors else (0, 0, 0)
    
    # Create color bands
    band_height = height // num_colors
    
    # Determine which band we're in and the position within the band
    band = min(y // band_height, num_colors - 1)
    pos_in_band = (y % band_height) / band_height
    
    # Blend with next color at the edge of bands
    if pos_in_band > 0.8 and band < num_colors - 1:
        # Blend with next color
        ratio = (pos_in_band - 0.8) / 0.2  # 0 to 1
        return blend_colors(colors[band], colors[band + 1], ratio)
    
    return colors[band]

# ======================
# VAR1: REFINED WOVEN LATTICE QR CODE
# ======================
def generate_var1(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Much denser grid to match VAR4
    cell_size = max(2, min(width, height) // 200)  # Match VAR4 density
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Fill QR code pixels with dense horizontal and vertical lines
    for x in range(0, width, cell_size):
        for y in range(0, height, cell_size):
            if x < width and y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    color = random.choice(colors)
                    # Draw a small cross pattern to fill the module
                    draw.line([(x, y), (x + cell_size, y)], fill=color, width=1)
                    draw.line([(x, y), (x, y + cell_size)], fill=color, width=1)
                    # Add more lines to ensure complete filling
                    draw.line([(x, y + cell_size//2), (x + cell_size, y + cell_size//2)], fill=color, width=1)
                    draw.line([(x + cell_size//2, y), (x + cell_size//2, y + cell_size)], fill=color, width=1)
    
    return img

# ======================
# VAR2: TWISTED CORDS QR CODE
# ======================
def generate_var2(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Much denser spacing to match VAR4
    spacing = max(2, min(width, height) // 200)  # Match VAR4 density
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Create dense horizontal twisted cords
    for y_base in range(0, height, spacing):
        color = random.choice(colors)
        points = []
        
        for x in range(0, width, 1):  # Pixel-level sampling
            if x < width and y_base < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y_base][0] < 128:  # Black pixel in QR code
                    # Minimal sine wave for QR code clarity
                    offset = spacing // 4 * math.sin(x * 0.2)  # Higher frequency, smaller amplitude
                    points.append((x, y_base + offset))
                else:
                    # End the current line and start a new one
                    if len(points) > 1:
                        draw.line(points, fill=color, width=1)
                    points = []
                    color = random.choice(colors)
        
        # Draw the last line segment
        if len(points) > 1:
            draw.line(points, fill=color, width=1)
    
    # Create dense vertical twisted cords
    for x_base in range(0, width, spacing):
        color = random.choice(colors)
        points = []
        
        for y in range(0, height, 1):  # Pixel-level sampling
            if y < height and x_base < width:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x_base, y][0] < 128:  # Black pixel in QR code
                    # Minimal sine wave for QR code clarity
                    offset = spacing // 4 * math.sin(y * 0.2)  # Higher frequency, smaller amplitude
                    points.append((x_base + offset, y))
                else:
                    # End the current line and start a new one
                    if len(points) > 1:
                        draw.line(points, fill=color, width=1)
                    points = []
                    color = random.choice(colors)
        
        # Draw the last line segment
        if len(points) > 1:
            draw.line(points, fill=color, width=1)
    
    return img

# ======================
# VAR3: INTERWOVEN DIAGONALS QR CODE
# ======================
def generate_var3(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Much denser spacing to match VAR4
    spacing = max(2, min(width, height) // 200)  # Match VAR4 density
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Diagonal set 1: top-left to bottom-right
    for offset in range(-height, width + height, spacing):
        points = []
        color = random.choice(colors)
        
        for t in range(max(0, -offset), min(width, height - offset), 1):  # Pixel-level sampling
            x = t
            y = t + offset
            if 0 <= x < width and 0 <= y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    points.append((x, y))
                else:
                    # End the current line and start a new one
                    if len(points) > 1:
                        draw.line(points, fill=color, width=1)
                    points = []
                    color = random.choice(colors)
        
        # Draw the last line segment
        if len(points) > 1:
            draw.line(points, fill=color, width=1)
    
    # Diagonal set 2: top-right to bottom-left
    for offset in range(0, width + height, spacing):
        points = []
        color = random.choice(colors)
        
        for t in range(max(0, offset - height), min(width, offset), 1):  # Pixel-level sampling
            x = t
            y = offset - t
            if 0 <= x < width and 0 <= y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    points.append((x, y))
                else:
                    # End the current line and start a new one
                    if len(points) > 1:
                        draw.line(points, fill=color, width=1)
                    points = []
                    color = random.choice(colors)
        
        # Draw the last line segment
        if len(points) > 1:
            draw.line(points, fill=color, width=1)
    
    return img

# ======================
# VAR4: MICRO-WEAVE QR CODE (UNCHANGED - IT WORKS)
# ======================
def generate_var4(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Very fine weave for QR code visibility
    horz_spacing = max(1, min(width, height) // 200)
    vert_spacing = max(1, min(width, height) // 200)
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Horizontal micro-threads - only where QR code has black pixels
    for y in range(0, height, horz_spacing):
        x = 0
        while x < width:
            if x < width and y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    color = random.choice(colors)
                    # Always draw for QR code pixels
                    seg_len = random.randint(1, 3)  # Very small segments for QR code
                    end_x = min(x + seg_len, width)
                    draw.line([(x, y), (end_x, y)], fill=color, width=1)
                    x = end_x + 1  # Minimal gaps for QR code
                else:
                    x += max(2, horz_spacing)  # Skip white areas in QR code
    
    # Vertical micro-threads - only where QR code has black pixels
    for x in range(0, width, vert_spacing):
        y = 0
        while y < height:
            if x < width and y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    color = random.choice(colors)
                    # Always draw for QR code pixels
                    seg_len = random.randint(1, 3)  # Very small segments for QR code
                    end_y = min(y + seg_len, height)
                    draw.line([(x, y), (x, end_y)], fill=color, width=1)
                    y = end_y + 1  # Minimal gaps for QR code
                else:
                    y += max(2, vert_spacing)  # Skip white areas in QR code
    
    return img

# ======================
# VAR5: REFINED WOVEN LATTICE SERAPE QR CODE
# ======================
def generate_var5(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Much denser grid to match VAR4
    cell_size = max(2, min(width, height) // 200)  # Match VAR4 density
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Fill QR code pixels with dense horizontal and vertical lines
    for x in range(0, width, cell_size):
        for y in range(0, height, cell_size):
            if x < width and y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    # Get color based on position for serape effect
                    color = get_blended_color_at_position(y, height, colors, seed)
                    # Draw a small cross pattern to fill the module
                    draw.line([(x, y), (x + cell_size, y)], fill=color, width=1)
                    draw.line([(x, y), (x, y + cell_size)], fill=color, width=1)
                    # Add more lines to ensure complete filling
                    draw.line([(x, y + cell_size//2), (x + cell_size, y + cell_size//2)], fill=color, width=1)
                    draw.line([(x + cell_size//2, y), (x + cell_size//2, y + cell_size)], fill=color, width=1)
    
    return img

# ======================
# VAR6: TWISTED CORDS SERAPE QR CODE
# ======================
def generate_var6(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Much denser spacing to match VAR4
    spacing = max(2, min(width, height) // 200)  # Match VAR4 density
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Create dense horizontal twisted cords
    for y_base in range(0, height, spacing):
        # Get color based on position for serape effect
        color = get_blended_color_at_position(y_base, height, colors, seed)
        points = []
        
        for x in range(0, width, 1):  # Pixel-level sampling
            if x < width and y_base < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y_base][0] < 128:  # Black pixel in QR code
                    # Minimal sine wave for QR code clarity
                    offset = spacing // 4 * math.sin(x * 0.2)  # Higher frequency, smaller amplitude
                    points.append((x, y_base + offset))
                else:
                    # End the current line and start a new one
                    if len(points) > 1:
                        draw.line(points, fill=color, width=1)
                    points = []
                    # Get new color for next segment
                    color = get_blended_color_at_position(y_base, height, colors, seed)
        
        # Draw the last line segment
        if len(points) > 1:
            draw.line(points, fill=color, width=1)
    
    # Create dense vertical twisted cords
    for x_base in range(0, width, spacing):
        points = []
        
        for y in range(0, height, 1):  # Pixel-level sampling
            if y < height and x_base < width:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x_base, y][0] < 128:  # Black pixel in QR code
                    # Get color based on position for serape effect
                    color = get_blended_color_at_position(y, height, colors, seed)
                    # Minimal sine wave for QR code clarity
                    offset = spacing // 4 * math.sin(y * 0.2)  # Higher frequency, smaller amplitude
                    points.append((x_base + offset, y))
                else:
                    # End the current line and start a new one
                    if len(points) > 1:
                        draw.line(points, fill=color, width=1)
                    points = []
        
        # Draw the last line segment
        if len(points) > 1:
            draw.line(points, fill=color, width=1)
    
    return img

# ======================
# VAR7: INTERWOVEN DIAGONALS SERAPE QR CODE
# ======================
def generate_var7(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Much denser spacing to match VAR4
    spacing = max(2, min(width, height) // 200)  # Match VAR4 density
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Diagonal set 1: top-left to bottom-right
    for offset in range(-height, width + height, spacing):
        points = []
        
        for t in range(max(0, -offset), min(width, height - offset), 1):  # Pixel-level sampling
            x = t
            y = t + offset
            if 0 <= x < width and 0 <= y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    # Get color based on position for serape effect
                    color = get_blended_color_at_position(y, height, colors, seed)
                    points.append((x, y))
                else:
                    # End the current line and start a new one
                    if len(points) > 1:
                        draw.line(points, fill=color, width=1)
                    points = []
        
        # Draw the last line segment
        if len(points) > 1:
            # Get color for the last segment
            color = get_blended_color_at_position(points[-1][1], height, colors, seed)
            draw.line(points, fill=color, width=1)
    
    # Diagonal set 2: top-right to bottom-left
    for offset in range(0, width + height, spacing):
        points = []
        
        for t in range(max(0, offset - height), min(width, offset), 1):  # Pixel-level sampling
            x = t
            y = offset - t
            if 0 <= x < width and 0 <= y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    # Get color based on position for serape effect
                    color = get_blended_color_at_position(y, height, colors, seed)
                    points.append((x, y))
                else:
                    # End the current line and start a new one
                    if len(points) > 1:
                        draw.line(points, fill=color, width=1)
                    points = []
        
        # Draw the last line segment
        if len(points) > 1:
            # Get color for the last segment
            color = get_blended_color_at_position(points[-1][1], height, colors, seed)
            draw.line(points, fill=color, width=1)
    
    return img

# ======================
# VAR8: MICRO-WEAVE SERAPE QR CODE
# ======================
def generate_var8(width, height, colors, seed, qr_mask):
    random.seed(seed)
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # White background
    draw = ImageDraw.Draw(img)
    
    # Very fine weave for QR code visibility
    horz_spacing = max(1, min(width, height) // 200)
    vert_spacing = max(1, min(width, height) // 200)
    
    # Get QR code data
    qr_pixels = qr_mask.load()
    
    # Horizontal micro-threads - only where QR code has black pixels
    for y in range(0, height, horz_spacing):
        # Get color based on position for serape effect
        color = get_blended_color_at_position(y, height, colors, seed)
        x = 0
        while x < width:
            if x < width and y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    # Always draw for QR code pixels
                    seg_len = random.randint(1, 3)  # Very small segments for QR code
                    end_x = min(x + seg_len, width)
                    draw.line([(x, y), (end_x, y)], fill=color, width=1)
                    x = end_x + 1  # Minimal gaps for QR code
                else:
                    x += max(2, horz_spacing)  # Skip white areas in QR code
    
    # Vertical micro-threads - only where QR code has black pixels
    for x in range(0, width, vert_spacing):
        y = 0
        while y < height:
            if x < width and y < height:
                # Check if this pixel is part of the QR code (black)
                if qr_pixels[x, y][0] < 128:  # Black pixel in QR code
                    # Get color based on position for serape effect
                    color = get_blended_color_at_position(y, height, colors, seed)
                    # Always draw for QR code pixels
                    seg_len = random.randint(1, 3)  # Very small segments for QR code
                    end_y = min(y + seg_len, height)
                    draw.line([(x, y), (x, end_y)], fill=color, width=1)
                    y = end_y + 1  # Minimal gaps for QR code
                else:
                    y += max(2, vert_spacing)  # Skip white areas in QR code
    
    return img

# Map variations
VARIATIONS = {
    1: generate_var1,
    2: generate_var2,
    3: generate_var3,
    4: generate_var4,
    5: generate_var5,
    6: generate_var6,
    7: generate_var7,
    8: generate_var8
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

        print(f"  → Rendering 1920x1920...")
        
        # Generate QR code for this resolution
        qr_img = generate_qr_code(url, RESOLUTION)
        
        # Generate the pattern using the QR code as a mask
        img = generate_func(RESOLUTION[0], RESOLUTION[1], colors, seed, qr_img)

        filename = f"var{pattern_id}_1920x1920.png"
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        img.save(output_path, "PNG", dpi=(DPI, DPI), optimize=True)
        print(f"    Saved: {filename}")

    print(f"\n✅ All {NUM_PATTERNS} QR codes with woven patterns generated in '{OUTPUT_FOLDER}' at 600 DPI.")
    print("\nPattern Guide:")
    print("  var1: Refined Woven Lattice — clean orthogonal grid")
    print("  var2: Twisted Cords — paired threads with gentle helical motion")
    print("  var3: Interwoven Diagonals — dynamic criss-crossing structure")
    print("  var4: Micro-Weave — ultra-fine threads with intentional gaps")
    print("  var5: Refined Woven Lattice Serape — clean orthogonal grid with color bands")
    print("  var6: Twisted Cords Serape — paired threads with gentle helical motion in color bands")
    print("  var7: Interwoven Diagonals Serape — dynamic criss-crossing structure in color bands")
    print("  var8: Micro-Weave Serape — ultra-fine threads with intentional gaps in color bands")
    print(f"\nQR codes will track visits with Google Analytics ID: {google_analytics_id}")

if __name__ == "__main__":
    main()