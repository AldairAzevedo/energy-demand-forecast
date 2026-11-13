# PLANO DE TRABALHO: PREVISÃO DE CONSUMO EM SMART BUILDINGS

- **Disciplina:** PGENE585 - Transição Energética Sustentável e Mercados de Energia
- **Programa:** PPGEE / UFAM (Faculdade de Tecnologia)
- **Professor:** Prof. Dr. Kenny Vinente
- **Aluno:** Aldair da Silva Azevedo
- **Repositório:** [energy-demand-forecast](https://github.com/AldairAzevedo/energy-demand-forecast)
- **Aplicação Online:** [energy-demand-forecast-ufam.streamlit.app](https://energy-demand-forecast-ufam.streamlit.app/)

---

## 1. Diretriz do Desafio: Competição Zenodo 2025

A atividade é focada exclusivamente no desafio **"2025 Competition on Electric Energy Consumption Forecast Adopting Multi-criteria Performance Metrics"** (Zenodo):

1. **Base de Telemetria Real:** 1 ano de monitoramento a cada 5 minutos (105.120 leituras) de um Edifício Inteligente (Smart Building).
2. **Grandezas Monitoradas:** Potência Ativa (W), Tensão (V), Corrente (A), Temperatura externa (°C) e Geração Fotovoltaica em telhado (W).
3. **Objetivo Preditivo:** Previsão horária de consumo predial e análise de Demanda Líquida (Net Load = Consumo − Solar), identificando a formação da Curva do Pato e viabilizando estratégias de autoconsumo e sistemas de baterias (BESS).
4. **Métricas Multi-critério:** RMSE, MAE, R² Score e Tempo de Processamento Computacional (ms).

---

## 2. Arquitetura da Solução (Clean Code & Zero Trash)

O projeto adota arquitetura monolítica full stack moderna em Python:

```
energy-demand-forecast/
├── data/
│   ├── baseline/zenodo/      # Cópia protegida do dataset oficial de referência
│   ├── zenodo/               # Planilhas da competição (data_v1.0.xlsx)
│   └── cycles/               # Persistência auditável em JSON (cycle_07)
├── docs/                     # Enunciado oficial (zenodo.pdf) e plano de trabalho
├── results/                  # Figuras e gráficos em alta resolução (300 DPI)
├── presentation/             # Apresentação executiva de 7 slides (PPTX e PDF)
├── src/
│   ├── core/                 # Métricas multi-critério (RMSE, MAE, R², tempo)
│   ├── pipelines/            # ZenodoPipeline e orquestrador CycleManager
│   ├── ui/                   # Aplicação Streamlit reativa e gráficos Plotly
│   └── utils/                # I/O atômico de arquivos JSON
├── tests/                    # Suíte completa de testes unitários e de integração
├── streamlit_app.py          # Ponto de entrada do deploy Streamlit Cloud
├── requirements.txt          # Dependências do projeto
└── README.md                 # Guia completo de instalação e operação
```

---

## 3. Roteiro da Apresentação Executiva (7 Slides / 10 Minutos)

- **Slide 1:** Capa Oficial (UFAM / PPGEE / PGENE585 / Prof. Dr. Kenny Vinente / Aldair Azevedo).
- **Slide 2:** Contexto do Desafio Zenodo: Telemetria de Smart Building e Transição Energética.
- **Slide 3:** Arquitetura da Solução: Ingestão, agregação horária e engenharia de lags temporais (t-1 e t-24).
- **Slide 4:** Benchmarking Multi-critério: Ridge Linear vs. Random Forest (R² = 0.900, campeão em acurácia).
- **Slide 5:** Análise Visual da Curva de Carga e Demanda Líquida (Curva do Pato com 13,53% de cobertura solar).
- **Slide 6:** Plataforma Web Online (Streamlit Cloud): Retreinamento ao vivo, upload em massa e reset de fábrica.
- **Slide 7:** Conclusões, Integração com HEMS (Dissertação de Mestrado) e Links Oficiais (App e GitHub).
