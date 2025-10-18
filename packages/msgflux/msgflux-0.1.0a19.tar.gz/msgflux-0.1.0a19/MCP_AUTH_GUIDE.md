# MCP Authentication Guide

Este guia explica como usar os diferentes métodos de autenticação disponíveis no MCP (Model Context Protocol) integration do msgflux.

## Visão Geral

O msgflux MCP suporta múltiplos esquemas de autenticação para conectar com segurança a servidores MCP remotos:

- **Bearer Token**: Para tokens JWT, tokens de API simples
- **API Key**: Para chaves de API em headers customizados
- **Basic Auth**: Autenticação HTTP básica (username/password)
- **OAuth2**: Fluxo OAuth2 completo com refresh automático de tokens
- **Custom Headers**: Headers customizados para esquemas proprietários

## Providers Disponíveis

### 1. Bearer Token Authentication

Ideal para tokens JWT ou tokens Bearer padrão.

```python
from msgflux.protocols.mcp import MCPClient, BearerTokenAuth

# Uso básico
auth = BearerTokenAuth(token="your-jwt-token-here")

client = MCPClient.from_http(
    base_url="https://api.example.com/mcp",
    auth=auth
)
```

#### Com Auto-Refresh

```python
async def get_new_token():
    # Sua lógica para obter um novo token
    response = await your_auth_service.refresh_token()
    return response["access_token"]

auth = BearerTokenAuth(
    token="initial-token",
    expires_in=3600,  # Token expira em 1 hora
    refresh_callback=get_new_token
)

# O token será automaticamente renovado quando expirar
client = MCPClient.from_http(
    base_url="https://api.example.com/mcp",
    auth=auth
)
```

### 2. API Key Authentication

Para APIs que usam chaves em headers customizados.

```python
from msgflux.protocols.mcp import MCPClient, APIKeyAuth

# Com header padrão (X-API-Key)
auth = APIKeyAuth(api_key="your-api-key-12345")

# Com header customizado
auth = APIKeyAuth(
    api_key="your-api-key",
    header_name="X-Custom-Auth"
)

# Com prefixo (ex: "ApiKey your-key")
auth = APIKeyAuth(
    api_key="your-key",
    header_name="Authorization",
    key_prefix="ApiKey"
)

client = MCPClient.from_http(
    base_url="https://api.example.com/mcp",
    auth=auth
)
```

### 3. Basic Authentication

Autenticação HTTP básica com username e password.

```python
from msgflux.protocols.mcp import MCPClient, BasicAuth

auth = BasicAuth(
    username="your-username",
    password="your-password"
)

client = MCPClient.from_http(
    base_url="https://api.example.com/mcp",
    auth=auth
)
```

### 4. OAuth2 Authentication

Suporte completo para OAuth2 com refresh automático de tokens.

```python
from msgflux.protocols.mcp import MCPClient, OAuth2Auth

async def refresh_oauth_token(refresh_token: str) -> dict:
    """Callback para renovar tokens OAuth2."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://auth.example.com/oauth/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
            }
        )
        return response.json()

auth = OAuth2Auth(
    access_token="initial-access-token",
    refresh_token="your-refresh-token",
    expires_in=3600,  # 1 hora
    refresh_callback=refresh_oauth_token
)

client = MCPClient.from_http(
    base_url="https://api.example.com/mcp",
    auth=auth
)
```

### 5. Custom Header Authentication

Para esquemas de autenticação proprietários ou múltiplos headers.

```python
from msgflux.protocols.mcp import MCPClient, CustomHeaderAuth
import time
import hashlib

# Headers estáticos
auth = CustomHeaderAuth(headers={
    "X-API-Key": "your-api-key",
    "X-Client-ID": "your-client-id",
})

# Headers dinâmicos via callback
def generate_auth_headers():
    """Gera headers de autenticação dinamicamente."""
    timestamp = str(int(time.time()))
    signature = hashlib.sha256(
        f"{timestamp}:{SECRET_KEY}".encode()
    ).hexdigest()

    return {
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "X-Client-ID": "your-client-id",
    }

auth = CustomHeaderAuth(headers_callback=generate_auth_headers)

client = MCPClient.from_http(
    base_url="https://api.example.com/mcp",
    auth=auth
)
```

