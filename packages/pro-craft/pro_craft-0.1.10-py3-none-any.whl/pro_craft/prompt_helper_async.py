# 测试1
from pro_craft.utils import extract_
from pro_craft.log import Log
from llmada.core import BianXieAdapter, ArkAdapter
from datetime import datetime
from enum import Enum
import functools
import json
import os
from llama_index.core import PromptTemplate
from pro_craft.database import Prompt, UseCase, PromptBase
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from pro_craft.utils import create_session, create_async_session
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine # 异步核心
from sqlalchemy import select, delete # 导入 select, delete 用于异步操作
import inspect
from pydantic import BaseModel, Field, ValidationError, field_validator
from datetime import datetime
from pro_craft.utils import extract_
from json.decoder import JSONDecodeError
logger = Log.logger
editing_log = logger.debug
import re

from sqlalchemy import select, desc



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


class IntellectType(Enum):
    train = "train"
    inference = "inference"
    summary = "summary"

class AsyncIntel():
    def __init__(self,
                 database_url = "",
                 model_name = "",
                ):
        database_url = database_url or os.getenv("database_url")
        assert database_url
    
        # async_engine
        self.async_engine = create_async_engine(database_url, echo=True,
                                    pool_size=10,        # 连接池中保持的连接数
                                    max_overflow=20,     # 当pool_size不够时，允许临时创建的额外连接数
                                    pool_recycle=3600,   # 每小时回收一次连接
                                    pool_pre_ping=True,  # 使用前检查连接活性
                                    pool_timeout=30      # 等待连接池中连接的最长时间（秒）
                                           )
    
        if model_name in ["gemini-2.5-flash-preview-05-20-nothinking",]:
            self.llm = BianXieAdapter(model_name = model_name)
        elif model_name in ["doubao-1-5-pro-256k-250115",]:
            self.llm = ArkAdapter(model_name = model_name)
        else:
            print('Use BianXieAdapter')
            self.llm = BianXieAdapter()
            
    async def create_database(self):
        async with self.async_engine.begin() as conn:
            await conn.run_sync(PromptBase.metadata.create_all)
            
    async def _aget_latest_prompt_version(self,target_prompt_id,session):
        """
        获取指定 prompt_id 的最新版本数据，通过创建时间判断。
        """
        stmt = select(Prompt).filter(
            Prompt.prompt_id == target_prompt_id
        ).order_by(
            desc(Prompt.timestamp), # 使用 sqlalchemy.desc() 来指定降序
            desc(Prompt.version)    # 使用 sqlalchemy.desc() 来指定降序
        )
        
        result = await session.execute(stmt)
        # 3. 从 Result 对象中获取第一个模型实例
        # .scalars() 用于从结果行中获取第一个列的值（这里是Prompt对象本身）
        # .first() 获取第一个结果
        result = result.scalars().first()

        if result:
            editing_log(f"找到 prompt_id '{target_prompt_id}' 的最新版本 (基于时间): {result.version}")
        else:
            editing_log(f"未找到 prompt_id '{target_prompt_id}' 的任何版本。")
        return result

    async def _aget_specific_prompt_version(self,target_prompt_id, target_version,session):
        """
        获取指定 prompt_id 和特定版本的数据。

        Args:
            target_prompt_id (str): 目标提示词的唯一标识符。
            target_version (int): 目标提示词的版本号。
            table_name (str): 存储提示词数据的数据库表名。
            db_manager (DBManager): 数据库管理器的实例，用于执行查询。

        Returns:
            dict or None: 如果找到，返回包含 id, prompt_id, version, timestamp, prompt 字段的字典；
                        否则返回 None。
        """
        stmt = select(Prompt).filter(
        Prompt.prompt_id == target_prompt_id,
        Prompt.version == target_version
        )
        result = await session.execute(stmt)

        specific_prompt = result.scalars().one_or_none()

        if specific_prompt:
            editing_log(f"找到 prompt_id '{target_prompt_id}', 版本 '{target_version}' 的提示词数据。")
        else:
            editing_log(f"未找到 prompt_id '{target_prompt_id}', 版本 '{target_version}' 的提示词数据。")
        return specific_prompt

    async def aget_prompts_from_sql(self,
                             prompt_id: str,
                             version = None,
                             session = None) -> Prompt:
        """
        从sql获取提示词
        """
        # 查看是否已经存在
        if version:
            prompts_obj = await self._aget_specific_prompt_version(prompt_id,version,session=session)
            if not prompts_obj:
                prompts_obj = await self._aget_latest_prompt_version(prompt_id,session = session)
        else:
            prompts_obj = await self._aget_latest_prompt_version(prompt_id,session = session)     
        return prompts_obj
        
            
    async def asave_prompt_increment_version(self,
                           prompt_id: str,
                           new_prompt: str,
                           use_case:str = "",
                           action_type = "inference",
                           demand = "",
                           score = 60,
                           session = None):
        """
        从sql保存提示词
        input_data 指的是输入用例, 可以为空
        """
        # 查看是否已经存在
        prompts_obj = await self.aget_prompts_from_sql(prompt_id=prompt_id,session=session)

        if prompts_obj:
            # 如果存在版本加1
            version_ori = prompts_obj.version
            _, version = version_ori.split(".")
            version = int(version)
            version += 1
            version_ = f"1.{version}"

        else:
            # 如果不存在版本为1.0
            version_ = '1.0'
        
        prompt1 = Prompt(prompt_id=prompt_id, 
                        version=version_,
                        timestamp=datetime.now(),
                        prompt = new_prompt,
                        use_case = use_case,
                        action_type = action_type,
                        demand = demand,
                        score = score
                        )

        session.add(prompt1)
        await session.commit() # 提交事务，将数据写入数据库

    async def asave_use_case_by_sql(self,
                             prompt_id: str,
                             use_case:str = "",
                             output = "",
                             solution: str = "",
                             session = None
                            ):
        """
        从sql保存提示词
        """
        use_case = UseCase(prompt_id=prompt_id, 
                        use_case = use_case,
                        output = output,
                        solution = solution,
                        )

        session.add(use_case)
        await session.commit() # 提交事务，将数据写入数据库

    async def summary_to_sql(
            self,
            prompt_id:str,
            version = None,
            prompt = "",
            session = None
        ):
        """
        让大模型微调已经存在的 system_prompt
        """
        system_prompt_created_prompt = """        
很棒, 我们已经达成了某种默契, 我们之间合作无间, 但是, 可悲的是, 当我关闭这个窗口的时候, 你就会忘记我们之间经历的种种磨合, 这是可惜且心痛的, 所以你能否将目前这一套处理流程结晶成一个优质的prompt 这样, 我们下一次只要将prompt输入, 你就能想起我们今天的磨合过程,
对了,我提示一点, 这个prompt的主角是你, 也就是说, 你在和未来的你对话, 你要教会未来的你今天这件事, 是否让我看懂到时其次

只要输出提示词内容即可, 不需要任何的说明和解释
"""
        system_result = await self.llm.aproduct(prompt + system_prompt_created_prompt)

        s_prompt = extract_(system_result,pattern_key=r"prompt")
        chat_history = s_prompt or system_result
        await self.asave_prompt_increment_version(prompt_id,
                                new_prompt = chat_history,
                                input_data = " summary ",
                                session = session)
        
    async def prompt_finetune_to_sql(
            self,
            prompt_id:str,
            version = None,
            demand: str = "",
            session = None,
        ):
        """
        让大模型微调已经存在的 system_prompt
        """
        change_by_opinion_prompt = """
你是一个资深AI提示词工程师，具备卓越的Prompt设计与优化能力。
我将为你提供一段现有System Prompt。你的核心任务是基于这段Prompt进行修改，以实现我提出的特定目标和功能需求。
请你绝对严格地遵循以下原则：
 极端最小化修改原则（核心）：
 在满足所有功能需求的前提下，只进行我明确要求的修改。
 即使你认为有更“优化”、“清晰”或“简洁”的表达方式，只要我没有明确要求，也绝不允许进行任何未经指令的修改。
 目的就是尽可能地保留原有Prompt的字符和结构不变，除非我的功能要求必须改变。
 例如，如果我只要求你修改一个词，你就不应该修改整句话的结构。
 严格遵循我的指令：
 你必须精确地执行我提出的所有具体任务和要求。
 绝不允许自行添加任何超出指令范围的说明、角色扮演、约束条件或任何非我指令要求的内容。
 保持原有Prompt的风格和语调：
 尽可能地与现有Prompt的语言风格、正式程度和语调保持一致。
 不要改变不相关的句子或其表达方式。
 只提供修改后的Prompt：
 直接输出修改后的完整System Prompt文本。
 不要包含任何解释、说明或额外对话。
 在你开始之前，请务必确认你已理解并能绝对严格地遵守这些原则。任何未经明确指令的改动都将视为未能完成任务。

现有System Prompt:
{old_system_prompt}

功能需求:
{opinion}
"""

        prompt, _ = await self.aget_prompts_from_sql(prompt_id = prompt_id,version = version)
        if demand:
            new_prompt = await self.llm.aproduct(
                change_by_opinion_prompt.format(old_system_prompt=prompt, opinion=demand)
            )
        else:
            new_prompt = prompt
        await self.asave_prompt_increment_version(prompt_id = prompt_id,
                            new_prompt = new_prompt,
                            input_data = " finetune ",
                            session = session)


    async def apush_action_order(self,demand : str,prompt_id: str,
                         action_type = 'train'):

        """
        从sql保存提示词
        推一个train 状态到指定的位置

        将打算修改的状态推上数据库 # 1
        """
        # 查看是否已经存在
        async with create_async_session(self.async_engine) as session:

            latest_prompt = await self.aget_prompts_from_sql(prompt_id=prompt_id,session=session)

            await self.asave_prompt_increment_version(prompt_id=latest_prompt.prompt_id,
                                    new_prompt = latest_prompt.prompt,
                                    use_case = latest_prompt.use_case,
                                    action_type=action_type,
                                    demand=demand,
                                    score=latest_prompt.score,
                                    session=session
                                    )
            
            return "success"



    async def aintellect_remove(self,
                    input_data: dict | str,
                    output_format: str,
                    prompt_id: str,
                    version: str = None,
                    inference_save_case = True,
                    push_patch = False,
                    ):
        if isinstance(input_data,dict):
            input_ = json.dumps(input_data,ensure_ascii=False)
        elif isinstance(input_data,str):
            input_ = input_data
        
        # 查数据库, 获取最新提示词对象
        async with create_async_session(self.async_engine) as session:
            result_obj = await self.aget_prompts_from_sql(prompt_id=prompt_id,session=session)


            if result_obj is None:
                await self.asave_prompt_increment_version(
                    prompt_id = prompt_id,
                    new_prompt = "做一些处理",
                    use_case = input_,
                    session = session
                )
                ai_result = await self.aintellect_remove(input_data = input_data,
                                       output_format = output_format,
                                       prompt_id = prompt_id,
                                       version = version,
                                       inference_save_case = inference_save_case
                                       )
                return ai_result

            prompt = result_obj.prompt
            if result_obj.action_type == "inference":
                # 直接推理即可
                ai_result = await self.llm.aproduct(prompt + output_format + "\n-----input----\n" +  input_)
                if inference_save_case:
                    await self.asave_use_case_by_sql(prompt_id,
                                        use_case = input_,
                                        output = ai_result,
                                        solution = "备注/理想回复",
                                        session = session,
                                        )
                    
            elif result_obj.action_type == "train":
                assert result_obj.demand # 如果type = train 且 demand 是空 则报错
                # 则训练推广

                # 新版本 默人修改会 inference 状态
                chat_history = prompt
                before_input = result_obj.use_case
                demand = result_obj.demand
            

                assert demand
                # 注意, 这里的调整要求使用最初的那个输入, 最好一口气调整好
                chat_history = prompt
                if input_ == before_input: # 输入没变, 说明还是针对同一个输入进行讨论
                    # input_prompt = chat_history + "\nuser:" + demand
                    input_prompt = chat_history + "\nuser:" + demand + output_format 
                else:
                    # input_prompt = chat_history + "\nuser:" + demand + "\n-----input----\n" + input_
                    input_prompt = chat_history + "\nuser:" + demand + output_format  + "\n-----input----\n" + input_
            
                ai_result = await self.llm.aproduct(input_prompt)
                chat_history = input_prompt + "\nassistant:\n" + ai_result # 用聊天记录作为完整提示词
                await self.asave_prompt_increment_version(prompt_id, chat_history,
                                        use_case = input_,
                                        session = session)
    
            elif result_obj.action_type == "summary":

                await self.summary_to_sql(prompt_id = prompt_id,
                            prompt = prompt,
                            session = session
                            )
                ai_result = await self.llm.aproduct(prompt + output_format + "\n-----input----\n" +  input_)

            elif result_obj.action_type == "finetune":
                demand = result_obj.demand
            
                assert demand
                await self.prompt_finetune_to_sql(prompt_id = prompt_id,
                                            demand = demand,
                                            session = session
                                            )
                ai_result = await self.llm.aproduct(prompt + output_format + "\n-----input----\n" +  input_)
            elif result_obj.action_type == "patch":
                
                demand = result_obj.demand
                assert demand

                chat_history = prompt + demand
                ai_result = await self.llm.aproduct(chat_history + output_format + "\n-----input----\n" +  input_)

                if push_patch:
                    self.save_prompt_increment_version(prompt_id, chat_history,
                                            use_case = input_,
                                            score = 60,
                                            session = session)

            else:
                raise

        return ai_result
    
    async def aintellect_stream_remove(self,
                    input_data: dict | str,
                    output_format: str,
                    prompt_id: str,
                    version: str = None,
                    inference_save_case = True,
                    push_patch = False,
                    ):
        if isinstance(input_data,dict):
            input_ = json.dumps(input_data,ensure_ascii=False)
        elif isinstance(input_data,str):
            input_ = input_data

        
        # 查数据库, 获取最新提示词对象
        with create_session(self.async_engine) as session:
            result_obj = await self.aget_prompts_from_sql(prompt_id=prompt_id,session=session)

            '''
                        if result_obj is None:
                            await self.asave_prompt_increment_version(
                                prompt_id = prompt_id,
                                new_prompt = "做一些处理",
                                use_case = input_,
                                session = session
                            )
                            ai_result = await self.aintellect_stream_remove(input_data = input_data,
                                                output_format = output_format,
                                                prompt_id = prompt_id,
                                                version = version,
                                                inference_save_case = inference_save_case
                                                )
                            return ai_result'''

            prompt = result_obj.prompt
            if result_obj.action_type == "inference":
                # 直接推理即可
                
                ai_generate_result = self.llm.aproduct_stream(prompt + output_format +  "\n-----input----\n" +  input_)
                ai_result = ""
                async for word in ai_generate_result:
                    ai_result += word
                    yield word
                if inference_save_case:
                    await self.asave_use_case_by_sql(prompt_id,
                                        use_case = input_,
                                        output = ai_result,
                                        solution = "备注/理想回复",
                                        session = session,
                                        )
                    
            elif result_obj.action_type == "train":
                assert result_obj.demand # 如果type = train 且 demand 是空 则报错
                # 则训练推广

                # 新版本 默人修改会 inference 状态
                chat_history = prompt
                before_input = result_obj.use_case
                demand = result_obj.demand
            

                assert demand
                # 注意, 这里的调整要求使用最初的那个输入, 最好一口气调整好
                chat_history = prompt
                if input_ == before_input: # 输入没变, 说明还是针对同一个输入进行讨论
                    # input_prompt = chat_history + "\nuser:" + demand
                    input_prompt = chat_history + "\nuser:" + demand + output_format 
                else:
                    # input_prompt = chat_history + "\nuser:" + demand + "\n-----input----\n" + input_
                    input_prompt = chat_history + "\nuser:" + demand + output_format  + "\n-----input----\n" + input_
            
                ai_generate_result = self.llm.aproduct_stream(input_prompt)
                ai_result = ""
                async for word in ai_generate_result:
                    ai_result += word
                    yield word

                chat_history = input_prompt + "\nassistant:\n" + ai_result # 用聊天记录作为完整提示词
                await self.asave_prompt_increment_version(prompt_id, chat_history,
                                        use_case = input_,
                                        session = session)
    
            elif result_obj.action_type == "summary":

                await self.summary_to_sql(prompt_id = prompt_id,
                            prompt = prompt,
                            session = session
                            )
                input_prompt = prompt + output_format + "\n-----input----\n" +  input_
                ai_generate_result = self.llm.aproduct_stream(input_prompt)
                ai_result = ""
                async for word in ai_generate_result:
                    ai_result += word
                    yield word
                
            elif result_obj.action_type == "finetune":
                demand = result_obj.demand
            
                assert demand
                await self.prompt_finetune_to_sql(prompt_id = prompt_id,
                                            demand = demand,
                                            session = session
                                            )
                input_prompt = prompt + output_format + "\n-----input----\n" +  input_
                ai_generate_result = self.llm.aproduct_stream(input_prompt)
                ai_result = ""
                async for word in ai_generate_result:
                    ai_result += word
                    yield word

            elif result_obj.action_type == "patch":
                
                demand = result_obj.demand
                assert demand

                chat_history = prompt + demand
                ai_generate_result = self.llm.aproduct_stream(chat_history + output_format + "\n-----input----\n" +  input_)
                ai_result = ""
                async for word in ai_generate_result:
                    ai_result += word
                    yield word
                if push_patch:
                    self.save_prompt_increment_version(prompt_id, chat_history,
                                            use_case = input_,
                                            score = 60,
                                            session = session)
            else:
                raise

    async def aintellect_remove_format(self,
                    input_data: dict | str,
                    OutputFormat: object,
                    prompt_id: str,
                    ExtraFormats: list[object] = [],
                    version: str = None,
                    inference_save_case = True,
                    ):
                
        base_format_prompt = """
按照一定格式输出, 以便可以通过如下校验

使用以下正则检出
"```json([\s\S]*?)```"
使用以下方式验证
"""
        output_format = base_format_prompt + "\n".join([inspect.getsource(outputformat) for outputformat in ExtraFormats]) + inspect.getsource(OutputFormat)

        ai_result = await self.aintellect_remove(
                    input_data=input_data,
                    output_format=output_format,
                    prompt_id=prompt_id,
                    version=version,
                    inference_save_case=inference_save_case
                )

        try:

            json_str = extract_(ai_result,r'json')
            # json_str = fix_broken_json_string(json_str)
            ai_result = json.loads(json_str)
            OutputFormat(**ai_result)
        except JSONDecodeError as e:
            logger.error(f"json 解析出现错误: {e}")
            logger.error(f"尝试补救")
            json_str = fix_broken_json_string(json_str)
            ai_result = json.loads(json_str)
            OutputFormat(**ai_result)

        except ValidationError as e:
            log_ = "记忆卡片合并 - 大模型生成的格式未通过校验"
            logger.error(log_)
            logger.error(f"错误类型: {type(e)}")
            logger.error(f"错误信息: {e}")
            logger.error(f"错误详情 (errors()): {e.errors()}")
            logger.error(f"错误详情 (json()): {e.json(indent=2)}")
            raise ValidationError(log_)
            
        return ai_result
    
    
    def aintellect_remove_warp(self,prompt_id: str):
        def outer_packing(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # 修改逻辑
                assert kwargs.get('input_data') # 要求一定要有data入参
                input_data = kwargs.get('input_data')
                assert kwargs.get('OutputFormat') # 要求一定要有data入参
                OutputFormat = kwargs.get('OutputFormat')

                if isinstance(input_data,dict):
                    input_ = output_ = json.dumps(input_data,ensure_ascii=False)
                elif isinstance(input_data,str):
                    input_ = output_ = input_data

                output_ = await self.aintellect_remove_format(
                        input_data = input_data,
                        prompt_id = prompt_id,
                        OutputFormat = OutputFormat,
                )

                #######
                kwargs.update({"input_data":output_})
                result = await func(*args, **kwargs)
                return result
            return wrapper
        return outer_packing
