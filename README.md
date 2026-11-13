# Sistema Monolítico Full Stack de Previsão de Consumo Elétrico (Zenodo 2025)

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
├── .githooks/                # Hooks pré-commit e pré-push para garantia de qualidade
├── data/
│   ├── baseline/zenodo/      # Cópia protegida do dataset original oficial
│   ├── zenodo/               # Datasets da Competição Zenodo 2025
│   └── cycles/               # Armazenamento JSON do pipeline Zenodo
├── docs/                     # Documentação e enunciado (zenodo.pdf)
├── presentation/             # Apresentação em slides (PPTX e PDF)
├── results/                  # Figuras renderizadas em 300 DPI para publicação
├── rules/                    # Diretrizes obrigatórias de governança para IAs (SOLID, Clean Code, Git)
├── scripts/                  # Scripts utilitários de formatação e verificação de qualidade
├── src/
│   ├── core/                 # Domínio e matemática: métricas multi-critério
│   ├── pipelines/            # Orquestrador ZenodoPipeline e CLI CycleManager
│   ├── ui/                   # Aplicação web monolítica, componentes e gráficos Plotly
│   └── utils/                # I/O atômico de arquivos JSON com codificador NumPy
├── tests/                    # Suíte completa de testes unitários e de integração
├── streamlit_app.py          # Ponto de entrada para Streamlit Community Cloud
├── .flake8                   # Configuração do linter estático e complexidade Sonar
├── pyproject.toml            # Configuração unificada do Black, isort e pytest
├── requirements.txt          # Dependências do projeto
├── MEMORY.md                 # Memória persistente de atividades recentes (rolling buffer)
└── README.md                 # Este guia de operação
```

---

## 2. Pipeline Zenodo Smart Building

Todos os resultados de predição são persistidos em `data/cycles/zenodo_forecast_results.json` e consumidos diretamente pela interface web:

- **Ingestão e Limpeza:** Leituras de consumo elétrico (`power (W)`), tensão (`voltage (V)`), corrente (`amperage (A)`), geração fotovoltaica e temperatura em intervalos de 5 minutos, agregados em base horária.
- **Engenharia de Atributos Causais:** Codificação cíclica da hora (`sin/cos`), temperatura, geração FV, lags autoregressivos de consumo ($t-1, t-2, t-3, t-24, t-48, t-168$), estatísticas móveis (6h e 24h) e lags ($t-1$) de tensão e corrente.
- **Modelos Avaliados:** Ridge Linear (baseline), Random Forest (100 árvores) e HistGradientBoosting, avaliados com RMSE, MAE, $R^2$, tempo de treino e tempo de inferência.

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
1. **Previsão de Consumo (Zenodo 2025):** Acompanhe a previsão horária do edifício inteligente (Ridge vs. Random Forest vs. HistGradientBoosting) e a tabela multi-critério (RMSE, MAE, R², treino e inferência).
2. **Auditoria do Pipeline (JSON):** Faça upload de novas séries temporais `.xlsx` para retreinar os modelos e inspecione o arquivo JSON completo.

### 4.2. Executar via Terminal (CLI)

```bash
# Executa o pipeline Zenodo
python -m src.pipelines.cycle_manager --run-all

