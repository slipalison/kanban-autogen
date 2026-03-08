import asyncio
import logging
from pathlib import Path
from datetime import datetime
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat

from local_autogen.config.llm_ollama import make_ollama_client, make_ollama_qwen_client
from local_autogen.agents.planner_agent import make_planner_agent
from local_autogen.agents.architect_agent import make_architect_agent
from local_autogen.agents.coder_agent import make_coder_agent
from local_autogen.agents.reviewer_agent import make_reviewer_agent
from local_autogen.agents.infrastructure_agent import make_infrastructure_agent
from local_autogen.runner.file_writer_termination import FileWriterTermination
from local_autogen.tools.mcp_context7 import get_cached_context7_tools

# Configurar logging estruturado
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger("autogen_core").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def run_kanban_team(initial_task: str) -> None:
    logger.info("🚀 Iniciando Kanban Team")
    logger.info(f"📋 Tarefa inicial: {initial_task}")

    try:
        # Buscar ferramentas do Context7 MCP
        logger.info("🔧 Carregando ferramentas MCP Context7...")
        mcp_tools = await get_cached_context7_tools()
        logger.info(f"✅ {len(mcp_tools)} ferramentas MCP carregadas")

        # Criar agentes com ferramentas MCP
        logger.info("👥 Inicializando agentes especializados...")
        planner = make_planner_agent(extra_tools=mcp_tools)
        architect = make_architect_agent(extra_tools=mcp_tools)
        coder = make_coder_agent(extra_tools=mcp_tools)
        reviewer = make_reviewer_agent(extra_tools=mcp_tools)
        infrastructure = make_infrastructure_agent(extra_tools=mcp_tools)
        logger.info("✅ Agentes criados: planner, architect, coder, reviewer, infrastructure")

        # Usar o terminador personalizado que salva arquivos
        termination = FileWriterTermination(output_dir="project", max_messages=100)

        # Cliente para o seletor (quem decide quem fala a seguir)
        logger.info("🤖 Configurando modelo seletor...")
        # Unificar num_ctx com os agentes (32k) para otimizar reuso de KV Cache no Ollama
        # num_predict reduzido para forçar brevidade e economizar tempo
        selector_client = make_ollama_client(model_params={
            "num_ctx": 32768,
            "num_predict": 32,
            "temperature": 0.0
        })

        # SelectorGroupChat garante o controle dinâmico da vez de quem vai falar
        logger.info("🎯 Criando SelectorGroupChat com workflow estruturado...")
        team = SelectorGroupChat(
            participants=[planner, architect, coder, reviewer, infrastructure],
            model_client=selector_client,
            termination_condition=termination,
            max_selector_attempts=5,
            allow_repeated_speaker=True,
            selector_prompt=(
                "### INSTRUCTION ###\n"
                "You are the team coordinator. Analyze the history and pick the NEXT agent to speak.\n"
                "Reply ONLY with the exact name. NO punctuation, NO markdown, NO explanation.\n\n"
                "### AGENTS ###\n"
                "- planner: Defines plans and stories.\n"
                "- architect: Database and system design.\n"
                "- coder: Writes application code (.cs, .razor).\n"
                "- reviewer: Validates and reviews code.\n"
                "- infrastructure: Setup, Docker, README.\n\n"
                "### WORKFLOW RULES ###\n"
                "1. New task? -> planner\n"
                "2. Planner done? -> architect\n"
                "3. Architect done? -> coder\n"
                "4. Coder done? -> reviewer\n"
                "5. Reviewer found bugs? -> coder\n"
                "6. Reviewer approved? -> planner\n\n"
                "### FORMAT ###\n"
                "Response: [agent_name]\n"
                "Example 1: coder\n"
                "Example 2: architect"
            )
        )

        from local_autogen.runner.claude_console import ClaudeConsole
        
        logger.info("🎬 Iniciando execução do team com ClaudeConsole...")
        await ClaudeConsole(
            team.run_stream(task=initial_task)
        ).run()
        logger.info("✅ Kanban Team finalizado com sucesso")

    except Exception as e:
        logger.error(f"❌ Erro durante execução do Kanban Team: {e}", exc_info=True)
        raise

async def main() -> None:
    initial_task = (
        "OBJETIVO: Criar um sistema Kanban (estilo Trello) minimalista e funcional.\n\n"
        "STACK TECNOLÓGICA:\n"
        "- Backend: C# .NET 10 (Web API ou integrado ao Blazor), deve usar o arquivo .slnx o novo formato do arquivo de solução\n"
        "- Frontend: MudBlazor pois ele já tem suporte a Drag & Drop\n"
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
        "- Infraestrutura: Crie um README com as instruções para rodar a aplicação localmente.\n\n"
        "🚫 RESTRIÇÃO CRÍTICA:\n"
        "APENAS O 'coder' PODE ESCREVER CÓDIGO DE APLICAÇÃO (.cs, .razor, .js, migrations, etc.).\n"
        "Planner, Architect e Reviewer NÃO PODEM criar ou modificar código - apenas especificar ou revisar.\n"
        "Infrastructure PODE criar Dockerfiles, K8s manifests, CI/CD - NÃO pode criar código de aplicação."
    )
    await run_kanban_team(initial_task)

if __name__ == "__main__":
    asyncio.run(main())
