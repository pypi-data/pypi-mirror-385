"""AI处理和工具调用相关的辅助函数

此模块提供了与AI处理和工具调用相关的辅助函数，用于支持交互式聊天应用。
"""

import asyncio
import json
import re
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

from ketacli.sdk.ai.client import AIClient
from ketacli.sdk.ai.function_call import function_registry, function_executor
from ketacli.sdk.ai.tool_output_compressor import compress_if_large
from textual.widget import Widget

from ketacli.sdk.textual_chart.utils.chat_stream import safe_notify

# 设置日志记录器
logger = logging.getLogger("ketacli.textual.ai_helpers")

async def assess_planning_readiness(ai_client: AIClient, user_text: str) -> dict:
    """评估是否应立即生成计划，或先进行信息发现。
    
    分析用户输入文本，判断是否有足够信息直接生成执行计划，或需要先进行信息收集。
    使用AI模型进行判断，失败时回退到基于关键词的启发式判断。
    
    Args:
        ai_client: AI客户端实例
        user_text: 用户输入的文本
        
    Returns:
        dict: 包含plan_now(是否立即规划)和reason(原因)的字典
    """
    try:
        prompt = (
            "你是任务规划时机判断助手。\n"
            "判断当前用户需求是否需要先进行信息发现（例如列出服务/实体）再生成详细计划。\n"
            "若当前信息不足以明确拆分任务，请返回 plan_now=false。\n"
            "仅输出JSON且不含Markdown代码块，格式："
            "{\"plan_now\": true|false, \"reason\": \"string\"}。\n"
            "判断标准举例：包含'每个/各个/所有/逐个/分别'且未枚举对象时，多为先发现。\n"
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text},
        ]
        resp = await ai_client.chat_async(messages, temperature=0.0)
        raw = (resp.content or "").strip()
        data = json.loads(raw)
        plan_now = bool(data.get("plan_now"))
        reason = str(data.get("reason") or "")
        return {"plan_now": plan_now, "reason": reason}
    except Exception:
        # 启发式回退：检测典型词汇与未明确枚举
        text = (user_text or "").strip()
        lowered = text.lower()
        hints = ["各个", "每个", "所有", "逐个", "分别", "每台", "每项", "每个服务", "各服务"]
        has_plural_hint = any(h in text for h in hints)
        # 简单枚举检测：是否出现多个逗号分隔项
        enumerated = bool(re.search(r"[，,]\s*\S+[，,]", text))
        plan_now = not has_plural_hint or enumerated
        reason = "启发式判断：{}".format("已枚举或无复数提示" if plan_now else "疑似需要先列出实体")
        return {"plan_now": plan_now, "reason": reason}

