# 🛑 05. Política de Git, Commits e Regra Inviolável de Push

Este documento estabelece as regras estritas de controle de versão para qualquer modelo de Inteligência Artificial ou ferramenta de desenvolvimento operando neste repositório.

---

## 🚨 REGRA INVIOLÁVEL: PROIBIÇÃO ABSOLUTA DE `git push` PELA IA

> [!CAUTION]
> **A IA (QUALQUER MODELO OU AGENTE) ESTÁ TERMINANTEMENTE PROIBIDA DE EXECUTAR `git push` PARA QUALQUER REMOTO (`origin`, `upstream`, ETC.).**

1. **Permissão Restrita a Commits Locais:**  
   A IA tem autorização **exclusivamente** para preparar o *stage* (`git add`) e criar commits locais (`git commit`) na máquina de desenvolvimento.
2. **Soberania do Usuário:**  
   O envio das alterações para o GitHub (`git push`) é uma decisão **exclusiva do usuário humano (`AldairAzevedo`)**. Ele é quem revisa, julga o momento oportuno e dispara o push.
3. **Comportamento em Falhas ou Dúvidas:**  
   Mesmo que o usuário diga "salve no git" ou "suba as alterações", a IA deve apenas realizar o `git commit` local e informar ao usuário que o commit foi criado com sucesso e que o comando `git push` está à disposição para quando ele desejar executar.

---

## 📝 Padrões de Mensagens de Commit (Conventional Commits)

Todas as mensagens de commit devem ser escritas de forma clara, contextualizada e seguindo o padrão **Conventional Commits**:

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
