# GUIA TEORICO E EXPLICATIVO DOS ITENS 5 E 6 (CMU 15-884)
**Disciplina:** PGENE585 - Transição Energética Sustentável e Mercados de Energia  
**Objetivo:** Explicar a teoria, a matemática e o que cada linha de código em Python fará na prática.

---

## 1. Visao Geral: O Que Estamos Fazendo?

O objetivo central dos itens 5 e 6 e responder a uma pergunta basica do setor eletrico:
> *"Se a previsao do tempo diz que amanha fara X graus, quantos Megawatts (MW) a cidade vai consumir?"*

Para responder isso, transformamos dados historicos em modelos matematicos dentro do Python.

---

## 2. ITEM 5: Regressoes de Demanda vs. Temperatura

No Item 5, recebemos dois arquivos simples e limpos:
* `q5_max_temp.txt`: Temperaturas maximas diarias.
* `q5_max_demand.txt`: Demandas maximas (picos de consumo) diarias.

### 2.1. O que e a Funcao de Perda (Loss Function)?
O computador nao adivinha nada. Ele ajusta coeficientes (pesos $\theta$) para **minimizar uma funcao de erro**:

* **Perda Quadratica (L2 / Squared Loss):**
  * Equacao do Erro: $\sum (y_{real} - y_{previsto})^2$
  * **O que faz no codigo:** Eleva as diferencas ao quadrado. Pune com muita forca os erros grandes. E a base do metodo dos Minimos Quadrados Ordinarios (MQO / OLS).
* **Perda Absoluta (L1 / Absolute Loss):**
  * Equacao do Erro: $\sum |y_{real} - y_{previsto}|$
  * **O que faz no codigo:** Mede o erro em valor absoluto (sem elevar ao quadrado). E muito mais robusta contra dados anomalos (*outliers*), como dias de blecaute ou feriados fora de epoca.

---

### 2.2. Os 4 Modelos Explicados (Da Matematica ao Codigo)

O exercicio pede para implementar 4 formas diferentes de desenhar a curva de predicao:

#### Modelo 1: Regressao Linear Simples (Reta)
* **A Matematica:** $y = \theta_0 + \theta_1 x$
* **O que o codigo Python faz:** Encontra a melhor reta que corta os pontos.
* **Comando tipico em Python:** `LinearRegression()` ou via Equacao Normal direta: `theta = inv(X.T @ X) @ X.T @ y`.
* **Limitacao:** Assume que a demanda cresce em linha reta, ignorando que no calor extremo o ar-condicionado dispara de forma acelerada.

#### Modelo 2: Regressao Polinomial (Grau d = 5)
* **A Matematica:** $y = \theta_0 + \theta_1 x + \theta_2 x^2 + \theta_3 x^3 + \theta_4 x^4 + \theta_5 x^5$
* **O que o codigo Python faz:** Cria colunas extras no DataFrame contendo a temperatura elevada ao quadrado, ao cubo, ate a quinta potencia.
* **Comando tipico em Python:** `PolynomialFeatures(degree=5)`.
* **Vantagem e Risco:** Permite que a reta se dobre e capture curvas, mas se nao tiver cuidado, as pontas da curva disparam para o infinito (*overfitting* nas bordas).

#### Modelo 3: Regressao com Funcoes RBF (Radial Basis Functions)
* **A Matematica:** Espalha 5 "sinos gaussianos" uniformemente ao longo da temperatura:
  $$\phi_j(x) = \exp\left( -\frac{(x - \mu_j)^2}{2\sigma^2} \right)$$
* **O que significam os parametros:**
  * $\mu_j$: O centro de cada um dos 5 sinos (ex: em 10 C, 20 C, 30 C, etc.).
  * $\sigma = 20$ (Largura de Banda / Bandwidth): Define a "gordura" do sino. Com $\sigma = 20$, os sinos se sobrepoem suavemente.
* **O que o codigo Python faz:** Calcula a distancia da temperatura de cada dia para os 5 centros e aplica a funcao exponencial. O resultado e uma combinacao suave de respostas termicas locais.

#### Modelo 4: Regressao Ridge com Kernel Gaussiano (O Mais Avancado)
* **A Matematica:** Em vez de chutar 5 centros na mao, compara cada ponto com **todos os outros pontos da base historica** atraves de uma matriz de similaridade (Kernel):
  $$K(x, x') = \exp\left( -\frac{\|x - x'\|^2}{2\sigma^2} \right)$$
* **O freio de mao ($\lambda = 10^{-4}$):** O termo de regularizacao penaliza pesos muito grandes, impedindo que a curva fique tremida ou decorando ruido.
* **Comando tipico em Python:** `KernelRidge(kernel='rbf', alpha=1e-4, gamma=1/(2*20**2))`.
* **Por que e o melhor:** Se molda com precisao a realidade fisica do consumo sem explodir nas pontas.

