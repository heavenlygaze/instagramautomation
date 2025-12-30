from instagrapi import Client
from pathlib import Path


def download_stories(cl: Client, new_pks: list[int], out_dir: Path, uname: str) -> None:
    user_folder = out_dir / uname
    user_folder.mkdir(parents=True, exist_ok=True)

    for pk in new_pks:
        try:
            path = cl.story_download(pk, folder=user_folder)
            print(f"  downloaded: {path}")
        except Exception as e:
            print(f"  [WARN] download failed for story {pk}: {e}")
