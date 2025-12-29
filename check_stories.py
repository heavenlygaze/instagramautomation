#!/usr/bin/env python3
"""
check_stories.py

Check if specified accounts have posted new Instagram stories (via instagrapi),
optionally download new story media, and persist state so you only see new items.

Usage:
  1) pip install instagrapi
  2) export IG_USERNAME="your_username"
     export IG_PASSWORD="your_password"
  3) Create targets.txt with one username per line (accounts you follow)
  4) python check_stories.py --targets targets.txt --download --out downloads

State is stored in: story_state.json (by default)
Session is stored in: ig_session.json (by default)
"""

from __future__ import annotations

import argparse
import json
import os
from dotenv import load_dotenv
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from instagrapi import Client

load_dotenv()

def load_lines(path: Path) -> List[str]:
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    return lines


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def story_pk(story_obj: Any) -> Optional[int]:
    """
    instagrapi Story objects typically have .pk; sometimes .id is used elsewhere.
    We'll try both safely.
    """
    for attr in ("pk", "id"):
        v = getattr(story_obj, attr, None)
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.isdigit():
            return int(v)
    return None


def login_with_session(cl: Client, username: str, password: str, session_path: Path) -> None:
    """
    Prefer session reuse to reduce login challenges.
    """
    if session_path.exists():
        try:
            cl.load_settings(session_path.as_posix())
            cl.login(username, password)
            return
        except Exception:
            # fall back to fresh login
            pass

    cl.login(username, password)
    cl.dump_settings(session_path.as_posix())


def resolve_targets_to_ids(cl: Client, target_usernames: List[str], cache: Dict[str, int]) -> Dict[str, int]:
    """
    Resolve usernames -> user_id, caching results in state.
    """
    resolved: Dict[str, int] = {}
    for uname in target_usernames:
        if uname in cache:
            resolved[uname] = cache[uname]
            continue
        uid = cl.user_id_from_username(uname)
        cache[uname] = int(uid)
        resolved[uname] = int(uid)
        # tiny delay to be polite
        time.sleep(0.3)
    return resolved


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", type=str, required=True, help="Path to targets.txt (one username per line)")
    ap.add_argument("--state", type=str, default="story_state.json", help="State file to remember last seen story pk")
    ap.add_argument("--session", type=str, default="ig_session.json", help="Session settings file for instagrapi")
    ap.add_argument("--download", action="store_true", help="Download newly detected stories")
    ap.add_argument("--out", type=str, default="downloads", help="Output folder for downloads")
    ap.add_argument("--sleep", type=float, default=0.8, help="Sleep between users (seconds)")
    args = ap.parse_args()

    username = os.environ.get("IG_USERNAME")
    password = os.environ.get("IG_PASSWORD")
    if not username or not password:
        print("Missing IG_USERNAME / IG_PASSWORD env vars.", file=sys.stderr)
        return 2

    targets_path = Path(args.targets)
    if not targets_path.exists():
        print(f"Targets file not found: {targets_path}", file=sys.stderr)
        return 2

    state_path = Path(args.state)
    session_path = Path(args.session)
    out_dir = Path(args.out)

    state: Dict[str, Any] = load_json(state_path, default={})
    # state layout:
    # {
    #   "user_id_cache": {"someuser": 123, ...},
    #   "last_seen": {"someuser": 999999999999, ...}
    # }
    user_id_cache: Dict[str, int] = state.get("user_id_cache", {})
    last_seen: Dict[str, int] = state.get("last_seen", {})

    target_usernames = load_lines(targets_path)
    if not target_usernames:
        print("No targets found in targets file.", file=sys.stderr)
        return 2

    cl = Client()
    login_with_session(cl, username, password, session_path)

    resolved = resolve_targets_to_ids(cl, target_usernames, user_id_cache)

    any_new = False

    for uname, uid in resolved.items():
        try:
            stories = cl.user_stories(uid)  # List[Story] :contentReference[oaicite:1]{index=1}
        except Exception as e:
            print(f"[WARN] Failed fetching stories for @{uname}: {e}", file=sys.stderr)
            time.sleep(args.sleep)
            continue

        if not stories:
            print(f"@{uname}: no active stories")
            time.sleep(args.sleep)
            continue

        # Determine which are "new" since last run
        last = int(last_seen.get(uname, 0))
        story_pks: List[int] = []
        for s in stories:
            pk = story_pk(s)
            if pk is not None:
                story_pks.append(pk)

        if not story_pks:
            print(f"@{uname}: stories found, but couldn't read story PKs")
            time.sleep(args.sleep)
            continue

        newest_pk = max(story_pks)
        new_pks = sorted([pk for pk in story_pks if pk > last])

        if not new_pks:
            print(f"@{uname}: stories active (no new since last check)")
            time.sleep(args.sleep)
            continue

        any_new = True
        print(f"@{uname}: NEW stories detected ({len(new_pks)} item(s))")

        if args.download:
            user_folder = out_dir / uname
            user_folder.mkdir(parents=True, exist_ok=True)
            for pk in new_pks:
                try:
                    path = cl.story_download(pk, folder=user_folder)  # :contentReference[oaicite:2]{index=2}
                    print(f"  downloaded: {path}")
                except Exception as e:
                    print(f"  [WARN] download failed for story {pk}: {e}", file=sys.stderr)

        # Update last seen to newest for this user
        last_seen[uname] = newest_pk

        time.sleep(args.sleep)

    state["user_id_cache"] = user_id_cache
    state["last_seen"] = last_seen
    save_json(state_path, state)

    if any_new:
        print("\nDone: new stories were found.")
        return 0
    else:
        print("\nDone: no new stories found.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
