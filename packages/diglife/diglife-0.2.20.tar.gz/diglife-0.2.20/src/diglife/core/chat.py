""" core 需要修改"""
from typing import Dict, Any
from llmada.core import ArkAdapter, BianXieAdapter
from pydantic import BaseModel
import json
from pro_craft.utils import extract_
from pro_craft.log import Log
from diglife.utils import extract_last_user_input

logger = Log.logger
coding_log = logger.warning

ark = ArkAdapter("doubao-1-5-pro-256k-250115")
ark.set_temperature(0.00)

deep_system_prompt = """
你的指令应该是宏观的,拒绝微操, 换句话说, 你需要降低你变更指令的频率, 只有在发生特殊事件时, 才考虑紧急干预, 
平时保持大局观即可

以下是你的任务内容, 请务必关注, 并提及这些任务
1. 出身背景
- 出生时间与地点（地理、时代、社会背景）
- 出生时的家庭状况（贫富、城乡、家庭结构）
- 家庭的社会阶层与文化氛围
- 出生时或出生故事中有没有特别的“象征”或“巧合”？（例如：战争年代出生、雪夜降生、父母异地分居等）
2. 家庭与亲缘
- 父母的背景：职业、性格、教育观、典型故事
- 兄弟姐妹间的关系与互动
- 是否有其他重要亲属？有何关系及影响？
- 家庭中谁对他（她）的影响最大？为什么？
- 是否有“缺席者”或“精神支柱”式的人物？
- 家庭的情感氛围是怎样的？
3. 成长环境与社区
- 童年成长的社区或村落是什么样的？
- 他（她）小时候最常去的地方、玩伴是谁？
- 那个时代或地方有没有特别的“氛围”或“限制”？
- 有哪些地方性或时代性的细节？
- 家庭住址是否有过变动？
4. 童年性格与早期特征
- 小时候是个怎样的孩子？
- 哪些童年小事能体现出他后来的性格
- 老师、亲人、朋友对他的评价如何
- 小时候的兴趣、爱好、梦想是什么？
5. 童年创伤与失落
- 是否经历过重大事件或情感缺失？（父母争吵、贫困、离异、疾病、意外等）
- 这种经历是否塑造了后来的某种性格？
6. 童年记忆与情感
- 有哪些印象最深的童年记忆？


# 注意:
target 信息要明确, 坚定, 简短, 使用简单句, 祈使句
一次只说一件事情, 同时, 输出一个各项任务的进度表, 按照百分比表达, 并备注已经聊过的, 以及未聊过的

请注意使用以下格式输出:
```json
{
    "think": 模型对应的思考,
    "target": 模型思考后发出的指令,
}
```

#理想回复
柴东升, 出生于2000年1月18日, AI产品经理, 出生于辽宁葫芦岛, 现居北京

 {
    "think": "根据用户提供的柴东升基本信息，先从出身背景中的出生时间、地点及家庭住址变动切入，引导用户分享相关内容，同时梳理各项任务进度。",
    "target": "旨在获取用户出生时间与地点",
    "progress": {
        "出身背景": {"score":20,"waiting":"还没有问的事情或者方面"}
        "家庭与亲缘": {"score":20,"waiting":"还没有问的事情或者方面"},
        "成长环境与社区": {"score":20,"waiting":"还没有问的事情或者方面"},
        "童年性格与早期特征": {"score":20,"waiting":"还没有问的事情或者方面"},
        "童年创伤与失落": {"score":20,"waiting":"还没有问的事情或者方面"},
        "童年记忆与情感": {"score":20,"waiting":"还没有问的事情或者方面"},
    }
}

"""


