"""
Generate Traditional Chinese (zhTW) language assets for d4lf.

Unlike gen_data.py which depends on d4data (English-only repo), this script
sources all zhTW data from D4Companion which has authoritative Blizzard-extracted
multilingual data.

Strategy:
  - Match D4Companion enUS <-> zhTW entries by IdName (language-independent).
  - For affixes/aspects/uniques: keep enUS-derived snake_case keys, swap values to Chinese.
  - This preserves cross-language YAML profile portability where possible.

Usage:
  python -m src.tools.gen_data_zhTW <path-to-D4Companion-repo>

Example:
  python -m src.tools.gen_data_zhTW C:\\code\\Diablo4Companion
"""
import json
import re
from pathlib import Path

D4LF_BASE_DIR = Path(__file__).parent.parent.parent
LANG = "zhTW"
OUT_DIR = D4LF_BASE_DIR / f"assets/lang/{LANG}"


# Reuse the description-cleaning logic from gen_data.py for English-side processing
def remove_content_in_braces(input_string: str) -> str:
    pattern = r"\{.*?\}"
    result = re.sub(pattern, "", input_string)
    pattern = r"\[.*?\]"
    result = re.sub(pattern, "", result)
    result = re.sub(r"#%.*?#%", "", result)
    result = re.sub(r"\|.*?:", "|:", result)
    result = result.replace("|", "")
    result = result.replace(";", "")
    result = re.sub(r"(\d)[, ]+(\d)", r"\1\2", result)
    result = re.sub(r"(\+)?\d+(\.\d+)?%?", "", result)
    result = re.sub(r"[\[\]+\-:%\'\#]", "", result)
    result = " ".join(result.split())
    return result.strip()


def clean_zh_value(s: str) -> str:
    """Clean a zhTW DescriptionClean / Description for matching against TTS output.

    The TTS reads the displayed item text. Game text often contains:
      - placeholder markers like # for numbers
      - control codes in {curly} or [square] brackets
      - newline / carriage-return characters
    We strip those and collapse whitespace so values match what TTS speaks.
    """
    if not s:
        return s
    s = s.replace("\r", " ").replace("\n", " ")
    # Remove embedded curly/square bracket control sequences
    s = re.sub(r"\{[^{}]*\}", "", s)
    s = re.sub(r"\[[^\[\]]*\]", "", s)
    # Remove numeric placeholders (# and surrounding %)
    s = s.replace("#%", "").replace("#", "")
    s = s.replace("+", "")
    # Collapse whitespace, but DO NOT touch full-width punctuation, those are part of TTS
    s = re.sub(r"\s+", " ", s).strip()
    return s


