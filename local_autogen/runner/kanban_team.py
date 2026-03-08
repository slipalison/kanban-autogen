import asyncio
import logging
from pathlib import Path
from datetime import datetime
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console

from local_autogen.config.llm_ollama import make_ollama_qwen_client
from local_autogen.agents.planner_agent import make_planner_agent
from local_autogen.agents.architect_agent import make_architect_agent
from local_autogen.agents.coder_agent import make_coder_agent
from local_autogen.agents.reviewer_agent import make_reviewer_agent
from local_autogen.agents.infrastructure_agent import make_infrastructure_agent
from local_autogen.runner.file_writer_termination import FileWriterTermination
from local_autogen.tools.mcp_context7 import get_cached_context7_tools

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def run_kanban_team(initial_task: str) -> None:
    # Buscar ferramentas do Context7 MCP
    mcp_tools = await get_cached_context7_tools()
    
    planner = make_planner_agent()
    architect = make_architect_agent(extra_tools=mcp_tools)
    coder = make_coder_agent(extra_tools=mcp_tools)
    reviewer = make_reviewer_agent(extra_tools=mcp_tools)
    infrastructure = make_infrastructure_agent(extra_tools=mcp_tools)

    # Usar o terminador personalizado que salva arquivos
    termination = FileWriterTermination(output_dir=".", max_messages=20)

    # Cliente para o seletor (quem decide quem fala a seguir)
    selector_client = make_ollama_qwen_client()

    # SelectorGroupChat garante o controle dinâmico da vez de quem vai falar
    team = SelectorGroupChat(
        participants=[planner, architect, coder, reviewer, infrastructure],
        model_client=selector_client,
        termination_condition=termination,
        selector_prompt=(
            "Você é o coordenador do projeto. Decida quem deve falar a seguir baseado na conversa atual.\n"
            "- 'planner' começa estabelecendo a visão.\n"
            "- 'architect' cria e documenta a arquitetura técnica.\n"
            "- 'coder' programa e implementa o código seguindo a arquitetura. O 'coder' SÓ DEVE realizar o commit do código SE o 'reviewer' já tiver validado e aprovado as alterações.\n"
            "- 'reviewer' deve SEMPRE revisar o código do 'coder'. Se houver erro ou necessidade de ajuste, mande a vez de volta para o 'coder'. Se estiver aprovado, declare claramente.\n"
            "- 'infrastructure' cuida de scripts de deploy e Docker."
        )
    )

    await Console(
        team.run_stream(task=initial_task)
    )

async def main() -> None:
    initial_task = (
        "OBJETIVO: Criar um sistema Kanban (estilo Trello) minimalista e funcional.\n\n"
        "STACK TECNOLÓGICA:\n"
        "- Backend: C# .NET 10 (Web API ou integrado ao Blazor)\n"
        "- Frontend: MudBlazor Server\n"
        "- Banco de Dados: PostgreSQL (para facilitar o setup) com Entity Framework Core\n\n"
        "REQUISITOS FUNCIONAIS:\n"
        "1. Autenticação Simples: Tela de login e tela de cadastro (Nome, Email, Senha), com sessão de usuário logado.\n"
        "2. O painel deve ter 3 colunas padrão: 'A Fazer', 'Em Andamento', 'Concluído' por padrão mas posso adicionar colunas customizadas.\n"
        "3. Capacidade de criar novos cartões (Cards) contendo Título e Descrição, tempo estimado de conclusão e prioridade, e uma area para adicionar comentarios.\n"
        "4. Capacidade de arrastar e soltar (Drag & Drop) os cartões entre as colunas.\n"
        "5. A posição real (ordem e coluna) dos cartões deve ser persistida no banco de dados, atrelada ao usuário logado.\n"
        "6. O layout deve ser limpo, utilizando os componentes nativos do MudBlazor.\n\n"
        "DIRETRIZES PARA OS AGENTES:\n"
        "- Planner: Estruture as histórias de usuário e defina a ordem de execução.\n"
        "- Architect: Defina o esquema do banco, organização de pastas e como o estado do Drag & Drop será gerenciado no Blazor Server.\n"
        "- Coder: Implemente o código passo a passo, fornecendo todo o HTML/C# necessário.\n"
        "- Reviewer: Garanta que o Drag & Drop do MudBlazor está implementado corretamente e os EF migrations funcionam.\n"
        "- Infraestrutura: Crie um README com as instruções para rodar a aplicação localmente."
    )
    await run_kanban_team(initial_task)

if __name__ == "__main__":
    asyncio.run(main())
