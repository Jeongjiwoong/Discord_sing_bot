import os
import discord
from discord.ext import commands
import yt_dlp
from discord import FFmpegOpusAudio
import ctypes


def load_opus():
    search_paths = [
        "/usr/lib/libopus.so.0",
        "/usr/lib/x86_64-linux-gnu/libopus.so.0",
        "/lib/x86_64-linux-gnu/libopus.so.0",
        "/nix/store",
    ]

    for path in search_paths:
        try:
            if os.path.exists(path) or "nix" in path:
                discord.opus.load_opus(path)
                print(f"[OK] Opus loaded from: {path}")
                return True
        except Exception as e:
            pass

    print("❌ Opus not loaded.")
    return False

if not discord.opus.is_loaded():
    print("[DEBUG] Trying to load Opus...")
    load_opus()

print(f"[DEBUG] Opus Loaded: {discord.opus.is_loaded()}")



# 디버그: Opus 정상 연결 여부 확인
print("[DEBUG] Opus Loaded:", discord.opus.is_loaded())

# ----------------------
# 설정
# ----------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # 중요: 음성 이벤트 허용

bot = commands.Bot(command_prefix="!", intents=intents)

queue = []  # 음악 큐

YDL_OPTIONS = {"format": "bestaudio/best", "noplaylist": True}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


# ----------------------
# 봇 시작 이벤트
# ----------------------
@bot.event
async def on_ready():
    print(f"🎶 봇 실행됨: {bot.user}")
    await bot.tree.sync()
    print("📌 슬래시 명령어 등록 완료")


# ----------------------
# 음악 재생 함수
# ----------------------
async def play_music(interaction, query):
    if not interaction.user.voice:
        return await interaction.followup.send("❗ 먼저 음성 채널에 들어가줘!")

    voice_channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client

    if not vc:
        vc = await voice_channel.connect()

    # 유튜브 검색
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        url = info["entries"][0]["url"]
        title = info["entries"][0]["title"]

    queue.append((title, url))

    # 첫 곡이면 바로 재생
    if not vc.is_playing():
        await interaction.followup.send(f"▶️ **재생 시작:** `{title}`")
        await play_queue(interaction, vc)
    else:
        await interaction.followup.send(f"➕ `{title}` 대기열에 추가됨")


async def play_queue(interaction, vc):
    """큐가 있을 때 다음 곡 자동 재생"""
    while queue:
        title, url = queue.pop(0)
        source = discord.FFmpegOpusAudio(
            url,
            executable="/usr/bin/ffmpeg",
            **FFMPEG_OPTIONS
        )
        
        vc.play(source)
        await interaction.followup.send(f"🎵 **지금 재생 중:** `{title}`")

        while vc.is_playing():
            await asyncio.sleep(1)



# ----------------------
# 슬래시 명령어
# ----------------------
@bot.tree.command(name="play", description="노래 제목 입력하면 음악 재생")
async def play_cmd(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    await play_music(interaction, query)


@bot.tree.command(name="skip", description="현재 재생 중인 노래를 넘어갑니다")
async def skip_cmd(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭ 다음 곡으로 넘어갑니다!")
    else:
        await interaction.response.send_message("❌ 재생 중인 노래가 없습니다!")


@bot.tree.command(name="queue", description="현재 대기열을 보여줍니다")
async def queue_cmd(interaction: discord.Interaction):
    if queue:
        text = "\n".join([f"{i+1}. {name}" for i, (name, _) in enumerate(queue)])
        await interaction.response.send_message(f"📜 **대기열:**\n{text}")
    else:
        await interaction.response.send_message("📭 대기열이 비어 있습니다.")


@bot.tree.command(name="stop", description="봇을 음성 채널에서 나가기 + 큐 초기화")
async def stop_cmd(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    queue.clear()
    if vc:
        await vc.disconnect()
        await interaction.response.send_message("🛑 재생 종료 및 채널에서 나갔습니다.")
    else:
        await interaction.response.send_message("❌ 봇이 음성 채널에 없습니다.")


# ----------------------
# 실행
# ----------------------
bot.run(TOKEN)