async def plan_task_steps(ai_client: AIClient, user_text: str, enabled_tools: set = None, conversation_history: List[Dict] = None) -> list:
    """使用AI判断复杂度并生成任务步骤列表。
    
    根据用户输入的文本，使用AI模型判断任务复杂度并将其拆分为可执行的步骤列表。
    如果任务简单，则返回单个步骤；如果任务复杂，则拆分为多个步骤。
    
    Args:
        ai_client: AI客户端实例
        user_text: 用户输入的文本
        enabled_tools: 已启用的工具集合
        
    Returns:
        list: 任务步骤文本列表，解析失败时返回包含原始需求的单步骤列表
    """
    logger.debug("使用AI判断复杂度并生成任务步骤列表")
    try:
        prompt = (
            "你是任务规划助手。判断用户需求复杂度：简单则仅一个步骤；复杂则拆分多个步骤。"
            "只输出JSON且不包含Markdown代码块。格式为："
            "{\"complexity\": \"low|high\", \"steps\": [\"步骤文本\"]}。"
            "步骤文本应简洁、可执行、无编号，仅保留文字本身。"
            "注意：当前是在规划任务，返回时不要返回任何上述json之外的字符，例如标记字段[PLAY_READY]等均不能携带。"
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"可用工具：{', '.join(enabled_tools or []) or '无'}\n用户需求：{user_text}"}
        ]
        
        # 附加最近的工具上下文摘要以提升规划准确性
        try:
            ctx_snippets = []
            hist = list(conversation_history or [])
            count = 0
            for idx in range(len(hist)-1, -1, -1):
                msg = hist[idx]
                if msg.get("role") == "tool":
                    txt = (msg.get("content") or "").strip()
                    if txt:
                        ctx_snippets.append(txt[:600])
                        count += 1
                        if count >= 3:
                            break
            if ctx_snippets:
                ctx_text = "\n\n".join(reversed(ctx_snippets))
                messages.append({
                    "role": "user",
                    "content": f"[上下文工具结果摘要]\n{ctx_text}"
                })
        except Exception:
            pass
            
        resp = await ai_client.chat_async(messages, temperature=0.2)
        raw = (resp.content or "").strip()
        # 去除可能的代码块包裹
        raw = re.sub(r"^```json\s*|\s*```$", "", raw)
        # 先移除可能附带的流程标记，避免影响JSON解析
        raw = re.sub(r"\[(?:PLAN_READY|PLAY_READY|STEP_DONE|STEP_CONTINUE|STEP_REQUIRE_USER|step_done|step_continue|step_require_user)\]", "", raw)
        # 兼容 JSON 与 Python 字面量，并容忍回复中夹杂文字
        steps = []
        try:
            import ast
            # 总是尝试提取最可能的JSON对象子串，避免尾部混入标记
            candidate = raw
            m = re.search(r"\{[\s\S]*\}", raw)
            if m:
                candidate = m.group(0)
            data = None
            try:
                data = json.loads(candidate)
            except Exception:
                try:
                    data = ast.literal_eval(candidate)
                except Exception:
                    data = None
            if isinstance(data, dict):
                raw_steps = data.get("steps")
                if isinstance(raw_steps, list):
                    # 支持列表元素为字符串或对象
                    normalized = []
                    for item in raw_steps:
                        if isinstance(item, str):
                            txt = item.strip()
                            if txt:
                                normalized.append(txt)
                        elif isinstance(item, dict):
                            for key in ("step", "text", "description"):
                                v = item.get(key)
                                if isinstance(v, str) and v.strip():
                                    normalized.append(v.strip())
                                    break
                    steps = normalized
                elif isinstance(raw_steps, str):
                    # 如果 steps 是字符串，则按行拆分并去除编号/符号
                    lines = [ln.strip() for ln in raw_steps.splitlines() if ln.strip()]
                    normalized = []
                    for ln in lines:
                        ln = re.sub(r"^\s*[\-\*\u2022]+\s*", "", ln)  # 项目符号
                        ln = re.sub(r"^\s*\d+[\.\)]\s*", "", ln)     # 编号
                        if ln:
                            normalized.append(ln)
                    steps = normalized
                else:
                    steps = []
            else:
                raise ValueError("planning json parse failed")
        except Exception:
            # 文本fallback：提取行作为步骤，并忽略明显的JSON行
            logger.warning(f"解析AI响应失败，使用文本fallback。原始响应：{raw}")
            lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
            cleaned = []
            for ln in lines:
                # 跳过明显的JSON/代码块/元数据行
                if re.match(r'^\s*(\{|\}|\[|\]|```|"?complexity"?\s*:|"?steps"?\s*:)', ln):
                    continue
                ln2 = re.sub(r"^\s*[\-\*\u2022]+\s*", "", ln)
                ln2 = re.sub(r"^\s*\d+[\.\)]\s*", "", ln2)
                if ln2:
                    cleaned.append(ln2)
            steps = cleaned
        # 至少返回一个步骤
        if not steps:
            steps = [user_text.strip()]
        # 限制最多10步，避免过长
        logger.debug(f"生成任务步骤列表: {steps}。")
        return steps[:10]
    except Exception:
        logger.error(f"生成任务步骤失败。原始需求：{user_text}")
        return [user_text.strip()]

def get_enabled_tools_openai_format(enabled_tools: set) -> list:
    """获取已启用工具的OpenAI格式定义列表
    
    从全局工具注册表中筛选出已启用的工具，并返回其OpenAI格式定义。
    
    Args:
        enabled_tools: 已启用工具的集合
        
    Returns:
        list: 已启用工具的OpenAI格式定义列表，如果出错则返回空列表
    """
    try:
        all_tools = function_registry.get_openai_tools_format() or []
        if not enabled_tools:
            return []
        filtered = []
        for t in all_tools:
            fn = (t or {}).get("function", {})
            nm = fn.get("name")
            if nm and nm in enabled_tools:
                filtered.append(t)
        return filtered
    except Exception:
        return []

def requires_user_confirmation(text: str) -> bool:
    """判断AI响应是否需要用户确认或输入
    
    分析AI响应文本，判断是否包含需要用户确认或输入的提示。
    
    Args:
        text: AI响应文本
        
    Returns:
        bool: 是否需要用户确认或输入
    """
    if not text:
        return False
    
    # 检查是否包含明确的用户输入请求
    input_patterns = [
        r"请输入",
        r"请提供",
        r"需要你[的]?(输入|确认)",
        r"请选择",
        r"你想要[的]?(\w+)吗",
        r"你需要[的]?(\w+)吗",
        r"你希望[的]?(\w+)吗",
        r"是否继续",
        r"是否需要",
        r"是否要",
        r"你确定",
        r"请确认",
    ]
    
    for pattern in input_patterns:
        if re.search(pattern, text):
            return True
    
    # 检查是否包含问句
    question_patterns = [
        r"\?$",
        r"？$",
        r"请问",
        r"如何选择",
        r"怎么选择",
        r"要选择哪个",
    ]
    
    for pattern in question_patterns:
        if re.search(pattern, text):
            return True
    
    return False

