#!/usr/bin/env python3
"""
██╗  ██╗ █████╗ ███████╗██╗  ██╗    ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██║  ██║██╔══██╗██╔════╝██║  ██║    ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
███████║███████║███████╗███████║    ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██╔══██║██╔══██║╚════██║██╔══██║    ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
██║  ██║██║  ██║███████║██║  ██║    ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
                    TikTok Intelligence Terminal — v1.0
"""

from __future__ import annotations

import datetime
import io
import json
import re
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox

import requests

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    HAS_BIDI = False


# ── Colour palette — terminal green-on-black hacker aesthetic ─────────
class C:
    BG        = "#0a0f0a"   # near-black
    PANEL     = "#0d140d"   # card background
    BOX       = "#111a11"   # stat box
    BORDER    = "#1a2e1a"   # subtle borders
    GREEN     = "#00ff41"   # matrix green — primary accent
    GREEN_DIM = "#00c032"   # dimmed green
    GREEN_LO  = "#005c18"   # dark green for disabled
    CYAN      = "#00ffcc"   # secondary accent
    AMBER     = "#ffa200"   # warning / highlight
    WHITE     = "#d4f5d4"   # readable text
    MUTED     = "#4a6b4a"   # secondary text
    RED       = "#ff3c3c"   # error / private
    GOLD      = "#ffd700"   # loading indicator


# ── Shared TikTok session cookies (replace with your own) ─────────────
COOKIES: dict[str, str] = {
    "sessionid":     "0f836a0c35ae256ce359f71eb8e106c0",
    "tt_csrf_token": "v3TmNqIa-6gkY4odaOcDjcU0dyWbQdgM1-_Y",
    "ttwid":         (
        "1%7Crrr2tGZ_WvxZePAga-WviFIijTG5O0-uMOSvnSDBtDg"
        "%7C1782086758%7C61002380b9f0ec76d7711d4bce09e4ddd0f02ad156e0c13bd08a57604d98969f"
    ),
    "s_v_web_id":    "verify_mqoez0pg_l7Wpj1dV_aslQ_4euL_AZYX_nrjWyN14YbrD",
}

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


# ══════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════

def fix_rtl(text: str) -> str:
    """Reshape Arabic / RTL text so Tkinter renders it correctly."""
    if not text:
        return ""
    if HAS_BIDI and any(ord(c) > 127 for c in text):
        try:
            return get_display(arabic_reshaper.reshape(text))
        except Exception:
            pass
    return text


def deep_find(obj, target_key=None, target_value=None):
    """Recursive dict/list search — returns the first matching container."""
    if isinstance(obj, dict):
        if target_key and target_key in obj:
            return obj
        if target_value is not None:
            for v in obj.values():
                if v == target_value:
                    return obj
        for v in obj.values():
            res = deep_find(v, target_key, target_value)
            if res:
                return res
    elif isinstance(obj, list):
        for item in obj:
            res = deep_find(item, target_key, target_value)
            if res:
                return res
    return None


def find_master_user(payload: dict, username: str) -> dict | None:
    """Extract the richest user object from TikTok's rehydration JSON."""
    clean = username.lower().lstrip("@")
    candidates: list[dict] = []

    def traverse(obj):
        if isinstance(obj, dict):
            uid = obj.get("uniqueId") or obj.get("unique_id") or ""
            if str(uid).lower() == clean:
                candidates.append(obj)
            for v in obj.values():
                traverse(v)
        elif isinstance(obj, list):
            for i in obj:
                traverse(i)

    # Fast path — modern TikTok web structure
    try:
        usr = payload["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]["user"]
        if usr.get("uniqueId", "").lower() == clean:
            candidates.append(usr)
    except (KeyError, TypeError):
        pass

    traverse(payload)
    return max(candidates, key=len) if candidates else None


# ══════════════════════════════════════════════════════════════════════
# DATA LAYER
# ══════════════════════════════════════════════════════════════════════

def get_profile_data(username: str) -> dict:
    """Fetch and parse a TikTok profile page; returns a flat data dict."""
    username = username.lstrip("@")
    url      = f"https://www.tiktok.com/@{username}"
    headers  = {
        "User-Agent":      _UA,
        "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie":          "; ".join(f"{k}={v}" for k, v in COOKIES.items()),
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
    except Exception as exc:
        return {"error": f"Connection failed: {exc}"}

    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code} from TikTok"}

    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        resp.text, re.DOTALL,
    )
    if not match:
        return {"error": "Rehydration script not found — TikTok may have changed their page structure"}

    raw = match.group(1).strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        try:
            payload = json.loads(re.sub(r"[\x00-\x1f]", "", raw))
        except Exception as exc:
            return {"error": f"JSON parse failed: {exc}"}

    user_obj = find_master_user(payload, username)
    if not user_obj:
        return {"error": f"No user object found for @{username}"}

    stats = deep_find(payload, target_key="followerCount") or user_obj.get("stats", {})

    region = (
        user_obj.get("region")
        or user_obj.get("iso_country_code")
        or user_obj.get("country")
        or user_obj.get("location")
        or user_obj.get("regionCode")
        or user_obj.get("language")
        or "UNKNOWN"
    )

    return {
        "user_id":        user_obj.get("id"),
        "unique_id":      user_obj.get("uniqueId"),
        "nickname":       user_obj.get("nickname"),
        "bio":            user_obj.get("bioDescription") or user_obj.get("signature"),
        "avatar":         user_obj.get("avatarLarger") or user_obj.get("avatarMedium") or user_obj.get("avatarThumb"),
        "follower_count": stats.get("followerCount"),
        "following_count":stats.get("followingCount"),
        "heart_count":    stats.get("heartCount"),
        "video_count":    stats.get("videoCount"),
        "digg_count":     stats.get("diggCount"),
        "is_verified":    user_obj.get("verified", False),
        "is_private":     user_obj.get("privateAccount", False),
        "region":         region,
        "created":        user_obj.get("createTime"),
    }


