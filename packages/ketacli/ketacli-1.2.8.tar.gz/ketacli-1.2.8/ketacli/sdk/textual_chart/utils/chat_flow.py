from typing import List, Dict, Any

from .ai_helpers import get_enabled_tools_openai_format, process_tool_calls, requires_user_confirmation
from ..widgets import ChatHistoryWidget, ModelSelectorWidget, ChatInputWidget

# 统一标记常量与判定助手
DONE_MARKERS = {"[STEP_DONE]", "[step_done]", "步骤完成", "完成该步骤", "已完成该步骤"}
CONTINUE_MARKERS = {"[STEP_CONTINUE]", "[step_continue]", "继续下一步", "需要继续", "继续执行"}
PLAN_READY_MARKERS = {"[PLAN_READY]", "[PLAY_READY]"}
REQUIRE_USER_MARKERS = {"[STEP_REQUIRE_USER]", "[step_require_user]"}
# 新增：会话结束标记
SESSION_DONE_MARKERS = {"[SESSION_DONE]", "[session_done]", "会话结束", "结束会话"}

def safe_notify(app, message: str, severity: str = None, timeout: int = None, **kwargs) -> None:
    """安全通知包装：统一捕获通知异常，减少视觉噪音。"""
    try:
        notify = getattr(app, "notify", None)
        if callable(notify):
            if severity is not None:
                kwargs["severity"] = severity
            if timeout is not None:
                kwargs["timeout"] = timeout
            notify(message, **kwargs)
    except Exception:
        pass


def has_marker(text: str, markers: set) -> bool:
    try:
        lower = (text or "").lower()
    except Exception:
        lower = ""
    if not lower:
        return False
    return any((m or "").lower() in lower for m in (markers or set()))

# 新增：是否结束会话判定
def should_end_session(text: str, has_tool_calls: bool = False) -> bool:
    """判断是否应结束当前会话：
    - 若包含会话结束标记，直接结束；
    - 若存在工具调用，优先执行工具，不以 STEP_DONE 结束会话；
    - 若明确完成且未带继续标记，则结束会话。
    """
    try:
        if has_marker(text, SESSION_DONE_MARKERS):
            return True
        return False
    except Exception:
        return False

def should_pause_for_user(text: str) -> bool:
    return bool(
        requires_user_confirmation(text)
        or has_marker(text, REQUIRE_USER_MARKERS)
    )


def should_force_tool_call(app: Any, messages: List[Dict[str, Any]], user_text: str) -> bool:
    """统一的工具分支强制判定：
    - 若用户文本含“继续”语义标记，则强制走工具分支；
    - 若最近历史中存在 tool 角色消息（表示工具上下文仍在进行），也进入工具分支；
    - 若最近 assistant/user/system 文本出现继续语义，也进入工具分支。
    """
    try:
        if has_marker(user_text, CONTINUE_MARKERS):
            return True
        recent = messages[-6:] if messages else []
        for m in recent:
            if (m or {}).get("role") == "tool":
                return True
        for m in messages[-3:] if messages else []:
            if (m or {}).get("role") in ("assistant", "user", "system"):
                if has_marker((m or {}).get("content") or "", CONTINUE_MARKERS):
                    return True
    except Exception:
        return False
    return False


