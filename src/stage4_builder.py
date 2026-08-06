import os
import json
import time
import sys
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    clean_dir = base_dir / "data" / "clean-messages"
    out_file = base_dir / "data" / "conversations.jsonl"
    
    if not clean_dir.exists():
        print(f"Error: {clean_dir} does not exist. Run stage 3 first.")
        return

    print("Loading messages into memory...")
    start_time = time.time()

    messages = {}
    children = {}

    files_processed = 0
    total_messages = 0

    for root, _, files in os.walk(clean_dir):
        for file in files:
            if not file.endswith(".jsonl"):
                continue
            files_processed += 1
            file_path = Path(root) / file
            
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        msg_id = data.get("id")
                        if not msg_id:
                            continue
                            
                        messages[msg_id] = data
                        total_messages += 1
                        
                        reply_id = data.get("reply")
                        if reply_id:
                            if reply_id not in children:
                                children[reply_id] = []
                            children[reply_id].append(msg_id)
                            
                    except json.JSONDecodeError:
                        continue

    print(f"Loaded {total_messages} messages from {files_processed} files in {round(time.time() - start_time, 2)}s.")
    print("Building conversation trees...")
    
    # Identify roots: messages that either don't reply to anything, or reply to something NOT in our dataset
    roots = []
    for msg_id, data in messages.items():
        reply_id = data.get("reply")
        if not reply_id or reply_id not in messages:
            roots.append(msg_id)
            
    print(f"Found {len(roots)} conversation roots.")
    
    def build_tree(node_id):
        """Recursively builds the tree in chronological order (DFS) or just collects them."""
        # We will collect messages in order. To make it a flat list of messages in chronological order:
        # Actually, flattening the tree into a list of messages sorted by timestamp is easiest.
        tree_msgs = [messages[node_id]]
        if node_id in children:
            for child_id in children[node_id]:
                tree_msgs.extend(build_tree(child_id))
        return tree_msgs

    conversations_written = 0
    
    with open(out_file, "w", encoding="utf-8") as out_f:
        for root_id in roots:
            conversation = build_tree(root_id)
            # Sort by timestamp just in case
            conversation.sort(key=lambda x: x.get("t", 0))
            
            # Format: wrap in an object to store metadata later
            conv_data = {
                "root_id": root_id,
                "messages": conversation
            }
            
            out_f.write(json.dumps(conv_data) + "\n")
            conversations_written += 1

    print(f"Successfully built and wrote {conversations_written} conversations to {out_file}.")
    print(f"Total time: {round(time.time() - start_time, 2)}s.")

if __name__ == "__main__":
    main()
