from fastapi import FastAPI, HTTPException, status, Depends, Response, Cookie
from pydantic import BaseModel, EmailStr, Field
from database import engine, Base, SessionLocal
import models
from models import User, Repositories
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError, OperationalError
import logging
from logging.handlers import RotatingFileHandler
import os
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime,timedelta, timezone
import secrets
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

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
#hash password
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str):
    return pwd_context.hash(password)

def get_db():
    #SessionLocal
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_pw,hashed_pw):
    return pwd_context.verify(plain_pw,hashed_pw)

@app.get("/")
def home():
    return {"message":"backend is running"}

@app.get("/hello")
def hello():
    return {"message":"hello world"}




def get_current_user(access_token:str| None = Cookie(default=None)):
    # get the jwt as argument
    if access_token is None:
        raise HTTPException(status_code=401,detail="Not authenticated")
    
    try:
        payload=jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id:str|None=payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401,detail="Invalid token")
        logger.info(f"user_id is: {user_id}")
        return user_id
    except InvalidTokenError:
        raise HTTPException(status_code=401,detail="Invalid token")

class RepositoryCreate(BaseModel):
    repo_title: str

@app.post("/repositories")
def create_repo( request_body: RepositoryCreate, user_id=Depends(get_current_user), db: Session = Depends(get_db)):

    user=db.query(User).filter(User.user_id==user_id).first()
    
    new_repo=Repositories(repo_title=request_body.repo_title,user_id=user.user_id)
    try:
        db.add(new_repo)
        db.commit()
        db.refresh(new_repo)
        logger.info(f"Repository '{request_body.repo_title}' created for user_id {user_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create repository")

    return {"message":"Repository created"}


@app.get("/profile")
def get_profile(current_user:int=Depends(get_current_user), db: Session=Depends(get_db)):

    user_details=db.query(User).filter(User.user_id==current_user).first()
    if user_details is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_repos=db.query(Repositories).filter(Repositories.user_id==current_user).all()
    repo_list=[]
    for repo in user_repos:
        repo_list.append({"repo_id":repo.repo_id,"repo_title":repo.repo_title})
    return {"username":user_details.username,"display_pic":user_details.display_pic,"repositories":repo_list}


class LoginRequest(BaseModel):
    email:str
    password:str


def create_access_token(data):
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    payload.update({
        "exp":expire
    })
    
    token = jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    
    return token


@app.post("/login")
def user_login(data:LoginRequest, response:Response, db: Session = Depends(get_db)):
    
    #query the sqlite if this password and email address match any existing user
    user = db.query(User).filter(User.email==data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

    password_valid=verify_password(data.password, user.password)
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    

    access_token = create_access_token({"sub":str(user.user_id)})
    
    response.set_cookie(key="access_token",value=access_token, httponly=True, secure=True, samesite="lax" )
    return {"message":"Login Successful"}

class SignupRequest(BaseModel):
    email:EmailStr
    password:str = Field(min_length=8)
# endpoint for creating acct



    

def email_exists(email: str, db:Session):
    #query the sqlite database check if such a user exist, get a response. then return true or false accordingly
    existing_user=db.query(User).filter(User.email==email).first()
    
    if existing_user:
        return True
    return False





@app.post("/register", status_code=status.HTTP_201_CREATED)
def create_acct(data:SignupRequest,  db:Session=Depends(get_db)):
    if email_exists(data.email,db):
        logger.warning(f"Duplicate registration attempt: {data.email}")
        raise HTTPException(status_code=409, detail="Email already registered")
    
    

    hashed_pw=hash_password(data.password)

    new_user = User(email = data.email, password = hashed_pw)
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
    

