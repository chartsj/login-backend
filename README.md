
# Using Git Bash terminal to activate Virtual Environment:
source .venv/Scripts/activate

# Storing required packages and dependencies into requirements.txt
pip freeze > requirements.txt

# Installing all the packages in requirements.txt into virtual environment
pip install -r requirements.txt

# Command to run FastAPI backend service 
uvicorn main:app --reload


# pip installations and their version
pip install passlib 
pip install bcrypt==4.0.1


# steps to run this backend application
step 1: Go into the Fastapi Login Backend Folder
step 2: source .venv/Scripts/activate
step 3: uvicorn main:app --reload
step 4: Use postman to query the api endpoints
step 5: Use DB Browser to view data in sqlite database (aka login.db)