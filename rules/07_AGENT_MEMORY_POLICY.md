# 🧠 07. Política de Memória do Agente (Living Memory & Rolling Buffer)

Para garantir continuidade, agilidade e contexto persistente entre sessões de desenvolvimento com diferentes modelos de IA, o projeto adota o padrão de mercado **Living Context Memory Buffer** através do arquivo [`MEMORY.md`](../MEMORY.md) localizado na raiz do repositório.

---

## 🔥 PRINCÍPIO FUNDAMENTAL: O ARQUIVO DE MEMÓRIA É VIVO

> **ATENÇÃO PARA TODA IA, AGENTE OU ASSISTENTE:**  
> O arquivo `MEMORY.md` **NÃO É UM DOCUMENTO ESTÁTICO OU DE REGISTRO ÚNICO**.  
> Ele é um **organismo vivo** que acompanha em tempo real o ciclo de desenvolvimento do projeto.  
> Toda IA que interagir com o repositório deve ter a consciência explícita de que **a atualização do `MEMORY.md` é mandatória a cada nova tarefa realizada**. Finalizar uma sessão sem atualizar a memória viva é considerado uma quebra grave de governança.

---

## 🚨 REGRAS MANDATÓRIAS DE USO DO `MEMORY.md`

### 1. Leitura Obrigatória no Início de Cada Sessão (Awareness Instantâneo)
* Toda IA que iniciar um atendimento **DEVE** ler o arquivo `MEMORY.md` imediatamente após ler `AGENTS.md`.
* O objetivo é carregar o estado operacional do projeto em segundos:
  - Onde o projeto parou;
  - Quais foram as últimas tarefas realizadas;
  - Decisões técnicas e estado do branch e testes;
  - Sem precisar varrer milhares de linhas de código ou histórico extenso de commits.

### 2. Atualização Viva e Obrigatória a Cada Nova Tarefa
* Ao concluir **qualquer** nova tarefa, refatoração, implementação ou correção, a IA **DEVE** atualizar o `MEMORY.md` antes de dar o trabalho por encerrado:
  * **Registrar a Nova Atividade:** Inserir a nova atividade no topo da seção de histórico recente com:
    - Identificador e título claro da atividade;
    - Data da intervenção;
    - O que foi implementado, refatorado ou corrigido;
    - Lista de arquivos-chave modificados/criados.
  * **Atualizar a Seção "Onde Parou & Próximos Passos":** Indicar com precisão o estado em que o projeto ficou e qual a recomendação para o próximo agente ou humano que assumir.
  * **Atualizar o Estado do Sistema:** Se a tarefa alterou testes, dependências, rotas ou métricas, atualizar o sumário de estado na Seção 1.

### 3. Janela Deslizante (Rolling Buffer) & Zero Trash
* **Limite Rigoroso de Tamanho:** O arquivo `MEMORY.md` **nunca deve ultrapassar ~100 a 120 linhas** (~1.000 tokens).
* **Padrão de Janela Deslizante:** Manter **apenas as últimas 3 a 5 atividades mais recentes**.
* **Rotação Automática:** Ao adicionar uma nova atividade que exceda o limite de 5 itens, a atividade mais antiga deve ser descartada ou compactada para uma única linha.
* É **terminantemente proibido** transformar o `MEMORY.md` em um log acumulativo infinito de centenas de linhas. A memória deve ser cirúrgica, densa e leve.
