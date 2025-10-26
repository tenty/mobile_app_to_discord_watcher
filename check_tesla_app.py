#!/usr/bin/env python3
import requests
import re
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_app_store_info(app_url):
    """Fetch app info from App Store page and API"""
    try:
        # Extract app ID from URL
        app_id_match = re.search(r'/id(\d+)', app_url)
        if not app_id_match:
            return None, None, None, None, None, None, None
        
        app_id = app_id_match.group(1)
        
        # Try Apple's public API first
        api_url = f"https://itunes.apple.com/lookup?id={app_id}&country=au"
        api_response = requests.get(api_url)
        api_response.raise_for_status()
        
        api_data = api_response.json()
        if api_data.get('resultCount', 0) > 0:
            app_info = api_data['results'][0]
            current_version = app_info.get('version')
            current_date = app_info.get('currentVersionReleaseDate', '')
            release_notes = app_info.get('releaseNotes', '')
            
            # Format date
            if current_date:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(current_date.replace('Z', '+00:00'))
                    current_date = dt.strftime('%d %b %Y')
                except:
                    pass
            
            # Also fetch the webpage to get more detailed info
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            web_response = requests.get(app_url, headers=headers)
            web_response.raise_for_status()
            
            # Extract release date from webpage
            date_pattern = r'<time[^>]*>([^<]+)</time>'
            date_match = re.search(date_pattern, web_response.text)
            if date_match:
                current_date = date_match.group(1).strip()
            
            # Extract release notes from webpage if API didn't provide them
            if not release_notes:
                version_match = re.search(r'Version \d+\.\d+(?:\.\d+)?', web_response.text)
                if version_match:
                    notes_pattern = r'Version \d+\.\d+(?:\.\d+)?[^<]*</p>.*?<p[^>]*>([^<]+)'
                    notes_match = re.search(notes_pattern, web_response.text, re.DOTALL | re.IGNORECASE)
                    if notes_match:
                        release_notes = notes_match.group(1).strip()
                        release_notes = release_notes.replace('&#39;', "'")
                        release_notes = release_notes.replace('&amp;', '&')
                        release_notes = re.sub(r'\s+', ' ', release_notes)
            
            # Try to get version history from the Apple API
            previous_version = None
            previous_date = None
            previous_notes = None
            
            # For now, we'll store the previous version from our local data
            # The App Store doesn't easily expose version history via public APIs
            
            return current_version, current_date, release_notes, previous_version, previous_date, previous_notes, None
        
        return None, None, None, None, None, None, None
        
    except Exception as e:
        print(f"Error fetching app info: {e}")
        return None, None, None, None, None, None, None

