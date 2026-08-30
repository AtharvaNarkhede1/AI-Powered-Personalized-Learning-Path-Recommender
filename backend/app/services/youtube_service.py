"""
YouTube Resource Discovery Service.

If YOUTUBE_API_KEY is configured, calls the real YouTube Data API v3
(search.list + videos.list) to get actual video titles, channel names,
durations, and engagement (view/like counts used as a real quality signal).
Results are cached in-process per skill to stay well within the free 10k
quota units/day.

If no key is configured, falls back to a static search-results link (no
fabricated per-video metadata -- previously this fallback invented ratings
like 4.95 that fed directly into ranking as if they were real).
"""
import re
import urllib.parse
from functools import lru_cache
from typing import List, Dict, Any

from app.core.config import settings

try:
    import requests
except Exception:
    requests = None

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def _parse_iso8601_duration_hours(duration: str) -> float:
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    if not match:
        return 1.0
    h, m, s = (int(g) if g else 0 for g in match.groups())
    hours = h + m / 60 + s / 3600
    return round(max(0.1, hours), 2)


def _real_youtube_search(skill_name: str) -> List[Dict[str, Any]]:
    if not settings.YOUTUBE_API_KEY or requests is None:
        return []
    try:
        search_resp = requests.get(YOUTUBE_SEARCH_URL, params={
            "key": settings.YOUTUBE_API_KEY,
            "q": f"{skill_name} full course tutorial",
            "part": "snippet",
            "type": "video",
            "maxResults": 3,
            "relevanceLanguage": "en",
            "videoDuration": "long",
        }, timeout=6)
        search_resp.raise_for_status()
        items = search_resp.json().get("items", [])
        video_ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]
        if not video_ids:
            return []

        details_resp = requests.get(YOUTUBE_VIDEOS_URL, params={
            "key": settings.YOUTUBE_API_KEY,
            "id": ",".join(video_ids),
            "part": "snippet,contentDetails,statistics",
        }, timeout=6)
        details_resp.raise_for_status()
        detail_items = details_resp.json().get("items", [])

        results = []
        for it in detail_items:
            snippet = it.get("snippet", {})
            stats = it.get("statistics", {})
            content = it.get("contentDetails", {})
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            # Real engagement-based rating proxy: like ratio, scaled onto our 0-5 display scale
            rating = round(min(5.0, 3.5 + (likes / max(views, 1)) * 150), 2) if views else 4.0
            results.append({
                "id": f"yt_{it['id']}",
                "title": snippet.get("title", f"{skill_name} tutorial"),
                "type": "video",
                "provider": f"YouTube - {snippet.get('channelTitle', 'Unknown Channel')}",
                "url": f"https://www.youtube.com/watch?v={it['id']}",
                "duration_hours": _parse_iso8601_duration_hours(content.get("duration", "")),
                "difficulty": "intermediate",
                "skills_covered": [skill_name],
                "rating": rating,
                "is_free": True,
                "match_reason": f"Real YouTube result for '{skill_name}' -- {views:,} views, {likes:,} likes.",
            })
        return results
    except Exception:
        return []


def _fallback_search_link(skill_name: str, category: str) -> List[Dict[str, Any]]:
    encoded_query = urllib.parse.quote_plus(f"{skill_name} full course tutorial masterclass")
    search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    return [{
        "id": f"yt_fallback_{urllib.parse.quote_plus(skill_name.lower())}",
        "title": f"Search YouTube: {skill_name} Courses & Playlists",
        "type": "video",
        "provider": "YouTube Search (no API key configured)",
        "url": search_url,
        "duration_hours": 1.0,
        "difficulty": "beginner",
        "skills_covered": [skill_name],
        "rating": 4.0,  # neutral default -- not a claim of real quality
        "is_free": True,
        "match_reason": f"Set YOUTUBE_API_KEY to get real ranked results for {category} - {skill_name}; showing a search link for now.",
    }]


@lru_cache(maxsize=256)
def _cached_lookup(skill_name: str, category: str) -> tuple:
    real = _real_youtube_search(skill_name)
    results = real if real else _fallback_search_link(skill_name, category)
    return tuple(results)


def get_dynamic_youtube_resources(skill_name: str, category: str = "Engineering") -> List[Dict[str, Any]]:
    """Returns real YouTube video resources (if YOUTUBE_API_KEY is set) or a fallback search link."""
    return list(_cached_lookup(skill_name, category))
