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

### Dataset nao encontrado

Certifique-se de que os arquivos estao no local correto:
- `api_error_logs_with_root_causes_220k_rows.csv` deve estar na raiz do projeto

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

## Proximos Passos

Com o dataset pre-processado, pode-se:

1. Executar Analise Exploratoria de Dados (EDA)
2. Criar visualizacoes
3. Fazer Feature Engineering
4. Treinar modelos de Machine Learning

## Suporte

Para mais detalhes sobre o pre-processamento, veja:
- `PREPROCESSING_REPORT.md` - Relatorio completo
- `src/data_cleaning.py` - Codigo com documentacao
- `src/analysis_report.py` - Script de validacao

---

**Status**: ✓ Projeto Pronto para Execucao
**Ultima Atualizacao**: 2024-03-03