async def execute_task_steps(app: Any, steps: List[str], original_user_text: str) -> None:
    """执行任务步骤的通用流程，支持工具调用与总结标记。

    参数:
        app: 携带 UI/状态/AI 客户端的应用实例
        steps: 已规划的步骤列表
        original_user_text: 原始用户输入文本（用于上下文提示）
    """
    # 保护性检查
    if not getattr(app, "ai_client", None):
        safe_notify(app, "AI客户端未初始化", severity="error")
        return

    # 获取 UI 组件（容错）
    try:
        chat_history = app.query_one("#chat-history", None)
        model_selector = app.query_one("#model-selector", None)
    except Exception:
        chat_history = None
        model_selector = None

    # 根据选择的模型刷新客户端（容错）
    try:
        selected_model = model_selector.get_selected_model() if model_selector else None
        if selected_model:
            app.ai_client = app.ai_client.__class__(
                system_prompt=getattr(app.ai_client, "system_prompt", ""),
                model_name=selected_model,
            )
    except Exception:
        pass

    # 每步迭代上限（读取配置并限流）
    try:
        max_step_iterations = getattr(app.ai_client.model_config, "max_iterations", 8) or 8
        if not isinstance(max_step_iterations, int) or max_step_iterations <= 0:
            max_step_iterations = 8
        max_step_iterations = min(max_step_iterations, 8)
    except Exception:
        max_step_iterations = 8

    # 完成/继续标记（统一常量）
    done_markers = DONE_MARKERS
    continue_markers = CONTINUE_MARKERS

    # 获取工具列表（容错）
    try:
        tools = get_enabled_tools_openai_format(getattr(app, "enabled_tools", {}))
    except Exception:
        tools = []

    # 逐步执行
    for idx, step in enumerate(steps, start=1):
        try:
            if chat_history:
                chat_history.add_message("assistant", f"▶️ 开始执行第 {idx} 步：{step}")

            # 基础消息（含严格标记提示）
            base_messages: List[Dict[str, Any]] = list(getattr(app, "conversation_history", []))
            base_messages.append({
                "role": "user",
                "content": (
                    f"用户任务：{original_user_text}\n"
                    f"请严格执行以下步骤（第 {idx} 步）：\n{step}\n"
                    f"在结尾显式追加标签：\n"
                    f"当此步骤(\"{step}\")明确完成时，追加标签 [STEP_DONE]；否则追加标签 [STEP_CONTINUE]。\n"
                    f"当需要用户进行确认或者补全信息时，追加标签 [STEP_REQUIRE_USER]。\n"
                    f"当此任务(\"{original_user_text}\")明确完成时，追加标签 [SESSION_DONE]。\n"
                ),
            })

            # 步内迭代
            for it in range(1, max_step_iterations + 1):
                # 助手响应（含工具）
                try:
                    response = await app.ai_client.chat_with_tools_async(
                        messages=base_messages,
                        tools=tools,
                        tool_choice="auto",
                    )
                except Exception as e:
                    if chat_history:
                        chat_history.add_message("assistant", f"❌ 工具阶段出错：{e}")
                    break

                assistant_msg = getattr(response, "content", "")
                tool_calls = getattr(response, "tool_calls", []) or []
 
                if assistant_msg:
                    if chat_history:
                        chat_history.add_message("assistant", assistant_msg)
                    base_messages.append({"role": "assistant", "content": assistant_msg})
 
                # 过滤仅启用的工具调用
                enabled_attr = getattr(app, "enabled_tools", None)
                if isinstance(enabled_attr, dict):
                    enabled_names = set(enabled_attr.keys())
                elif isinstance(enabled_attr, (set, list, tuple)):
                    enabled_names = set(enabled_attr)
                else:
                    enabled_names = set()
                filtered_tool_calls = [
                    tc for tc in tool_calls if tc.get("function", {}).get("name") in enabled_names
                ]
 
                # 确保按 OpenAI 规范：若存在工具调用，前置 assistant 消息必须携带 tool_calls
                if filtered_tool_calls:
                    if base_messages and (base_messages[-1].get("role") == "assistant"):
                        # 将最近的 assistant 消息补充上 tool_calls
                        base_messages[-1]["tool_calls"] = filtered_tool_calls
                        # 若无文本内容，保持为空字符串即可
                        if "content" not in base_messages[-1]:
                            base_messages[-1]["content"] = assistant_msg or ""
                    else:
                        base_messages.append({
                            "role": "assistant",
                            "content": assistant_msg or "",
                            "tool_calls": filtered_tool_calls,
                        })

                # 执行工具调用并附加消息
                try:
                    tool_messages = await process_tool_calls(
                        filtered_tool_calls,
                        chat_history_widget=chat_history,
                        add_to_base_messages=True,
                    )
                    base_messages.extend(tool_messages or [])
                except Exception as e:
                    if chat_history:
                        chat_history.add_message("assistant", f"⚠️ 处理工具调用失败：{e}")

                # 总结与完成判定
                try:
                    summary = await app.ai_client.chat_async(base_messages)
                except Exception as e:
                    if chat_history:
                        chat_history.add_message("assistant", f"❌ 总结阶段出错：{e}")
                    break

                summary_text = getattr(summary, "content", "") or ""
                # 若需要用户确认/补全，确保追加标记
                if requires_user_confirmation(summary_text) and not has_marker(summary_text, REQUIRE_USER_MARKERS):
                    sep = "\n\n" if not summary_text.endswith("\n") else "\n"
                    summary_text = summary_text + sep + "[STEP_REQUIRE_USER]"
                if chat_history and summary_text:
                    chat_history.add_message("assistant", summary_text)
                base_messages.append({"role": "assistant", "content": summary_text})

                # 新增：需要用户确认时暂停并返回，不继续后续步骤
                if should_pause_for_user(summary_text):
                    safe_notify(app, "⏸️ 暂停：等待你的输入或确认后继续。", timeout=4)
                    try:
                        app.conversation_history = base_messages
                    except Exception:
                        pass
                    return
                
                if should_end_session(summary_text):
                    safe_notify(app, "✅ 会话完成", timeout=4)
                    return

                done_hit = has_marker(summary_text, DONE_MARKERS)
                cont_hit = has_marker(summary_text, CONTINUE_MARKERS)

                if done_hit and not cont_hit:
                    if chat_history:
                        chat_history.add_message("assistant", f"✅ 第 {idx} 步`({step})`完成")
                    break
                else:
                    # 继续迭代
                    if chat_history:
                        chat_history.add_message("assistant", f"↻ 第 {idx} 步`({step})`继续迭代（{it}/{max_step_iterations}）")
                    continue

            # 更新对话历史
            try:
                app.conversation_history = base_messages
            except Exception:
                pass

        except Exception as e:
            if chat_history:
                chat_history.add_message("assistant", f"❌ 执行第 {idx} 步失败：{e}")
            continue

    # 完成提示
    safe_notify(app, f"🧭 {len(steps)} 个步骤执行结束", timeout=3)


