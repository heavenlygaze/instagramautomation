# Instagram Story Checker with Email Notifications

This script checks for new stories uploaded by users you follow on Instagram. It sends email notifications when a new story is uploaded by specific users, and optionally downloads the stories to your local system.

## Features:
- Check for new stories uploaded by specified Instagram users.
- Send email notifications when a new story is posted by a specific user.
- Optionally download the new stories to a local directory.
- Store the last seen story for each user to avoid processing the same stories multiple times.

## Requirements:
1. **Python 3.x** (Recommended: Python 3.8+)
2. **Instagrapi**: A Python library for interacting with Instagram.
3. **SMTP server credentials** (for Gmail in this case, with an App Password).

## Installation & Setup:

### 1. Install Dependencies
To use this script, you need to install the required dependencies. You can do this using `pip`.

```bash
pip install instagrapi python-dotenv
```

### 2. Set Up Email Notifications

You'll need to configure Gmail's App Password for email notifications. Follow these steps:

1. Enable Two-Factor Authentication (2FA) on your Google account if it's not already enabled.
2. Generate an App Password:

   - Go to Google App Passwords

   - Select "Mail" as the app and "Other" for the device, then enter a custom name like InstagramScript.

   - Google will generate a 16-character App Password for you. Save it securely.

3. Create a .env file to store your sensitive information (email credentials, Instagram credentials):
```dotenv
IG_USERNAME=your_instagram_username
IG_PASSWORD=your_instagram_password
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_16_character_app_password
```

### 3. Prepare targets.txt

Create a `targets.txt` file with the usernames of the Instagram accounts you want to track. Each username should be on a new line, for example:

```textxt
user1
user2
user3
```

### 4. Running the Script

```bash
python main.py --targets targets.txt --download --out downloads

```

- `--targets`: Path to the file that contains the usernames of the users you want to track.

- `--download`: (Optional) If included, the script will download the new stories to a local folder.

- `--out`: (Optional) Specifies the output folder where downloaded stories will be saved. Default is downloads.


### 5. Email Notifications

The script will send an email notification whenever a new story is posted by any of the users listed in `users_to_notify` (defined in `main.py`). You can specify which users should trigger an email by editing the list:

```python
users_to_notify = ['specific_user1', 'specific_user2']  # Define which users you want to be notified about
```

### 6. File Structure

```graphql
InstagramStoryChecker/
│
├── main.py                # The entry point of the program
├── config.py              # Configuration file for loading credentials
├── email_utils.py         # Functions to handle sending emails
├── file_utils.py          # Functions for file reading and saving
├── instagrapi_utils.py    # Functions related to instagrapi
├── state_utils.py         # Functions to load and save the state
├── targets.txt            # List of Instagram usernames to track
├── story_state.json       # State file to store the last seen stories
├── .env                   # Environment variables for Instagram and email credentials
└── README.md              # This file
```

### 7. How It Works

- **Session Reuse**: The script uses the session stored in `ig_session.json` to avoid logging in every time you run it.

- **Story Tracking**: It tracks the last seen story for each user by storing their latest story ID in the `story_state.json` file. This allows the script to know which stories are "new" since the last time it ran.

- **Email Notification**: When a new story is detected for a specified user, the script sends an email notification using Gmail's SMTP service. Make sure you have generated an App Password for secure email authentication.

- **Story Download**: If the `--download` flag is included, the script will download any new stories to the directory specified by `--out`.


### 8. .env File Example
Your `.env` file should look like this:

```dotenv
IG_USERNAME=your_instagram_username
IG_PASSWORD=your_instagram_password
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_16_character_app_password
```

### 9. Example Output
When you run the script, you should see output similar to this

```bash
@user1: NEW stories detected (2 items)
  downloaded: /path/to/downloads/user1/story1.mp4
  downloaded: /path/to/downloads/user1/story2.mp4
@user2: NEW stories detected (1 item)
  downloaded: /path/to/downloads/user2/story3.mp4
@user3: no new stories since last check
```

### 10. Troubleshooting

- **Email not sent**: Ensure that you've enabled less secure apps for Gmail (if not using 2FA) or set up App Passwords properly if you're using two-factor authentication.
  
  If you face any issues with Gmail's SMTP, check your Google account settings or review Gmail's security settings.

- **No new stories detected**: Ensure that the `last_seen` data is being correctly updated in the `story_state.json` file. If you've added new users, ensure they're initialized in the state file with a default value (e.g., 0).

- **Missing dependencies**: If you encounter missing dependencies, ensure you've installed all necessary Python packages.


### License

This project is licensed under the MIT License.

---

**Note:** Make sure to keep your .env file secure and never share it publicly as it contains sensitive information (like your Gmail credentials and Instagram login details).
