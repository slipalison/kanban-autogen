import subprocess
import os

def execute_shell_command(command: str) -> str:
    """
    Executa um comando no terminal Windows (PowerShell) e retorna a saída combinada (stdout e stderr).
    
    Args:
        command: O comando completo a ser executado.
        
    Returns:
        A saída textual do comando.
    """
    try:
        # Usar powershell.exe explicitamente para garantir o comportamento esperado
        process = subprocess.run(
            ["powershell.exe", "-Command", command],
            capture_output=True,
            text=True,
            encoding='cp850', # Codificação padrão do Windows PT-BR (ou use 'utf-8' se preferir)
            timeout=60 # Limite de tempo para segurança
        )
        
        stdout = process.stdout
        stderr = process.stderr
        
        result = ""
        if stdout:
            result += stdout
        if stderr:
            result += f"\nERRO:\n{stderr}"
            
        if not result:
            result = "Comando executado com sucesso, mas sem saída."
            
        return result
        
    except subprocess.TimeoutExpired:
        return "Erro: O comando excedeu o tempo limite de 60 segundos."
    except Exception as e:
        return f"Erro ao executar o comando: {str(e)}"
