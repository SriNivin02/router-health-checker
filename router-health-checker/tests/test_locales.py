"""Pytest test to verify locale key parity across all language dictionaries."""
import json
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / "static" / "locales"

REQUIRED_LANGS = ["en", "hi", "ta", "te", "kn", "ml", "bn", "mr", "ur", "ar", "es", "fr"]

def test_all_locales_exist_and_match():
    en_path = LOCALES_DIR / "en.json"
    assert en_path.exists(), "en.json must exist"
    
    with open(en_path, "r", encoding="utf-8") as f:
        en_keys = set(json.load(f).keys())
    assert len(en_keys) >= 50, "en.json should have comprehensive dictionary"

    for lang in REQUIRED_LANGS:
        p = LOCALES_DIR / f"{lang}.json"
        assert p.exists(), f"Locale file {lang}.json must exist"
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            lang_keys = set(data.keys())
            missing = en_keys - lang_keys
            assert len(missing) == 0, f"{lang}.json is missing keys: {missing}"
