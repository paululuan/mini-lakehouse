# Apache Airflow — Ambiente Docker Compose

Este repositório contém uma configuração pronta para rodar o **Apache Airflow 2.x** utilizando **Docker Compose**, seguindo as melhores práticas da Apache Foundation.


## 📌 Requisitos

Antes de começar, instale:

- Docker Engine  
- Docker Compose v2  
- Git

Em sistemas Linux, verifique as versões instaladas:

```bash
docker --version
docker compose version
```


## 📂 Estrutura do Projeto

```bash
airflow/
├── dags/                                     # Suas DAGs ficam aqui
│   └── <dag_context_load_frequency>/         # Pasta de cada DAG (padrão: dag+contexto+carga+frequência)
│       ├── <dag_context_load_frequency>.py   # Código da DAG
│       ├── dev.json                          # Configurações do ambiente Dev
│       └── prd.json                          # Configurações do ambiente PRD
├── logs/                                     # Logs gerados pelo Airflow (ignorado no Git)
├── plugins/                                  # Plugins opcionais
├── requirements.txt                          # Dependências extras do Airflow (opcional)
├── docker-compose.yml                        # Stack oficial da Apache Airflow
├── README.md                                 # Guia do Repositório
├── .env                                      # Variáveis de ambiente locais (NÃO versionar)
└── .env.example                              # Exemplo de variáveis para outros usuários
```


## ⚙️ Como subir os ambientes Dev e PRD localmente

O projeto suporta ambientes Dev e PRD usando Docker Compose. Cada ambiente lê automaticamente o JSON correspondente (dev.json ou prd.json) das DAGs com base na variável de ambiente ENVIRONMENT.

### 1️⃣ Subir o ambiente Dev

No diretório raiz do projeto, execute:

```bash
docker compose up -d airflow-dev-webserver airflow-dev-scheduler airflow-dev-worker airflow-dev-triggerer
```
- Webserver Dev disponível em: http://localhost:8080
- Variável de ambiente ENVIRONMENT=dev faz com que as DAGs leiam o dev.json.

### 2️⃣ Subir o ambiente PRD

No diretório raiz do projeto, execute:

```bash
docker compose up -d airflow-prd-webserver airflow-prd-scheduler airflow-prd-worker airflow-prd-triggerer
```
- Webserver Prd disponível em: http://localhost:8081
- Variável de ambiente ENVIRONMENT=prd faz com que as DAGs leiam o prd.json.

### 3️⃣ Parar os containers

```bash
docker compose down
```
- Para reiniciar qualquer ambiente, basta executar novamente os comandos 1️⃣ ou 2️⃣.
- Os logs permanecem na pasta logs/ (não versionada).

## 📝 Notas importantes

- Cada DAG deve ter `dev.json` e `prd.json` dentro da pasta da DAG, seguindo o padrão `<dag_context_load_frequency>`.  
- A DAG lê automaticamente o JSON correto com base na variável de ambiente `ENVIRONMENT`.  
- Novas DAGs podem ser adicionadas sem alterar o docker-compose, desde que sigam a estrutura de pasta e JSON.  
- Mantenha a pasta `logs/` no `.gitignore` para não versionar arquivos temporários.  
- Use `.env` para variáveis de ambiente locais (como senhas ou chaves), e não versionar esse arquivo.

### Exemplos de JSON

#### dev.json
```json
{
  "dag_context_load_frequency": {
    "schedule_interval": null,
    "raw_project": "sandbox-usuario",
    "bronze_project": "sandbox-usuario",
    "silver_project": "sandbox-usuario",
    "gold_project": "sandbox-usuario"
  }
}
```

#### prd.json
```json
{
  "dag_context_load_frequency": {
    "schedule_interval": "0 8 * * *",
    "raw_project": "raw-layer",
    "bronze_project": "bronze-layer",
    "silver_project": "silver-layer",
    "gold_project": "gold-layer"
  }
}
```

### Próximos passos sugeridos

- Adicionar suas DAGs seguindo o padrão <dag_context_load_frequency>.
- Testar a leitura dinâmica de dev.json e prd.json.
- Preparar CI/CD futuro, onde cada ambiente poderá ser atualizado separadamente.