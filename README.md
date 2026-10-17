# Sistema Monolítico Full Stack de Previsão de Carga e Demanda Líquida

[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Security: Policy](https://img.shields.io/badge/Security-Policy-brightgreen.svg)](SECURITY.md)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&square)](https://pycqa.github.io/isort/)
[![Linter: Flake8](https://img.shields.io/badge/linter-flake8-green.svg)](https://flake8.pycqa.org/)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-blue.svg)](https://docs.pytest.org/)

Aplicação acadêmica monolítica desenvolvida para a disciplina **PGENE585 – Transição Energética Sustentável e Mercados de Energia**.

---

## 1. Visão Geral da Arquitetura

O sistema implementa uma arquitetura **monolítica moderna 100% em Python**, combinando Programação Orientada a Objetos (**POO**), princípios **SOLID**, design limpo (**Clean Code**) e uma interface reativa em **Streamlit + Plotly**.

```
energy-demand-forecast/
├── data/
│   ├── cmu/                  # Arquivos brutos de telemetria do CMU 15-884 (Q5 e Q6)
│   ├── zenodo/               # Datasets oficiais da Competição Zenodo 2025 (10 arquivos)
│   └── cycles/               # Armazenamento JSON dos 7 ciclos de dados refinados
├── docs/                     # Enunciados oficiais (cmu.pdf, zenodo.pdf) e roteiros
├── results/                  # Figuras renderizadas em 300 DPI para publicação
├── presentation/             # Apresentação em slides (slides_apresentacao.pptx e .pdf)
├── src/
│   ├── core/                 # Domínio e matemática: perdas L1/L2, 4 modelos, métricas
│   ├── pipelines/            # Orquestradores dos Ciclos 01 a 07 e CLI CycleManager
│   ├── ui/                   # Aplicação web monolítica, componentes e gráficos Plotly
│   └── utils/                # I/O atômico de arquivos JSON com codificador NumPy
├── tests/                    # Suíte completa de testes unitários e de integração
├── .flake8                   # Configuração do linter estático
├── pyproject.toml            # Configuração unificada do Black, isort e pytest
├── requirements.txt          # Dependências do projeto
└── README.md                 # Este guia de operação
```

---

## 2. A Trilha de Refinamento: Os 7 Ciclos em JSON

Todos os dados intermediários e finais são persistidos na pasta `data/cycles/` em arquivos JSON estruturados, formando uma trilha de auditoria contínua consumida diretamente pela interface web:

| Ciclo  | Arquivo JSON                                   | Descrição                                                                                                             |
| :----: | :--------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------- |
| **01** | `cycle_01_cmu_q5_raw.json`                     | 1.460 dias de $T_{\max}$ (°F) e Pico de Demanda (GW) com estatísticas descritivas.                                    |
| **02** | `cycle_02_cmu_q5_fitted_models.json`           | Predições, resíduos e métricas dos **4 modelos $\times$ 2 funções de perda ($L_2$ e $L_1$)**.                         |
| **03** | `cycle_03_cmu_q6_cleaned_weather.json`         | Limpeza de 100 valores sentinelas (`-9999`) de sensores e deduplicação de timestamps.                                 |
| **04** | `cycle_04_cmu_q6_interpolated_sync.json`       | Sincronização temporal de 35.064 horas entre clima e demanda via interpolação linear.                                 |
| **05** | `cycle_05_cmu_q6_daily_features.json`          | Agregação diária e correlações multivariadas (orvalho, umidade, pressão e vento).                                     |
| **06** | `cycle_06_cmu_q6_multivariate_comparison.json` | **Prova empírica da redução de 8.73% no MSE** pelo modelo multivariado.                                               |
| **07** | `cycle_07_zenodo_smart_building.json`          | Curva de carga de Smart Building (105.120 amostras) e **Demanda Líquida** com geração solar FV (13.53% de cobertura). |

---

## 3. Instalação e Configuração

### 3.1. Pré-requisitos

- Python 3.11 ou 3.12 instalado.

### 3.2. Instalação das Dependências

Na raiz do repositório (`energy-demand-forecast`), execute:

```bash
pip install -r requirements.txt
```

_(Em redes corporativas/acadêmicas com proxy SSL, utilize: `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt`)_

---

## 4. Como Executar a Aplicação

### 4.1. Iniciar o Dashboard Web Interativo (Streamlit)

Para iniciar o servidor local e abrir a interface monolítica no seu navegador:

```bash
# Recomendado (funciona diretamente em qualquer terminal Windows, Linux ou macOS):
python -m streamlit run src/ui/app.py

# Ou atalho direto (caso a pasta Scripts do Python esteja no seu PATH):
streamlit run src/ui/app.py
```

> [!TIP]
> **Primeira Execução do Streamlit (Prompt de Boas-Vindas):**  
> Na primeira vez em que o comando for executado, o terminal exibirá uma mensagem de boas-vindas solicitando um e-mail opcional:
> ```text
> Welcome to Streamlit!
> Email: 
> ```
> **Basta pressionar a tecla `Enter`** (deixando o campo vazio). O Streamlit salvará essa preferência, iniciará o servidor local e abrirá automaticamente uma aba no navegador em:  
> 👉 **`http://localhost:8501`**

A interface carregará com 4 módulos de navegação:

1. **Laboratório de Modelos (CMU Item 5):** Alterne entre $L_2$ (Mínimos Quadrados) e $L_1$ (LAD Robusta), selecione qualquer combinação dos 4 modelos (Linear, Polinomial $d=5$, RBF com 5 centros e Kernel Gaussiano Ridge) e inspecione o gráfico de resíduos.
2. **Engenharia de Features (CMU Item 6):** Visualize a limpeza dos sentinelas `-9999`, a correlação do clima com a carga e o gráfico comprovando a queda no MSE.
3. **Smart Building & Solar (Zenodo 2025):** Acompanhe a previsão horária do edifício inteligente e a Curva do Pato gerada pela microgeração solar no telhado.
4. **Auditoria dos 7 Ciclos (JSON):** Inspecione diretamente a estrutura dos arquivos JSON salvos no disco.

### 4.2. Executar ou Regenerar os 7 Ciclos via Terminal (CLI)

Caso queira recalcular todos os 7 ciclos em lote sem abrir o navegador:

```bash
# Executa todos os 7 ciclos sequencialmente
python -m src.pipelines.cycle_manager --run-all

# Verifica a integridade dos arquivos JSON gerados
python -m src.pipelines.cycle_manager --check
```

---

## 5. Testes Automatizados e Qualidade de Código (SonarQube)

A base de código segue rigorosamente as diretrizes do **SonarQube** (sem code smells, tipagem estática, métodos curtos e tratamento defensivo).

### 5.1. Execução dos Testes com Cobertura

```bash
python -m pytest --cov=src tests/ -v
```

### 5.2. Padronização e Formatação de Código (Estilo Prettier no Python)

```bash
# Formatação determinística de código (análogo ao Prettier)
black src tests presentation

# Ordenação automática de imports alinhada ao PEP 8
isort src tests presentation

# Verificação estática de conformidade e erros (zero warnings)
flake8 src tests presentation
```

---

## 6. Materiais da Apresentação de Sábado (17/10/2026)

Os slides da apresentação oral já foram gerados e estão disponíveis na pasta `presentation/`:

- **PowerPoint Editável:** `presentation/slides_apresentacao.pptx` (10 slides com visual moderno e figuras em alta resolução de 300 DPI inseridas).
- **PDF para Apresentação:** `presentation/slides_apresentacao.pdf`.
- **Script de Regeneração dos Slides:**
  ```bash
  python presentation/gerar_slides.py
  ```

---

## 7. Licença e Segurança

- **Licença:** Este projeto está sob a licença livre [MIT](LICENSE) © 2026 Aldair da Silva Azevedo.
- **Segurança:** Diretrizes de integridade de dados e processo de divulgação responsável detalhados em [SECURITY.md](SECURITY.md).

---

## 8. Autor

Desenvolvido por **Aldair da Silva Azevedo**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Aldair%20Azevedo-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/aldair-azevedo/)
[![GitHub](https://img.shields.io/badge/GitHub-AldairAzevedo-100000?style=flat&logo=github&logoColor=white)](https://github.com/AldairAzevedo)
[![Email](https://img.shields.io/badge/Email-aldairazevedo%40hotmail.com.br-D14836?style=flat&logo=gmail&logoColor=white)](mailto:aldairazevedo@hotmail.com.br)

Conecte-se comigo no LinkedIn: [linkedin.com/in/aldair-azevedo](https://www.linkedin.com/in/aldair-azevedo/)
