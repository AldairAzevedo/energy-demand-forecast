# 🏛️ 01. Arquitetura Monolítica e Princípios SOLID em POO

## 1. Arquitetura Monolítica Modular

O projeto adota uma arquitetura monolítica autocontida em Python puro, evitando dependências externas desnecessárias, microsserviços ou fragmentação de repositórios.

A separação de responsabilidades é estritamente estruturada em camadas bem definidas:

```
src/
├── core/         # Camada de Domínio Puro: Funções matemáticas, métricas e interfaces abstratas.
│                 # Não depende de I/O, bancos de dados ou interfaces de usuário.
├── pipelines/    # Camada de Aplicação / Orquestração: Ingestão, higienização, treinamento de modelos
│                 # e persistência de dados estruturados.
├── ui/           # Camada de Apresentação (Streamlit + Plotly): Renderização de dashboards,
│                 # componentes visuais reativos e interação com o usuário.
└── utils/        # Camada de Infraestrutura Utilitária: I/O atômico de arquivos JSON, encoders e helpers.
```

### Regras de Acoplamento entre Camadas:
* `core` **nunca** importa de `pipelines`, `ui` ou `utils`.
* `pipelines` consome `core` e `utils`.
* `ui` consome `pipelines`, `core` e `utils`.
* Ciclos de importação circular são expressamente proibidos.

---

## 2. Princípios SOLID Aplicados ao Python

Qualquer nova funcionalidade ou refatoração desenvolvida por uma IA deve aderir aos 5 princípios SOLID:

### S – Single Responsibility Principle (Princípio da Responsabilidade Única)
* Cada classe ou módulo deve possuir apenas **uma razão para mudar**.
* *Exemplo:* A classe `MetricsCalculator` calcula exclusivamente métricas estatísticas (RMSE, MAE, R²); ela não realiza leitura de disco nem renderização de tabelas.
* Classes orquestradoras (ex: `CycleManager`) coordenam fluxos, mas delegam a execução concreta para pipelines específicos.

### O – Open/Closed Principle (Princípio do Aberto/Fechado)
* Entidades de software devem estar **abertas para extensão, mas fechadas para modificação**.
* Utilize classes abstratas (`abc.ABC`) e herança polimórfica ou injeção de estratégia para adicionar novos algoritmos preditivos sem alterar as classes existentes.

### L – Liskov Substitution Principle (Princípio da Substituição de Liskov)
* Subclasses ou implementações concretas devem poder substituir suas interfaces base sem quebrar a consistência ou comportamento esperado do sistema.
* Não altere assinaturas de métodos nem lance exceções inesperadas em classes derivadas.

### I – Interface Segregation Principle (Princípio da Segregação de Interfaces)
* Em Python, prefira interfaces pequenas, coesas e focadas a interfaces monolíticas sobrecarregadas.
* Utilize `typing.Protocol` ou classes abstratas mínimas para definir contratos claros entre componentes.

### D – Dependency Inversion Principle (Princípio da Inversão de Dependência)
* Módulos de alto nível não devem depender diretamente de módulos de baixo nível; ambos devem depender de abstrações.
* Sempre injete caminhos de diretórios, instâncias de calculadores ou callbacks de log via construtor (`__init__`), permitindo testes unitários fáceis com dados em memória (`tmp_path`).
