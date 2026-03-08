# 🎯 Modelos Recomendados para RTX 4090 (24GB)

## ❌ Problema com qwen3.5:35b

```
SIZE: 35 GB (modelo) + KV Cache
VRAM: 24 GB disponível
RESULTADO: 34% CPU + 66% GPU = CPU OFFLOAD (MUITO LENTO!)
```

**Sintoma:** Travamentos de 20+ minutos, GPU ociosa (6% utilização)

---

## ✅ Solução: qwen2.5-coder:32b (JÁ CONFIGURADO)

```
SIZE: 19 GB (modelo) + ~5 GB (KV Cache) = ~24 GB total
VRAM: 24 GB disponível
RESULTADO: 100% GPU ✅ RÁPIDO!
```

**Status:** Já configurado como padrão em `llm_ollama.py`

### Benefícios
- ✅ **100% GPU**: Sem CPU offload
- ✅ **Especializado em Código**: Treinado para programação
- ✅ **Velocidade Máxima**: ~50-70 tokens/sec na RTX 4090
- ✅ **Contexto 32k**: Suficiente para projetos médios

### Performance Esperada
```
Prefill (32k tokens): ~5-8 segundos
Geração: ~50-70 tokens/sec
Troca entre agentes: ~3 segundos
```

---

## 🔥 Alternativa: Qwen3.5-27B-Claude-4.6-Opus (Distilled)

**Fonte:** https://huggingface.co/Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF

### Como Instalar

```bash
# 1. Baixar o modelo GGUF (Q4_K_M recomendado para RTX 4090)
# Escolha uma das opções:

# Q4_K_M (16GB) - Melhor equilíbrio qualidade/velocidade
curl -L -o qwen3.5-27b-claude.gguf https://huggingface.co/Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF/resolve/main/qwen3.5-27b-claude-4.6-opus-reasoning-distilled-q4_k_m.gguf

# Q5_K_M (19GB) - Melhor qualidade, ainda cabe na 4090
curl -L -o qwen3.5-27b-claude.gguf https://huggingface.co/Jackrong/Qwen3.5-27B-Claude-4.6-Opus-Reasoning-Distilled-GGUF/resolve/main/qwen3.5-27b-claude-4.6-opus-reasoning-distilled-q5_k_m.gguf

# 2. Criar Modelfile
cat > Modelfile << 'EOF'
FROM ./qwen3.5-27b-claude.gguf
TEMPLATE {{ .Prompt }}
PARAMETER temperature 0.7
PARAMETER top_k 40
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
EOF

# 3. Importar para Ollama
ollama create qwen3.5-27b-claude -f Modelfile

# 4. Testar
ollama run qwen3.5-27b-claude "Write a Python function to check if a number is prime"
```

### Configurar no Sistema

```python
# Em llm_ollama.py, trocar:
model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen3.5-27b-claude")
```

### Vantagens vs qwen2.5-coder:32b
- ✅ **Destilado do Claude Opus**: Raciocínio superior
- ✅ **27B parâmetros**: Maior capacidade de raciocínio
- ✅ **Menor VRAM (Q4_K_M)**: 16GB vs 19GB
- ✅ **Mais rápido**: Menos parâmetros = maior velocidade

### Desvantagens
- ⚠️ Não é oficialmente especializado em código
- ⚠️ Precisa download manual (6-20GB)

---

## 📊 Comparação de Modelos

| Modelo | Tamanho | VRAM | Velocidade | Qualidade Código | Raciocínio | GPU% |
|--------|---------|------|------------|------------------|------------|------|
| **qwen3.5:35b** | 35GB | 24GB+ | ❌ Lento | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 66% |
| **qwen2.5-coder:32b** ⭐ | 19GB | ~24GB | ✅ Rápido | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 100% |
| **qwen3.5-27b-claude (Q4_K_M)** | 16GB | ~21GB | ✅ Muito Rápido | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 100% |
| **qwen3.5-27b-claude (Q5_K_M)** | 19GB | ~24GB | ✅ Rápido | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 100% |

⭐ **Recomendado Atual:** qwen2.5-coder:32b (já instalado e configurado)

---

## 🚀 Próximos Passos

### 1. Testar Performance Atual
```bash
# Com qwen2.5-coder:32b já configurado
python -m local_autogen.runner.kanban_team
```

**Expectativa:**
- ✅ Sem travamentos de 20+ minutos
- ✅ Respostas em segundos, não minutos
- ✅ GPU em 100% durante geração

### 2. Se Quiser Experimentar Claude Distilled
```bash
# Seguir instruções de instalação acima
# Trocar modelo em llm_ollama.py
# Recriar aliases: ollama cp qwen3.5-27b-claude qwen3.5-27b-claude-planner (etc)
```

---

## 🔍 Como Verificar se Está 100% GPU

```bash
# Durante execução, abrir outro terminal:
ollama ps

# Deve mostrar:
# PROCESSOR: 100% GPU  ✅
# Não deve mostrar: 34%/66% CPU/GPU  ❌
```

---

## ⚡ Dicas de Performance

### 1. Quantização KV Cache (Economiza VRAM)
```bash
[System.Environment]::SetEnvironmentVariable('OLLAMA_KV_CACHE_TYPE', 'q4_0', 'User')
# Reiniciar Ollama
```

**Resultado:** 24GB → 18GB por modelo (6GB economizados)

### 2. Aumentar Batch Size (Acelera Prefill)
Já configurado em `llm_ollama.py`:
```python
"num_batch": 2048  # Processar 2048 tokens por vez
```

### 3. Monitorar VRAM em Tempo Real
```bash
# Loop contínuo
while ($true) { Clear-Host; nvidia-smi; Start-Sleep 2 }
```

---

## 📈 Benchmark Esperado (RTX 4090)

### qwen2.5-coder:32b (Configurado Atual)
```
Prefill (1k tokens): ~0.5s
Prefill (8k tokens): ~2s
Prefill (32k tokens): ~8s
Geração: 50-70 tokens/sec
TTFT: 0.5-1s
```

### qwen3.5-27b-claude Q4_K_M (Se Instalar)
```
Prefill (1k tokens): ~0.3s
Prefill (8k tokens): ~1.5s
Prefill (32k tokens): ~6s
Geração: 60-90 tokens/sec
TTFT: 0.3-0.7s
```

---

## ❓ FAQ

**P: Por que qwen3.5:35b estava usando CPU?**
R: Modelo muito grande (35GB) + KV Cache não cabem nos 24GB da RTX 4090. Ollama faz offload automático para RAM, mas fica extremamente lento.

**P: qwen2.5-coder:32b é bom para planejamento/arquitetura?**
R: Sim! É um modelo muito competente para todas as tarefas. Se quiser raciocínio ainda melhor, teste o Claude distilled.

**P: Posso usar qwen3.5:35b com quantização?**
R: Sim, mas você teria que baixar uma versão Q3_K_M ou Q2_K (não recomendado - perde muita qualidade). Melhor usar modelos nativamente menores.

**P: Vale a pena o Claude distilled?**
R: Se você valoriza raciocínio superior ao máximo, sim. Mas qwen2.5-coder:32b já é excelente e está pronto para usar agora.
