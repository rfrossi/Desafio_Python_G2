"""
Analise Descritiva - Card 3
Dataset AFID: API Error Logs

Criterios de Aceite:
- Calculo de media, mediana e desvio padrao das metricas de resposta
- Identificacao de outliers usando a tecnica IQR

Checklist Tecnico:
[x] Histogramas para visualizar a distribuicao dos erros
[x] Matriz de correlacao entre carga da API e taxa de falha
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path


# ─── Configuracao ────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "api_error_logs_cleaned.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

METRICAS_RESPOSTA = ["latency_ms", "request_size_bytes", "response_size_bytes"]

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 120, "figure.facecolor": "white"})


# ─── Carregamento ─────────────────────────────────────────────────────────────

def carregar_dados() -> pd.DataFrame:
    """
    Carrega o dataset AFID pré-processado (sem valores nulos).

    Returns:
        pd.DataFrame: DataFrame carregado.
    """
    print(f"\n[LOADING] Carregando dataset: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE, parse_dates=["timestamp"])
    print(f"[OK] {df.shape[0]:,} linhas, {df.shape[1]} colunas (pré-processado)")

    return df


# ─── 1. Estatisticas Descritivas ──────────────────────────────────────────────

def estatisticas_descritivas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula as estatisticas descritivas (media, mediana, desvio padrao, min, max, n)
    das métricas de resposta do dataset.
    
    Args:
        df: DataFrame contendo os logs da API.
        
    Returns:
        pd.DataFrame: DataFrame contendo as estatisticas processadas.
    """
    print("\n" + "=" * 70)
    print("1. ESTATISTICAS DESCRITIVAS DAS METRICAS DE RESPOSTA")
    print("=" * 70)

    rows = []
    for col in METRICAS_RESPOSTA:
        serie = df[col].dropna()
        rows.append({
            "Metrica":       col,
            "Media":         round(serie.mean(), 2),
            "Mediana":       round(serie.median(), 2),
            "Desvio Padrao": round(serie.std(), 2),
            "Min":           round(serie.min(), 2),
            "Max":           round(serie.max(), 2),
            "N":             len(serie),
        })

    stats = pd.DataFrame(rows).set_index("Metrica")
    print(stats.to_string())
    return stats


# ─── 2. Deteccao de Outliers (IQR) ───────────────────────────────────────────

