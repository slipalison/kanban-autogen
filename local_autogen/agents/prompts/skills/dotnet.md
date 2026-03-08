# COMANDOS .NET (CLI)

Este arquivo contém uma referência dos comandos `dotnet` mais comuns para auxiliar na criação, gerenciamento, build e execução de projetos .NET.

## 🚀 Comandos de Gerenciamento de Projeto

| Comando | Descrição | Exemplo |
| :--- | :--- | :--- |
| `dotnet new <TEMPLATE>` | Cria um novo projeto, arquivo ou solução. | `dotnet new console -n MyApp` |
| `dotnet sln` | Gerencia arquivos de solução (.sln). | `dotnet sln add src/Project.csproj` |
| `dotnet sln migrate` | Migra um arquivo de solução para uma versão mais recente. | `dotnet sln MySolution.sln migrate` |
| `dotnet new sln --format slnx` | Cria uma solução no novo formato XML (.slnx). | `dotnet new sln --format slnx` |
| `dotnet add package <PACKAGE>` | Adiciona uma referência de pacote NuGet ao projeto. | `dotnet add package Newtonsoft.Json` |
| `dotnet remove package <PACKAGE>`| Remove um pacote NuGet do projeto. | `dotnet remove package Newtonsoft.Json` |
| `dotnet add reference <PROJECT>` | Adiciona uma referência de projeto a projeto (P2P).| `dotnet add src/App.csproj reference lib/Lib.csproj` |
| `dotnet list package` | Lista os pacotes NuGet instalados. | `dotnet list package` |
| `dotnet list reference` | Lista as referências de projeto a projeto (P2P). | `dotnet list reference` |
| `dotnet remove reference <PROJECT>` | Remove uma referência de projeto a projeto (P2P). | `dotnet remove reference lib/Lib.csproj` |

## 🛠️ Comandos de Build e Execução

| Comando | Descrição | Exemplo |
| :--- | :--- | :--- |
| `dotnet restore` | Restaura as dependências e ferramentas de um projeto. | `dotnet restore` |
| `dotnet build` | Compila um projeto e todas as suas dependências. | `dotnet build --configuration Release` |
| `dotnet run` | Compila e executa o código-fonte imediatamente. | `dotnet run --project src/App.csproj` |
| `dotnet watch` | Executa um comando e reinicia quando arquivos mudam. | `dotnet watch run` |
| `dotnet publish` | Publica o aplicativo para implantação (self-contained/framework-dependent). | `dotnet publish -c Release -r win-x64` |
| `dotnet pack` | Cria um pacote NuGet a partir do código. | `dotnet pack --output ./dist` |
| `dotnet format` | Corrige problemas de estilo de código e convenções de nomenclatura. | `dotnet format` |
| `dotnet clean` | Limpa a saída de um build anterior. | `dotnet clean` |

## 🧪 Comandos de Teste

| Comando | Descrição | Exemplo |
| :--- | :--- | :--- |
| `dotnet test` | Executa testes unitários usando um test runner. | `dotnet test --logger "console;verbosity=detailed"` |

## 📦 Ferramentas e Diagnóstico

| Comando | Descrição | Exemplo |
| :--- | :--- | :--- |
| `dotnet tool install` | Instala uma ferramenta global ou local. | `dotnet tool install -g dotnet-ef` |
| `dotnet tool list` | Lista as ferramentas instaladas. | `dotnet tool list -g` |
| `dotnet tool update` | Atualiza uma ferramenta instalada. | `dotnet tool update -g dotnet-ef` |
| `dotnet tool uninstall` | Desinstala uma ferramenta instalada. | `dotnet tool uninstall -g dotnet-ef` |
| `dotnet nuget list source` | Lista as fontes de pacotes NuGet configuradas. | `dotnet nuget list source` |
| `dotnet dev-certs` | Gerencia certificados de desenvolvimento. | `dotnet dev-certs https --trust` |
| `dotnet --info` | Exibe informações detalhadas sobre a instalação do .NET. | `dotnet --info` |
| `dotnet --list-sdks` | Lista os SDKs instalados. | `dotnet --list-sdks` |
| `dotnet --list-runtimes` | Lista os runtimes instalados. | `dotnet --list-runtimes` |

## 💡 Dicas Úteis (PowerShell)

- Use o parâmetro `-n` ou `--name` para especificar o nome do projeto/output.
- O parâmetro `-o` ou `--output` define o diretório de saída.
- Para passar argumentos para a aplicação no `dotnet run`, use `--` seguido dos argumentos: `dotnet run -- arg1 arg2`.
- No PowerShell, comandos que alteram o sistema (como `dev-certs https --trust`) podem exigir privilégios de Administrador.
