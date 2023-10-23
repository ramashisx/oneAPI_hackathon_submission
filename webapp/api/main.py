from fastapi import FastAPI
from pydantic import BaseModel
from api.model import Model

app = FastAPI()
answer_generator = Model("./model/oneapi-hack-model/", "./model/oneapi-hack-model/")
answer_generator.prepare_model()

class Input(BaseModel):
    context: str
    question: str

@app.post("/")
async def get_answer(item: Input):
    item_dict = item.dict()
    answer = answer_generator(item_dict["context"], item_dict["question"])
    return {
        "answer": answer
    }