async def process_ai_response(app: Any, user_message: str, streaming: bool = None) -> None:
    """通用的 AI 响应处理流程：准备上下文、规划步骤、工具迭代与收尾。"""
    if not getattr(app, "ai_client", None):
        safe_notify(app, "AI客户端未初始化", severity="error")
        return

    # 若未显式传入，则从应用或模型配置读取，默认启用流式
    if streaming is None:
        try:
            streaming = getattr(app, "enable_streaming", None)
        except Exception:
            streaming = None
        if streaming is None:
            try:
                # 先读取直接字段
                streaming = bool(getattr(app.ai_client.model_config, "streaming", True))
                # 再尝试 extra_params 中的 streaming / enable_streaming / stream
                extra = getattr(app.ai_client.model_config, "extra_params", {}) or {}
                for key in ("streaming", "enable_streaming", "stream"):
                    if key in extra:
                        streaming = bool(extra.get(key))
                        break
            except Exception:
                safe_notify(app, "读取流式配置失败，默认启用流式", severity="warning")
                streaming = True

    # 标记进程进行中
    app._chat_in_progress = True
    try:
        chat_history = app.query_one("#chat-history", ChatHistoryWidget)
        model_selector = app.query_one("#model-selector", ModelSelectorWidget)
    except Exception:
        chat_history = None
        model_selector = None

    try:
        # 增强系统提示词
        try:
            app.ai_client.system_prompt = app._augment_system_prompt(app.ai_client.system_prompt)
        except Exception:
            pass

        # 准备消息
        messages = app._prepare_messages(user_message)

        # 自动任务规划
        try:
            readiness = await app._assess_planning_readiness(user_message)
            if readiness.get("plan_now"):
                steps = await app._plan_task_steps(user_message)
            else:
                steps = [user_message]
                try:
                    safe_notify(app, "🧭 先进行信息发现，稍后再生成详细计划", timeout=3)
                except Exception:
                    pass
        except Exception:
            safe_notify(app, f"生成任务步骤失败。原始需求：{user_message}", severity="error")
            steps = [user_message]

        # 若有多步，先展示规划并委托步骤执行
        if len(steps) > 0:
            try:
                plan_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
                if chat_history:
                    chat_history.add_message("assistant", f"🧭 已拆分为{len(steps)}个步骤：\n{plan_text}")
            except Exception:
                pass
            await execute_task_steps(app, steps, user_message)
            return

        # 规范化工具消息顺序
        messages, removed_assistant, removed_tool = app._enforce_openai_tool_sequence(messages)
        if removed_assistant or removed_tool:
            safe_notify(
                app,
                f"🧹 已规范化工具消息：移除不完整assistant {removed_assistant} 条/孤立tool {removed_tool} 条",
                severity="warning",
                timeout=4,
            )

        # 获取可用工具
        tools = app._get_enabled_tools_openai_format()
        try:
            provider = getattr(app.ai_client.model_config, "provider", "")
            current_model = app.ai_client.get_current_model() if hasattr(app.ai_client, "get_current_model") else ""
            safe_notify(app, f"🔧 当前模型: {current_model} / 提供方: {provider}，可用工具: {len(tools)}", timeout=3)
            if should_force_tool_call(app, messages, user_message):
                safe_notify(app, "➡️ 已因‘继续’与历史工具调用，强制走工具分支", timeout=4)
        except Exception:
            safe_notify(app, "🔧 获取可用工具失败，默认使用20次迭代", severity="warning", timeout=3)

        # 迭代上限（用于流控信息展示）
        try:
            max_iterations = getattr(app.ai_client.model_config, "max_iterations", 20) or 20
            if not isinstance(max_iterations, int) or max_iterations <= 0:
                max_iterations = 20
        except Exception:
            max_iterations = 20

        # 运行工具迭代（委托到公共实现）
        result = await run_tool_iterations(app, messages, tools, user_message, streaming=streaming)
        messages = result.get("messages", messages)
        app.conversation_history = messages
        return

    except Exception as e:
        try:
            if chat_history:
                chat_history.add_message("assistant", f"❌ 处理请求时出错: {str(e)}")
        except Exception:
            pass
    finally:
        app._chat_in_progress = False
        app._current_ai_task = None
        try:
            chat_input = app.query_one("#chat-input", ChatInputWidget)
            chat_input.set_loading(False)
            chat_input.set_processing(False)
        except Exception:
            pass
        # 自动保存会话
        try:
            app._save_current_session()
        except Exception:
            pass


