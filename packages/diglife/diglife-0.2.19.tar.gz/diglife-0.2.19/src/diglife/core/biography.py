
from diglife.utils import extract_json, extract_article, super_log
from llmada.core import BianXieAdapter, ArkAdapter
from diglife.models import MemoryCard, MemoryCardScore, MemoryCards
import math
import asyncio
import json

import inspect
from pydantic import BaseModel, Field, ValidationError, field_validator
from datetime import datetime
import re

from pro_craft.prompt_helper import Intel,IntellectType
from pro_craft.prompt_helper_async import AsyncIntel


from diglife import logger
from .utils import memoryCards2str

def fix_broken_json_string(broken_json_str):
    # 移除 BOM
    broken_json_str = broken_json_str.lstrip('\ufeff')
    # 移除大部分非法 ASCII 控制字符
    broken_json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', broken_json_str)

    # 尝试找到 "content": " 和它对应的结束 "
    # 这是一个挑战，因为中间有未转义的换行。
    # 我们会寻找 "content": "，然后捕获从那以后直到最后一个 " 的所有内容，并替换其中的裸换行。

    # 注意：这个正则假设 "content" 的值是最后一个键值对，并且直到字符串末尾的 " 才结束
    # 并且假设其他字段都是合法的单行字符串
    fixed_json_str = re.sub(
        r'("content":\s*")(.+?)"\s*}',  # 匹配 "content": "，然后捕获所有内容直到最后一个 " }
        lambda m: m.group(1) + m.group(2).replace('\n', '\\n').replace('\r', '\\r') + '"\n}',
        broken_json_str,
        flags=re.DOTALL # 允许 . 匹配换行
    )

    # 修正可能的最后一行丢失的 }
    if not fixed_json_str.strip().endswith('}'):
        fixed_json_str += '\n}' # 补上结束的 }

    return fixed_json_str

def deal_json_result(result_str:str)->dict:
    json_str = extract_json(result_str)
    json_str = fix_broken_json_string(json_str)
    return json.loads(json_str)

class Extract_Person(BaseModel):
    content: list[str] = Field(..., description="提取人名")

class Extract_Place(BaseModel):
    content: list[str] = Field(..., description="提取地名")

class Biography_Free(BaseModel):
    title: str = Field(..., description="标题")
    description: str = Field(..., description="传记的简介")
    content: str = Field(..., description="传记正文")

class ContentVer(BaseModel):
    content: str = Field(..., description="内容")

inters = AsyncIntel(model_name = "doubao-1-5-pro-256k-250115")

