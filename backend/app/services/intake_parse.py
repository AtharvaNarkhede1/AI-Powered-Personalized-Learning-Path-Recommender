from __future__ import annotations

import re
from typing import Dict, List

from app.data.keywords_data import ENGINEERING_KEYWORDS_VOCABULARY
from app.services.skill_extract import extract_skills_from_text

_STATUS_RULES = [
    (("career switch", "switching career", "switch career", "career change", "transition into", "pivot"), "Career Switcher"),
    (("working professional", "software engineer at", "currently working", "full-time", "full time", "my job", "at my company", "years of experience in industry"), "Working Professional"),
    (("recent graduate", "just graduated", "fresh graduate", "final year", "final-year", "graduated last", "passed out"), "Recent Graduate"),
    (("student", "studying", "pursuing", "undergrad", "sophomore", "freshman", "in college", "b.tech", "btech", "b.e.", "engineering degree"), "Engineering Student"),
]

_EXPERIENCE_RULES = [
    (("advanced", "senior", "expert", "several years", "many projects", "built multiple", "professionally for"), "Advanced"),
    (("intermediate", "comfortable with", "some experience", "know the basics of programming", "built a few"), "Intermediate"),
    (("beginner", "complete beginner", "just starting", "new to", "no experience", "from scratch", "never coded", "absolute beginner"), "Beginner"),
]

_BRANCH_RULES = [
    (("computer", "software", "information technology", " it ", "cse", "comp sci", "computer science"), "Computer Engineering / IT"),
    (("electronics", "communication", "ece", "vlsi", "embedded"), "Electronics & Communication Engineering"),
    (("electrical", "power systems", "eee"), "Electrical Engineering"),
    (("mechanical", "thermodynamics", "cad", "manufacturing"), "Mechanical Engineering"),
    (("civil", "structural", "construction"), "Civil Engineering"),
    (("chemical", "process engineering"), "Chemical Engineering"),
    (("aerospace", "aeronautical", "avionics"), "Aerospace Engineering"),
    (("biomedical", "bioengineering"), "Biomedical Engineering"),
    (("robotics", "mechatronics"), "Robotics / Mechatronics"),
    (("automobile", "automotive"), "Automobile Engineering"),
]

_LEARN_PATTERN = re.compile(
    r"(?:want to learn|wanna learn|learn|study|studying|master|get into|getting into|become(?:\s+an?)?|"
    r"work as(?:\s+an?)?|interested in|focus on|speciali[sz]e in|dive into|explore|upskill in|transition into)\s+"
    r"([a-z0-9][a-z0-9 +#./&-]{1,40})",
    re.IGNORECASE,
)

_PHRASE_STOP = re.compile(r"\b(and|but|so|because|since|for|to|with|as|the|a|an|then|also|plus|from|in|on|of|my|i|it|that|this|which|while|within|over|next|coming|about)\b", re.IGNORECASE)
_TRAIL_JUNK = re.compile(r"[^a-z0-9+#.]+$", re.IGNORECASE)
_GENERIC = {"stuff", "things", "field", "domain", "area", "career", "job", "role", "coding", "programming", "tech", "technology", "development", "engineering", "more", "new", "some"}


def _first_int(text: str, pattern: str, lo: int, hi: int):
    for m in re.finditer(pattern, text, re.IGNORECASE):
        try:
            val = int(m.group(1))
        except ValueError:
            continue
        if lo <= val <= hi:
            return val
    return None


def _parse_hours(low: str):
    per_day = _first_int(low, r"(\d{1,2})\s*(?:hours?|hrs?)\s*(?:a|per|each|/)\s*day", 1, 12)
    if per_day is not None:
        return min(80, per_day * 7)
    per_week = _first_int(low, r"(\d{1,3})\s*(?:hours?|hrs?)\s*(?:a|per|each|/)\s*week", 1, 80)
    if per_week is not None:
        return per_week
    return _first_int(low, r"(\d{1,3})\s*(?:hours?|hrs?)\b", 1, 80)


def _parse_timeline(low: str):
    years = _first_int(low, r"(\d{1,2})\s*years?\b", 1, 5)
    if years is not None:
        return min(60, years * 12)
    months = _first_int(low, r"(\d{1,2})\s*months?\b", 1, 60)
    if months is not None:
        return months
    weeks = _first_int(low, r"(\d{1,3})\s*weeks?\b", 2, 260)
    if weeks is not None:
        return max(1, round(weeks / 4.3))
    return None


def _match_rule(low: str, rules):
    for needles, value in rules:
        if any(n in low for n in needles):
            return value
    return None


def _clean_phrase(raw: str) -> str:
    raw = raw.strip().lower()
    parts = _PHRASE_STOP.split(raw)
    phrase = parts[0].strip() if parts else raw
    phrase = _TRAIL_JUNK.sub("", phrase).strip()
    words = phrase.split()
    if not words or len(words) > 4:
        return ""
    if all(w in _GENERIC for w in words):
        return ""
    return " ".join(w.capitalize() if w.islower() else w for w in words)


def parse_intake(text: str, exclude_skills=(), exclude_interests=()) -> Dict:
    text = (text or "").strip()
    low = " " + re.sub(r"\s+", " ", text.lower()) + " "

    skills = extract_skills_from_text(text, exclude=exclude_skills)

    excl_int = {e.strip().lower() for e in exclude_interests}
    detected_interests: List[str] = []
    for kw in ENGINEERING_KEYWORDS_VOCABULARY:
        core = re.split(r"[(/]", kw)[0].strip().lower()
        if len(core) < 3:
            continue
        if core in low and kw.lower() not in excl_int and kw not in detected_interests:
            detected_interests.append(kw)

    known_low = {s["name"].lower() for s in skills} | excl_int | {i.lower() for i in detected_interests}
    new_keywords: List[str] = []
    for m in _LEARN_PATTERN.finditer(text):
        phrase = _clean_phrase(m.group(1))
        if not phrase:
            continue
        pl = phrase.lower()
        if pl in known_low or pl in {k.lower() for k in new_keywords}:
            continue
        if any(pl in v for v in known_low) or any(v and v in pl for v in known_low):
            continue
        new_keywords.append(phrase)

    hours = _parse_hours(low)
    timeline = _parse_timeline(low)
    status = _match_rule(low, _STATUS_RULES)
    experience = _match_rule(low, _EXPERIENCE_RULES)
    branch = _match_rule(low, _BRANCH_RULES)

    summary: List[str] = []
    if status:
        summary.append(f"Status set to {status}")
    if branch:
        summary.append(f"Branch set to {branch}")
    if experience:
        summary.append(f"Experience level set to {experience}")
    if hours:
        summary.append(f"Weekly time set to {hours} hrs/week")
    if timeline:
        summary.append(f"Target timeline set to {timeline} months")
    if detected_interests:
        summary.append(f"Added {len(detected_interests)} interest(s)")
    if new_keywords:
        summary.append(f"Added {len(new_keywords)} custom keyword(s): {', '.join(new_keywords)}")
    if skills:
        summary.append(f"Detected {len(skills)} skill(s) you can review")
    if not summary:
        summary.append("Nothing recognised yet — try adding your goal, weekly hours and current skills.")

    return {
        "detected_skills": skills,
        "detected_interests": detected_interests,
        "new_keywords": new_keywords,
        "hours_per_week": hours,
        "experience_level": experience,
        "user_status": status,
        "engineering_branch": branch,
        "target_timeline_months": timeline,
        "summary": summary,
    }
