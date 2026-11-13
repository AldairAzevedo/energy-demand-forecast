# 📖 06. Política de Evolução Contínua da Documentação (Documentation-as-Code)

A documentação deste repositório não é um artefato estático; ela é um componente vivo e sincronizado do software (**Documentation-as-Code**).

---

## 🚨 REGRA MANDATÓRIA: EVOLUÇÃO OBRIGATÓRIA DO `README.md`

> [!IMPORTANT]
> **Toda vez que houver qualquer alteração no projeto — por menor que seja — a IA e os desenvolvedores DEVEM avaliar e executar a evolução do `README.md`.**

### Gatilhos Obrigatórios de Atualização da Documentação:
1. **Novas Features ou Módulos:** Criação de novos fluxos, novas páginas na interface web, novos componentes gráficos ou algoritmos.
2. **Novas Ferramentas e Scripts:** Adição de ferramentas de qualidade, formatadores, linters, bibliotecas ou utilitários na pasta `scripts/`.
3. **Mudanças Arquiteturais:** Alteração na estrutura de pastas, novas camadas, refatorações significativas ou exclusão de componentes obsoletos.
4. **Novos Comandos de Operação:** Qualquer novo comando de terminal, atalho de teste ou rotina de execução deve ser imediatamente documentado.
5. **Atualização de Requisitos:** Alteração de dependências em `requirements.txt` ou configurações de ambiente.

---

## 🎯 Diretrizes de Qualidade para o `README.md`

1. **Clareza para Qualquer Leitor:**  
   Qualquer pessoa que acessar o repositório (professores, avaliadores de banca, recrutadores ou outros desenvolvedores) deve ser capaz de compreender imediatamente:
   * O que é o projeto e qual o seu propósito acadêmico/científico.
   * A árvore de diretórios atualizada e o papel de cada pasta.
   * O passo a passo exato para instalar dependências e rodar a aplicação.
   * Quais comandos executar para formatar código, rodar testes e checar o Quality Gate.
   * Onde acessar a aplicação em produção online.

2. **Fidelidade Absoluta:**  
   Nunca mantenha referências a arquivos, pastas ou tecnologias que foram removidos do código (Zero Trash na documentação).

3. **Checklist Pré-Entrega da IA:**  
   Antes de sinalizar a conclusão de qualquer tarefa para o usuário, a IA deve responder:  
   * *"As alterações feitas nesta sessão requerem atualização no README.md?"*  
   * Se **SIM**, o `README.md` deve ser atualizado **no mesmo turno**.
