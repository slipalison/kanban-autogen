import os
import requests
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.models.ollama._model_info import _MODEL_INFO


def make_ollama_client(
    model_name: str = None,
    base_url: str = None,
    api_key: str = "not-needed",
    model_capabilities: dict = None,
    validate_connection: bool = True,
    model_params: dict = None
):
    """
    Cria um cliente Ollama com configuração flexível.

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

    client = OllamaChatCompletionClient(
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
