"""
Conversational interface endpoint.

Endpoints:
  POST /api/chat  - send a free-text message, get back an assistant reply
                     plus any profile fields it extracted (so the frontend
                     can show "I picked up: goal=data scientist" chips).

TODO:
- Stream the reply (SSE / websockets) instead of a single blocking response
  once the LLM path is the default.
- Persist chat history per learner beyond the in-memory CHAT_HISTORY dict.
"""
from fastapi import APIRouter
from app.models.schemas import ChatMessageRequest, ChatMessageResponse
from app.services.profiling_engine import extract_from_message
from app.services.ai_assistant import chat_reply
from app.db import get_or_create_profile, PROFILES, CHAT_HISTORY

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatMessageResponse)
def send_message(req: ChatMessageRequest):
    profile = get_or_create_profile(req.learner_id)

    extracted = extract_from_message(req.message)
    for field, value in extracted.items():
        if field == "interests":
            merged = set(profile.interests) | set(value)
            profile.interests = list(merged)
        else:
            setattr(profile, field, value)
    PROFILES[req.learner_id] = profile

    reply = chat_reply(profile, req.message, extracted)

    CHAT_HISTORY.setdefault(req.learner_id, []).append({"role": "user", "content": req.message})
    CHAT_HISTORY[req.learner_id].append({"role": "assistant", "content": reply})

    return ChatMessageResponse(reply=reply, extracted_profile_updates=extracted)
