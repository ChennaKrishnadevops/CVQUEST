import sys
import os
from fastapi import FastAPI, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from io import BytesIO

from application.interview import InterviewQuestionMaker
from application.utils import OpenAIConfig

question_maker = InterviewQuestionMaker(config=OpenAIConfig(temperature=0.7))

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/public/', StaticFiles(directory=os.path.abspath("./site/build"), html=True), name="static")

@app.post("/questions/")
async def create_questions(file: UploadFile):
    try:
        print("File received: ", file.filename)
        content = await file.read()
        print("File content length: ", len(content))  # Check file content length
        file_like = BytesIO(content)  # Wrap bytes in a BytesIO object
        answers = question_maker.create_questions(file_like)
        print("Generated questions: ", answers)
        return answers
    except Exception as e:
        print("An error occurred: ", str(e))
        return {"error": str(e)}

static = FastAPI()
static.mount('', StaticFiles(directory=os.path.abspath("./site/build"), html=True), name="static")

little_nginx = FastAPI()
little_nginx.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

little_nginx.mount("/public", static, name="static")
little_nginx.mount("/api", app, name="api")

@little_nginx.get("/")
async def root(req: Request):
    url = req.url._url
    return RedirectResponse(url + "public")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <flag> <file_path>")
    else:
        flag = sys.argv[1]
        file_path = sys.argv[2]
        print(f"Flag: {flag}, File Path: {file_path}")
        try:
            # Your additional processing logic goes here
            # For example, read the file and pass it to the question_maker
            with open(file_path, 'rb') as file:
                content = file.read()
                print("File content length: ", len(content))  # Check file content length
                file_like = BytesIO(content)  # Wrap bytes in a BytesIO object
                answers = question_maker.create_questions(file_like)
                print("Generated questions: ", answers)
        except Exception as e:
            print("An error occurred while processing the file: ", str(e))
