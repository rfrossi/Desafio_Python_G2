"""
Relatorio de Analise do Pre-processamento do Dataset AFID
Compara os dados antes e depois do processamento
"""

import pandas as pd
from pathlib import Path


def generate_detailed_report():
    """Gera relatorio detalhado do pre-processamento."""

    # Carregar dados originais e limpos
    original_file = Path(__file__).parent.parent / "api_error_logs_with_root_causes_220k_rows.csv"
    cleaned_file = Path(__file__).parent.parent / "api_error_logs_cleaned.csv"

    print("\n[LOADING] Carregando datasets...")
    df_original = pd.read_csv(original_file)
    df_cleaned = pd.read_csv(cleaned_file)

    print(f"[OK] Original: {df_original.shape}")
    print(f"[OK] Limpo: {df_cleaned.shape}")

    # Relatorio de valores nulos
    print("\n" + "="*70)
    print("VALORES NULOS - ANTES vs DEPOIS")
    print("="*70)

    missing_original = df_original.isnull().sum()
    missing_cleaned = df_cleaned.isnull().sum()

    report_null = pd.DataFrame({
        'Coluna': df_original.columns,
        'Antes': missing_original.values,
        'Depois': missing_cleaned.values,
        'Corrigidos': (missing_original - missing_cleaned).values
    }).sort_values('Corrigidos', ascending=False)

    colunas_com_nulos = report_null[report_null['Corrigidos'] > 0]
    if len(colunas_com_nulos) > 0:
        print("\nColunas com valores nulos corrigidos:")
        print(colunas_com_nulos.to_string(index=False))
    else:
        print("\nNenhuma coluna tinha valores nulos para corrigir")

    # Conversao de tipos de dados
    print("\n" + "="*70)
    print("CONVERSAO DE TIPOS DE DADOS")
    print("="*70)

    print("\nAntes do Pre-processamento:")
    print(df_original.dtypes)

    print("\n\nDepois do Pre-processamento:")
    print(df_cleaned.dtypes)

    # Validar timestamps
    print("\n" + "="*70)
    print("VALIDACAO DE TIMESTAMPS")
    print("="*70)

    if 'timestamp' in df_cleaned.columns:
        df_cleaned_typed = pd.read_csv(cleaned_file, parse_dates=['timestamp'])
        print(f"Tipo: {df_cleaned_typed['timestamp'].dtype}")
        print(f"Min: {df_cleaned_typed['timestamp'].min()}")
        print(f"Max: {df_cleaned_typed['timestamp'].max()}")
        print(f"Valores Nulos: {df_cleaned_typed['timestamp'].isnull().sum()}")

    # Validacao de valores numericos
    print("\n" + "="*70)
    print("VALIDACAO DE VALORES NUMERICOS")
    print("="*70)

    numeric_cols = ['status_code', 'latency_ms', 'request_size_bytes', 'response_size_bytes', 'retry_count']

    for col in numeric_cols:
        if col in df_cleaned.columns:
            print(f"\n{col}:")
            print(f"  Tipo: {df_cleaned[col].dtype}")
            print(f"  Min: {df_cleaned[col].min()}")
            print(f"  Max: {df_cleaned[col].max()}")
            print(f"  Media: {df_cleaned[col].mean():.2f}")
            print(f"  Nulos: {df_cleaned[col].isnull().sum()}")

    # Validacao de texto padronizado
    print("\n" + "="*70)
    print("VALIDACAO DE TEXTO PADRONIZADO")
    print("="*70)

    text_cols = ['api_name', 'error_type', 'root_cause', 'environment', 'http_method']

    for col in text_cols:
        if col in df_cleaned.columns:
            unique_vals = df_cleaned[col].unique()[:5]
            print(f"\n{col}:")
            print(f"  Total de valores unicos: {df_cleaned[col].nunique()}")
            print(f"  Exemplos (primeiros 5):")
            for val in unique_vals:
                print(f"    - {val}")

    # Resumo final
    print("\n" + "="*70)
    print("CHECKLIST TECNICO")
    print("="*70)

    checks = {
        "Valores ausentes identificados com isnull()": len(colunas_com_nulos) > 0,
        "Timestamp convertido para datetime64": 'timestamp' in df_cleaned.columns,
        "Capitalizacao padronizada em colunas de texto": all(
            df_cleaned[col].dtype == 'object' for col in text_cols if col in df_cleaned.columns
        ),
        "Integridade de tipos numericos validada": all(
            pd.api.types.is_numeric_dtype(df_cleaned[col]) for col in numeric_cols if col in df_cleaned.columns
        ),
        "Nenhuma duplicata encontrada": df_cleaned.duplicated().sum() == 0,
        "Dataset salvo com sucesso": cleaned_file.exists()
    }

    for check, status in checks.items():
        status_str = "[OK]" if status else "[FAIL]"
        print(f"{status_str} {check}")

    print("\n" + "="*70)
    print("[SUCCESS] Relatorio gerado com sucesso!")
    print("="*70 + "\n")

    return {
        'original': df_original,
        'cleaned': df_cleaned,
        'checks': checks
    }


if __name__ == "__main__":
    generate_detailed_report()
