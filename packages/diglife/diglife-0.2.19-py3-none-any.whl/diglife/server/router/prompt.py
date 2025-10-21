from fastapi import APIRouter
from diglife.core import MemoryCardManager
from diglife.models import MemoryCardsRequest, MemoryCard, MemoryCards, MemoryCardsGenerate, ChatHistoryOrText, MemoryCard2
import os
from pro_craft.prompt_helper import IntellectType,Intel

router = APIRouter(tags=["prompt"])

intels = Intel(model_name="doubao-1-5-pro-256k-250115")

@router.get("/push_order")
async def push_order(demand:str, prompt_id: str, key: str,action_type = "train"):
    assert key == '1234'
    result = intels.push_train_order(
                            demand = demand,
                            prompt_id = prompt_id,
                            action_type = action_type
                        )
    print(result,'result')
    return {"message":"success",
            "result":result}

@router.get("/get_latest_prompt")
async def get_latest_prompt(prompt_id: str):
    result = intels.get_prompts_from_sql(
                            prompt_id = prompt_id
                        )
    return {"message":"success",
            "result":result}

@router.get("/sync_database")
async def get_latest_prompt():
    # test_database_url
    result = intels.sync_prompt_data_to_database()
    return {"message":"success"}