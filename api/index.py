import os
import datetime
import json
import modulefinder
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Set up fallback if not provided
if not DATABASE_URL:
    print("DATABASE_URL not set — using SQLite fallback")
    DATABASE_URL = "sqlite:///./test.db"

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Render's DB string often starts with postgres://, SQLAlchemy requires postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =========================
# DATABASE MODEL
# =========================

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    author = Column(String(100))
    title = Column(String(255))
    cat = Column(String(50))
    content = Column(Text)
    image = Column(Text)
    likes = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.datetime.utcnow)

# Create tables safely
Base.metadata.create_all(bind=engine)

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://coruscating-speculoos-f78005.netlify.app", # <-- REPLACE with your actual Netlify URL
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Pydantic Schema
# =========================

class ArticleCreate(BaseModel):
    author: str
    title: str
    cat: str
    content: str
    image: str = ""

# =========================
# ROUTES
# =========================

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Could not find the index.html file in the project root directory.</h1>"


@app.get("/posts")
def get_posts():
    db = SessionLocal()
    try:
        posts = db.query(Article).order_by(Article.id.desc()).all()
        return posts
    finally:
        db.close()


@app.post("/posts")
def create_post(article: ArticleCreate):
    db = SessionLocal()
    try:
        new_post = Article(**article.model_dump())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    finally:
        db.close()


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    db = SessionLocal()
    try:
        post = db.query(Article).filter(Article.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        db.delete(post)
        db.commit()
        return {"message": "Deleted"}
    finally:
        db.close()