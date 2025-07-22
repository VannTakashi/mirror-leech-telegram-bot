from time import time
from re import search as research
from asyncio import gather, sleep as asyncio_sleep
from aiofiles.os import path as aiopath
from psutil import (
    disk_usage,
    cpu_percent,
    swap_memory,
    cpu_count,
    virtual_memory,
    net_io_counters,
    boot_time,
)

from .. import bot_start_time
from ..helper.ext_utils.status_utils import get_readable_file_size, get_readable_time
from ..helper.ext_utils.bot_utils import cmd_exec, new_task
from ..helper.telegram_helper.message_utils import send_message, edit_message

commands = {
    "aria2": (["aria2c", "--version"], r"aria2 version ([\d.]+)"),
    "qBittorrent": (["qbittorrent-nox", "--version"], r"qBittorrent v([\d.]+)"),
    "SABnzbd+": (["sabnzbdplus", "--version"], r"sabnzbdplus-([\d.]+)"),
    "python": (["python3", "--version"], r"Python ([\d.]+)"),
    "rclone": (["rclone", "--version"], r"rclone v([\d.]+)"),
    "yt-dlp": (["yt-dlp", "--version"], r"([\d.]+)"),
    "ffmpeg": (["ffmpeg", "-version"], r"ffmpeg version ([\d.]+(-\w+)?).*"),
    "7z": (["7z", "i"], r"7-Zip ([\d.]+)"),
}

def create_progress_bar(percentage, length=10):
    filled_blocks = int(length * percentage / 100)
    empty_blocks = length - filled_blocks
    bar = "■" * filled_blocks + "□" * empty_blocks
    return f"[{bar}] {percentage:.1f}%"

async def get_bot_stats_text():
    total, used, free, disk_percent = disk_usage("/")
    swap = swap_memory()
    memory = virtual_memory()

    cpu_p = cpu_percent(interval=0.5)

    stats = f"""
<b>Tanggal Komit:</b> {commands["commit"]}

<b>Uptime Bot:</b> {get_readable_time(time() - bot_start_time)}
<b>Uptime OS:</b> {get_readable_time(time() - boot_time())}

<b>Total Disk:</b> {get_readable_file_size(total)}
<b>Digunakan:</b> {get_readable_file_size(used)} | <b>Bebas:</b> {get_readable_file_size(free)}
<b>DISK:</b> <code>{create_progress_bar(disk_percent)}</code>

<b>Upload:</b> {get_readable_file_size(net_io_counters().bytes_sent)}
<b>Download:</b> {get_readable_file_size(net_io_counters().bytes_recv)}

<b>CPU:</b> <code>{create_progress_bar(cpu_p)}</code>
<b>RAM:</b> <code>{create_progress_bar(memory.percent)}</code>

<b>Core Fisik CPU:</b> {cpu_count(logical=False)}
<b>Total Core CPU:</b> {cpu_count()}
<b>SWAP:</b> {get_readable_file_size(swap.total)} | <b>Digunakan:</b> <code>{create_progress_bar(swap.percent)}</code>

<b>Total Memori:</b> {get_readable_file_size(memory.total)}
<b>Memori Bebas:</b> {get_readable_file_size(memory.available)}
<b>Memori Digunakan:</b> {get_readable_file_size(memory.used)}

<b>python:</b> <code>{commands["python"]}</code>
<b>aria2:</b> <code>{commands["aria2"]}</code>
<b>qBittorrent:</b> <code>{commands["qBittorrent"]}</code>
<b>SABnzbd+:</b> <code>{commands["SABnzbd+"]}</code>
<b>rclone:</b> <code>{commands["rclone"]}</code>
<b>yt-dlp:</b> <code>{commands["yt-dlp"]}</code>
<b>ffmpeg:</b> <code>{commands["ffmpeg"]}</code>
<b>7z:</b> <code>{commands["7z"]}</code>
"""
    return stats

@new_task
async def bot_stats(_, message):
    msg = await send_message(message, "Mengambil statistik bot... 📊")

    update_interval = 5
    max_updates = 6

    for _ in range(max_updates):
        stats_text = await get_bot_stats_text()
        await edit_message(msg, stats_text)
        await asyncio_sleep(update_interval)

async def get_version_async(command, regex):
    try:
        out, err, code = await cmd_exec(command)
        if code != 0:
            return f"Error: {err}"
        match = research(regex, out)
        return match.group(1) if match else "Versi tidak ditemukan"
    except Exception as e:
        return f"Pengecualian: {str(e)}"

@new_task
async def get_packages_version():
    tasks = [get_version_async(command, regex) for command, regex in commands.values()]
    versions = await gather(*tasks)
    for tool, version in zip(commands.keys(), versions):
        commands[tool] = version
    if await aiopath.exists(".git"):
        last_commit, err, code = await cmd_exec(
            "git log -1 --date=short --pretty=format:'%cd <b>Dari</b> %cr'", True
        )
        if code != 0:
            last_commit = f"Error mengambil komit: {err or 'Unknown'}"
    else:
        last_commit = "Tidak ada UPSTREAM_REPO"
    commands["commit"] = last_commit