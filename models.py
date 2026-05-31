from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from database import Base

class User(Base):
    __tablename__="users"
    
    user_id = Column(Integer, primary_key = True, index=True)
    email = Column(String,unique=True, nullable=False) #change  username to email
    password = Column(String, nullable=False)
    username=Column(String, unique=True,nullable=True)
    display_pic=Column(String, unique=True,nullable=True)

class Repositories(Base):
    __tablename__="repositories"

    repo_id = Column(Integer, primary_key=True)
    user_id=Column(Integer, ForeignKey("users.user_id"))
    repo_title=Column(String, nullable=False)
    
    __table_args__=(UniqueConstraint("repo_title","user_id"), )
