# Relatorio de Pre-processamento - Dataset AFID

## Resumo Executivo

O pre-processamento do dataset AFID foi executado com sucesso. O dataset contém 220.000 registros de logs de erros de API com 22 colunas.

- **Dataset Original**: 220.000 linhas × 22 colunas
- **Dataset Limpo**: 220.000 linhas × 22 colunas
- **Linhas Removidas**: 0 (nenhuma duplicata encontrada)
- **Tamanho do Arquivo Limpo**: 46.61 MB

## Criacao de Arquivos

### Scripts Criados

1. **src/data_cleaning.py** - Script principal de pré-processamento
   - Classe `AFIDDataCleaner` com métodos para limpeza
   - Detecção automática de colunas de data
   - Padronização de texto (Title case para categorias)
   - Tratamento de valores nulos
   - Validação de integridade dos dados

2. **src/analysis_report.py** - Script de análise comparativa
   - Compara dados antes e depois do processamento
   - Validação de tipos de dados
   - Análise de valores nulos
   - Verificação de duplicatas
   - Checklist técnico

### Dataset Limpo

- **api_error_logs_cleaned.csv** - Dataset processado e salvo

## Detalhes do Pre-processamento

### 1. Carregamento de Dados ✓

```
[OK] Dataset carregado: 220000 linhas, 22 colunas
```

### 2. Identificacao de Valores Ausentes ✓

Checklist: `[ ] Identificar valores ausentes com isnull()`

```python
df.isnull().sum()  # Aplicado em todas as colunas
```

**Resultado**: Encontrado 36.771 valores nulos na coluna 'error_type' (16.71%)

### 3. Conversao de Timestamps ✓

Checklist: `[ ] Colunas de data convertidas para datetime64[ns] via Pandas`

```
Coluna 'timestamp': str -> datetime64[us]
```

**Detalhes**:
- Tipo Final: `datetime64[us]` (microsegundos)
- Range: 2024-01-01 00:00:00 até 2024-01-13 17:33:15
- Valores Nulos: 0
- Erros na Conversão: 0

### 4. Padronizacao de Texto ✓

Checklist: `[ ] Padronizar capitalização de textos (ex: nomes de APIs)`

**Colunas Padronizadas** (aplicado Title Case):
1. `api_name` (ex: "Inventory-Api", "User-Api", "Order-Api")
2. `environment` (ex: "Dev", "Staging", "Prod", "Qa")
3. `http_method` (ex: "Delete", "Get", "Post", "Patch", "Put")
4. `error_type` (ex: "Timeout", "Clienterror", "Autherror")
5. `root_cause` (ex: "High Latency In Network", "Database Connection Failure")
6. `error_message` (com strip() para remover espaços)

### 5. Remocao de Duplicatas ✓

Checklist: `[ ] Remoção de duplicatas`

```
[OK] Nenhuma duplicata encontrada
```

### 6. Validacao de Tipos Numericos ✓

Checklist: `[ ] Validar integridade dos tipos numéricos`

**Colunas Numéricas (int64)**:

| Coluna | Min | Max | Média | Nulos |
|--------|-----|-----|-------|-------|
| status_code | 200 | 504 | 404.65 | 0 |
| latency_ms | 10 | 14999 | 7513.06 | 0 |
| request_size_bytes | 200 | 49999 | 25092.10 | 0 |
| response_size_bytes | 200 | 79999 | 40154.40 | 0 |
| retry_count | 0 | 4 | 2.00 | 0 |
| thread_id | 1000 | 9998 | 5500.07 | 0 |

**Coluna Booleana**:
- `is_retry_successful`: bool (valores True/False)

## Estrutura Final do Dataset

### Tipos de Dados

```
bool: 1 coluna
  - is_retry_successful

datetime64[us]: 1 coluna
  - timestamp

int64: 6 colunas
  - status_code
  - latency_ms
  - request_size_bytes
  - response_size_bytes
  - retry_count
  - thread_id

str: 14 colunas (texto/categorias)
  - api_name
  - service_owner
  - environment
  - http_method
  - endpoint
  - error_type
  - root_cause
  - client_ip
  - region
  - container_id
  - host_id
  - log_level
  - error_message
  - resolution_action
```

## Checklist Tecnico - Conclusao

| Item | Status | Detalhes |
|------|--------|----------|
| Identificar valores ausentes com `isnull()` | ✓ | 36.771 valores nulos encontrados e tratados |
| Padronizar capitalização de textos | ✓ | 6 colunas padronizadas com Title Case |
| Validar integridade dos tipos numéricos | ✓ | 6 colunas int64 e 1 coluna bool validadas |
| Converter timestamps para datetime64 | ✓ | Coluna 'timestamp' convertida para datetime64[us] |
| Remover duplicatas | ✓ | Nenhuma duplicata encontrada |
| Tratamento de valores nulos | ✓ | Valores nulos preenchidos com "Unknown" |
| Dataset salvo com sucesso | ✓ | api_error_logs_cleaned.csv (46.61 MB) |

## Como Usar os Scripts

### Executar Pre-processamento Completo

```bash
poetry run python src/data_cleaning.py
```

Saída:
- Dataset limpo: `api_error_logs_cleaned.csv`
- Log completo do processamento

### Gerar Relatório de Análise

```bash
poetry run python src/analysis_report.py
```

Saída:
- Comparação antes vs. depois
- Validação de tipos de dados
- Checklist técnico

## Dependências Utilizadas

- **pandas**: 3.0.1 (manipulação e análise de dados)
- **numpy**: 2.4.2 (operações numéricas)
- **Python**: 3.13

## Proximos Passos

Com o dataset pre-processado e limpo, os proximos cards podem:

1. **Card 3**: Análise Exploratória de Dados (EDA)
   - Estatísticas descritivas
   - Visualizações
   - Correlações entre variáveis

2. **Card 4**: Feature Engineering
   - Criação de novas features
   - Transformações de dados

3. **Card 5**: Modelagem
   - Seleção de modelos
   - Treinamento
   - Validação

## Notas Importantes

- O dataset não continha duplicatas, logo nenhuma linha foi removida
- A maioria dos valores nulos estava em 'error_type'; eles foram preenchidos com "Unknown"
- A conversão de timestamp utiliza precisão em microsegundos (datetime64[us]) em vez de nanosegundos
- A padronização de texto utiliza Title Case, apropriado para categorias e nomes de API

---

**Data**: 2024-03-03
**Status**: ✓ Concluído com Sucesso
**Desenvolvido com**: Claude Code + Python 3.13
