import os
import json
import time
import re
from pathlib import Path

# Regex patterns to remove
# Matches Discord emojis: <:name:id> or <a:name:id>
EMOJI_PATTERN = re.compile(r"<a?:[a-zA-Z0-9_]+:[0-9]+>")
# Matches Discord mentions: <@id>, <@!id>, <@&id>, <#id>
MENTION_PATTERN = re.compile(r"<@[!&]?[0-9]+>|<#[0-9]+>")

def clean_message_content(content):
    if not content:
        return ""
        
    # Remove zero-width characters
    content = content.replace("\u200b", "")
    content = content.replace("\u200c", "")
    content = content.replace("\u200d", "")
    content = content.replace("\ufeff", "")
    
    # Remove emojis and mentions
    content = EMOJI_PATTERN.sub("", content)
    content = MENTION_PATTERN.sub("", content)
    
    # Trim whitespace
    content = content.strip()
    return content

def main():
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / "data" / "raw-messages"
    clean_dir = base_dir / "data" / "clean-messages"
    
    if not raw_dir.exists():
        print(f"Error: {raw_dir} does not exist.")
        return

    stats = {
        "files_processed": 0,
        "messages_read": 0,
        "messages_written": 0,
        "empty_messages_dropped": 0
    }

    print(f"Starting cleaning process from {raw_dir} to {clean_dir}...")
    start_time = time.time()

    for root, _, files in os.walk(raw_dir):
        for file in files:
            if not file.endswith(".jsonl"):
                continue
                
            stats["files_processed"] += 1
            
            # Determine relative path to recreate directory structure
            rel_path = Path(root).relative_to(raw_dir)
            out_dir = clean_dir / rel_path
            out_dir.mkdir(parents=True, exist_ok=True)
            
            in_file_path = Path(root) / file
            out_file_path = out_dir / file
            
            with open(in_file_path, "r", encoding="utf-8") as in_f, \
                 open(out_file_path, "w", encoding="utf-8") as out_f:
                
                for line in in_f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    stats["messages_read"] += 1
                    
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                        
                    original_content = data.get("m", "")
                    cleaned_content = clean_message_content(original_content)
                    
                    if not cleaned_content:
                        stats["empty_messages_dropped"] += 1
                        continue
                        
                    # Update content and write
                    data["m"] = cleaned_content
                    
                    out_f.write(json.dumps(data) + "\n")
                    stats["messages_written"] += 1

    end_time = time.time()
    
    print("\nCleaning Complete. Statistics:")
    print(json.dumps(stats, indent=4))
    print(f"Execution time: {round(end_time - start_time, 2)} seconds")

if __name__ == "__main__":
    main()