def get_play_store_info(app_url):
    """Fetch app info from Google Play Store"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(app_url, headers=headers)
        response.raise_for_status()
        
        # Extract version from the JSON data in the page
        version_pattern = r'\[\["([^"]+\d+-\d+)"\]\]'
        version_match = re.search(version_pattern, response.text)
        
        if not version_match:
            # Alternative pattern for version
            version_pattern = r'(\d+\.\d+\.\d+-\d+)'
            version_match = re.search(version_pattern, response.text)
        
        current_version = version_match.group(1) if version_match else None
        
        # Extract release date
        date_pattern = r'\["(\d{1,2}\s+\w+\s+\d{4)",\['
        date_match = re.search(date_pattern, response.text)
        if not date_match:
            date_pattern = r'Updated.*?(\d{1,2}\s+\w+\s+\d{4})'
            date_match = re.search(date_pattern, response.text, re.IGNORECASE)
        
        current_date = date_match.group(1) if date_match else None
        
        # Extract release notes from the JSON data
        release_notes = ""
        notes_pattern = r'\[null,"([^"]+)"\],\["\d{1,2}\s+\w+\s+\d{4}"'
        notes_match = re.search(notes_pattern, response.text)
        
        if notes_match:
            release_notes = notes_match.group(1).strip()
            # Filter out common non-release-note content
            if len(release_notes) < 10 or release_notes.isdigit():
                release_notes = ""
        else:
            # Fallback: look for "What's new" section
            notes_pattern = r'What.s.new[^>]*>([^<]+)'
            notes_match = re.search(notes_pattern, response.text, re.IGNORECASE)
            if notes_match:
                release_notes = notes_match.group(1).strip()
        
        # If no release notes found, indicate this
        if not release_notes:
            release_notes = "No release notes available on Play Store"
        
        return current_version, current_date, release_notes, None, None, None, None
        
    except Exception as e:
        print(f"Error fetching Play Store info: {e}")
        return None, None, None, None, None, None, None

def load_previous_version(platform='ios'):
    """Load previously stored version"""
    filename = f'tesla_app_{platform}_version.json'
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                return data.get('version'), data.get('last_checked'), data.get('release_notes', '')
        except:
            pass
    return None, None, ""

def save_current_version(version, release_notes="", platform='ios'):
    """Save current version to file"""
    filename = f'tesla_app_{platform}_version.json'
    data = {
        'version': version,
        'release_notes': release_notes,
        'last_checked': datetime.now().isoformat()
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def send_discord_webhook(platform, old_version, new_version, old_notes, new_notes, release_date):
    """Send Discord notification about version change"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    avatar_url = os.getenv('DISCORD_AVATAR_URL')
    bot_name = os.getenv('DISCORD_BOT_NAME', 'Tesla App Watcher')
    
    if not webhook_url:
        print("❌ Discord webhook URL not found in environment variables")
        return
    
    # Set embed color based on platform
    if platform.lower() == 'ios':
        color = 0xFFFFFF  # White for iOS
        platform_emoji = "🍎"
        platform_name = "iOS"
    else:
        color = 0x404040  # Dark gray for Android
        platform_emoji = "🤖"
        platform_name = "Android"
    
    # Create embed
    embed = {
        "title": f"{platform_emoji} Tesla App Updated - {platform_name}",
        "description": f"The Tesla app has been updated on {platform_name}!",
        "color": color,
        "fields": [
            {
                "name": "Version Change",
                "value": f"**{old_version}** → **{new_version}**",
                "inline": True
            },
            {
                "name": "Release Date",
                "value": release_date,
                "inline": True
            }
        ],
        "timestamp": datetime.now().isoformat(),
        "footer": {
            "text": "Tesla App Watcher"
        }
    }
    
    # Add release notes if available
    if new_notes and new_notes != "No release notes available on Play Store":
        embed["fields"].append({
            "name": "📝 Release Notes",
            "value": new_notes,
            "inline": False
        })
    
    # Add old release notes if available and different
    if old_notes and old_notes != new_notes and old_notes != "No release notes available on Play Store":
        embed["fields"].append({
            "name": "📜 Previous Release Notes",
            "value": old_notes,
            "inline": False
        })
    
    payload = {
        "embeds": [embed],
        "avatar_url": avatar_url,
        "username": bot_name
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Discord notification sent for {platform_name} update!")
    except Exception as e:
        print(f"❌ Failed to send Discord notification: {e}")

def check_ios_app():
    """Check iOS Tesla app version"""
    print("\n" + "="*50)
    print("🍎 iOS Tesla App")
    print("="*50)
    
    app_url = "https://apps.apple.com/au/app/tesla/id582007913"
    
    # Get app information from App Store
    current_version, current_date, current_notes, _, _, _, _ = get_app_store_info(app_url)
    
    if not current_version:
        print("❌ Failed to fetch iOS version information")
        return
    
    print(f"Current version: {current_version} (Released: {current_date})")
    if current_notes:
        print(f"Release notes: {current_notes}")
    
    # Load stored version for comparison
    stored_version, last_checked, stored_notes = load_previous_version('ios')
    
    if stored_version:
        print(f"Last checked: {last_checked}")
        
        if current_version != stored_version:
            print(f"\n🚨 iOS VERSION CHANGED!")
            print(f"Old version: {stored_version}")
            if stored_notes:
                print(f"Old release notes: {stored_notes}")
            print(f"New version: {current_version} (Released: {current_date})")
            if current_notes:
                print(f"New release notes: {current_notes}")
            
            # Send Discord notification
            send_discord_webhook('ios', stored_version, current_version, stored_notes, current_notes, current_date)
        else:
            print("\n✅ No iOS version change detected")
    else:
        print("\n📝 First time checking iOS app - saving baseline version")
    
    # Save current version for next check
    save_current_version(current_version, current_notes or "", 'ios')

def check_android_app():
    """Check Android Tesla app version"""
    print("\n" + "="*50)
    print("🤖 Android Tesla App")
    print("="*50)
    
    app_url = "https://play.google.com/store/apps/details?id=com.teslamotors.tesla&hl=en_AU"
    
    # Get app information from Play Store
    current_version, current_date, current_notes, _, _, _, _ = get_play_store_info(app_url)
    
    if not current_version:
        print("❌ Failed to fetch Android version information")
        return
    
    print(f"Current version: {current_version} (Updated: {current_date})")
    if current_notes:
        print(f"What's new: {current_notes}")
    
    # Load stored version for comparison
    stored_version, last_checked, stored_notes = load_previous_version('android')
    
    if stored_version:
        print(f"Last checked: {last_checked}")
        
        if current_version != stored_version:
            print(f"\n🚨 Android VERSION CHANGED!")
            print(f"Old version: {stored_version}")
            if stored_notes:
                print(f"Old release notes: {stored_notes}")
            print(f"New version: {current_version} (Updated: {current_date})")
            if current_notes:
                print(f"New release notes: {current_notes}")
            
            # Send Discord notification
            send_discord_webhook('android', stored_version, current_version, stored_notes, current_notes, current_date)
        else:
            print("\n✅ No Android version change detected")
    else:
        print("\n📝 First time checking Android app - saving baseline version")
    
    # Save current version for next check
    save_current_version(current_version, current_notes or "", 'android')

def main():
    print("🚗 Checking Tesla App Versions...")
    
    # Check both iOS and Android apps
    check_ios_app()
    check_android_app()
    
    print("\n" + "="*50)
    print("✅ Check completed!")
    print("="*50)

if __name__ == "__main__":
    main()