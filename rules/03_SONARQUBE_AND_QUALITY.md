# 🔍 03. Qualidade de Código e Conformidade com SonarQube

O projeto é submetido à análise estática de código através do **SonarQube**. Portanto, qualquer IA ou desenvolvedor deve antecipar e neutralizar qualquer padrão que cause *Code Smells*, *Bugs*, *Security Hotspots* ou quebra do *Quality Gate*.

---

## 1. Regras Principais do SonarQube

### 1.1. Complexidade Ciclomática (Cognitive Complexity)
* O SonarQube penaliza funções com alta complexidade ciclomática.
* **Limite do Projeto:** A complexidade ciclomática de qualquer função ou método deve ser **$\le 15$** (regra `C901` do flake8 e regras do Sonar).
* **Solução:** Divida fluxos longos com múltiplos `if`/`elif`/`for` em métodos privados auxiliares (`_sub_metodo`).

### 1.2. Tratamento Defensivo de Exceções
* **PROIBIDO:** Capturar `Exception` de forma genérica sem tratamento ou usar `pass` silencioso:
  ```python
  # ❌ Inaceitável pelo SonarQube
  try:
      do_something()
  except Exception:
      pass
  ```
* **OBRIGATÓRIO:** Capture exceções específicas (`FileNotFoundError`, `ValueError`, `KeyError`) ou registre o erro adequadamente:
  ```python
  # ✅ Padrão SonarQube
  try:
      do_something()
  except ValueError as err:
      logger.error("Entrada inválida ao processar dados: %s", err)
      raise
  ```

### 1.3. Tipagem Estática Completa (Type Hinting)
* Todos os parâmetros e retornos de funções e métodos devem ser explicitamente tipados utilizando o módulo `typing` (ou tipos nativos do Python 3.10+):
  ```python
  def calculate_net_load(
      consumption: np.ndarray,
      solar_pv: np.ndarray,
  ) -> np.ndarray:
  ```
* Evite o uso indiscriminado de `Any`. Quando uma estrutura for flexível, utilize `Dict[str, Any]` ou `Optional[T]`.

### 1.4. Comprimento Máximo de Linhas (PEP 8 & Flake8)
* **Limite Rigoroso:** Máximo de **100 caracteres por linha**.
* Utilize quebras de linha entre parênteses para strings longas, parâmetros de funções ou expressões matemáticas.

---

## 2. Checklist Obrigatório de Conformidade Pré-Commit

Antes de considerar qualquer alteração concluída, a IA deve rodar:

1. **Linter Estático (Flake8):**
   ```bash
   python -m flake8 src/ tests/ presentation/ streamlit_app.py
   ```
   *Exigência: 0 erros e 0 alertas.*

2. **Formatação Consistente:**
   * Alinhamento estrito aos padrões do Black e isort.
   * Sem espaços em branco no final das linhas (*trailing whitespace*).
   * Linha em branco ao final de todo arquivo (*final newline*).
