from typing import List, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import Tool
from local_autogen.config.llm_ollama import make_ollama_qwen_client
from local_autogen.agents.prompt_loader import load_prompt
from local_autogen.tools.terminal import execute_shell_command
from local_autogen.tools.file_writer_utils import write_project_file

def make_planner_agent(extra_tools: Optional[List[Tool]] = None) -> AssistantAgent:
    client = make_ollama_qwen_client()

    tools = [execute_shell_command, write_project_file]
    if extra_tools:
        tools.extend(extra_tools)

    return AssistantAgent(
        "planner",
        model_client=client,
        system_message=load_prompt("planner", skills=["context7", "file_writer"]),
        description="Tech Lead & Product Owner - Define a visão de produto, prioriza o backlog e coordena a execução técnica do time.",
        model_client_stream=True,
        tools=tools,
    )
