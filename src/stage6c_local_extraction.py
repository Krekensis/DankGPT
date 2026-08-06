import json
import shutil
import time
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
if not os.environ.get("HF_TOKEN"):
    print("WARNING: HF_TOKEN not found in environment. Make sure it's in your .env file.")

# -----------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------
INPUT_FILE      = "data/filtered-split/filtered_1.jsonl"
OUTPUT_FILE     = "data/extracted-split/extracted_knowledge_1.jsonl"
CHECKPOINT_FILE = "data/extracted-split/checkpoint_1.txt"
MODEL_ID        = "hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4"
BATCH_SIZE      = 100
MAX_TOKENS      = 512

# -----------------------------------------------------------------------
# RESUME DETECTION
# -----------------------------------------------------------------------
start_index = 0

if Path(CHECKPOINT_FILE).exists():
    start_index = int(Path(CHECKPOINT_FILE).read_text().strip())
    print(f"Checkpoint found: resuming from conversation index {start_index:,}")
else:
    print("No checkpoint found — starting fresh.")
    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------
# LOAD CONVERSATIONS
# -----------------------------------------------------------------------
conversations = []
if Path(INPUT_FILE).exists():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    conversations.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
else:
    print(f"ERROR: Input file {INPUT_FILE} not found. Please adjust the path.")
    exit(1)

# File is already pre-sorted by quality score from stage 6a!
remaining = conversations[start_index:]
print(f"Loaded {len(conversations):,} total from split file, {len(remaining):,} to process this session.")

# -----------------------------------------------------------------------
# INIT VLLM
# -----------------------------------------------------------------------
print("Loading model...")
from vllm import LLM, SamplingParams

llm = LLM(
    model=MODEL_ID,
    tensor_parallel_size=1,
    dtype="float16",
    max_model_len=8192,
    gpu_memory_utilization=0.85,
    enforce_eager=True,
)
sampling_params = SamplingParams(temperature=0.1, max_tokens=MAX_TOKENS)
print("Model loaded.")

# -----------------------------------------------------------------------
# PROMPT BUILDER
# -----------------------------------------------------------------------
SYSTEM_PROMPT = """You are an elite Knowledge Extraction AI for Dank Memer, a massive Discord economy/RPG bot.
Your sole purpose is to extract highly specific, wiki-worthy game mechanics from raw Discord conversations.
We only care about hard facts, numbers, optimal strategies, and hidden mechanics.

CRITICAL EXTRACTION TARGETS (Hunt for these!):
- **Items & Market**: Specific item uses, crafting recipes, drop rates, market strategies, hidden interactions.
- **Fishing & Minigames**: Bait mechanics, fish variants, boss fighting strategies, location unlocks, skill challenges.
- **Commands & Cooldowns**: Exact command behaviors, optimal multi-command grinding setups, cooldown times.
- **Min-Maxing & Meta**: High-level player strategies, XP multiplier stacking, prestige/omega requirements.

STRICT REJECTION RULES (Ignore these entirely!):
1. NO GENERIC FLUFF: Ignore obvious/common sense advice (e.g., "Grinding gets you money", "Voting gives rewards", "Check the guide").
2. NO CHAT STATE: Do not extract anything about the users talking (e.g., "User doesn't have a fishing rod", "User asked how to fish").
3. NO SPECULATION: If players are guessing or unsure, ignore it completely.
4. PRESERVE URLs: If a conversation contains a helpful URL (like a spreadsheet or guide), you MUST include the exact URL inside your extracted knowledge text. Do not just say "a link provides X".
5. NEVER reference usernames or session-specific data (e.g. "Flow QM60YP is invalid").
6. NEVER extract empty strategy stubs like "Follow these strats" with no actual strats given.
7. NEVER extract opinions or personal choices (e.g. "Prestige is up to the player").

OUTPUT FORMAT:
Output ONLY a JSON array of objects. Each object must have exactly these fields:
  - topic: A highly specific 1-4 word category (e.g., "Weighted Bait Strategy", "Lasso Epique Market", "Prestige Coin Multipliers").
  - knowledge: The extracted fact written as a standalone, objective, Wikipedia-style sentence. MUST contain the specific details (names, numbers, items, URLs) mentioned in the chat.
  - category: One of ["Item", "Mechanic", "Strategy", "Economy", "Fishing", "Other"]
  - confidence: "high" (stated as fact) or "medium" (inferred).

If the conversation contains NO high-value, specific game knowledge, you MUST output an empty array: []
Output ONLY valid JSON. Do not include markdown formatting, backticks, or explanations."""


def build_prompt(conversation: dict) -> str:
    lines = [f"- {m.get('m', '').strip()}" for m in conversation.get("messages", []) if m.get("m", "").strip()]
    chat_text = "\n".join(lines)

    return (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n\n"
        f"{SYSTEM_PROMPT}<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n\n"
        f"Extract knowledge from this Discord conversation:\n\n{chat_text}<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    )


def parse_output(raw: str, conv_root_id: str) -> list:
    try:
        start = raw.index("[")
        facts = json.loads(raw[start:])
        if not isinstance(facts, list):
            return []
        valid = []
        for f in facts:
            if isinstance(f, dict) and f.get("topic") and f.get("knowledge"):
                f["source_conv"] = conv_root_id
                valid.append(f)
        return valid
    except (ValueError, json.JSONDecodeError):
        return []

print("Prompt builder ready.")

# -----------------------------------------------------------------------
# EXECUTION
# -----------------------------------------------------------------------
total_facts = 0
session_start = time.time()
current_index = start_index

with open(OUTPUT_FILE, "a", encoding="utf-8") as out_f:
    for batch_start in range(0, len(remaining), BATCH_SIZE):
        batch    = remaining[batch_start : batch_start + BATCH_SIZE]
        prompts  = [build_prompt(c) for c in batch]
        root_ids = [c.get("root_id", "") for c in batch]

        outputs = llm.generate(prompts, sampling_params)

        for output, root_id in zip(outputs, root_ids):
            facts = parse_output(output.outputs[0].text, root_id)
            for fact in facts:
                out_f.write(json.dumps(fact) + "\n")
                total_facts += 1

        current_index = start_index + batch_start + len(batch)

        out_f.flush()
        Path(CHECKPOINT_FILE).write_text(str(current_index))

        elapsed         = time.time() - session_start
        rate            = (batch_start + len(batch)) / elapsed
        remaining_count = len(remaining) - batch_start - len(batch)
        eta_min         = remaining_count / rate / 60 if rate > 0 else 0

        print(
            f"[{current_index:>7}/{len(conversations)}] "
            f"Facts: {total_facts:,} | "
            f"Rate: {rate:.0f}/s | "
            f"ETA: {eta_min:.1f}min"
        )

print(f"\nSession complete. Processed up to index {current_index:,}/{len(conversations):,}")
print(f"Total facts extracted this session: {total_facts:,}")
if Path(OUTPUT_FILE).exists():
    print(f"Output: {OUTPUT_FILE} ({Path(OUTPUT_FILE).stat().st_size / 1_048_576:.1f} MB)")
