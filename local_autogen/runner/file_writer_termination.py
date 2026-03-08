from pathlib import Path
from autogen_agentchat.base import TerminationCondition
from autogen_agentchat.messages import TextMessage, StopMessage


class FileWriterTermination(TerminationCondition):
    """
    Terminador personalizado que controla o limite de mensagens.
    A escrita de arquivos é feita exclusivamente pela ferramenta 'write_project_file'.
    """

    def __init__(self, output_dir: str = ".", max_messages: int = 20):
        self.output_dir = Path(output_dir)
        self.max_messages = max_messages
        self.message_count = 0
        self.created_files: list[str] = []

    async def __call__(self, messages: list[TextMessage]) -> StopMessage | None:
        """
        Verifica se deve terminar.

        Args:
            messages: Lista de mensagens recebidas

        Returns:
            StopMessage se deve terminar, None caso contrário
        """
        self.message_count += 1

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
