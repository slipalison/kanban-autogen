# 🎯 Solução Final: Modelo que Obedece + Cabe na GPU

## ❌ Problema Identificado

**qwen2.5-coder:32b** está **ignorando** as instruções do system message:
- Continua exibindo código/conteúdo no console
- Não chama `write_project_file` imediatamente
- Comportamento: Modelo treinado para "explicar" código, não seguir regras rígidas

**qwen3.5:35b** obedece perfeitamente, mas **não cabe na GPU**:
- 35GB modelo + KV cache = ~40GB total
- RTX 4090 = 24GB VRAM
- Resultado: CPU offload (50-100x mais lento)

---

## ✅ Solução: Qwen2.5:32B (Versão Base, Não Coder)

O **qwen2.5:32b** (sem sufixo "coder") é:
- ✅ Modelo base generalista (obedece prompts melhor)
- ✅ 19GB (cabe na RTX 4090 com folga)
- ✅ 100% GPU (sem CPU offload)
- ✅ Excelente em código E em seguir instruções

### Como Implementar

```bash
# 1. Baixar modelo base (não o coder)
ollama pull qwen2.5:32b

# 2. Criar aliases
ollama cp qwen2.5:32b qwen2.5:32b-planner
ollama cp qwen2.5:32b qwen2.5:32b-architect
ollama cp qwen2.5:32b qwen2.5:32b-coder
ollama cp qwen2.5:32b qwen2.5:32b-reviewer
ollama cp qwen2.5:32b qwen2.5:32b-infrastructure
ollama cp qwen2.5:32b qwen2.5:32b-selector

```

```bash
# 1. Baixar modelo base (não o coder)
ollama pull qwen3.5:27b

# 2. Criar aliases
ollama cp qqwen3.5:27b qwen3.5:27b-selector

ollama cp qwen3.5:27b qwen3.5:27b-planner
ollama cp qwen3.5:27b qwen3.5:27b-architect
ollama cp qwen3.5:27b qwen3.5:27b-coder
ollama cp qwen3.5:27b qwen3.5:27b-reviewer
ollama cp qwen3.5:27b qwen3.5:27b-infrastructure
ollama cp qwen3.5:27b qwen3.5:27b-selector
```

### Atualizar Código

```python
# Em llm_ollama.py linha 259
model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen2.5:32b")
```

---

## 🔥 Alternativa Premium: Qwen3.5-27B-Claude (Distilled)

Se você quer o **melhor dos dois mundos**:

### 1. Baixar GGUF Q4_K_M ou Q5_K_M

```bash
# Q4_K_M (16GB) - Mais rápido
curl -L -o qwen3.5-27b-claude-q4.gguf https://huggingface.co/Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF/resolve/main/qwen3.5-27b-claude-4.6-opus-reasoning-distilled-q4_k_m.gguf

# OU Q5_K_M (19GB) - Mais qualidade
curl -L -o qwen3.5-27b-claude-q5.gguf https://huggingface.co/Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF/resolve/main/qwen3.5-27b-claude-4.6-opus-reasoning-distilled-q5_k_m.gguf
```

### 2. Criar Modelfile

```bash
cat > Modelfile << 'EOF'
FROM ./qwen3.5-27b-claude-q5.gguf
TEMPLATE {{ .Prompt }}
PARAMETER temperature 0.7
PARAMETER top_k 40
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
EOF
```

### 3. Importar para Ollama

```bash
ollama create qwen3.5-27b-claude -f Modelfile
```

### 4. Criar Aliases

```bash
ollama cp qwen3.5-27b-claude qwen3.5-27b-claude-planner
ollama cp qwen3.5-27b-claude qwen3.5-27b-claude-architect
ollama cp qwen3.5-27b-claude qwen3.5-27b-claude-coder
ollama cp qwen3.5-27b-claude qwen3.5-27b-claude-reviewer
ollama cp qwen3.5-27b-claude qwen3.5-27b-claude-infrastructure
ollama cp qwen3.5-27b-claude qwen3.5-27b-claude-selector
```

### 5. Atualizar Código

```python
# Em llm_ollama.py linha 259
model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen3.5-27b-claude")
```

---

## 📊 Comparação Final

| Modelo | VRAM | Obedece Prompts | Velocidade | Qualidade Código | Disponível |
|--------|------|-----------------|------------|------------------|------------|
| qwen3.5:35b | 35GB ❌ | ⭐⭐⭐⭐⭐ | Lento (CPU) | ⭐⭐⭐⭐⭐ | ✅ Ollama |
| qwen2.5-coder:32b | 19GB ✅ | ⭐⭐ ❌ | Rápido | ⭐⭐⭐⭐⭐ | ✅ Ollama |
| **qwen2.5:32b** ⭐ | 19GB ✅ | ⭐⭐⭐⭐ | Rápido | ⭐⭐⭐⭐ | ✅ Ollama |
| **qwen3.5-27b-claude (Q5)** 🔥 | 19GB ✅ | ⭐⭐⭐⭐⭐ | Muito Rápido | ⭐⭐⭐⭐⭐ | ⚠️ Manual |

⭐ **Recomendado Imediato:** qwen2.5:32b (já no Ollama, 1 comando)
🔥 **Recomendado Premium:** qwen3.5-27b-claude Q5_K_M (download 19GB, melhor qualidade)

---

## 🚀 Ação Imediata Recomendada

### Opção A: Rápido (5 minutos)

```bash
# Trocar para qwen2.5:32b base
ollama pull qwen2.5:32b
# Criar aliases (comandos acima)
# Testar
```

### Opção B: Melhor (30 minutos)

```bash
# Download Qwen3.5-27B-Claude Q5_K_M (19GB)
# Importar para Ollama
# Criar aliases
# Testar
```

---

## 🧪 Como Validar Sucesso

Após trocar o modelo, execute:

```bash
python -m local_autogen.runner.kanban_team
```

**✅ SUCESSO** se ver:
```
📋 PLANNER
  🔨 Gravando arquivo: PLAN.md...
    ✅ Arquivo salvo (00:00:01)

  ✅ Plano salvo em project/PLAN.md
```

**❌ FALHA** se ver:
```
📋 PLANNER
  ### Visão do Produto

  **Objetivo:** Desenvolver um sistema...
  [300 linhas de texto no console]
```

---

## 💡 Por Que qwen2.5-coder Não Funciona?

O sufixo "-coder" indica **fine-tuning específico para código**:
- ✅ Excelente em gerar código de qualidade
- ✅ Segue padrões de programação
- ❌ **Pode ignorar meta-instruções** (ex: "não exiba no console")
- ❌ Treinado para "explicar" código (comportamento didático)

O modelo **base** (qwen2.5:32b) é mais **obediente** a instruções de workflow.

---

## 📝 Próximos Passos

1. **Escolher opção** (A = rápido, B = melhor)
2. **Executar comandos** acima
3. **Testar** com execução real
4. **Validar** que arquivos são escritos diretamente
5. **Confirmar** que console fica limpo

Qual opção você prefere? 🎯
