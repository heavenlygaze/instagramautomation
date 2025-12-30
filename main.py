#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from time import sleep

from config import load_dotenv_and_get_credentials
from file_utils import load_lines, load_json, save_json
from instagrapi_utils import login_with_session, resolve_targets_to_ids, story_pk
from story_utils import download_stories
from state_utils import load_state, save_state
from email_utils import send_email

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", type=str, required=True, help="Path to targets.txt (one username per line)")
    ap.add_argument("--state", type=str, default="story_state.json", help="State file to remember last seen story pk")
    ap.add_argument("--session", type=str, default="ig_session.json", help="Session settings file for instagrapi")
    ap.add_argument("--download", action="store_true", help="Download newly detected stories")
    ap.add_argument("--out", type=str, default="downloads", help="Output folder for downloads")
    ap.add_argument("--sleep", type=float, default=0.8, help="Sleep between users (seconds)")
    ap.add_argument("--notify", type=str, default="notify_users.txt", help="Path to the file with users to notify")
    args = ap.parse_args()

    # Load credentials
    try:
        username, password, email_username, email_password = load_dotenv_and_get_credentials()
    except ValueError as e:
        print(f"{e}", file=sys.stderr)
        sys.exit(2)

    targets_path = Path(args.targets)
    if not targets_path.exists():
        print(f"Targets file not found: {targets_path}", file=sys.stderr)
        sys.exit(2)

    state_path = Path(args.state)
    session_path = Path(args.session)
    out_dir = Path(args.out)

    # Load state data
    try:
        state = load_state(state_path)
    except Exception as e:
        print(f"Error loading state: {e}", file=sys.stderr)
        sys.exit(2)

    user_id_cache, last_seen = state["user_id_cache"], state["last_seen"]

    # Load target usernames
    try:
        target_usernames = load_lines(targets_path)
    except Exception as e:
        print(f"Error reading targets file: {e}", file=sys.stderr)
        sys.exit(2)

    for uname in target_usernames:
        if uname not in last_seen:
            last_seen[uname] = 0  # or None depending on how you want to initialize

    notify_path = Path(args.notify)
    if not notify_path.exists():
        print(f"Notify file not found: {notify_path}", file=sys.stderr)
        sys.exit(2)

    # Load users to notify from external file
    users_to_notify = load_lines(notify_path)


    # Initialize Instagrapi client
    try:
        cl = login_with_session(session_path, username, password)
    except Exception as e:
        print(f"Error logging in: {e}", file=sys.stderr)
        sys.exit(2)

    # Resolve target usernames to user IDs
    try:
        resolved = resolve_targets_to_ids(cl, target_usernames, user_id_cache)
    except Exception as e:
        print(f"Error resolving usernames to IDs: {e}", file=sys.stderr)
        sys.exit(2)

    any_new = False
    for uname, uid in resolved.items():
        try:
            stories = cl.user_stories(uid)
        except Exception as e:
            print(f"[WARN] Failed fetching stories for @{uname}: {e}", file=sys.stderr)
            sleep(args.sleep)
            continue

        if not stories:
            print(f"@{uname}: no active stories")
            sleep(args.sleep)
            continue

        last = last_seen.get(uname, 0)
        story_pks = [story_pk(s) for s in stories]
        new_pks = [pk for pk in story_pks if pk > last]

        if not new_pks:
            print(f"@{uname}: no new stories since last check")
            sleep(args.sleep)
            continue

        any_new = True
        print(f"@{uname}: NEW stories detected ({len(new_pks)} items)")

        if args.download:
            try:
                # Download the story and get the file path
                story_file_path = download_stories(cl, new_pks, out_dir, uname)
            except Exception as e:
                print(f"[WARN] Failed to download stories for @{uname}: {e}", file=sys.stderr)
                continue
        else:
            story_file_path = None
        # Send an email if this user is in the 'users_to_notify' list
        if uname in users_to_notify:
            subject = f"New story posted by {uname}!"
            body = f"Check out the latest story posted by @{uname} on Instagram."
            if story_file_path:
                send_email(subject, body, email_username, attachment_path=story_file_path)
            else:
                send_email(subject, body, email_username)

        last_seen[uname] = max(new_pks)
        sleep(args.sleep)

    # Save the updated state
    try:
        state["user_id_cache"], state["last_seen"] = user_id_cache, last_seen
        save_state(state_path, state)
    except Exception as e:
        print(f"Error saving state: {e}", file=sys.stderr)
        sys.exit(2)

    if any_new:
        print("\nDone: new stories found.")
        return 0
    else:
        print("\nDone: no new stories found.")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
