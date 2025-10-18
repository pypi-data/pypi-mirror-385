""" core 需要修改"""
from typing import Dict, Any
from serverz.utils import extract_last_user_input
from serverz.log import Log
from llmada.core import BianXieAdapter
from prompt_writing_assistant.prompt_helper import Intel,IntellectType
from prompt_writing_assistant.utils import extract_
from pydantic import BaseModel
import json
import time
from serverz.prompt import chat_model,deep_model,Works
from utils_tool.file import super_log
from llmada.core import ArkAdapter

logger = Log.logger

coding_log = logger.debug

wok = Works()
class ChatBox():
    """ chatbox """
    def __init__(self) -> None:
        self.bx = BianXieAdapter()
        self.ark = ArkAdapter()
        self.custom = ["OriginGemini","Z_LongMemory","diglife_interview","doubao"]

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

        if model == "OriginGemini":
            async for word in self.bx.aproduct_stream(prompt_with_history):
                yield word
        elif model == 'Z_LongMemory':
            yield "hello"

        elif model == "doubao":
            yield "开始2\n"
            async for word in self.ark.aproduct_stream(prompt_with_history):
                yield word

        elif model == 'diglife_interview':
            yield "开始\n"
            gener = wok.chat_interview(prompt_with_history)
            async for word in gener:
                yield word
        else:
            yield 'pass'


