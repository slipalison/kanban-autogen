import os
import asyncio
from typing import List
from dotenv import load_dotenv
from autogen_core import Component
from autogen_ext.tools.mcp import mcp_server_tools, StdioServerParams
from autogen_core.tools import Tool

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Context7 MCP
CONTEXT7_API_KEY = os.getenv("CONTEXT7_API_KEY")
if not CONTEXT7_API_KEY:
    raise ValueError("CONTEXT7_API_KEY não encontrada. Defina-a no arquivo .env")

async def get_context7_tools() -> List[Tool]:
    """
    Inicializa a conexão com o servidor MCP do Context7 e retorna as ferramentas disponíveis.
    """
    server_params = StdioServerParams(
        command="npx.cmd",
        args=["-y", "@upstash/context7-mcp", "--api-key", CONTEXT7_API_KEY]
    )
    
    try:
        tools = await mcp_server_tools(server_params)
        return tools
    except Exception as e:
        print(f"Erro ao carregar ferramentas do Context7: {e}")
        return []

# Cache para as ferramentas para evitar múltiplas conexões
_cached_tools: List[Tool] = None

async def get_cached_context7_tools() -> List[Tool]:
    global _cached_tools
    if _cached_tools is None:
        _cached_tools = await get_context7_tools()
    return _cached_tools
