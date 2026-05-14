meu_app_data_pipeline/
│
├── app/                              # Camada View e Controller (Flask)
│   ├── __init__.py
│   ├── controllers/                  # Controller - Lógica de negócio
│   │   ├── __init__.py
│   │   ├── dagster_controller.py
│   │   ├── dbt_controller.py
│   │   └── pipeline_controller.py
│   │
│   ├── models/                       # Model - Dados e schemas
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   └── repositories.py
│   │
│   ├── views/                        # View - Templates e rotas
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── templates/
│   │   │   ├── base.html
│   │   │   ├── dashboard/
│   │   │   │   ├── index.html
│   │   │   │   ├── pipelines.html
│   │   │   │   └── quality.html
│   │   │   ├── dbt/
│   │   │   │   ├── run_models.html
│   │   │   │   └── docs_viewer.html
│   │   │   └── errors/
│   │   │       ├── 404.html
│   │   │       └── 500.html
│   │   └── static/
│   │       ├── css/
│   │       │   └── style.css
│   │       ├── js/
│   │       │   └── main.js
│   │       └── images/
│   │
│   ├── services/                     # Serviços auxiliares
│   │   ├── __init__.py
│   │   ├── notification_service.py
│   │   ├── monitoring_service.py
│   │   └── validation_service.py
│   │
│   ├── utils/                        # Utilitários
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── decorators.py
│   │   └── helpers.py
│   │
│   ├── config.py                     # Configurações da aplicação
│   └── extensions.py                 # Extensões Flask
│
├── dagster_project/                  # Dagster pipelines
│   ├── __init__.py
│   ├── pipelines/                    # Pipelines principais
│   │   ├── __init__.py
│   │   ├── etl_pipeline.py
│   │   ├── quality_pipeline.py
│   │   └── reporting_pipeline.py
│   │
│   ├── assets/                       # Assets Dagster
│   │   ├── __init__.py
│   │   ├── raw_assets.py
│   │   ├── transformed_assets.py
│   │   └── business_assets.py
│   │
│   ├── ops/                          # Operações individuais
│   │   ├── __init__.py
│   │   ├── extract_ops.py
│   │   ├── transform_ops.py
│   │   └── load_ops.py
│   │
│   ├── jobs/                         # Jobs orquestrados
│   │   ├── __init__.py
│   │   ├── daily_etl_job.py
│   │   ├── hourly_quality_job.py
│   │   └── weekly_report_job.py
│   │
│   ├── schedules/                    # Agendamentos
│   │   ├── __init__.py
│   │   ├── daily_schedules.py
│   │   └── custom_schedules.py
│   │
│   ├── sensors/                      # Sensores para triggers
│   │   ├── __init__.py
│   │   ├── file_sensor.py
│   │   └── time_sensor.py
│   │
│   └── repositories/                 # Repositórios de dados
│       ├── __init__.py
│       ├── source_repo.py
│       └── target_repo.py
│
├── dbt_project/                      # DBT transformations
│   ├── models/                       # Modelos DBT
│   │   ├── staging/                  # Camada staging
│   │   │   ├── __init__.py
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_products.sql
│   │   │   └── schema.yml
│   │   │
│   │   ├── intermediate/             # Camada intermediária
│   │   │   ├── __init__.py
│   │   │   ├── int_order_items.sql
│   │   │   ├── int_customer_orders.sql
│   │   │   └── schema.yml
│   │   │
│   │   ├── marts/                    # Camada de negócio
│   │   │   ├── core/
│   │   │   │   ├── dim_customers.sql
│   │   │   │   ├── dim_products.sql
│   │   │   │   ├── fact_orders.sql
│   │   │   │   └── schema.yml
│   │   │   └── finance/
│   │   │       ├── fct_sales.sql
│   │   │       ├── fct_inventory.sql
│   │   │       └── schema.yml
│   │   │
│   │   └── utilities/                # Utilitários DBT
│   │       ├── __init__.py
│   │       ├── date_spine.sql
│   │       └── utility_macros.sql
│   │
│   ├── seeds/                        # Dados estáticos
│   │   ├── countries.csv
│   │   ├── categories.csv
│   │   └── users.csv
│   │
│   ├── tests/                        # Testes de dados
│   │   ├── generic/
│   │   │   ├── test_not_null.sql
│   │   │   └── test_unique.sql
│   │   └── singular/
│   │       ├── assert_total_sales_positive.sql
│   │       └── assert_customer_orders.sql
│   │
│   ├── macros/                       # Macros reutilizáveis
│   │   ├── __init__.py
│   │   ├── custom_macros.sql
│   │   ├── incremental_logic.sql
│   │   └── audit_columns.sql
│   │
│   ├── analysis/                     # Análises ad-hoc
│   │   ├── customer_lifetime_value.sql
│   │   └── inventory_turnover.sql
│   │
│   ├── snapshots/                    # Snapshots para SCD
│   │   ├── __init__.py
│   │   ├── customer_snapshot.sql
│   │   └── product_snapshot.sql
│   │
│   ├── target/                       # Pasta compilada (gerada)
│   │   └── (conteúdo gerado pelo dbt)
│   │
│   ├── logs/                         # Logs DBT
│   │   └── dbt.log
│   │
│   ├── dbt_project.yml               # Configuração do projeto DBT
│   ├── profiles.yml                  # Perfis de conexão
│   └── packages.yml                  # Dependências externas
│
├── data/                             # Dados locais (desenvolvimento)
│   ├── raw/                          # Dados brutos
│   │   ├── source1/
│   │   └── source2/
│   ├── processed/                    # Dados processados
│   └── temp/                         # Dados temporários
│
├── logs/                             # Logs da aplicação
│   ├── app.log
│   ├── dagster.log
│   └── dbt.log
│
├── tests/                            # Testes unitários/integração
│   ├── __init__.py
│   ├── conftest.py                   # Configuração pytest
│   ├── unit/
│   │   ├── test_controllers.py
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── integration/
│   │   ├── test_dagster_integration.py
│   │   └── test_dbt_integration.py
│   └── fixtures/
│       ├── sample_data.csv
│       └── mock_responses.py
│
├── scripts/                          # Scripts utilitários
│   ├── init_db.py                    # Inicialização do banco
│   ├── seed_data.py                  # Carregar dados de teste
│   ├── backup_pipelines.py           # Backup de configurações
│   └── monitoring.py                 # Monitoramento manual
│
├── config/                           # Configurações por ambiente
│   ├── development.py
│   ├── staging.py
│   ├── production.py
│   └── docker/
│       ├── Dockerfile
│       ├── docker-compose.yml
│       └── .env.example
│
├── docs/                             # Documentação
│   ├── architecture.md
│   ├── api_reference.md
│   ├── deployment_guide.md
│   └── dbt_linage.html
│
├── migrations/                       # Migrações de banco (Alembic)
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── .env                              # Variáveis de ambiente
├── .gitignore
├── requirements.txt                  # Dependências Python
├── requirements-dev.txt              # Dependências desenvolvimento
├── Makefile                          # Comandos automatizados
├── docker-compose.yml                # Orquestração containers
├── Dockerfile                        # Imagem da aplicação
├── README.md                         # Documentação principal
└── run.py                            # Entry point da aplicação