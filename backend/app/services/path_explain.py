"""
Per-phase "why these courses" explanation for a learning path + an overall
overview. Uses the LLM if an API key is set, otherwise a grounded template built
from the planner's real `why_now` / driver data and the career taxonomy.
"""
from __future__ import annotations

from typing import List, Optional

from app.core.config import settings
from app.data.taxonomy_data import CAREERS_DATABASE
from app.models.schemas import (
    LearningPathResponse, PathExplanationResponse, PhaseExplanation,
)

_FACTOR_SHORT = {
    "goal_fit": "goal match", "skill_gain": "skill-gap coverage", "branch_fit": "branch fit",
    "level_fit": "level fit", "quality": "course rating", "prereq_ready": "prerequisite readiness",
    "effort_fit": "time fit", "format_pref": "format match",
}


def _career(career_id: str):
    return next((c for c in CAREERS_DATABASE if c["career_id"] == career_id), None)


def _phase_template(path: LearningPathResponse, m) -> str:
    skills = ", ".join(m.target_skills[:4]) or "core skills for this phase"
    lines = [f"**{m.title}** focuses on {skills}."]
    if m.description:
        lines.append(m.description)
    lead = m.resources[0] if m.resources else None
    if lead and lead.why_now:
        lines.append(f"You start with *{lead.title}* — {lead.why_now.rstrip('.')}.")
    # driver rationale for the first couple of courses
    for r in m.resources[:2]:
        fc = r.factor_contributions or {}
        top = sorted(fc.items(), key=lambda kv: -kv[1])[:2]
        parts = [f"{_FACTOR_SHORT.get(f, f)} {round(v * 100)}%" for f, v in top if v >= 0.08]
        if parts:
            lines.append(f"*{r.title}* was ranked mainly on {', '.join(parts)}.")
    unlocks: List[str] = []
    for r in m.resources:
        unlocks.extend(r.unlocks or [])
    if unlocks:
        lines.append(f"Finishing this phase prepares you for: {', '.join(list(dict.fromkeys(unlocks))[:3])}.")
    return " ".join(lines)


def _overview_template(path: LearningPathResponse) -> str:
    career = _career(path.career_id)
    tracks = ", ".join(path.track_names) if path.track_names else "the required skill tracks"
    txt = (
        f"This roadmap gets you to **{path.career_title}** in about "
        f"{path.estimated_weeks} weeks at {path.hours_per_week} hrs/week. "
        f"It is built from {len(path.track_names) or 'several'} skill tracks ({tracks}) and "
        f"ordered by prerequisite depth: each phase only assumes what the earlier phases "
        f"already taught, so you are never dropped into a course you are not ready for."
    )
    if career and career.get("key_responsibilities"):
        txt += (" The sequence is anchored to what the role actually does day to day: "
                + "; ".join(career["key_responsibilities"][:2]) + ".")
    return txt


def _try_llm_phase(career_title: str, phase_title: str, course_titles: List[str],
                   why_now: Optional[str]) -> Optional[str]:
    if not (settings.GEMINI_API_KEY or settings.OPENAI_API_KEY):
        return None
    context = (
        f"Career: {career_title}\nPhase: {phase_title}\n"
        f"Courses in order: {', '.join(course_titles)}\n"
        f"Planner rationale for the first course: {why_now or 'n/a'}"
    )
    prompt = (
        "In 2-3 sentences, explain why this phase's courses are good for the learner and "
        "how they help toward the career. Use ONLY the context. Do not invent course names."
    )
    try:
        if settings.GEMINI_API_KEY:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            for name in ("gemini-flash-latest", "gemini-2.5-flash"):
                try:
                    model = genai.GenerativeModel(name)
                    resp = model.generate_content(f"{context}\n\n{prompt}")
                    if resp and getattr(resp, "text", None):
                        return resp.text.strip()
                except Exception:
                    continue
        if settings.OPENAI_API_KEY:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"{context}\n\n{prompt}"}],
                temperature=0.4,
            )
            if res.choices and res.choices[0].message.content:
                return res.choices[0].message.content.strip()
    except Exception:
        return None
    return None


def build_path_explanation(path: LearningPathResponse) -> PathExplanationResponse:
    phases: List[PhaseExplanation] = []
    for m in path.milestones:
        text = _try_llm_phase(
            path.career_title, m.title,
            [r.title for r in m.resources[:5]],
            m.resources[0].why_now if m.resources else None,
        ) or _phase_template(path, m)
        phases.append(PhaseExplanation(milestone_key=m.id, title=m.title, explanation=text))

    return PathExplanationResponse(overview=_overview_template(path), phases=phases)
