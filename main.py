from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from database import engine, Base, SessionLocal
import models
from models import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError, OperationalError
import logging
from logging.handlers import RotatingFileHandler
import os
os.makedirs("logs", exist_ok=True)
logging.basicConfig(level=logging.INFO, force=True)
logger=logging.getLogger(__name__)


file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=1024 * 1024,
    backupCount=3
)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

logger.info("Server started")

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message":"backend is running"}

@app.get("/hello")
def hello():
    return {"message":"hello world"}

class LoginRequest(BaseModel):
    email:str
    password:str

#user login endpoint
@app.post("/login")
def user_login(data:LoginRequest):
    if data.email=='test@gmail.com' and data.password=='123':
        return {"message":"Login Successful"}
    raise HTTPException(status_code=401, detail="Invalid email or password")


class SignupRequest(BaseModel):
    email:EmailStr
    password:str = Field(min_length=8)
# endpoint for creating acct


def get_db():
    #SessionLocal
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

def email_exists(email: str, db:Session):
    #query the sqlite database check if such a user exist, get a response. then return true or false accordingly
    existing_user=db.query(User).filter(User.username==email).first()
    
    if existing_user:
        return True
    return False


#hash password
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str):
    return pwd_context.hash(password)


@app.post("/register", status_code=status.HTTP_201_CREATED)
def create_acct(data:SignupRequest,  db:Session=Depends(get_db)):
    if email_exists(data.email,db):
        logger.warning(f"Duplicate registration attempt: {data.email}")
        raise HTTPException(status_code=409, detail="Email already registered")
    
    

    hashed_pw=hash_password(data.password)

    new_user = User(username = data.email, password = hashed_pw)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"New account created: {data.email}")
    except IntegrityError:
        db.rollback()
        logger.warning(f"Duplicate registration attempt: {data.email}")
        raise HTTPException(
            status_code=409,
            detail="Email already registered no way"
        )
    except OperationalError:
        db.rollback()
        logger.exception("Database error during account creation")
        raise HTTPException(
            status_code=500,
            detail="Database operational error"
        )


    except Exception as e:
        db.rollback()
        logger.exception(f"Error occured during account creation: {e}")
        raise HTTPException(
            status_code=500,
            detail = "Internal server error"
        )
        

    return {"message":"Successfully created an account"}
    

