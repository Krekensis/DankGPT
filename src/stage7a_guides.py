import os
import glob
import json
import re

GUIDES_DIR = "data/guides"
OUTPUT_FILE = "data/extracted-split/guides_knowledge.jsonl"

def clean_discord_text(text):
    # Convert custom Discord emojis like <:DankCoin:1470569275268796487> into "DankCoin"
    text = re.sub(r'<a?:([^:]+):\d+>', r'\1', text)
    return text.strip()

def get_guide_title(text, fallback):
    # Find the first markdown header (# Title or ## Title)
    match = re.search(r'^#+\s+(.+)$', text, flags=re.MULTILINE)
    if match:
        # Strip any formatting just in case
        return match.group(1).replace('*', '').strip()
    return fallback

def process_guides():
    knowledge_items = []
    
    for fpath in glob.glob(os.path.join(GUIDES_DIR, "*.md")):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            
        if not content.strip():
            print(f"Skipping empty file: {fpath}")
            continue
            
        fallback_name = os.path.basename(fpath).replace(".md", "").replace("_", " ").title()
        name = get_guide_title(content, fallback_name)
        
        clean_content = clean_discord_text(content)
        
        # Split large guides by Header 2 (##) so they fit inside the Embedding model's token limits
        sections = re.split(r'(?=^## )', clean_content, flags=re.MULTILINE)
        
        # Filter out empty sections first so enumeration starts at 0 (Part 1) correctly
        valid_sections = [s.strip() for s in sections if s.strip()]
        
        for i, section in enumerate(valid_sections):
            topic_suffix = f" (Part {i+1})" if len(valid_sections) > 1 else ""
                
            knowledge_items.append({
                "topic": f"Guide: {name}{topic_suffix}",
                "knowledge": f"Official Guide - {name}:\n\n{section}",
                "category": "Guides",
                "confidence": "high",
                "raw_data": {"filename": os.path.basename(fpath), "raw_text": section}
            })
        
    print(f"Processed {len(knowledge_items)} guide chunks.")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for item in knowledge_items:
            f.write(json.dumps(item) + "\n")
    
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_guides()
