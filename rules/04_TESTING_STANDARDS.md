# 🧪 04. Padrões de Testes Unitários e de Integração

A estabilidade e integridade matemática do sistema dependem de uma suíte de testes automatizados com execução rápida e alta confiabilidade.

---

## 1. Princípios de Testes no Projeto

1. **Test-First / Test-Accompanied:** Nenhuma nova regra de cálculo, modelo de IA, processador de dados ou endpoint de pipeline pode ser commitado sem o respectivo teste automatizado.
2. **Determinismo:** Os testes não podem depender de conectividade com a internet, serviços externos em nuvem ou estados não reprodutíveis.
3. **Isolamento de I/O:** Testes que criam ou leem arquivos devem obrigatoriamente utilizar a fixture `tmp_path` do pytest, evitando poluir o disco com artefatos de teste.

---

## 2. Tipos de Testes Obrigatórios

### 2.1. Testes Unitários (`tests/test_*.py`)
* Testam funções e métodos de forma atômica e isolada.
* **Exemplos Obrigatórios:**
  * `test_metrics.py`: Validação de cálculos exatos de MSE, RMSE, MAE, R² com casos de borda (divisão por zero, predição perfeita, variância nula).
  * `test_zenodo_pipeline.py`: Validação de inicialização do pipeline, formatos de saída e integridade das estruturas de dados.

### 2.2. Testes de Integração (`tests/test_integration_*.py`)
* Validam o fluxo completo e a colaboração entre múltiplos componentes (ingestão $\to$ modelo $\to$ métrica $\to$ persistência JSON).
* **Exemplos Obrigatórios:**
  * `test_integration_cycles.py`: Garante que `CycleManager.run_all()` e `check_integrity()` operam sem falhas e geram os arquivos JSON esperados com estrutura válida.

---

## 3. Critérios de Aceitação de Testes

* **Taxa de Aprovação:** **100% dos testes devem passar**. Falhas em testes são impeditivas para qualquer commit.
* **Comando de Verificação:**
  ```bash
  python -m pytest tests/ -v
  ```
* Se uma alteração quebrar um teste existente, a IA deve investigar a causa raiz: se a regra de negócio mudou propositalmente, o teste deve ser atualizado; caso contrário, a regressão no código deve ser corrigida imediatamente.
