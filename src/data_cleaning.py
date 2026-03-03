"""
Data Cleaning Script for AFID Dataset

Este script realiza o pré-processamento do dataset AFID:
- Carregamento de dados
- Conversão de tipos de dados (especialmente timestamps)
- Tratamento de valores nulos
- Remoção de duplicatas
- Padronização de texto
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple


class AFIDDataCleaner:
    """Classe para limpeza e pré-processamento do dataset AFID."""

    def __init__(self, filepath: str):
        """
        Inicializa o limpador de dados.

        Args:
            filepath: Caminho para o arquivo CSV do dataset AFID
        """
        self.filepath = Path(filepath)
        self.df = None
        self.original_shape = None
        self.cleaning_log = []

    def load_data(self) -> pd.DataFrame:
        """
        Carrega o dataset AFID do arquivo CSV.

        Returns:
            DataFrame carregado
        """
        if not self.filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.filepath}")

        self.df = pd.read_csv(self.filepath)
        self.original_shape = self.df.shape
        self.cleaning_log.append(f"Dataset carregado: {self.original_shape}")

        print(f"[OK] Dataset carregado: {self.original_shape[0]} linhas, {self.original_shape[1]} colunas")
        return self.df

    def identify_missing_values(self) -> pd.DataFrame:
        """
        Identifica valores ausentes no dataset usando isnull().

        Returns:
            DataFrame com informações sobre valores nulos
        """
        missing_info = pd.DataFrame({
            'coluna': self.df.columns,
            'valores_nulos': self.df.isnull().sum().values,
            'percentual': (self.df.isnull().sum() / len(self.df) * 100).values
        }).sort_values('valores_nulos', ascending=False)

        missing_info = missing_info[missing_info['valores_nulos'] > 0]

        if len(missing_info) > 0:
            print("\n[INFO] Valores Ausentes Identificados:")
            print(missing_info.to_string(index=False))
            self.cleaning_log.append(f"Valores nulos encontrados em {len(missing_info)} colunas")
        else:
            print("\n[OK] Nenhum valor nulo encontrado")
            self.cleaning_log.append("Nenhum valor nulo encontrado")

        return missing_info

    def convert_datetime_columns(self) -> None:
        """
        Converte colunas de data para datetime64[ns].
        Detecta automaticamente colunas de data por nome.
        """
        print("\n[DATETIME] Convertendo colunas de data para datetime64[ns]...")

        # Detecta possíveis colunas de data por nome
        date_keywords = ['timestamp', 'date', 'time', 'data', 'hora', 'criado', 'modificado', 'atualizado']
        date_columns = [col for col in self.df.columns
                       if any(keyword in col.lower() for keyword in date_keywords)]

        converted_count = 0
        for col in date_columns:
            try:
                original_dtype = str(self.df[col].dtype)
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                new_dtype = str(self.df[col].dtype)
                print(f"  [OK] {col}: {original_dtype} -> {new_dtype}")
                self.cleaning_log.append(f"Coluna '{col}' convertida para {new_dtype}")
                converted_count += 1
            except Exception as e:
                print(f"  [ERROR] {col}: erro na conversao - {str(e)}")
                self.cleaning_log.append(f"Erro ao converter '{col}': {str(e)}")

        print(f"\n[OK] Total de colunas de data convertidas: {converted_count}")

    def standardize_text(self) -> None:
        """
        Padroniza capitalização de textos em colunas string.
        Ex: nomes de APIs, tipos de erro, etc.
        """
        print("\n[TEXT] Padronizando textos...")

        text_columns = self.df.select_dtypes(include=['object', 'str']).columns
        standardized_count = 0

        for col in text_columns:
            try:
                # Remove espaços em branco no início/fim
                self.df[col] = self.df[col].str.strip()

                # Para colunas que parecem ser nomes de APIs, tipos de erro, etc
                if any(keyword in col.lower() for keyword in ['api', 'name', 'type', 'error', 'cause', 'environment', 'method']):
                    self.df[col] = self.df[col].str.title()
                    standardized_count += 1
                    print(f"  [OK] {col}: capitalizacao padronizada")
                    self.cleaning_log.append(f"Coluna '{col}' padronizada com capitalizacao titulo")
            except Exception as e:
                print(f"  [WARN] {col}: erro ao padronizar - {str(e)}")

        print(f"\n[OK] Total de colunas padronizadas: {standardized_count}")

    def remove_duplicates(self) -> None:
        """
        Remove registros duplicados do dataset.
        """
        print("\n[DUPLICATES] Removendo duplicatas...")

        duplicates_before = self.df.duplicated().sum()

        if duplicates_before > 0:
            self.df = self.df.drop_duplicates().reset_index(drop=True)
            duplicates_after = self.df.duplicated().sum()
            print(f"  [OK] {duplicates_before} linhas duplicadas removidas")
            print(f"  [OK] Linhas restantes: {len(self.df)}")
            self.cleaning_log.append(f"{duplicates_before} linhas duplicadas removidas")
        else:
            print("  [OK] Nenhuma duplicata encontrada")
            self.cleaning_log.append("Nenhuma duplicata encontrada")

    def validate_numeric_types(self) -> pd.DataFrame:
        """
        Valida integridade dos tipos numericos.

        Returns:
            DataFrame com informacoes de validacao
        """
        print("\n[NUMERIC] Validando tipos numericos...")

        numeric_columns = self.df.select_dtypes(include=[np.number]).columns
        validation_results = []

        for col in numeric_columns:
            stats = {
                'coluna': col,
                'tipo': str(self.df[col].dtype),
                'min': self.df[col].min(),
                'max': self.df[col].max(),
                'media': round(self.df[col].mean(), 2),
                'nulos': self.df[col].isnull().sum()
            }
            validation_results.append(stats)
            print(f"  [OK] {col} ({stats['tipo']}): min={stats['min']}, max={stats['max']}, media={stats['media']}")
            self.cleaning_log.append(f"Validacao de '{col}': {stats['tipo']}")

        if not validation_results:
            print("  Nenhuma coluna numerica encontrada")

        return pd.DataFrame(validation_results) if validation_results else pd.DataFrame()

    def handle_missing_values(self) -> None:
        """
        Trata valores nulos baseado na analise anterior.
        """
        print("\n[MISSING] Tratando valores nulos...")

        missing_before = self.df.isnull().sum().sum()

        if missing_before == 0:
            print("  [OK] Nenhum valor nulo para tratar")
            return

        # Para colunas numericas, preencher com mediana
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if self.df[col].isnull().any():
                median_val = self.df[col].median()
                self.df[col].fillna(median_val, inplace=True)
                print(f"  [OK] {col}: valores nulos preenchidos com mediana ({median_val})")
                self.cleaning_log.append(f"Valores nulos de '{col}' preenchidos com mediana")

        # Para colunas de texto, preencher com "Unknown"
        text_cols = self.df.select_dtypes(include=['object', 'str']).columns
        for col in text_cols:
            if self.df[col].isnull().any():
                self.df[col] = self.df[col].fillna("Unknown")
                print(f"  [OK] {col}: valores nulos preenchidos com 'Unknown'")
                self.cleaning_log.append(f"Valores nulos de '{col}' preenchidos com 'Unknown'")

        missing_after = self.df.isnull().sum().sum()
        print(f"\n[OK] Valores nulos tratados: {missing_before} -> {missing_after}")

    def generate_report(self) -> dict:
        """
        Gera relatorio completo do pre-processamento.

        Returns:
            Dicionario com informacoes do processamento
        """
        report = {
            'shape_original': self.original_shape,
            'shape_final': self.df.shape,
            'linhas_removidas': self.original_shape[0] - self.df.shape[0],
            'colunas': list(self.df.columns),
            'tipos_dados': self.df.dtypes.to_dict(),
            'log': self.cleaning_log
        }

        print("\n" + "="*70)
        print("RELATORIO FINAL DO PRE-PROCESSAMENTO")
        print("="*70)
        print(f"Shape Original:        {report['shape_original']}")
        print(f"Shape Final:           {report['shape_final']}")
        print(f"Linhas Removidas:      {report['linhas_removidas']}")
        print(f"\nTipos de Dados ({len(report['tipos_dados'])} colunas):")

        # Agrupar por tipo
        dtypes_grouped = {}
        for col, dtype in report['tipos_dados'].items():
            dtype_str = str(dtype)
            if dtype_str not in dtypes_grouped:
                dtypes_grouped[dtype_str] = []
            dtypes_grouped[dtype_str].append(col)

        for dtype, cols in sorted(dtypes_grouped.items()):
            print(f"  {dtype}: {len(cols)} colunas")
            for col in cols[:3]:  # mostrar apenas as 3 primeiras
                print(f"    - {col}")
            if len(cols) > 3:
                print(f"    ... e mais {len(cols) - 3}")

        print("="*70 + "\n")

        return report

    def save_cleaned_data(self, output_path: str) -> None:
        """
        Salva o dataset limpo em um novo arquivo CSV.

        Args:
            output_path: Caminho para salvar o arquivo limpo
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        self.df.to_csv(output_file, index=False)
        file_size = output_file.stat().st_size / (1024 * 1024)  # em MB
        print(f"[OK] Dataset limpo salvo em: {output_file}")
        print(f"  Tamanho: {file_size:.2f} MB")
        self.cleaning_log.append(f"Dataset salvo em: {output_file}")

    def process(self, output_path: str = None) -> Tuple[pd.DataFrame, dict]:
        """
        Executa o pipeline completo de limpeza e pre-processamento.

        Args:
            output_path: Caminho para salvar dados limpos (opcional)

        Returns:
            Tupla com DataFrame limpo e relatorio
        """
        print("\n" + "="*70)
        print("INICIANDO PRE-PROCESSAMENTO DO DATASET AFID")
        print("="*70)

        self.load_data()
        self.identify_missing_values()
        self.convert_datetime_columns()
        self.standardize_text()
        self.remove_duplicates()
        self.handle_missing_values()
        self.validate_numeric_types()

        report = self.generate_report()

        if output_path:
            self.save_cleaned_data(output_path)

        return self.df, report


def main():
    """Funcao principal para execucao do script."""

    # Defina o caminho do arquivo de entrada
    input_file = Path(__file__).parent.parent / "api_error_logs_with_root_causes_220k_rows.csv"
    output_file = Path(__file__).parent.parent / "api_error_logs_cleaned.csv"

    try:
        cleaner = AFIDDataCleaner(str(input_file))
        df_cleaned, report = cleaner.process(output_path=str(output_file))
        print("\n[SUCCESS] Pre-processamento concluido com sucesso!")
        return df_cleaned, report

    except FileNotFoundError as e:
        print(f"\n[ERROR] Erro: {e}")
        print(f"\nCertifique-se de que o arquivo esta em: {input_file}")
        return None, None
    except Exception as e:
        print(f"\n[ERROR] Erro durante o processamento: {e}")
        raise


if __name__ == "__main__":
    main()
