# 🤖 Kanban AutoGen Agent Team

Este repositório contém uma equipe de agentes baseada em Multi-Agentes utilizando o **Microsoft AutoGen 0.4+** para conceber, planejar, arquitetar e codificar um sistema Kanban completo do zero, de forma autônoma.

## 🚀 Como Executar

A execução é coordenada pelo `kanban_team.py`. Ele irá instanciar a "sala de chat" dos agentes e passar o prompt inicial para que eles comecem a trabalhar.

1. **Ative seu ambiente virtual (se aplicável):**
   ```bash
   # Exemplo no Windows
   .venv\Scripts\activate
   ```

2. **Certifique-se que o Ollama e os modelos estão rodando:**
   Se você estiver utilizando LLMs locais, garanta que o serviço do Ollama está up.
   ```bash
   ollama serve
   ```

3. **Inicie o Trabalho da Equipe:**
   ```bash
   python local_autogen/runner/kanban_team.py
   ```

Os agentes conversam no terminal e começarão a criar documentos e arquivos de código na raiz ou nas pastas indicadas dentro das conversas.

---

## 🏗️ Estrutura do Projeto

Abaixo está o detalhamento de como o sistema multi-agentes está organizado dentro da pasta `local_autogen/`:

```text
local_autogen/
│
├── agents/                   # Definição das personalidades dos Agentes
│   ├── planner_agent.py      # Product Owner: Define as regras e a ordem de execução
│   ├── architect_agent.py    # Tech Lead: Desenha infra, C4 Model, banco e ADRs
│   ├── coder_agent.py        # Dev Pleno/Senior: Focado na implementação de código C# e Blazor
│   ├── reviewer_agent.py     # Revisor: Valida o código, aponta bugs e exige refatoração
│   └── infrastructure_agent.py # DevOps: Cria Dockerfiles, docker-compose e readme técnico
│
├── agents/prompts/           # As "almas" dos agentes (System Prompts)
│   ├── planner.md            # Regras e comportamentos específicos do Planner
│   ├── architect.md          # Regras e comportamentos (ex: aprovar infra, contratos)
│   ├── coder.md              # Regras sobre SOLID, Clean Code e padrões C#
│   ├── reviewer.md           # Focado em qualidade e testes
│   └── infrastructure.md     # Focado em deploy, observabilidade e containers
│
├── config/                   # Configuração das conexões de linguagem
│   └── llm_ollama.py         # Client customizado para o Ollama interagir com os LLMs
│
├── runner/                   # Lógica de Orquestração da Equipe
│   ├── kanban_team.py        # O Ponto de Entrada: Orquestra usando o SelectorGroupChat
│   └── file_writer_termination.py # Lógica de término de conversa e salvamento formatado
│
└── tools/                    # Ferramentas extras que os agentes podem acessar (MCP / Shell)
    └── mcp_context7.py       # Integração com MCP para busca em documentação técnica
```

---

## 🧠 Como a "Sala de Chat" (`kanban_team.py`) Funciona

A coordenação ocorre via um **SelectorGroupChat**. Isso significa que a conversa não é um loop forçado, mas sim um formato dinâmico mediado por um *LLM Coordenador*.

As regras enforçadas na hora de passar o bastão entre os agentes são:
1. Começa com o **Planner**.
2. Passa a vez para o **Architect**.
3. Em seguida, para o **Coder**.
4. Quando o Coder envia um código, a vez **SEMPRE** vai obrigatoriamente para o **Reviewer**.
5. Se o Reviewer encontrar erros, ele joga a vez **de volta** para o Coder. O Coder só tem permissão para fazer um "commit" ou finalizar o trabalho após ganhar a declaração "Aprovado" do Reviewer.
6. A **Infrastructure** foca nos contêineres e documentação técnica de rodar o código finalizado.

Esse fluxo dinâmico aumenta vertiginosamente a confiabilidade dos agentes geradores de código.

---

## 🛠️ Personalizando a Geração (Kanban)

Se você quiser alterar o escopo do que os agentes irão criar (ex: mudar o PostgreSQL para MySQL, pedir um Kanban com 5 colunas em vez de 3), edite a variável `initial_task` dentro de:
`local_autogen/runner/kanban_team.py` (linha 63 em diante).

Lá está definido o **Business Requirements Document**, moldando exatamente os requisitos de Negócio que o `Planner` usará de base.
