"""主应用类"""

import asyncio
from datetime import datetime
import os
import logging
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Button
from textual.worker import Worker
from textual import on

from .data_models import ChatSession, SessionManager
from .widgets import (
    ModelSelectorWidget, ChatHistoryWidget, ChatInputWidget, 
    CustomTextArea, ToolsListModal, SessionHistoryModal, ContextWindowModal,
    ModelConfigManagerWidget
)
from .widgets.config_widgets import ModelConfigModal
from .styles import CSS
from .context_manager import ContextManager, SessionContextManager
from .token_calculator import calculate_token_stats
from .utils.ai_helpers import (
    assess_planning_readiness,
    plan_task_steps,
    get_enabled_tools_openai_format,
    requires_user_confirmation,
    process_tool_calls
)
from .utils import needs_tool_call, execute_tool_call
from .utils.chat_flow import execute_task_steps, process_ai_response
from .utils.chat_stream import stream_chat_with_tools_async, stream_chat_async, stream_and_process_response, augment_system_prompt, sanitize_tool_messages, enforce_openai_tool_sequence, process_tool_sequence
from ketacli.sdk.ai.client import AIClient
from ketacli.sdk.ai.function_call import function_registry, function_executor
from ketacli.sdk.ai.tool_output_compressor import compress_if_large
from textual.widget import Widget

# 轻量日志：写入到仓库根目录的 log/textual_debug.log
logger = logging.getLogger("ketacli.textual")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        log_dir = os.path.join(base_dir, "log")
        os.makedirs(log_dir, exist_ok=True)
        fh = logging.FileHandler(os.path.join(log_dir, "textual_debug.log"))
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(fh)
    except Exception:
        # 若文件日志初始化失败，不影响运行
        pass


