from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers=["*"]
)

class QueryRequest(BaseModel):
    query : str

@app.get("/")
def read_root():
    return{"message": "Backend Is working"}

@app.post("/query")
def answer_query(request : QueryRequest):
    user_question = request.query
    print("Received question:", user_question)

    return {
        "answer": f"This is a dummy response to: '{user_question}'"
    }