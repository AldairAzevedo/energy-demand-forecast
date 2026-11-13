# 🧹 02. Padrões de Clean Code e Política de Zero Trash

## 1. Clean Code (Código Limpo e Elegante)

O código deve ser escrito para seres humanos lerem e máquinas executarem com máxima eficiência. Qualquer IA atuando neste projeto deve seguir:

### 1.1. Nomes Significativos e Intencionais
* Classes em `PascalCase` representando substantivos claros (ex: `ZenodoPipeline`, `MetricsCalculator`).
* Funções e métodos em `snake_case` representando verbos de ação explícitos (ex: `evaluate_all`, `build_zenodo_chart`).
* Variáveis expressivas: evite nomes crípticos de uma letra (como `x`, `y1`, `temp2`), exceto variáveis consagradas na matemática quando estritamente locais e documentadas.
* Constantes em `UPPER_SNAKE_CASE` (ex: `COLOR_PALETTE`).

### 1.2. Funções Pequenas e com Propósito Único
* Métodos devem ser curtos (idealmente menos de 30 a 40 linhas).
* Cada método deve realizar apenas uma tarefa e fazê-la bem.
* Evite números mágicos no código; extraia valores padrão e hiperparâmetros para constantes nomeadas ou argumentos configuráveis com valores default.

### 1.3. Auto-documentação e Docstrings
* Todo módulo, classe e método público deve possuir docstrings em conformidade com a PEP 257 (em Português claro ou Inglês técnico consistente).
* As docstrings devem explicar o **propósito** e os parâmetros de entrada/saída, sem redundância óbvia.
* Não utilize comentários para explicar código ruim; refatore o código até que ele se torne autoexplicativo.

---

## 2. Política de Zero Trash (Tolerância Zero a Resíduos)

A política de Zero Trash é mandatória para manter a base de código enxuta, confiável e profissional:

### 2.1. Código Morto e Não Utilizado
* **Proibição Absoluta:** Funções não chamadas, classes órfãs, variáveis declaradas e nunca lidas ou imports não utilizados devem ser imediatamente removidos.
* **Proibido Código Comentado:** Trechos de código comentados ("para caso precisemos no futuro") são considerados lixo. O histórico do Git é o local de preservação de código passado.

### 2.2. Arquivos Temporários e Resíduos de Execução
* A IA nunca deve deixar arquivos temporários no repositório (ex: `*.tmp`, `temp_*.py`, `teste.py`, cópias manuais de backup).
* Diretórios vazios deixados por remoções anteriores devem ser deletados imediatamente do disco.
* Caches e arquivos gerados (ex: `.pytest_cache`, `__pycache__`, `.coverage`) devem estar no `.gitignore` e nunca serem comitados.

### 2.3. Estrito Alinhamento ao Escopo Zenodo
* O projeto pertence exclusivamente ao desafio **Zenodo 2025 Smart Building**.
* Nenhum artefato, dataset, script ou documentação de desafios anteriores ou paralelos pode ser reintroduzido.
