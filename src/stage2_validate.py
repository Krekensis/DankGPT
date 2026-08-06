import os
import json
import time
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / "data" / "raw-messages"
    
    if not raw_dir.exists():
        print(f"Error: {raw_dir} does not exist.")
        return

    stats = {
        "total_files": 0,
        "total_messages": 0,
        "empty_messages": 0,
        "duplicate_ids": 0,
        "malformed_json_lines": 0,
        "total_replies": 0,
        "missing_parents": 0
    }
    
    all_ids = set()
    all_reply_ids = set()
    total_message_length = 0
    valid_messages = 0

    print(f"Starting validation in {raw_dir}...")
    start_time = time.time()

    for root, _, files in os.walk(raw_dir):
        for file in files:
            if not file.endswith(".jsonl"):
                continue
                
            stats["total_files"] += 1
            file_path = Path(root) / file
            
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                        
                    stats["total_messages"] += 1
                    
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        stats["malformed_json_lines"] += 1
                        continue
                        
                    # Check ID
                    msg_id = data.get("id")
                    if msg_id:
                        if msg_id in all_ids:
                            stats["duplicate_ids"] += 1
                        else:
                            all_ids.add(msg_id)
                            
                    # Check empty messages
                    msg_content = data.get("m", "").strip()
                    if not msg_content:
                        stats["empty_messages"] += 1
                    else:
                        total_message_length += len(msg_content)
                        valid_messages += 1
                        
                    # Check replies
                    reply_id = data.get("reply")
                    if reply_id:
                        stats["total_replies"] += 1
                        all_reply_ids.add(reply_id)

    # Calculate missing parents
    # A parent is missing if it was replied to, but is not in our dataset
    missing_parents = all_reply_ids - all_ids
    stats["missing_parents"] = len(missing_parents)
    
    avg_length = total_message_length / valid_messages if valid_messages > 0 else 0
    
    end_time = time.time()
    
    report = {
        "execution_time_seconds": round(end_time - start_time, 2),
        "statistics": stats,
        "average_message_length": round(avg_length, 2),
        "unique_messages_tracked": len(all_ids)
    }
    
    print("\nValidation Complete. Report:")
    print(json.dumps(report, indent=4))
    
    # Save report
    report_path = base_dir / "data" / "validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    print(f"\nReport saved to {report_path}")

if __name__ == "__main__":
    main()
