"""
Análise Preditiva — PCA + ARIMA + Prophet
Dataset AFID: API Error Logs

Descrição:
    Aplicar PCA para redução de dimensionalidade e usar ARIMA e Prophet
    para prever tendências futuras de falhas nas APIs.

Critérios de Aceite:
    - Modelo treinado e visualização de previsões futuras gerada.
    - Comparação entre os modelos em termos de precisão.

Checklist Técnico:
    [x] Normalizar os dados com StandardScaler.
    [x] Aplicar PCA para simplificar as features.
    [x] Ajustar modelo Prophet para tendências sazonais.
"""

import sys
import warnings

# Garante UTF-8 no stdout/stderr (necessário no Windows com cp1252)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use("Agg")  # backend não-interativo (sem Tkinter/display)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("[WARN] Prophet não instalado. Execute: pip install prophet")

warnings.filterwarnings("ignore")

# ─── Configuração ─────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "api_error_logs_with_root_causes_220k_rows.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

NUMERIC_FEATURES = [
    "latency_ms", "request_size_bytes", "response_size_bytes",
    "retry_count", "status_code",
]
N_PCA          = 3     # número de componentes principais
FORECAST_HOURS = 48    # horizonte de previsão (horas)
TRAIN_RATIO    = 0.80  # proporção treino/teste

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 120, "figure.facecolor": "white"})


# ─── 1. Carregamento ──────────────────────────────────────────────────────────

