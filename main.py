from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from database import engine, Base, SessionLocal
import models
from models import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext



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
    email:str
    password:str
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



@app.post("/register", status_code=status.HTTP_201_CREATED)
def create_acct(data:SignupRequest,  db:Session=Depends(get_db)):
    if email_exists(data.email,db):
        raise HTTPException(status_code=409, detail="Email already registered")
    
    #hash password
    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto"
    )

    def hash_password(password: str):
        return pwd_context.hash(password)

    hashed_pw=hash_password(data.password)

    new_user = User(username = data.email, password = hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message":"Successfully created an account"}
    
    