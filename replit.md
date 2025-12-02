# Discord Music Bot

## Overview
This is a Discord music bot that plays music from YouTube in voice channels. Users can search for songs, manage a queue, skip tracks, and control playback using slash commands.

**Current State:** The bot is fully configured and running on Replit. It connects to Discord and responds to slash commands.

## Recent Changes
- **December 2, 2025**: Initial setup for Replit environment
  - Installed Python 3.11 and dependencies (discord.py, yt-dlp, PyNaCl)
  - Installed system dependencies (ffmpeg, libopus)
  - Configured workflow to run the bot
  - Set up Discord bot token as a secret

## Features
- **Music Playback**: Play music from YouTube by search query
- **Queue Management**: Add multiple songs to a queue
- **Playback Controls**: Skip, stop, and view the queue
- **Voice Channel Integration**: Automatically joins and leaves voice channels

## Slash Commands
- `/play <query>` - Search and play a song from YouTube
- `/skip` - Skip the current song
- `/queue` - View the current queue
- `/stop` - Stop playback and disconnect from voice channel

## Project Structure
```
.
├── discord-sing-bot.py    # Main bot code
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version specification
├── .gitignore            # Git ignore file
└── replit.md             # This documentation
```

## Dependencies
### System Dependencies
- `ffmpeg` - For audio processing
- `libopus` - For voice encoding
- Python 3.11

### Python Packages
- `discord.py[voice]` - Discord API library with voice support
- `yt-dlp` - YouTube video/audio downloader
- `PyNaCl` - Cryptography library for voice

## Configuration
The bot requires a Discord bot token stored as a secret:
- `DISCORD_BOT_TOKEN` - Your Discord bot token from the Discord Developer Portal

To get a bot token:
1. Go to https://discord.com/developers/applications
2. Create a new application or select an existing one
3. Go to the "Bot" section
4. Copy the token and add it to Replit Secrets

## Running the Bot
The bot runs automatically via the configured workflow. To manually restart:
- Click the "Run" button in Replit
- Or use: `python discord-sing-bot.py`

## Technical Notes
- FFmpeg is automatically detected from the Nix store
- The bot uses yt-dlp for YouTube audio extraction
- Voice playback uses FFmpegOpusAudio for streaming
- The bot syncs slash commands on startup

## User Preferences
None specified yet.
