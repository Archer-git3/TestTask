from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "postgresql://postgres:111@5432/TestTask"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Створення моделі для постів
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True

# Створення CRUD роутерів
@app.post("/posts/", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(SessionLocal)):
    db_post = Post(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int, db: Session = Depends(SessionLocal)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostCreate, db: Session = Depends(SessionLocal)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_post.title = post.title
    db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(SessionLocal)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"detail": "Post deleted"}
