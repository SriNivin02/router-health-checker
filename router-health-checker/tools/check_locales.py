"""Verifies all locale JSON files have identical keys and no missing translations."""
import json
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / "static" / "locales"

REQUIRED_LANGUAGES = ["en", "hi", "ta", "te", "kn", "ml", "bn", "mr", "ur", "ar", "es", "fr"]

def check_locales() -> bool:
    en_path = LOCALES_DIR / "en.json"
    if not en_path.exists():
        print(f"FAIL: English base locale {en_path} does not exist.")
        return False

    with open(en_path, "r", encoding="utf-8") as f:
        en_data = json.load(f)
    en_keys = set(en_data.keys())

    print(f"Found base English dictionary with {len(en_keys)} keys.\n")
    all_passed = True

    for lang in REQUIRED_LANGUAGES:
        lang_path = LOCALES_DIR / f"{lang}.json"
        if not lang_path.exists():
            print(f"❌ FAIL: Missing locale file for '{lang}': {lang_path}")
            all_passed = False
            continue

        try:
            with open(lang_path, "r", encoding="utf-8") as f:
                lang_data = json.load(f)
            lang_keys = set(lang_data.keys())

            missing = en_keys - lang_keys
            extra = lang_keys - en_keys

            if missing:
                print(f"❌ FAIL [{lang}.json]: Missing {len(missing)} keys: {list(missing)[:5]}...")
                all_passed = False
            elif extra:
                print(f"⚠️ WARN [{lang}.json]: Extra {len(extra)} keys found.")
            else:
                print(f"✅ PASS [{lang}.json]: All {len(lang_keys)} keys match perfectly.")
        except Exception as e:
            print(f"❌ FAIL [{lang}.json]: Parse error: {e}")
            all_passed = False

    if all_passed:
        print("\n🎉 ALL LOCALES PASSED INTEGRITY CHECK!")
    else:
        print("\n❌ LOCALE INTEGRITY CHECK FAILED.")
    return all_passed

if __name__ == "__main__":
    passed = check_locales()
    sys.exit(0 if passed else 1)