class BiographyGenerate:
    def __init__(self,model_name: str = "gemini-2.5-flash-preview-05-20-nothinking",
                      api_key: str = None):
        # self.llm = ArkAdapter(model_name=model_name,
        #                       api_key= api_key,)

        self.llm = BianXieAdapter(model_name=model_name,
                              api_key= api_key,)
        self.base_format_prompt = """
按照一定格式输出, 以便可以通过如下校验

使用以下正则检出
"```json([\s\S]*?)```"
使用以下方式验证
"""

        # output_format = self.base_format_prompt + inspect.getsource(ContentVer)
    async def extract_person_name(self, bio_chunk: str):
        """0087 提取人名"""

        result = await inters.aintellect_remove_format(
            input_data = bio_chunk,
            prompt_id = "0087",
            version = None,
            inference_save_case=False,
            OutputFormat = Extract_Person,
        )


        return result

    async def extract_person_place(self, bio_chunk: str):
        """0086 提取地名"""

        result = await inters.aintellect_remove_format(
            input_data = bio_chunk,
            prompt_id = "0086",
            version = None,
            inference_save_case=False,
            OutputFormat = Extract_Place,
        )


        return result
    
    async def aoutline_generate(self, material: str) -> str:
        """
        0084 大纲生成
        """
        output_format = """
输出格式
```json
{
    "预章" : [
        {
            "chapter_number": "-",
            "title": "山村童年的自由奔跑",
            "topic": "第三人称。本章将追溯张三在1980年代末至1990年代初，辽宁葫芦岛小村庄的童年岁月。描绘乡村的淳朴生活、日出而作日落而息的节奏，以及他作为“山里的野孩子”与自然亲密接触的自由时光。这是张三生命中“第一起”的萌芽，奠定了他与自然连接的性格底色和对规律生活的最初认知。"
        },
    ]
    "第一部 童年与自然启蒙": [
        {
            "chapter_number": "第一章",
            "title": "山村童年的自由奔跑",
            "topic": "第三人称。本章将追溯张三在1980年代末至1990年代初，辽宁葫芦岛小村庄的童年岁月。描绘乡村的淳朴生活、日出而作日落而息的节奏，以及他作为“山里的野孩子”与自然亲密接触的自由时光。这是张三生命中“第一起”的萌芽，奠定了他与自然连接的性格底色和对规律生活的最初认知。"
        },
        {
            "chapter_number": "第二章",
            "title": "漫天繁星的宇宙初识",
            "topic": "第一人称。深入探究张三童年时期对夜晚星空的深刻记忆和感受。描述“漫天繁星”如何在他幼小的心灵中种下对宇宙和未知世界的好奇种子，成为他最早的“觉醒点”，预示其未来对知识的无尽求索。这是他“第一起”中重要的情感与思想铺垫。"
        }
    ],
    "第二部 知识与理性的求索": [
        {
            "chapter_number": "第三章",
            "title": "县城高中：物理兴趣的萌芽",
            "topic": "第三人称。本章叙述张三青少年时期在县城高中的学习经历。尽管学习资源相对有限，他却对天文物理和理论物理产生了浓厚兴趣，这显示出超越应试教育的深层求知欲。这是他“第一起”中知识探索的关键一步，从感性自然体验转向理性科学思考。"
        },
        {
            "chapter_number": "第四章",
            "title": "从具象到抽象：思维的跃迁",
            "topic": "第一人称。探讨张三从童年对具象星空的直观感受，到高中时期对抽象天文物理和理论物理的兴趣转变。本章将揭示他思维深度和广度的发展，以及这种从感性到理性的过渡如何塑造了他理解世界的方式。这是他“第一起”中思维方式形成的重要节点。"
        }
    ],
    "第三部 身体力行的探索与挑战": [
        {
            "chapter_number": "第五章",
            "title": "虎跳峡初体验：徒步新篇章",
            "topic": "第三人称。本章聚焦张三成年后在2005年云南虎跳峡的第一次徒步经历。描述这次徒步对体能和意志的巨大考验，特别是为了赶车在陡峭台阶上“猛爬”的坚持。这次经历开启了他对户外运动的兴趣，标志着他探索世界方式的拓展，从智力层面延伸到身体力行层面，是其人生“第二起”的开端。"
        },
        {
            "chapter_number": "第六章",
            "title": "挑战极限：意志力的磨砺",
            "topic": "第一人称。深入剖析张三在虎跳峡徒步过程中，身体极度疲惫却仍坚持不懈的内心挣扎与最终超越。探讨这次挑战如何磨砺了他的意志力，并让他意识到身体力行探索外部世界的乐趣与价值。这为他未来持续挑战自我埋下伏笔，是“第二起”中的重要转折与心境沉淀。"
        }
    ]
    ...
    "尾章" : [
        {
            "chapter_number": "-",
            "title": "山村童年的自由奔跑",
            "topic": "第三人称。本章将追溯张三在1980年代末至1990年代初，辽宁葫芦岛小村庄的童年岁月。描绘乡村的淳朴生活、日出而作日落而息的节奏，以及他作为“山里的野孩子”与自然亲密接触的自由时光。这是张三生命中“第一起”的萌芽，奠定了他与自然连接的性格底色和对规律生活的最初认知。"
        },
    ]
}
```
"""

        outline_origin = await inters.aintellect_remove(input_data=material,
                                            output_format=output_format,
                                            prompt_id ="0084",
                                            version = None,
                                            inference_save_case=False)

        outline = extract_json(outline_origin)
        return json.loads(outline)
    

    async def agener_biography_brief(self, outline: dict) -> str:
        """
        0083 传记简介
        """
        result = await inters.aintellect_remove_format(
            input_data = json.dumps(outline, ensure_ascii=False),
            prompt_id = "0083",
            version = None,
            inference_save_case=False,
            OutputFormat = ContentVer,
        )

        return result.get("content")

    async def amaterial_generate(self, vitae: str, memory_cards: list[str]) -> str:
        """
        素材整理
        vitae : 简历
        memory_cards : 记忆卡片们
        0085 素材整理
        0082 素材增量生成
        """
        def split_into_chunks(my_list, chunk_size=5):
            """
            使用列表推导式将列表分割成大小为 chunk_size 的块。
            """
            return [
                my_list[i : i + chunk_size] for i in range(0, len(my_list), chunk_size)
            ]

        # --- 示例 ---
        chunks = split_into_chunks(memory_cards, chunk_size=2)

        material = {"content":""}
        for i, chunk in enumerate(chunks):
            chunk = json.dumps(chunk, ensure_ascii=False)
            if i == 0:
                material = await inters.aintellect_remove_format(
                    input_data = vitae + chunk,
                    prompt_id = "0085",
                    version = None,
                    inference_save_case=False,
                    OutputFormat = ContentVer,
                        )
            else:
                material = await inters.aintellect_remove_format(
                    input_data = "#素材:\n" + material.get('content') + "#记忆卡片:\n" + chunk,
                    prompt_id = "0082",
                    version = None,
                    inference_save_case=False,
                    OutputFormat = ContentVer,
                        )
        return material.get("content")



    async def awrite_chapter(
        self,
        chapter,
        master="",
        material="",
        outline: dict = {},
        suggest_number_words=3000,
    ):
        created_material = ""
        try:
            # 0080 prompt_get_infos
            # 0081 prompt_base
            # TODO 大量的format 怎么办
            
            prompt_get_infos, _ = inters.get_prompts_from_sql(
                prompt_id="0080"
            )
            prompt_base, _ = inters.get_prompts_from_sql(
                prompt_id="0081"
            )

            material_prompt = prompt_get_infos.format(
                material=material,
                frame=json.dumps(outline),
                requirements=json.dumps(chapter),
            )
            try:
                material = await self.llm.aproduct(material_prompt)
            except Exception as e:
                raise TypeError("素材整理的时候出问题了")
            words = prompt_base.format(
                master=master,
                chapter=f'{chapter.get("chapter_number")} {chapter.get("title")}',
                topic=chapter.get("topic"),
                number_words=suggest_number_words,
                material=material,
                reference="",
                port_chapter_summery="",
            )
            try:
                article = await self.llm.aproduct(words)
            except Exception as e:
                raise TypeError("写传记的时候出问题了")
            try:
                chapter_name = await self.extract_person_name(article)
                chapter_place = await self.extract_person_place(article)
            except Exception as e:
                raise TypeError(f"提取东西的时候出问题了 {e}")

            assert isinstance(chapter_name, list)
            assert isinstance(chapter_place, list)

            return {
                "chapter_number": chapter.get("chapter_number"),
                "article": extract_article(article),
                "material": material,
                "created_material": created_material,
                "chapter_name": chapter_name,
                "chapter_place": chapter_place,
            }

        except Exception as e:
            print(f"Error processing chapter {chapter.get('chapter_number')}: {e}")
            return {
                "chapter_number": chapter.get("chapter_number"),
                "article": "",
                "material": "material",
                "created_material": "created_material",
                "chapter_name": "chapter_name",
                "chapter_place": "chapter_place",
            }

    async def agenerate_biography_free(
        self, user_name: str, vitae: str, memory_cards: list[dict]
    ):

        memoryCards_str, _ = memoryCards2str(memory_cards)

        result = await inters.aintellect_remove_format(
            input_data = f"{user_name},{vitae},{memoryCards_str}",
            prompt_id = "0095",
            version = None,
            inference_save_case=False,
            OutputFormat = Biography_Free,
        )
        
        return result


        # super_log(result,'gener_95')
        # result = deal_json_result(result)
        # return result
