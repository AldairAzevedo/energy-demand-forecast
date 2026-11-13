# 🛑 05. Política de Git, Commits e Regras Invioláveis de Controle de Versão

Este documento estabelece as regras estritas de controle de versão para qualquer modelo de Inteligência Artificial ou ferramenta de desenvolvimento operando neste repositório.

---

## 🚨 REGRAS INVIOLÁVEIS DE GIT PARA A IA

> [!CAUTION]
> **1. PROIBIÇÃO TOTAL DE `git push` PELA IA:**  
> A IA (qualquer modelo ou agente) está **TERMINANTEMENTE PROIBIDA** de executar `git push` para qualquer repositório remoto (`origin`, `upstream`, etc.). Apenas o usuário humano (`AldairAzevedo`) tem permissão de realizar o push.

> [!CAUTION]
> **2. PROIBIÇÃO DE `git commit` SEM ORDEM EXPLÍCITA:**  
> A IA está **PROIBIDA DE FAZER COMMITS POR INICIATIVA PRÓPRIA**.  
> A IA só pode executar `git commit` quando o usuário pedir de forma **direta e explícita** (ex: *"faça o commit"*, *"pode comitar as alterações"*). Caso o usuário não tenha pedido expressamente o commit, as alterações devem permanecer apenas no ambiente de trabalho (*working tree*), prontas para inspeção.

---

## 📋 Resumo das Permissões de Git da IA

| Operação | IA pode executar? | Condição |
| :--- | :---: | :--- |
| `git status` / `git diff` / `git log` | ✅ **SIM** | Livremente para inspeção do estado do repositório. |
| `git add` | ⚠️ **CONDICIONADO** | Apenas quando preparando o commit expressamente solicitado pelo usuário. |
| `git commit` | 🛑 **RESTRITO** | **SOMENTE quando o usuário solicitar explicitamente**. Nunca por iniciativa própria. |
| `git push` | ❌ **PROIBIDO** | **TERMINANTEMENTE PROIBIDO EM QUALQUER HIPÓTESE**. Somente o usuário faz push. |

---

## 📝 Padrões de Mensagens de Commit (Quando Solicitado pelo Usuário)

Quando o usuário autorizar/solicitar a criação do commit, a mensagem deve ser clara, contextualizada e seguir o padrão **Conventional Commits**:

### Estrutura Obrigatória:
```text
<tipo>(<escopo>): <descrição clara e concisa em português>

[opcional: corpo explicando o motivo da alteração e impacto técnico]
```

### Tipos Permitidos:
* **`feat`**: Implementação de nova funcionalidade ou capacidade analítica.  
  *Exemplo:* `feat(zenodo): implementa extrator de atributos temporais autoregressivos`
* **`fix`**: Correção de bug, erro de cálculo ou falha de renderização.  
  *Exemplo:* `fix(ui): corrige formatacao de unidades na tabela de benchmarking`
* **`refactor`**: Refatoração de código sem alterar o comportamento externo (Clean Code).  
  *Exemplo:* `refactor(core): modulariza calculadora de metricas multi-criterio`
* **`test`**: Adição ou aprimoramento de testes unitários e de integração.  
  *Exemplo:* `test(pipeline): adiciona teste parametrizado para validacao do zenodo`
* **`docs`**: Atualização de documentação, README, slides ou guias.  
  *Exemplo:* `docs(rules): documenta diretrizes de governanca e arquitetura do projeto`
* **`chore`**: Tarefas de manutenção, atualização de dependências ou limpeza de arquivos.  
  *Exemplo:* `chore(git): atualiza gitignore para ignorar novos caches de teste`

### Requisitos da Mensagem:
* Seja específico: nunca utilize mensagens genéricas como `"ajustes"`, `"update"`, `"fix"` ou `"wip"`.
* Explique **o que** foi feito e, quando relevante, **por que** foi necessário.
