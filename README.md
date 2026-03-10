# Trabalho Final NoSQL - Plataforma de Inteligencia de Mercado

Implementacao do exercicio com arquitetura poliglota:
- Redis (cache)
- MongoDB (data lake)
- Cassandra (serie temporal)
- Neo4j (rede de investidores)

## Requisitos
- Docker + Docker Compose
- Python 3.11+
- `uv`

## Estrutura
- `monitor.py`: execucao integrada em loop
- `docker-compose.yml`: infraestrutura dos 4 bancos
- `requirements.txt`: dependencias Python
- `src/`: modulos da aplicacao
- `scenarios/`: validacoes separadas por etapa

## Setup com uv (venv)
No diretorio `nosql/`:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Subir os bancos
```bash
docker compose up -d
```

Servicos e portas:
- Redis: `localhost:6379`
- MongoDB: `localhost:27017`
- Cassandra: `localhost:9042`
- Neo4j Browser: `http://localhost:7474`
- Neo4j Bolt: `localhost:7687`

Credenciais Neo4j padrao:
- usuario: `neo4j`
- senha: `password123`

## Variaveis de ambiente (opcional)
Defaults ja funcionam com o `docker-compose.yml`. Se quiser customizar:

```bash
export SYMBOL=BTCUSDT
export TTL_SECONDS=25
export INTERVAL_SECONDS=5

export REDIS_URL=redis://localhost:6379/0
export MONGO_URL=mongodb://localhost:27017
export CASSANDRA_HOST=localhost
export CASSANDRA_PORT=9042
export CASSANDRA_KEYSPACE=market_intel

export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password123
```

## Executar cenarios separados
No diretorio `nosql/`:

```bash
python scenarios/01_api_once.py
python scenarios/02_redis_cache.py
python scenarios/03_mongo_insert.py
python scenarios/04_cassandra_insert.py
python scenarios/05_neo4j_setup_match.py
python scenarios/06_full_cycle_dry.py
```

## Executar fluxo integrado (final)
```bash
python monitor.py
```

Comportamento esperado:
- Cache Hit: usa Redis e notifica investidores (sem gravar Mongo/Cassandra)
- Cache Miss: busca Binance, atualiza Redis, grava Mongo/Cassandra e notifica investidores

## Logs esperados no terminal
- `[REDIS] Cache Hit/Cache Miss`
- `[MONGO] Payload bruto salvo...`
- `[CASSANDRA] Preco gravado...`
- `[NEO4J] Notificando investidores...`

## Encerrar ambiente
```bash
docker compose down
```

Para remover volumes e dados:
```bash
docker compose down -v
```

## Solucao rapida de problemas
- Cassandra demora para ficar pronto no primeiro boot; aguarde alguns minutos.
- Se um banco nao estiver pronto, rode novamente o script apos os containers ficarem saudaveis.
- Se trocar senha/URI do Neo4j, atualize as variaveis de ambiente correspondentes.
