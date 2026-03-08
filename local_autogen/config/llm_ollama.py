from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_ext.models.ollama._model_info import _MODEL_INFO

def make_ollama_qwen_client():
    model_name = "qwen3.5:35b"
    base_url = "http://localhost:11434"
    api_key = "not-needed"

    # Definir model_info completo para o modelo personalizado
    model_info = {
        'vision': False,
        'function_calling': True,
        'json_output': True,
        'family': 'qwen',
        'structured_output': True
    }

    # Registrar o modelo personalizado
    _MODEL_INFO[model_name] = model_info

    client = OllamaChatCompletionClient(
        model=model_name,
        base_url=base_url,
        api_key=api_key,
        model_info=model_info  # Passar model_info explicitamente
    )
    return client
