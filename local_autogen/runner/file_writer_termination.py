from pathlib import Path
from autogen_agentchat.base import TerminationCondition
from autogen_agentchat.messages import TextMessage, StopMessage

from local_autogen.tools.file_writer_utils import extract_and_save_files


class FileWriterTermination(TerminationCondition):
    """
    Terminador personalizado que salva arquivos gerados pelo coder_agent.
    Processa mensagens do formato 'Arquivo: caminho' e cria os arquivos no disco.
    """

    def __init__(self, output_dir: str = ".", max_messages: int = 20):
        self.output_dir = Path(output_dir)
        self.max_messages = max_messages
        self.message_count = 0
        self.created_files: list[str] = []

    async def __call__(self, messages: list[TextMessage]) -> StopMessage | None:
        """
        Verifica se deve terminar e processa mensagens para salvar arquivos.

        Args:
            messages: Lista de mensagens recebidas

        Returns:
            StopMessage se deve terminar, None caso contrário
        """
        self.message_count += 1

        # Processar a última mensagem para salvar arquivos
        if messages:
            last_message = messages[-1]
            success, count, paths = extract_and_save_files(
                last_message.content, self.output_dir
            )
            if success:
                self.created_files.extend(paths)
                print(f"\n[FILE WRITER] Salvos {count} arquivo(s): {', '.join(paths)}\n")

        # Verificar limite de mensagens
        if self.message_count >= self.max_messages:
            return StopMessage("Limite de mensagens atingido. Gerando resumo final...")

        return None

    @property
    def terminated(self) -> bool:
        """Verifica se a condição de término foi atingida."""
        return self.message_count >= self.max_messages

    async def reset(self):
        """Reseta o estado do terminador."""
        self.message_count = 0
        self.created_files = []
