from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database configuration (using environment variables in production)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/documind"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="DocuMind AI API")

@app.get("/")
def read_root():
    return {"message": "Welcome to DocuMind AI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
