#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from time import sleep
import random
from log import setup_logging

from config import load_dotenv_and_get_credentials
from file_utils import load_lines, load_json, save_json
from instagrapi_utils import login_with_session, resolve_targets_to_ids, story_pk
from story_utils import download_stories
from state_utils import load_state, save_state
from email_utils import send_email

logger = setup_logging()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", type=str, required=True, help="Path to targets.txt (one username per line)")
    ap.add_argument("--state", type=str, default="story_state.json", help="State file to remember last seen story pk")
    ap.add_argument("--session", type=str, default="ig_session.json", help="Session settings file for instagrapi")
    ap.add_argument("--download", action="store_true", help="Download newly detected stories")
    ap.add_argument("--out", type=str, default="downloads", help="Output folder for downloads")
    ap.add_argument("--sleep", type=float, default=0.8, help="Sleep between users (seconds)")
    ap.add_argument("--notify", type=str, default="notify_users.txt", help="Path to the file with users to notify")
    ap.add_argument("--min_sleep", type=float, default=3, help="Minimum random sleep time (seconds)")
    ap.add_argument("--max_sleep", type=float, default=15, help="Maximum random sleep time (seconds)")
    args = ap.parse_args()

    logger.info("Starting the Instagram story checker script.")

    # Load credentials
    try:
        username, password, email_username, email_password = load_dotenv_and_get_credentials()
    except ValueError as e:
        print(f"{e}", file=sys.stderr)
        sys.exit(2)

    targets_path = Path(args.targets)
    if not targets_path.exists():
        logger.error(f"Targets file not found: {targets_path}")
        sys.exit(2)

    state_path = Path(args.state)
    session_path = Path(args.session)
    out_dir = Path(args.out)

    # Load state data
    try:
        state = load_state(state_path)
    except Exception as e:
        logger.error(f"Error loading state: {e}")
        sys.exit(2)

    user_id_cache, last_seen = state["user_id_cache"], state["last_seen"]

    # Load target usernames
    try:
        target_usernames = load_lines(targets_path)
    except Exception as e:
        logger.error(f"Error reading targets file: {e}")
        sys.exit(2)

    for uname in target_usernames:
        if uname not in last_seen:
            last_seen[uname] = 0  # or None depending on how you want to initialize

    notify_path = Path(args.notify)
    if not notify_path.exists():
        logger.error(f"Notify file not found: {notify_path}")
        sys.exit(2)

    # Load users to notify from external file
    users_to_notify = load_lines(notify_path)

    # Initialize Instagrapi client
    try:
        cl = login_with_session(session_path, username, password)
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        sys.exit(2)

    # Resolve target usernames to user IDs
    try:
        resolved = resolve_targets_to_ids(cl, target_usernames, user_id_cache)
    except Exception as e:
        logger.error(f"Error resolving usernames to IDs: {e}")
        sys.exit(2)

    # Track users and the number of new stories
    stories_summary = {}

    any_new = False
    for uname, uid in resolved.items():
        try:
            sleep(random.uniform(args.min_sleep, args.max_sleep))
            stories = cl.user_stories(uid)
        except Exception as e:
            logger.warning(f"Failed fetching stories for @{uname}: {e}")
            sleep(random.uniform(args.min_sleep, args.max_sleep))
            continue

        if not stories:
            logger.info(f"@{uname}: no active stories")
            sleep(random.uniform(args.min_sleep, args.max_sleep))
            continue

        last = last_seen.get(uname, 0)
        story_pks = [story_pk(s) for s in stories]
        new_pks = [pk for pk in story_pks if pk > last]

        if not new_pks:
            logger.info(f"@{uname}: no new stories since last check")
            sleep(random.uniform(args.min_sleep, args.max_sleep))
            continue

        any_new = True
        logger.info(f"@{uname}: NEW stories detected ({len(new_pks)} items)")

        if args.download:
            try:
                # Download the story and get the file path
                story_file_path = download_stories(cl, new_pks, out_dir, uname)
            except Exception as e:
                logger.warning(f"Failed to download stories for @{uname}: {e}")
                continue
        else:
            story_file_path = None

        # Track the number of new stories for this user
        stories_summary[uname] = len(new_pks)

        last_seen[uname] = max(new_pks)
        sleep(random.uniform(args.min_sleep, args.max_sleep))

    # Save the updated state
    try:
        state["user_id_cache"], state["last_seen"] = user_id_cache, last_seen
        save_state(state_path, state)
    except Exception as e:
        logger.error(f"Error saving state: {e}")
        sys.exit(2)

    # Send a summary email at the end
    if any_new:
        email_subject = "New Stories from Users You Follow: Daily Recap"
        email_body = "Here is a recap of the new stories uploaded by users you follow:\n\n"

        for user, story_count in stories_summary.items():
            email_body += f"@{user}: {story_count} new story(ies)\n"

        try:
            send_email(
                subject=email_subject,
                body=email_body,
                to_email=email_username,
            )
        except Exception as e:
            logger.error(f"Error sending recap email: {e}")

        logger.info("\nDone: new stories found and recap email sent.")
    else:
        logger.info("\nDone: no new stories found.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