---

## 3. ITEM 6: Tratamento de Dados Brutos e Engenharia de Features

No mundo real, os dados nunca vem limpos como no item 5. O Item 6 entrega dados "crus" baixados da internet:
* `q6_demand.txt`: Demanda eletrica da regiao de Pittsburgh (Duquesne Light) registrada com carimbo de tempo UTC.
* `q6_weather.txt`: Telemetria meteorologica bruta do aeroporto (temperatura, ponto de orvalho, umidade, pressao, vento e condicao).

Aqui o codigo executa 4 tarefas essenciais de engenharia de dados:

### Etapa A: Limpeza de Dados (Data Cleaning)
* **O problema:** Sensores meteorologicos sofrem panes ou perda de sinal. Quando falham, gravam o valor padrao **`-9999`**. Alem disso, ha carimbos de tempo repetidos.
* **O que o Python faz:**
  * Filtra e remove linhas onde o valor e `-9999`: `df = df[df['temp'] != -9999]`
  * Remove duplicatas de horario mantendo a primeira leitura: `df.drop_duplicates(subset=['timestamp'])`

### Etapa B: Sincronizacao Temporal (Interpolacao)
* **O problema:** O relogio da estacao meteorologica mede em minutos aleatorios (ex: 10h14, 10h52). O relogio da concessionaria de energia mede em horas cheias (ex: 10h00, 11h00). Os horarios nao batem!
* **O que o Python faz:** Usa interpolacao linear (`scipy.interpolate.interp1d` ou `pandas.merge_asof`) para estimar com precisao matematica qual era a temperatura exata na hora cheia medida pela eletrica.

### Etapa C: Agregacao Diaria
* Converte o horario universal (UTC) para o fuso local da cidade (Eastern Time = UTC - 5 horas).
* Agrupa os dados por dia civil e extrai a **temperatura maxima** e a **demanda de pico** de cada dia.

### Etapa D: Engenharia de Features (A Pergunta Cientifica)
* O professor quer provar se **clima e so temperatura**.
* O codigo extrai novas variaveis:
  * Ponto de orvalho medio (*dewpoint*) e Umidade relativa (o ar umido dificulta o resfriamento e sobrecarrega o ar-condicionado);
  * Velocidade media do vento (troca de calor nas paredes dos edificios);
  * Pressao barometrica e condicao predominante (chuva, nublado, ceu limpo).
* **O Resultado:** O Python roda dois modelos:
  1. Modelo A: usando apenas a temperatura maxima.
  2. Modelo B: usando todas as variaveis combinadas.
* Comprovamos numericamente que o **Erro Quadratico Medio (MSE) do Modelo B e significativamente menor**, provando o valor da engenharia de features no setor eletrico.

---

## 4. Dicionario Rapido: Traducao do Conceito para a Linha de Codigo

| Conceito Teorico | O que a linha de codigo Python faz |
| :--- | :--- |
| **Normal Equations (Equacoes Normais)** | Resolve `theta = np.linalg.solve(X.T @ X, X.T @ y)` para achar os pesos sem precisar de loop. |
| **Bandwidth $\sigma = 20$** | Define a largura do sino gaussiano na formula `np.exp(-dist / (2 * 20**2))`. |
| **Regularizacao $\lambda = 10^{-4}$** | Adiciona uma pequena taxa na diagonal da matriz `(X.T @ X + lambda * I)` para estabilizar a inversao. |
| **Limpeza de -9999** | `df = df[df['valor'] > -9000]` para eliminar dados de sensor quebrado. |
| **Interpolacao 1D** | `f_interp = interp1d(tempo_clima, temp_clima); temp_alinhada = f_interp(tempo_demanda)` |
| **Metricas de Erro (MSE / RMSE)** | `mean_squared_error(y_real, y_pred)` para medir numericamente quem errou menos. |

---

## 5. Como usar esse conhecimento na Apresentacao de Sabado (10 minutos)

Quando voce estiver apresentando os slides:
1. **Ao mostrar o Item 5:** Destaque que voce nao apenas plotou linhas, mas comparou abordagens lineares e nao-lineares, explicando que o Kernel Gaussiano e regularizado para nao explodir nas bordas e que a perda L1 protege contra anomalias.
2. **Ao mostrar o Item 6:** Explique que o trabalho incluiu um pipeline profissional de engenharia de dados (remocao de `-9999` e interpolacao de timestamps) e que provou numericamente que umidade e vento reduzem o erro de previsao de carga.
