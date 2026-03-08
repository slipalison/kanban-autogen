from typing import List, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import Tool
from local_autogen.config.llm_ollama import make_ollama_qwen_client
from local_autogen.agents.prompt_loader import load_prompt
from local_autogen.tools.terminal import execute_shell_command

def make_coder_agent(extra_tools: Optional[List[Tool]] = None) -> AssistantAgent:
    client = make_ollama_qwen_client()
    
    tools = [execute_shell_command]
    if extra_tools:
        tools.extend(extra_tools)
        
    return AssistantAgent(
        "coder",
        model_client=client,
        system_message=load_prompt("coder", skills=["context7", "terminal", "file_writer", "dotnet"]),
        description="Senior Developer - Implementa lógica e componentes em qualquer linguagem solicitada.",
        model_client_stream=True,
        tools=tools,
    )
