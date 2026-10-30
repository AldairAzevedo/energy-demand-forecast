"""Script para geração automatizada dos slides da apresentação (PowerPoint)."""

import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt


def build_presentation(base_dir: str) -> str:
    """Constrói a apresentação PPTX completa com 10 slides widescreen."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    NAVY = RGBColor(15, 23, 42)  # #0F172A
    BLUE = RGBColor(37, 99, 235)  # #2563EB
    DARK = RGBColor(51, 65, 85)  # #334155

    results_dir = os.path.join(base_dir, "results")
    img_q5 = os.path.join(results_dir, "cmu_q5_fits.png")
    img_q6 = os.path.join(results_dir, "cmu_q6_features.png")
    img_zenodo = os.path.join(results_dir, "zenodo_forecast.png")

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, subtitle_text):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title_text
        p1.font.size = Pt(26)
        p1.font.bold = True
        p1.font.color.rgb = NAVY

        p2 = tf.add_paragraph()
        p2.text = subtitle_text
        p2.font.size = Pt(13)
        p2.font.color.rgb = BLUE
        p2.space_before = Pt(4)

    def add_chart_with_notes(
        slide,
        img_path: str,
        notes: list,
        note_title: str,
        highlight_title: str,
        highlight_text: str,
        img_width_in: float = 7.3,
        highlight_top_in: float = 4.85,
        highlight_h_in: float = 2.05,
    ):
        """Insere imagem na esquerda, destaque inferior e painel explicativo na direita."""
        if os.path.exists(img_path):
            slide.shapes.add_picture(img_path, Inches(0.8), Inches(1.8), width=Inches(img_width_in))

        card_hl = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.8),
            Inches(highlight_top_in),
            Inches(img_width_in),
            Inches(highlight_h_in),
        )
        card_hl.fill.solid()
        card_hl.fill.fore_color.rgb = RGBColor(241, 245, 249)
        card_hl.line.color.rgb = BLUE
        card_hl.line.width = Pt(1.2)

        tf_hl = card_hl.text_frame
        tf_hl.word_wrap = True
        tf_hl.margin_top = Inches(0.10)
        tf_hl.margin_bottom = Inches(0.10)
        tf_hl.margin_left = Inches(0.15)
        tf_hl.margin_right = Inches(0.15)

        p_hl0 = tf_hl.paragraphs[0]
        p_hl0.text = highlight_title
        p_hl0.font.bold = True
        p_hl0.font.size = Pt(11.5)
        p_hl0.font.color.rgb = NAVY

        p_hl1 = tf_hl.add_paragraph()
        p_hl1.text = highlight_text
        p_hl1.font.size = Pt(10)
        p_hl1.font.color.rgb = DARK
        p_hl1.space_before = Pt(3)

        card_rt = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(8.3),
            Inches(1.8),
            Inches(4.2),
            Inches(5.1),
        )
        card_rt.fill.solid()
        card_rt.fill.fore_color.rgb = RGBColor(248, 250, 252)
        card_rt.line.color.rgb = RGBColor(203, 213, 225)
        card_rt.line.width = Pt(1)

        tf_rt = card_rt.text_frame
        tf_rt.word_wrap = True
        tf_rt.margin_top = Inches(0.12)
        tf_rt.margin_bottom = Inches(0.12)
        tf_rt.margin_left = Inches(0.15)
        tf_rt.margin_right = Inches(0.15)

        p_rt0 = tf_rt.paragraphs[0]
        p_rt0.text = note_title
        p_rt0.font.bold = True
        p_rt0.font.size = Pt(12)
        p_rt0.font.color.rgb = NAVY

        for title, desc in notes:
            p = tf_rt.add_paragraph()
            p.space_before = Pt(5)
            run1 = p.add_run()
            run1.text = title
            run1.font.bold = True
            run1.font.size = Pt(10)
            run1.font.color.rgb = BLUE
            run2 = p.add_run()
            run2.text = desc
            run2.font.size = Pt(10)
            run2.font.color.rgb = DARK

    # =========================================================================
    # SLIDE 1: Capa Oficial
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "Modelagem Preditiva de Carga e Demanda Líquida\nna Transição Energética"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = NAVY

    p = tf1.add_paragraph()
    p.text = "Da Regressão Não-Linear Clássica ao Smart Building com Microgeração Solar"
    p.font.size = Pt(18)
    p.font.color.rgb = BLUE
    p.space_before = Pt(12)

    p = tf1.add_paragraph()
    p.text = (
        "Disciplina: PGENE585 – Transição Energética Sustentável e Mercados de Energia\n"
        "PPGEE / UFAM – Universidade Federal do Amazonas\n"
        "Aluno: Aldair da Silva Azevedo | Professor: Dr. Kenny Vinente"
    )
    p.font.size = Pt(13)
    p.font.color.rgb = DARK
    p.space_before = Pt(28)

    # =========================================================================
    # SLIDE 2: Cenários Físicos & Relevância Energética
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(
        s2,
        "1. Cenários Reais e Relevância Energética",
        "Fundamentos Físicos dos Dois Sistemas Modelados em Python",
    )
    tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    points_s2 = [
        (
            "Cenário 1 — Rede de Distribuição Metropolitana (CMU 15-884):",
            " Dados reais da concessionária Duquesne Light (Pittsburgh, EUA) cobrindo 4 anos "
            "completos (2008 a 2011) — totalizando 1.460 dias e 35.064 horas consecutivas de "
            "despacho elétrico da rede.",
        ),
        (
            "A Física da Não-Linearidade Térmica:",
            " O consumo de energia responde à termodinâmica humana em curva em 'U': dias amenos "
            "(~15,6°C) têm baixa demanda, enquanto o frio rigoroso (abaixo de 0°C e até "
            "-14,4°C) dispara o aquecimento e o calor intenso (acima de 29°C e até 35,0°C) "
            "dispara o ar-condicionado.",
        ),
        (
            "Cenário 2 — Edifício Inteligente Comercial Prosumidor (Zenodo 2025):",
            " Prédio com geração solar fotovoltaica instalada na cobertura (Rooftop Solar PV). "
            "Telemetria de 1 ano completo com medições a cada 5 minutos (105.120 amostras) de "
            "potência ativa, tensão, corrente, temperatura e geração solar.",
        ),
        (
            "Relevância para a Transição e Mercado Livre (Grupo B):",
            " A expansão do PLD Horário e das tarifas dinâmicas exige prever com alta precisão a "
            "Demanda Líquida (Carga - Solar) para evitar multas de ultrapassagem e "
            "despachar baterias.",
        ),
    ]
    for title, desc in points_s2:
        p = tf2.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(13.5)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(13)
        run2.font.color.rgb = DARK
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 3: Formulação Matemática (L2 vs. L1)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(
        s3,
        "2. Formulação Matemática: Funções de Perda L2 vs. L1",
        "Otimização Paramétrica e Comportamento dos Erros no Sistema em Python",
    )
    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    points_s3 = [
        (
            "Variáveis Físicas do Modelo (CMU Item 5):",
            " Entrada (x): Temperatura máxima diária em graus Celsius (°C). Alvo (y): Pico diário "
            "de demanda da concessionária em Gigawatts (GW). Histórico: N = 1.460 dias observados.",
        ),
        (
            "Perda Quadrática (L2 — Mínimos Quadrados / Squared Loss):",
            " J(θ) = Σ (y_i - φ(x_i) θ)². Resolvida no Python por Equação Normal analítica: "
            "θ = (Φᵀ Φ)⁻¹ Φᵀ y. Supõe distribuição normal de ruídos; pune severamente erros "
            "grandes, sendo puxada para baixo por feriados ou quedas pontuais de carga.",
        ),
        (
            "Perda Absoluta (L1 — LAD Robusta / Absolute Loss):",
            " J(θ) = Σ |y_i - φ(x_i) θ|. Otimiza a MEDIANA condicional (distribuição Laplace). "
            "Resolvida no Python por otimização convexa direta (scipy via Powell). Extremamente "
            "robusta a desvios e quedas anômalas, traçando a curva da demanda típica.",
        ),
        (
            "Regularização Ridge (L2 Shrinkage com λ = 10⁻⁴):",
            " Adiciona penalidade λ ||θ||² na função objetivo para restringir a norma dos pesos "
            "e evitar sobreajuste (overfitting) em transformações de alta dimensão.",
        ),
    ]
    for title, desc in points_s3:
        p = tf3.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(13)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(12.5)
        run2.font.color.rgb = DARK
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 4: Os 4 Modelos de Regressão (Item 5)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(
        s4,
        "3. Arquitetura dos 4 Modelos de Regressão",
        "CMU 15-884 (Item 5) – Capacidade de Modelagem e Resposta Térmica",
    )

    # Card Superior: Definição Explícita de Modelo de Regressão
    card_def4 = s4.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.8),
        Inches(1.7),
        Inches(11.733),
        Inches(1.2),
    )
    card_def4.fill.solid()
    card_def4.fill.fore_color.rgb = RGBColor(239, 246, 255)
    card_def4.line.color.rgb = BLUE
    card_def4.line.width = Pt(1.2)

    tf_def4 = card_def4.text_frame
    tf_def4.word_wrap = True
    tf_def4.margin_top = Inches(0.1)
    tf_def4.margin_bottom = Inches(0.08)
    tf_def4.margin_left = Inches(0.18)
    tf_def4.margin_right = Inches(0.18)

    p_def0 = tf_def4.paragraphs[0]
    p_def0.text = "O que é um Modelo de Regressão?"
    p_def0.font.bold = True
    p_def0.font.size = Pt(12.5)
    p_def0.font.color.rgb = NAVY

    p_def1 = tf_def4.add_paragraph()
    p_def1.text = (
        "É uma técnica estatística e de aprendizado de máquina (Machine Learning) usada para "
        "investigar a relação entre uma variável dependente (o desfecho ou valor que queremos "
        "prever) e uma ou mais variáveis independentes (os preditores ou características)."
    )
    p_def1.font.size = Pt(11)
    p_def1.font.color.rgb = DARK
    p_def1.space_before = Pt(3)

    tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(3.05), Inches(11.733), Inches(4.0))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    points_s4 = [
        (
            "1. Linear Simples [φ(x) = [1, x]]:",
            " Linha reta rígida com pesos θ ∈ ℝ². Falha na física do problema (R² = 0.116), "
            "pois supõe erroneamente que frio e calor agem na mesma direção sobre o consumo.",
        ),
        (
            "2. Polinomial [φ(x) = [1, x, x², x³, x⁴, x⁵]]:",
            " Curva contínua suave com pesos θ ∈ ℝ⁶. Modela a elevação no frio e no calor "
            "(R² salta para 0.715). Ponto fraco: vulnerabilidade a oscilações em extremos "
            "térmicos.",
        ),
        (
            "3. Funções de Base Radial (RBF Local):",
            " 5 centros fixos distribuídos na faixa térmica μ = [-6,7; 4,4; 15,6; 26,7; 37,8]°C "
            "com dispersão σ ≈ 11,1°C. φ_j(x) = exp(-(x - μ_j)² / (2σ²)). Sinos gaussianos que "
            "capturam comportamentos locais sem instabilidade nas bordas (R² = 0.713).",
        ),
        (
            "4. Kernel Gaussiano com Ridge (Dual, λ = 10⁻⁴):",
            " Formulação dual via matriz de Gram K ∈ ℝ¹⁴⁶⁰ˣ¹⁴⁶⁰, comparando cada dia contra "
            "todo o histórico. Atingiu a maior acurácia global do estudo (R² = 0.717 e menor "
            "RMSE = 0.157 GW).",
        ),
    ]
    for idx, (title, desc) in enumerate(points_s4):
        p = tf4.add_paragraph() if idx > 0 else tf4.paragraphs[0]
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(12)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(11.5)
        run2.font.color.rgb = DARK
        if idx > 0:
            p.space_before = Pt(6)

    # =========================================================================
    # SLIDE 5: Resultados Visuais CMU Q5 (Gráfico + Painel Lateral)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(
        s5,
        "4. Resultados Experimentais: Ajuste dos 4 Modelos (Q5)",
        "CMU 15-884 (Item 5) – Comparativo das Curvas Ajustadas em 1.460 Dias",
    )
    notes_s5 = [
        (
            "Dispersão Observada: ",
            "1.460 pontos cinzas registrando a demanda diária real em GW da Duquesne Light.",
        ),
        (
            "Mínimo Térmico: ",
            "O vale de consumo ocorre perto de 15,6°C; acima de 29°C (chegando a 35,0°C) a "
            "demanda atinge pico.",
        ),
        (
            "Comportamento L1 vs L2: ",
            "As curvas com perda L1 (mediana) situam-se ligeiramente ACIMA de L2 (média), "
            "pois a perda quadrática L2 é puxada para baixo por feriados e quedas anômalas.",
        ),
        (
            "Conclusão do Estudo: ",
            "A não-linearidade térmica é mandatória: modelos não-lineares elevam a acurácia "
            "em >600%.",
        ),
    ]
    hl_title_s5 = "Métricas de Acurácia Calculadas no Sistema em Python:"
    hl_desc_s5 = (
        "• Métricas: R² = Acurácia/Explicação (0 a 1) | RMSE = Erro quadrático (GW) | "
        "MAE = Desvio médio absoluto (GW)\n"
        "• Linear Simples (L2): RMSE = 0.278 GW | MAE = 0.226 GW | R² = 0.116 (Insuficiente)\n"
        "• Polinomial d=5 (L2): RMSE = 0.158 GW | MAE = 0.120 GW | R² = 0.715 (Excelente em U)\n"
        "• RBF 5 centros (L2): RMSE = 0.158 GW | MAE = 0.121 GW | R² = 0.713 (Estável local)\n"
        "• Kernel Gaussiano (L2): RMSE = 0.157 GW | MAE = 0.120 GW | R² = 0.717 (Campeão global)\n"
        "• Kernel Gaussiano (L1): Menor MAE de toda a suíte (0.118 GW) com máxima robustez."
    )
    add_chart_with_notes(
        s5, img_q5, notes_s5, "Roteiro de Leitura Física", hl_title_s5, hl_desc_s5
    )

    # =========================================================================
    # SLIDE 6: Engenharia de Dados & Limpeza de Sensores (Item 6)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(
        s6,
        "5. Engenharia de Dados: Higienização e Sincronização",
        "CMU 15-884 (Item 6) – Tratamento de Sensores e Alinhamento Temporal",
    )
    tb6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    points_s6 = [
        (
            "Dados Brutos de Entrada:",
            " q6_demand.txt (35.064 horas de demanda da Duquesne Light em MW) e "
            "q6_weather.txt (38.765 medições meteorológicas assíncronas do Aeroporto de "
            "Pittsburgh).",
        ),
        (
            "Detecção e Tratamento de Sentinelas (-9999):",
            " Sensores meteorológicos reais apresentam falhas reportadas como '-9999'. O módulo "
            "DataCleaner substituiu 100 medições defeituosas (18 em temp, 18 em orvalho, 18 em "
            "umidade, 20 em pressão, 26 em vento) por interpolação linear temporal contínua.",
        ),
        (
            "Deduplicação e Sincronização Horária Exata:",
            " Timestamps duplicados foram expurgados. Como as leituras climáticas chegavam em "
            "intervalos irregulares (a cada 45 ou 50 min), o TimeSeriesInterpolator sincronizou "
            "cada medição ao segundo zero de cada uma das 35.064 horas da carga.",
        ),
        (
            "Agregação Diária e Matriz de Features:",
            " Extração do pico diário de demanda elétrica (y_d em MW) e 6 atributos climáticos "
            "agregados por dia: Temp Máx, Temp Mín, Orvalho Médio, Umidade Média, Pressão e Vento.",
        ),
    ]
    for title, desc in points_s6:
        p = tf6.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(13)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(12.5)
        run2.font.color.rgb = DARK
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 7: Prova da Redução do MSE (Item 6)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(
        s7,
        "6. Prova Empírica: Benefício do Modelo Multivariado",
        "CMU 15-884 (Item 6) – Redução de 8.73% no Erro Quadrático Médio (MSE)",
    )
    notes_s7 = [
        (
            "O Teste de Hipótese: ",
            "Verificar se incorporar vento, umidade e orvalho reduz o erro frente à temperatura "
            "máxima isolada.",
        ),
        (
            "Ponto de Orvalho (+0.39): ",
            "Expressa calor latente e umidade absoluta; sensação de abafamento eleva o uso "
            "de condicionadores de ar.",
        ),
        (
            "Velocidade do Vento (-0.14): ",
            "Promove convecção térmica nas fachadas e arrefecimento passivo, aliviando a carga.",
        ),
        (
            "Pressão Atmosférica: ",
            "Indica aproximação de tempestades e frentes frias, antecipando picos de demanda.",
        ),
    ]
    hl_title_s7 = "Evidência Empírica Calculada no Pipeline em Python:"
    hl_desc_s7 = (
        "• Modelo Univariado (T_max isolada): MSE = 19.866,54 MW² | R² = 0.509\n"
        "• Modelo Multivariado (6 Variáveis Climáticas): MSE = 18.131,88 MW² | R² = 0.552\n"
        "➔ GANHO REAL DE ACURÁCIA: REDUÇÃO DE 8.73% NO ERRO QUADRÁTICO MÉDIO (MSE).\n"
        "Comprova a tese de que a atmosfera atua de forma multivariada sobre a demanda da rede."
    )
    add_chart_with_notes(
        s7, img_q6, notes_s7, "Física das Novas Variáveis", hl_title_s7, hl_desc_s7
    )

    # =========================================================================
    # SLIDE 8: Competição Zenodo 2025 (Smart Building)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(
        s8,
        "7. Smart Building & Energia Solar (Zenodo 2025)",
        "Competição Zenodo 2025 – Telemetria Real em 105.120 Amostras",
    )
    tb8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    points_s8 = [
        (
            "Cenário Físico do Edifício Inteligente:",
            " Telemetria de 1 ano completo a cada 5 minutos (105.120 leituras) de Potência "
            "Ativa (W), Tensão (V), Corrente (A), Temperatura (°C) e Geração Fotovoltaica "
            "em telhado (W).",
        ),
        (
            "Pipeline de Modelagem no Python:",
            " Agregação em 8.760 horas, defasagens temporais autoregressivas (lags t-1, t-2) e "
            "variáveis de calendário (hora do dia 0-23 e dia da semana 0-6).",
        ),
        (
            "Avaliação Multi-critério da Competição:",
            " Avalia conjuntamente acurácia de erro (RMSE e MAE), qualidade de ajuste (R²) e "
            "tempo de processamento computacional para viabilizar controle em tempo real.",
        ),
        (
            "Resultados Comparativos dos Modelos:",
            " Ridge Linear: RMSE = 398,35 W | MAE = 221,67 W | R² = 0.871 | Latência: 17,5 ms.\n"
            " Random Forest (50 árvores): RMSE = 349,45 W | MAE = 184,12 W | R² = 0.900 | "
            "Tempo: 134,1 ms (Campeão em acurácia e capacidade de generalização).",
        ),
    ]
    for title, desc in points_s8:
        p = tf8.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(13)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(12.5)
        run2.font.color.rgb = DARK
        p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 9: Demanda Líquida & Curva do Pato
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(
        s9,
        "8. Impacto da Demanda Líquida e Curva do Pato",
        "Smart Building & Transição – Autoconsumo Solar e Curva do Pato",
    )
    notes_s9 = [
        (
            "Demanda Líquida: ",
            "Calculada no sistema como P_líquida = P_consumo - P_solar. Representa a carga líquida "
            "que a rede deve atender.",
        ),
        (
            "Curva do Pato: ",
            "O pico solar ao meio-dia (~6 kW) afunda a demanda líquida para perto de zero; às 18h "
            "surge uma rampa de subida severa.",
        ),
        (
            "Oportunidade BESS: ",
            "Justifica o uso de bancos de baterias para absorver excedente solar e descarregar "
            "no horário de ponta.",
        ),
        (
            "Gestão Econômica: ",
            "Permite ao gestor predial no Mercado Livre evitar custos abusivos com demanda "
            "contratada.",
        ),
    ]
    hl_title_s9 = "Balanço Energético Anual Calculado no Sistema em Python:"
    hl_desc_s9 = (
        "• Potência Média Consumida pelo Edifício: 1.909 W (1,91 kW)\n"
        "• Potência Média Gerada pelos Painéis Solares: 715 W (Pico máximo registrado: 5.993 W)\n"
        "• TAXA DE COBERTURA / AUTOCONSUMO SOLAR: 13.53% de toda a energia do edifício.\n"
        "Apresenta a formação clássica da Curva do Pato, evidenciando a necessidade de "
        "inteligência preditiva para despacho e resposta da demanda."
    )
    add_chart_with_notes(
        s9,
        img_zenodo,
        notes_s9,
        "Análise Operacional",
        hl_title_s9,
        hl_desc_s9,
        img_width_in=7.3,
        highlight_top_in=5.8,
        highlight_h_in=1.1,
    )

    # =========================================================================
    # SLIDE 10: Conclusões & Repositório GitHub
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(
        s10,
        "9. Conclusões e Contribuições para a Pesquisa",
        "Síntese das Contribuições e Integração com a Dissertação de Mestrado",
    )
    tb10 = s10.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(3.6))
    tf10 = tb10.text_frame
    tf10.word_wrap = True

    points_s10 = [
        (
            "Superioridade de Modelos Não-Lineares Regularizados:",
            " O Kernel Gaussiano Ridge (CMU) e o Random Forest (Zenodo) atingiram R² de 0.717 e "
            "0.900, demonstrando a necessidade de capturar a não-linearidade térmica e solar.",
        ),
        (
            "A Força da Engenharia de Atributos Multivariada:",
            " A inclusão de variáveis como ponto de orvalho e vento reduziu o erro em 8.73% "
            "em relação ao uso de temperatura isolada na rede da Duquesne Light.",
        ),
        (
            "Conexão com a Dissertação de Mestrado (HEMS no Mercado Livre):",
            " A previsão de demanda líquida desenvolvida neste trabalho constitui o módulo de "
            "inteligência central do sistema autônomo (HEMS) proposto para o Grupo B.",
        ),
        (
            "Arquitetura e Qualidade de Software:",
            " Aplicação monolítica full stack em Python com POO, auditável via 7 ciclos em JSON, "
            "com cobertura de testes automatizados e zero débito técnico (Clean Code).",
        ),
    ]
    for title, desc in points_s10:
        p = tf10.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(13)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(12.5)
        run2.font.color.rgb = DARK
        p.space_before = Pt(5)

    # Card do Repositório GitHub para Download e Teste
    card_gh = s10.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.8),
        Inches(5.35),
        Inches(11.7),
        Inches(1.55),
    )
    card_gh.fill.solid()
    card_gh.fill.fore_color.rgb = RGBColor(241, 245, 249)
    card_gh.line.color.rgb = BLUE
    card_gh.line.width = Pt(1.5)

    tf_gh = card_gh.text_frame
    tf_gh.word_wrap = True
    tf_gh.margin_top = Inches(0.12)
    tf_gh.margin_left = Inches(0.2)
    tf_gh.margin_right = Inches(0.2)

    p_gh1 = tf_gh.paragraphs[0]
    p_gh1.text = "Repositório no GitHub (Código-Fonte Aberto, Dados, Testes e Dashboard Web):"
    p_gh1.font.bold = True
    p_gh1.font.size = Pt(12)
    p_gh1.font.color.rgb = NAVY

    p_gh2 = tf_gh.add_paragraph()
    run_gh_link = p_gh2.add_run()
    run_gh_link.text = "👉 https://github.com/AldairAzevedo/energy-demand-forecast"
    run_gh_link.font.bold = True
    run_gh_link.font.size = Pt(14)
    run_gh_link.font.color.rgb = BLUE
    run_gh_link.hyperlink.address = "https://github.com/AldairAzevedo/energy-demand-forecast"
    p_gh2.space_before = Pt(3)

    p_gh3 = tf_gh.add_paragraph()
    p_gh3.text = (
        "Para clonar e testar localmente:  git clone "
        "https://github.com/AldairAzevedo/energy-demand-forecast.git  &&  "
        "python -m streamlit run src/ui/app.py"
    )
    p_gh3.font.size = Pt(10.5)
    p_gh3.font.color.rgb = DARK
    p_gh3.space_before = Pt(3)

    out_file = os.path.join(base_dir, "presentation", "slides_apresentacao.pptx")
    prs.save(out_file)
    print(f"Apresentação gerada com sucesso em: {out_file}")
    return out_file


if __name__ == "__main__":
    current = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current, ".."))
    build_presentation(project_root)
