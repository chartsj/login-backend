
# Using Git Bash terminal to activate Virtual Environment:
source .venv/Scripts/activate

# Storing required packages and dependencies into requirements.txt
pip freeze > requirements.txt

# Installing all the packages in requirements.txt into virtual environment
pip install -r requirements.txt

# Command to run FastAPI backend service 
uvicorn main:app --reload