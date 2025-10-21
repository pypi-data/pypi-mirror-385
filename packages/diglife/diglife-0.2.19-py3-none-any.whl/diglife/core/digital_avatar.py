#
from diglife.utils import extract_json, extract_article, super_log
from llmada.core import BianXieAdapter
from diglife.models import MemoryCard, MemoryCardScore, MemoryCards, BriefResponse
import math
import asyncio
import json

import inspect
from pydantic import BaseModel, Field, ValidationError, field_validator
from datetime import datetime
import re
from pro_craft.prompt_helper import Intel,IntellectType
from pro_craft.prompt_helper_async import AsyncIntel

inters = AsyncIntel(model_name = "doubao-1-5-pro-256k-250115")
table_name="prompts_table"

from .utils import memoryCards2str
from diglife import logger

from typing import Dict, Optional
from pydantic import BaseModel, Field, RootModel
class PersonInfo(BaseModel):
    """
    表示一个人的详细信息。
    """
    relationship: str = Field(..., description="与查询对象的_关系_")
    profession: str = Field(..., description="职业信息")
    birthday: str = Field(..., description="生日信息 (格式可根据实际情况调整)")

class CharactersData(RootModel[Dict[str, PersonInfo]]):
    """
    表示一个包含多个角色信息的字典，键为角色名称，值为 PersonInfo 模型。
    """
    pass # RootModel 不需要定义额外的字段，它直接代理其泛型类型

class ContentVer(BaseModel):
    content: str = Field(..., description="内容")
###

class DigitalAvatar:
    def __init__(self):

        self.base_format_prompt = """
按照一定格式输出, 以便可以通过如下校验

使用以下正则检出
"```json([\s\S]*?)```"
使用以下方式验证
"""
    async def desensitization(self, memory_cards: list[str]) -> list[str]:
        """
        数字分身脱敏 0100
        """
        tasks = []
        for memory_card in memory_cards:
            tasks.append(inters.aintellect_remove_format(
                                input_data=memory_card.get("content"),
                                prompt_id="0100",
                                version = None,
                                inference_save_case=False,
                                OutputFormat = ContentVer,
                                 ))

        results = await asyncio.gather(*tasks, return_exceptions=False)
        for i, memory_card in enumerate(memory_cards):
            memory_card["content"] = results[i].get("content")
        return memory_cards
    
    async def personality_extraction(self, memory_cards: list[dict],action:str,old_character:str) -> str:
        """
        数字分身性格提取 0099
        """
        memoryCards_str, _ = memoryCards2str(memory_cards)

        result = await inters.aintellect_remove_format(
                                input_data="\n操作方案:\n" + action + "\n旧人物性格:\n" + old_character +"\n记忆卡片:\n" +  memoryCards_str,
                                prompt_id="0099",
                                version = None,
                                inference_save_case=False,
                                OutputFormat = ContentVer,
                                 )
        
        result_content = result.get("content")
        return result_content

    
    async def abrief(self, memory_cards: list[dict]) -> dict:
        """
        数字分身介绍 0098
        """
        
        memoryCards_str, _ = memoryCards2str(memory_cards)
        result = await inters.aintellect_remove_format(
                                input_data="聊天历史:\n" + memoryCards_str,
                                prompt_id="0098",
                                version = None,
                                inference_save_case=False,
                                OutputFormat = BriefResponse,
                                 )
        return result

    async def auser_relationship_extraction(self,text: str) -> dict:
        """
        用户关系提取 0097
        # TODO
        """
        result = await inters.aintellect_remove_format(
                        input_data="聊天历史" + text,
                        prompt_id="0097",
                        version = None,
                        inference_save_case=False,
                        OutputFormat = CharactersData,
                        ExtraFormats=[PersonInfo]
                            )
        
        return result


    async def auser_overview(self,action: str,old_overview: str, memory_cards: list[dict],
                             version = None,
                             ) -> str:
        """
        用户概述 0096
        """
        memoryCards_str, _ = memoryCards2str(memory_cards)
        result = await inters.aintellect_remove_format(
                input_data="\n操作方案:\n" + action + "\n旧概述文本:\n" + old_overview +"\n记忆卡片:\n" +  memoryCards_str,
                prompt_id="0096",
                version = None,
                inference_save_case=False,
                OutputFormat = ContentVer,
                    )
        print(result,'result')
        return result.get("content")


