import os
from PIL import Image

def fix_pngs(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.png'):
                filepath = os.path.join(root, file)
                try:
                    img = Image.open(filepath)
                    data = list(img.getdata()) if not hasattr(img, 'get_flattened_data') else list(img.get_flattened_data())
                    img_without_exif = Image.new(img.mode, img.size)
                    img_without_exif.putdata(data)
                    img_without_exif.save(filepath, "PNG")
                    print(f"Fixed: {filepath}")
                except Exception as e:
                    print(f"Failed to fix {filepath}: {e}")

fix_pngs('assets/')
print("Done!")