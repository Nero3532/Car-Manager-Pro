from PIL import Image, ImageDraw, ImageFont
import os

def create_logo():
    # Size for the icon (standard ico sizes include 16, 32, 48, 64, 128, 256)
    size = (256, 256)
    
    # Create a new image with transparency
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background: Rounded Rectangle / Circle style (Deep Blue)
    # Using a circle for a modern app look
    margin = 10
    draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], fill='#0056b3', outline='#004494', width=5)
    
    # Draw a stylized car front or text
    # Since drawing a complex car is hard with basic shapes, we'll use stylized text "CM" and a simple car outline
    
    # Simple Car Body (White)
    car_y = 140
    car_width = 160
    car_height = 60
    car_x = (size[0] - car_width) // 2
    
    # Car bottom part
    draw.rectangle([car_x, car_y, car_x + car_width, car_y + car_height], fill='white')
    
    # Car top part (roof)
    roof_width = 100
    roof_height = 50
    roof_x = (size[0] - roof_width) // 2
    roof_y = car_y - roof_height
    
    # Draw roof as a polygon to make it look like a car
    draw.polygon([
        (roof_x, car_y),  # Bottom left of roof
        (roof_x + 10, roof_y), # Top left
        (roof_x + roof_width - 10, roof_y), # Top right
        (roof_x + roof_width, car_y) # Bottom right
    ], fill='white')
    
    # Windows (Blueish)
    win_margin = 5
    draw.polygon([
        (roof_x + win_margin + 5, car_y - win_margin),
        (roof_x + 10 + win_margin, roof_y + win_margin),
        (roof_x + roof_width - 10 - win_margin, roof_y + win_margin),
        (roof_x + roof_width - win_margin - 5, car_y - win_margin)
    ], fill='#e6f2ff')
    
    # Wheels (Black)
    wheel_radius = 25
    wheel_y = car_y + car_height
    
    # Left wheel
    draw.ellipse([car_x + 20, wheel_y - wheel_radius, car_x + 20 + wheel_radius*2, wheel_y + wheel_radius], fill='#333333')
    draw.ellipse([car_x + 30, wheel_y - wheel_radius + 10, car_x + 30 + (wheel_radius*2 - 20), wheel_y + wheel_radius - 10], fill='#888888')
    
    # Right wheel
    draw.ellipse([car_x + car_width - 20 - wheel_radius*2, wheel_y - wheel_radius, car_x + car_width - 20, wheel_y + wheel_radius], fill='#333333')
    draw.ellipse([car_x + car_width - 30 - (wheel_radius*2 - 20), wheel_y - wheel_radius + 10, car_x + car_width - 30, wheel_y + wheel_radius - 10], fill='#888888')

    # Text "Pro"
    # Note: Default font is used because we can't guarantee system fonts
    # Drawing simple lines for "PRO" on the car body if needed, or just leave it clean
    
    # Save as ICO
    img.save('app_icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Icon created: app_icon.ico")

if __name__ == "__main__":
    create_logo()
