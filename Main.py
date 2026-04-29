from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup (Replace with your actual Postgres URL from Neon/Supabase)
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Postgres Table Model
class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True) # type: ignore
    author = Column(String(100))
    title = Column(String(255))
    cat = Column(String(50))
    content = Column(Text)
    image = Column(Text) # Storing Base64 string for now
    likes = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS so your HTML file can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://journeythroughmedia.co.za/"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for receiving data
class ArticleCreate(BaseModel):
    author: str
    title: str
    cat: str
    content: str
    image: str = ""
    
@app.get("/")
def read_root():
    return {"message": "Journey Through Media API is Live!"}    

@app.get("/posts")
def get_posts():
    db = SessionLocal()
    try:
        return db.query(Article).order_by(Article.id.desc()).all()
    finally:
        db.close()

@app.post("/posts")
def create_post(article: ArticleCreate):
    db = SessionLocal()
    new_post = Article(**article.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    db.close()
    return new_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    db = SessionLocal()
    post = db.query(Article).filter(Article.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    db.close()
    return {"message": "Deleted"}