# Documentação msgflux

Este projeto usa MkDocs com Material theme para gerar a documentação a partir do arquivo `msgflux_zero_to_hero.py`.

## Estrutura

```
msgflux/
├── docs/                    # Arquivos Markdown da documentação
├── mkdocs.yml              # Configuração do MkDocs
├── .readthedocs.yaml       # Configuração do ReadTheDocs
├── .github/workflows/
│   └── docs.yml           # GitHub Action para deploy automático
└── convert_to_docs.py     # Script para converter o .py em docs
```

## Como usar

### 1. Regenerar a documentação do arquivo Python

Se você editar o `msgflux_zero_to_hero.py`, execute:

```bash
python3 convert_to_docs.py
```

Isso irá reprocessar o arquivo e atualizar os arquivos em `docs/`.

### 2. Visualizar localmente

Para ver a documentação localmente em modo desenvolvimento:

```bash
uv run --group doc mkdocs serve
```

Acesse: http://127.0.0.1:8000

### 3. Build da documentação

Para gerar o site estático:

```bash
uv run --group doc mkdocs build
```

Os arquivos serão gerados em `site/`.

## Deploy automático

### GitHub Pages

Quando você fizer push para as branches `main` ou `feature/init`, o GitHub Actions irá automaticamente:

1. Instalar as dependências com uv
2. Fazer build da documentação
3. Publicar no GitHub Pages (branch `gh-pages`)

**Para ativar o GitHub Pages:**

1. Vá em Settings → Pages
2. Em "Source", selecione "Deploy from a branch"
3. Escolha a branch `gh-pages` e pasta `/ (root)`
4. Clique em Save

Sua documentação ficará disponível em:
`https://<seu-usuario>.github.io/msgflux/`

### ReadTheDocs

O ReadTheDocs irá detectar automaticamente o arquivo `.readthedocs.yaml` e fazer o build.

**Para configurar:**

1. Acesse https://readthedocs.org
2. Importe o repositório msgflux
3. O ReadTheDocs irá usar as configurações do `.readthedocs.yaml`

Sua documentação ficará disponível em:
`https://msgflux.readthedocs.io/`

## Comandos úteis

```bash
# Instalar dependências de documentação
uv sync --group doc

# Servir localmente
uv run --group doc mkdocs serve

# Build
uv run --group doc mkdocs build

# Build com verificação de erros
uv run --group doc mkdocs build --strict

# Limpar build anterior
uv run --group doc mkdocs build --clean
```

## Personalização

### Editar tema/cores

Edite o arquivo `mkdocs.yml`, seção `theme`.

### Adicionar plugins

1. Adicione o plugin via uv:
   ```bash
   uv add <plugin-name> --group doc
   ```

2. Configure em `mkdocs.yml` na seção `plugins`.

### Reorganizar navegação

Edite a seção `nav` em `mkdocs.yml`.

## Troubleshooting

**Erro: "Config file 'mkdocs.yml' does not exist"**
- Certifique-se de estar na raiz do projeto

**Erro de build no GitHub Actions**
- Verifique se o `uv.lock` está commitado
- Veja os logs da Action em Actions → Deploy Documentation

**Página não atualiza no GitHub Pages**
- Aguarde alguns minutos (pode demorar até 5 minutos)
- Verifique se a Action rodou com sucesso
- Force refresh com Ctrl+Shift+R

## Referências

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [ReadTheDocs](https://docs.readthedocs.io/)