def gen_affixes(companion_dir: Path) -> None:
    """Generate affixes.json for zhTW.

    Match enUS <-> zhTW by IdSno (the most stable identifier).
    enUS produces the snake_case key; zhTW DescriptionClean produces the value.
    """
    print(f"=== Generating affixes for {LANG} ===")
    with (companion_dir / "D4Companion/Data/Affixes.enUS.json").open(encoding="utf-8") as f:
        en_data = json.load(f)
    with (companion_dir / f"D4Companion/Data/Affixes.{LANG}.json").open(encoding="utf-8") as f:
        zh_data = json.load(f)

    # Build IdSno -> zhTW DescriptionClean mapping
    zh_by_sno: dict[str, str] = {}
    for entry in zh_data:
        sno = entry.get("IdSno", "")
        desc = clean_zh_value(entry.get("DescriptionClean", ""))
        if sno and desc:
            zh_by_sno[sno] = desc

    # Process enUS the same way gen_data.py does, then pair with zhTW value.
    # Multiple enUS entries can collide on the same snake_case key (e.g. a pure
    # "Movement Speed" affix and a "+#% Attack Speed +#% Movement Speed" combined
    # affix both produce key "movement_speed"). For zhTW the values differ, so we
    # need a tiebreaker: prefer the entry with the SHORTEST zhTW DescriptionClean
    # (canonical pure affix) and the FEWEST AffixAttributes (single-effect).
    candidates: dict[str, list[tuple[int, int, str, str]]] = {}
    for affix in en_data:
        en_desc: str = affix.get("Description", "")
        en_desc = en_desc.lower().strip().replace("'", "").replace("\u2019", "").replace(".", "")
        en_desc = remove_content_in_braces(en_desc)
        en_desc = en_desc.removeprefix("x ")
        en_key = en_desc.replace(",", "").replace(" ", "_")
        if len(en_desc) <= 2:
            continue

        sno = affix.get("IdSno", "")
        zh_value = zh_by_sno.get(sno)
        attr_count = len(affix.get("AffixAttributes", []))
        if zh_value:
            zh_len = len(zh_value)
            candidates.setdefault(en_key, []).append((attr_count, zh_len, zh_value, en_desc))
        else:
            candidates.setdefault(en_key, []).append((attr_count, len(en_desc), en_desc, en_desc))

    out: dict[str, str] = {}
    matched, missed = 0, 0
    for key, opts in candidates.items():
        # Sort by (fewest attributes, shortest zh value); first wins
        opts.sort(key=lambda t: (t[0], t[1]))
        chosen = opts[0]
        out[key] = chosen[2]
        # Track whether the chosen value is a real Chinese translation (vs en fallback)
        if any(0x4E00 <= ord(c) <= 0x9FFF for c in chosen[2]):
            matched += 1
        else:
            missed += 1

    # Apply custom_affixes_zhTW.json overrides if present
    custom_path = D4LF_BASE_DIR / f"src/tools/data/custom_affixes_{LANG}.json"
    if custom_path.exists():
        with custom_path.open(encoding="utf-8") as f:
            for k, v in json.load(f).items():
                out[k] = v

    out_path = OUT_DIR / "affixes.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=4, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print(f"  Wrote {out_path} ({len(out)} entries; matched={matched}, fallback_to_en={missed})")


def gen_aspects(companion_dir: Path) -> None:
    """Generate aspects.json for zhTW.

    Format is a flat list of aspect display names. The runtime matches TTS
    output against this list. For zhTW we use the Name field from D4Companion.
    """
    print(f"=== Generating aspects for {LANG} ===")
    with (companion_dir / f"D4Companion/Data/Aspects.{LANG}.json").open(encoding="utf-8") as f:
        data = json.load(f)

    aspects: set[str] = set()
    for entry in data:
        if not entry.get("IsCodex", False):
            # gen_data.py iterates *all* aspect files. We mirror that by including everything.
            pass
        name = (entry.get("Name") or "").strip()
        if not name:
            continue
        # Normalize: strip trailing markers like "之" suffix is intentional in Chinese, keep as-is
        # Lowercase doesn't apply to CJK; just strip whitespace.
        name = re.sub(r"\s+", "", name)
        # Skip placeholder-looking entries (English placeholders in zhTW data)
        if all(ord(c) < 128 for c in name):
            continue
        aspects.add(name)

    out_list = sorted(aspects)
    out_path = OUT_DIR / "aspects.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out_list, f, indent=4, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print(f"  Wrote {out_path} ({len(out_list)} aspects)")


def gen_item_types() -> None:
    """Generate item_types.json for zhTW.

    Maps Python ItemType enum names to Chinese display strings. We hand-curate
    this because D4Companion uses different keys; the enum names are stable
    in d4lf source code so we map them directly.
    """
    print(f"=== Generating item_types for {LANG} ===")
    # Hand-curated mapping based on Diablo IV Traditional Chinese in-game terminology.
    # Source: D4 zhTW client tooltips and D4Companion ItemTypes.zhTW.json verification.
    mapping = {
        "Amulet": "護身符",
        "Axe": "斧",
        "Axe2H": "雙手斧",
        "Boots": "靴",
        "Bow": "弓",
        "ChestArmor": "胸甲",
        "Crossbow2H": "弩",
        "Dagger": "匕首",
        "Elixir": "藥水",
        "Flail": "連枷",
        "Focus": "聚能器",
        "Glaive": "斬刀",
        "Gloves": "手套",
        "Helm": "頭盔",
        "Incense": "薰香",
        "Legs": "護腿",
        "Mace": "錘",
        "Mace2H": "雙手錘",
        "Material": "材料",
        "OffHandTotem": "圖騰",
        "Polearm": "長柄武器",
        "Quarterstaff": "齊眉棍",
        "Ring": "戒指",
        "Scythe": "鐮刀",
        "Scythe2H": "雙手鐮刀",
        "Shield": "盾",
        "Sigil": "封印",
        "Staff": "法杖",
        "Sword": "劍",
        "Sword2H": "雙手劍",
        "TemperManual": "淬鍊手冊",
        "Tome": "魔典",
        "Wand": "魔杖",
    }
    out_path = OUT_DIR / "item_types.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=4, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print(f"  Wrote {out_path} ({len(mapping)} types)")