async def process_tool_calls(
    tool_calls: List[Dict], 
    chat_history_widget=None, 
    add_to_base_messages: bool = True
) -> List[Dict]:
    """处理工具调用并展示结果
    
    执行工具调用，并将结果添加到聊天历史和基础消息列表中。
    
    Args:
        tool_calls: 工具调用列表
        chat_history_widget: 聊天历史控件
        add_to_base_messages: 是否将工具结果添加到基础消息列表
        
    Returns:
        List[Dict]: 工具结果消息列表，可添加到基础消息中
    """
    tool_messages = []
    
    if not tool_calls:
        return tool_messages
    
    tool_results = await function_executor.execute_from_tool_calls_async(tool_calls)
    
    for i, tool_result in enumerate(tool_results):
        tool_call = tool_calls[i]
        fn = tool_call.get("function", {})
        func_name = fn.get("name")
        func_args = fn.get("arguments", "{}")
        
        if tool_result.get("success"):
            val = tool_result.get("result", "")
            if isinstance(val, (dict, list)):
                try:
                    result_str = json.dumps(val, ensure_ascii=False)
                except Exception:
                    result_str = str(val)
                result_obj_for_ui = val if isinstance(val, dict) else None
            elif isinstance(val, Widget):
                result_str = "(图表可视化结果)"
                result_obj_for_ui = val
            else:
                result_str = str(val) if val is not None else ""
                result_obj_for_ui = None
                
            if not result_str.strip():
                result_str = "(结果为空)"
                
            compressed_text, was_compressed = compress_if_large(result_str, threshold=8000)
            
            if chat_history_widget:
                chat_history_widget.add_tool_call(
                    func_name,
                    func_args,
                    compressed_text if was_compressed else result_str,
                    True,
                    result_obj=result_obj_for_ui,
                )
                
            if add_to_base_messages:
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                    "content": compressed_text if was_compressed else result_str
                }
                tool_messages.append(tool_msg)
        else:
            err = tool_result.get("error", "执行失败")
            
            if chat_history_widget:
                chat_history_widget.add_tool_call(func_name, func_args, err, False)
                
            if add_to_base_messages:
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                    "content": err or ""
                }
                tool_messages.append(tool_msg)
                
    return tool_messages


def needs_tool_call(content: str) -> bool:
    """检测是否需要工具调用（增强版）
    
    目标：减少漏判，让常见数据检索/列表类请求自动走工具通道。
    """
    try:
        text = (content or "").strip()
    except Exception:
        text = ""
    if not text:
        return False

    # 基础关键字（中英文）
    base_keywords = [
        "搜索", "查询", "获取", "执行", "调用", "运行", "查看", "看下", "列出", "列表", "统计", "top", "limit",
        "search", "query", "get", "execute", "call", "run", "smart_search"
    ]

    # 常见模式：前N条、最近N条、limit N
    import re
    patterns = [
        r"前\s*\d+\s*条",
        r"最近\s*\d+\s*条",
        r"limit\s*\d+",
    ]

    text_lower = text.lower()
    if any(k in text for k in base_keywords) or any(re.search(p, text_lower) for p in patterns):
        return True

    # 涉及明显数据域词汇时也倾向使用工具
    domain_hints = ["事件", "日志", "记录", "仓库", "repo", "数据", "表", "查询语句"]
    if any(h in text for h in domain_hints):
        return True

    return False

# -------------------- 新增：通知过滤与单次工具执行 --------------------

def filter_notification(message: Any, kwargs: Dict[str, Any], debug_markers: Tuple[str, ...] = ()) -> Tuple[bool, Dict[str, Any]]:
    """过滤通知，仅保留重要信息并屏蔽明显调试噪音。
    
    返回值：
    - should_send: 是否应发送通知
    - prepared_kwargs: 传递给 notify 的参数（确保 markup=False，限制长度等）
    """
    try:
        text = str(message or "")
    except Exception:
        text = ""

    # 屏蔽明显的调试/噪音标记
    try:
        for mark in (debug_markers or ()):  # e.g. "DEBUG", emojis
            if mark and mark in text:
                return False, {}
    except Exception:
        pass

    # 仅展示重要等级（error/warning/success）
    severity = (kwargs or {}).get("severity")
    important = {"error", "warning", "success"}
    if not severity or str(severity) not in important:
        # 无等级或非重要等级，默认不展示
        return False, {}

    # 规范化参数：禁用富文本，限制超长消息
    prepared = dict(kwargs or {})
    prepared.setdefault("markup", False)
    try:
        if len(text) > 2000:
            text = text[:2000] + " …"
    except Exception:
        pass
    # 保留原 severity/timeout 等
    return True, prepared

