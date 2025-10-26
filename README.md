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
DISCORD_WEBHOOK_URLS=your_discord_webhook_url_here,another_webhook_url_here
DISCORD_AVATAR_URL=your_avatar_url_here
DISCORD_BOT_NAME=your_bot_name_here
```

**Multiple Webhooks**: You can specify multiple Discord webhook URLs separated by commas. The script will send notifications to all of them.

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
- `tesla_app_ios_version_history.json`: iOS version history (created on first run)
- `tesla_app_android_version_history.json`: Android version history (created on first run)
- `cron.log`: Cron job output log

## Version History Logic

**JSON files are created on first run** and maintain full version history:

### File Structure (`tesla_app_{platform}_version_history.json`):
```json
{
  "platform": "ios|android",
  "last_updated": "2025-10-26T01:12:00.367696",
  "history": [
    {
      "version": "4.50.1",
      "release_notes": "This release contains minor fixes and improvements.",
      "release_date": "23 Oct 2025",
      "last_checked": "2025-10-26T01:12:00.367689"
    }
  ]
}
```

**How it works**:
1. **First run**: Creates JSON file with current version as baseline
2. **Subsequent runs**: Compares current version with latest stored version
3. **Version change detected**: 
   - Sends Discord notification with old vs new version
   - Adds new version to beginning of history array
   - **Preserves all previous versions** (keeps last 10 versions)
4. **History management**: Automatically maintains last 10 versions to prevent file bloat

**Benefits**:
- ✅ **Full version history**: Tracks all recent versions, not just immediate previous
- ✅ **Complete data**: Preserves release notes and dates for all versions
- ✅ **Automatic cleanup**: Keeps only last 10 versions to manage file size
- ✅ **Rich comparison**: Can compare current version with any previous version