async def filter_and_deduplicate_tool_calls(app, tool_calls: list, executed_tool_signatures: set) -> tuple:
    """过滤和去重工具调用，返回(过滤后的调用列表, 被忽略的未启用工具名列表)。"""
    filtered_tool_calls = []
    disabled_called_names = []
    try:
        enabled = set(getattr(app, "enabled_tools", set()) or set())
        # 只保留启用工具的调用
        filtered_tool_calls = [
            tc for tc in (tool_calls or [])
            if ((tc or {}).get("function", {}).get("name") in enabled)
        ]
        # 根据函数名+规范化参数做去重
        try:
            import json
            dedup = []
            for tc in filtered_tool_calls:
                fn = (tc or {}).get("function", {})
                nm = fn.get("name")
                args = fn.get("arguments", "{}")
                try:
                    if isinstance(args, (dict, list)):
                        args_norm = json.dumps(args, ensure_ascii=False, sort_keys=True)
                    else:
                        args_norm = str(args)
                except Exception:
                    args_norm = str(args)
                sig = f"{nm}:{args_norm}"
                if sig in executed_tool_signatures:
                    safe_notify(app, f"♻️ 跳过重复工具调用: {nm}", severity="warning", timeout=3)
                    continue
                executed_tool_signatures.add(sig)
                dedup.append(tc)
            filtered_tool_calls = dedup
        except Exception:
            pass
        # 收集未启用工具名
        try:
            disabled_called_names = [
                (tc or {}).get("function", {}).get("name")
                for tc in (tool_calls or [])
                if ((tc or {}).get("function", {}).get("name") not in enabled)
            ]
            if disabled_called_names:
                try:
                    preview = ", ".join([n for n in disabled_called_names if n][:6])
                    safe_notify(
                        app,
                        f"🚫 检测到未启用的工具调用已被忽略：{preview}",
                        severity="warning",
                        timeout=4,
                    )
                except Exception:
                    pass
        except Exception:
            pass
    except Exception:
        filtered_tool_calls = []
    return filtered_tool_calls, disabled_called_names


