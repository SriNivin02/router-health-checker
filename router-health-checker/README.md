# Router Health Checker 🛡️
> **"Check. Score. Fix."**  
> A defensive, educational, language-independent one-click security diagnostic web app for your Wi-Fi router.

---

## 1. Project Background
Most households, student hostels, and small retail shops never change their router factory defaults. An open port (such as Telnet 23), an 8-digit WPS PIN, or default administrator credentials (`admin/admin`) expose every phone, laptop, and UPI billing machine on the local network.

**Router Health Checker** solves this through a friendly 4-step workflow:
1. **▶️ Run**: Single-click scan trigger from your browser.
2. **🔍 Scan**: Non-intrusive diagnostic checking Wi-Fi encryption, open ports, admin reachability, and DNS.
3. **💯 Score**: Transparent 0–100 health score with clear traffic-light colors (🟢 Excellent, 🟡 Good, 🟠 Fair, 🔴 Risky).
4. **🛠️ Fix**: Exactly **Top 3 Fixes** sorted by points gain, explained with step-by-step guides and audio read-aloud.

---

## 2. Architecture & Folder Structure

```
router-health-checker/
├─ app/
│  ├─ __init__.py
│  ├─ main.py            # FastAPI app, WAF middleware, static mounts
│  ├─ config.py          # Environment settings (.env)
│  ├─ security/
│  │  ├─ auth.py         # Argon2/PBKDF2 hashing & session management
│  │  ├─ csrf.py         # CSRF double-submit token middleware
│  │  ├─ firewall.py     # Application-level WAF inspection (XSS/SQLi/Path traversal)
│  │  ├─ ratelimit.py    # IP and endpoint sliding window rate limiter
│  │  └─ headers.py      # Strict CSP, nosniff, DENY security headers
│  ├─ scanner/
│  │  ├─ gateway.py      # Cross-platform default gateway auto-discovery & RFC1918 validation
│  │  ├─ ports.py        # Socket port scanner (21, 22, 23, 53, 80, 443, 1900, 7547, 8080)
│  │  ├─ admin_page.py   # Admin HTTP/HTTPS reachability & default credential check
│  │  ├─ wifi.py         # OS Wi-Fi encryption & WPS detection (netsh / nmcli)
│  │  ├─ dns.py          # System DNS resolver inspection
│  │  ├─ scoring.py      # Transparent 0-100 scoring algorithm
│  │  └─ fixes.py        # Top 3 prioritized remediation generator
│  ├─ stability/
│  │  ├─ discovery.py    # ARP table parser & OUI MAC vendor lookup
│  │  └─ metrics.py      # Ping latency, jitter, packet loss, stability score
│  ├─ speed/
│  │  └─ routes.py       # Download/Upload streaming and latency test routes
│  ├─ agent/
│  │  ├─ llm.py          # Online LLM proxy with automatic offline fallback
│  │  ├─ kb.py           # Offline knowledge base engine (fuzzy search)
│  │  └─ prompts.py      # Mascot system prompt & safe refusal templates
│  ├─ db/
│  │  ├─ models.py       # Pydantic schemas
│  │  └─ session.py      # SQLite connection & schema initializer
│  └─ api/               # Modular route controllers
├─ static/
│  ├─ index.html         # Reference UI shell with responsive mobile-first tabs
│  ├─ css/theme.css      # CSS design tokens, dark mode, high contrast, RTL
│  ├─ js/
│  │  ├─ app.js          # SPA controller, event listeners, keyboard shortcuts
│  │  ├─ i18n.js         # Language switcher & RTL handler
│  │  ├─ voice.js        # Web Speech API (SpeechRecognition + SpeechSynthesis)
│  │  └─ chart_helper.js # Circular gauge & animation helper
│  ├─ vendor/chart.umd.min.js # Vendored offline Chart.js
│  ├─ locales/           # Complete 12-language JSON translation dictionaries
│  ├─ manifest.json      # PWA application manifest
│  └─ sw.js              # Service Worker for offline shell caching
├─ knowledge/
│  └─ qa.json            # 125 rich Q&A entries across brands, hygiene, and ethics
├─ tools/
│  └─ check_locales.py   # Integrity script checking key parity across all locales
├─ tests/                # Pytest unit and integration test suite
├─ verify_project.py     # End-to-end automated project verifier
├─ make_zip.py           # Standalone packaging script
├─ .env.example
├─ .gitignore
├─ requirements.txt
├─ SECURITY.md
└─ LICENSE
```

---

## 3. Step-by-Step Run Instructions (VS Code)

### Prerequisites
- Python 3.11 or higher
- Git

### 1. Setup Virtual Environment
```bash
# Clone or open the router-health-checker directory in VS Code
cd router-health-checker

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```

### 4. Run Verification
```bash
python verify_project.py
```

### 5. Launch Application
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## 4. GitHub Push Commands

To commit and push this repository to GitHub:

```bash
# 1. Initialize git
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "feat: complete Router Health Checker application release v1.0.0"

# 4. Set main branch
git branch -M main

# 5. Connect remote repository (replace with your GitHub URL)
git remote add origin https://github.com/<your-username>/router-health-checker.git

# 6. Push to GitHub
git push -u origin main
```

---

## 5. How to Add a New Language

1. Copy `static/locales/en.json` to `static/locales/<new_code>.json` (e.g. `de.json` for German, `ja.json` for Japanese).
2. Translate the values while keeping all 124 keys intact.
3. Add the language option to the `#langSel` dropdown in `static/index.html` and the `#langs` picker grid.
4. If the language is right-to-left (RTL), add its code to `RTL_LANGUAGES` in `static/js/i18n.js`.
5. Run the locale checker:
   ```bash
   python tools/check_locales.py
   ```

---

## 6. How to Deploy Safely

- **Bind to Loopback**: By default, keep `HOST=127.0.0.1`.
- **Reverse Proxy with TLS**: When deploying for home lab or small office access, place behind **Caddy** or **Nginx** with automatic HTTPS:
  ```nginx
  server {
      listen 443 ssl http2;
      server_name router.home.arpa;
      ssl_certificate /etc/ssl/certs/router.crt;
      ssl_certificate_key /etc/ssl/private/router.key;
      location / {
          proxy_pass http://127.0.0.1:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
      }
  }
  ```

---

## 7. Known Limitations Stated Honestly

1. **Browser Socket Constraints**: Pure client-side JavaScript cannot create raw TCP sockets. The Python backend is necessary to execute port probes and read OS network configuration.
2. **ARP Table Permissions**: On certain hardened Linux environments without `iproute2` or raw socket capabilities, ARP sweeps require standard user network permissions.
3. **Web Speech API Availability**: Speech synthesis and recognition depend on browser vendor implementations (Chrome, Edge, and Safari have the best native support; Firefox requires manual Web Speech flags).
4. **Read-Only Guarantee**: The tool strictly inspects settings and never alters or writes configurations to your router. Changes must be finalized in your router administration dashboard.
