#
import asyncio
from pro_craft.prompt_helper_async import AsyncIntel
from diglife.models import PersonInfo, CharactersData, ContentVer, BriefResponse
from diglife.utils import memoryCards2str
from diglife import inference_save_case


###


class DigitalAvatar:
    def __init__(self):
        self.inters = AsyncIntel(model_name = "doubao-1-5-pro-256k-250115")


    async def desensitization(self, memory_cards: list[str]) -> list[str]:
        """
        数字分身脱敏 0100
        """
        tasks = []
        for memory_card in memory_cards:
            tasks.append(self.inters.aintellect_remove_format(
                                input_data=memory_card.get("content"),
                                prompt_id="0100",
                                version = None,
                                inference_save_case=inference_save_case,
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

        result = await self.inters.aintellect_remove_format(
                                input_data="\n操作方案:\n" + action + "\n旧人物性格:\n" + old_character +"\n记忆卡片:\n" +  memoryCards_str,
                                prompt_id="0099",
                                version = None,
                                inference_save_case=inference_save_case,
                                OutputFormat = ContentVer,
                                 )
        
        result_content = result.get("content")
        return result_content

    
    async def abrief(self, memory_cards: list[dict]) -> dict:
        """
        数字分身介绍 0098
        """
        
        memoryCards_str, _ = memoryCards2str(memory_cards)
        result = await self.inters.aintellect_remove_format(
                                input_data="聊天历史:\n" + memoryCards_str,
                                prompt_id="0098",
                                version = None,
                                inference_save_case=inference_save_case,
                                OutputFormat = BriefResponse,
                                 )
        return result

    async def auser_relationship_extraction(self,text: str) -> dict:
        """
        用户关系提取 0097
        # TODO
        """
        result = await self.inters.aintellect_remove_format(
                        input_data="聊天历史" + text,
                        prompt_id="0097",
                        version = None,
                        inference_save_case=inference_save_case,
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
        result = await self.inters.aintellect_remove_format(
                input_data="\n操作方案:\n" + action + "\n旧概述文本:\n" + old_overview +"\n记忆卡片:\n" +  memoryCards_str,
                prompt_id="0096",
                version = None,
                inference_save_case=inference_save_case,
                OutputFormat = ContentVer,
                    )
        return result.get("content")


