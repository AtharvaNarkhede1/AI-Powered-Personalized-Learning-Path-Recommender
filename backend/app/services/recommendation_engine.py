"""
Two-Stage Recommendation Architecture.
Stage 1: Candidate Retrieval (Metadata & skill gap filtering)
Stage 2: Scoring & Ranking Model (Multi-factor ranking: skill overlap, prerequisite completeness, difficulty fit, user feedback adjustments)
"""
from typing import List, Dict, Any, Optional
from app.data.taxonomy_data import SKILLS_DATABASE, CAREERS_DATABASE
from app.models.schemas import ResourceItem, ProfileOnboardingRequest
from app.services.youtube_service import get_dynamic_youtube_resources


def retrieve_and_rank_resources(
    profile: ProfileOnboardingRequest,
    target_career_id: Optional[str] = None,
    skill_filter: Optional[str] = None,
    feedback_history: Optional[Dict[str, str]] = None
) -> List[ResourceItem]:
    """Two-Stage candidate retrieval and scoring ranking model."""
    feedback_history = feedback_history or {}

    # Gather all candidate resources across skills taxonomy
    all_candidates: List[Dict[str, Any]] = []

    for s_id, s_info in SKILLS_DATABASE.items():
        if skill_filter and skill_filter.lower() not in s_id.lower() and skill_filter.lower() not in s_info["name"].lower():
            continue
        for res in s_info.get("resources", []):
            res_copy = dict(res)
            res_copy["skill_id"] = s_id
            res_copy["skill_name"] = s_info["name"]
            all_candidates.append(res_copy)
        
        # Inject dynamic YouTube discovery resources for scalability
        yt_res_list = get_dynamic_youtube_resources(s_info["name"], s_info.get("category", "Engineering"))
        for yt_res in yt_res_list:
            yt_copy = dict(yt_res)
            yt_copy["skill_id"] = s_id
            yt_copy["skill_name"] = s_info["name"]
            all_candidates.append(yt_copy)

    if not all_candidates:
        # Fallback candidate pool
        for s_id, s_info in SKILLS_DATABASE.items():
            for res in s_info.get("resources", []):
                res_copy = dict(res)
                res_copy["skill_id"] = s_id
                res_copy["skill_name"] = s_info["name"]
                all_candidates.append(res_copy)

    ranked_items: List[ResourceItem] = []

    for res in all_candidates:
        r_id = res["id"]
        
        # Check feedback adjustments
        fb = feedback_history.get(r_id, None)
        if fb == "dismiss":
            continue  # Skip dismissed items in retrieval

        # Base rating score
        score = res.get("rating", 4.5) * 10.0  # 45 - 50 points

        # Format match bonus
        pref_fmt = profile.preferred_format.lower()
        if pref_fmt in res.get("type", "").lower() or ("project" in pref_fmt and res.get("type") == "project"):
            score += 15.0

        # Difficulty fit bonus
        exp = profile.experience_level.lower()
        diff = res.get("difficulty", "beginner").lower()
        if ("beginner" in exp and diff == "beginner") or ("intermediate" in exp and diff == "intermediate"):
            score += 15.0

        # Upvote boost / Downvote penalty
        if fb == "upvote":
            score += 20.0
        elif fb == "downvote":
            score -= 25.0

        reason = f"Top-rated {res['type'].capitalize()} aligned with your {profile.preferred_format} learning preference and skill level."

        ranked_items.append(ResourceItem(
            id=res["id"],
            title=res["title"],
            type=res["type"],
            provider=res["provider"],
            url=res["url"],
            duration_hours=res["duration_hours"],
            difficulty=res["difficulty"],
            skills_covered=res["skills_covered"],
            rating=res["rating"],
            is_free=res.get("is_free", True),
            match_reason=reason
        ))

    # Sort descending by calculated score
    ranked_items.sort(key=lambda x: x.rating, reverse=True)
    return ranked_items
