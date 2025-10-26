# Tesla App Watcher

A Python script that monitors Tesla app versions on both iOS and Android platforms and sends Discord notifications when updates are detected.

## Features

- 🍎 **iOS App Monitoring**: Tracks Tesla app version on App Store
- 🤖 **Android App Monitoring**: Tracks Tesla app version on Google Play Store  
- 📱 **Version History**: Maintains local version history with release notes
- 🚨 **Discord Notifications**: Sends webhook notifications when versions change
- ⏰ **Automated**: Can be run via cron for continuous monitoring

## Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd AppWatch
```

2. **Install dependencies**:
```bash
pip install python-dotenv requests
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your Discord webhook URL and preferences
```

4. **Run the script**:
```bash
python3 check_tesla_app.py
```

## Environment Variables

Create a `.env` file with the following variables:

```env
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
DISCORD_AVATAR_URL=https://images.seeklogo.com/logo-png/50/1/tesla-logo-png_seeklogo-506161.png
DISCORD_BOT_NAME=Tesla App Watcher
```

## Automation

Set up a cron job to run every 6 hours:

```bash
crontab -e
```

Add this line:
```bash
0 */6 * * * /usr/bin/python3 /path/to/AppWatch/check_tesla_app.py >> /path/to/AppWatch/cron.log 2>&1
```

## Discord Notifications

- **iOS updates**: White embed color (0xFFFFFF)
- **Android updates**: Dark gray embed color (0x404040)
- Shows version changes, release dates, and release notes
- Includes Tesla logo avatar

## Files

- `check_tesla_app.py`: Main monitoring script
- `.env`: Environment variables (not tracked in git)
- `.env.example`: Example environment variables
- `tesla_app_ios_version.json`: iOS version history
- `tesla_app_android_version.json`: Android version history
- `cron.log`: Cron job output log