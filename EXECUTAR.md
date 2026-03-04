# Como Rodar o Projeto - Desafio Python G2

## Estado Atual do Projeto

O projeto possui os seguintes scripts implementados:

```
src/
├── data_cleaning.py      # Script de pre-processamento (COMPLETO)
└── analysis_report.py    # Script de analise comparativa (COMPLETO)
```

Arquivos de saida gerados:
- `api_error_logs_cleaned.csv` - Dataset pre-processado (220k linhas)
- `PREPROCESSING_REPORT.md` - Relatorio detalhado do pre-processamento

## Prerequisitos

1. **Python 3.13+** instalado
2. **Poetry** instalado (`pip install poetry`)
3. **Dataset Kaggle**: Baixe o arquivo CSV do dataset no [Kaggle: API Failure Intelligence Dataset (AFID)](https://www.kaggle.com/datasets/mirzayasirabdullah07/api-failure-intelligence-dataset-afid/). Salve-o na raiz do projeto com o nome exato: `api_error_logs_with_root_causes_220k_rows.csv`.

## Instalacao das Dependencias

Execute uma unica vez para configurar o ambiente:

```bash
cd C:\Users\levis\Desktop\Projeto\Desafio_Python_G2
poetry install
```

Isso instalara:
- pandas >= 3.0.1
- numpy >= 2.4.2
- matplotlib >= 3.10.8
- seaborn >= 0.13.2
- scikit-learn >= 1.8.0

## Rodar os Scripts

### Opcao 1: Com Poetry (Recomendado)

#### 1. Pre-processamento do Dataset

```bash
poetry run python src/data_cleaning.py
```

**Saida esperada**:
- Logs do processamento na tela
- Arquivo: `api_error_logs_cleaned.csv` (46.61 MB)
- Tempo estimado: 20-30 segundos

**Exemplo de saida**:
```
======================================================================
INICIANDO PRE-PROCESSAMENTO DO DATASET AFID
======================================================================
[OK] Dataset carregado: 220000 linhas, 22 colunas

[INFO] Valores Ausentes Identificados:
    coluna  valores_nulos  percentual
error_type          36771   16.714091

[DATETIME] Convertendo colunas de data para datetime64[ns]...
  [OK] timestamp: str -> datetime64[us]

[TEXT] Padronizando textos...
  [OK] api_name: capitalizacao padronizada
  [OK] environment: capitalizacao padronizada
  ...

[OK] Dataset limpo salvo em: C:\Users\levis\Desktop\Projeto\Desafio_Python_G2\api_error_logs_cleaned.csv
  Tamanho: 46.61 MB

[SUCCESS] Pre-processamento concluido com sucesso!
```

#### 2. Gerar Relatorio de Analise

```bash
poetry run python src/analysis_report.py
```

**Saida esperada**:
- Comparacao antes vs. depois do processamento
- Validacao de tipos de dados
- Checklist tecnico completo
- Tempo estimado: 30-40 segundos

**Exemplo de saida**:
```
[LOADING] Carregando datasets...
[OK] Original: (220000, 22)
[OK] Limpo: (220000, 22)

======================================================================
VALORES NULOS - ANTES vs DEPOIS
======================================================================
...

======================================================================
CHECKLIST TECNICO
======================================================================
[OK] Valores ausentes identificados com isnull()
[OK] Timestamp convertido para datetime64
[OK] Capitalizacao padronizada em colunas de texto
[OK] Integridade de tipos numericos validada
[OK] Nenhuma duplicata encontrada
[OK] Dataset salvo com sucesso

[SUCCESS] Relatorio gerado com sucesso!
```

### Opcao 2: Ativar Ambiente Virtual

Se preferir trabalhar dentro do ambiente virtual do Poetry:

```bash
# Ativar o ambiente virtual
poetry shell

# Rodar scripts sem prefixo 'poetry run'
python src/data_cleaning.py
python src/analysis_report.py

# Sair do ambiente
exit
```

## Estrutura de Arquivos Criados

```
Desafio_Python_G2/
├── src/
│   ├── data_cleaning.py          # Script principal (280+ linhas)
│   └── analysis_report.py        # Script de analise (170+ linhas)
├── api_error_logs_with_root_causes_220k_rows.csv    # Dataset original
├── api_error_logs_cleaned.csv    # Dataset processado [SAIDA]
├── PREPROCESSING_REPORT.md       # Relatorio em Markdown
├── EXECUTAR.md                   # Este arquivo
├── pyproject.toml
├── poetry.lock
└── README.md
```

## Verificacao de Sucesso

Apos executar `poetry run python src/data_cleaning.py`, verifique:

1. **Arquivo gerado**: `api_error_logs_cleaned.csv` existe
2. **Tamanho**: Aproximadamente 46.61 MB
3. **Log final**: Mensagem "[SUCCESS] Pre-processamento concluido com sucesso!"

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'pandas'"

Solucao:
```bash
poetry install
```

### Erro de Encoding (Windows)

Se encontrar erros de codificacao UTF-8:

```bash
# Use o comando com chcp 65001 antes
chcp 65001
poetry run python src/data_cleaning.py
```

### Dataset nao encontrado ou nome incorreto

Certifique-se de que os arquivos estao no local correto:
- O arquivo baixado do Kaggle deve estar na raiz do projeto.
- O nome deve ser **exatamente** `api_error_logs_with_root_causes_220k_rows.csv`.

### Lentidao ao processar

O dataset tem 220k linhas. Tempo normal:
- Carregamento: ~5-10 segundos
- Processamento: ~15-20 segundos
- Salvamento: ~5 segundos

## Checklist Tecnico Completado

- [x] Script data_cleaning.py funcional
- [x] Colunas de data convertidas para datetime64[us] via Pandas
- [x] Remocao de duplicatas implementada
- [x] Correcao de inconsistencias de texto (Title Case)
- [x] Identificacao de valores ausentes com isnull()
- [x] Padronizacao de capitalizacao (ex: nomes de APIs)
- [x] Validacao de integridade dos tipos numericos
- [x] Relatorio de analise gerado
- [x] Dataset limpo salvo em CSV

## Card 3 - Analise Descritiva

#### 3. Analise Descritiva (Card 3)

```bash
poetry run python src/descriptive_analysis.py
```

**Saida esperada**:
- Estatisticas descritivas (media, mediana, desvio padrao) de latency_ms, request_size_bytes e response_size_bytes
- Deteccao de outliers via IQR para as tres metricas
- Graficos salvos em `outputs/`:
  - `histogramas_erros.png` - Top 15 tipos de erro + histogramas de latencia e tamanho
  - `serie_temporal_falhas.png` - Volume de falhas por hora (01/01/2024 a 13/01/2024)
  - `matriz_correlacao.png` - Correlacao entre carga da API e taxa de falha

**Checklist Card 3**:
- [x] Media, mediana e desvio padrao calculados
- [x] Outliers identificados com IQR
- [x] Histogramas de distribuicao dos erros gerados
- [x] Matriz de correlacao entre carga e taxa de falha gerada

## Card 4 - Analise Preditiva (PCA + ARIMA + Prophet)

#### 4. Analise Preditiva

```bash
poetry run python src/predictive_analysis.py
```

**O que este script faz**:
1. Normaliza as features numericas com `StandardScaler`
2. Aplica `PCA` com 3 componentes para reducao de dimensionalidade
3. Agrega falhas por hora para criar serie temporal
4. Treina modelo `ARIMA(1,1,1)` e gera previsao para 48h futuras
5. Treina modelo `Prophet` com sazonalidade diaria e gera previsao para 48h futuras
6. Compara os modelos com MAE, RMSE e MAPE

**Graficos gerados em `outputs/`**:
- `pca_analise.png`         - Scree plot, loadings e dispersao PC1 x PC2
- `previsao_falhas.png`     - Previsoes futuras de ARIMA e Prophet
- `comparacao_modelos.png`  - Scatter real x previsto + barras de metricas

**Dependencias adicionais necessarias**:
```bash
# Instala statsmodels e prophet junto com todas as dependencias
poetry install
```

> **Nota**: O Prophet requer `cmdstanpy` como backend. Em caso de problemas
> na instalacao, tente: `pip install prophet` diretamente no ambiente.
> O script funciona normalmente sem o Prophet (ARIMA continua disponivel).

**Exemplo de saida**:
```
======================================================================
ANALISE PREDITIVA — PCA + ARIMA + Prophet
Dataset: API Error Logs (220k registros)
======================================================================
[LOADING] api_error_logs_with_root_causes_220k_rows.csv
[OK] 220,000 linhas x 22 colunas

======================================================================
2. NORMALIZACAO — StandardScaler
======================================================================
[INFO] Features: ['latency_ms', 'request_size_bytes', ...]
[INFO] Amostras: 50,000
  latency_ms         media=+0.0000  std=1.0000
  ...

======================================================================
3. REDUCAO DE DIMENSIONALIDADE — PCA
======================================================================
[OK] PCA com 3 componentes principais:
  PC1:   52.3%   ████████████████████████   (acumulada: 52.3%)
  PC2:   28.1%   █████████████              (acumulada: 80.4%)
  PC3:   12.6%   ██████                     (acumulada: 93.0%)

======================================================================
7. COMPARACAO DE MODELOS — METRICAS DE PRECISAO
======================================================================
  ARIMA(1,1,1)  →  MAE=XX.XX  |  RMSE=XX.XX  |  MAPE=XX.XX%
  Prophet       →  MAE=XX.XX  |  RMSE=XX.XX  |  MAPE=XX.XX%
  Melhor modelo por RMSE: Prophet

======================================================================
CHECKLIST TECNICO — ANALISE PREDITIVA
======================================================================
  [OK] Dados normalizados com StandardScaler
  [OK] PCA aplicado as features numericas
  [OK] ARIMA(1,1,1) treinado e previsao gerada
  [OK] Prophet ajustado para tendencias sazonais
  [OK] Visualizacao de previsoes futuras gerada
  [OK] Comparacao entre modelos gerada

  Resultado: 6/6 itens concluidos

[SUCCESS] Analise preditiva concluida!
```

**Checklist Card 4**:
- [x] Dados normalizados com StandardScaler
- [x] PCA com 3 componentes aplicado
- [x] ARIMA(1,1,1) treinado com previsao de 48h
- [x] Prophet com sazonalidade diaria ajustado
- [x] Metricas MAE, RMSE e MAPE calculadas para ambos os modelos
- [x] Visualizacoes de previsoes e comparacao geradas

## Suporte

Para mais detalhes sobre cada etapa, veja:
- `PREPROCESSING_REPORT.md` - Relatorio completo do pre-processamento
- `src/data_cleaning.py` - Codigo com documentacao (Card 1/2)
- `src/analysis_report.py` - Script de validacao (Card 1/2)
- `src/descriptive_analysis.py` - Analise descritiva (Card 3)
- `src/predictive_analysis.py` - Analise preditiva PCA + ARIMA + Prophet (Card 4)

---

**Status**: Projeto com Cards 1, 2, 3 e 4 concluidos
**Ultima Atualizacao**: 2026-03-03
