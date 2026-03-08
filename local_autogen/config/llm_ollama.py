import os
import requests
from typing import List, Any, Optional, Union, Mapping, Sequence
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.models.ollama._model_info import _MODEL_INFO
from autogen_core.models import (
    ChatCompletionClient,
    CreateResult,
    LLMMessage,
    ModelCapabilities,
)

class OllamaLoggingClient(OllamaChatCompletionClient):
    """
    Extensão do cliente Ollama que loga o tamanho do contexto de cada chamada.
    Permite visualizar a janela de contexto de cada agente.
    """
    async def create(
        self,
        messages: Sequence[LLMMessage],
        **kwargs: Any,
    ) -> CreateResult:
        # Calcular tamanho do contexto
        total_chars = 0
        msg_count = len(messages)
        
        for msg in messages:
            if hasattr(msg, "content"):
                if isinstance(msg.content, str):
                    total_chars += len(msg.content)
                elif isinstance(msg.content, list):
                    for item in msg.content:
                        if isinstance(item, str):
                            total_chars += len(item)
                        elif isinstance(item, dict) and "text" in item:
                            total_chars += len(item["text"])

        # Estimativa grosseira de tokens (1 token ~ 4 caracteres para PT/EN)
        est_tokens = total_chars // 4
        
        # Log visual discreto no console (estilo Claude Code: minimalista e cinza)
        num_ctx = self._raw_config.get('num_ctx', '32768')
        print(f"\033[90m[CONTEXTO] {msg_count} msgs | ~{est_tokens}/{num_ctx} tokens\033[0m")
        
        return await super().create(
            messages=messages,
            **kwargs
        )

def make_ollama_client(
    model_name: str = None,
    base_url: str = None,
    api_key: str = "not-needed",
    model_capabilities: dict = None,
    validate_connection: bool = True,
    model_params: dict = None
):
    """
    Cria um cliente Ollama com monitoramento de contexto.

    Args:
        model_name: Nome do modelo (ex: 'qwen3.5:35b'). Default: env OLLAMA_MODEL ou 'qwen3.5:35b'
        base_url: URL do servidor Ollama. Default: env OLLAMA_BASE_URL ou 'http://localhost:11434'
        api_key: API key (mantida para compatibilidade com interface)
        model_capabilities: Dicionário com capacidades do modelo. Se None, usa defaults do Qwen
        validate_connection: Se True, valida conexão com Ollama antes de criar cliente
        model_params: Parâmetros extras para o modelo (ex: temperature, num_ctx, repeat_penalty)

    Returns:
        OllamaChatCompletionClient configurado
    """
    # Configurações padrão com fallback para variáveis de ambiente
    model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen3.5:35b")
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Capabilities padrão para modelos Qwen (pode ser sobrescrito)
    default_capabilities = {
        'vision': False,
        'function_calling': True,
        'json_output': True,
        'family': 'qwen',
        'structured_output': True
    }

    model_info = model_capabilities or default_capabilities
    
    # Parâmetros padrão para otimização de velocidade
    # num_ctx: 32768 (conforme solicitado pelo usuário)
    # temperature: 0 para ser mais determinístico e rápido em decisões
    default_params = {
        "num_ctx": 32768,
        "temperature": 0.0,
        "num_predict": 4096,
        "repeat_penalty": 1.1
    }
    
    params = default_params.copy()
    if model_params:
        params.update(model_params)

    # Validar conexão com Ollama se solicitado
    if validate_connection:
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Não foi possível conectar ao Ollama em {base_url}. "
                f"Certifique-se de que o Ollama está rodando. Erro: {e}"
            )

    # Registrar o modelo personalizado no _MODEL_INFO (evita re-registro)
    if model_name not in _MODEL_INFO:
        _MODEL_INFO[model_name] = model_info

    client = OllamaLoggingClient(
        model=model_name,
        base_url=base_url,
        api_key=api_key,
        model_info=model_info,
        **params
    )

    return client


def make_ollama_qwen_client():
    """
    Função de conveniência para criar cliente Qwen (mantida para compatibilidade).
    """
    return make_ollama_client(model_name="qwen3.5:35b")