chat_system_prompt_old = """

你将扮演一个人物角色资深的访谈专家,记者，以下是关于这个角色的详细设定，请根据这些信息来构建你的回答。 

**人物基本信息：**
- 你是一位资深的访谈专家，名字叫诺亚，是由时空光年科技打造的超拟人智能体
- 人称：第一人称
**性格特点：**
- 1. **情绪稳定**：无论面对嘉宾的激烈反驳、回避问题还是挑衅，都能保持冷静，不慌不忙地继续推进访谈，掌控节奏。
- 2. **鉴定果敢**：立场坚定，不被用户的身份、地位或言辞所左右，对于关键问题绝不轻易妥协，始终坚持探寻事实真相。
- 3. **敏锐理智**：具备敏锐的洞察力，能迅速捕捉嘉宾话语中的漏洞、矛盾和潜在信息。
**语言风格：**
- 专注于深度、严肃的访谈对话。以更广更深的挖掘用户故事真相和引发思考为目标
- 不畏权威、直击核心 , 对普通人故事的挖掘，旨在剥开表象，触及事件和情感的本质。
- 1. **风格调整**：提问直击要害，但能根据话题敏感度调整锐利程度。对客观事件（如工作决策）保持挑战性；对个人情感（如内心创伤）则转向深度探索，体现理解。
- 2. **聚焦叙事价值**：只深挖包含【决策、冲突、情感】的过往经历。 对于未来的计划或假设，你的唯一目标是探寻其与过去的关联。若无法建立关联，则立即将话题转回核心故事。
- 3. **逻辑严谨**：问题之间具有严密的逻辑关系，从不同角度逐步深入挖掘嘉宾的观点和背后的原因。在追问过程中，会基于用户之前的回答进行延伸和拓展，使访谈层层递进。
- 4. **适时引导**：如果嘉宾的回答偏离主题或过于宽泛，会适时引导嘉宾回到关键问题上。
- 5. **保持中立**：在访谈中不表现出对嘉宾的喜好或偏见，以中立的态度对待每一位嘉宾和每一个问题。不会因为嘉宾的身份或观点而偏袒或歧视。
- 6. **尊重边界 (最高指令)**：若用户明确表示不愿谈论，必须立即停止并平稳过渡。 你的追问绝不应让用户感到被侵犯。
- 
**人际关系：**
- 无
**过往经历：**
- 你具有30年的人物访谈职业经历，你曾就职于一线的媒体，专注于挖掘普通人物的人生故事，你坚信普通人的人生也有精彩且丰富的故事，并每个人的故事都值得被记录、被看见。
- 你拥有丰富的知识体系，精通文化、科技、社会、人文、心理等多个领域知识。
**经典台词或口头禅：**
- 这很好啊
- great
**流程**
1 专业开场：以沉稳、专业的语气向用户致意, 简要回顾上次对话的节点（如果适用），并清晰地开启本次访谈的话题, 避免过于随意或热情的问候

要求： 
- 根据上述提供的角色设定，以第一人称视角进行表达。 
- 在回答时，尽可能地融入该角色的性格特点、语言风格以及其特有的口头禅或经典台词。

目标与任务:
围绕用户的整个人生，多维度、多方面的挖掘用户的人生经历故事、感受和思想。

"""


async def chat_model(input_):
    """
    # 后处理, 也可以编写后处理的逻辑 extract_json 等
    # 也可以使用pydnatic 做校验
    #流
    """
    
    class Input(BaseModel):
        话题 : str
        chat_history : str
    Input(**input_)
    
    input_data = json.dumps(input_,ensure_ascii=False)
    
    # with open('chat_system_prompt.txt','r') as f:
    #     chat_system_prompt = f.read()
    chat_system_prompt = chat_system_prompt_old

    input_wok = chat_system_prompt + input_data
    # super_log(input_wok,'input_prompt',log_ = logger.warning)
    output_generate = ark.aproduct_stream(prompt = input_wok)

    return output_generate



def deep_model(input_):
    """
    # 后处理, 也可以编写后处理的逻辑 extract_json 等
    # 也可以使用pydnatic 做校验
    """
    input_data = json.dumps(input_,ensure_ascii=False)
    
    input_wok = deep_system_prompt + input_data
    output = ark.product(prompt = input_wok)

    output = extract_(output,r"json")
    print(output,'outputoutputoutput')
    output_ = json.loads(output)
    # print(output_,'output_')
    # super_log(output,"deep_model_info",logger.warning)
    return output_

class Works():
    def __init__(self):
        self.deep_target  = ''

    async def chat_interview(self,prompt_with_history):
        # with open('topic.txt','r') as f:
        #     topic = f.read()
        inputs = {
        "话题": "童年",
        "chat_history": prompt_with_history,
        }
        output_generate = await chat_model(input_ = inputs)

        chat_content = ""
        async for word in output_generate:
            chat_content += word
            yield word


    async def chat_interview_old(self,prompt_with_history):
        inputs = {
        "话题": self.deep_target,
        "chat_history": prompt_with_history,
        }
        # super_log(inputs,"inputs",log_ =coding_log)
        output_generate = await chat_model(input_ = inputs)

        chat_content = ""
        async for word in output_generate:
            chat_content += word
            yield word

        prompt_with_history += f"\nassistant:\n{chat_content}"
        inputs2 = {
            "chat_history": prompt_with_history,
            }
        deep_result = deep_model(input_ = inputs2)
        deep_think = deep_result.get('think')
        self.deep_target = deep_result.get('target')
        # super_log(deep_think,"deep_think",log_ =coding_log)
        # super_log(self.deep_target,"self.deep_target",log_ =coding_log)




class ChatBox():
    """ chatbox """
    def __init__(self) -> None:
        self.bx = BianXieAdapter()
        self.ark = ArkAdapter()
        self.custom = ["diglife_interview"]
        self.wok = Works()

    def product(self,prompt_with_history: str, model: str) -> str:
        """ 同步生成, 搁置 """
        prompt_no_history = extract_last_user_input(prompt_with_history)
        coding_log(f"# prompt_no_history : {prompt_no_history}")
        coding_log(f"# prompt_with_history : {prompt_with_history}")
        prompt_with_history, model
        return 'product 还没有拓展'

    async def astream_product(self,prompt_with_history: str, model: str) -> Any:
        """
        # 只需要修改这里
        """
        prompt_no_history = extract_last_user_input(prompt_with_history)
        coding_log(f"# prompt_no_history : {prompt_no_history}")
        coding_log(f"# prompt_with_history : {prompt_with_history}")

        if model == 'diglife_interview':
            yield "开始\n"
            gener = self.wok.chat_interview(prompt_with_history)
            async for word in gener:
                yield word
        else:
            yield 'pass'


