"""
Dashboard Interativo — API Error Logs
Card 4: Interface de filtragem por período e equipe

Execução:
    poetry run streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ─── Configuração da página ───────────────────────────────────────────────────

st.set_page_config(
    page_title="API Error Dashboard",
    page_icon="🔴",
    layout="wide",
)

BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "api_error_logs_cleaned.csv"


# ─── Carregamento otimizado ───────────────────────────────────────────────────

@st.cache_data
def carregar_dados() -> pd.DataFrame:
    """
    Carrega o dataset pre-processado do disco com cacheamento do Streamlit.
    Realiza o tratamento de nulos em 'error_type' e cria colunas auxiliares
    como 'falha' e 'data' para uso nos graficos e testes.
    
    Returns:
        pd.DataFrame: DataFrame contendo os registros pre-processados.
    """
    df = pd.read_csv(INPUT_FILE, parse_dates=["timestamp"])
    df["error_type"] = df["error_type"].fillna("Undefined")
    df["falha"] = (df["status_code"] >= 400).astype(int)
    df["data"] = df["timestamp"].dt.date
    return df


df_raw = carregar_dados()

# ─── Sidebar — Filtros ────────────────────────────────────────────────────────

st.sidebar.title("Filtros")

# Período
data_min = df_raw["data"].min()
data_max = df_raw["data"].max()
periodo = st.sidebar.date_input(
    "Período",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
)

# Garante que o usuário sempre selecione um intervalo completo
if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
    data_inicio, data_fim = periodo
else:
    data_inicio, data_fim = data_min, data_max

# Equipe
todas_equipes = sorted(df_raw["service_owner"].unique())
equipes = st.sidebar.multiselect(
    "Equipe",
    options=todas_equipes,
    default=todas_equipes,
)

# Ambiente
todos_ambientes = sorted(df_raw["environment"].unique())
ambientes = st.sidebar.multiselect(
    "Ambiente",
    options=todos_ambientes,
    default=todos_ambientes,
)

# API
todas_apis = sorted(df_raw["api_name"].unique())
apis = st.sidebar.multiselect(
    "API",
    options=todas_apis,
    default=todas_apis,
)

# ─── Aplicação dos filtros ────────────────────────────────────────────────────

df = df_raw[
    (df_raw["data"] >= data_inicio)
    & (df_raw["data"] <= data_fim)
    & (df_raw["service_owner"].isin(equipes))
    & (df_raw["environment"].isin(ambientes))
    & (df_raw["api_name"].isin(apis))
].copy()

# ─── Título ───────────────────────────────────────────────────────────────────

st.title("API Error Logs — Dashboard Interativo")
st.caption(
    f"Exibindo **{len(df):,}** registros de {data_inicio} a {data_fim} "
    f"| Equipes: {', '.join(equipes) if equipes else '—'}"
)

if df.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# ─── KPIs ─────────────────────────────────────────────────────────────────────

taxa_falha = df["falha"].mean() * 100
latencia_media = df["latency_ms"].mean()
taxa_retry = (df["retry_count"] > 0).mean() * 100
top_erro = df["error_type"].value_counts().idxmax()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de registros", f"{len(df):,}")
col2.metric("Taxa de falha", f"{taxa_falha:.1f}%")
col3.metric("Latência média (ms)", f"{latencia_media:,.0f}")
col4.metric("Top tipo de erro", top_erro)

st.divider()

# ─── Gráfico 1: Série temporal de falhas por dia ──────────────────────────────

serie_dia = (
    df.groupby(["data", "service_owner"])["falha"]
    .sum()
    .reset_index()
    .rename(columns={"falha": "falhas", "service_owner": "Equipe"})
)

fig_tempo = px.line(
    serie_dia,
    x="data",
    y="falhas",
    color="Equipe",
    markers=True,
    title="Volume diário de falhas por equipe",
    labels={"data": "Data", "falhas": "Nº de Falhas"},
)
fig_tempo.update_layout(hovermode="x unified", height=350)

st.plotly_chart(fig_tempo, use_container_width=True)

# ─── Linha 2: Distribuição de tipos de erro + Latência por equipe ─────────────

col_bar, col_box = st.columns(2)

with col_bar:
    contagem_erro = df["error_type"].value_counts()
    n_top_erros = min(len(contagem_erro), 10)  # Máximo 10, ou menos se houver poucos
    contagem_erro = (
        contagem_erro
        .head(n_top_erros)
        .reset_index()
        .rename(columns={"error_type": "Tipo de Erro", "count": "Quantidade"})
    )
    fig_erro = px.bar(
        contagem_erro,
        x="Quantidade",
        y="Tipo de Erro",
        orientation="h",
        title=f"Top {n_top_erros} Tipos de Erro",
        color="Quantidade",
        color_continuous_scale="Blues",
    )
    fig_erro.update_layout(height=380, showlegend=False, coloraxis_showscale=False)
    fig_erro.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_erro, use_container_width=True)

with col_box:
    fig_box = px.box(
        df,
        x="service_owner",
        y="latency_ms",
        color="service_owner",
        title="Distribuição de Latência por Equipe",
        labels={"service_owner": "Equipe", "latency_ms": "Latência (ms)"},
        points=False,
    )
    fig_box.update_layout(height=380, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# ─── Linha 3: Taxa de falha por API + Heatmap erro × equipe ──────────────────

col_api, col_heat = st.columns(2)

with col_api:
    taxa_api = (
        df.groupby("api_name")["falha"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"api_name": "API", "sum": "falhas", "count": "total"})
    )
    taxa_api["taxa"] = taxa_api["falhas"] / taxa_api["total"] * 100

    fig_api = px.bar(
        taxa_api.sort_values("taxa", ascending=False),
        x="API",
        y="taxa",
        title="Taxa de Falha por API (%)",
        labels={"taxa": "Taxa de Falha (%)", "API": "API"},
        color="taxa",
        color_continuous_scale="Reds",
        text_auto=".1f",
    )
    fig_api.update_layout(height=360, coloraxis_showscale=False)
    st.plotly_chart(fig_api, use_container_width=True)

with col_heat:
    pivot = (
        df.groupby(["service_owner", "error_type"])
        .size()
        .reset_index(name="count")
        .pivot(index="service_owner", columns="error_type", values="count")
        .fillna(0)
    )

    # Limita às top 8 colunas para legibilidade
    top_cols = pivot.sum().nlargest(8).index
    pivot = pivot[top_cols]

    fig_heat = px.imshow(
        pivot,
        title="Heatmap: Erros por Equipe",
        labels={"x": "Tipo de Erro", "y": "Equipe", "color": "Ocorrências"},
        color_continuous_scale="YlOrRd",
        aspect="auto",
        text_auto=True,
    )
    fig_heat.update_layout(height=360)
    st.plotly_chart(fig_heat, use_container_width=True)

# ─── Linha 4: Status HTTP dividido por ambiente ───────────────────────────────

status_env = (
    df.groupby(["environment", "status_code"])
    .size()
    .reset_index(name="count")
    .rename(columns={"environment": "Ambiente", "status_code": "Status HTTP"})
)
status_env["Status HTTP"] = status_env["Status HTTP"].astype(str)

fig_status = px.bar(
    status_env,
    x="Ambiente",
    y="count",
    color="Status HTTP",
    barmode="stack",
    title="Distribuição de Status HTTP por Ambiente",
    labels={"count": "Quantidade", "Ambiente": "Ambiente"},
)
fig_status.update_layout(height=350)
st.plotly_chart(fig_status, use_container_width=True)

# ─── Rodapé ───────────────────────────────────────────────────────────────────

st.caption("Desafio Python G2 — Card 4: Dashboard Interativo")
