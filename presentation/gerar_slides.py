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

    NAVY = RGBColor(15, 23, 42)        # #0F172A
    BLUE = RGBColor(37, 99, 235)       # #2563EB
    DARK = RGBColor(51, 65, 85)        # #334155

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

    # SLIDE 1: Capa
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

    # SLIDE 2: Contexto & Motivação
    s2 = prs.slides.add_slide(blank_layout)
    add_header(
        s2,
        "1. Contexto e Motivação na Engenharia Elétrica",
        "Fundamentos e Desafios da Descarbonização e Mercado Livre",
    )
    tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    points_s2 = [
        (
            "A Demanda Elétrica como Fenômeno Físico-Climático:",
            " O consumo de energia é fortemente não-linear. Em baixas e altas temperaturas, "
            "os picos disparam (aquecimento no frio, condicionamento de ar no calor extremo).",
        ),
        (
            "Transição Energética e Incerteza:",
            " A penetração massiva de energias renováveis (solar e eólica) transforma consumidores "
            "em 'prosumidores', exigindo modelos preditivos mais rápidos e robustos.",
        ),
        (
            "Abertura do Mercado Livre (Grupo B):",
            " Pequenos consumidores e residências passam a responder a sinais horários de preço "
            "(PLD Horário), tornando a acurácia da previsão um ativo econômico vital.",
        ),
        (
            "Objetivo do Trabalho:",
            " Implementar, avaliar e comparar sistematicamente modelos de regressão clássicos e "
            "modernos (CMU 15-884) e algoritmos em Smart Buildings (Zenodo 2025).",
        ),
    ]
    for title, desc in points_s2:
        p = tf2.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(14)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(14)
        run2.font.color.rgb = DARK
        p.space_before = Pt(10)

    # SLIDE 3: Formulação Matemática
    s3 = prs.slides.add_slide(blank_layout)
    add_header(
        s3,
        "2. Formulação Matemática: Funções de Perda L2 vs. L1",
        "CMU 15-884 (Item 5) – Minimização de Resíduos e Otimização Paramétrica",
    )
    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    points_s3 = [
        (
            "Perda Quadrática (L2 - Squared Loss / Mínimos Quadrados):",
            " J(θ) = Σ (y_i - φ(x_i) θ)². Pune erros grandes de forma quadrática. "
            "Fornece solução analítica exata: θ = (Φᵀ Φ)⁻¹ Φᵀ y. Vulnerável a outliers.",
        ),
        (
            "Perda Absoluta (L1 - Absolute Loss / LAD):",
            " J(θ) = Σ |y_i - φ(x_i) θ|. Penaliza linearmente os desvios. Otimiza a MEDIANA "
            "condicional em vez da média. Extremamente robusta a ruídos e anomalias de rede.",
        ),
        (
            "Regularização Ridge (L2 Shrinkage):",
            " Adiciona λ ||θ||² à função de perda para restringir a magnitude dos pesos "
            "e evitar sobreajuste (overfitting) em espaços de alta dimensão.",
        ),
    ]
    for title, desc in points_s3:
        p = tf3.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(14)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(14)
        run2.font.color.rgb = DARK
        p.space_before = Pt(12)

    # SLIDE 4: Os 4 Modelos de Regressão
    s4 = prs.slides.add_slide(blank_layout)
    add_header(
        s4,
        "3. Arquitetura dos 4 Modelos Avaliados",
        "CMU 15-884 (Item 5) – Do Linear Rígido ao Kernel Gaussiano Ridge",
    )
    tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    points_s4 = [
        (
            "1. Linear Simples:",
            " φ(x) = [1, x]. Linha reta rígida. Incapaz de modelar a curva em 'U' "
            "da demanda térmica (R² baixo ~ 0.11).",
        ),
        (
            "2. Polinomial (Grau 5):",
            " φ(x) = [1, x, x², x³, x⁴, x⁵]. Curva suave que dobra no calor e no frio "
            "(R² salta para ~ 0.71). Limitação: oscilações nas pontas térmicas.",
        ),
        (
            "3. Funções de Base Radial (RBF):",
            " 5 sinos gaussianos espalhados com σ=20: φ_j(x) = exp(-(x - μ_j)² / (2σ²)). "
            "Captura respostas térmicas locais sem explodir nas extremidades.",
        ),
        (
            "4. Kernel Gaussiano com Regularização Ridge (λ=10⁻⁴):",
            " Compara cada dia com todo o histórico: K(x, x') = exp(-(x - x')² / (2σ²)). "
            "Alcança o melhor R² (0.717) e menor RMSE (0.157 GW).",
        ),
    ]
    for title, desc in points_s4:
        p = tf4.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(13.5)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(13.5)
        run2.font.color.rgb = DARK
        p.space_before = Pt(8)

    # SLIDE 5: Resultados CMU Q5 com Gráfico
    s5 = prs.slides.add_slide(blank_layout)
    add_header(
        s5,
        "4. Resultados Experimentais: Ajuste dos 4 Modelos (Q5)",
        "CMU 15-884 (Item 5) – Comparativo das Curvas Ajustadas em 1.460 Dias",
    )
    if os.path.exists(img_q5):
        s5.shapes.add_picture(img_q5, Inches(0.8), Inches(1.8), width=Inches(11.7))

    # SLIDE 6: Pré-processamento e Engenharia de Features
    s6 = prs.slides.add_slide(blank_layout)
    add_header(
        s6,
        "5. Higienização de Sensores e Interpolação (Q6)",
        "CMU 15-884 (Item 6) – Tratamento de Sentinelas e Sincronização Horária",
    )
    tb6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    points_s6 = [
        (
            "Detecção de Sentinelas (-9999):",
            " Sensores físicos falham e registram '-9999'. Foram detectados 100 registros "
            "sentinelas, tratados por substituição por NaN e interpolação linear temporal.",
        ),
        (
            "Deduplicação de Timestamps:",
            " Remoção de leituras duplicadas no mesmo segundo para garantir consistência "
            "cronológica estrita.",
        ),
        (
            "Interpolação e Sincronização Horária:",
            " As leituras climáticas assíncronas foram interpoladas linearmente para alinhar "
            "com as 35.064 horas de demanda elétrica.",
        ),
        (
            "Agregação Diária:",
            " Extração da Demanda Máxima do dia (y_d) e médias climáticas para "
            "alimentação dos modelos.",
        ),
    ]
    for title, desc in points_s6:
        p = tf6.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(14)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(14)
        run2.font.color.rgb = DARK
        p.space_before = Pt(10)

    # SLIDE 7: Prova da Redução do MSE com Gráfico
    s7 = prs.slides.add_slide(blank_layout)
    add_header(
        s7,
        "6. Prova Empírica: Benefício do Modelo Multivariado",
        "CMU 15-884 (Item 6) – Redução de 8.73% no Erro Quadrático Médio (MSE)",
    )
    if os.path.exists(img_q6):
        s7.shapes.add_picture(img_q6, Inches(0.8), Inches(1.8), width=Inches(11.7))

    # SLIDE 8: Competição Zenodo 2025
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
            "Base de Dados Real de Edifício Inteligente:",
            " 1 ano completo monitorando Potência (W), Tensão (V), Corrente (A), "
            "Geração Solar FV (W) e Temperatura (°C).",
        ),
        (
            "Avaliação Multi-critério da Competição:",
            " Avalia acurácia preditiva (RMSE, MAE, R²) e tempo computacional de execução.",
        ),
        (
            "Comparativo dos Modelos:",
            " Ridge Linear (RMSE: 398 W, Tempo: 17 ms) vs. "
            "Random Forest (RMSE: 349 W, R²: 0.900, Tempo: 134 ms).",
        ),
        (
            "Autoconsumo e Cobertura Solar:",
            " A geração solar no telhado cobriu 13.53% de toda a energia elétrica consumida, "
            "alterando o perfil de demanda da rede.",
        ),
    ]
    for title, desc in points_s8:
        p = tf8.add_paragraph()
        run1 = p.add_run()
        run1.text = title
        run1.font.bold = True
        run1.font.size = Pt(14)
        run1.font.color.rgb = NAVY
        run2 = p.add_run()
        run2.text = desc
        run2.font.size = Pt(14)
        run2.font.color.rgb = DARK
        p.space_before = Pt(10)

    # SLIDE 9: Demanda Líquida e Transição Energética com Gráfico
    s9 = prs.slides.add_slide(blank_layout)
    add_header(
        s9,
        "8. Impacto da Demanda Líquida e Curva do Pato",
        "Smart Building & Transição – Autoconsumo Solar e Curva do Pato",
    )
    if os.path.exists(img_zenodo):
        s9.shapes.add_picture(img_zenodo, Inches(0.8), Inches(1.8), width=Inches(11.7))

    # SLIDE 10: Conclusão & Próximos Passos
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
            " O Kernel Gaussiano Ridge (CMU) e o Random Forest (Zenodo) atingiram R² superior "
            "a 0.71 e 0.90, demonstrando a necessidade de capturar a não-linearidade térmica.",
        ),
        (
            "A Força da Engenharia de Atributos:",
            " A inclusão de variáveis como ponto de orvalho e umidade reduziu o erro em 8.73% "
            "em relação ao uso de temperatura isolada.",
        ),
        (
            "Conexão com a Dissertação de Mestrado:",
            " A previsão de demanda líquida desenvolvida neste trabalho constitui o "
            "módulo de inteligência central do sistema autônomo (HEMS) proposto para "
            "o Mercado Livre (Grupo B).",
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
        run2.font.size = Pt(13)
        run2.font.color.rgb = DARK
        p.space_before = Pt(6)

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
