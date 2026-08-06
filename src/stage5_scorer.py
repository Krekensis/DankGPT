import re
import json
import time
from pathlib import Path

MANUAL_KEYWORDS: dict[str, float] = {
    # General
    "dank": 1.05, "dank memer": 1.70, "dmc": 0.85,
    "economy": 0.85, "currency": 0.75,

    # Community aliases — shorthands players actually use in chat
    "pres": 1.05,               # prestige
    "bal": 0.62,
    "inv": 0.75,                # inventory
    "cd": 0.50,                 # cooldown
    "cf": 0.62,                 # coinflip
    "bj": 0.62,                 # blackjack
    "hl": 0.62,                 # highlow
    "rob": 0.75,                # robbing
    "hunt": 0.75,               # hunting
    "fish": 0.75,               # fishing
    "bet": 0.62,                # betting
    "vote": 0.75,               # voting rewards
    "daily": 0.62,              # daily box / daily reward
    "dailies": 0.62,            # plural of daily
    "shop": 0.62,               # item shop

    # Progression
    "prestige": 1.05, "omega": 1.05, "lvl": 0.62, "level": 0.62, "levels": 0.62,
    "xp": 0.75, "experience": 0.62, "badge": 0.75, "badges": 0.75,
    "achievement": 0.85, "achievements": 0.85, "quest": 0.85, "quests": 0.85,
    "streak": 0.62, "milestone": 0.62, "progression": 0.85,

    # Economy
    "wallet": 0.62, "bank": 0.62, "balance": 0.62, "deposit": 0.62,
    "withdraw": 0.62, "withdrawal": 0.62, "net": 0.40, "networth": 0.85,
    "worth": 0.50, "value": 0.62, "price": 0.50, "pricing": 0.50,
    "inflation": 0.85, "tax": 0.62,

    # Market
    "market": 1.05, "marketplace": 1.05, "trade": 0.95, "trading": 0.95,
    "buyer": 0.50, "seller": 0.50, "offer": 0.50, "offers": 0.50,
    "auction": 0.85, "listing": 0.85, "valuation": 0.85, "demand": 0.85, "supply": 0.85,

    # Game mechanics
    "mechanic": 1.05, "mechanics": 1.05, "cooldown": 1.05, "cooldowns": 1.05,
    "chance": 0.75, "probability": 0.95, "odds": 0.85, "rng": 0.85,
    "drop": 0.75, "drops": 0.75, "drop rate": 1.05,
    "spawn": 0.75, "multiplier": 1.05, "multipliers": 1.05, "multi": 0.75,
    "multis": 0.75, "boost": 0.85, "bonus": 0.75, "modifier": 0.85,
    "cap": 0.62, "limit": 0.62, "limits": 0.62, "scaling": 0.85,

    # Crafting
    "craft": 1.05, "crafted": 0.85, "crafting": 1.05, "forge": 1.05,
    "forging": 1.05, "recipe": 0.95, "recipes": 0.95, "ingredient": 0.85,
    "ingredients": 0.85, "upgrade": 0.85, "upgrades": 0.85,

    # Rarity
    "rarity": 0.95, "common": 0.30, "uncommon": 0.40, "rare": 0.50,
    "epic": 0.62, "legendary": 0.75, "mythic": 0.85, "exclusive": 0.85,
    "limited": 0.85,

    # Gameplay
    "grind": 0.95, "grinding": 0.95, "strategy": 1.05, "strategies": 1.05,
    "guide": 1.05, "guides": 1.05, "tutorial": 1.05, "efficient": 0.95,
    "efficiency": 0.95, "optimal": 1.05, "optimize": 1.05, "optimization": 1.05,
    "maximize": 0.95, "profit": 0.95, "profits": 0.95, "income": 0.85,
    "earnings": 0.85, "farm": 0.85, "farming": 0.85, "method": 0.75,
    "methods": 0.75, "meta": 0.95, "best": 0.40, "fastest": 0.75,

    # Discussion
    "update": 0.75, "updates": 0.75, "patch": 0.95, "patches": 0.95,
    "changelog": 1.05, "announcement": 0.85, "event": 0.85, "events": 0.85,
    "season": 0.85, "release": 0.75, "rework": 0.95, "revamp": 0.95,
    "rebalance": 1.05, "buff": 0.95, "buffed": 0.95, "nerf": 0.95,
    "nerfed": 0.95, "change": 0.50, "changes": 0.50,

    # Quality indicators
    "tested": 1.05, "testing": 0.95, "confirmed": 1.05, "verify": 0.85,
    "verified": 0.95, "proof": 0.85, "evidence": 0.85, "experiment": 0.95,
    "analysis": 1.05, "calculation": 0.95, "formula": 0.95,
    "spreadsheet": 0.95, "statistics": 0.95, "average": 0.62, "expected": 0.62,

    # Community
    "wiki": 1.05, "faq": 0.95, "documentation": 0.95, "support": 0.75,
    "bug": 0.95, "bugs": 0.95, "issue": 0.75, "issues": 0.75,
    "exploit": 1.05, "feature": 0.85, "feedback": 0.85, "suggestion": 0.85,
}

