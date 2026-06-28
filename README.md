# HASH::RECON — TikTok Intelligence Terminal

```
██╗  ██╗ █████╗ ███████╗██╗  ██╗    ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██║  ██║██╔══██╗██╔════╝██║  ██║    ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
███████║███████║███████╗███████║    ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██║██╔══██║╚════██║██╔══██║    ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║██║  ██║███████║██║  ██║    ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
```

![Python](https://img.shields.io/badge/Python-3.9%2B-00ff41?style=flat-square&logo=python&logoColor=black&labelColor=0a0f0a)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-00ffcc?style=flat-square&labelColor=0a0f0a)
![GUI](https://img.shields.io/badge/Interface-Tkinter%20GUI-00ff41?style=flat-square&labelColor=0a0f0a)
![License](https://img.shields.io/badge/License-MIT-ffa200?style=flat-square&labelColor=0a0f0a)
![Status](https://img.shields.io/badge/Status-Active-00ff41?style=flat-square&labelColor=0a0f0a)

> A terminal-aesthetic TikTok profile intelligence viewer built with Python and Tkinter.  
> Extracts public profile data, engagement stats, and metadata from any TikTok account — no official API required.

---

## Screenshot

```
┌─────────────────────────────────────────────────────────────────────────┐
│  # HASH::RECON              TikTok Intelligence Terminal  [v1.0]        │
├─────────────────────────────────────────────────────────────────────────┤
│  TARGET >>> [ hawa_alamin          ]  [ EXECUTE ]  [ OPEN PROFILE ]     │
├──────────────────────────────┬──────────────────────────────────────────┤
│  // IDENTITY                 │  // ENGAGEMENT_STATS                     │
│                              │                                          │
│  USER_ID  : 123456789        │  ┌─FOLLOWERS─┐  ┌─FOLLOWING──┐          │
│  USERNAME : @hawa_alamin     │  │  1,234,567 │  │     892    │          │
│  NICKNAME : Hawa             │  └────────────┘  └────────────┘          │
│  REGION   : SA               │  ┌─TOTAL_LIKES┐  ┌─VIDEOS─────┐         │
│  CREATED  : 2020-03-14       │  │ 45,230,100 │  │    312     │         │
│  VERIFIED : TRUE  [✓]        │  └────────────┘  └────────────┘          │
│  PRIVATE  : FALSE [🔓]       │  ┌─LIKED──────┐  ┌────────────┐         │
│                              │  │    4,210   │  │  TARGET    │         │
│  BIO: [ bio text here ]      │  └────────────┘  │  ACQUIRED  │         │
│                              │                  └────────────┘          │
├──────────────────────────────┴──────────────────────────────────────────┤
│  >> Target @hawa_alamin acquired. Data exfiltrated successfully.        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Features

| Feature | Description |
|---|---|
| **Profile Identity** | User ID, username, nickname, region, account creation date |
| **Account Flags** | Verified status, private account detection |
| **Engagement Stats** | Followers, following, total likes, video count, liked videos |
| **Bio Extraction** | Full bio with Arabic / RTL text support |
| **Avatar Display** | Live profile picture download and render (requires Pillow) |
| **Direct Link** | One-click open profile in browser |
| **Threading** | Non-blocking UI — scans run in background threads |
| **Terminal Aesthetic** | Matrix green-on-black monospace design, no external CSS |

---

## Requirements

### Python

Python 3.9 or higher is required.

```bash
python --version
```

### Dependencies

Install required packages:

```bash
pip install requests Pillow arabic-reshaper python-bidi
```

| Package | Required | Purpose |
|---|---|---|
| `requests` | **Yes** | HTTP requests to TikTok |
| `Pillow` | Optional | Avatar image display |
| `arabic-reshaper` | Optional | Arabic text rendering fix |
| `python-bidi` | Optional | RTL text direction support |

Tkinter is included with standard Python on Windows and macOS. On Linux:

```bash
sudo apt install python3-tk   # Debian / Ubuntu
sudo dnf install python3-tkinter  # Fedora
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/yourhandle/hash-recon.git
cd hash-recon

# Install dependencies
pip install -r requirements.txt

# Launch
python hash_recon.py
```

### requirements.txt

```
requests>=2.31.0
Pillow>=10.0.0
arabic-reshaper>=3.0.0
python-bidi>=0.4.2
```

---

## Usage

### GUI Mode

```bash
python hash_recon.py
```

1. Enter a TikTok username in the `TARGET >>>` field (with or without `@`)
2. Press `[ EXECUTE ]` or hit `Enter`
3. Wait for `TARGET ACQUIRED` confirmation
4. Click `[ OPEN PROFILE ]` to visit the account in your browser

### Session Cookies (Important)

The tool uses TikTok session cookies to bypass bot detection. The defaults included are **example values** — replace them with your own in the `COOKIES` dict at the top of `hash_recon.py`:

```python
COOKIES: dict[str, str] = {
    "sessionid":     "YOUR_SESSION_ID_HERE",
    "tt_csrf_token": "YOUR_CSRF_TOKEN_HERE",
    "ttwid":         "YOUR_TTWID_HERE",
    "s_v_web_id":    "YOUR_S_V_WEB_ID_HERE",
}
```

**How to get your cookies:**

1. Log into TikTok in your browser
2. Open DevTools → `Application` tab → `Cookies` → `https://www.tiktok.com`
3. Copy the values for `sessionid`, `tt_csrf_token`, `ttwid`, `s_v_web_id`

> ⚠️ Never share your `sessionid` publicly — treat it like a password.

---

## Project Structure

```
hash-recon/
├── hash_recon.py        # Main application (single file)
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── LICENSE              # MIT License
```

### Code Architecture

```
hash_recon.py
├── C                    # Colour token class (palette constants)
├── COOKIES              # TikTok session cookies
├── fix_rtl()            # Arabic / RTL text reshaper
├── deep_find()          # Recursive JSON search utility
├── find_master_user()   # Extracts richest user object from payload
├── get_profile_data()   # HTTP fetch + JSON parse → flat data dict
└── HashReconGUI         # Tkinter GUI class
    ├── _build_header()
    ├── _build_input_bar()
    ├── _build_cards()
    ├── _build_statusbar()
    ├── _start_scan()    # Spawns background thread
    ├── _render()        # Populates UI with results
    ├── _fetch_avatar()  # Background image download
    └── _set_avatar()    # Main-thread image render
```

---

## How It Works

1. **Fetch** — Sends a GET request to `https://www.tiktok.com/@{username}` with browser-like headers and session cookies
2. **Extract** — Parses the `__UNIVERSAL_DATA_FOR_REHYDRATION__` JSON script embedded in the HTML
3. **Traverse** — Recursively searches the payload for the richest matching user object
4. **Display** — Renders all extracted fields in the split-panel GUI

No official API, no rate-limit keys, no scraping framework needed.

---

## Status Indicators

| Display | Meaning |
|---|---|
| `AWAITING TARGET` | Ready, no scan started |
| `PROBING TARGET...` | Scan in progress |
| `TARGET ACQUIRED` | Scan completed successfully |
| `SCAN FAILED` | Network error or user not found |

---

## Troubleshooting

**"Rehydration script not found"**
TikTok may have updated their page structure. Try refreshing your cookies or updating the regex pattern in `get_profile_data()`.

**"HTTP 404"**
The username does not exist or has been banned.

**"HTTP 403 / Connection error"**
Your session cookies have expired. Re-copy them from your browser.

**Avatar not showing**
Install Pillow: `pip install Pillow`

**Arabic text appears reversed**
Install bidi libraries: `pip install arabic-reshaper python-bidi`

---

## Ethical Use & Legal Notice

This tool is intended for:

- OSINT research on **public** TikTok profiles
- Personal use and educational purposes
- CTF challenges and security coursework

This tool only reads **publicly available** profile data — the same information visible to any visitor on TikTok's website.

> ⚠️ Do not use this tool to harass, stalk, or collect data on individuals without their knowledge in contexts where privacy laws apply. The user assumes full responsibility for how this tool is used. Scraping TikTok may violate their Terms of Service.

---

## License

MIT © 2024 — see LICENSE for full terms.

---

## Contributing

Pull requests are welcome. To suggest a feature or report a bug, open an issue first.

```bash
# Quick test
python hash_recon.py
# Enter: tiktok  (official account — good baseline test)
```
