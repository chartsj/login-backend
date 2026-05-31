
# Activate Virtual Environment (Git Bash):
source .venv/Scripts/activate

# Install Dependencies
Install all required packages from requirements.txt
pip install -r requirements.txt

To generate/update requirements.txt

pip freeze > requirements.txt




# Run FastAPI Server 
uvicorn main:app --reload


# Packages
pip install passlib 
pip install bcrypt==4.0.1


# Steps to Run this Backend Application
## Step 1: 
Navigate into the Fastapi Login Backend Folder
## Step 2: 
### Activate the virtual environment:
source .venv/Scripts/activate
## Step 3: 
### Start the FastAPI server
uvicorn main:app --reload
## Step 4: 
Use postman to query the api endpoints
## Step 5: 
Use DB Browser to view data in sqlite database (aka login.db)
## Step 6: 
Ensure that a .env file exists in the project root and contains the SECRET_KEY used for JWT encoding and decoding.

Example:

SECRET_KEY=your-secret-key

## Step 7: 

When querying protected endpoints such as:

- /repositories
- /profile

through Postman, attach the JWT token as a cookie named:

access_token

Example cookie:

access_token=your-jwt-token