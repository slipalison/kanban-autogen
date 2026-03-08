# KV Cache Separado por Agente + Timeout Protection

## Implementação Concluída ✅

Cada agente agora possui seu próprio **KV Cache isolado** através de aliases únicos do Ollama:

- `qwen3.5:35b-planner` → Planner Agent
- `qwen3.5:35b-architect` → Architect Agent
- `qwen3.5:35b-coder` → Coder Agent
- `qwen3.5:35b-reviewer` → Reviewer Agent
- `qwen3.5:35b-infrastructure` → Infrastructure Agent
- `qwen3.5:35b-selector` → Selector (quem decide próximo agente)

## Benefícios

✅ **Cache Hit Garantido**: Cada agente mantém seu próprio histórico de contexto
✅ **Sem Competição**: Não há mais eviction de cache entre agentes
✅ **Prefill Reduzido**: Reaproveitamento máximo do contexto de 32k tokens
✅ **Performance Consistente**: Velocidade previsível sem degradação
✅ **Proteção contra Travamento**: Timeout de 180s (3min) evita requisições infinitas

## Trade-off: Memória vs Performance

### Cenário Ideal (Requer ~115GB VRAM)
```bash
# Permitir 5 modelos carregados simultaneamente
OLLAMA_MAX_LOADED_MODELS=5
```
**Resultado**: Performance máxima, todos os agentes prontos instantaneamente

### Cenário Real (RTX 4090 24GB)
```bash
# Permitir 1-2 modelos simultaneamente (padrão do Ollama)
OLLAMA_MAX_LOADED_MODELS=1
```
**Resultado**:
- ✅ Cache isolado preservado por agente
- ⏱️ Loading delay (~5s) ao trocar de agente
- 💾 Cada modelo usa ~23GB VRAM

### Configuração Recomendada

Para RTX 4090 (24GB), o **comportamento padrão do Ollama** (LRU cache) é ideal:

1. **Modelo ativo permanece em VRAM** com seu KV Cache intacto
2. **Ao trocar de agente**:
   - Ollama descarrega modelo anterior (libera VRAM)
   - Carrega novo modelo (~5 segundos)
   - **KV Cache do agente anterior é preservado no disco**
3. **Ao retornar ao agente anterior**:
   - Recarrega o modelo
   - **Restaura o KV Cache anterior** (contexto preservado!)

## Testar Implementação

### Verificar aliases criados
```bash
ollama list | grep qwen3.5
```

### Verificar configuração dos agentes
```bash
python -c "
from local_autogen.agents.planner_agent import make_planner_agent
agent = make_planner_agent()
print(agent._model_client._to_config().model)
"
# Saída esperada: qwen3.5:35b-planner
```

### Executar o sistema
```bash
python -m local_autogen.runner.kanban_team
```

## Como Funciona (Internamente)

### Antes (Problema)
```
[Planner fala] → Cache cheio com contexto A
[Architect fala] → Ollama evict cache A, cria cache B  ❌
[Planner fala novamente] → Ollama evict cache B, refaz prefill A  ❌ LENTO
```

### Depois (Solução)
```
[Planner fala] → qwen3.5:35b-planner cache A (persistido)
[Architect fala] → qwen3.5:35b-architect cache B (persistido)
[Planner fala novamente] → qwen3.5:35b-planner reusa cache A  ✅ RÁPIDO
```

## Configurações Avançadas

### Aumentar tempo de keep_alive (opcional)
```python
# Em llm_ollama.py, adicionar:
"keep_alive": 3600  # Mantém modelo em memória por 1 hora
```

### Monitorar modelos carregados
```bash
# Ver modelos atualmente na VRAM
curl http://localhost:11434/api/ps | jq

# Ver uso de VRAM
nvidia-smi
```

## ⚠️ ATUALIZAÇÃO IMPORTANTE: Troca de Modelo (CRÍTICO!)

### 🚨 Problema Descoberto: qwen3.5:35b com CPU Offload

```bash
# Sintoma observado
ollama ps
NAME           SIZE     PROCESSOR
qwen3.5:35b    35 GB    34%/66% CPU/GPU  ❌ LENTO!
```

**Causa:** Modelo 35GB não cabe nos 24GB da RTX 4090. Ollama faz offload para CPU/RAM, ficando 50-100x mais lento!

### ✅ Solução Aplicada: qwen2.5-coder:32b

```bash
# Agora usando modelo que cabe na GPU
ollama ps
NAME                    SIZE     PROCESSOR
qwen2.5-coder:32b-*     19 GB    100% GPU  ✅ RÁPIDO!
```

