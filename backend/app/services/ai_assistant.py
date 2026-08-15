"""
AI Assistant service.

Two responsibilities:
  1. chat_reply() - conversational front door. Extracts profile info from a
     free-text message (via profiling_engine) and returns a natural-language
     reply, optionally asking a follow-up question if the profile is
     incomplete (no goal / no skill level yet).
  2. answer_question() - free-form Q&A about the learner's recommendations
     or path ("why this course?", "how long will this take?").

If OPENAI_API_KEY is set (see core/config.py), both functions call the
OpenAI API for richer responses. Otherwise they fall back to templated
responses so the prototype runs fully offline out of the box.

TODO:
- Add conversation memory beyond the single-turn extraction (pass recent
  CHAT_HISTORY into the LLM prompt for multi-turn context).
- Add guardrails/system prompt hardening before this touches real user data.
"""
from typing import Dict, List
from app.core.config import settings
from app.models.schemas import LearnerProfile, RecommendationItem

_client = None
if settings.OPENAI_API_KEY:
    from openai import OpenAI
    _client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _llm_available() -> bool:
    return _client is not None


def chat_reply(profile: LearnerProfile, message: str, extracted: Dict) -> str:
    if _llm_available():
        system_prompt = (
            "You are a friendly learning path advisor. Keep replies short (2-4 "
            "sentences), acknowledge what the learner said, and if their goal "
            "or skill level is still unknown, ask one clarifying question."
        )
        user_prompt = (
            f"Learner message: {message}\n"
            f"Current known profile: goal={profile.goal}, "
            f"skill_level={profile.skill_level}, interests={profile.interests}\n"
            f"Just extracted from this message: {extracted}"
        )
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content

    # Offline fallback
    parts = []
    if extracted.get("goal"):
        parts.append(f"Got it — targeting the goal \"{extracted['goal']}\".")
    if extracted.get("interests"):
        parts.append(f"Noted your interest in {', '.join(extracted['interests'])}.")
    if extracted.get("skill_level"):
        parts.append(f"I'll treat you as {extracted['skill_level']} level.")

    if not parts:
        parts.append(
            "Tell me a bit more — what's your learning goal (e.g. \"become a "
            "data scientist\"), and how would you rate your current experience?"
        )
    elif not profile.goal and not extracted.get("goal"):
        parts.append("What's the career or skill goal you're working toward?")
    else:
        parts.append("I'll refresh your recommendations based on this.")

    return " ".join(parts)


def explain_recommendation(course_title: str, reason: str) -> str:
    return f"\"{course_title}\" was recommended because it {reason}."


def answer_question(profile: LearnerProfile, question: str, recommendations: List[RecommendationItem]) -> str:
    if _llm_available():
        context = "\n".join(f"- {r.title}: {r.reason}" for r in recommendations)
        system_prompt = (
            "You are a learning path assistant. Answer the learner's question "
            "using the profile and recommendation context provided. Be concise."
        )
        user_prompt = (
            f"Profile: goal={profile.goal}, level={profile.skill_level}\n"
            f"Current recommendations:\n{context}\n\nQuestion: {question}"
        )
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content

    # Offline fallback: naive keyword-based Q&A
    q = question.lower()
    if "why" in q and recommendations:
        top = recommendations[0]
        return explain_recommendation(top.title, top.reason)
    if "how long" in q or "hours" in q:
        total = sum(r.estimated_hours for r in recommendations)
        return f"Your current recommended courses total about {total} hours."
    if "next" in q:
        if recommendations:
            return f"Your next recommended step is \"{recommendations[0].title}\"."
        return "Complete your profile so I can suggest a next step."
    return (
        "I can explain why a course was recommended, estimate time commitment, "
        "or suggest your next step — ask me about any of those."
    )
