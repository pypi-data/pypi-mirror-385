# MCP (Model Context Protocol) Integration

A integração MCP permite que o msgflux se conecte a servidores MCP e use suas ferramentas remotas como se fossem ferramentas locais.

## Características

- ✅ **Múltiplos Transporte**: Suporte para stdio (subprocess) e HTTP/SSE
- ✅ **Múltiplos Servidores**: Conecte-se a vários servidores MCP simultaneamente
- ✅ **Namespace**: Ferramentas MCP são prefixadas com namespace para evitar conflitos
- ✅ **Filtros**: Inclua ou exclua ferramentas específicas de cada servidor
- ✅ **Tool Config**: Aplique configurações como `inject_vars`, `return_direct`, etc.
- ✅ **Async/Sync**: Suporte completo para operações síncronas e assíncronas
- ✅ **Zero Dependências**: httpx é opcional, apenas necessário para HTTP transport
- ✅ **Auto-Reconnect**: Reconexão automática com backoff exponencial
- ✅ **Connection Pooling**: Pool de conexões HTTP para melhor performance
- ✅ **Telemetria**: Instrumentação OpenTelemetry para observabilidade completa

## Instalação

```bash
# Para usar MCP com HTTP transport
pip install msgflux[httpx]

# Para usar apenas stdio transport (sem dependências extras)
pip install msgflux
```

## Uso Básico

### Stdio Transport (Subprocess Local)

```python
from msgflux.nn.modules import Agent
from msgflux.models import OpenAI

agent = Agent(
    name="assistant",
    model=OpenAI("gpt-4"),
    mcp_servers=[
        {
            "name": "fs",  # Namespace
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem"],
            "cwd": "/workspace"
        }
    ]
)

response = agent("List files in the current directory")
```

### HTTP Transport (Servidor Remoto)

```python
agent = Agent(
    name="assistant",
    model=OpenAI("gpt-4"),
    mcp_servers=[
        {
            "name": "api",
            "transport": "http",
            "base_url": "http://localhost:8080",
            "headers": {"Authorization": "Bearer token"}
        }
    ]
)
```

## Configuração de Servidores

### Parâmetros Comuns

- `name` (obrigatório): Namespace para as ferramentas deste servidor
- `transport` (obrigatório): `"stdio"` ou `"http"`
- `include_tools` (opcional): Lista de ferramentas para incluir
- `exclude_tools` (opcional): Lista de ferramentas para excluir
- `tool_config` (opcional): Configurações por ferramenta

### Stdio Transport

```python
{
    "name": "server_name",
    "transport": "stdio",
    "command": "comando",           # Comando para executar
    "args": ["arg1", "arg2"],       # Argumentos do comando
    "cwd": "/path",                 # Diretório de trabalho
    "env": {"VAR": "value"},        # Variáveis de ambiente
    "timeout": 30.0                 # Timeout em segundos
}
```

### HTTP Transport

```python
{
    "name": "server_name",
    "transport": "http",
    "base_url": "http://host:port",
    "headers": {"Header": "value"},
    "timeout": 30.0
}
```

## Filtros de Ferramentas

### Incluir Apenas Ferramentas Específicas

```python
mcp_servers=[
    {
        "name": "fs",
        "transport": "stdio",
        "command": "mcp-server-fs",
        "include_tools": ["read_file", "write_file"]  # Apenas estas
    }
]
```

### Excluir Ferramentas Específicas

```python
mcp_servers=[
    {
        "name": "git",
        "transport": "stdio",
        "command": "mcp-server-git",
        "exclude_tools": ["git_push", "git_force_push"]  # Todas exceto estas
    }
]
```

## Tool Config

Aplique configurações específicas para cada ferramenta MCP:

### Inject Vars

Injeta variáveis do contexto nos parâmetros da ferramenta:

