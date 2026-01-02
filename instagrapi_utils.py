from instagrapi import Client
import time
from typing import Dict, List
from pathlib import Path
from typing import Optional, Any
from time import sleep
from random import randint

def login_with_session(session_path: Path, username: str, password: str) -> Client:
    sleep(randint(10, 60))
    cl = Client()
    if session_path.exists():
        try:
            cl.load_settings(session_path.as_posix())
            cl.login(username, password)
            return cl
        except Exception:
            pass

    cl.login(username, password)
    cl.dump_settings(session_path.as_posix())
    return cl

def resolve_targets_to_ids(cl: Client, target_usernames: List[str], cache: Dict[str, int]) -> Dict[str, int]:
    resolved = {}
    for uname in target_usernames:
        if uname in cache:
            resolved[uname] = cache[uname]
            continue
        uid = cl.user_id_from_username(uname)
        cache[uname] = int(uid)
        resolved[uname] = int(uid)
        time.sleep(0.3)
    return resolved

def story_pk(story_obj: Any) -> Optional[int]:
    for attr in ("pk", "id"):
        v = getattr(story_obj, attr, None)
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.isdigit():
            return int(v)
    return None