def detectar_outliers_iqr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta outliers numericos usando o metodo IQR (Intervalo Interquartil)
    para cada metrica de resposta.
    
    Args:
        df: DataFrame original de logs da API.
        
    Returns:
        pd.DataFrame: DataFrame quantificando os outliers encontrados em cada metrica.
    """
    print("\n" + "=" * 70)
    print("2. DETECCAO DE OUTLIERS - METODO IQR")
    print("=" * 70)

    rows = []
    for col in METRICAS_RESPOSTA:
        serie = df[col].dropna()
        Q1 = serie.quantile(0.25)
        Q3 = serie.quantile(0.75)
        IQR = Q3 - Q1
        limite_inf = Q1 - 1.5 * IQR
        limite_sup = Q3 + 1.5 * IQR
        outliers = serie[(serie < limite_inf) | (serie > limite_sup)]
        pct = len(outliers) / len(serie) * 100

        rows.append({
            "Metrica":      col,
            "Q1":           round(Q1, 2),
            "Q3":           round(Q3, 2),
            "IQR":          round(IQR, 2),
            "Limite Inf":   round(limite_inf, 2),
            "Limite Sup":   round(limite_sup, 2),
            "Outliers":     len(outliers),
            "% Outliers":   round(pct, 2),
        })

        print(f"\n  [{col}]")
        print(f"    Q1={Q1:.2f}  Q3={Q3:.2f}  IQR={IQR:.2f}")
        print(f"    Limites: [{limite_inf:.2f}, {limite_sup:.2f}]")
        print(f"    Outliers: {len(outliers):,} ({pct:.2f}%)")

    return pd.DataFrame(rows).set_index("Metrica")


# ─── 3. Histogramas de Distribuicao dos Erros ────────────────────────────────

def histogramas_erros(df: pd.DataFrame) -> None:
    """
    Gera e salva um painel contendo histogramas da distribuicao dos tipos de erros, 
    latencia e tamanho da requisicao.
    
    Args:
        df: DataFrame de logs da API.
    """
    print("\n" + "=" * 70)
    print("3. HISTOGRAMAS - DISTRIBUICAO DOS ERROS")
    print("=" * 70)

    fig = plt.figure(figsize=(18, 14))
    fig.suptitle("Distribuição dos Tipos de Erro e Métricas de Resposta",
                 fontsize=15, fontweight="bold", y=0.98)

    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    # --- 3a. Top 15 tipos de erro (barras horizontais) ---
    ax0 = fig.add_subplot(gs[0, :])
    contagem_erro = (
        df["error_type"]
        .value_counts()
        .head(15)
        .sort_values()
    )
    cores = sns.color_palette("Blues_d", len(contagem_erro))
    bars = ax0.barh(contagem_erro.index, contagem_erro.values, color=cores)
    ax0.set_title("Top 15 Tipos de Erro (error_type)", fontsize=12, fontweight="bold")
    ax0.set_xlabel("Quantidade de Ocorrências")
    ax0.set_ylabel("Tipo de Erro")
    for bar, val in zip(bars, contagem_erro.values):
        ax0.text(val + 100, bar.get_y() + bar.get_height() / 2,
                 f"{val:,}", va="center", fontsize=8)
    ax0.set_xlim(0, contagem_erro.values.max() * 1.12)

    # --- 3b–3d. Histogramas das metricas numericas ---
    posicoes = [gs[1, 0], gs[1, 1]]
    metricas_hist = METRICAS_RESPOSTA[:2]          # latency_ms e request_size_bytes
    titulos = ["Latência (ms)", "Tamanho da Requisição (bytes)"]

    for ax_pos, col, titulo in zip(posicoes, metricas_hist, titulos):
        ax = fig.add_subplot(ax_pos)
        serie = df[col].dropna()

        # Limita a 99 percentil para melhor visualizacao
        lim_sup = serie.quantile(0.99)
        serie_clip = serie[serie <= lim_sup]

        ax.hist(serie_clip, bins=60, color=sns.color_palette("Blues_d")[3],
                edgecolor="white", linewidth=0.4)

        # Linhas de media e mediana
        media = serie.mean()
        mediana = serie.median()
        ax.axvline(media,   color="#e74c3c", linestyle="--", linewidth=1.4,
                   label=f"Média: {media:,.0f}")
        ax.axvline(mediana, color="#2ecc71", linestyle="-",  linewidth=1.4,
                   label=f"Mediana: {mediana:,.0f}")

        ax.set_title(titulo, fontsize=11, fontweight="bold")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequência")
        ax.legend(fontsize=8)
        ax.tick_params(axis="x", labelsize=8)

    caminho = OUTPUT_DIR / "histogramas_erros.png"
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"[OK] Salvo em: {caminho}")


# ─── 4. Analise Temporal das Falhas ──────────────────────────────────────────

def analise_temporal(df: pd.DataFrame) -> None:
    """
    Gera e salva o grafico contendo o volume de falhas agrupado por hora.
    
    Args:
        df: DataFrame com os logs gerais da API.
    """
    print("\n" + "=" * 70)
    print("4. ANALISE TEMPORAL DAS FALHAS")
    print("=" * 70)

    serie_hora = df.set_index("timestamp").resample("h").size()
    print(f"[INFO] Periodo: {serie_hora.index.min()} ate {serie_hora.index.max()}")
    print(f"[INFO] Total de horas com dados: {len(serie_hora):,}")
    print(f"[INFO] Pico maximo: {serie_hora.max():,} falhas/hora")

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(serie_hora.index, serie_hora.values,
            color="#2980b9", linewidth=0.8, alpha=0.85)
    ax.fill_between(serie_hora.index, serie_hora.values,
                    alpha=0.2, color="#2980b9")
    ax.set_title("Volume de Falhas por Hora", fontsize=13, fontweight="bold")
    ax.set_xlabel("Tempo")
    ax.set_ylabel("Nº de Falhas")
    ax.tick_params(axis="x", rotation=30, labelsize=8)

    caminho = OUTPUT_DIR / "serie_temporal_falhas.png"
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"[OK] Salvo em: {caminho}")


# ─── 5. Matriz de Correlacao ─────────────────────────────────────────────────

def matriz_correlacao(df: pd.DataFrame) -> None:
    """
    Gera a matriz de correlação contendo diversas metricas como latencia media, 
    volume de requisicoes, entre outras, extraidas a cada hora.
    
    Args:
        df: DataFrame com dados e features de requests a API.
    """
    print("\n" + "=" * 70)
    print("5. MATRIZ DE CORRELACAO - CARGA DA API vs TAXA DE FALHA")
    print("=" * 70)

    # Feature de taxa de falha: 1 para status_code >= 400
    df = df.copy()
    df["falha"] = (df["status_code"] >= 400).astype(int)

    # Agrega por hora para capturar a relacao entre carga e falhas
    df_hora = df.set_index("timestamp").resample("h").agg(
        volume_requisicoes=("falha", "count"),
        taxa_falha=("falha", "mean"),
        latencia_media=("latency_ms", "mean"),
        req_size_medio=("request_size_bytes", "mean"),
        resp_size_medio=("response_size_bytes", "mean"),
        retry_medio=("retry_count", "mean"),
    ).dropna()

    print("[INFO] Variaveis usadas na correlacao:")
    print("  volume_requisicoes, taxa_falha, latencia_media,")
    print("  req_size_medio, resp_size_medio, retry_medio")

    corr = df_hora.corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    mascara = np.triu(np.ones_like(corr, dtype=bool), k=1)

    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
        linecolor="white",
        square=True,
        ax=ax,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title(
        "Matriz de Correlação\nCarga da API × Taxa de Falha (agregação horária)",
        fontsize=12,
        fontweight="bold",
        pad=14,
    )
    ax.tick_params(axis="x", rotation=30, labelsize=9)
    ax.tick_params(axis="y", rotation=0,  labelsize=9)

    caminho = OUTPUT_DIR / "matriz_correlacao.png"
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"[OK] Salvo em: {caminho}")

    # Exibe correlacoes mais relevantes com 'taxa_falha'
    print("\n[INFO] Correlacoes com 'taxa_falha':")
    correlacoes_falha = corr["taxa_falha"].drop("taxa_falha").sort_values(key=abs, ascending=False)
    for var, val in correlacoes_falha.items():
        print(f"  {var:<25} r = {val:+.4f}")


# ─── 6. Checklist Tecnico ────────────────────────────────────────────────────

def checklist_tecnico(stats: pd.DataFrame, outliers: pd.DataFrame) -> None:
    """
    Testes manuais para relatorio indicando cada check basico e sua completude.
    
    Args:
        stats: DataFrame com status_code gerais para afericao na avaliacao de conclusoes
        outliers: DataFrame listando outliers pre mensurados por deteccao_iqr.
    """
    print("\n" + "=" * 70)
    print("CHECKLIST TECNICO - CARD 3")
    print("=" * 70)

    checks = {
        "Media calculada para metricas de resposta":
            all(col in stats.index for col in METRICAS_RESPOSTA),
        "Mediana calculada para metricas de resposta":
            "Mediana" in stats.columns,
        "Desvio padrao calculado para metricas de resposta":
            "Desvio Padrao" in stats.columns,
        "Outliers identificados com IQR":
            "Outliers" in outliers.columns,
        "Histogramas de distribuicao dos erros gerados":
            (OUTPUT_DIR / "histogramas_erros.png").exists(),
        "Matriz de correlacao entre carga e taxa de falha gerada":
            (OUTPUT_DIR / "matriz_correlacao.png").exists(),
        "Serie temporal das falhas gerada":
            (OUTPUT_DIR / "serie_temporal_falhas.png").exists(),
    }

    for descricao, status in checks.items():
        marcador = "[OK]" if status else "[FAIL]"
        print(f"  {marcador} {descricao}")

    total = sum(checks.values())
    print(f"\n  Resultado: {total}/{len(checks)} itens concluidos")
    print("=" * 70)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    """
    Funcao principal de entrada. Carrega os dados, chama todos os metodos processuais
    e relatorios necessarios e imprime a mensagem do checklist gerado via arquivo log.
    """
    print("\n" + "=" * 70)
    print("ANALISE DESCRITIVA - CARD 3")
    print("Dataset: API Error Logs (220k registros)")
    print("=" * 70)

    df = carregar_dados()
    stats    = estatisticas_descritivas(df)
    outliers = detectar_outliers_iqr(df)
    histogramas_erros(df)
    analise_temporal(df)
    matriz_correlacao(df)
    checklist_tecnico(stats, outliers)

    print("\n[SUCCESS] Analise descritiva concluida!")
    print(f"[INFO] Graficos salvos em: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
