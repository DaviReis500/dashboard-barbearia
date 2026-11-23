# Dashboard Gerencial — Sistema Barbearia Navalha

Projeto individual desenvolvido para a disciplina de Banco de Dados no **Centro Universitário Santo Agostinho (UNIFSA)**, evoluindo o sistema **Barbearia Navalha** com um dashboard interativo de indicadores (KPIs), gráficos e consultas SQL aplicadas a dados reais no PostgreSQL.

## Identificação do Aluno
- **Nome:** Davi Negreiros de Macêdo Reis
- **Instituição:** Centro Universitário Santo Agostinho (UNIFSA)


## Tecnologias Utilizadas
- **Linguagem:** Python 3
- **Dashboard:** Streamlit e Pandas
- **Banco de Dados:** PostgreSQL (`barbearia_db`) via `psycopg2`
- **Controle de Versão:** Git e GitHub

## Estrutura do Repositório
- `barbearia1.py`: Sistema principal da barbearia (login, inicialização do banco e operações).
- `dashboard.py`: Aplicação do dashboard com KPIs, gráficos e consultas SQL dinâmicas.
- `banco_barbearia.sql`: Script SQL para criação das tabelas, inserção de dados e consultas analíticas.
- `README.md`: Documentação e instruções de uso.

## Instalação e Execução

1. **Configure o PostgreSQL:**
   Certifique-se de que o serviço do PostgreSQL está em execução na porta `5432` com usuário `postgres`, senha `root` e banco `barbearia_db` (ou execute o script `banco_barbearia.sql` / `barbearia1.py` para criar as tabelas).

2. **Instale as dependências Python:**
   ```bash
   pip install streamlit pandas psycopg2-binary
