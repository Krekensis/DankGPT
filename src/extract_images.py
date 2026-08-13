import json
import os

OUTPUT_FILE = "frontend/public/images.json"
scraped_dir = "data/scraped"

data = {}

def add_image(name, url):
    if not name or not url:
        return
    # Store directly as name: url. If duplicate, we just overwrite (usually fine).
    data[name] = url

def extract_urls(obj):
    if "name" in obj and "imageURL" in obj and obj["imageURL"]:
        add_image(obj["name"], obj["imageURL"])
    
    if "skins" in obj and isinstance(obj["skins"], dict):
        for skin in obj["skins"].values():
            if isinstance(skin, dict) and "name" in skin and "imageURL" in skin:
                add_image(skin["name"], skin["imageURL"])
                
    if "skins" in obj and isinstance(obj["skins"], list):
        for skin in obj["skins"]:
            if isinstance(skin, dict) and "name" in skin and "imageURL" in skin:
                add_image(skin["name"], skin["imageURL"])
                
    if "variants" in obj and isinstance(obj["variants"], dict):
        for variant in obj["variants"].values():
            if isinstance(variant, dict) and "name" in variant and "imageURL" in variant:
                add_image(variant["name"], variant["imageURL"])

# Process Items
with open(os.path.join(scraped_dir, "items.json"), "r", encoding="utf-8") as f:
    items_data = json.load(f).get("data", [])
    for item in items_data:
        extract_urls(item)

# Process Fish
with open(os.path.join(scraped_dir, "fish.json"), "r", encoding="utf-8") as f:
    fish_raw = json.load(f).get("data", [])
    if fish_raw and len(fish_raw) > 0 and "data" in fish_raw[0]:
        fish_data = fish_raw[0]["data"]
        for category, cat_data in fish_data.items():
            if isinstance(cat_data, dict) and "items" in cat_data:
                for item in cat_data["items"]:
                    extract_urls(item)
            
# Process Pets
with open(os.path.join(scraped_dir, "pets.json"), "r", encoding="utf-8") as f:
    pets_data = json.load(f).get("data", [])
    for pet in pets_data:
        extract_urls(pet)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Extracted {len(data)} images to {OUTPUT_FILE}")
