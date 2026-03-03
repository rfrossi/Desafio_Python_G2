# Desafio 03 - Python Data Analysis

Projeto de análise de dados usando Python com ferramentas modernas de data science.

## 🛠️ Tecnologias

- **Python 3.13+**
- **Poetry** - Gerencimento de dependências e ambiente virtual
- **Pandas** - Manipulação e análise de dados
- **NumPy** - Computação numérica
- **Matplotlib** - Visualização estática
- **Seaborn** - Visualização estatística
- **Scikit-learn** - Machine learning

## 📋 Pré-requisitos

- Python 3.13 ou superior
- Poetry instalado (`pip install poetry`)

## 🚀 Setup do Projeto

### 1. Clonar ou inicializar o projeto

```bash
cd Desafio03_Python
```

### 2. Instalar dependências

```bash
poetry install
```

### 3. Ativar o ambiente virtual

```bash
poetry shell
```

Ou rodar comandos diretamente com:

```bash
poetry run python script.py
```

## 📁 Estrutura do Projeto

```
Desafio03_Python/
├── 01_documents/      # Documentação e materiais de referência
├── 02_research/       # Pesquisa e análise preliminar
├── main.py            # Script principal
├── pyproject.toml     # Configuração do Poetry
├── README.md          # Este arquivo
└── .gitignore         # Arquivos ignorados pelo Git
```

## 💡 Uso

Após instalar e ativar o ambiente:

```bash
poetry run python main.py
```

## 🔧 Configuração VS Code

O projeto já está pré-configurado para usar o Python do Poetry no VS Code. O interpretador apontará automaticamente para `.venv/bin/python`.

Se precisar reconhecê-lo manualmente:
1. Abra a paleta de comandos: `Ctrl+Shift+P`
2. Procure por: `Python: Select Interpreter`
3. Escolha a opção com `.venv`

## 📖 Recursos Úteis

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Matplotlib Documentation](https://matplotlib.org/)
