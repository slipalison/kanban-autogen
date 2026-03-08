import os
import requests
import time
import sys
import asyncio
from typing import List, Any, Optional, Union, Mapping, Sequence, AsyncGenerator
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
    def _get_context_info(self, messages: Sequence[LLMMessage], is_streaming: bool = False) -> str:
        """Calcula metadados do contexto sem imprimir imediatamente."""
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
        mode_label = "STREAM" if is_streaming else "CREATE"
        return f"\033[90m[CONTEXTO] {mode_label} | {msg_count} msgs | ~{est_tokens}/{num_ctx} tokens | "

    async def _animate_wait(self, header: str, stop_event: asyncio.Event):
        """Tarefa de fundo que exibe um spinner animado no console."""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        try:
            while not stop_event.is_set():
                frame = frames[i % len(frames)]
                sys.stdout.write(f"\r{header}{frame} Processando...\033[0m")
                sys.stdout.flush()
                i += 1
                await asyncio.sleep(0.1)
            # Ao parar, finaliza a linha de forma limpa
            sys.stdout.write(f"\r{header}✅ Pronto!                         \n")
            sys.stdout.flush()
        except (asyncio.CancelledError, Exception):
            # Fallback para garantir que o console não fique em estado inconsistente
            sys.stdout.write("\n")
            sys.stdout.flush()

    async def create(
        self,
        messages: Sequence[LLMMessage],
        **kwargs: Any,
    ) -> CreateResult:
        header = self._get_context_info(messages, is_streaming=False)
        stop_event = asyncio.Event()
        anim_task = asyncio.create_task(self._animate_wait(header, stop_event))
        
        start_time = time.time()
        result = None
        try:
            result = await super().create(
                messages=messages,
                **kwargs
            )
            return result
        finally:
            stop_event.set()
            await anim_task
            if result:
                self._log_performance(result, time.time() - start_time, msg_count=len(messages))

    async def create_stream(
        self,
        messages: Sequence[LLMMessage],
        **kwargs: Any,
    ) -> AsyncGenerator[Union[str, CreateResult], None]:
        header = self._get_context_info(messages, is_streaming=True)
        stop_event = asyncio.Event()
        anim_task = asyncio.create_task(self._animate_wait(header, stop_event))
        
        start_time = time.time()
        ttft = None
        full_content = []
        
        try:
            async for chunk in super().create_stream(messages=messages, **kwargs):
                if ttft is None:
                    ttft = time.time() - start_time
                    stop_event.set()
                    # Aguardar brevemente para a tarefa de animação limpar a linha
                    await anim_task
                
                if isinstance(chunk, str):
                    full_content.append(chunk)
                elif isinstance(chunk, CreateResult):
                    full_content.append(chunk.content)
                yield chunk
        finally:
            if not stop_event.is_set():
                stop_event.set()
                await anim_task
            
            duration = time.time() - start_time
            if full_content:
                self._log_performance("".join(full_content), duration, ttft=ttft, msg_count=len(messages))

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
    
    # Parâmetros padrão para otimização de velocidade extrema na RTX 4090 + 7900X3D
    # num_ctx: 32768 (conforme solicitado pelo usuário)
    # num_batch: 2048 - Acelera drasticamente o processamento inicial (Prefill)
    # num_thread: 12 - Otimizado para os cores físicos do 7900X3D
    # f16_kv: True - Melhora performance do cache na GPU
    default_params = {
        "num_ctx": 32768,
        "temperature": 0.0,
        "num_predict": 4096,
        "repeat_penalty": 1.1,
        "num_batch": 2048,
        "num_thread": 12,
        "f16_kv": True,
        "num_gpu": 99,       # Garante uso total da GPU
        "low_vram": False    # Desativa se estiver com bastante VRAM (como na 4090)
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
