from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.data.quiz_bank import GENERIC, SKILL_QUIZ_BANK
from app.db import repository
_GEMINI_MODELS = ("gemini-flash-latest", "gemini-2.5-flash")
_NORM = re.compile(r"[^a-z0-9]+")
def _norm(s: str) -> str:
    return _NORM.sub(" ", (s or "").lower()).strip()
_BANK = {_norm(k): v for k, v in SKILL_QUIZ_BANK.items()}
def _course_row(course_id: str):
    from app.ml.engine import engine
    engine._require()
    pos = engine.catalog.df.index[engine.catalog.df["course_id"] == course_id].tolist()
    if not pos:
        return None
    return engine.catalog.df.iloc[int(pos[0])]
def _bank_key_for(track: str, title: str) -> Optional[str]:
    nt = _norm(track)
    if nt in _BANK:
        return nt
    tw = set(nt.split())
    best, best_score = None, 0.0
    for key in _BANK:
        kw = set(key.split())
        if not kw:
            continue
        score = len(tw & kw) / len(kw)
        if score > best_score:
            best, best_score = key, score
    if best_score >= 0.5:
        return best
    titlew = set(_norm(title).split())
    for key in _BANK:
        kw = set(key.split())
        if kw and len(kw & titlew) / len(kw) >= 0.6:
            return key
    return None
def _with_ids(questions: List[dict]) -> List[dict]:
    return [{"id": f"q{i}", **q} for i, q in enumerate(questions[:4], 1)]
def _clean_json(raw: str) -> Optional[dict]:
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
def _validate(questions: Any) -> List[dict]:
    out: List[dict] = []
    if not isinstance(questions, list):
        return out
    for q in questions[:4]:
        if not isinstance(q, dict):
            continue
        text = str(q.get("question_text") or q.get("question") or "").strip()
        opts = q.get("options")
        idx = q.get("correct_option_index", q.get("answer_index"))
        if not text or not isinstance(opts, list) or len(opts) < 3:
            continue
        try:
            idx = int(idx)
        except (TypeError, ValueError):
            continue
        opts = [str(o) for o in opts[:4]]
        if not 0 <= idx < len(opts):
            continue
        out.append({"question_text": text, "options": opts,
                    "correct_option_index": idx, "explanation": str(q.get("explanation", "")).strip()})
    return out
def _llm_questions(title: str, skills: str, description: str, difficulty: str) -> List[dict]:
    if not settings.COURSE_QUIZ_LLM or not (settings.GEMINI_API_KEY or settings.OPENAI_API_KEY):
        return []
    prompt = (
        f"Write a diagnostic quiz for the course \"{title}\" ({difficulty} level). "
        f"Skills: {skills}. Summary: {description}\n"
        "EXACTLY 4 multiple-choice questions testing real understanding. Each: 4 options, "
        "one correct, a one-sentence explanation. Return ONLY JSON: "
        '{"questions":[{"question_text":"...","options":["a","b","c","d"],'
        '"correct_option_index":0,"explanation":"..."}]}'
    )
    try:
        if settings.GEMINI_API_KEY:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            for name in _GEMINI_MODELS:
                try:
                    resp = genai.GenerativeModel(name).generate_content(prompt)
                    parsed = _clean_json(getattr(resp, "text", "") or "")
                    qs = _validate(parsed.get("questions")) if parsed else []
                    if len(qs) >= 3:
                        return qs
                except Exception:
                    continue
        if settings.OPENAI_API_KEY:
            from openai import OpenAI
            res = OpenAI(api_key=settings.OPENAI_API_KEY).chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5, response_format={"type": "json_object"},
            )
            parsed = _clean_json(res.choices[0].message.content or "")
            qs = _validate(parsed.get("questions")) if parsed else []
            if len(qs) >= 3:
                return qs
    except Exception:
        pass
    return []
def get_course_quiz(course_id: str) -> Optional[Dict[str, Any]]:
    cached = repository.get_course_quiz(course_id)
    if cached and cached.get("questions"):
        return cached
    row = _course_row(course_id)
    if row is None:
        return None
    title = str(row["course_title"])
    track = str(row["track"])
    skills = str(row["skills_taught"]).replace(";", ", ")
    key = _bank_key_for(track, title)
    source = "bank"
    if key:
        questions = _with_ids(_BANK[key])
    else:
        questions = _llm_questions(title, skills, str(row["description"])[:600], str(row["difficulty_level"]))
        source = "llm" if questions else "generic"
        if not questions:
            questions = _with_ids(GENERIC)
    quiz = {
        "id": f"cq_{course_id}", "assessment_id": f"cq_{course_id}", "course_id": course_id,
        "skill_id": f"cq_{course_id}", "skill_name": title,
        "title": f"{title.split(':')[0].strip()} - Concept Check",
        "description": f"{len(questions)} questions on this course's material.",
        "questions": questions, "source": source, "matched_skill": key or track,
    }
    repository.save_course_quiz(course_id, quiz)
    return quiz