```python
{
    "name": "fs",
    "transport": "stdio",
    "command": "mcp-server-fs",
    "tool_config": {
        "read_file": {
            "inject_vars": ["user_id", "session_id"]  # Injeta vars específicas
        },
        "advanced_tool": {
            "inject_vars": True  # Injeta todas as vars como "vars"
        }
    }
}
```

### Return Direct

Retorna resultado da ferramenta diretamente sem processamento adicional:

```python
{
    "tool_config": {
        "get_data": {
            "return_direct": True
        }
    }
}
```

## Namespace

As ferramentas MCP são automaticamente prefixadas com o namespace do servidor para evitar conflitos:

```python
# Servidor com namespace "fs"
mcp_servers=[{"name": "fs", ...}]

# Ferramentas ficam disponíveis como:
# - fs__read_file
# - fs__write_file
# - fs__list_directory
```

O modelo vê essas ferramentas nos schemas e pode chamá-las normalmente. Internamente, o msgflux detecta o prefixo `__` e roteia para o cliente MCP correto.

## Múltiplos Servidores

Você pode conectar a vários servidores MCP simultaneamente:

```python
agent = Agent(
    name="super_assistant",
    model=model,
    mcp_servers=[
        {"name": "fs", "transport": "stdio", "command": "mcp-server-fs"},
        {"name": "git", "transport": "stdio", "command": "mcp-server-git"},
        {"name": "api", "transport": "http", "base_url": "http://api.example.com"}
    ]
)

# Agent tem acesso a:
# - fs__* (ferramentas do filesystem)
# - git__* (ferramentas do git)
# - api__* (ferramentas do API)
```

## Combinando com Ferramentas Locais

Ferramentas MCP funcionam perfeitamente ao lado de ferramentas locais:

```python
def local_tool(x: int) -> int:
    """Local tool that doubles a number."""
    return x * 2

agent = Agent(
    name="hybrid_assistant",
    model=model,
    tools=[local_tool],  # Ferramenta local
    mcp_servers=[        # Ferramentas remotas
        {"name": "fs", "transport": "stdio", "command": "mcp-server-fs"}
    ]
)

# Agent tem acesso a:
# - local_tool (local)
# - fs__read_file (remota MCP)
# - fs__write_file (remota MCP)
```

## Arquitetura

```
Agent
  └─> ToolLibrary
       ├─> Local Tools (tool.py)
       └─> MCP Clients
            ├─> Client 1 (namespace "fs")
            │    ├─> Transport (stdio/HTTP)
            │    └─> Tools: read_file, write_file
            └─> Client 2 (namespace "git")
                 ├─> Transport (stdio)
                 └─> Tools: git_status, git_commit
```

## API Avançada

### Uso Direto do MCPClient

Se você quiser usar o cliente MCP diretamente sem Agent:

```python
from msgflux.protocols.mcp import MCPClient

# Stdio
client = MCPClient.from_stdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem"]
)

# HTTP
client = MCPClient.from_http(
    base_url="http://localhost:8080"
)

# Usar com context manager
async with client:
    tools = await client.list_tools()
    result = await client.call_tool("read_file", {"path": "/tmp/test.txt"})
    print(result)
```

### Schemas

Obtenha schemas de todas as ferramentas (local + MCP):

```python
agent = Agent(...)
schemas = agent.tool_library.get_tool_json_schemas()

# Schemas incluem tanto ferramentas locais quanto MCP
for schema in schemas:
    print(schema["function"]["name"])
    # local_tool
    # fs__read_file
    # fs__write_file
```

## Tratamento de Erros

Erros de ferramentas MCP são capturados e retornados como `ToolCall` com campo `error`:

```python
# Se uma ferramenta MCP falhar:
result = agent("Read a non-existent file")

# O erro é capturado e retornado estruturadamente
# Não quebra a execução do Agent
```

## Performance

- **Conexões**: Clientes MCP são inicializados uma vez na criação do Agent
- **Cache**: Schemas de ferramentas são cacheados
- **Async**: Operações MCP são totalmente assíncronas
- **Reconnect**: Não há reconexão automática (ainda)

