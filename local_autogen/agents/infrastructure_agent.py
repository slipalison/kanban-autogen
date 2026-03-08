from typing import List, Optional
from autogen_agentchat.agents import AssistantAgent
from autogen_core.tools import Tool
from local_autogen.config.llm_ollama import make_ollama_qwen_client
from local_autogen.agents.prompt_loader import load_prompt
from local_autogen.tools.terminal import execute_shell_command
from local_autogen.tools.file_writer_utils import write_project_file

def make_infrastructure_agent(extra_tools: Optional[List[Tool]] = None) -> AssistantAgent:
    """Cria o agente responsável por Docker e infraestrutura."""
    # Criar cliente com KV Cache isolado para o infrastructure
    from local_autogen.config.llm_ollama import make_ollama_client
    client = make_ollama_client(agent_name="infrastructure")

    tools = [execute_shell_command, write_project_file]
    if extra_tools:
        tools.extend(extra_tools)

    return AssistantAgent(
        "infrastructure",
        model_client=client,
        system_message=load_prompt("infrastructure", skills=["terminal", "file_writer"]),
        description="DevOps / Infrastructure Engineer - Especialista em Docker e infraestrutura do projeto.",
        model_client_stream=True,
        tools=tools,
    )