## Exemplos Práticos

### Exemplo 1: Conectar a MCP Server com JWT

```python
from msgflux.protocols.mcp import MCPClient, BearerTokenAuth

async def main():
    # Configurar autenticação
    auth = BearerTokenAuth(token=os.getenv("MCP_JWT_TOKEN"))

    # Criar cliente
    client = MCPClient.from_http(
        base_url="https://mcp-server.example.com",
        auth=auth
    )

    # Conectar e usar
    async with client:
        tools = await client.list_tools()
        print(f"Ferramentas disponíveis: {[t.name for t in tools]}")

        result = await client.call_tool(
            "execute_query",
            {"query": "SELECT * FROM users LIMIT 10"}
        )
        print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Exemplo 2: OAuth2 com Refresh Automático

```python
from msgflux.protocols.mcp import MCPClient, OAuth2Auth
import httpx

async def refresh_token_from_auth0(refresh_token: str) -> dict:
    """Renovar token via Auth0."""
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            "https://your-tenant.auth0.com/oauth/token",
            json={
                "grant_type": "refresh_token",
                "client_id": os.getenv("AUTH0_CLIENT_ID"),
                "client_secret": os.getenv("AUTH0_CLIENT_SECRET"),
                "refresh_token": refresh_token,
            }
        )
        data = response.json()
        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", refresh_token),
            "expires_in": data["expires_in"],
        }

async def main():
    # Obter tokens iniciais (login)
    initial_tokens = await login_and_get_tokens()

    # Configurar OAuth2 auth
    auth = OAuth2Auth(
        access_token=initial_tokens["access_token"],
        refresh_token=initial_tokens["refresh_token"],
        expires_in=initial_tokens["expires_in"],
        refresh_callback=refresh_token_from_auth0
    )

    # Cliente renovará automaticamente o token quando expirar
    client = MCPClient.from_http(
        base_url="https://api.example.com/mcp",
        auth=auth
    )

    async with client:
        # Mesmo após horas de uso, o token será renovado automaticamente
        for i in range(1000):
            result = await client.call_tool("process_data", {"id": i})
            await asyncio.sleep(10)  # Simular trabalho longo

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Exemplo 3: Integração com Agent

```python
from msgflux.nn.modules.agent import Agent
from msgflux.models import OpenAI
from msgflux.protocols.mcp import BearerTokenAuth

# Configurar autenticação MCP
mcp_auth = BearerTokenAuth(token=os.getenv("MCP_TOKEN"))

# Configurar servidor MCP com auth
mcp_servers = [
    {
        "name": "database",
        "transport": "http",
        "base_url": "https://db-mcp.example.com",
        "auth": mcp_auth,  # Auth provider
        "include_tools": ["query", "insert", "update"],
    }
]

# Criar agent com ferramentas MCP autenticadas
agent = Agent(
    name="DatabaseAgent",
    model=OpenAI(model="gpt-4"),
    mcp_servers=mcp_servers,
    system_prompt="You are a database assistant."
)

# Usar agent normalmente
response = agent("List all users in the database")
print(response)
```

### Exemplo 4: Múltiplos Servidores com Autenticações Diferentes

```python
from msgflux.protocols.mcp import (
    BearerTokenAuth,
    APIKeyAuth,
    BasicAuth,
)

# Diferentes auth para diferentes servidores
auth_server1 = BearerTokenAuth(token=os.getenv("SERVER1_TOKEN"))
auth_server2 = APIKeyAuth(api_key=os.getenv("SERVER2_KEY"))
auth_server3 = BasicAuth(
    username=os.getenv("SERVER3_USER"),
    password=os.getenv("SERVER3_PASS")
)

mcp_servers = [
    {
        "name": "analytics",
        "transport": "http",
        "base_url": "https://analytics.example.com/mcp",
        "auth": auth_server1,
    },
    {
        "name": "data_warehouse",
        "transport": "http",
        "base_url": "https://dw.example.com/mcp",
        "auth": auth_server2,
    },
    {
        "name": "legacy_system",
        "transport": "http",
        "base_url": "https://legacy.example.com/mcp",
        "auth": auth_server3,
    },
]

agent = Agent(
    name="MultiSourceAgent",
    model=OpenAI(model="gpt-4"),
    mcp_servers=mcp_servers
)
```

