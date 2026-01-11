from instagrapi import Client
from pathlib import Path
from time import sleep
from random import randint


def download_stories(cl: Client, new_pks: list[int], out_dir: Path, uname: str) -> str:
    """
    Downloads new stories and returns the path to the last downloaded story.
    """
    user_folder = out_dir / uname
    user_folder.mkdir(parents=True, exist_ok=True)

    last_downloaded_path = None

    for pk in new_pks:
        try:
            sleep(randint(3,15))
            path = cl.story_download(pk, folder=user_folder)
            print(f"  downloaded: {path}")
            last_downloaded_path = path  # Keep track of the last downloaded story path
        except Exception as e:
            print(f"  [WARN] download failed for story {pk}: {e}")

    if last_downloaded_path:
        return last_downloaded_path
    else:
        return ""  # Return an empty string if no stories were downloaded
