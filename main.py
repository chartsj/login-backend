from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

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

def email_exists(email):
    list_existing_email=['test@gmail.com','123@outlook.com']
    if email in list_existing_email:
        return True
    return False

@app.post("/register", status_code=status.HTTP_201_CREATED)
def create_acct(data:SignupRequest):
    if email_exists(data.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    if data.email and data.password:
        return {"message":"Successfully created an account"}
    
    