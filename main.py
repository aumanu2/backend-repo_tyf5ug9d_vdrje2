import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import User, Channel, Message, Video, BotMessage

app = FastAPI(title="Nova Social API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Nova Social API is live"}


@app.get("/test")
def test_database():
    """Quick connectivity check for the database"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# ------------- Users -------------
@app.post("/api/users", response_model=dict)
def create_user(user: User):
    try:
        inserted_id = create_document("user", user)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users", response_model=List[dict])
def list_users():
    try:
        items = get_documents("user")
        # convert ObjectId to str if present
        for it in items:
            if "_id" in it:
                it["id"] = str(it.pop("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------- Channels & Messages -------------
@app.post("/api/channels", response_model=dict)
def create_channel(channel: Channel):
    try:
        inserted_id = create_document("channel", channel)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/channels", response_model=List[dict])
def list_channels():
    try:
        items = get_documents("channel")
        for it in items:
            if "_id" in it:
                it["id"] = str(it.pop("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/messages", response_model=dict)
def create_message(message: Message):
    try:
        inserted_id = create_document("message", message)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/messages", response_model=List[dict])
def list_messages(channel_id: Optional[str] = None):
    try:
        filter_dict = {"channel_id": channel_id} if channel_id else {}
        items = get_documents("message", filter_dict=filter_dict, limit=100)
        for it in items:
            if "_id" in it:
                it["id"] = str(it.pop("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------- Videos -------------
@app.post("/api/videos", response_model=dict)
def create_video(video: Video):
    try:
        inserted_id = create_document("video", video)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/videos", response_model=List[dict])
def list_videos(tag: Optional[str] = None):
    try:
        filter_dict = {"tags": {"$in": [tag]}} if tag else {}
        items = get_documents("video", filter_dict=filter_dict, limit=50)
        for it in items:
            if "_id" in it:
                it["id"] = str(it.pop("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------- AI Chatbot (mock) -------------
class BotResponse(BaseModel):
    reply: str


@app.post("/api/bot", response_model=BotResponse)
def chatbot(msg: BotMessage):
    """
    Simple placeholder AI: echoes with a friendly tone.
    Replace with a real LLM call if desired (OpenAI, etc.).
    """
    user = msg.user
    text = msg.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty message")
    # naive keyword flavoring
    if any(k in text.lower() for k in ["video", "clip", "reel"]):
        reply = f"Hey {user}! That sounds like a great video idea. Want me to draft a catchy caption?"
    elif any(k in text.lower() for k in ["channel", "chat", "room"]):
        reply = f"Sure {user}, I can help you set up a new channel or find trending topics."
    else:
        reply = f"Hi {user}, I hear you: '{text}'. How can I help further?"
    return BotResponse(reply=reply)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
