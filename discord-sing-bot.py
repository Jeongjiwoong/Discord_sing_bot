import os
import asyncio
import subprocess
import discord
from discord.ext import commands
import yt_dlp

# ---------------------------------
# 환경 변수 로드
# ---------------------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []


# ---------------------------------
# 🔧 FFmpeg 자동 탐색
# ---------------------------------
def find_ffmpeg():
    candidates = [
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/bin/ffmpeg",
    ]

    # PATH 기반 검색
    for path in os.getenv("PATH", "").split(":"):
        full_path = os.path.join(path, "ffmpeg")
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return full_path

    # Linux 환경에서 which ffmpeg 시도
    try:
        result = subprocess.run(["which", "ffmpeg"], stdout=subprocess.PIPE, text=True)
        if result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    return None


FFMPEG_EXECUTABLE = find_ffmpeg()
print(f"[DEBUG] FFmpeg Path → {FFMPEG_EXECUTABLE}")


# ---------------------------------
# 🔧 Opus 자동 로딩
# ---------------------------------
def load_opus():
    search_paths = [
        "/usr/lib/libopus.so.0",
        "/usr/lib/x86_64-linux-gnu/libopus.so.0",
        "/lib/x86_64-linux-gnu/libopus.so.0",
        "/nix/store",
    ]

    for path in search_paths:
        try:
            discord.opus.load_opus(path)
            print(f"[OK] Opus loaded: {path}")
            return True
        except:
            pass

    return False


if not discord.opus.is_loaded():
    print("[DEBUG] Loading Opus...")
    load_opus()

print(f"[DEBUG] Opus Loaded: {discord.opus.is_loaded()}")


# ---------------------------------
# yt-dlp 설정
# ---------------------------------
YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "extractor_args": {"youtube": {"player_client": "default"}}
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


# ---------------------------------
# 봇 이벤트
# ---------------------------------
@bot.event
async def on_ready():
    print(f"🎶 Bot Online: {bot.user}")
    await bot.tree.sync()
    print("📌 Slash Commands Ready")


# ---------------------------------
# 음악 실행 로직
# ---------------------------------
async def play_music(interaction, query):
    if not interaction.user.voice:
        return await interaction.response.send_message("❗ 먼저 음성 채널에 들어가줘!")

    voice_channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client

    if not vc:
        vc = await voice_channel.connect()

    # 음악 검색
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        url = info["entries"][0]["url"]
        title = info["entries"][0]["title"]

    queue.append((title, url))

    if not vc.is_playing():
        await interaction.followup.send(f"▶️ **재생 중:** `{title}`")
        await play_queue(interaction, vc)
    else:
        await interaction.followup.send(f"➕ `{title}` 대기열에 추가됨")


async def play_queue(interaction, vc):
    while queue:
        title, url = queue.pop(0)

        source = discord.FFmpegOpusAudio(
            url,
            executable=FFMPEG_EXECUTABLE,
            **FFMPEG_OPTIONS
        )

        vc.play(source)
        await interaction.followup.send(f"🎵 **지금 재생 중:** `{title}`")

        while vc.is_playing():
            await asyncio.sleep(1)


# ---------------------------------
# 슬래시 명령어
# ---------------------------------
@bot.tree.command(name="play", description="노래 제목 입력하면 재생함")
async def play_cmd(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    await play_music(interaction, query)


@bot.tree.command(name="skip", description="현재 노래 스킵")
async def skip_cmd(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭ 다음 곡으로 넘어갑니다!")
    else:
        await interaction.response.send_message("❌ 재생 중인 음악이 없어요!")


@bot.tree.command(name="queue", description="대기열 보기")
async def queue_cmd(interaction: discord.Interaction):
    if queue:
        msg = "\n".join([f"{i+1}. {name}" for i, (name, _) in enumerate(queue)])
        await interaction.response.send_message(f"📜 **대기열:**\n{msg}")
    else:
        await interaction.response.send_message("📭 대기열이 비어 있습니다.")


@bot.tree.command(name="stop", description="봇 종료 & 음성 채널 나가기")
async def stop_cmd(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    queue.clear()
    if vc:
        await vc.disconnect()
        await interaction.response.send_message("🛑 재생 종료 및 채널에서 나갔습니다.")
    else:
        await interaction.response.send_message("❌ 봇이 음성 채널에 없습니다.")


# ---------------------------------
# 실행
# ---------------------------------
bot.run(TOKEN)