# ---------------------------------------------------------------------------
# Keyword index — built at startup from scraped JSONs + manual list
# Maps lowercase term -> score bonus
# ---------------------------------------------------------------------------

_KEYWORDS: dict[str, float] = {}


def _build_keyword_index(base_dir: Path) -> None:
    scraped = base_dir / "data" / "scraped"

    def _add(term: str, bonus: float) -> None:
        t = term.lower().strip()
        if t and len(t) > 2:
            _KEYWORDS[t] = max(_KEYWORDS.get(t, 0), bonus)

    def _add_item(name: str, bonus: float) -> None:
        """Add item name + fast prefix variants to _KEYWORDS at build time.
        Costs a few ms at startup; zero cost at runtime vs. SequenceMatcher per word.
        Variants: full name, each word, 4-char prefix of each word.
        """
        _add(name, bonus)
        for word in name.split():
            _add(word, bonus)            # first word: "daily" from "Daily Box"
            if len(word) >= 6:
                _add(word[:4], bonus * 0.7)  # 4-char prefix: "dail" from "Daily Box"

    # items.json — item names and itemKeys
    items_path = scraped / "items.json"
    if items_path.exists():
        data = json.loads(items_path.read_text(encoding="utf-8"))
        for item in data.get("data", []):
            _add_item(item.get("name", ""), 2.0)
            _add(item.get("itemKey", ""), 2.0)

    # pets.json — pet names and ids
    pets_path = scraped / "pets.json"
    if pets_path.exists():
        data = json.loads(pets_path.read_text(encoding="utf-8"))
        for pet in data.get("data", []):
            _add_item(pet.get("name", ""), 2.0)
            _add(pet.get("id", ""), 2.0)

    # fish.json — fish/creature names
    fish_path = scraped / "fish.json"
    if fish_path.exists():
        data = json.loads(fish_path.read_text(encoding="utf-8"))
        try:
            items = data["data"][0]["data"]["creatures"]["items"]
            for creature in items:
                _add_item(creature.get("name", ""), 1.5)
                _add(creature.get("id", ""), 1.5)
        except (KeyError, IndexError, TypeError):
            pass

    # changelogs.json — extract capitalized words from titles as topic hints
    changelogs_path = scraped / "changelogs.json"
    if changelogs_path.exists():
        data = json.loads(changelogs_path.read_text(encoding="utf-8"))
        for entry in data.get("data", []):
            title = entry.get("title", "")
            for word in re.findall(r'[A-Z][a-z]{3,}', title):
                _add(word, 1.0)

    # Apply manual overrides (they win if higher)
    for term, bonus in MANUAL_KEYWORDS.items():
        _add(term, bonus)

    print(f"[scorer] Keyword index built: {len(_KEYWORDS)} terms.")


