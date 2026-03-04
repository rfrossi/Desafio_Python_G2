# Insights do Projeto: Análise de Falhas de API (AFID)

Este documento centraliza os principais aprendizados e conclusões extraídos das quatro etapas do projeto (Limpeza, Análise Descritiva, Preditiva e Dashboard Interativo), com foco em fornecer material rico para a apresentação à banca.

## 1. Limpeza e Qualidade de Dados (Pré-processamento)
- **Descoberta:** O dataset apresentava aproximadamente 16,7% (36.771 registros) de valores ausentes apenas na coluna `error_type`. O preenchimento com "Undefined" garante que as dimensões da equipe e as estatísticas não sejam distorcidas, mantendo as informações de latência e contagem intactas.
- **Padronização:** A conversão correta da coluna `timestamp` e a homogeneização em Title Case em nomenclaturas como `api_name` e `environment` foram cruciais para que o Streamlit pudesse agrupar as métricas temporais corretamente, sem sujas em variações da mesma string.

## 2. Análise Descritiva e Anomalias
- **Volume de Falhas:** O período analisado compreende 306 horas (1 a 13 de Janeiro), apresentando picos bem definidos, com o volume de falhas atingindo uma máxima de 720 falhas/hora, um indicativo importante de gargalos sistêmicos de alta carga.
- **Outliers de Latência e Tamanho:** Na análise utilizando Boxplot (método IQR), nós definimos limites muito amplos de tolerância para os cenários atuais de latência (limite superior de 22.512ms) e tamanho de requisição. A análise automatizada identificou 0% de outliers formais sob esse critério matemático nos 220.000 registros, o que aponta para um comportamento de falhas distribuído sem comportamentos anômalos isolados e isolados extremos nestes quesitos.
- **Correlação Direta:** A matriz de correlação horária indicou uma correlação sutil (linear) negativa entre latência média e taxa de falhas (r = -0.05). Na agregação em nível da API, outros fatores não lineares afetam mais o volume de falhas que a carga puramente bruta.

## 3. Análise Preditiva e Sazonalidade
- **Simplificação de Dimensionalidade (PCA):** A Análise de Componentes Principais reduziu o dataset condensando features numéricas como latência, tamanhos de pacote, contagem de retries e status code. O PCA capturou **60.3% da variância total** nos 3 primeiros componentes (cada um com ~20%), equilibrando a importância de todas as variáveis no monitoramento holístico do tráfego.
- **Projeção Futura (ARIMA vs. Prophet):**
  - **Resultado na Prática:** O **ARIMA(1,1,1)** reportou a melhor precisão média neste conjunto específico, vencendo o Prophet com ligeira vantagem de estabilidade com um Erro Quadrático Médio (RMSE) menor (ARIMA = 34.61 vs Prophet = 34.80) e um Erro Médio Absoluto Quase idêntico (~11.5).
  - Ambos os modelos mantiveram um Margem de Erro Percentual Absoluta (MAPE) incrivelmente baixa, oscilando perto de **2.48%**, mostrando alta aptidão para prever picos sazonais (ondas base diárias) no volume futuro em um horizonte de 48h.

## 4. O Valor de Negócio (Dashboard Interativo)
- **Agilidade na Resolução:** O dashboard do `Streamlit` permite cruzar `Período, Equipe, Ambiente e API`, resolvendo o problema de "onde está a falha?" em tempo real para times de SRE e Backend.
- **Heatmap de Atribuição:** O gráfico que cruza `Equipe` e `Tipo de Erro` é a principal ferramenta gerencial criada. Se "team-alpha" domina os "AuthErrors" mas tem baixos "Timeout", e o "team-beta" sofre mais com "DatabaseError", a diretoria de TI pode alocar orçamentos focados no problema específico de cada squad.

## Resumo para a Banca
1. **Governança de Dados resolvida** com tratamentos sistemáticos via `pandas`.
2. **Diagnóstico estatístico** implementado com detecção local de tendências falhas (EDA).
3. **Poder preditivo** estabelecido, abrindo portas para alertar as equipes 48h antes da possível fadiga sistêmica.
4. **Governança Visual e Operacional** implementada de forma ágil com Streamlit e Plotly.