async def execute_tool_call(
    tool_call: Dict[str, Any],
    tools: List[Dict[str, Any]],
    chat_history_widget,
    messages: List[Dict[str, Any]],
    *,
    tool_executor=None,
    notifier=None,
) -> Dict[str, Any]:
    """执行单个工具调用，更新UI与消息历史，并返回结果。
    
    参数：
    - tool_call: 单个OpenAI风格的工具调用对象
    - tools: 提供给模型的工具定义列表（此处仅用于上下文，不强制校验）
    - chat_history_widget: 聊天历史控件（用于展示工具执行结果）
    - messages: 对话消息列表（将在末尾追加 tool 消息）
    - tool_executor: 可选的执行器（无则使用全局 function_executor）
    - notifier: 可选的通知函数（如 app.notify）
    
    返回：
    - dict，包含 "tool_message" 与 "result" 两项，便于上层记录
    """
    try:
        fn = (tool_call or {}).get("function", {})
        func_name = fn.get("name")
        func_args = fn.get("arguments", "{}")
        if not func_name:
            raise ValueError("缺少函数名")

        # 执行工具调用（复用批量接口执行单项，保持一致的错误处理与超时策略）
        execu = tool_executor if tool_executor is not None else function_executor
        results = await execu.execute_from_tool_calls_async([tool_call])
        tool_result = results[0] if results else {"success": False, "error": "执行器未返回结果"}

        import json as _json
        if tool_result.get("success"):
            val = tool_result.get("result", "")
            if isinstance(val, Widget):
                result_str = "(图表可视化结果)"
                result_obj_for_ui = val
            elif isinstance(val, (dict, list)):
                try:
                    result_str = _json.dumps(val, ensure_ascii=False)
                except Exception:
                    result_str = str(val)
                result_obj_for_ui = val if isinstance(val, dict) else None
            else:
                result_str = str(val) if val is not None else ""
                result_obj_for_ui = None
            if not result_str.strip():
                result_str = "(结果为空)"

            compressed_text, was_compressed = compress_if_large(result_str, threshold=8000)
            if chat_history_widget:
                chat_history_widget.add_tool_call(
                    func_name,
                    func_args,
                    compressed_text if was_compressed else result_str,
                    True,
                    result_obj=result_obj_for_ui,
                )
            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                "content": compressed_text if was_compressed else result_str,
            }
            messages.append(tool_message)
            try:
                if notifier:
                    notifier(f"✅ 工具 {func_name} 执行成功", timeout=2)
            except Exception:
                pass
        else:
            error_msg = tool_result.get("error", "执行失败") or "执行失败"
            if not error_msg.strip():
                error_msg = "(错误信息为空)"
            if chat_history_widget:
                chat_history_widget.add_tool_call(func_name, func_args, error_msg, False)
            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                "content": error_msg,
            }
            messages.append(tool_message)
            try:
                if notifier:
                    notifier(f"❌ 工具 {func_name} 执行失败：{error_msg}", severity="warning", timeout=4, markup=False)
            except Exception:
                pass

        return {"tool_message": tool_message, "result": tool_result}
    except Exception as e:
        # 捕获异常也作为失败的工具消息写入，避免对话断裂
        try:
            fn = (tool_call or {}).get("function", {})
            func_name = fn.get("name") or "unknown"
            func_args = fn.get("arguments", "{}")
        except Exception:
            func_name, func_args = "unknown", "{}"
        err_text = f"工具执行异常: {e}"
        if chat_history_widget:
            try:
                chat_history_widget.add_tool_call(func_name, func_args, err_text, False)
            except Exception:
                pass
        tool_message = {
            "role": "tool",
            "tool_call_id": (tool_call or {}).get("id", f"call_{func_name}"),
            "content": err_text,
        }
        try:
            messages.append(tool_message)
        except Exception:
            pass
        try:
            if notifier:
                notifier(f"❌ 工具 {func_name} 执行异常：{e}", severity="warning", timeout=4, markup=False)
        except Exception:
            pass
        return {"tool_message": tool_message, "result": {"success": False, "error": err_text}}