_ALPHA_RE = re.compile(r'[a-zA-Z]')

def is_useless(msg: str) -> bool:
    text = msg.strip()
    if text.startswith(("pls ", "/", "!")):
        return True  # bot commands
    if len(text.split()) < 4:
        return True  # too short to contain real knowledge
    if not _ALPHA_RE.search(text):
        return True  # pure emoji / symbols
    return False


def keyword_bonus(text: str) -> float:
    """Return total keyword score bonus for a block of text (pure exact substring matching)."""
    lower = text.lower()
    bonus = 0.0
    for term, val in _KEYWORDS.items():
        if term in lower:
            bonus += val
    return bonus


def calculate_score(conversation: dict) -> tuple[float, dict]:
    messages = conversation.get("messages", [])
    if not messages:
        return 0, {}

    message_count = len(messages)
    word_count = 0
    contains_question = False
    spam_count = 0
    kw_bonus = 0.0
    newest_t = 0

    for msg in messages:
        content = msg.get("m", "")
        if "?" in content:
            contains_question = True
        word_count += len(content.split())
        if is_useless(content):
            spam_count += 1
        kw_bonus += keyword_bonus(content)
        t = msg.get("t", 0)
        if t > newest_t:
            newest_t = t

    # ponytail: word_count is primary signal; keyword hits rescue short-but-relevant messages.
    useful_count = message_count - spam_count
    score = (word_count / 5) + (useful_count * 1.5) + kw_bonus
    if contains_question:
        score += 3
    score -= (spam_count * 3)

    # Recency bonus — newer conversations score higher, old ones get penalised.
    # t is a Unix ms timestamp; dividing by 1000 gives seconds.
    age_days = (time.time() - newest_t / 1000) / 86400 if newest_t else 9999
    if age_days < 180:
        recency_bonus = 2.0
    elif age_days < 365:
        recency_bonus = 0.5
    elif age_days < 730:
        recency_bonus = -1.0
    else:
        # 2+ year old convo — heavy penalty unless it's a long, keyword-rich discussion
        # (those are likely deep mechanic explanations that remain evergreen).
        is_evergreen = word_count >= 100 and kw_bonus >= 3.0
        recency_bonus = -1.5 if is_evergreen else -4.0
    score += recency_bonus

    metrics = {
        "message_count": message_count,
        "word_count": word_count,
        "contains_question": contains_question,
        "spam_count": spam_count,
        "kw_bonus": round(kw_bonus, 2),
        "recency_bonus": recency_bonus,
        "age_days": round(age_days),
    }

    return round(score, 2), metrics


def main() -> None:
    base_dir = Path(__file__).parent.parent
    in_file = base_dir / "data" / "conversations.jsonl"
    out_file = base_dir / "data" / "high_quality_conversations.jsonl"

    if not in_file.exists():
        print(f"Error: {in_file} does not exist. Run stage 4 first.")
        return

    _build_keyword_index(base_dir)

    SCORE_THRESHOLD = 5.0

    total_processed = 0
    total_kept = 0

    print("Scoring conversations...")
    start_time = time.time()

    with open(in_file, "r", encoding="utf-8") as in_f, \
         open(out_file, "w", encoding="utf-8") as out_f:

        for line in in_f:
            line = line.strip()
            if not line:
                continue
            try:
                conversation = json.loads(line)
            except json.JSONDecodeError:
                continue

            total_processed += 1
            score, metrics = calculate_score(conversation)

            if score >= SCORE_THRESHOLD:
                conversation["quality_score"] = score
                conversation["metrics"] = metrics
                out_f.write(json.dumps(conversation) + "\n")
                total_kept += 1

    print(f"Scoring Complete.")
    print(f"Total Conversations Evaluated: {total_processed}")
    print(f"High Quality Conversations Kept: {total_kept} ({(total_kept/total_processed*100) if total_processed else 0:.2f}%)")
    print(f"Total time: {round(time.time() - start_time, 2)}s.")


if __name__ == "__main__":
    main()
