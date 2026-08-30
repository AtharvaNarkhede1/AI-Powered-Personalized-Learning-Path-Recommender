import re
import urllib.parse
from functools import lru_cache
from typing import List, Dict, Any
from app.core.config import settings
try:
    import requests
except Exception:  # pragma: no cover
    requests = None
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
_CACHE_VERSION = 2
_SP_PLAYLIST = "EgIQAw%3D%3D" 
_SP_LONG_VIDEO = "EgIYAg%3D%3D"
def _parse_iso8601_duration_hours(duration: str) -> float:
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    if not match:
        return 1.0
    h, m, s = (int(g) if g else 0 for g in match.groups())
    return round(max(0.1, h + m / 60 + s / 3600), 2)
def _search(params: dict) -> list:
    resp = requests.get(YOUTUBE_SEARCH_URL, params={
        "key": settings.YOUTUBE_API_KEY,
        "part": "snippet",
        "relevanceLanguage": "en",
        "safeSearch": "moderate",
        **params,
    }, timeout=6)
    resp.raise_for_status()
    return resp.json().get("items", [])
def _real_youtube_search(skill_name: str) -> List[Dict[str, Any]]:
    if not settings.YOUTUBE_API_KEY or requests is None:
        return []
    query = f"{skill_name} full course"
    try:
        playlists = []
        try:
            for it in _search({"q": f"{skill_name} tutorial playlist", "type": "playlist", "maxResults": 2}):
                pid = it.get("id", {}).get("playlistId")
                sn = it.get("snippet", {})
                if not pid:
                    continue
                playlists.append({
                    "id": f"yt_pl_{pid}",
                    "title": sn.get("title", f"{skill_name} playlist"),
                    "type": "video",
                    "provider": f"YouTube Playlist - {sn.get('channelTitle', 'Unknown')}",
                    "url": f"https://www.youtube.com/playlist?list={pid}",
                    "duration_hours": 6.0,
                    "difficulty": "beginner",
                    "skills_covered": [skill_name],
                    "rating": 4.6,
                    "is_free": True,
                    "match_reason": f"Curated YouTube playlist for '{skill_name}' -- a full multi-part course.",
                    "_views": 0,
                })
        except Exception:
            pass
        items = _search({"q": query, "type": "video", "maxResults": 5, "videoDuration": "long"})
        video_ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]
        videos = []
        if video_ids:
            details = requests.get(YOUTUBE_VIDEOS_URL, params={
                "key": settings.YOUTUBE_API_KEY,
                "id": ",".join(video_ids),
                "part": "snippet,contentDetails,statistics",
            }, timeout=6)
            details.raise_for_status()
            for it in details.json().get("items", []):
                sn, st, cd = it.get("snippet", {}), it.get("statistics", {}), it.get("contentDetails", {})
                views = int(st.get("viewCount", 0))
                likes = int(st.get("likeCount", 0))
                rating = round(min(5.0, 3.6 + (likes / max(views, 1)) * 120), 2) if views else 4.0
                videos.append({
                    "id": f"yt_{it['id']}",
                    "title": sn.get("title", f"{skill_name} tutorial"),
                    "type": "video",
                    "provider": f"YouTube - {sn.get('channelTitle', 'Unknown Channel')}",
                    "url": f"https://www.youtube.com/watch?v={it['id']}",
                    "duration_hours": _parse_iso8601_duration_hours(cd.get("duration", "")),
                    "difficulty": "intermediate",
                    "skills_covered": [skill_name],
                    "rating": rating,
                    "is_free": True,
                    "match_reason": f"Most-watched '{skill_name}' course on YouTube -- {views:,} views, {likes:,} likes.",
                    "_views": views,
                })
        videos.sort(key=lambda v: v["_views"], reverse=True)
        merged = (playlists[:1] + videos + playlists[1:])[:3]
        for m in merged:
            m.pop("_views", None)
        return merged
    except Exception:
        return []
def _fallback_search_link(skill_name: str, category: str) -> List[Dict[str, Any]]:
    course_q = urllib.parse.quote_plus(f"{skill_name} full course")
    return [{
        "id": f"yt_fallback_{urllib.parse.quote_plus(skill_name.lower())}",
        "title": f"YouTube: best '{skill_name}' full-course playlists",
        "type": "video",
        "provider": "YouTube Search",
        "url": f"https://www.youtube.com/results?search_query={course_q}&sp={_SP_PLAYLIST}",
        "duration_hours": 6.0,
        "difficulty": "beginner",
        "skills_covered": [skill_name],
        "rating": 4.0,
        "is_free": True,
        "match_reason": (
            f"Opens YouTube's playlist results for '{skill_name} full course'. "
            f"Set YOUTUBE_API_KEY in backend/.env for ranked, view-count-sorted picks."
        ),
    }]
@lru_cache(maxsize=512)
def _cached_lookup(skill_name: str, category: str, _version: int) -> tuple:
    real = _real_youtube_search(skill_name)
    return tuple(real if real else _fallback_search_link(skill_name, category))
def get_dynamic_youtube_resources(skill_name: str, category: str = "Engineering") -> List[Dict[str, Any]]:
    """Real YouTube playlists/videos (if YOUTUBE_API_KEY is set), else a playlist search link.
    Returns up to 3 dicts; never raises."""
    skill_name = (skill_name or "").strip()
    if not skill_name:
        return []
    return list(_cached_lookup(skill_name, category, _CACHE_VERSION))