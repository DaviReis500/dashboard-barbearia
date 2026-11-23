import pandas as pd
import psycopg2
import streamlit as st

st.set_page_config(
    page_title="Dashboard - Barbearia Navalha",
    page_icon="💈",
    layout="wide"
)

HOST = "localhost"
PORTA = "5432"
BANCO = "barbearia_db"
USUARIO = "postgres"
SENHA = "root"


@st.cache_data(ttl=10)
def consultar_df(sql, params=()):
    conexao = psycopg2.connect(
        host=HOST,
        port=PORTA,
        dbname=BANCO,
        user=USUARIO,
        password=SENHA
    )
    try:
        return pd.read_sql_query(sql, conexao, params=params)
    finally:
        conexao.close()


st.title("💈 Dashboard Gerencial — Barbearia Navalha")
st.caption("Indicadores e análises alimentados em tempo real pelo PostgreSQL (`barbearia_db`)")

try:
    # 1. KPIs gerais + MIN e MAX de preço dos serviços
    df_kpis = consultar_df("""
        SELECT
            COUNT(a.id) AS total_agendamentos,
            COALESCE(SUM(s.preco), 0) AS faturamento_total,
            COALESCE(MIN(s.preco), 0) AS menor_preco_servico,
            COALESCE(MAX(s.preco), 0) AS maior_preco_servico
        FROM agendamentos a
        LEFT JOIN servicos s ON a.servico_id = s.id;
    """)

    total_agend = int(df_kpis.loc[0, "total_agendamentos"])
    faturamento = float(df_kpis.loc[0, "faturamento_total"])
    menor_preco = float(df_kpis.loc[0, "menor_preco_servico"])
    maior_preco = float(df_kpis.loc[0, "maior_preco_servico"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Faturamento Total", f"R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("Total de Agendamentos", total_agend)
    col3.metric("Menor Preço Agendado (MIN)", f"R$ {menor_preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col4.metric("Maior Preço Agendado (MAX)", f"R$ {maior_preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.divider()

    # 2. Gráficos (Tipo 1: Barras com JOIN + GROUP BY | Tipo 2: Linha por data)
    graf_esq, graf_dir = st.columns(2)

    sql_servico_join_groupby = """
        SELECT
            s.nome AS servico,
            COUNT(a.id) AS qtd_agendamentos,
            COALESCE(SUM(s.preco), 0) AS faturamento
        FROM servicos s
        LEFT JOIN agendamentos a ON s.id = a.servico_id
        GROUP BY s.id, s.nome
        ORDER BY faturamento DESC, qtd_agendamentos DESC;
    """
    df_servicos = consultar_df(sql_servico_join_groupby)

    with graf_esq:
        st.subheader("📊 Faturamento por Serviço (JOIN + GROUP BY)")
        if not df_servicos.empty:
            st.bar_chart(df_servicos.set_index("servico")["faturamento"])
        else:
            st.info("Sem dados para exibir no gráfico de barras.")

    sql_por_data = """
        SELECT
            data_agendamento,
            COUNT(id) AS total_agendamentos
        FROM agendamentos
        GROUP BY data_agendamento
        ORDER BY data_agendamento ASC;
    """
    df_datas = consultar_df(sql_por_data)

    with graf_dir:
        st.subheader("📈 Evolução de Agendamentos por Data")
        if not df_datas.empty:
            df_datas["data_agendamento"] = pd.to_datetime(df_datas["data_agendamento"])
            st.line_chart(df_datas.set_index("data_agendamento")["total_agendamentos"])
        else:
            st.info("Cadastre agendamentos no sistema para visualizar a evolução por data.")

    st.divider()

    # 3. Consultas SQL obrigatórias detalhadas (HAVING e SUBQUERY)
    st.subheader("🔎 Consultas SQL Avançadas (HAVING e SUBQUERY)")

    aba1, aba2, aba3 = st.tabs([
        "JOIN + GROUP BY (Serviços)",
        "GROUP BY + HAVING (Serviços em Destaque)",
        "SUBQUERY (Agendamentos Acima da Média)"
    ])

    with aba1:
        st.code(sql_servico_join_groupby.strip(), language="sql")
        st.dataframe(df_servicos, use_container_width=True)

    with aba2:
        min_qtd = st.slider("Quantidade mínima de agendamentos (HAVING COUNT >= X):", min_value=1, max_value=10, value=1)
        sql_having = """
            SELECT
                s.nome AS servico,
                COUNT(a.id) AS qtd_agendamentos,
                SUM(s.preco) AS faturamento
            FROM servicos s
            JOIN agendamentos a ON s.id = a.servico_id
            GROUP BY s.id, s.nome
            HAVING COUNT(a.id) >= %s
            ORDER BY qtd_agendamentos DESC;
        """
        st.code(sql_having.strip().replace("%s", str(min_qtd)), language="sql")
        df_having = consultar_df(sql_having, (min_qtd,))
        st.dataframe(df_having, use_container_width=True)

    with aba3:
        sql_subquery = """
            SELECT
                a.id,
                a.cliente,
                s.nome AS servico,
                s.preco,
                a.data_agendamento,
                a.horario
            FROM agendamentos a
            JOIN servicos s ON a.servico_id = s.id
            WHERE s.preco >= (
                SELECT AVG(s2.preco)
                FROM agendamentos a2
                JOIN servicos s2 ON a2.servico_id = s2.id
            )
            ORDER BY s.preco DESC, a.data_agendamento DESC;
        """
        st.code(sql_subquery.strip(), language="sql")
        df_subquery = consultar_df(sql_subquery)
        st.dataframe(df_subquery, use_container_width=True)

except psycopg2.Error as erro:
    st.error(f"Erro ao conectar ou consultar o PostgreSQL: {erro}")
    st.info("Verifique se o PostgreSQL está rodando e se o banco `barbearia_db` já foi inicializado pelo `barbearia1.py`.")