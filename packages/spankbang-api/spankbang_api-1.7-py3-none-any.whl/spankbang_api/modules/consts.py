import re

headers = {
    "Referer": "https://spankbang.com",
}

cookies = {
    "age_pass": "1",
    "pg_interstitial_v5": "1",
    "pg_pop_v5": "1",
    "player_quality": "1080",
    "preroll_skip": "1",
    "backend_version": "main",
    "videos_layout": "four-col"
}

PATTERN_RESOLUTION = re.compile(r'(\d+p)\.mp4')

REGEX_VIDEO_RATING = re.compile(r'<span class="rate">(.*?)</span>')
REGEX_VIDEO_AUTHOR = re.compile(r'<span class="name">(.*?)</span>')
REGEX_VIDEO_LENGTH = re.compile(r"'length'\s*:\s*(\d+)")
REGEX_VIDEO_PROCESSING = re.compile(r'<div class="warning_process">')