# PLANO DE TRABALHO: PREVISAO DE CONSUMO E REGRESSOES CLIMATICAS

- **Disciplina:** PGENE585 - Transição Energética Sustentável e Mercados de Energia
- **Programa:** PPGEE / UFAM (Faculdade de Tecnologia)
- **Professor:** Prof. Dr. Kenny Vinente
- **Aluno:** Aldair da Silva Azevedo
- **Data da Apresentação:** 17/10/2026 (Sábado)
- **Diretório do Trabalho:** `C:\Users\Aldai\OneDrive\Documentos\UFAM\Mestrado\PGENE585 - Transição Energética Sustentável e Mercados de Energia\energy-demand-forecast`

---

## 1. O que o Professor Pediu (Tratativas Oficiais)

O professor Kenny Vinente disponibilizou dois links com dados reais e definiu as diretrizes para a atividade:

1. **Link 1 (CMU 15-884):** Acessar o Problem Set 1 (data) e resolver os **itens 5 e 6**. Os métodos de resolução são livres (utilizaremos Python).
2. **Link 2 (Zenodo - Competicao 2025):** Utilizar os datasets da _"2025 Competition on Electric Energy Consumption Forecast Adopting Multi-criteria Performance Metrics"_ e atender ao que se pede na competição (previsão de consumo com métricas multi-critério).
3. **Entregável:** **Somente uma apresentação em slides** a ser apresentada em sala de aula (máximo de 10 minutos). É necessário explicar os procedimentos e métodos adotados.

---

## 2. O que Realmente e para Fazer (Detalhamento Tecnico)

### Parte 1: CMU 15-884 (Itens 5 e 6)

#### Item 5 (Regressoes Lineares e Nao-Lineares de Demanda vs. Temperatura)

- **Dados:** `q5_max_temp.txt` (temperatura máxima) e `q5_max_demand.txt` (demanda de pico).
- **Objetivo:** Ajustar e comparar 4 modelos preditivos com função de perda quadrática (L2 / Squared Loss):
  1. Regressão Linear Simples;
  2. Regressão Polinomial (grau d = 5);
  3. Regressão Não-Linear com 5 funções RBF (Radial Basis Functions com sigma = 20);
  4. Regressão Ridge com Kernel Gaussiano (sigma = 20, lambda = 1e-4).
- **Otimizacao com Perda Absoluta (L1 / Absolute Loss):** Resolver o mesmo problema com perda L1 para comparar a robustez frente a outliers em relação a perda L2.

#### Item 6 (Tratamento de Dados Brutos e Engenharia de Features)

- **Dados brutos:** `q6_demand.txt` (demanda de Duquesne Light) e `q6_weather.txt` (clima de Pittsburgh).
- **Limpeza:** Tratar registros com falha (valores -9999) e remover duplicidades temporais.
- **Sincronizacao:** Interpolar e alinhar timestamps UTC de clima com medições horárias de consumo.
- **Agregacao Diaria:** Calcular a temperatura máxima e demanda máxima diária.
- **Engenharia de Atributos:** Extrair temperatura mínima, ponto de orvalho médio, umidade média, pressão barométrica média, velocidade do vento e condição predominante.
- **Teste de Hipotese:** Demonstrar se usar essas múltiplas variáveis climáticas reduz o erro quadrático (MSE/RMSE) em comparação com usar apenas a temperatura máxima.

### Parte 2: Competicao Zenodo 2025 (Electric Energy Consumption Forecast)

- **Dados:** Telemetria de um Edifício Inteligente (Smart Building) com leituras a cada 5 minutos ao longo de 1 ano (`data_v1.0.xlsx` / `data_v2.0.xlsx`).
- **Variaveis disponiveis:** Tempo, Potência (W), Tensão (V), Corrente (A), Geração Solar Fotovoltaica em telhado (W) e Temperatura externa (C).
- **Objetivo:** Prever o consumo futuro de energia considerando a geração solar e o clima, avaliando métricas multi-critério: RMSE, MAE, R2 e tempo de processamento.

---

## 3. Estrutura de Pastas em energy-demand-forecast

Todos os arquivos deste trabalho ficam organizados dentro de `energy-demand-forecast`:

- `energy-demand-forecast/PLANO_DE_TRABALHO.md`: Este documento de planejamento e acompanhamento.
- `energy-demand-forecast/data/cmu/`: Arquivo `ps1.pdf` e dados brutos do Problem Set 1 (`q5_*.txt`, `q6_*.txt`).
- `energy-demand-forecast/data/zenodo/`: Planilhas da competição Zenodo (`data_v1.0.xlsx`, etc.).
- `energy-demand-forecast/src/`: Scripts e módulos em Python desenvolvidos para resolver as tarefas.
- `energy-demand-forecast/results/`: Gráficos gerados e tabelas de métricas de acurácia.
- `energy-demand-forecast/presentation/`: Slides da apresentação (formato PPTX e PDF).

---

## 4. Roteiro Planejado da Apresentacao (10 Slides)

Estrutura formal da apresentação:

- **Slide 1:** Capa Oficial (UFAM, FT, PPGEE, PGENE585, Nome do Aluno e Titulo).
- **Slide 2:** Introdução e Contexto: Previsão de demanda sob intermitência climática e geração solar.
- **Slide 3:** CMU Item 5: Metodologia de Regressão (MQO vs. L1, Polinomial, RBF e Kernel Gaussiano).
- **Slide 4:** CMU Item 5: Resultados Visuais e Comparativo de Curvas de Ajuste.
- **Slide 5:** CMU Item 6: Pipeline de Dados (Limpeza de ruídos -9999, Interpolação e Sincronização UTC).
- **Slide 6:** CMU Item 6: Modelo Multivariado (Impacto de vento, umidade e pressão no erro de previsão).
- **Slide 7:** Competição Zenodo 2025: Previsão em Smart Buildings com Geração Solar Fotovoltaica.
- **Slide 8:** Competição Zenodo 2025: Avaliação Multi-critério de Modelos (RMSE, MAE e Tempo).
- **Slide 9:** Discussão Prática: Aplicação no Mercado Livre e Gestão Residencial de Energia.
- **Slide 10:** Conclusões, Lições Aprendidas e Síntese Final.

---

## 5. Cronograma e Proximos Passos

1. **Etapa 1:** Validação deste planejamento em Markdown.
2. **Etapa 2:** Execução dos scripts em Python na pasta `energy-demand-forecast/src/` e geração dos gráficos em `energy-demand-forecast/results/`.
3. **Etapa 3:** Criação dos slides em `energy-demand-forecast/presentation/`.
4. **Etapa 4:** Apresentação em sala neste sábado (17/10/2026).