# Verifica a integridade do JSON gerado
python -m src.pipelines.cycle_manager --check
```

---

## 5. Qualidade de Código, Linting, Formatação e Testes (SonarQube Ready)

O projeto adota uma esteira completa de engenharia de software para garantir conformidade estrita com o **SonarQube**, **PEP 8** e cobertura de **testes automatizados**.

### 5.1. Ferramentas Utilizadas

| Ferramenta | Propósito Técnico |
| :--- | :--- |
| **`black`** | Formatador determinístico de código (estilo Prettier para Python), configurado para 100 caracteres. |
| **`isort`** | Organizador e ordenador semântico de imports em blocos (built-in, terceiros e locais). |
| **`flake8`** | Linter estático que verifica aderência à PEP 8 e penaliza complexidade ciclomática elevada (`max-complexity = 12`). |
| **`pytest`** | Framework de testes unitários (cálculo de métricas) e testes de integração (execução do pipeline). |

---

### 5.2. Comandos Disponíveis para o Desenvolvedor

#### 🎨 1. Formatar Código Automaticamente
Aplica o `isort` e o `black` em todos os módulos Python do projeto em um único comando:
```bash
python scripts/format_code.py
```

#### 🔍 2. Verificar Quality Gate Completo (Sem Modificar Arquivos)
Executa a validação de imports, formatação, análise estática e todos os testes:
```bash
python scripts/verify_quality.py
```

#### 🧪 3. Executar Apenas os Testes Automatizados
```bash
python -m pytest tests/ -v
```

#### 📋 4. Executar Apenas o Linter Estático (Flake8)
```bash
python -m flake8 src/ tests/ presentation/ scripts/ streamlit_app.py
```

---

### 5.3. Automação de Qualidade no Git (Pre-Commit & Pre-Push Hooks)

Para garantir que nenhum código com erro de sintaxe, complexidade excessiva ou falha em testes seja gravado ou enviado ao GitHub, configuramos dois **Git Hooks automatizados**:

```mermaid
flowchart TD
    subgraph CommitFlow ["Fluxo Local: git commit"]
        COMMIT["git commit"] --> HOOK_C[".githooks/pre-commit"]
        HOOK_C --> CHECK_C["python scripts/verify_quality.py"]
        CHECK_C -->|Falha| BLOCK_C["❌ Commit Cancelado"]
        CHECK_C -->|100% OK| ALLOW_C["✅ Commit Realizado"]
    end

    subgraph PushFlow ["Fluxo Remoto: git push"]
        PUSH["git push"] --> HOOK_P[".githooks/pre-push"]
        HOOK_P --> CHECK_P["python scripts/verify_quality.py"]
        CHECK_P -->|Falha| BLOCK_P["❌ Push Cancelado"]
        CHECK_P -->|100% OK| ALLOW_P["🚀 Envio ao GitHub Autorizado"]
    end
```

* **Pre-Commit Hook (`.githooks/pre-commit`):** Executa automaticamente a cada `git commit`, validando `isort`, `black`, `flake8` e `pytest`. Se houver falha, o commit é abortado imediatamente.
* **Pre-Push Hook (`.githooks/pre-push`):** Executa automaticamente a cada `git push`, servindo como segunda barreira de proteção antes do código atingir o repositório remoto no GitHub.
* **Ativação dos Hooks:**
  ```bash
  git config core.hooksPath .githooks
  ```

---

## 6. Governança e Regras para IAs

As diretrizes detalhadas de arquitetura, POO com SOLID, Zero Trash, testes e controle de versão estão formalizadas no diretório [`rules/`](rules/README.md) e no ponto de entrada [`AGENTS.md`](AGENTS.md):
- [`rules/01_ARCHITECTURE_SOLID.md`](rules/01_ARCHITECTURE_SOLID.md): Arquitetura monolítica em camadas e SOLID.
- [`rules/02_CLEAN_CODE_ZERO_TRASH.md`](rules/02_CLEAN_CODE_ZERO_TRASH.md): Clean Code, legibilidade e política de zero resíduos.
- [`rules/03_SONARQUBE_AND_QUALITY.md`](rules/03_SONARQUBE_AND_QUALITY.md): Conformidade SonarQube e complexidade ciclomática.
- [`rules/04_TESTING_STANDARDS.md`](rules/04_TESTING_STANDARDS.md): Testes unitários e de integração obrigatórios.
- [`rules/05_GIT_AND_COMMIT_POLICY.md`](rules/05_GIT_AND_COMMIT_POLICY.md): Conventional Commits e **proibição total de push pela IA**.
- [`rules/06_DOCUMENTATION_EVOLUTION.md`](rules/06_DOCUMENTATION_EVOLUTION.md): **Evolução mandatória do README.md** a cada mudança.
- [`rules/07_AGENT_MEMORY_POLICY.md`](rules/07_AGENT_MEMORY_POLICY.md): **Memória Viva (Living Memory & Rolling Buffer)** via [`MEMORY.md`](MEMORY.md) com atualização mandatória a cada tarefa.

---

## 7. Licença e Autor

- **Licença:** [MIT](LICENSE) © 2026 Aldair da Silva Azevedo.
- **Autor:** **Aldair da Silva Azevedo** ([LinkedIn](https://www.linkedin.com/in/aldair-azevedo/) | [GitHub](https://github.com/AldairAzevedo)).