# ══════════════════════════════════════════════════════════════════════
# GUI
# ══════════════════════════════════════════════════════════════════════

class HashReconGUI:
    """Terminal-aesthetic TikTok intelligence viewer."""

    TITLE = "[ HASH::RECON ]  TikTok Intelligence Terminal"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(self.TITLE)
        self.root.geometry("920x660")
        self.root.minsize(820, 580)
        self.root.configure(bg=C.BG)
        self._build_ui()

    # ── UI construction ─────────────────────────────────────────────
    def _build_ui(self) -> None:
        self._build_header()
        self._build_input_bar()
        self._build_cards()
        self._build_statusbar()

    def _build_header(self) -> None:
        hdr = tk.Frame(self.root, bg=C.PANEL, pady=0)
        hdr.pack(fill=tk.X, padx=12, pady=(12, 0))

        # Top border line
        tk.Frame(hdr, bg=C.GREEN, height=1).pack(fill=tk.X)

        inner = tk.Frame(hdr, bg=C.PANEL)
        inner.pack(fill=tk.X, padx=16, pady=10)

        tk.Label(
            inner,
            text="# HASH::RECON",
            font=("Courier", 20, "bold"),
            fg=C.GREEN, bg=C.PANEL,
        ).pack(side=tk.LEFT)

        tk.Label(
            inner,
            text="TikTok Intelligence Terminal  [v1.0]",
            font=("Courier", 9),
            fg=C.MUTED, bg=C.PANEL,
        ).pack(side=tk.RIGHT, pady=4)

        tk.Frame(hdr, bg=C.GREEN, height=1).pack(fill=tk.X)

    def _build_input_bar(self) -> None:
        bar = tk.Frame(self.root, bg=C.BG)
        bar.pack(fill=tk.X, padx=12, pady=10)

        tk.Label(
            bar,
            text="TARGET >>>",
            font=("Courier", 10, "bold"),
            fg=C.GREEN, bg=C.BG,
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.entry_target = tk.Entry(
            bar,
            font=("Courier", 12),
            width=26,
            bg=C.BOX,
            fg=C.GREEN,
            insertbackground=C.GREEN,
            relief="flat",
            highlightthickness=1,
            highlightcolor=C.GREEN,
            highlightbackground=C.BORDER,
        )
        self.entry_target.pack(side=tk.LEFT, ipady=5, padx=(0, 10))
        self.entry_target.insert(0, "hawa_alamin")
        self.entry_target.bind("<Return>", lambda _: self._start_scan())

        self.btn_scan = tk.Button(
            bar,
            text="[ EXECUTE ]",
            font=("Courier", 10, "bold"),
            bg=C.GREEN, fg=C.BG,
            activebackground=C.CYAN,
            activeforeground=C.BG,
            relief="flat",
            cursor="hand2",
            padx=14,
            command=self._start_scan,
        )
        self.btn_scan.pack(side=tk.LEFT)

        self.btn_web = tk.Button(
            bar,
            text="[ OPEN PROFILE ]",
            font=("Courier", 9),
            bg=C.BOX, fg=C.MUTED,
            activebackground=C.GREEN_DIM,
            activeforeground=C.BG,
            relief="flat",
            cursor="hand2",
            padx=10,
            state=tk.DISABLED,
            command=lambda: webbrowser.open(
                f"https://www.tiktok.com/@{self.entry_target.get().strip()}"
            ),
        )
        self.btn_web.pack(side=tk.LEFT, padx=(8, 0))

    def _build_cards(self) -> None:
        container = tk.Frame(self.root, bg=C.BG)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        # ── Left card: Identity ──────────────────────────────────
        left = tk.LabelFrame(
            container,
            text="  // IDENTITY  ",
            font=("Courier", 10, "bold"),
            bg=C.PANEL, fg=C.GREEN,
            bd=1, relief="solid",
        )
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        # Avatar
        self.lbl_avatar = tk.Label(
            left,
            text="#\n[NO IMG]",
            font=("Courier", 9),
            bg=C.BOX, fg=C.MUTED,
            width=11, height=5,
        )
        self.lbl_avatar.grid(row=0, column=2, rowspan=5, padx=14, pady=12, sticky="n")

        # Identity fields
        fields = [
            ("USER_ID",    "user_id"),
            ("USERNAME",   "unique_id"),
            ("NICKNAME",   "nickname"),
            ("REGION",     "region"),
            ("CREATED",    "created"),
            ("VERIFIED",   "is_verified"),
            ("PRIVATE",    "is_private"),
        ]
        self.info_labels: dict[str, tk.Label] = {}

        for idx, (label, key) in enumerate(fields):
            tk.Label(
                left,
                text=f"{label}:",
                font=("Courier", 9, "bold"),
                bg=C.PANEL, fg=C.MUTED,
                anchor="w",
            ).grid(row=idx, column=0, sticky="w", padx=(12, 4), pady=5)

            val = tk.Label(
                left,
                text="—",
                font=("Courier", 10),
                bg=C.PANEL, fg=C.WHITE,
                anchor="w",
            )
            val.grid(row=idx, column=1, sticky="w", padx=4, pady=5)
            self.info_labels[key] = val

        tk.Label(
            left,
            text="BIO:",
            font=("Courier", 9, "bold"),
            bg=C.PANEL, fg=C.MUTED,
        ).grid(row=7, column=0, sticky="nw", padx=(12, 4), pady=(10, 0))

        self.txt_bio = tk.Text(
            left,
            height=4, width=28,
            font=("Courier", 9),
            bg=C.BOX, fg=C.WHITE,
            insertbackground=C.GREEN,
            relief="flat",
            wrap="word",
        )
        self.txt_bio.grid(row=7, column=1, columnspan=2, sticky="nsew", padx=10, pady=10)

        left.grid_rowconfigure(7, weight=1)
        left.grid_columnconfigure(1, weight=1)

        # ── Right card: Stats ─────────────────────────────────────
        right = tk.LabelFrame(
            container,
            text="  // ENGAGEMENT_STATS  ",
            font=("Courier", 10, "bold"),
            bg=C.PANEL, fg=C.GREEN,
            bd=1, relief="solid",
        )
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))

        stat_defs = [
            ("FOLLOWERS",   "follower_count",  0, 0),
            ("FOLLOWING",   "following_count", 0, 1),
            ("TOTAL_LIKES", "heart_count",     1, 0),
            ("VIDEOS",      "video_count",     1, 1),
            ("LIKED",       "digg_count",      2, 0),
        ]
        self.stat_widgets: dict[str, tk.Label] = {}

        for label, key, row, col in stat_defs:
            box = tk.Frame(right, bg=C.BOX, bd=0)
            box.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            tk.Label(
                box,
                text=label,
                font=("Courier", 8, "bold"),
                bg=C.BOX, fg=C.MUTED,
            ).pack(pady=(12, 2))

            num = tk.Label(
                box,
                text="—",
                font=("Courier", 17, "bold"),
                bg=C.BOX, fg=C.GREEN,
            )
            num.pack(pady=(0, 12))
            self.stat_widgets[key] = num

        # Hash indicator box (bottom-right)
        hash_box = tk.Frame(right, bg=C.BOX)
        hash_box.grid(row=2, column=1, padx=8, pady=8, sticky="nsew")
        self.lbl_hash_status = tk.Label(
            hash_box,
            text="AWAITING\nTARGET",
            font=("Courier", 11, "bold"),
            bg=C.BOX, fg=C.GREEN_LO,
        )
        self.lbl_hash_status.pack(expand=True)

        for i in range(3):
            right.grid_rowconfigure(i, weight=1)
        for j in range(2):
            right.grid_columnconfigure(j, weight=1)

    def _build_statusbar(self) -> None:
        foot = tk.Frame(self.root, bg=C.PANEL)
        foot.pack(fill=tk.X, side=tk.BOTTOM, padx=12, pady=(0, 10))
        tk.Frame(foot, bg=C.GREEN, height=1).pack(fill=tk.X)

        self.status_var = tk.StringVar(
            value="  >> HASH::RECON ready. Enter target username and press [ EXECUTE ]."
        )
        tk.Label(
            foot,
            textvariable=self.status_var,
            font=("Courier", 9),
            bg=C.PANEL, fg=C.MUTED,
            anchor="w",
        ).pack(fill=tk.X, padx=8, pady=4)

    # ── Scan control ────────────────────────────────────────────────
    def _start_scan(self) -> None:
        user = self.entry_target.get().strip()
        if not user:
            messagebox.showwarning("No Target", "Enter a username to scan.")
            return

        self.btn_scan.config(text="[ SCANNING... ]", state=tk.DISABLED, bg=C.GREEN_LO)
        self.lbl_hash_status.config(text="PROBING\nTARGET...", fg=C.AMBER)
        self.status_var.set(f"  >> Dispatching recon probes for @{user}...")

        def _worker():
            data = get_profile_data(user)
            self.root.after(0, self._render, data, user)

        threading.Thread(target=_worker, daemon=True).start()

    def _render(self, data: dict, user: str) -> None:
        self.btn_scan.config(text="[ EXECUTE ]", state=tk.NORMAL, bg=C.GREEN)

        if "error" in data:
            self.status_var.set(f"  >> ERROR: {data['error']}")
            self.lbl_hash_status.config(text="SCAN\nFAILED", fg=C.RED)
            messagebox.showerror("Recon Failed", data["error"])
            return

        self.status_var.set(f"  >> Target @{user} acquired. Data exfiltrated successfully.")
        self.lbl_hash_status.config(text="TARGET\nACQUIRED", fg=C.GREEN)

        # Identity fields
        self.info_labels["user_id"].config(text=str(data.get("user_id") or "N/A"))
        self.info_labels["unique_id"].config(text=f"@{data.get('unique_id') or user}", fg=C.CYAN)
        self.info_labels["nickname"].config(text=fix_rtl(data.get("nickname") or "N/A"))
        self.info_labels["region"].config(text=str(data.get("region") or "N/A"))

        ts = data.get("created")
        self.info_labels["created"].config(
            text=datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else "N/A"
        )

        verified = data.get("is_verified")
        self.info_labels["is_verified"].config(
            text="TRUE  [✓]" if verified else "FALSE [✗]",
            fg=C.GREEN if verified else C.MUTED,
        )

        private = data.get("is_private")
        self.info_labels["is_private"].config(
            text="TRUE  [🔒]" if private else "FALSE [🔓]",
            fg=C.RED if private else C.MUTED,
        )

        self.txt_bio.delete("1.0", tk.END)
        self.txt_bio.insert(tk.END, fix_rtl(data.get("bio") or "[no bio]"))

        # Stats
        for key, widget in self.stat_widgets.items():
            raw = data.get(key)
            widget.config(text=f"{int(raw):,}" if raw else "0")

        self.btn_web.config(state=tk.NORMAL, fg=C.GREEN)

        # Avatar
        if HAS_PIL and data.get("avatar"):
            threading.Thread(
                target=self._fetch_avatar, args=(data["avatar"],), daemon=True
            ).start()
        else:
            self.lbl_avatar.config(image="", text="#\n[NO PIL]", width=11, height=5)

    def _fetch_avatar(self, url: str) -> None:
        try:
            resp = requests.get(url, timeout=7)
            if resp.status_code == 200:
                pil_img = Image.open(io.BytesIO(resp.content)).resize(
                    (88, 88), Image.Resampling.LANCZOS
                )
                self.root.after(0, self._set_avatar, pil_img)
        except Exception:
            pass

    def _set_avatar(self, pil_img) -> None:
        photo = ImageTk.PhotoImage(pil_img)
        self.lbl_avatar.config(image=photo, text="", width=88, height=88)
        self.lbl_avatar.image = photo  # prevent GC


# ══════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    HashReconGUI(root)
    root.mainloop()
