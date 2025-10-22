#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
import sys
import json

from rich.tree import Tree
from rich.text import Text
from rich.console import Console
from rich.status import Status
from rich.syntax import Syntax
from rich.progress import Progress, TimeElapsedColumn

from aipyapp.display import RichDisplayPlugin
from aipyapp import T

def restore_output(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__

        try:
            return func(self, *args, **kwargs)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr
    return wrapper

class DisplayMinimal(RichDisplayPlugin):
    """Minimal display style"""
    name = "minimal"
    version = "1.0.0"
    description = "Minimal display style"
    author = "AiPy Team"

    def __init__(self, console: Console, quiet: bool = False):
        super().__init__(console, quiet)
        self.live_display = None
        self.received_lines = 0  # 记录接收的行数
        self.status = None  # Status 对象
        self.progress = None

    def _get_title(self, title: str, *args, style: str = "info", prefix: str = "\n"):
        text = Text(f"{prefix}● {title}".format(*args), style=style)
        text.highlight_words(args, style="bold white")
        return text
    
    def on_exception(self, event):
        """异常事件处理"""
        msg = event.typed_event.msg
        exception = event.typed_event.exception
        title = self._get_title(T("Exception occurred"), msg, style="error")
        tree = Tree(title)
        tree.add(exception)
        self.console.print(tree)

    def on_task_started(self, event):
        """任务开始事件处理"""
        instruction = event.typed_event.instruction
        title = event.typed_event.title
        if not title:
            title = instruction
        tree = Tree(f"🚀 {T('Task processing started')}")
        tree.add(title)
        self.console.print(tree)

    def on_task_completed(self, event):
        """任务结束事件处理"""
        path = event.typed_event.path or ''
        self.console.print(f"[green]{T('Task completed')}: {path}")

    def on_request_started(self, event):
        """查询开始事件处理"""
        llm = event.typed_event.llm
        title = self._get_title(T("Sending message to {}"), llm)
        self.console.print(title)

    def on_step_started(self, event):
        """步骤开始事件处理"""
        instruction = event.typed_event.instruction
        title = event.typed_event.title
        if not title:
            title = instruction
        prompt = self._get_title(T("Instruction processing started"))
        tree = Tree(prompt)
        tree.add(title)
        self.console.print(tree)

    def on_stream_started(self, event):
        """流式开始事件处理"""
        # 简约风格：重置行数计数器并启动 Status
        self.received_lines = 0
        title = self._get_title(T("Streaming started"), prefix="")
        #self.status = Status(title, console=self.console)
        #self.status.start()
        self.progress = Progress(*Progress.get_default_columns(),TimeElapsedColumn(), transient=False)
        self.progress.start()
        self.progress.add_task(title, total=None)

    def on_stream_completed(self, event):
        """流式结束事件处理"""
        # 简约风格：停止 Status 并显示最终结果
        if self.status:
            self.status.stop()
            if self.received_lines > 0:
                title = self._get_title(T("Received {} lines total"), self.received_lines)
                self.console.print(title)
            self.status = None
        if self.progress:
            self.progress.stop()
            self.progress = None
            
    def on_stream(self, event):
        """LLM 流式响应事件处理"""
        lines = event.typed_event.lines
        reason = event.typed_event.reason

        if not reason:  # 只统计非思考内容
            self.received_lines += len(lines) if lines else 0
            # 使用 Status 在同一行更新进度
            if self.status:
                title = self._get_title(T("Receiving response... ({})"), self.received_lines)
                self.status.update(title)
                
    def on_response_completed(self, event):
        """LLM 响应完成事件处理"""
        llm = event.typed_event.llm
        msg = event.typed_event.msg
        if not msg:
            title = self._get_title(T("LLM response is empty"), style="error")
            self.console.print(title)
            return
        
        if msg.role == 'error':
            title = self._get_title(T("Failed to receive message"), style="error")
            tree = Tree(title)
            tree.add(msg.content)
            self.console.print(tree)
            return
        
        if msg.reason:
            content = f"{msg.reason}\n\n-----\n\n{msg.content}"
        else:
            content = msg.content
        title = self._get_title(f"{T('Completed receiving message')} ({llm})", style="success")
        tree = Tree(title)
        self.console.print(tree)

    def on_task_status(self, event):
        """任务状态事件处理"""
        status = event.typed_event.status
        completed = status.completed
        style = "success" if completed else "error" 
        title = self._get_title(T("Task status"), style=style)
        tree = Tree(title, guide_style=style)
        if completed:
            tree.add(T("Completed"))
            tree.add(T("Confidence level: {}", status.confidence))
        else:
            tree.add(status.status)
            if status.reason:
                tree.add(T("Reason: {}", status.reason))
            if status.suggestion:
                tree.add(T("Suggestion: {}", status.suggestion))
        self.console.print(tree)
        
    def on_parse_reply_completed(self, event):
        """消息解析结果事件处理"""
        response = event.typed_event.response
        errors = response.errors
        if not response:
            return
            
        title = self._get_title(T("Message parse result"))
        tree = Tree(title)
        
        if response.code_blocks:
            block_count = len(response.code_blocks)
            tree.add(f"{block_count} {T('code blocks')}")
        
        if response.tool_calls:
            tool_calls = response.tool_calls
            exec_count = sum(1 for tool_call in tool_calls if tool_call.name.value == 'Exec')
            edit_count = sum(1 for tool_call in tool_calls if tool_call.name.value == 'Edit')
            subtask_count = sum(1 for tool_call in tool_calls if tool_call.name.value == 'SubTask')

            if exec_count > 0:
                tree.add(f"{T('Execution')}: {exec_count}")
            if edit_count > 0:
                tree.add(f"{T('Edit')}: {edit_count}")
            if subtask_count > 0:
                tree.add(f"{T('SubTask')}: {subtask_count}")
        
        if errors:
            error_count = len(errors)
            tree.add(f"{error_count} {T('errors')}")
        
        self.console.print(tree)

    def on_exec_started(self, event):
        """代码执行开始事件处理"""
        block = event.typed_event.block
        title = self._get_title(T("Start executing code block {}"), block.name)
        self.console.print(title)
        
    def on_edit_started(self, event):
        """代码编辑开始事件处理"""
        block = event.typed_event.block
        title = self._get_title(T("Start editing {}"), block.name, style="warning")
        self.console.print(title)
        
    def on_edit_completed(self, event):
        """代码编辑结果事件处理"""
        success = event.typed_event.success
        block_name = event.typed_event.block_name
        new_version = event.typed_event.new_version
        
        if success:
            style = "success"
            version_info = f" (v{new_version})" if new_version else ""
            title = self._get_title(T("Edit completed {}{}"), block_name, version_info, style=style)
        else:
            style = "error"
            title = self._get_title(T("Edit failed {}"), block_name, style=style)
            
        self.console.print(title)
            
    @restore_output
    def on_function_call_started(self, event):
        """函数调用事件处理"""
        funcname = event.typed_event.funcname
        title = self._get_title(T("Start calling function {}"), funcname)
        self.console.print(title)
    
    @restore_output
    def on_function_call_completed(self, event):
        """函数调用结果事件处理"""
        funcname = event.typed_event.funcname
        success = event.typed_event.success
        result = event.typed_event.result
        error = event.typed_event.error
        
        if success:
            style = "success"
            title = self._get_title(T("Function call result {}"), funcname, style=style)
            tree = Tree(title)
            # 简约风格：只显示结果存在性，不显示详细内容
            if result is not None:
                tree.add(T("Result returned"))
            else:
                tree.add(T("No return value"))
            self.console.print(tree)
        else:
            style = "error"
            title = self._get_title(T("Function call failed {}"), funcname, style=style)
            tree = Tree(title)
            tree.add(error if error else T("Unknown error"))
            self.console.print(tree)

    def on_exec_completed(self, event):
        """代码执行结果事件处理"""
        result = event.typed_event.result
        block = event.typed_event.block
        
        try:
            success = result['__state__']['success']
            style = "success" if success else "error"
        except:
            style = "warning"
        
        # 显示说明信息
        block_name = getattr(block, 'name', 'Unknown') if block else 'Unknown'
        title = self._get_title(T("Execution result {}"), block_name, style=style)
        tree = Tree(title)
        
        # JSON格式化和高亮显示结果
        #json_result = json.dumps(result, ensure_ascii=False, indent=2, default=str)
        #tree.add(Syntax(json_result, "json", word_wrap=True))
        self.console.print(tree)

    def on_tool_call_started(self, event):
        """工具调用开始事件处理"""
        tool_call = event.typed_event.tool_call
        title = self._get_title(T("Start calling tool {}"), tool_call.name.value)
        tree = Tree(title)
        args = tool_call.arguments.model_dump_json()
        tree.add(args[:64] + '...' if len(args) > 64 else args)
        self.console.print(tree)

    def on_tool_call_completed(self, event):
        """MCP 工具调用结果事件处理"""
        typed_event = event.typed_event
        result = typed_event.result
        title = self._get_title(T("Tool call result {}"), result.tool_name.value)
        tree = Tree(title)
        json_result = result.result.model_dump_json(exclude_none=True, exclude_defaults=True)
        tree.add(json_result[:64] + '...' if len(json_result) > 64 else json_result)
        self.console.print(tree)

    def on_step_completed(self, event):
        """任务总结事件处理"""
        summary = event.typed_event.summary
        response = event.typed_event.response
        # 简约显示：只显示总结信息
        title = self._get_title(T("End processing instruction"))
        tree = Tree(title)
        if response:
            tree.add(Syntax(response, "markdown", word_wrap=True))
        tree.add(f"{T('Summary')}: {summary.get('summary', '') if summary else ''}")
        self.console.print(tree)

    def on_step_cleanup_completed(self, event):
        """Step清理完成事件处理 - 简约风格"""
        typed_event = event.typed_event
        cleaned_messages = typed_event.cleaned_messages
        tokens_saved = typed_event.tokens_saved
        # 简约显示：只显示关键信息
        if cleaned_messages > 0:
            title = self._get_title(T("🧹 Cleaned {} messages, saved {} tokens"), cleaned_messages, tokens_saved, style="dim cyan")
        else:
            title = self._get_title(T("🧹 No cleanup needed"), style="dim cyan")
        self.console.print(title)

    def on_upload_result(self, event):
        """云端上传结果事件处理"""
        status_code = event.typed_event.status_code
        url = event.typed_event.url
        if url:
            self.console.print(f"🟢 {T('Article uploaded successfully, {}', url)}", style="success")
        else:
            self.console.print(f"🔴 {T('Upload failed (status code: {})', status_code)}", style="error")


    def on_runtime_message(self, event):
        """Runtime消息事件处理"""
        message = event.typed_event.message
        status = event.typed_event.status or 'info'
        title = self._get_title(message, style=status)
        self.console.print(title)

    def on_runtime_input(self, event):
        """Runtime输入事件处理"""
        # 输入事件通常不需要特殊处理，因为input_prompt已经处理了
        pass