-- Criar schemas principais
CREATE SCHEMA IF NOT EXISTS "raw-layer";
CREATE SCHEMA IF NOT EXISTS "bronze-layer";
CREATE SCHEMA IF NOT EXISTS "silver-layer";
CREATE SCHEMA IF NOT EXISTS "gold-layer";

-- Criar sandbox para usuário
CREATE SCHEMA IF NOT EXISTS "sandbox-luan";

-- Opcional: dar permissões ao usuário airflow
GRANT USAGE ON SCHEMA "raw-layer" TO airflow;
GRANT USAGE ON SCHEMA "bronze-layer" TO airflow;
GRANT USAGE ON SCHEMA "silver-layer" TO airflow;
GRANT USAGE ON SCHEMA "gold-layer" TO airflow;
GRANT USAGE ON SCHEMA "sandbox-luan" TO airflow;