from fastapi import APIRouter
from pro_craft.prompt_helper import IntellectType,Intel
from pro_craft.utils import create_session
import os

router = APIRouter(tags=["prompt"])
intels = Intel(model_name="doubao-1-5-pro-256k-250115")

@router.get("/push_order")
async def push_order(demand:str, prompt_id: str, key: str,action_type = "train"):
    assert key == '1234'
    result = intels.push_action_order(
                            demand = demand,
                            prompt_id = prompt_id,
                            action_type = action_type
                        )
    print(result,'result')
    return {"message":"success",
            "result":result}

@router.get("/get_latest_prompt")
async def get_latest_prompt(prompt_id: str):
    
    with create_session(intels.engine) as session:
        result = intels.get_prompts_from_sql(
                                prompt_id = prompt_id,
                                session = session
                            )
    return {"message":"success",
            "result":result}

@router.get("/sync_database")
async def get_latest_prompt():
    # test_database_url
    result = intels.sync_prompt_data_to_database(os.getenv("test_database_url"))
    return {"message":"success"}