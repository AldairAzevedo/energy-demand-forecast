# 🤖 AI Agent Directive & Rules Guide (LEIA PRIMEIRO)

> **ATENÇÃO PARA QUALQUER MODELO DE IA, AGENTE AUTÔNOMO OU ASSISTENTE:**  
> Este documento é o ponto de entrada mandatório deste repositório. Antes de planejar, codificar, refatorar ou executar comandos, você **DEVE** ler e aderir estritamente a todas as diretrizes aqui descritas e detalhadas no diretório [`rules/`](rules/README.md).

---

## 🚨 REGRA CRÍTICA & INVIOLÁVEL: PROIBIÇÃO DE `git push`

* **A IA NUNCA DEVE EXECUTAR `git push`**: Você tem permissão **exclusiva** para criar commits locais (`git commit`) na máquina de desenvolvimento.
* O envio para o repositório remoto (`origin` / GitHub) é uma **decisão e prerrogativa exclusiva e soberana do usuário humano (`AldairAzevedo`)**.
* Mesmo que o usuário diga "suba no git" ou "atualize o deploy", a IA deve apenas realizar o `git commit` local e instruir o usuário de que o commit foi criado e que o comando `git push` está à disposição dele.

---

## 📚 LEITURA OBRIGATÓRIA NO DIRETÓRIO `rules/`

Antes de executar qualquer tarefa, consulte os manuais específicos em `rules/`:

1. [**`rules/01_ARCHITECTURE_SOLID.md`**](rules/01_ARCHITECTURE_SOLID.md):
   * **Arquitetura Monolítica em Camadas:** Domínio puro em `src/core/`, orquestração em `src/pipelines/`, interface em `src/ui/` e I/O atômico em `src/utils/`. Sem dependências circulares.
   * **POO com SOLID:** Aplicação prática dos 5 princípios (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion).
2. [**`rules/02_CLEAN_CODE_ZERO_TRASH.md`**](rules/02_CLEAN_CODE_ZERO_TRASH.md):
   * **Clean Code:** Nomes intencionais, métodos curtos (< 30 linhas), auto-documentação e sem comentários redundantes.
   * **Zero Trash:** Proibição de arquivos temporários (`*.tmp`), pastas vazias, trechos de código comentados ou código morto.
   * **Escopo Estrito:** Foco 100% no desafio **Zenodo Smart Building (2025)**. Todo e qualquer artefato de desafios passados (ex: CMU) é considerado lixo e não pode ser reintroduzido.
3. [**`rules/03_SONARQUBE_AND_QUALITY.md`**](rules/03_SONARQUBE_AND_QUALITY.md):
   * **Conformidade SonarQube:** Complexidade ciclomática estritamente $\le 15$ (`C901`), tipagem estática completa com `typing`, tratamento defensivo de exceções (proibido `except Exception: pass`).
   * **Formatação:** PEP 8, Black, isort e limite de 100 caracteres por linha. `flake8` com **0 erros e 0 warnings**.
4. [**`rules/04_TESTING_STANDARDS.md`**](rules/04_TESTING_STANDARDS.md):
   * **Testes Automatizados:** Testes unitários para cálculos matemáticos (`test_metrics.py`, `test_zenodo_pipeline.py`) e de integração para orquestração (`test_integration_cycles.py`).
   * **Aprovação de 100%:** Nenhuma alteração é aceita sem a suíte do `pytest` passando integralmente. Uso obrigatório de `tmp_path` para testes de arquivo.
5. [**`rules/05_GIT_AND_COMMIT_POLICY.md`**](rules/05_GIT_AND_COMMIT_POLICY.md):
   * **Conventional Commits:** Mensagens claras em português estruturadas como `<tipo>(<escopo>): <descrição>` (`feat`, `fix`, `refactor`, `test`, `docs`, `chore`).

---

## 🎯 Escopo Exclusivo do Projeto: Zenodo 2025 Smart Building

* **Problema:** *2025 Competition on Electric Energy Consumption Forecast Adopting Multi-criteria Performance Metrics*.
* **Dados:** Telemetria de 1 ano a cada 5 minutos (105.120 amostras) de edifício inteligente, agregadas em 8.760 horas, com potência elétrica ativa (W), geração solar fotovoltaica em telhado (W) e temperatura ambiente (°C).
* **Demanda Líquida:** $P_{\text{líquida}} = P_{\text{consumo}} - P_{\text{solar}}$ (modelagem da **Curva do Pato** e estratégias BESS).
* **Modelos:** Ridge Linear (lags autoregressivos) vs. Random Forest Regressor ($R^2 = 0.900$).
* **Métricas Multi-critério:** RMSE, MAE, $R^2$ Score e Tempo de Processamento (ms).

---

## 🛠️ Comandos de Verificação & Operação

```bash
# 1. Executar bateria de testes automatizados
python -m pytest tests/ -v

# 2. Executar linter estático e qualidade de código
python -m flake8 src/ tests/ presentation/ streamlit_app.py

# 3. Executar o pipeline Zenodo via CLI
python -m src.pipelines.cycle_manager --run-all

# 4. Executar aplicação Streamlit localmente
python -m streamlit run streamlit_app.py
```