def gen_sigils(companion_dir: Path) -> None:
    """Generate sigils.json for zhTW.

    Output is a nested dict {dungeons, minor, major, positive} mapping snake_case
    English keys -> Chinese display names. We match enUS <-> zhTW by IdName.
    """
    print(f"=== Generating sigils for {LANG} ===")
    with (companion_dir / "D4Companion/Data/Sigils.enUS.json").open(encoding="utf-8") as f:
        en_data = json.load(f)
    with (companion_dir / f"D4Companion/Data/Sigils.{LANG}.json").open(encoding="utf-8") as f:
        zh_data = json.load(f)

    zh_by_id = {e["IdName"]: e for e in zh_data}

    # Group by Type (Dungeon, Minor, Major, Positive) but normalize to lowercase
    # plurals that match d4lf's existing schema
    type_to_section = {
        "Dungeon": "dungeons",
        "Major": "major",
        "Minor": "minor",
        "Positive": "positive",
    }
    sections: dict[str, dict[str, str]] = {v: {} for v in type_to_section.values()}

    for en_entry in en_data:
        sigil_type = en_entry.get("Type", "")
        section = type_to_section.get(sigil_type)
        if not section:
            continue
        en_name = (en_entry.get("Name") or "").strip()
        if not en_name:
            continue
        # Build snake_case English key the same way gen_data.py does
        key = en_name.lower().replace(" ", "_").replace("'", "").replace("\u2019", "")
        key = re.sub(r"[^a-z0-9_-]", "", key)
        if not key:
            continue

        zh_entry = zh_by_id.get(en_entry.get("IdName"))
        zh_value = (zh_entry.get("Name") if zh_entry else "") or en_name
        sections[section][key] = zh_value

    out_path = OUT_DIR / "sigils.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(sections, f, indent=4, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    counts = {k: len(v) for k, v in sections.items()}
    print(f"  Wrote {out_path} {counts}")


def gen_uniques(companion_dir: Path) -> None:
    """Generate uniques.json for zhTW.

    Format: {key: {num_inherents: N}} where key is the unique's normalized
    display name. For zhTW we use the Chinese unique name as the key.
    Matches enUS <-> zhTW by IdNameItem to recover num_inherents from the
    existing enUS uniques.json.
    """
    print(f"=== Generating uniques for {LANG} ===")
    with (companion_dir / "D4Companion/Data/Uniques.enUS.json").open(encoding="utf-8") as f:
        en_data = json.load(f)
    with (companion_dir / f"D4Companion/Data/Uniques.{LANG}.json").open(encoding="utf-8") as f:
        zh_data = json.load(f)

    # Load existing enUS uniques.json to get num_inherents per unique
    with (D4LF_BASE_DIR / "assets/lang/enUS/uniques.json").open(encoding="utf-8") as f:
        en_uniques_d4lf = json.load(f)

    def to_key(name: str) -> str:
        return (
            name.strip()
            .replace(" ", "_")
            .replace("\xa0", "_")
            .lower()
            .replace("\u2019", "")
            .replace("'", "")
            .replace(",", "")
        )

    # Build map: IdNameItem -> snake_case enUS key -> num_inherents
    en_by_id_item: dict[str, str] = {}
    for entry in en_data:
        id_item = entry.get("IdNameItem", "")
        en_name = (entry.get("Name") or "").strip()
        if id_item and en_name:
            en_by_id_item[id_item] = to_key(en_name)

    out: dict[str, dict] = {}
    placeholder_count = 0
    for entry in zh_data:
        zh_name = (entry.get("Name") or "").strip()
        if not zh_name:
            continue
        # Skip placeholder/untranslated entries (pure ASCII names in zhTW data)
        if all(ord(c) < 128 for c in zh_name):
            placeholder_count += 1
            continue
        zh_key = to_key(zh_name)
        # Recover num_inherents via the enUS d4lf uniques.json keyed by enUS name
        en_key = en_by_id_item.get(entry.get("IdNameItem", ""))
        num_inherents = en_uniques_d4lf.get(en_key, {}).get("num_inherents", 0) if en_key else 0
        out[zh_key] = {"num_inherents": num_inherents}

    out_path = OUT_DIR / "uniques.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=4, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print(f"  Wrote {out_path} ({len(out)} uniques; skipped {placeholder_count} placeholders)")