class InteractiveChatApp(App):
    """交互式聊天应用"""
    
    CSS = CSS
    
    BINDINGS = [
        ("q", "quit", "退出"),
        ("c", "clear_chat", "清空对话"),
        ("n", "clear_chat", "新会话"),
        ("t", "show_tools", "显示工具"),
        ("i", "focus_input", "聚焦输入框"),
        ("h", "show_session_history", "历史会话"),
        ("m", "show_model_config", "模型配置"),
        ("k", "show_context", "上下文"),
    ]
    
    def __init__(self, **kwargs):
        """初始化交互式聊天应用
        
        初始化应用状态，包括AI客户端、会话管理、上下文管理和工具配置等
        
        Args:
            **kwargs: 传递给父类App的参数
        """
        super().__init__(**kwargs)
        self.ai_client = None
        self.conversation_history = []
        self.session_manager = SessionManager()
        self.current_session = None
        self._chat_in_progress = False
        self._current_ai_task = None  # 当前AI响应任务
        
        # 是否启用流式输出（可通过模型配置或外部参数覆盖）
        self.enable_streaming = True
        
        # 上下文管理器
        self.context_manager = ContextManager()
        self.session_context_manager = SessionContextManager()

        # 工具启用状态：默认开启资源列出、日志/指标搜索、获取文档
        # 对应函数名：list_assets, list_queryable_assets, search_data_for_log, search_data_for_metric, get_docs
        self.enabled_tools = {
            "list_assets",
            "list_queryable",
            "search_data",
            "get_repo_fields",
            "get_docs",
        }
        
        # 通知过滤配置：仅展示重要信息（error/warning/success）
        self._important_severities = {"error", "warning", "success"}
        # 明显的调试/噪音标记，统一屏蔽
        self._debug_markers = ("DEBUG", "🧪", "🔧", "➡️", "🔗", "⚙️", "📩", "🛠️", "🧹", "🔁")

    def notify(self, message, **kwargs):
        """统一过滤通知（委托公共过滤逻辑），仅保留重要提示。"""
        try:
            from .utils import filter_notification
        except Exception:
            # 回退：若导入失败，仍直接调用父类
            if "markup" not in kwargs:
                kwargs['markup'] = False
            return super().notify(message, **kwargs)
        should_send, prepared = filter_notification(message, kwargs, getattr(self, "_debug_markers", ()))
        if not should_send:
            return
        return super().notify(message, **prepared)
        
    def compose(self) -> ComposeResult:
        """构建应用UI布局
        
        定义应用的界面结构，包括头部、聊天容器和底部组件
        
        Returns:
            ComposeResult: 包含UI组件的生成器结果
        """
        yield Header()
        
        with Container(classes="chat-container"):
            yield Static("🤖 AI智能对话助手", classes="chat-header")
            
            with Vertical(classes="chat-main"):
                yield ModelSelectorWidget(id="model-selector")
                yield ChatHistoryWidget(id="chat-history", classes="chat-history")
                yield ChatInputWidget(id="chat-input", classes="chat-input-container")
                
        yield Footer()
        
    def on_mount(self) -> None:
        """应用挂载时的初始化操作
        
        在应用UI完成挂载后执行初始化操作，包括初始化AI客户端和添加欢迎消息
        """
        self._initialize_ai_client()
        self._add_welcome_message()
        
    def _initialize_ai_client(self):
        """初始化AI客户端
        
        从系统提示词文件加载提示词并创建AI客户端实例。
        如果初始化失败，会显示错误通知。
        """
        try:
            # 修正系统提示词文件路径，指向 sdk/ai/prompts/system.md
            prompt_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../ai/prompts/system.md")
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
            self.ai_client = AIClient(system_prompt=system_prompt)
            # 读取模型配置中的 streaming 开关（若存在）
            try:
                # 1) 直接字段
                self.enable_streaming = bool(getattr(self.ai_client.model_config, "streaming", self.enable_streaming))
                # 2) extra_params 中的 streaming / enable_streaming / stream
                extra = getattr(self.ai_client.model_config, "extra_params", {}) or {}
                for key in ("streaming", "enable_streaming", "stream"):
                    if key in extra:
                        self.enable_streaming = bool(extra.get(key))
                        break
            except Exception:
                pass
        except Exception as e:
            self.notify(f"AI客户端初始化失败: {e}", severity="error")
            
    def _add_welcome_message(self):
        """添加欢迎消息
        
        在聊天历史中添加欢迎消息，包括功能介绍、示例和当前启用的工具列表。
        """
        chat_history = self.query_one("#chat-history", ChatHistoryWidget)
        welcome_msg = f"""👋 欢迎使用KetaOps AI智能对话助手！

我可以帮助您：
- 📊 数据查询和分析
- 🔍 智能搜索
- 📈 资源监控
- 🛠️ 系统管理

推荐示例：
- 对当前系统进行巡检
- 查询traceid为xxx的记录，分析其潜在的性能或异常
- 创建一个repo、soucetype等资源
- 查询logs_keta仓库中的异常日志并分析

请输入您的问题，我会尽力为您提供帮助。

当前已启用工具：{', '.join([f'`{x}`' for x in self.enabled_tools]) or '无'}。您也可以按 `T` 查看可用的工具列表来启用或关闭工具开关。"""
        
        chat_history.add_message("assistant", welcome_msg)

    def _get_enabled_tools_openai_format(self):
        """获取已启用工具的OpenAI格式定义列表
        
        从全局工具注册表中筛选出已启用的工具，并返回其OpenAI格式定义。
        
        Returns:
            list: 已启用工具的OpenAI格式定义列表，如果出错则返回空列表
        """
        return get_enabled_tools_openai_format(self.enabled_tools)
        
    def on_chat_input_widget_stop_requested(self, message: ChatInputWidget.StopRequested) -> None:
        """处理聊天输入控件的停止请求事件
        
        当用户请求停止当前AI任务时触发，取消正在进行的AI任务并重置相关状态。
        
        Args:
            message: 停止请求事件对象
        """
        """处理停止请求"""
        if self._current_ai_task:
            self._current_ai_task.cancel()
            self._current_ai_task = None
            self._chat_in_progress = False
            
            # 重置按钮状态
            chat_input = self.query_one("#chat-input", ChatInputWidget)
            chat_input.set_processing(False)
            
            # 显示停止消息
            chat_history = self.query_one("#chat-history", ChatHistoryWidget)
            if chat_history._current_streaming_widget:
                chat_history.finish_streaming_message("**[已停止响应]**")
            else:
                try:
                    # 非流式模式下也给出停止提示
                    chat_history.add_message("assistant", "**[已停止响应]**")
                except Exception:
                    pass
            
            self.notify("已停止AI响应", severity="success")

    def on_chat_input_widget_message_sent(self, message: ChatInputWidget.MessageSent) -> None:
        """处理聊天输入控件的消息发送事件
        
        当用户在聊天输入控件中发送消息时触发，将用户消息添加到聊天历史并启动AI响应处理。
        
        Args:
            message: 消息发送事件对象
        """
        """处理用户发送的消息"""
        if self._chat_in_progress:
            chat_input = self.query_one("#chat-input", ChatInputWidget)
            chat_input.set_loading(False)
            # 进度提示弱化，减少噪音
            self.notify("对话正在进行中，请稍候...", severity="info")
            return
            
        user_message = message.message
        chat_history = self.query_one("#chat-history", ChatHistoryWidget)
        
        # 如果是新会话，创建会话
        if not self.current_session:
            self.current_session = ChatSession.create_new()
        
        # 添加用户消息到历史，计算token统计
        model_selector = self.query_one("#model-selector", ModelSelectorWidget)
        selected_model = model_selector.get_selected_model() or "gpt-3.5-turbo"
        
        # 计算用户消息的token统计
        user_msg_dict = {"role": "user", "content": user_message}
        context_messages = [{"role": msg["role"], "content": msg["content"]} for msg in self.conversation_history]
        user_token_stats = calculate_token_stats(
            current_message=user_msg_dict,
            context_messages=context_messages
        )
        
        chat_history.add_message("user", user_message, token_stats=user_token_stats)
        
        # 设置处理状态
        chat_input = self.query_one("#chat-input", ChatInputWidget)
        chat_input.set_processing(True)
        
        # 异步处理AI响应
        self._current_ai_task = self.run_worker(self._process_ai_response(user_message))
        
    async def _assess_planning_readiness(self, user_text: str) -> dict:
        """评估是否应立即生成计划，或先进行信息发现。
        
        分析用户输入文本，判断是否有足够信息直接生成执行计划，或需要先进行信息收集。
        使用AI模型进行判断，失败时回退到基于关键词的启发式判断。
        
        Args:
            user_text: 用户输入的文本
            
        Returns:
            dict: 包含plan_now(是否立即规划)和reason(原因)的字典
        """
        return await assess_planning_readiness(self.ai_client, user_text)

    async def _plan_task_steps(self, user_text: str) -> list:
        """使用AI判断复杂度并生成任务步骤列表。
        
        根据用户输入的文本，使用AI模型判断任务复杂度并将其拆分为可执行的步骤列表。
        如果任务简单，则返回单个步骤；如果任务复杂，则拆分为多个步骤。
        
        Args:
            user_text: 用户输入的文本
            
        Returns:
            list: 任务步骤文本列表，解析失败时返回包含原始需求的单步骤列表
        """
        return await plan_task_steps(
            self.ai_client,
            user_text,
            enabled_tools=self.enabled_tools,
            conversation_history=self.conversation_history,
        )
    
    async def _execute_task_steps(self, steps: list, original_user_text: str) -> None:
        """顺序执行任务步骤：委托通用执行模块
        
        使用通用模块执行步骤，包含工具调用、总结与完成判定。
        """
        return await execute_task_steps(self, steps, original_user_text)
    
    async def _process_ai_response(self, user_message: str):
        """处理AI响应，委托到通用流程"""
        await process_ai_response(self, user_message)

    async def _stream_chat_with_tools_async(self, messages, tools):
        """委托到公共流式实现（支持工具调用）"""
        return stream_chat_with_tools_async(self, messages, tools)
    
    async def _stream_chat_async(self, messages):
        """委托到公共流式实现"""
        return stream_chat_async(self, messages)
            
    def _augment_system_prompt(self, base: str) -> str:
        return augment_system_prompt(base)

    def _sanitize_tool_messages(self, messages: list, provider: str) -> list:
        return sanitize_tool_messages(messages, provider)

    def _enforce_openai_tool_sequence(self, msgs: list) -> tuple[list, int, int]:
        return enforce_openai_tool_sequence(msgs)

    def _should_force_tool_call(self, msgs: list, user_text: str) -> bool:
        try:
            text = (user_text or "").strip().lower()
        except Exception:
            text = ""
        continue_words = {"继续", "继续执行", "继续查询", "继续检索", "继续分析", "go on", "continue", "carry on"}
        force_by_text = text in continue_words or (len(text) <= 6 and any(w in text for w in {"继续", "go", "cont"}))
        has_prev_tool_calls = any(
            (m.get("role") == "assistant" and (m.get("tool_calls") or []))
            for m in self.conversation_history
        )
        return bool(force_by_text and has_prev_tool_calls)

    def _prepare_messages(self, user_message: str) -> list:
        current_message = {"role": "user", "content": user_message}
        if len(self.conversation_history) > 20:
            self.context_manager.update_config(max_messages=15)
            original_messages = self.conversation_history
            compressed_messages = self.context_manager.process_messages(
                original_messages, force_compress=True
            )
            provider = getattr(self.ai_client.model_config, "provider", "")
            sanitized_messages = self._sanitize_tool_messages(compressed_messages, provider)
            if len(compressed_messages) < len(original_messages):
                try:
                    stats = self.context_manager.compressor.get_compression_stats(
                        original_messages, compressed_messages
                    )
                    tokens_saved = max(
                        0,
                        stats.get("estimated_original_tokens", 0)
                        - stats.get("estimated_compressed_tokens", 0)
                    )
                    self.notify(
                        f"🗜️ 上下文已压缩: {len(original_messages)}→{len(compressed_messages)}条消息, 节省{tokens_saved}个token",
                        timeout=3
                    )
                except Exception:
                    pass
            removed_count = len(compressed_messages) - len(sanitized_messages)
            if removed_count > 0:
                self.notify(f"已移除 {removed_count} 条不合规的工具消息，避免请求错误", severity="warning")
            return sanitized_messages + [current_message]
        else:
            return self.conversation_history + [current_message]

    async def _process_tool_sequence(self, messages: list) -> tuple:
        """处理工具调用序列（委托到公共实现）"""
        return await process_tool_sequence(self, messages)
            
    async def _stream_and_process_response(self, messages: list, tools: list, streaming_widget) -> tuple:
        """流式获取并处理AI响应（委托公共实现）"""
        return await stream_and_process_response(self, messages, tools, streaming_widget)
        
    async def _filter_and_deduplicate_tool_calls(self, tool_calls: list, executed_tool_signatures: set) -> tuple:
        """委托到公共实现，过滤并去重工具调用"""
        return await filter_and_deduplicate_tool_calls(self, tool_calls, executed_tool_signatures)

    async def _execute_tool_call(self, tool_call, tools, chat_history, messages):
        """执行单个工具调用（委托到公共实现）"""
        tool_executor = getattr(self, "tool_executor", None)
        notifier = getattr(self, "notify", None)
        return await execute_tool_call(
            tool_call,
            tools,
            chat_history,
            messages,
            tool_executor=tool_executor,
            notifier=notifier,
        )
        

    def _needs_tool_call(self, content: str) -> bool:
        """委托到 utils.needs_tool_call，集中工具触发逻辑"""
        return needs_tool_call(content)

    # 兜底方案暂不启用：改为强化调试信息，定位模型未返回 tool_calls 的原因

    def _requires_user_confirmation(self, text: str) -> bool:
        return requires_user_confirmation(text)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """处理按钮点击事件"""
        if event.button.id == "tools-button":
            # 保持与快捷键 Ctrl+T 一致：传入当前已启用工具以预选复选框
            try:
                self.push_screen(ToolsListModal(enabled_tools=self.enabled_tools))
            except Exception:
                # 回退：若异常则仍尝试打开，但不预选
                self.push_screen(ToolsListModal())
        elif event.button.id == "new-session-button":
            self.action_clear_chat()
            
    def action_clear_chat(self) -> None:
        """清空对话历史"""
        # 保存当前会话
        self._save_current_session()
        
        # 清空对话
        chat_history = self.query_one("#chat-history", ChatHistoryWidget)
        chat_history.clear_history()
        self.conversation_history.clear()
        self.current_session = None
        self._chat_in_progress = False
        self._add_welcome_message()
        self.notify("对话历史已清空", severity="success")
        
    def action_show_tools(self) -> None:
        """显示工具列表"""
        try:
            self.push_screen(ToolsListModal(enabled_tools=self.enabled_tools))
        except Exception as e:
            self.notify(f"打开工具列表失败: {e}", severity="error")

    @on(ToolsListModal.ToolsSaved)
    def on_tools_list_modal_tools_saved(self, message: ToolsListModal.ToolsSaved) -> None:
        """处理工具选择保存事件"""
        try:
            selected = set(message.selected_tools or [])
            self.enabled_tools = selected
            # 简单提示当前启用工具
            names_preview = ", ".join(list(selected)[:6]) if selected else "(无)"
            self.notify(f"✅ 已更新启用工具：{names_preview}", timeout=4, severity="success")
        except Exception as e:
            self.notify(f"更新启用工具失败: {e}", severity="error")
        
    def action_show_session_history(self) -> None:
        """显示历史会话"""
        modal = SessionHistoryModal(self.session_manager)
        self.push_screen(modal)
        
    def action_show_model_config(self) -> None:
        """显示模型配置管理"""
        from .model_config_app import ModelConfigScreen
        self.push_screen(ModelConfigScreen())
    
    def action_show_context(self) -> None:
        """显示上下文窗口"""
        try:
            self.push_screen(ContextWindowModal())
        except Exception as e:
            self.notify(f"打开上下文窗口失败: {e}", severity="error")
    
    @on(ModelConfigModal.ConfigSaved)
    def on_model_config_saved(self, event: ModelConfigModal.ConfigSaved) -> None:
        """处理模型配置保存事件，转发给当前的 ModelConfigScreen"""
        # 添加调试信息
        self.notify("DEBUG: InteractiveChatApp.on_model_config_saved 被调用，准备转发给 ModelConfigScreen", severity="info")
        
        # 获取当前屏幕栈中的 ModelConfigScreen
        from .model_config_app import ModelConfigScreen
        for screen in reversed(self.screen_stack):
            if isinstance(screen, ModelConfigScreen):
                # 找到了 ModelConfigScreen，转发消息
                self.notify("DEBUG: 找到 ModelConfigScreen，转发 ConfigSaved 消息", severity="info")
                screen.on_config_saved(event)
                break
        else:
            self.notify("DEBUG: 未找到 ModelConfigScreen", severity="warning")
        
        # 刷新主界面的模型选择器
        try:
            model_selector = self.query_one(ModelSelectorWidget)
            model_selector.refresh_model_list()
            self.notify("DEBUG: 主界面模型选择器已刷新", severity="info")
        except Exception as e:
            self.notify(f"DEBUG: 刷新模型选择器失败: {e}", severity="warning")
        
    def action_focus_input(self) -> None:
        """聚焦到输入框"""
        input_widget = self.query_one("#message-input", CustomTextArea)
        input_widget.focus()
    
    def on_session_history_modal_session_selected(self, message) -> None:
        """处理历史会话选择事件"""
        self._load_session(message.session)
    
    def _load_session(self, session: ChatSession):
        """加载指定会话"""
        # 保存当前会话
        if self.current_session and self.conversation_history:
            self.current_session.messages = self.conversation_history.copy()
            self.session_manager.save_session(self.current_session)
        
        # 加载新会话
        self.current_session = session
        self.conversation_history = session.messages.copy()
        
        # 更新UI
        chat_history = self.query_one("#chat-history", ChatHistoryWidget)
        chat_history.clear_history()
        
        # 重新显示历史消息
        for message in self.conversation_history:
            if message["role"] == "user":
                chat_history.add_message("user", message["content"])
            elif message["role"] == "assistant":
                chat_history.add_message("assistant", message["content"])
        
        # 加载完成后提示一次
        self.notify(f"已加载会话: {session.get_display_title()}", severity="success")
    
    def _save_current_session(self):
        """保存当前会话
        
        将当前会话的消息历史和上下文保存到会话管理器中，
        确保会话状态在应用重启后能够恢复。
        """
        """保存当前会话"""
        if not self.conversation_history:
            return
        
        if not self.current_session:
            # 创建新会话
            self.current_session = ChatSession.create()
        
        # 更新会话消息
        self.current_session.messages = self.conversation_history.copy()
        self.current_session.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存会话
        self.session_manager.save_session(self.current_session)


def run_interactive_chat():
    """运行交互式对话应用"""
    import signal
    import sys
    import threading
    import concurrent.futures
    
    # 添加信号处理，确保程序可以正常退出
    def signal_handler(sig, frame):
        print("\n正在安全退出程序...")
        # 关闭所有线程池
        for executor in concurrent.futures._thread._global_shutdown_thread_pools:
            if hasattr(executor, '_threads'):
                for thread in executor._threads:
                    if thread is not None:
                        thread._tstate_lock = None
        # 退出程序
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        app = InteractiveChatApp()
        app.run()
    except KeyboardInterrupt:
        print("\n检测到键盘中断，正在安全退出...")
        sys.exit(0)
    except Exception as e:
        print(f"交互式聊天应用启动失败: {e}")
        import traceback
        with open("interactive_chat_error.log", "w") as f:
            traceback.print_exc(file=f)
