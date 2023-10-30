from fastapi import FastAPI
from pydantic import BaseModel
from api.model import Model

app = FastAPI()
answer_generator = Model("ramashisx/t5_base_generative_qa", "ramashisx/t5_base_generative_qa")
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
