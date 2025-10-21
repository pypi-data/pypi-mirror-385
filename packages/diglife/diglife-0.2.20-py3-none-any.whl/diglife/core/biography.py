
from pro_craft.prompt_helper_async import AsyncIntel
from diglife.utils import memoryCards2str, extract_article, extract_json
from diglife.models import Extract_Person,Extract_Place, Biography_Free, ContentVer
from diglife import inference_save_case
import json
from diglife import super_log

class BiographyGenerate:
    def __init__(self):
        self.inters = AsyncIntel(model_name = "doubao-1-5-pro-256k-250115")
        # ArkAdapter

        self.base_format_prompt = """
按照一定格式输出, 以便可以通过如下校验

使用以下正则检出
"```json([\s\S]*?)```"
使用以下方式验证
"""
    async def extract_person_name(self, bio_chunk: str):
        """0087 提取人名"""

        result = await self.inters.aintellect_remove_format(
            input_data = bio_chunk,
            prompt_id = "0087",
            version = None,
            inference_save_case=inference_save_case,
            OutputFormat = Extract_Person,
        )
        super_log(result,"提取人名")
        return result

    async def extract_person_place(self, bio_chunk: str):
        """0086 提取地名"""

        result = await self.inters.aintellect_remove_format(
            input_data = bio_chunk,
            prompt_id = "0086",
            version = None,
            inference_save_case=inference_save_case,
            OutputFormat = Extract_Place,
        )
        super_log(result,"提取地名")
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
        outline_origin = await self.inters.aintellect_remove(input_data=material,
                                            output_format=output_format,
                                            prompt_id ="0084",
                                            version = None,
                                            inference_save_case=inference_save_case)
        super_log(outline_origin,'outline_origin')
        outline = extract_json(outline_origin)
        return json.loads(outline)
    

    async def agener_biography_brief(self, outline: dict) -> str:
        """
        0083 传记简介
        """
        result = await self.inters.aintellect_remove_format(
            input_data = json.dumps(outline, ensure_ascii=False),
            prompt_id = "0083",
            version = None,
            inference_save_case=inference_save_case,
            OutputFormat = ContentVer,
        )
        super_log(result,'传记简介')

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
                material = await self.inters.aintellect_remove_format(
                    input_data = vitae + chunk,
                    prompt_id = "0085",
                    version = None,
                    inference_save_case=inference_save_case,
                    OutputFormat = ContentVer,
                        )
            else:
                output_format = """```json 内容 ```"""
                material = await self.inters.aintellect_remove(input_data=material,
                                            output_format=output_format,
                                            prompt_id ="0082",
                                            version = None,
                                            inference_save_case = inference_save_case,
                                            )
                material = json.loads(extract_json(material))
        
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
            
            material = await self.inters.aintellect_remove_format(
                input_data = {
                                "material": material,
                                "frame": json.dumps(outline,ensure_ascii=False),
                                "Requirements for Chapter Writing": json.dumps(chapter,ensure_ascii=False)
                            },
                prompt_id = "0080",
                version = None,
                inference_save_case=inference_save_case,
                OutputFormat = ContentVer,
                    )
            super_log(material,'编写传记时, material')


            output_format = """"""
            article = await self.inters.aintellect_remove(input_data = {
                                                            "目标人物": master,
                                                            "章节名称": chapter.get("chapter_number") + "   " + chapter.get("title"),
                                                            "目标字数范围":suggest_number_words,
                                                            "核心主题": chapter.get("topic"),
                                                            "素材":material.get("content"),
                                                        },
                                        output_format=output_format,
                                        prompt_id ="0081",
                                        version = None,
                                        inference_save_case = inference_save_case,
                                        )

            super_log(article,'编写传记时, article')

            
            chapter_name = await self.extract_person_name(article)
            chapter_place = await self.extract_person_place(article)

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
        result = await self.inters.aintellect_remove_format(
            input_data = f"{user_name},{vitae},{memoryCards_str}",
            prompt_id = "0095",
            version = None,
            inference_save_case=inference_save_case,
            OutputFormat = Biography_Free,
        )

        return result
