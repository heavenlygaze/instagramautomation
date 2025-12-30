from dotenv import load_dotenv
import os


def load_dotenv_and_get_credentials() -> tuple:
    load_dotenv()
    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")
    email_username = os.getenv("EMAIL_USERNAME")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not username or not password:
        raise ValueError("Missing IG_USERNAME / IG_PASSWORD env vars.")

    if not email_username or not email_password:
        raise ValueError("Missing EMAIL_USERNAME / EMAIL_PASSWORD env vars.")

    return username, password, email_username, email_password