async def run_tool_iterations(app, messages: list, tools: list, user_message: str, streaming: bool = True) -> dict:
    """运行工具调用迭代（公共实现），支持流式/非流式两种模式。"""
    iteration = 0
    block_tool_retry_for_current_query = False
    executed_tool_signatures = set()

    # 迭代上限
    try:
        max_iterations = getattr(app.ai_client.model_config, "max_iterations", 20) or 20
        if not isinstance(max_iterations, int) or max_iterations <= 0:
            max_iterations = 20
    except Exception:
        max_iterations = 20

    # UI 组件
    try:
        from ..widgets import ChatHistoryWidget
        chat_history = app.query_one("#chat-history", ChatHistoryWidget)
    except Exception:
        chat_history = None
    streaming_widget = chat_history.start_streaming_message("assistant") if (chat_history and streaming) else None

    # 依赖函数（避免顶部改动，内部导入）
    from .chat_stream import process_tool_sequence, stream_and_process_response
    from ..token_calculator import calculate_token_stats
    from ketacli.sdk.ai.function_call import function_executor
    from ketacli.sdk.ai.tool_output_compressor import compress_if_large
    from textual.widget import Widget
    from .ai_helpers import plan_task_steps, requires_user_confirmation

    while iteration < max_iterations:
        iteration += 1
        safe_notify(app, f"➡️ 第{iteration}轮工具请求，上下文消息数: {len(messages)}", timeout=2)

        # 处理工具调用序列，规范化消息历史
        messages, ra, rt = await process_tool_sequence(app, messages)

        # 获取AI响应：根据模式选择流式或非流式
        if streaming:
            response, _ = await stream_and_process_response(app, messages, tools, streaming_widget)
        else:
            try:
                response = await app.ai_client.chat_with_tools_async(messages=messages, tools=tools)
            except Exception:
                # 回退到普通回答
                try:
                    response = await app.ai_client.chat_async(messages)
                except Exception:
                    class _EmptyResp:
                        content = ""
                        tool_calls = []
                    response = _EmptyResp()

        # 构造助手消息
        assistant_message = {"role": "assistant", "content": getattr(response, "content", "")}

        # 过滤与去重工具调用
        filtered_tool_calls, disabled_called_names = await filter_and_deduplicate_tool_calls(
            app, (getattr(response, "tool_calls", None) or []), executed_tool_signatures
        )

        # 处理禁用工具提示与空内容回退
        try:
            if disabled_called_names:
                try:
                    preview = ", ".join([n for n in disabled_called_names if n][:6])
                    guidance = (
                        f"⚠️ 检测到模型尝试调用未启用的工具：{preview}。该调用已被忽略。\n"
                        "请按 `T` 或 `Ctrl+T` 打开工具列表启用所需工具，或继续输入让我在不使用工具的情况下回答。"
                    )
                    existing = (assistant_message.get("content") or "")
                    if existing.strip():
                        sep = "\n\n" if not existing.endswith("\n") else "\n"
                        assistant_message["content"] = existing + sep + guidance
                    else:
                        assistant_message["content"] = guidance
                except Exception:
                    pass
            if (not filtered_tool_calls) and disabled_called_names and not (assistant_message.get("content") or "").strip():
                disabled_preview = ", ".join([n for n in disabled_called_names if n][:6])
                fallback_text = (
                    f"⚠️ 检测到模型尝试调用未启用的工具：{disabled_preview}。该调用已被忽略。\n"
                    "请按 `Ctrl+T` 打开工具列表启用所需工具，或继续输入让我在不使用工具的情况下回答。"
                )
                assistant_message["content"] = fallback_text
        except Exception:
            pass

        # 限制每轮只执行一个工具调用
        if filtered_tool_calls:
            try:
                filtered_tool_calls = filtered_tool_calls[:1]
                safe_notify(app, "🎯 为提升精准度：本轮仅执行1次工具调用并随后进行思考", severity="success", timeout=3)
            except Exception:
                pass
            assistant_message["tool_calls"] = filtered_tool_calls
            try:
                names = []
                for tc in filtered_tool_calls:
                    fn = (tc or {}).get("function", {})
                    nm = fn.get("name")
                    if nm:
                        names.append(nm)
                if names:
                    safe_notify(app, f"🛠️ 将执行工具: {', '.join(names[:5])}", timeout=3)
            except Exception:
                pass

        # 若需要用户确认/补全，确保追加标记
        try:
            cur = (assistant_message.get("content") or "")
            if requires_user_confirmation(cur) and not has_marker(cur, REQUIRE_USER_MARKERS):
                sep = "\n\n" if not cur.endswith("\n") else "\n"
                assistant_message["content"] = cur + sep + "[STEP_REQUIRE_USER]"
        except Exception:
            pass

        # 附加助手消息
        messages.append(assistant_message)

        # 显示助手消息（根据模式）
        try:
            assistant_content = (assistant_message.get("content") or "")
            if assistant_content.strip() and chat_history:
                if streaming:
                    message_added = chat_history.finish_streaming_message(assistant_content)
                    if not message_added:
                        assistant_msg_dict = {"role": "assistant", "content": assistant_content}
                        context_for_assistant = messages[:-1] if messages else []
                        assistant_token_stats = calculate_token_stats(
                            current_message=assistant_msg_dict,
                            context_messages=context_for_assistant,
                        )
                        chat_history.add_message("assistant", assistant_content, token_stats=assistant_token_stats)
                else:
                    assistant_msg_dict = {"role": "assistant", "content": assistant_content}
                    context_for_assistant = messages[:-1] if messages else []
                    assistant_token_stats = calculate_token_stats(
                        current_message=assistant_msg_dict,
                        context_messages=context_for_assistant,
                    )
                    chat_history.add_message("assistant", assistant_content, token_stats=assistant_token_stats)
            # 规划/确认早停判断
            try:
                if has_marker(assistant_content, PLAN_READY_MARKERS):
                    context_hint = ""
                    for idx in range(len(messages) - 2, -1, -1):
                        if messages[idx].get("role") == "tool":
                            ctx = (messages[idx].get("content") or "").strip()
                            if ctx:
                                context_hint = ctx[:800]
                                break
                    plan_input = assistant_content
                    if context_hint:
                        plan_input = f"{assistant_content}\n\n[已识别上下文摘要]\n{context_hint}"
                    steps = await plan_task_steps(plan_input)
                    if len(steps) > 1:
                        plan_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps)])
                        chat_history.add_message("assistant", f"🧭 已拆分为{len(steps)}个步骤：\n{plan_text}")
                        await execute_task_steps(app, steps, user_message)
                        return {"messages": messages, "stop": True}
            except Exception:
                pass
            try:
                if should_pause_for_user(assistant_content):
                    safe_notify(app, "⏸️ 暂停：等待你的输入或确认后继续。", timeout=4)
                    return {"messages": messages, "stop": True}
            except Exception:
                pass
            # 新增：会话结束或步骤完成早停
            try:
                if should_end_session(assistant_content, has_tool_calls=bool(filtered_tool_calls)):
                    safe_notify(app, "✅ 会话已结束，停止继续迭代。", timeout=4)
                    return {"messages": messages, "stop": True}
            except Exception:
                pass
        except Exception:
            pass

        # 执行工具或者结束
        if filtered_tool_calls:
            tool_results = await function_executor.execute_from_tool_calls_async(filtered_tool_calls)
            import json
            for i, tool_result in enumerate(tool_results):
                tool_call = filtered_tool_calls[i]
                func_data = tool_call.get("function", {})
                func_name = func_data.get("name")
                func_args = func_data.get("arguments", "{}")
                if tool_result.get("success"):
                    result_val = tool_result.get("result", "")
                    if isinstance(result_val, Widget):
                        result_str = "(图表可视化结果)"
                        result_obj_for_ui = result_val
                    elif isinstance(result_val, (dict, list)):
                        try:
                            result_str = json.dumps(result_val, ensure_ascii=False)
                        except Exception:
                            result_str = str(result_val)
                        result_obj_for_ui = result_val if isinstance(result_val, dict) else None
                    else:
                        result_str = str(result_val) if result_val is not None else ""
                        result_obj_for_ui = None
                    if not result_str.strip():
                        result_str = "(结果为空)"
                    compressed_text, was_compressed = compress_if_large(result_str, threshold=8000)
                    if chat_history:
                        chat_history.add_tool_call(
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
                        safe_notify(app, f"✅ 工具 {func_name} 执行成功", timeout=2)
                    except Exception:
                        pass
                else:
                    error_msg = tool_result.get("error", "执行失败")
                    if not (error_msg or "").strip():
                        error_msg = "(错误信息为空)"
                    if chat_history:
                        chat_history.add_tool_call(func_name, func_args, error_msg, False)
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", f"call_{func_name}"),
                        "content": error_msg or "",
                    }
                    messages.append(tool_message)
                    block_tool_retry_for_current_query = True
                    try:
                        safe_notify(app, f"❌ 工具 {func_name} 执行失败：{error_msg}", severity="warning", timeout=4, markup=False)
                    except Exception:
                        pass
            continue
        else:
            # 仅在流式模式下执行非流式回退尝试，避免重复
            if streaming:
                try:
                    import re
                    provider = getattr(app.ai_client.model_config, "provider", "")
                    current_model = app.ai_client.get_current_model() if hasattr(app.ai_client, "get_current_model") else ""
                    tools_names = []
                    for t in tools:
                        fn = (t or {}).get("function", {})
                        nm = fn.get("name")
                        if nm:
                            tools_names.append(nm)
                    markers = re.findall(r"<\|\s*tool_call_begin\s*\|>(.*?)<\|\s*tool_call_end\s*\|>", getattr(response, "content", "") or "", flags=re.DOTALL)
                    snippet = (getattr(response, "content", "") or "").strip().replace("\n", " ")[:300]
                    last_user = ""
                    for idx in range(len(messages) - 1, -1, -1):
                        if messages[idx].get("role") == "user":
                            last_user = (messages[idx].get("content") or "").strip().replace("\n", " ")[:120]
                            break
                    safe_notify(
                        app,
                        f"🧪 调试：模型未返回结构化工具调用 | 模型: {current_model}/{provider} | 工具数: {len(tools)} | 标记段: {len(markers)}",
                        severity="warning",
                        timeout=5,
                        markup=False,
                    )
                    if tools_names:
                        safe_notify(app, f"🧪 可用工具: {', '.join(tools_names[:6])}", timeout=4, markup=False)
                    if last_user:
                        safe_notify(app, f"🧪 最近用户输入片段: {last_user}", timeout=4, markup=False)
                    if snippet:
                        safe_notify(app, f"🧪 响应片段: {snippet}", timeout=5, markup=False)
                except Exception:
                    pass

                # 新增：非流式一次性回退尝试，尽量拿到结构化工具调用
                try:
                    fallback_resp = await app.ai_client.chat_with_tools_async(messages, tools=tools)
                    fallback_calls = getattr(fallback_resp, "tool_calls", []) or []
                except Exception:
                    fallback_calls = []
                if fallback_calls:
                    filtered_fallback_calls, _ = await filter_and_deduplicate_tool_calls(app, fallback_calls, executed_tool_signatures)
                    if filtered_fallback_calls:
                        safe_notify(app, "🔁 非流式回退获取到工具调用，继续执行", timeout=4)
                        assistant_message["tool_calls"] = filtered_fallback_calls[:1]
                        messages.append(assistant_message)
                        # 显示助手消息（与流式组件对齐）
                        try:
                            assistant_content = (assistant_message.get("content") or "")
                            if assistant_content.strip() and chat_history:
                                message_added = chat_history.finish_streaming_message(assistant_content)
                                if not message_added:
                                    assistant_msg_dict = {"role": "assistant", "content": assistant_content}
                                    context_for_assistant = messages[:-1] if messages else []
                                    assistant_token_stats = calculate_token_stats(
                                        current_message=assistant_msg_dict,
                                        context_messages=context_for_assistant,
                                    )
                                    chat_history.add_message("assistant", assistant_content, token_stats=assistant_token_stats)
                        except Exception:
                            pass
                        # 执行工具并将结果追加到消息
                        try:
                            tool_messages = await process_tool_calls(filtered_fallback_calls[:1], chat_history_widget=chat_history, add_to_base_messages=True)
                            messages.extend(tool_messages or [])
                        except Exception:
                            pass
                        continue
            # 若回退仍未拿到工具调用，则继续下一轮，让模型思考
            safe_notify(app, "⏭️ 未返回结构化工具调用，本轮继续下一轮尝试", timeout=4)
            continue

    if iteration >= max_iterations:
        safe_notify(app, f"⚠️ 工具执行次数已达到上限（{max_iterations}），已停止继续。", severity="warning", timeout=5)
        try:
            if chat_history:
                chat_history.add_message(
                    "assistant",
                    (
                        f"工具执行次数已达到上限（{max_iterations}）。"
                        "如需继续，请输入“继续”让我接着执行，"
                        "或按 Ctrl+T 打开工具列表启用/调整所需工具后再试。"
                    ),
                )
        except Exception:
            pass
    return {"messages": messages, "stop": False}