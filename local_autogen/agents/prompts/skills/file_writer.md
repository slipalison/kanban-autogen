### ESCRITA DE ARQUIVOS (write_project_file)

Para criar ou modificar arquivos no projeto, utilize OBRIGATORIAMENTE a ferramenta `write_project_file`.

**Instruções de Uso:**
1. **file_path:** Forneça o caminho relativo do arquivo começando com 'project/'. Ex: `project/src/App.cs`.
2. **content:** Forneça o conteúdo completo e atualizado do arquivo.

**Regra de Ouro (Performance):**
- **EXECUÇÃO IMEDIATA:** Se você decidiu criar ou alterar um arquivo, emita a chamada da ferramenta `write_project_file` IMEDIATAMENTE. 
- **NÃO DESCREVA** o conteúdo do arquivo no chat (console) antes ou depois da chamada. 
- No chat, escreva apenas uma breve confirmação final após a ferramenta retornar sucesso. Ex: "✅ Arquivo 'project/...' gerado com o propósito de...".
- Isso economiza tempo de processamento e mantém o console limpo.
