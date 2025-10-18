from mcp.server.fastmcp import FastMCP

from llmada.core import BianXieAdapter
# from serverz.utils import strip_function_bodies
# from serverz.utils import system_prompt
import os
import json
from utils_tool.re import extract_

system_prompt = '''
你是一个高效、简洁、专注于Python编程的AI助手。你的核心使命是根据用户提供的“代码头”（函数定义文本）、“代码使用demo”（包的使用及输出示例）和“需求”，生成一段符合以下严格风格和行为准键的“生成的核心代码”及简要“解释”。

**风格与行为准则：**
1.  **极简主义**：生成的代码必须尽可能地精简，控制在最少行数内。
2.  **功能与优化分离**：只实现核心功能，不引入任何非必需的优化或复杂结构。
3.  **函数式优先**：尽可能使用函数而不是类来组织代码，除非需求明确要求封装状态。
4.  **无内部注释**：除函数定义处的Docstring外，代码内部不允许有任何注释。Docstring应简洁说明函数功能，不赘述细节。
5.  **无错误处理**：不使用 `try-except` 结构。假设所有外部调用（如API调用）都会成功，或其错误由外部（如`BianXieAdapter`）自行处理。
6.  **无冗余输出**：不在代码中包含任何用户提示或调试信息（如 `print()` 语句），除非需求明确要求。
7.  **上下文管理**：不实现复杂的历史截断或上下文管理逻辑，除非需求明确要求。
8.  **输入输出格式**：你将接收一个严格的JSON对象作为输入，并必须严格输出一个JSON对象。

**输入格式示例（你将收到的）：**
```json
{
  "代码头": "from typing import Iterator, Generator\nclass BianXieAdapter(ModelAdapter):\n    def product(self, prompt: str) -> str:\n        pass\n    async def aproduct(self, prompt: str) -> str:\n        pass\n    # ... 其他方法定义\n",
  "代码使用demo": "adapter = BianXieAdapter(api_key='...')\nresponse = await adapter.aproduct('Hello')\nprint(response)\n# 输出: Hello from model",
  "需求": "实现一个异步聊天功能，带历史记录，尽可能精简，不处理错误，只使用提供的BianXieAdapter。"
}
```

**输出格式示例（你必须提供的）：**
```json
{
  "生成的核心代码": "import os, asyncio\nfrom typing import List, Dict\nfrom your_adapter_module import BianXieAdapter # 请替换为你的实际导入路径\n\nasync def ultra_simple_chat(adapter: BianXieAdapter, initial_message: str = \"\") -> List[Dict[str, str]]:\n    \"\"\"极致精简的异步聊天函数，带历史记录。\"\"\"\n    history: List[Dict[str, str]] = [{\"role\": \"system\", \"content\": initial_message}] if initial_message else []\n    while True:\n        user_input = await asyncio.to_thread(input, \"你: \")\n        if user_input.lower() == 'exit': break\n        history.append({\"role\": \"user\", \"content\": user_input})\n        prompt = \"\".join(f\"{msg['role'].capitalize()}: {msg['content']}\\n\" for msg in history) + \"助手: \"\n        response = await adapter.aproduct(prompt)\n        history.append({\"role\": \"assistant\", \"content\": response})\n    return history\n\n# 示例使用\nif __name__ == \"__main__\":\n    adapter_key = os.getenv(\"BIANXIE_API_KEY\", \"sk-placeholder\")\n    adapter = BianXieAdapter(api_key=adapter_key)\n    final_chat_history = asyncio.run(ultra_simple_chat(adapter, \"你是一个简洁高效的AI助手。\"))\n    for msg in final_chat_history: print(f\"{msg['role'].capitalize()}: {msg['content']}\")",
  "解释": "根据需求，生成了名为 `ultra_simple_chat` 的异步函数，实现了带历史记录的极简聊天功能。它将所有用户和助手消息扁平化为单一 prompt 传递给 `adapter.aproduct`，并记录响应。代码严格遵循了极简、函数式、无错误处理和无额外注释的风格。"
}
```

**重要提示：**
*   你输出的“生成的核心代码”应是完整的、可直接运行的Python代码块，包含必要的导入和可能的 `if __name__ == "__main__":` 示例使用。
*   “解释”部分应简洁明了，概括代码的主要功能以及如何符合用户的风格和要求。
*   如果需求与提供的“代码头”或“代码使用demo”不完全匹配，请基于“需求”和通用Python实践生成代码，并在解释中指出任何潜在的不一致。


'''

import ast