def carregar_dados() -> pd.DataFrame:
    """Carrega o dataset e adiciona coluna de falha (status_code >= 400)."""
    print(f"\n[LOADING] {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE, parse_dates=["timestamp"])
    print(f"[OK] {df.shape[0]:,} linhas × {df.shape[1]} colunas")

    if df["error_type"].isnull().any():
        n = df["error_type"].isnull().sum()
        df["error_type"] = df["error_type"].fillna("Undefined")
        print(f"[INFO] {n:,} nulos em 'error_type' preenchidos com 'Undefined'")

    df["falha"] = (df["status_code"] >= 400).astype(int)
    return df


# ─── 2. Normalização com StandardScaler ───────────────────────────────────────

def normalizar_dados(df: pd.DataFrame):
    """
    Normaliza as features numéricas com StandardScaler.

    Returns:
        scaler: objeto StandardScaler ajustado
        X_scaled: array normalizado
        X_base: DataFrame original das features (sem NaN)
    """
    print("\n" + "=" * 70)
    print("2. NORMALIZAÇÃO — StandardScaler")
    print("=" * 70)

    X_base = df[NUMERIC_FEATURES].dropna()

    # Limita a 50k amostras para eficiência computacional
    if len(X_base) > 50_000:
        X_base = X_base.sample(50_000, random_state=42)

    scaler  = StandardScaler()
    X_scaled = scaler.fit_transform(X_base)

    print(f"[INFO] Features: {NUMERIC_FEATURES}")
    print(f"[INFO] Amostras: {len(X_base):,}")
    print("\n  Estatísticas após normalização (média ≈ 0, std ≈ 1):")
    for i, feat in enumerate(NUMERIC_FEATURES):
        print(
            f"  {feat:<28} média={X_scaled[:, i].mean():+.4f}  "
            f"std={X_scaled[:, i].std():.4f}"
        )

    return scaler, X_scaled, X_base


# ─── 3. PCA ───────────────────────────────────────────────────────────────────

def aplicar_pca(X_scaled: np.ndarray):
    """
    Aplica PCA ao dataset normalizado.

    Returns:
        pca: objeto PCA ajustado
        X_pca: array com os componentes principais
    """
    print("\n" + "=" * 70)
    print("3. REDUÇÃO DE DIMENSIONALIDADE — PCA")
    print("=" * 70)

    pca   = PCA(n_components=N_PCA, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    var = pca.explained_variance_ratio_
    print(f"[OK] PCA com {N_PCA} componentes principais:")
    for i, (v, c) in enumerate(zip(var, var.cumsum())):
        bar = "█" * int(v * 40)
        print(f"  PC{i + 1}:  {v * 100:5.1f}%   {bar}   (acumulada: {c * 100:.1f}%)")

    return pca, X_pca


def visualizar_pca(pca, X_scaled: np.ndarray, X_pca: np.ndarray) -> None:
    """Gera 3 visualizações do PCA: scree plot, loadings e dispersão."""
    var        = pca.explained_variance_ratio_
    componentes = [f"PC{i + 1}" for i in range(N_PCA)]
    loadings   = pd.DataFrame(
        pca.components_.T,
        columns=componentes,
        index=NUMERIC_FEATURES,
    )

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(
        "Análise de Componentes Principais (PCA)\nNormalização com StandardScaler",
        fontsize=14, fontweight="bold",
    )

    # --- Scree Plot ---
    ax = axes[0]
    ax.bar(componentes, var * 100, color=sns.color_palette("Blues_d", N_PCA))
    ax.plot(componentes, np.cumsum(var) * 100, "ro-", lw=2, ms=6, label="Acumulada")
    for i, v in enumerate(var * 100):
        ax.text(i, v + 1.5, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_ylim(0, 115)
    ax.set_title("Variância Explicada (Scree Plot)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Variância Explicada (%)")
    ax.legend(fontsize=9)

    # --- Heatmap de Loadings ---
    ax = axes[1]
    sns.heatmap(
        loadings, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
        linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Matriz de Loadings\n(Contribuição das Features)", fontsize=11, fontweight="bold")
    ax.tick_params(axis="y", rotation=0, labelsize=8)
    ax.tick_params(axis="x", labelsize=9)

    # --- Dispersão PC1 × PC2 ---
    ax = axes[2]
    sc = ax.scatter(
        X_pca[:, 0], X_pca[:, 1],
        c=X_pca[:, 2] if N_PCA >= 3 else "steelblue",
        alpha=0.15, s=3, cmap="RdYlBu", rasterized=True,
    )
    if N_PCA >= 3:
        fig.colorbar(sc, ax=ax, label="PC3", shrink=0.8)
    ax.set_xlabel(f"PC1 ({var[0] * 100:.1f}% var.)")
    ax.set_ylabel(f"PC2 ({var[1] * 100:.1f}% var.)")
    ax.set_title("Dispersão: PC1 × PC2", fontsize=11, fontweight="bold")

    plt.tight_layout()
    caminho = OUTPUT_DIR / "pca_analise.png"
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"[OK] Visualização PCA salva em: {caminho}")


# ─── 4. Série Temporal ────────────────────────────────────────────────────────

def preparar_serie_temporal(df: pd.DataFrame) -> pd.Series:
    """
    Agrega o número de falhas por hora para criar a série temporal de treino.
    Retorna uma pd.Series com frequência horária.
    """
    print("\n" + "=" * 70)
    print("4. SÉRIE TEMPORAL DE FALHAS (agregação horária)")
    print("=" * 70)

    serie = (
        df.set_index("timestamp")["falha"]
        .resample("h")
        .sum()
        .asfreq("h", fill_value=0)
    )

    # Remove horas completamente sem dados no início/fim
    serie = serie.loc[serie.first_valid_index():serie.last_valid_index()]

    print(f"[INFO] Período: {serie.index.min()}  →  {serie.index.max()}")
    print(f"[INFO] Total de horas: {len(serie):,}")
    print(f"[INFO] Pico máximo: {serie.max():,} falhas/hora")
    print(f"[INFO] Média:       {serie.mean():.1f} falhas/hora")

    return serie


# ─── 5. ARIMA ─────────────────────────────────────────────────────────────────

def treinar_arima(train: pd.Series, test: pd.Series, n_forecast: int):
    """
    Ajusta ARIMA(1,1,1) na série de treino e gera previsões para
    o período de teste + horizonte futuro.

    Returns:
        resultado: objeto ARIMAResults
        fc_mean: pd.Series com previsão central
        fc_ci: pd.DataFrame com intervalo de confiança 95%
    """
    print("\n" + "=" * 70)
    print("5. MODELO ARIMA(1,1,1)")
    print("=" * 70)

    model    = ARIMA(train, order=(1, 1, 1))
    resultado = model.fit()

    n_steps    = len(test) + n_forecast
    fc_obj     = resultado.get_forecast(steps=n_steps)
    fc_mean    = fc_obj.predicted_mean
    fc_ci      = fc_obj.conf_int(alpha=0.05)

    future_idx = pd.date_range(
        start=train.index[-1] + pd.Timedelta(hours=1),
        periods=n_steps,
        freq="h",
    )
    fc_mean.index = future_idx
    fc_ci.index   = future_idx

    print(f"[OK] ARIMA(1,1,1) ajustado")
    print(f"  AIC  = {resultado.aic:.2f}")
    print(f"  BIC  = {resultado.bic:.2f}")
    print(f"  HQIC = {resultado.hqic:.2f}")
    print(f"  Previsão: {n_steps} horas  ({len(test)} teste + {n_forecast} futuro)")

    return resultado, fc_mean, fc_ci


# ─── 6. Prophet ───────────────────────────────────────────────────────────────

def treinar_prophet(train: pd.Series, test: pd.Series, n_forecast: int):
    """
    Ajusta modelo Prophet com sazonalidade diária na série de treino.

    Returns:
        model: objeto Prophet ajustado (ou None se não disponível)
        previsao: DataFrame com ds, yhat, yhat_lower, yhat_upper (ou None)
    """
    print("\n" + "=" * 70)
    print("6. MODELO PROPHET")
    print("=" * 70)

    if not PROPHET_AVAILABLE:
        print("[WARN] Prophet não disponível. Instale com: pip install prophet")
        return None, None

    df_train = pd.DataFrame({"ds": train.index, "y": train.values})

    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=False,
        yearly_seasonality=False,
        seasonality_mode="additive",
        changepoint_prior_scale=0.05,
        interval_width=0.95,
    )
    model.fit(df_train)

    n_steps  = len(test) + n_forecast
    futuro   = model.make_future_dataframe(periods=n_steps, freq="h", include_history=False)
    previsao = model.predict(futuro)

    cols = ["ds", "yhat", "yhat_lower", "yhat_upper"]
    print("[OK] Prophet ajustado com sazonalidade diária (horária)")
    print(f"  Previsão: {n_steps} horas  ({len(test)} teste + {n_forecast} futuro)")

    return model, previsao[cols].reset_index(drop=True)


# ─── 7. Métricas de Comparação ────────────────────────────────────────────────

def comparar_modelos(
    test: pd.Series,
    arima_fc_mean: pd.Series,
    prophet_previsao,
) -> pd.DataFrame:
    """
    Calcula MAE, RMSE e MAPE para ARIMA e Prophet no período de teste.

    Returns:
        metricas: DataFrame comparativo indexado pelo nome do modelo
    """
    print("\n" + "=" * 70)
    print("7. COMPARAÇÃO DE MODELOS — MÉTRICAS DE PRECISÃO")
    print("=" * 70)

    y_real = test.values
    rows   = []

    # ARIMA
    y_arima = arima_fc_mean.iloc[:len(test)].values
    mae_a   = mean_absolute_error(y_real, y_arima)
    rmse_a  = np.sqrt(mean_squared_error(y_real, y_arima))
    mape_a  = np.mean(np.abs((y_real - y_arima) / (y_real + 1e-9))) * 100
    rows.append({
        "Modelo": "ARIMA(1,1,1)",
        "MAE": round(mae_a, 2),
        "RMSE": round(rmse_a, 2),
        "MAPE (%)": round(mape_a, 2),
    })
    print(f"\n  ARIMA(1,1,1)  →  MAE={mae_a:.2f}  |  RMSE={rmse_a:.2f}  |  MAPE={mape_a:.2f}%")

    if prophet_previsao is not None:
        y_prophet = prophet_previsao["yhat"].iloc[:len(test)].clip(lower=0).values
        mae_p     = mean_absolute_error(y_real, y_prophet)
        rmse_p    = np.sqrt(mean_squared_error(y_real, y_prophet))
        mape_p    = np.mean(np.abs((y_real - y_prophet) / (y_real + 1e-9))) * 100
        rows.append({
            "Modelo": "Prophet",
            "MAE": round(mae_p, 2),
            "RMSE": round(rmse_p, 2),
            "MAPE (%)": round(mape_p, 2),
        })
        print(f"  Prophet       →  MAE={mae_p:.2f}  |  RMSE={rmse_p:.2f}  |  MAPE={mape_p:.2f}%")

    metricas = pd.DataFrame(rows).set_index("Modelo")

    print("\n  Tabela Comparativa:")
    print(metricas.to_string())

    vencedor = metricas["RMSE"].idxmin()
    print(f"\n  Melhor modelo por RMSE: {vencedor}")

    return metricas


# ─── 8. Visualização de Previsões ─────────────────────────────────────────────

def visualizar_previsoes(
    train: pd.Series,
    test: pd.Series,
    arima_fc_mean: pd.Series,
    arima_fc_ci,
    prophet_previsao,
    metricas: pd.DataFrame,
) -> None:
    """Gera gráfico de previsões para ARIMA e Prophet."""
    n_linhas = 2
    fig, axes = plt.subplots(n_linhas, 1, figsize=(16, n_linhas * 5))
    fig.suptitle(
        "Previsão de Tendências de Falhas nas APIs\nARIMA(1,1,1) × Prophet",
        fontsize=14, fontweight="bold",
    )

    n_test     = len(test)
    n_forecast = FORECAST_HOURS

    arima_test_pred   = arima_fc_mean.iloc[:n_test]
    arima_future_pred = arima_fc_mean.iloc[n_test:]
    arima_ci_test     = arima_fc_ci.iloc[:n_test]
    arima_ci_future   = arima_fc_ci.iloc[n_test:]

    # ── Painel ARIMA ──
    ax = axes[0]
    # Exibe apenas as últimas 72h de treino para melhor leitura
    tail = train.iloc[-72:]
    ax.plot(tail.index, tail.values, color="#2980b9", lw=1.2, label="Treino (últimas 72h)")
    ax.plot(test.index, test.values, color="#27ae60", lw=1.5, label="Teste (real)")
    ax.plot(
        arima_test_pred.index, arima_test_pred.values,
        color="#e74c3c", lw=1.5, linestyle="--", label="ARIMA — Período de teste",
    )
    ax.plot(
        arima_future_pred.index, arima_future_pred.values,
        color="#c0392b", lw=2, linestyle="-",
        label=f"ARIMA — Previsão ({n_forecast}h)",
    )
    ax.fill_between(
        arima_future_pred.index,
        arima_ci_future.iloc[:, 0], arima_ci_future.iloc[:, 1],
        alpha=0.20, color="#c0392b", label="IC 95% (futuro)",
    )
    ax.fill_between(
        arima_test_pred.index,
        arima_ci_test.iloc[:, 0], arima_ci_test.iloc[:, 1],
        alpha=0.12, color="#e74c3c",
    )
    ax.axvline(test.index[0], color="gray", linestyle=":", lw=1.5, label="Início Teste")
    ax.axvline(
        arima_future_pred.index[0], color="#c0392b",
        linestyle=":", lw=1.5, label="Início Previsão Futura",
    )

    mae  = metricas.loc["ARIMA(1,1,1)", "MAE"]
    rmse = metricas.loc["ARIMA(1,1,1)", "RMSE"]
    mape = metricas.loc["ARIMA(1,1,1)", "MAPE (%)"]
    ax.set_title(
        f"ARIMA(1,1,1)  ·  MAE={mae:.1f}  |  RMSE={rmse:.1f}  |  MAPE={mape:.1f}%",
        fontsize=11, fontweight="bold",
    )
    ax.set_ylabel("Nº de Falhas / Hora")
    ax.legend(fontsize=8, loc="upper left", ncol=2)
    ax.tick_params(axis="x", rotation=20, labelsize=8)

    # ── Painel Prophet ──
    ax = axes[1]
    if PROPHET_AVAILABLE and prophet_previsao is not None:
        prophet_test_fc   = prophet_previsao.iloc[:n_test]
        prophet_future_fc = prophet_previsao.iloc[n_test:]

        p_test_dates   = pd.to_datetime(prophet_test_fc["ds"].values)
        p_future_dates = pd.to_datetime(prophet_future_fc["ds"].values)

        ax.plot(tail.index, tail.values, color="#2980b9", lw=1.2, label="Treino (últimas 72h)")
        ax.plot(test.index, test.values, color="#27ae60", lw=1.5, label="Teste (real)")
        ax.plot(
            p_test_dates, prophet_test_fc["yhat"].clip(lower=0),
            color="#8e44ad", lw=1.5, linestyle="--", label="Prophet — Período de teste",
        )
        ax.plot(
            p_future_dates, prophet_future_fc["yhat"].clip(lower=0),
            color="#6c3483", lw=2, label=f"Prophet — Previsão ({n_forecast}h)",
        )
        ax.fill_between(
            p_future_dates,
            prophet_future_fc["yhat_lower"].clip(lower=0),
            prophet_future_fc["yhat_upper"],
            alpha=0.20, color="#6c3483", label="IC 95% (futuro)",
        )
        ax.fill_between(
            p_test_dates,
            prophet_test_fc["yhat_lower"].clip(lower=0),
            prophet_test_fc["yhat_upper"],
            alpha=0.12, color="#8e44ad",
        )
        ax.axvline(test.index[0], color="gray", linestyle=":", lw=1.5, label="Início Teste")
        ax.axvline(
            p_future_dates[0], color="#6c3483",
            linestyle=":", lw=1.5, label="Início Previsão Futura",
        )

        mae_p  = metricas.loc["Prophet", "MAE"]
        rmse_p = metricas.loc["Prophet", "RMSE"]
        mape_p = metricas.loc["Prophet", "MAPE (%)"]
        ax.set_title(
            f"Prophet  ·  MAE={mae_p:.1f}  |  RMSE={rmse_p:.1f}  |  MAPE={mape_p:.1f}%",
            fontsize=11, fontweight="bold",
        )
    else:
        ax.text(
            0.5, 0.5,
            "Prophet não disponível\nInstale com: pip install prophet",
            ha="center", va="center", fontsize=13, transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.6", facecolor="#f8f9fa", edgecolor="#dee2e6"),
        )
        ax.set_title("Prophet (não disponível)", fontsize=11, fontweight="bold")

    ax.set_ylabel("Nº de Falhas / Hora")
    ax.legend(fontsize=8, loc="upper left", ncol=2)
    ax.tick_params(axis="x", rotation=20, labelsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    caminho = OUTPUT_DIR / "previsao_falhas.png"
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"[OK] Previsões salvas em: {caminho}")


# ─── 9. Visualização de Comparação entre Modelos ──────────────────────────────

def visualizar_comparacao(
    test: pd.Series,
    arima_fc_mean: pd.Series,
    prophet_previsao,
    metricas: pd.DataFrame,
) -> None:
    """Gera gráfico de comparação: real × previsto e barras de métricas."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle(
        "Comparação de Modelos — ARIMA(1,1,1) × Prophet",
        fontsize=13, fontweight="bold",
    )

    y_real   = test.values
    y_arima  = arima_fc_mean.iloc[:len(test)].values

    # --- Scatter: Real × Previsto ---
    ax = axes[0]
    ax.scatter(
        y_real, y_arima, alpha=0.45, s=18, color="#e74c3c", zorder=3,
        label=f"ARIMA  (MAE={metricas.loc['ARIMA(1,1,1)', 'MAE']:.1f})",
    )
    if PROPHET_AVAILABLE and prophet_previsao is not None:
        y_prophet = prophet_previsao["yhat"].iloc[:len(test)].clip(lower=0).values
        ax.scatter(
            y_real, y_prophet, alpha=0.45, s=18, color="#6c3483", zorder=3,
            label=f"Prophet (MAE={metricas.loc['Prophet', 'MAE']:.1f})",
        )

    lim = max(y_real.max(), y_arima.max()) * 1.08
    ax.plot([0, lim], [0, lim], "k--", lw=1.2, label="Previsão perfeita")
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel("Valores Reais (falhas/hora)")
    ax.set_ylabel("Valores Previstos (falhas/hora)")
    ax.set_title("Real × Previsto — Período de Teste", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)

    # --- Barras: Métricas Comparativas ---
    ax = axes[1]
    metricas_cols = metricas.columns.tolist()
    n_metrics = len(metricas_cols)
    x     = np.arange(n_metrics)
    width = 0.35
    cores = ["#e74c3c", "#6c3483"]

    for i, (modelo, row) in enumerate(metricas.iterrows()):
        bars = ax.bar(
            x + i * width, row.values, width,
            label=modelo, color=cores[i % len(cores)], alpha=0.85,
        )
        for bar, v in zip(bars, row.values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + row.values.max() * 0.01,
                f"{v:.1f}", ha="center", fontsize=9,
            )

    ax.set_xticks(x + width * (len(metricas) - 1) / 2)
    ax.set_xticklabels(metricas_cols, fontsize=10)
    ax.set_title("Métricas de Precisão por Modelo", fontsize=11, fontweight="bold")
    ax.set_ylabel("Valor da Métrica")
    ax.legend(fontsize=9)

    plt.tight_layout()
    caminho = OUTPUT_DIR / "comparacao_modelos.png"
    plt.savefig(caminho, bbox_inches="tight")
    plt.close()
    print(f"[OK] Comparação salva em: {caminho}")


# ─── 10. Checklist Técnico ────────────────────────────────────────────────────

def checklist_tecnico(metricas: pd.DataFrame) -> None:
    print("\n" + "=" * 70)
    print("CHECKLIST TÉCNICO — ANÁLISE PREDITIVA")
    print("=" * 70)

    checks = {
        "Dados normalizados com StandardScaler":
            True,
        "PCA aplicado às features numéricas":
            (OUTPUT_DIR / "pca_analise.png").exists(),
        "ARIMA(1,1,1) treinado e previsão gerada":
            "ARIMA(1,1,1)" in metricas.index,
        "Prophet ajustado para tendências sazonais":
            PROPHET_AVAILABLE and "Prophet" in metricas.index,
        "Visualização de previsões futuras gerada":
            (OUTPUT_DIR / "previsao_falhas.png").exists(),
        "Comparação entre modelos gerada":
            (OUTPUT_DIR / "comparacao_modelos.png").exists(),
    }

    for desc, ok in checks.items():
        marcador = "[OK]" if ok else "[FAIL]"
        print(f"  {marcador} {desc}")

    total = sum(checks.values())
    print(f"\n  Resultado: {total}/{len(checks)} itens concluídos")
    print("=" * 70)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 70)
    print("ANÁLISE PREDITIVA — PCA + ARIMA + Prophet")
    print("Dataset: API Error Logs (220k registros)")
    print("=" * 70)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado: {INPUT_FILE}\n"
            "Certifique-se de que o arquivo está na raiz do projeto."
        )

    # ── Etapa 1–3: Normalização + PCA ──
    df = carregar_dados()
    scaler, X_scaled, _ = normalizar_dados(df)
    pca, X_pca          = aplicar_pca(X_scaled)
    visualizar_pca(pca, X_scaled, X_pca)

    # ── Etapa 4: Série Temporal ──
    serie = preparar_serie_temporal(df)

    split_idx = int(len(serie) * TRAIN_RATIO)
    train, test = serie.iloc[:split_idx], serie.iloc[split_idx:]

    print(f"\n[INFO] Treino: {len(train)} horas  "
          f"({train.index.min().date()} → {train.index.max().date()})")
    print(f"[INFO] Teste:  {len(test)} horas  "
          f"({test.index.min().date()} → {test.index.max().date()})")

    # ── Etapa 5: ARIMA ──
    arima_model, arima_fc_mean, arima_fc_ci = treinar_arima(train, test, FORECAST_HOURS)

    # ── Etapa 6: Prophet ──
    prophet_model, prophet_fc = treinar_prophet(train, test, FORECAST_HOURS)

    # ── Etapa 7–9: Métricas + Visualizações ──
    metricas = comparar_modelos(test, arima_fc_mean, prophet_fc)
    visualizar_previsoes(train, test, arima_fc_mean, arima_fc_ci, prophet_fc, metricas)
    visualizar_comparacao(test, arima_fc_mean, prophet_fc, metricas)

    # ── Checklist ──
    checklist_tecnico(metricas)

    print(f"\n[SUCCESS] Análise preditiva concluída!")
    print(f"[INFO] Gráficos salvos em: {OUTPUT_DIR}/")
    print(f"  → pca_analise.png         (StandardScaler + PCA)")
    print(f"  → previsao_falhas.png     (ARIMA e Prophet)")
    print(f"  → comparacao_modelos.png  (Métricas comparativas)")

    return metricas


if __name__ == "__main__":
    main()
