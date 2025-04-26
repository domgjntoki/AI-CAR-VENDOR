# Assistente IA para Vendas de Carros

Este projeto oferece um assistente com inteligência artificial que ajuda usuários a encontrar carros com base em suas preferências. O sistema consiste em uma API backend com FastAPI, banco de dados PostgreSQL e uma interface de chat via linha de comando.

## Pré-requisitos

- Docker e Docker Compose
- Python 3.11 ou superior (para execução local)
- Poetry (para execução local)
Considerando que o README está em português, vou adicionar a seção sobre configuração do ambiente também em português:


## Configuração do Ambiente

1. Copie o arquivo de ambiente de exemplo para criar seu próprio arquivo `.env`:
   ```bash
   cp .env.example .env


2. Atualize o arquivo `.env` com sua própria chave de API do OpenAI:
   ```
   OPENAI_API_KEY=sua_chave_de_api_openai_real
   ```

Observação: Uma chave de API OpenAI válida é necessária para que a aplicação funcione corretamente. Você pode obter uma chave de API registrando-se na [plataforma da OpenAI](https://platform.openai.com/).


## Como Iniciar

### 1. Iniciar o Banco de Dados e Backend

Inicie o banco de dados PostgreSQL e o serviço de backend usando Docker Compose:

```bash
docker compose up -d
```

Este comando inicia:
- Banco de dados PostgreSQL acessível na porta 5432
- Serviço de API backend acessível na porta 8000

### 2. Povoar o Banco de Dados com Dados de Exemplo

Para adicionar dados de carros de exemplo ao banco de dados:

```bash
# Aplica as migrações para criar a estrutura das tabelas no banco de dados
docker exec -it car_api poetry run alembic upgrade head

# Popula o banco com um catálogo de carros de exemplo para demonstração
docker exec -it car_api poetry run python scripts/populate_db.py
```

Este comando adiciona registros de teste de carros ao seu banco de dados.

### 3. Executar a Aplicação de Chat

Inicie a interface de chat interativa:

```bash
docker exec -it car_api poetry run python scripts/chat.py
```

## Usando a Interface de Chat

A aplicação de chat suporta consultas em linguagem natural para buscar carros. Exemplos:

- "Quero um Toyota vermelho de 2015 a 2020 por menos de $20.000"
- "Me mostre carros sedan automáticos"
- "Qual desses carros tem melhor consumo?"
- "Quero ver apenas os modelos mais recentes"

Digite `exit` para sair da aplicação.

## Desenvolvimento

Para executar os serviços localmente, use os comandos do `justfile`:

- `just run` - Iniciar o servidor FastAPI
- `just lint` - Executar linting
- `just migrate` - Executar migrações de banco de dados