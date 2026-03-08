import re
from pathlib import Path
from typing import List, Tuple

# Padrão regex para identificar blocos de código formatados
FILE_BLOCK_PATTERN = re.compile(
    r'Arquivo:\s*(.+?)\s*\n+```\w*\n(.+?)```',
    re.DOTALL | re.MULTILINE
)


def write_project_file(file_path: str, content: str) -> str:
    """
    Grava o conteúdo em um arquivo dentro do diretório 'project/'.

    Args:
        file_path: Caminho relativo do arquivo (ex: 'src/main.py'). O prefixo 'project/' será tratado.
        content: O conteúdo completo do arquivo.

    Returns:
        Mensagem de confirmação da gravação.
    """
    output_dir = Path("project")
    
    # Limpar o caminho do arquivo se começar com 'project/'
    clean_path = file_path.strip()
    if clean_path.lower().startswith('project/'):
        clean_path = clean_path[len('project/'):]
    elif clean_path.lower().startswith('project\\'):
        clean_path = clean_path[len('project\\'):]

    clean_path = clean_path.lstrip('/')
    
    # Criar caminho completo
    full_path = output_dir / clean_path
    
    try:
        # Criar diretórios se não existirem
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escrever o arquivo
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
            
        return f"✅ Arquivo '{file_path}' gravado com sucesso em '{full_path}'."
    except Exception as e:
        return f"❌ Erro ao gravar o arquivo '{file_path}': {str(e)}"


def extract_and_save_files(content: str, output_dir: Path) -> Tuple[bool, int, List[str]]:
    """
    Extrai blocos de código de uma mensagem e salva como arquivos no disco.

    Args:
        content: Texto contendo blocos no formato 'Arquivo: caminho\\n```...```'
        output_dir: Diretório base para salvar os arquivos

    Returns:
        Tuple de (teve_sucesso, qtd_salvos, lista_de_caminhos)
    """
    matches = FILE_BLOCK_PATTERN.findall(content)

    if not matches:
        return False, 0, []

    saved_paths: List[str] = []

    for file_path, code_content in matches:
        file_path = file_path.strip()

        # Limpar o caminho do arquivo se começar com 'project/'
        clean_path = file_path
        if clean_path.lower().startswith('project/'):
            clean_path = clean_path[len('project/'):]
        elif clean_path.lower().startswith('project\\'):
            clean_path = clean_path[len('project\\'):]

        clean_path = clean_path.lstrip('/')

        # Criar caminho completo
        full_path = output_dir / clean_path

        # Criar diretórios se não existirem
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Escrever o arquivo
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(code_content.strip())

        saved_paths.append(str(full_path))

    return len(saved_paths) > 0, len(saved_paths), saved_paths
