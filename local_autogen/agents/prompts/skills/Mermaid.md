# Mermaid.js - Guia Rápido de Sintaxe

### 1. Flowchart (Diagramas de Fluxo)
```mermaid
flowchart TD
    A[Início] --> B{Decisão}
    B -- Sim --> C[Ação 1]
    B -- Não --> D[Ação 2]
    C --> E((Fim))
    subgraph Módulo
        D
    end
```
- **Direções:** TD (Top-Down), LR (Left-Right), BT, RL.
- **Formas:** `[]` Retângulo, `()` Arredondado, `{}` Losango, `[[]]` Sub-rotina, `[()]` Banco de Dados.

### 2. Sequence Diagram (Diagramas de Sequência)
```mermaid
sequenceDiagram
    participant A as Cliente
    actor B as Usuário
    A->>+Server: Request
    Server-->>-A: Response
    alt Sucesso
        A->>B: Mostra dados
    else Erro
        A->>B: Alerta
    end
```
- **Mensagens:** `->>` Sólida, `-->>` Pontilhada, `-)` Assíncrona.
- **Blocos:** `alt/else`, `loop`, `opt`, `par`.

### 3. Class Diagram (Diagramas de Classe)
```mermaid
classDiagram
    class User {
        +String Name
        -Guid Id
        +Login() bool
    }
    User <|-- Admin : Herança
    User *-- Profile : Composição
```
- **Relações:** `<|--` Herança, `*--` Composição, `o--` Agregação, `-->` Associação.
- **Visibilidade:** `+` Public, `-` Private, `#` Protected.

### 4. Entity Relationship (ER)
```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string email
    }
```
- **Cardinalidade:** `||--||` (1:1), `||--o{` (1:N), `}o--o{` (N:M).

### 5. Outros
- **State:** `stateDiagram-v2`, `[*] --> State1`, `State1 --> [*]`.
- **Mindmap:** `mindmap`, `root`, `child`.
- **Gantt:** `gantt`, `section`, `task :active, a1, 2024-01-01, 30d`.
