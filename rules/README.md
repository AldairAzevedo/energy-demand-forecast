# 📜 Diretrizes e Regras de Governança do Projeto (AI Rules)

Este diretório contém o conjunto oficial de regras, convenções arquiteturais, diretrizes de qualidade e políticas de versionamento que **devem ser seguidas rigorosamente por qualquer modelo de inteligência artificial (IA)**, agente autônomo ou desenvolvedor que atue neste repositório.

---

## 🎯 Escopo Exclusivo do Projeto
* **Desafio Único:** [Zenodo 2025 Smart Building](https://zenodo.org/) (*2025 Competition on Electric Energy Consumption Forecast Adopting Multi-criteria Performance Metrics*).
* **Foco Técnico:** Previsão horária de consumo de energia elétrica, modelagem da geração solar fotovoltaica, cálculo da **Demanda Líquida (Curva do Pato)** e avaliação multi-critério de algoritmos de Machine Learning (Ridge Linear e Random Forest).
* **Regra de Escopo:** Qualquer código, dado, comentário ou documento referente a problemas anteriores (como CMU) é expressamente proibido e considerado **trash**.

---

## 📚 Índice de Regras

| Arquivo | Título | Descrição |
| :--- | :--- | :--- |
| [**01_ARCHITECTURE_SOLID.md**](01_ARCHITECTURE_SOLID.md) | **Arquitetura Monolítica & SOLID** | Princípios de POO, design modular em camadas e aplicação estrita do SOLID em Python. |
| [**02_CLEAN_CODE_ZERO_TRASH.md**](02_CLEAN_CODE_ZERO_TRASH.md) | **Clean Code & Zero Trash** | Legibilidade, auto-documentação, eliminação de código morto e política de zero resíduos. |
| [**03_SONARQUBE_AND_QUALITY.md**](03_SONARQUBE_AND_QUALITY.md) | **SonarQube Compliance** | Diretrizes para garantir nota máxima no SonarQube (sem smells, bugs ou vulnerabilidades). |
| [**04_TESTING_STANDARDS.md**](04_TESTING_STANDARDS.md) | **Padrões de Testes (Pytest)** | Requisitos obrigatórios de testes unitários e de integração antes de qualquer alteração. |
| [**05_GIT_AND_COMMIT_POLICY.md**](05_GIT_AND_COMMIT_POLICY.md) | **Política de Git & Commit** | **PROIBIÇÃO TOTAL de `git push`** e **commits apenas quando expressamente solicitados**. |

---

## ⚡ Regras de Ouro para Modelos de IA (Resumo Executivo)

1. **PROIBIDO FAZER `git push`:** A IA está **terminantemente proibida** de executar `git push`. Apenas o usuário (`AldairAzevedo`) pode enviar alterações ao remoto.
2. **COMMITS APENAS QUANDO SOLICITADOS:** A IA está **proibida de fazer commits por conta própria**. Ela só executa `git commit` quando o usuário pedir expressamente.
3. **SONARQUBE ZERO WARNINGS:** Nenhum código gerado pela IA pode conter complexidade ciclomática elevada (> 15), variáveis sem uso, exceções genéricas vazias ou tipagem ausente.
4. **100% DOS TESTES PASSANDO:** Antes de concluir qualquer tarefa ou gerar commits, a IA deve executar `pytest` e `flake8`, garantindo 0 erros e 0 avisos.
5. **ZERO TRASH:** Nunca deixar arquivos `.tmp`, pastas vazias, cópias de segurança desnecessárias ou código comentado no repositório.
