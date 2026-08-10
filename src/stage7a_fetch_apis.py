import urllib.request
import json
import os
import time

API_ENDPOINTS = {
    "items": "https://dankstats.onrender.com/api/scraped?id=items",
    "pets": "https://dankstats.onrender.com/api/scraped?id=pets",
    "fish": "https://dankstats.onrender.com/api/scraped?id=fish",
    "changelogs": "https://dankstats.onrender.com/api/scraped?id=changelogs"
}

OUTPUT_FILE = "data/extracted-split/api_knowledge.jsonl"

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def process_items(data):
    knowledge_items = []
    for item in data.get("data", []):
        name = item.get("name", "Unknown Item")
        type_ = item.get("type", "Item")
        rarity = item.get("rarity", "Common")
        value = item.get("value", 0)
        net = item.get("netValue", 0)
        flavor = item.get("flavor", "")
        details = item.get("details", "")
        
        knowledge = f"{name} is a {rarity} {type_} item. Base value is {value}. Net value is {net}. Flavor text: {flavor} Details: {details}".strip()
        knowledge_items.append({
            "topic": f"Item: {name}",
            "knowledge": knowledge,
            "category": "Items",
            "confidence": "high",
            "raw_data": item
        })
    return knowledge_items

def process_pets(data):
    knowledge_items = []
    for pet in data.get("data", []):
        name = pet.get("name", "Unknown Pet")
        cost = pet.get("cost", 0)
        stats = pet.get("stats", {})
        phrases = pet.get("phrases", [])
        
        hunger = stats.get("hunger", 0)
        hygiene = stats.get("hygiene", 0)
        energy = stats.get("energy", 0)
        fun = stats.get("fun", 0)
        
        knowledge = f"Pet: {name}. Cost: {cost}. Base stats - Hunger: {hunger}, Hygiene: {hygiene}, Energy: {energy}, Fun: {fun}. Phrases: {', '.join(phrases[:3])}."
        knowledge_items.append({
            "topic": f"Pet: {name}",
            "knowledge": knowledge,
            "category": "Pets",
            "confidence": "high",
            "raw_data": pet
        })
    return knowledge_items

def process_fish(data):
    knowledge_items = []
    try:
        fish_data = data["data"][0]["data"]
        items = fish_data.get("creatures", {}).get("items", [])
    except (KeyError, IndexError):
        return []
        
    for fish in items:
        name = fish.get("name", "Unknown Fish")
        extra = fish.get("extra", {})
        rarity = extra.get("rarity", "Common")
        is_boss = "Yes" if extra.get("boss") else "No"
        is_mythical = "Yes" if extra.get("mythical") else "No"
        flavor = extra.get("flavor", "")
        
        locations = extra.get("locations", [])
        loc_str = ", ".join(locations) if locations else "Unknown"
        
        knowledge = f"Fish: {name}. Rarity: {rarity}. Boss: {is_boss}. Mythical: {is_mythical}. Found in locations: {loc_str}. Flavor text: {flavor}"
        knowledge_items.append({
            "topic": f"Fish: {name}",
            "knowledge": knowledge,
            "category": "Fish",
            "confidence": "high",
            "raw_data": fish
        })
        
    for npc in fish_data.get("npcs", {}).get("items", []):
        name = npc.get("name", "Unknown NPC")
        bio = npc.get("extra", {}).get("bio", "")
        knowledge = f"Fish NPC: {name}. Bio: {bio}"
        knowledge_items.append({
            "topic": f"NPC: {name}",
            "knowledge": knowledge,
            "category": "Fish",
            "confidence": "high",
            "raw_data": npc
        })
        
    for loc in fish_data.get("locations", {}).get("items", []):
        name = loc.get("name", "Unknown Location")
        type_ = loc.get("extra", {}).get("type", "")
        creatures = len(loc.get("extra", {}).get("creatures", []))
        knowledge = f"Fish Location: {name}. Type: {type_}. Holds {creatures} creatures."
        knowledge_items.append({
            "topic": f"Location: {name}",
            "knowledge": knowledge,
            "category": "Fish",
            "confidence": "high",
            "raw_data": loc
        })

    for tool in fish_data.get("tools", {}).get("items", []):
        name = tool.get("name", "Unknown Tool")
        flavor = tool.get("extra", {}).get("flavor", "")
        knowledge = f"Fish Tool: {name}. Flavor: {flavor}"
        knowledge_items.append({
            "topic": f"Tool: {name}",
            "knowledge": knowledge,
            "category": "Fish",
            "confidence": "high",
            "raw_data": tool
        })
        
    for bait in fish_data.get("baits", {}).get("items", []):
        name = bait.get("name", "Unknown Bait")
        flavor = bait.get("extra", {}).get("flavor", "")
        explanation = bait.get("extra", {}).get("explanation", "")
        knowledge = f"Fish Bait: {name}. Flavor: {flavor}. Effect: {explanation}"
        knowledge_items.append({
            "topic": f"Bait: {name}",
            "knowledge": knowledge,
            "category": "Fish",
            "confidence": "high",
            "raw_data": bait
        })

    for skill in fish_data.get("skills", {}).get("items", []):
        name = skill.get("name", "Unknown Skill")
        desc = skill.get("extra", {}).get("description", "")
        knowledge = f"Fish Skill: {name}. Description: {desc}"
        knowledge_items.append({
            "topic": f"Skill: {name}",
            "knowledge": knowledge,
            "category": "Fish",
            "confidence": "high",
            "raw_data": skill
        })
        
    return knowledge_items

def process_changelogs(data):
    knowledge_items = []
    for update in data.get("data", []):
        title = update.get("title", "Unknown Update")
        content = update.get("content", "").replace('\n', ' ')
        
        knowledge = f"Update {title}: {content}"
        knowledge_items.append({
            "topic": f"Update: {title}",
            "knowledge": knowledge,
            "category": "Changelogs",
            "confidence": "high",
            "raw_data": update
        })
    return knowledge_items

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    all_knowledge = []
    
    print("Fetching APIs...")
    for category, url in API_ENDPOINTS.items():
        print(f"Fetching {category}...")
        try:
            data = fetch_json(url)
            if category == "items":
                items = process_items(data)
            elif category == "pets":
                items = process_pets(data)
            elif category == "fish":
                items = process_fish(data)
            elif category == "changelogs":
                items = process_changelogs(data)
            
            all_knowledge.extend(items)
            print(f"-> Parsed {len(items)} {category} items.")
        except Exception as e:
            print(f"Error fetching {category}: {e}")
            
    print(f"Writing {len(all_knowledge)} total knowledge items to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for k in all_knowledge:
            f.write(json.dumps(k) + "\n")
            
    print("Done!")

if __name__ == "__main__":
    main()
