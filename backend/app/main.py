from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import Base, engine, get_db
from app.schemas import ChatRequest, ChatResponse

from app.inventory_service import search_inventory
from prompt.prompt_service import chat_with_inventory

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Merchandise Chatbot")

db_dependency = Annotated[Session, Depends(get_db)]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/greeting")
def greeting():
    return {
        "message": (
                "Hi! I'm the Inventory Assistance. I can help you with checking the inventory " 
                "and locating the store. " 
                "Which product you are looking for?"
                   )
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: db_dependency):

    def inventory_tool(**kwargs):
        return search_inventory(db=db, **kwargs)

    reply = chat_with_inventory(
        session_id=req.session_id,
        messages=req.messages,
        search_inventory_func=inventory_tool,
    )

    return ChatResponse(reply=reply)