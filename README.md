# Instagram Story Checker with Email Notifications


This script checks for new stories uploaded by users you follow on Instagram. It sends email notifications when a new story is uploaded by specific users, and optionally downloads the stories to your local system.

## Features:
- Check for new stories uploaded by specified Instagram users.
- Send email notifications when a new story is posted by selected users.
- Optionally download the new stories to a local directory.
- Store the last seen story for each user to avoid processing the same stories multiple times.

## Requirements:
1. **Python 3.x** (Recommended: Python 3.8+)
2. **instagrapi**: A Python library for interacting with Instagram.
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

```text
user1
user2
user3
```

### 4. Running the Script

```bash
python main.py \
  --targets targets.txt \
  --notify notify_users.txt \
  --download \
  --out downloads \
  --min_sleep 1.5 \
  --max_sleep 4.0
```

- `--targets`: Path to the file that contains the usernames of the users you want to track.

- `--download`: (Optional) If included, the script will download the new stories to a local folder.

- `--out`: (Optional) Specifies the output folder where downloaded stories will be saved. Default is downloads.


### 5. Email Notifications

Email notifications are sent only for users listed in a separate file called `notify_users.txt`.

This file should contain one Instagram username per line:

```text
user1
user2
```

To enable notifications, pass the file using:

```bash
python main.py --targets targets.txt --notify notify_users.txt
```

If `notify_users.txt` is missing or empty, the script will still run, but **no emails will be sent**.



### 6. File Structure

```graphql
InstagramStoryChecker/
│
├── ig_session.json        # Instagram session cache (auto-created)
├── notify_users.txt       # Users that trigger email notifications
├── app.log                # Application log file
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

- **Email not sent**: Ensure that you've set up App Passwords properly.
  
  If you face any issues with Gmail's SMTP, check your Google account settings or review Gmail's security settings.

- **No new stories detected**: Ensure that the `last_seen` data is being correctly updated in the `story_state.json` file. If you've added new users, ensure they're initialized in the state file with a default value (e.g., 0).

- **Missing dependencies**: If you encounter missing dependencies, ensure you've installed all necessary Python packages.

### Disclaimer

This project is provided **for educational and research purposes only**.

The script interacts with Instagram through unofficial means and may violate
Instagram’s Terms of Service. The author does **not** encourage or endorse the
use of this software for abusive, commercial, or large-scale automated activity.

By using this software, you acknowledge and agree that:

- You are solely responsible for how you use this code.
- You understand that automating interactions with Instagram may result in
  account restrictions, temporary blocks, or permanent bans.
- The author assumes **no liability** for any damages, account actions, or losses
  resulting from the use of this software.
- You are responsible for ensuring your use complies with all applicable laws,
  regulations, and platform terms.

This project is shared to demonstrate concepts such as:
- API interaction
- Session handling
- Rate limiting and randomized delays
- State persistence
- Email notifications and logging

If you choose to use this code against the terms of any service, you do so
**entirely at your own risk**.

### TODO

In the future I would like to also expand this repo with the following modules:
- Adding stories (photo/video) from files
- Emailing when someone messages me/replies to a story
-



### Security Notes

- Do NOT commit `.env`, `ig_session.json`, or proxy credentials
- Use a dedicated Instagram account
- Avoid running the script too frequently
- Consider residential proxies for long-term use

### Known Limitations

- Uses Instagram private APIs (may break if Instagram changes behavior)
- Accounts may be temporarily restricted if used aggressively
- Gmail attachments are limited to ~25 MB; larger videos may fail to send


### License

This project is licensed under the MIT License.
