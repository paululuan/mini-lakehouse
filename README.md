# Apache Airflow — Ambiente Docker Compose

Este repositório contém uma configuração pronta para rodar o **Apache Airflow 2.x** utilizando **Docker Compose**, seguindo as melhores práticas da Apache Foundation.

## 📌 Requisitos

Antes de começar, instale:

- Docker Engine  
- Docker Compose v2  
- Git

Em sistemas Linux, use:

```bash
docker --version
docker compose version

airflow/
├── dags/                 # Suas DAGs ficam aqui
├── logs/                 # Logs gerados pelo Airflow (ignorado no Git)
├── plugins/              # Plugins opcionais
├── requirements.txt      # Dependências extras do Airflow (opcional)
├── docker-compose.yaml   # Stack oficial da Apache
├── .env                  # Variáveis de ambiente locais (NÃO versionar)
└── .env.example          # Exemplo de variáveis para outros usuários
