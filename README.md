# Sistema Monolítico Full Stack de Previsão de Carga e Demanda Líquida (Zenodo Smart Building)

[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Security: Policy](https://img.shields.io/badge/Security-Policy-brightgreen.svg)](SECURITY.md)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&square)](https://pycqa.github.io/isort/)
[![Linter: Flake8](https://img.shields.io/badge/linter-flake8-green.svg)](https://flake8.pycqa.org/)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-blue.svg)](https://docs.pytest.org/)

Aplicação acadêmica monolítica desenvolvida para a disciplina **PGENE585 – Transição Energética Sustentável e Mercados de Energia**, com foco exclusivo no desafio **Zenodo Smart Building (2025)**.

---

## 1. Visão Geral da Arquitetura

O sistema implementa uma arquitetura **monolítica moderna 100% em Python**, combinando Programação Orientada a Objetos (**POO**), princípios **SOLID**, design limpo (**Clean Code**) e uma interface reativa em **Streamlit + Plotly**.

```
energy-demand-forecast/
├── data/
│   ├── baseline/zenodo/      # Cópia protegida do dataset original oficial
│   ├── zenodo/               # Datasets da Competição Zenodo 2025
│   └── cycles/               # Armazenamento JSON do pipeline Zenodo
├── docs/                     # Documentação e enunciado (zenodo.pdf)
├── results/                  # Figuras renderizadas em 300 DPI para publicação
├── presentation/             # Apresentação em slides
├── rules/                    # Diretrizes obrigatórias de governança para IAs (SOLID, Clean Code, Git)
├── src/
│   ├── core/                 # Domínio e matemática: perdas, modelos e métricas
│   ├── pipelines/            # Orquestrador ZenodoPipeline e CLI CycleManager
│   ├── ui/                   # Aplicação web monolítica, componentes e gráficos Plotly
│   └── utils/                # I/O atômico de arquivos JSON com codificador NumPy
├── tests/                    # Suíte completa de testes unitários e de integração
├── streamlit_app.py          # Ponto de entrada para Streamlit Community Cloud
├── .flake8                   # Configuração do linter estático
├── pyproject.toml            # Configuração unificada do Black, isort e pytest
├── requirements.txt          # Dependências do projeto
└── README.md                 # Este guia de operação
```

---

## 2. Pipeline Zenodo Smart Building

Todos os resultados de predição e análise solar são persistidos em `data/cycles/cycle_07_zenodo_smart_building.json` e consumidos diretamente pela interface web:

- **Ingestão e Limpeza:** Leituras de consumo elétrico, geração solar fotovoltaica e temperatura em intervalos de 5 minutos, agregados em base horária.
- **Engenharia de Atributos:** Criação de lags temporais ($t-1$ e $t-24$) e cálculo de **Demanda Líquida** ($\text{Consumo} - \text{Geração Solar FV}$).
- **Modelos Avaliados:** Regressão Ridge Linear vs. Random Forest Regressor (50 árvores), avaliados com RMSE, MAE, $R^2$ Score e tempo de execução.

---

## 3. Instalação e Configuração

```bash
pip install -r requirements.txt
```

---

## 4. Como Executar a Aplicação

### 4.1. Dashboard Web Interativo (Streamlit)

```bash
python -m streamlit run streamlit_app.py
```

A interface carregará com 2 módulos de navegação:
1. **Smart Building & Energia Solar (Zenodo):** Acompanhe a previsão horária do edifício inteligente (Ridge vs. Random Forest), indicadores de energia solar e a Curva do Pato.
2. **Auditoria do Pipeline (JSON):** Faça upload de novas séries temporais `.xlsx` para retreinar os modelos e inspecione o arquivo JSON completo.

### 4.2. Executar via Terminal (CLI)

```bash
# Executa o pipeline Zenodo
python -m src.pipelines.cycle_manager --run-all

# Verifica a integridade do JSON gerado
python -m src.pipelines.cycle_manager --check
```

---

## 5. Testes Automatizados e Qualidade de Código

```bash
python -m pytest tests/ -v
python -m flake8 src/ tests/ streamlit_app.py
```

---

## 6. Licença e Autor

- **Licença:** [MIT](LICENSE) © 2026 Aldair da Silva Azevedo.
- **Autor:** **Aldair da Silva Azevedo** ([LinkedIn](https://www.linkedin.com/in/aldair-azevedo/) | [GitHub](https://github.com/AldairAzevedo)).