## Gerenciamento de Tokens

### Verificar Estado do Auth

```python
auth = BearerTokenAuth(token="test", expires_in=3600)

# Obter informações sobre autenticação
info = auth.get_auth_info()
print(f"Type: {info['type']}")
print(f"Expired: {info['expired']}")
print(f"Expires at: {info['expires_at']}")
print(f"Last refresh: {info['last_refresh']}")
```

### Atualizar Tokens Manualmente

```python
# Bearer Token
auth.update_token("new-token", expires_in=7200)

# API Key
auth.update_api_key("new-key")

# Basic Auth
auth.update_credentials("new-user", "new-pass")

# OAuth2
auth.update_tokens(
    access_token="new-access",
    refresh_token="new-refresh",
    expires_in=3600
)
```

## Segurança e Boas Práticas

### ✅ Boas Práticas

1. **Nunca hardcode credenciais no código**
   ```python
   # ✅ BOM
   auth = BearerTokenAuth(token=os.getenv("MCP_TOKEN"))

   # ❌ MAU
   auth = BearerTokenAuth(token="hardcoded-secret-123")
   ```

2. **Use variáveis de ambiente ou gerenciadores de secrets**
   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()

   auth = BearerTokenAuth(token=os.getenv("MCP_JWT_TOKEN"))
   ```

3. **Implemente refresh callbacks para tokens de longa duração**
   ```python
   auth = OAuth2Auth(
       access_token=initial_token,
       refresh_token=refresh_token,
       expires_in=3600,
       refresh_callback=your_refresh_function  # Importante!
   )
   ```

4. **Use HTTPS em produção**
   ```python
   # ✅ BOM
   client = MCPClient.from_http(
       base_url="https://api.example.com/mcp",  # HTTPS
       auth=auth
   )

   # ❌ MAU (apenas para desenvolvimento local)
   client = MCPClient.from_http(
       base_url="http://api.example.com/mcp",  # HTTP não seguro
       auth=auth
   )
   ```

5. **Trate erros de autenticação adequadamente**
   ```python
   from msgflux.protocols.mcp.exceptions import MCPError

   try:
       async with client:
           result = await client.call_tool("my_tool", {})
   except MCPError as e:
       if "401" in str(e) or "403" in str(e):
           # Erro de autenticação
           logger.error(f"Authentication failed: {e}")
           # Implementar lógica de re-autenticação
       else:
           raise
   ```

## Troubleshooting

### Problema: Token Expirando Muito Rápido

**Solução**: Use refresh callbacks

```python
async def refresh_token():
    # Sua lógica de refresh
    return new_token

auth = BearerTokenAuth(
    token=initial_token,
    expires_in=3600,
    refresh_callback=refresh_token
)
```

### Problema: Headers Customizados Não Sendo Enviados

**Solução**: Verifique se está usando CustomHeaderAuth

```python
# ❌ Não funciona
client = MCPClient.from_http(
    base_url="...",
    headers={"X-Custom": "value"}  # Headers estáticos apenas
)

# ✅ Funciona
auth = CustomHeaderAuth(headers={"X-Custom": "value"})
client = MCPClient.from_http(base_url="...", auth=auth)
```

### Problema: OAuth2 Refresh Falhando

**Solução**: Verifique o retorno do callback

```python
async def refresh_callback(refresh_token: str) -> dict:
    # Deve retornar dict com estas chaves:
    return {
        "access_token": "novo-token",      # Obrigatório
        "refresh_token": "novo-refresh",   # Opcional
        "expires_in": 3600                 # Opcional
    }
```

## Referência da API

Ver docstrings completas em cada classe auth para detalhes de parâmetros e retornos.

- `BearerTokenAuth`: src/msgflux/protocols/mcp/auth/bearer.py
- `APIKeyAuth`: src/msgflux/protocols/mcp/auth/apikey.py
- `BasicAuth`: src/msgflux/protocols/mcp/auth/basic.py
- `OAuth2Auth`: src/msgflux/protocols/mcp/auth/oauth2.py
- `CustomHeaderAuth`: src/msgflux/protocols/mcp/auth/custom.py
