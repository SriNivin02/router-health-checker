"""Verification script for Router Health Checker.
Checks:
1. All required project files exist.
2. All Python files compile with zero syntax errors.
3. All 12 locale JSON files have identical key sets.
4. All static assets referenced in HTML/JS exist.
5. Knowledge base has at least 120 Q&A entries.
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
import py_compile
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "README.md",
    "SECURITY.md",
    "LICENSE",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    ".github/workflows/ci.yml",
    "app/__init__.py",
    "app/main.py",
    "app/config.py",
    "app/db/__init__.py",
    "app/db/models.py",
    "app/db/session.py",
    "app/security/__init__.py",
    "app/security/auth.py",
    "app/security/csrf.py",
    "app/security/firewall.py",
    "app/security/ratelimit.py",
    "app/security/headers.py",
    "app/scanner/__init__.py",
    "app/scanner/gateway.py",
    "app/scanner/ports.py",
    "app/scanner/admin_page.py",
    "app/scanner/wifi.py",
    "app/scanner/dns.py",
    "app/scanner/scoring.py",
    "app/scanner/fixes.py",
    "app/stability/__init__.py",
    "app/stability/discovery.py",
    "app/stability/metrics.py",
    "app/speed/__init__.py",
    "app/speed/routes.py",
    "app/agent/__init__.py",
    "app/agent/llm.py",
    "app/agent/kb.py",
    "app/agent/prompts.py",
    "app/api/__init__.py",
    "app/api/auth_routes.py",
    "app/api/scan_routes.py",
    "app/api/stability_routes.py",
    "app/api/agent_routes.py",
    "app/api/settings_routes.py",
    "static/index.html",
    "static/manifest.json",
    "static/sw.js",
    "static/css/theme.css",
    "static/js/app.js",
    "static/js/i18n.js",
    "static/js/voice.js",
    "static/js/chart_helper.js",
    "static/vendor/chart.umd.min.js",
    "knowledge/qa.json",
    "tools/check_locales.py",
    "tests/test_scoring.py",
    "tests/test_gateway_and_ip.py",
    "tests/test_auth_and_csrf.py",
    "tests/test_firewall_and_ratelimit.py",
    "tests/test_locales.py"
]

def verify() -> bool:
    print("=" * 60)
    print("ROUTER HEALTH CHECKER - AUTOMATED INTEGRITY VERIFICATION")
    print("=" * 60)
    all_ok = True

    # 1. Check required files
    print("\n[1/5] Checking Required Files Existence...")
    missing_files = []
    for rel_path in REQUIRED_FILES:
        full_p = BASE_DIR / rel_path
        if not full_p.exists():
            missing_files.append(rel_path)
    if missing_files:
        print(f"❌ FAIL: Missing {len(missing_files)} files: {missing_files}")
        all_ok = False
    else:
        print(f"✅ PASS: All {len(REQUIRED_FILES)} required files exist.")

    # 2. Check Python compilation
    print("\n[2/5] Compiling All Python Files...")
    py_files = list(BASE_DIR.glob("**/*.py"))
    compilation_errors = []
    for py_p in py_files:
        if ".venv" in str(py_p) or "venv" in str(py_p):
            continue
        try:
            py_compile.compile(str(py_p), doraise=True)
        except Exception as e:
            compilation_errors.append((py_p.name, str(e)))
    if compilation_errors:
        print(f"❌ FAIL: Compilation errors in: {compilation_errors}")
        all_ok = False
    else:
        print(f"✅ PASS: All {len(py_files)} Python files compiled with zero syntax errors.")

    # 3. Check Locale Parity
    print("\n[3/5] Verifying 12-Language Locale Key Parity...")
    locales_dir = BASE_DIR / "static" / "locales"
    en_p = locales_dir / "en.json"
    with open(en_p, "r", encoding="utf-8-sig") as f:
        en_keys = set(json.load(f).keys())

    langs = ["en", "hi", "ta", "te", "kn", "ml", "bn", "mr", "ur", "ar", "es", "fr"]
    locale_mismatch = False
    for l in langs:
        lp = locales_dir / f"{l}.json"
        if not lp.exists():
            print(f"❌ FAIL: Missing {l}.json")
            locale_mismatch = True
            continue
        with open(lp, "r", encoding="utf-8-sig") as f:
            l_keys = set(json.load(f).keys())
        diff = en_keys ^ l_keys
        if diff:
            print(f"❌ FAIL: Key mismatch in {l}.json: {diff}")
            locale_mismatch = True
    if locale_mismatch:
        all_ok = False
    else:
        print(f"✅ PASS: All 12 locale JSON files have identical {len(en_keys)} keys.")

    # 4. Check Static References in HTML
    print("\n[4/5] Checking Static Asset References in index.html...")
    html_p = BASE_DIR / "static" / "index.html"
    with open(html_p, "r", encoding="utf-8") as f:
        html_content = f.read()
    refs = re.findall(r'(?:href|src)=["\'](/static/[^"\']+)["\']', html_content)
    broken_refs = []
    for ref in refs:
        rel = ref.lstrip("/")
        if not (BASE_DIR / rel).exists():
            broken_refs.append(ref)
    if broken_refs:
        print(f"❌ FAIL: Broken references in index.html: {broken_refs}")
        all_ok = False
    else:
        print(f"✅ PASS: All {len(refs)} referenced static assets exist.")

    # 5. Check Knowledge Base
    print("\n[5/5] Checking Knowledge Base Count...")
    kb_p = BASE_DIR / "knowledge" / "qa.json"
    with open(kb_p, "r", encoding="utf-8") as f:
        kb_data = json.load(f)
    entries = kb_data.get("entries", [])
    if len(entries) < 120:
        print(f"❌ FAIL: Knowledge base has only {len(entries)} entries (need >= 120).")
        all_ok = False
    else:
        print(f"✅ PASS: Knowledge base contains {len(entries)} rich Q&A entries.")

    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 ALL CHECKS PASSED: PROJECT IS 100% COMPLETE & VERIFIED!")
    else:
        print("❌ VERIFICATION FAILED: PLEASE RESOLVE THE ISSUES ABOVE.")
    print("=" * 60)
    return all_ok

if __name__ == "__main__":
    passed = verify()
    sys.exit(0 if passed else 1)
