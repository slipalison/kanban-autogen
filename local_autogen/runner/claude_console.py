import sys
from typing import AsyncIterable, Any, Union
from autogen_agentchat.messages import (
    TextMessage, 
    StopMessage,
    HandoffMessage,
    ModelClientStreamingChunkEvent,
    ThoughtEvent
)

# Como os eventos de ferramentas podem variar, vamos usar nomes genéricos 
# e testar via hasattr ou isinstance se possível

class ClaudeConsole:
    """
    Um formatador de console que imita o estilo limpo e profissional do Claude Code.
    Substitui o Console padrão do AutoGen para uma experiência mais visual.
    """
    
    # Cores e Ícones por Agente
    AGENT_THEMES = {
        "planner": ("\033[94m", "📋"),        # Bright Blue
        "architect": ("\033[96m", "📐"),      # Bright Cyan
        "coder": ("\033[93m", "💻"),          # Bright Yellow
        "reviewer": ("\033[95m", "🔍"),       # Bright Magenta
        "infrastructure": ("\033[92m", "🏗️"),  # Bright Green
        "user": ("\033[97m", "👤"),           # White
        "selector": ("\033[90m", "🤖"),        # Gray (Seletor de Turnos)
    }
    
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[90m"
    ITALIC = "\033[3m"
    SUCCESS = "\033[92m"
    ERROR = "\033[91m"
    TOOL = "\033[96m"

    def __init__(self, stream: AsyncIterable[Any]):
        self.stream = stream
        self._current_source = None
        self._has_printed_header = False

    async def run(self):
        """Consome o stream e imprime formatado no console."""
        async for message in self.stream:
            self._print_message(message)

    def _print_message(self, message: Any):
        # Muitas vezes o que vem no stream é um evento que contém a mensagem
        msg_obj = message
        if hasattr(message, "message") and message.message is not None:
            msg_obj = message.message
        
        class_name = type(msg_obj).__name__

        if isinstance(msg_obj, ModelClientStreamingChunkEvent):
            self._handle_streaming_chunk(msg_obj)
        elif isinstance(msg_obj, ThoughtEvent):
            self._handle_thought(msg_obj)
        elif isinstance(msg_obj, TextMessage):
            self._handle_text_message(msg_obj)
        elif "ToolCallRequest" in class_name or "FunctionCall" in class_name:
            self._handle_tool_call(msg_obj)
        elif "ToolCallExecution" in class_name or "ToolCallSummary" in class_name:
            self._handle_tool_result(msg_obj)
        elif isinstance(msg_obj, StopMessage):
            self._handle_stop_message(msg_obj)
        elif isinstance(msg_obj, str):
            print(f"{self.DIM}{msg_obj}{self.RESET}")

    def _get_theme(self, source: str):
        source_lower = str(source).lower()
        for key, theme in self.AGENT_THEMES.items():
            if key in source_lower:
                return theme
        return ("\033[97m", "🤖") # Default

    def _print_header(self, source: str):
        if self._current_source == source and self._has_printed_header:
            return
            
        color, icon = self._get_theme(source)
        # Divisor sutil entre mensagens de agentes
        print(f"\n{self.DIM}─" * 60 + f"{self.RESET}")
        # Cabeçalho do Agente
        print(f"{color}{self.BOLD}{icon} {source.upper()}{self.RESET}")
        self._current_source = source
        self._has_printed_header = True

    def _handle_streaming_chunk(self, msg: ModelClientStreamingChunkEvent):
        if not self._has_printed_header:
            self._print_header(msg.source)
            # Indentação inicial apenas no começo da resposta
            sys.stdout.write("  ")
        
        # Substituir novas linhas para manter a indentação em cada linha do stream
        content = msg.content
        if "\n" in content:
            content = content.replace("\n", "\n  ")
            
        sys.stdout.write(content)
        sys.stdout.flush()

    def _handle_thought(self, msg: ThoughtEvent):
        self._print_header(msg.source)
        # Pensamentos geralmente são prefixados ou formatados diferentemente
        content = msg.content.strip()
        if content:
            print(f"\n  {self.DIM}{self.ITALIC}💭 Pensamento: {content}{self.RESET}")

    def _handle_text_message(self, msg: TextMessage):
        # Se já imprimimos os chunks, a mensagem completa pode vir vazia ou redundante
        # Mas no AutoGen, a TextMessage final contém o texto completo.
        # Se já imprimimos via chunks, não queremos imprimir tudo de novo.
        
        if self._current_source == msg.source and self._has_printed_header:
            # Já imprimimos chunks deste agente. Apenas finalizamos com uma nova linha.
            print("\n")
            self._has_printed_header = False # Reset para a próxima mensagem
            return

        self._print_header(msg.source)
        
        # Conteúdo (Pensamentos/Respostas)
        content = msg.content.strip()
        if content:
            # Indentar conteúdo para ficar mais legível
            lines = content.split('\n')
            for line in lines:
                print(f"  {line}")
        print("")
        self._has_printed_header = False

    def _handle_tool_call(self, msg: Any):
        # Tenta extrair o source e o conteúdo (lista de chamadas)
        source = getattr(msg, "source", "unknown")
        color, _ = self._get_theme(source)
        
        # O conteúdo costuma estar em .content ou .tool_calls
        calls = getattr(msg, "content", [])
        if not isinstance(calls, list):
            calls = [calls]
            
        for call in calls:
            # Pode ser um dict ou um objeto com atributos
            if isinstance(call, dict):
                tool_name = call.get("name", "unknown_tool")
                args = call.get("arguments", {})
            else:
                tool_name = getattr(call, "name", "unknown_tool")
                args = getattr(call, "arguments", {})
            
            print(f"  {self.TOOL}🔨 Executando {self.BOLD}{tool_name}{self.RESET}{self.TOOL}...")
            if args:
                import json
                try:
                    args_str = json.dumps(args, ensure_ascii=False) if isinstance(args, dict) else str(args)
                    if len(args_str) > 100:
                        args_str = args_str[:97] + "..."
                    print(f"    {self.DIM}{self.ITALIC}args: {args_str}{self.RESET}")
                except:
                    pass

    def _handle_tool_result(self, msg: Any):
        # O conteúdo costuma estar em .content ou .results
        results = getattr(msg, "content", [])
        if not isinstance(results, list):
            results = [results]
            
        for result in results:
            if isinstance(result, dict):
                output = str(result.get("content", "")).strip()
                is_error = result.get("is_error", False)
            else:
                # Pode ser um ToolCallSummaryMessage ou similar
                output = str(getattr(result, "content", "")).strip()
                is_error = False # Por default
            
            status_icon = "❌ " if is_error else "✅ "
            status_color = self.ERROR if is_error else self.SUCCESS
            
            # Se o conteúdo já começa com um ícone, não repetimos o ícone do status
            if output.startswith("✅") or output.startswith("❌"):
                status_icon = ""
            
            lines = output.split('\n')
            if len(lines) > 8:
                summary = "\n".join(lines[:4]) + f"\n{self.DIM}... ({len(lines)-4} linhas omitidas){self.RESET}"
            else:
                summary = output
                
            if summary:
                # Indentar o resultado
                indented = summary.replace('\n', '\n    ')
                print(f"    {status_color}{status_icon}{indented}{self.RESET}")
            else:
                print(f"    {status_color}{status_icon} (Sucesso sem saída){self.RESET}")
        print("")

    def _handle_stop_message(self, msg: StopMessage):
        print(f"\n{self.SUCCESS}{self.BOLD}🏁 FINALIZADO: {msg.content}{self.RESET}\n")
