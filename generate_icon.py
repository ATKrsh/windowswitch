# generate_icon.py
# Generates a premium, minimalist .ico file for the Assistive Window Switcher.

from PIL import Image, ImageDraw

def create_minimal_icon():
    # Create a 256x256 image with transparent background
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a premium dark glassmorphic base circle
    # Center = 128, 128; Radius = 110
    draw.ellipse([18, 18, 238, 238], fill=(30, 34, 45, 230), outline=(255, 255, 255, 40), width=6)
    
    # Draw minimalist horizontal switching arrows
    # Line width = 10 pixels for visibility
    arrow_color = (255, 255, 255, 240)
    width = 10
    
    # Right-pointing arrow (Top)
    # Shaft: (75, 105) to (165, 105)
    draw.line([(75, 105), (165, 105)], fill=arrow_color, width=width)
    # Head: (165, 105) pointing to (180, 105)
    draw.polygon([(180, 105), (155, 85), (155, 125)], fill=arrow_color)
    
    # Left-pointing arrow (Bottom)
    # Shaft: (181, 151) to (91, 151)
    draw.line([(181, 151), (91, 151)], fill=arrow_color, width=width)
    # Head: (91, 151) pointing to (76, 151)
    draw.polygon([(76, 151), (101, 131), (101, 171)], fill=arrow_color)
    
    # Save as ICO (supporting multiple resolutions)
    ico_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save("icon.ico", sizes=ico_sizes)
    print("icon.ico successfully generated.")

if __name__ == "__main__":
    create_minimal_icon()
