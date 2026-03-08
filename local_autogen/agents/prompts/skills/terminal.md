USO DO TERMINAL:
Você tem acesso ao terminal PowerShell através da ferramenta `execute_shell_command`.

⚠️ IMPORTANTE (Sintaxe PowerShell):
- NÃO use sintaxe exclusiva de Bash, como expansão de chave (brace expansion) `mkdir -p dir/{sub1,sub2}`. O PowerShell NÃO suporta isso.
- Se precisar criar multiplas pastas, crie elas individualmente ou usando um laço/array no PowerShell, ou escreva os nomes por extenso.
- Exemplo Correto: `mkdir -p dir/sub1, dir/sub2` ou comandos em sequência separando por `;`.

Use-a para:
- Navegar e explorar a estrutura de pastas e validar arquivos existentes.
- Executar qualquer comando de terminal necessário para o desenvolvimento (dotnet, npm, git, python, docker, etc.).
- Realizar builds, testes e automações de ambiente.
- Instalar dependências e gerenciar pacotes.
- Executar tarefas de gerenciamento de infraestrutura ou automação geral.
- Verificar o estado do sistema ou de serviços locais.
- Gerenciar projetos e soluções de qualquer linguagem.
