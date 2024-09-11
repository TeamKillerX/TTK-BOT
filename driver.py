import datetime
import json
import os
import random
import re
import time
import urllib.parse
import httpx
import requests
from urllib.parse import quote_plus

def format_text(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "]+",
        flags=re.UNICODE,
    )

    return re.sub(emoji_pattern, "", text)

class YoutubeDriver:
    def __init__(self, search_terms: str, max_results: int = 5):
        self.base_url = "https://youtube.com/results?search_query={0}"
        self.search_terms = search_terms
        self.max_results = max_results
        self.videos = self._search()

    def _search(self):
        encoded_search = urllib.parse.quote_plus(self.search_terms)
        response = requests.get(self.base_url.format(encoded_search)).text

        while "ytInitialData" not in response:
            response = requests.get(self.base_url.format(encoded_search)).text

        results = self._parse_html(response)

        if self.max_results is not None and len(results) > self.max_results:
            return results[: self.max_results]

        return results

    def _parse_html(self, response: str):
        results = []
        start = response.index("ytInitialData") + len("ytInitialData") + 3
        end = response.index("};", start) + 1
        json_str = response[start:end]
        data = json.loads(json_str)

        videos = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
            "sectionListRenderer"
        ]["contents"][0]["itemSectionRenderer"]["contents"]

        for video in videos:
            res = {}
            if "videoRenderer" in video.keys():
                video_data = video.get("videoRenderer", {})
                _id = video_data.get("videoId", None)

                res["id"] = _id
                res["thumbnail"] = f"https://i.ytimg.com/vi/{_id}/hqdefault.jpg"
                res["title"] = (
                    video_data.get("title", {}).get("runs", [[{}]])[0].get("text", None)
                )
                res["channel"] = (
                    video_data.get("longBylineText", {})
                    .get("runs", [[{}]])[0]
                    .get("text", None)
                )
                res["duration"] = video_data.get("lengthText", {}).get("simpleText", 0)
                res["views"] = video_data.get("viewCountText", {}).get(
                    "simpleText", "Unknown"
                )
                res["publish_time"] = video_data.get("publishedTimeText", {}).get(
                    "simpleText", "Unknown"
                )
                res["url_suffix"] = (
                    video_data.get("navigationEndpoint", {})
                    .get("commandMetadata", {})
                    .get("webCommandMetadata", {})
                    .get("url", None)
                )
                results.append(res)
        return results

    def to_dict(self, clear_cache=True) -> list[dict]:
        result = self.videos
        if clear_cache:
            self.videos = []
        return result

    @staticmethod
    def check_url(url: str) -> tuple[bool, str]:
        if "&" in url:
            url = url[: url.index("&")]

        if "?si=" in url:
            url = url[: url.index("?si=")]

        youtube_regex = (
            r"(https?://)?(www\.)?"
            r"(youtube|youtu|youtube-nocookie)\.(com|be)/"
            r'(video|embed|shorts/|watch\?v=|v/|e/|u/\\w+/|\\w+/)?([^"&?\\s]{11})'
        )
        match = re.match(youtube_regex, url)
        if match:
            return True, match.group(6)
        else:
            return False, "Invalid YouTube URL!"

    @staticmethod
    def song_options() -> dict:
        return {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "480",
                }
            ],
            "cookiefile": "cookies.txt",
            "outtmpl": "%(id)s",
            "quiet": True,
            "logtostderr": False,
        }

    @staticmethod
    def video_options() -> dict:
        return {
            "format": "best",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }
            ],
            "cookiefile": "cookies.txt",
            "outtmpl": "%(id)s.mp4",
            "quiet": True,
            "logtostderr": False,
        }