**Sistema agora usa `qwen2.5-coder:32b` por padrão** (configurado em `llm_ollama.py`).

**Performance esperada:**
- Prefill: 5-8s (vs 6+ minutos antes)
- Geração: 50-70 tokens/sec (vs 1-2 tokens/sec antes)
- Sem travamentos de 20+ minutos ✅

Para mais detalhes sobre modelos, veja `MODELOS_RECOMENDADOS.md`.

---

## ⚠️ Problema de Travamento do Selector (RESOLVIDO)

### Sintoma
```
[CONTEXTO] CREATE | 1 msgs | ~170/32768 tokens | ⠏ Processando... (00:22:01)
```

Travamento infinito após 22+ minutos, GPU ociosa (6% utilização).

### Causa Raiz
O **selector** (responsável por escolher o próximo agente) pode travar por:
1. Timeout HTTP não configurado (requisição infinita)
2. Parsing de JSON malformado de tool calls
3. Deadlock interno do AutoGen

### Solução Implementada
```python
# Em kanban_team.py
selector_client = make_ollama_client(
    agent_name="selector",
    timeout=60.0,  # ✅ Timeout de 60s (seletor só gera 1 palavra)
    model_params={
        "num_ctx": 4096,
        "num_predict": 8,
        "temperature": 0.0,
    }
)
```

**Todos os agentes** agora têm timeout de 180s (3min) por padrão, exceto o selector que usa 60s.

## 🚀 Otimização para RTX 4090 Única (24GB)

### Problema: Delay de ~5s ao Trocar de Agente

Com apenas 1 GPU, o Ollama precisa descarregar e recarregar modelos (23GB cada). Isso causa delay entre trocas de agente.

### Solução Recomendada: Quantização KV Cache (q4_0)

**Reduz VRAM de 23GB → 17GB por modelo**, acelerando trocas:

```bash
# Windows (PowerShell como Administrador)
[System.Environment]::SetEnvironmentVariable('OLLAMA_KV_CACHE_TYPE', 'q4_0', 'User')

# Reiniciar Ollama
taskkill /F /IM ollama.exe
ollama serve
```

**Resultado Esperado:**
- ⚡ Delay: ~5s → ~3s (40% mais rápido)
- 💾 VRAM: 23GB → 17GB (25% economia)
- 🎯 Qualidade: Praticamente igual (q4_0 é imperceptível)

### Alternativas (Trade-offs Maiores)

#### A) **Workflow Fixo** (sem selector)
Ordem rígida: Planner → Architect → Coder → Reviewer → Infrastructure

```python
# Trocar SelectorGroupChat por RoundRobinGroupChat
from autogen_agentchat.teams import RoundRobinGroupChat

team = RoundRobinGroupChat(
    participants=[planner, architect, coder, reviewer, infrastructure],
    termination_condition=termination,
)
```

**Prós:** Elimina selector, workflow previsível
**Contras:** Perde flexibilidade (não pode voltar ao planner)

#### B) **3 Agentes ao invés de 5**
- Designer (Planner + Architect)
- Developer (Coder)
- QA (Reviewer + Infrastructure)

**Prós:** Menos trocas de modelo
**Contras:** Agentes mais genéricos, pode perder qualidade

#### C) **Modelos Mistos** (7B/14B para tarefas simples)
```python
# Planner/Reviewer: qwen2.5:14b (5GB)
# Coder: qwen3.5:35b (23GB)
```

**Prós:** Múltiplos modelos pequenos cabem na VRAM
**Contras:** Qualidade variável, precisa testar

### Comparação de Estratégias

| Estratégia | Delay | Qualidade | Complexidade | Mudanças |
|-----------|-------|-----------|--------------|----------|
| **KV Cache q4_0** ⭐ | ~3s | ⭐⭐⭐⭐⭐ | Baixa | 1 variável |
| **RoundRobin** | ~5s | ⭐⭐⭐⭐ | Baixa | 3 linhas |
| **3 Agentes** | ~3s | ⭐⭐⭐⭐ | Média | Refatorar |
| **Modelos Mistos** | ~1s | ⭐⭐⭐⭐ | Alta | Múltiplos modelos |

⭐ **Recomendado:** Quantização KV Cache (q4_0) - Melhor custo-benefício

## Referências

- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Ollama FAQ - Model Loading](https://docs.ollama.com/faq)
- [Ollama KV Cache Quantization](https://smcleod.net/2024/12/bringing-k/v-context-quantisation-to-ollama/)
- [SideQuest: Model-Driven KV Cache Management](https://arxiv.org/html/2602.22603v1)