def gen_tributes() -> None:
    """Tributes are not in D4Companion zhTW data. Hand-curated subset.

    This covers the most commonly filtered tributes. Users can extend via custom file.
    """
    print(f"=== Generating tributes for {LANG} ===")
    mapping = {
        # Core Hordes tributes (Vessel of Hatred). Names per official zhTW client.
        "ancestral_tribute_of_armaments": "先祖的軍備貢品",
        "greater_tribute_of_armaments": "強大的軍備貢品",
        "greater_tribute_of_harmony": "強大的和諧貢品",
        "greater_tribute_of_ingenuity": "強大的智慧貢品",
        "greater_tribute_of_refinement": "強大的純化貢品",
        "greater_tribute_of_the_horadrim": "強大的赫拉迪姆貢品",
        "lesser_tribute": "次級貢品",
        "lesser_tribute_of_harmony": "次級和諧貢品",
        "lesser_tribute_of_ingenuity": "次級智慧貢品",
        "lesser_tribute_of_the_horadrim": "次級赫拉迪姆貢品",
        "major_tribute_of_andariel": "主要安達莉爾貢品",
        "minor_tribute_of_andariel": "次要安達莉爾貢品",
        "mythic_tribute_of_armaments": "神話的軍備貢品",
        "tribute_of_andariel": "安達莉爾貢品",
        "tribute_of_armaments": "軍備貢品",
        "tribute_of_ascendance_resolute": "崛起貢品（堅毅）",
        "tribute_of_growth": "生長貢品",
        "tribute_of_harmony": "和諧貢品",
        "tribute_of_heritage": "傳承貢品",
        "tribute_of_ingenuity": "智慧貢品",
        "tribute_of_radiance_resolute": "光輝貢品（堅毅）",
        "tribute_of_refinement": "純化貢品",
        "tribute_of_the_horadrim": "赫拉迪姆貢品",
        "tribute_of_titans": "泰坦貢品",
    }
    out_path = OUT_DIR / "tributes.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=4, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print(f"  Wrote {out_path} ({len(mapping)} tributes — verify against in-game text)")


def gen_tooltips() -> None:
    """tooltips.json: just maps ItemPower to its zhTW phrase."""
    print(f"=== Generating tooltips for {LANG} ===")
    # In Diablo IV zhTW client, the item-level label reads "物品力量"
    mapping = {"ItemPower": "物品力量"}
    out_path = OUT_DIR / "tooltips.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=4, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print(f"  Wrote {out_path}")


def gen_corrections() -> None:
    """Corrections start empty for zhTW; populate as TTS quirks are discovered."""
    print(f"=== Generating corrections for {LANG} ===")
    payload = {
        "bad_tts_uniques": {},
        "error_map": {},
        "filter_after_keyword": [
            "需要等級",
            "需要世界",
            "空插槽",
            "出售價值",
        ],
        "filter_words": [],
    }
    out_path = OUT_DIR / "corrections.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print(f"  Wrote {out_path}")


def main(companion_app_dir: Path) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gen_affixes(companion_app_dir)
    gen_aspects(companion_app_dir)
    gen_item_types()
    gen_sigils(companion_app_dir)
    gen_uniques(companion_app_dir)
    gen_tributes()
    gen_tooltips()
    gen_corrections()
    print("\n=== Done ===")
    print(f"Output: {OUT_DIR}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate zhTW language assets for d4lf")
    parser.add_argument("companion_app_dir", type=str, help="Path to Diablo4Companion repo")
    args = parser.parse_args()

    p = Path(args.companion_app_dir)
    if not (p.exists() and p.is_dir()):
        raise SystemExit(f"Path does not exist or is not a directory: {p}")
    main(p)
