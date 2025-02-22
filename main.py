# from fastapi import FastAPI
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import asyncio

# # Define the correct DATABASE_URL
# DATABASE_URL = "postgresql+asyncpg://apple:yourpassword@localhost:5432/yourdatabase"

# # Create the async SQLAlchemy engine
# engine = create_async_engine(DATABASE_URL, echo=True)

# # Create a session factory
# AsyncSessionLocal = sessionmaker(
#     bind=engine, class_=AsyncSession, expire_on_commit=False
# )

# # Base class for models
# Base = declarative_base()

# # FastAPI app instance
# app = FastAPI()

# # Dependency to get database session
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session

# # Root endpoint
# @app.get("/")
# async def root():
#     return {"message": "FastAPI with PostgreSQL is running!"}

# # Function to create tables
# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# # Run DB initialization on startup
# @app.on_event("startup")
# async def startup():
#     await init_db()

# # Run the application
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.future import select
from pydantic import BaseModel
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi.middleware.cors import CORSMiddleware


DATABASE_URL = "postgresql+asyncpg://apple:yourpassword@localhost:5432/yourdatabase"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📌 Database Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# 📌 Define the User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    mobile_number = Column(String, index=True)

# 📌 Create Tables on Startup
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await init_db()

# 📌 Pydantic Model for Validation
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    mobile_number: str

# 📌 Fetch All Users (GET)
@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

# 📌 Add a New User (POST)
@app.post("/users")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = User(first_name=user.first_name, last_name=user.last_name, mobile_number=user.mobile_number)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