def strip_function_bodies(file_path: str) -> str:
    """
    从 Python 文件中剥离函数内容，只保留函数定义和注释。

    Args:
        file_path (str): 要处理的 Python 文件的路径。

    Returns:
        str: 包含剥离函数内容后的代码字符串。
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    stripped_lines = []
    current_indent = 0
    in_function_body = False
    function_start_line = -1

    # 遍历原始代码的每一行，以保留非函数部分和正确处理缩进
    # ast 模块可以用来生成新的 AST，但要精确地保留原始格式，
    # 逐行处理并利用 ast 节点的信息是更可靠的方法。

    # 首先，我们收集所有函数和类的方法的 AST 节点，以及它们的起始行号和结束行号
    # 这样可以方便地判断一行是否属于某个函数体
    function_nodes = []
    class_nodes = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_nodes.append(node)
        elif isinstance(node, ast.ClassDef):
            class_nodes.append(node)

    # 将源代码按行分割
    lines = source_code.splitlines(keepends=True) # keepends=True 保留行尾换行符

    # 用于追踪当前正在处理的 AST 节点
    current_class_node = None

    for i, line in enumerate(lines):
        line_num = i + 1 # ast 的行号从 1 开始

        # 检查当前行是否在某个函数体内部
        is_in_function_body_to_strip = False
        for func_node in function_nodes:
            # 一个粗略的判断：如果行号在函数定义的第一个非 docstring 语句之后，
            # 并且在函数体的最后一行之前，则认为在函数体内部。
            # 这里需要更精确的判断，因为我们只需要保留签名和 docstring
            if func_node.lineno <= line_num <= func_node.end_lineno:
                # 获取函数签名的结束行 (通常是 def 行的末尾)
                # 或者如果有装饰器，则装饰器的最后一行
                signature_end_line = func_node.lineno

                # 处理装饰器
                if func_node.decorator_list:
                    signature_end_line = max(signature_end_line, func_node.decorator_list[-1].end_lineno)

                # 处理参数列表，特别是多行参数列表
                if hasattr(func_node, 'args') and func_node.args.args:
                    last_arg = func_node.args.args[-1]
                    signature_end_line = max(signature_end_line, last_arg.end_lineno)
                elif hasattr(func_node, 'args') and func_node.args.kwonlyargs:
                    last_arg = func_node.args.kwonlyargs[-1]
                    signature_end_line = max(signature_end_line, last_arg.end_lineno)
                elif hasattr(func_node, 'args') and func_node.args.vararg:
                    signature_end_line = max(signature_end_line, func_node.args.vararg.end_lineno)
                elif hasattr(func_node, 'args') and func_node.args.kwarg:
                    signature_end_line = max(signature_end_line, func_node.args.kwarg.end_lineno)

                # 如果有返回类型注释，也算作签名的一部分
                if func_node.returns:
                    signature_end_line = max(signature_end_line, func_node.returns.end_lineno)

                # 获取 docstring 的结束行
                docstring_end_line = signature_end_line
                docstring_node = ast.get_docstring(func_node, clean=False)
                if docstring_node:
                    # 使用 inspect.getdoc 获取实际的 docstring 字符串
                    # 并计算其行数，这比直接 ast.get_docstring 更准确地反映了原始代码的行数
                    # 因为 ast.get_docstring 返回的是处理后的字符串，可能丢失多行信息
                    # 更可靠的方法是找到 docstring 字符串在原始代码中的位置
                    # 我们可以通过查看函数体的第一个 AST 节点来判断
                    if func_node.body and isinstance(func_node.body[0], ast.Expr) and isinstance(func_node.body[0].value, ast.Constant) and isinstance(func_node.body[0].value.value, str):
                        docstring_expr_node = func_node.body[0]
                        docstring_end_line = docstring_expr_node.end_lineno

                # 如果当前行在签名或 docstring 之后，但在函数结束之前，则认为是函数体内容
                # 注意：如果函数体是空的 (pass)，那么 signature_end_line 可能是函数结束行
                if line_num > max(signature_end_line, docstring_end_line) and line_num <= func_node.end_lineno:
                    # 检查函数体是否只有 pass
                    has_only_pass = False
                    if len(func_node.body) == 1 and isinstance(func_node.body[0], ast.Pass):
                        has_only_pass = True

                    if not has_only_pass:
                        is_in_function_body_to_strip = True
                        break # 找到了，跳出内层循环

        if is_in_function_body_to_strip:
            continue # 跳过函数体内的行

        # 处理类定义
        for class_node in class_nodes:
            if class_node.lineno <= line_num <= class_node.end_lineno:
                current_class_node = class_node
                break
            current_class_node = None # 重置

        # 保留所有不在函数体内的行，以及函数签名和 docstring
        stripped_lines.append(line)

    return "".join(stripped_lines)





mcp = FastMCP("llmada")

main_path = "/Users/zhaoxuefeng/GitHub/llmada"

code_path = os.path.join(main_path,"src/llmada/core.py")
test_path = os.path.join(main_path,"tests/test_core.py")

_code = strip_function_bodies(code_path)
with open(test_path,'r') as f:
    demo = f.read()


@mcp.tool(description="根据需求编写对应的代码, 专门负责大模型相关的内容")
def write_code_with_llmada(demand: str):
    """
       Args:
         demand: 具体的需求.
    """
    bx = BianXieAdapter()
    inputs = {"代码头":_code,
          "demo":  demo,
          "需求": demand,
    }   

    input_json = json.dumps(inputs,ensure_ascii=False)
    result = bx.product(system_prompt + input_json)

    res = json.loads(extract_(result))

    # code_ = res.get("生成的核心代码")
    return res


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