## Reconexão Automática

Configure o comportamento de reconexão automática:

```python
mcp_servers=[
    {
        "name": "fs",
        "transport": "stdio",
        "command": "mcp-server-fs",

        # Reconnection settings
        "max_retries": 5,  # Tenta até 5 vezes
        "retry_delay": 2.0,  # Delay inicial de 2s (backoff exponencial)
        "auto_reconnect": True,  # Reconecta automaticamente
    }
]
```

**Backoff Exponencial:**
- Tentativa 1: Delay de 2s
- Tentativa 2: Delay de 4s
- Tentativa 3: Delay de 8s
- Tentativa 4: Delay de 16s
- Tentativa 5: Delay de 32s
- Se todas falharem: `MCPConnectionError`

## Connection Pooling (HTTP)

Configure pool de conexões para melhor performance:

```python
mcp_servers=[
    {
        "name": "api",
        "transport": "http",
        "base_url": "http://localhost:8080",

        # Connection pooling
        "pool_limits": {
            "max_connections": 200,  # Máximo de conexões totais
            "max_keepalive_connections": 50  # Conexões keepalive
        }
    }
]
```

**Benefícios:**
- Reutiliza conexões TCP
- Reduz latência de handshake
- Melhora throughput
- Suporta alta concorrência

## Telemetria e Observability

A integração MCP usa OpenTelemetry para observabilidade completa:

### Ativar Telemetria

```bash
# Environment variables
export MSGFLUX_TELEMETRY_REQUIRES_TRACE=true
export MSGFLUX_TELEMETRY_SPAN_EXPORTER_TYPE=console  # ou 'otlp'
export MSGFLUX_TELEMETRY_OTLP_ENDPOINT=http://localhost:4318/v1/traces
```

### Spans Criados

Operações MCP geram os seguintes spans:

- **mcp.client.connect**: Conexão ao servidor
  - `mcp.operation`: "connect"
  - `mcp.connection_attempts`: Número de tentativas
  - `mcp.retry_delay`: Delay entre tentativas

- **mcp.client.list_tools**: Listagem de ferramentas
  - `mcp.operation`: "list_tools"
  - `mcp.tools_count`: Número de ferramentas

- **mcp.client.call_tool**: Execução de ferramenta
  - `mcp.operation`: "call_tool"
  - `mcp.tool.name`: Nome da ferramenta
  - `mcp.tool.duration_ms`: Duração da execução
  - `mcp.tool.error`: Mensagem de erro (se houver)

- **mcp.client.list_resources**: Listagem de recursos
  - `mcp.operation`: "list_resources"

### Exporters Suportados

1. **Console**: Para desenvolvimento e debug
2. **OTLP**: Para Jaeger, Zipkin, etc.

### Exemplo com Jaeger

```bash
# Iniciar Jaeger
docker run -d -p 16686:16686 -p 4318:4318 jaegertracing/all-in-one:latest

# Configurar variáveis
export MSGFLUX_TELEMETRY_REQUIRES_TRACE=true
export MSGFLUX_TELEMETRY_SPAN_EXPORTER_TYPE=otlp
export MSGFLUX_TELEMETRY_OTLP_ENDPOINT=http://localhost:4318/v1/traces

# Executar código
python your_script.py

# Acessar UI: http://localhost:16686
```

## Limitações

- Não há suporte a MCP resources (implementação futura)
- Não há suporte a MCP prompts (implementação futura)
- Stdio transport não suporta input interativo
- HTTP transport não suporta WebSocket (apenas SSE)

## Roadmap

- [ ] Suporte a MCP Resources
- [ ] Suporte a MCP Prompts
- [ ] Circuit breaker pattern
- [ ] Health checks automáticos
- [ ] Metrics customizados

## Exemplos

Veja `examples/mcp_integration_example.py` para exemplos completos.

## Referências

- [Especificação MCP](https://modelcontextprotocol.io/specification/2025-03-26)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers](https://github.com/modelcontextprotocol)
