"""Script para geração automatizada dos slides da apresentação Zenodo (PowerPoint)."""

import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt


def build_presentation(base_dir: str) -> str:
    """Constrói a apresentação PPTX completa com 7 slides focados no desafio Zenodo."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    NAVY = RGBColor(15, 23, 42)  # #0F172A
    BLUE = RGBColor(37, 99, 235)  # #2563EB
    DARK = RGBColor(51, 65, 85)  # #334155
    GREEN = RGBColor(5, 150, 105)  # #059669

    results_dir = os.path.join(base_dir, "results")
    img_zenodo = os.path.join(results_dir, "zenodo_forecast.png")
    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text: str, subtitle_text: str) -> None:
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(1.15))
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

    def add_bullet_list(slide, points: list, top_in: float = 1.75, font_size: float = 13) -> None:
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(top_in), Inches(11.7), Inches(5.0))
        tf = tb.text_frame
        tf.word_wrap = True
        for idx, (title, desc) in enumerate(points):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            run1 = p.add_run()
            run1.text = title
            run1.font.bold = True
            run1.font.size = Pt(font_size)
            run1.font.color.rgb = NAVY

            run2 = p.add_run()
            run2.text = desc
            run2.font.size = Pt(font_size - 0.5)
            run2.font.color.rgb = DARK
            p.space_before = Pt(10 if idx > 0 else 0)

    def add_chart_with_notes(
        slide,
        img_path: str,
        notes: list,
        note_title: str,
        highlight_title: str,
        highlight_text: str,
        img_width_in: float = 7.3,
        highlight_top_in: float = 5.75,
        highlight_h_in: float = 1.25,
    ) -> None:
        """Insere imagem na esquerda, destaque inferior e painel explicativo na direita."""
        if os.path.exists(img_path):
            slide.shapes.add_picture(
                img_path, Inches(0.8), Inches(1.75), width=Inches(img_width_in)
            )

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
        tf_hl.margin_top = Inches(0.08)
        tf_hl.margin_bottom = Inches(0.08)
        tf_hl.margin_left = Inches(0.15)
        tf_hl.margin_right = Inches(0.15)

        p_hl0 = tf_hl.paragraphs[0]
        p_hl0.text = highlight_title
        p_hl0.font.bold = True
        p_hl0.font.size = Pt(11)
        p_hl0.font.color.rgb = NAVY

        p_hl1 = tf_hl.add_paragraph()
        p_hl1.text = highlight_text
        p_hl1.font.size = Pt(9.5)
        p_hl1.font.color.rgb = DARK
        p_hl1.space_before = Pt(3)

        card_rt = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(8.3),
            Inches(1.75),
            Inches(4.2),
            Inches(5.25),
        )
        card_rt.fill.solid()
        card_rt.fill.fore_color.rgb = RGBColor(248, 250, 252)
        card_rt.line.color.rgb = RGBColor(203, 213, 225)
        card_rt.line.width = Pt(1)

        tf_rt = card_rt.text_frame
        tf_rt.word_wrap = True
        tf_rt.margin_top = Inches(0.14)
        tf_rt.margin_bottom = Inches(0.14)
        tf_rt.margin_left = Inches(0.16)
        tf_rt.margin_right = Inches(0.16)

        p_rt0 = tf_rt.paragraphs[0]
        p_rt0.text = note_title
        p_rt0.font.bold = True
        p_rt0.font.size = Pt(12.5)
        p_rt0.font.color.rgb = NAVY

        for title, desc in notes:
            p = tf_rt.add_paragraph()
            p.space_before = Pt(7)
            run1 = p.add_run()
            run1.text = title
            run1.font.bold = True
            run1.font.size = Pt(10.5)
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
    p.text = "Previsão de Carga e Demanda Líquida\nem Smart Buildings (Zenodo 2025)"
    p.font.size = Pt(34)
    p.font.bold = True
    p.font.color.rgb = NAVY

    p = tf1.add_paragraph()
    p.text = "Modelos de Aprendizado de Máquina e Impacto da Geração Solar Fotovoltaica"
    p.font.size = Pt(18)
    p.font.color.rgb = BLUE
    p.space_before = Pt(14)

    p = tf1.add_paragraph()
    p.text = (
        "Disciplina: PGENE585 – Transição Energética Sustentável e Mercados de Energia\n"
        "PPGEE / UFAM – Universidade Federal do Amazonas\n"
        "Aluno: Aldair da Silva Azevedo | Professor: Dr. Kenny Vinente"
    )
    p.font.size = Pt(13.5)
    p.font.color.rgb = DARK
    p.space_before = Pt(30)

    # =========================================================================
    # SLIDE 2: Contexto, Desafio Zenodo e Transição Energética
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(
        s2,
        "1. Contexto do Desafio Zenodo e Relevância Energética",
        "Telemetria de Edifício Inteligente e Desafios da Microgeração Distribuída",
    )
    points_s2 = [
        (
            "Base de Dados Real (Competição Zenodo 2025):",
            " Monitoramento contínuo durante 1 ano inteiro (105.120 amostras em intervalos de "
            "5 minutos) de um edifício inteligente equipado com geração solar fotovoltaica.",
        ),
        (
            "Grandezas Físicas Monitoradas:",
            " Potência Ativa Consumida (W), Geração Solar Fotovoltaica em telhado (W) e "
            "Temperatura ambiente (°C).",
        ),
        (
            "Definição de Demanda Líquida (Net Load):",
            " Representa a energia efetivamente demandada da concessionária, calculada como "
            "P_líquida = P_consumo − P_solar.",
        ),
        (
            "Impacto nos Mercados de Energia:",
            " Prever com precisão a carga e o autoconsumo solar viabiliza despacho inteligente, "
            "redução de picos tarifários e gestão eficiente no Mercado Livre de Energia.",
        ),
    ]
    add_bullet_list(s2, points_s2, top_in=1.85, font_size=13.5)

    # =========================================================================
    # SLIDE 3: Arquitetura da Solução & Pipeline de Dados
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(
        s3,
        "2. Arquitetura do Sistema e Engenharia de Atributos",
        "Pipeline Modular em Python com Boas Práticas de Engenharia de Software",
    )
    points_s3 = [
        (
            "1. Ingestão e Higienização (data_v1.0.xlsx):",
            " Padronização de colunas e remoção de registros inconsistentes nas 105.120 leituras.",
        ),
        (
            "2. Agregação Horária:",
            " Consolidação das amostras de 5 minutos (blocos de 12 leituras) em 8.760 horas "
            "para estabilidade estatística no treinamento.",
        ),
        (
            "3. Engenharia de Lags Temporais:",
            " Construção de matriz de atributos com Temperatura, Geração Solar e defasagens "
            "autoregressivas de curto prazo (t - 1h) e ciclo diário (t - 24h).",
        ),
        (
            "4. Validação Temporal (Sem Data Leakage):",
            " Divisão cronológica rigorosa em 80% Treino (7.008 horas) e 20% Teste (1.752 horas), "
            "com persistência auditável em JSON e cobertura de testes automatizados (pytest).",
        ),
    ]
    add_bullet_list(s3, points_s3, top_in=1.85, font_size=13.5)

    # =========================================================================
    # SLIDE 4: Avaliação Multi-critério dos Modelos de IA
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(
        s4,
        "3. Benchmarking Multi-critério: Ridge Linear vs. Random Forest",
        "Equilíbrio entre Acurácia Preditiva (RMSE, MAE, R²) e Latência Computacional",
    )

    # Card Modelo 1: Ridge
    c_ridge = s4.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.85), Inches(5.6), Inches(3.3)
    )
    c_ridge.fill.solid()
    c_ridge.fill.fore_color.rgb = RGBColor(248, 250, 252)
    c_ridge.line.color.rgb = BLUE
    c_ridge.line.width = Pt(1.5)
    tf_r = c_ridge.text_frame
    tf_r.word_wrap = True
    tf_r.margin_top = Inches(0.18)
    tf_r.margin_left = Inches(0.22)
    p = tf_r.paragraphs[0]
    p.text = "Regressão Ridge Linear (α = 1.0)"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = BLUE
    for line in [
        "• RMSE (Erro Quadrático Médio): 398,35 W",
        "• MAE (Erro Médio Absoluto): 221,67 W",
        "• R² Score (Acurácia Global): 0.871 (87,1%)",
        "• Tempo de Execução: ~14,7 ms",
        "• Perfil: Extremamente leve e rápido; ideal para sistemas embarcados.",
    ]:
        p_i = tf_r.add_paragraph()
        p_i.text = line
        p_i.font.size = Pt(12.5)
        p_i.font.color.rgb = DARK
        p_i.space_before = Pt(8)

    # Card Modelo 2: Random Forest
    c_rf = s4.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.85), Inches(5.6), Inches(3.3)
    )
    c_rf.fill.solid()
    c_rf.fill.fore_color.rgb = RGBColor(240, 253, 244)
    c_rf.line.color.rgb = GREEN
    c_rf.line.width = Pt(1.8)
    tf_f = c_rf.text_frame
    tf_f.word_wrap = True
    tf_f.margin_top = Inches(0.18)
    tf_f.margin_left = Inches(0.22)
    p = tf_f.paragraphs[0]
    p.text = "Random Forest Regressor (50 árvores) — Campeão"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = GREEN
    for line in [
        "• RMSE (Erro Quadrático Médio): 349,45 W (-12,3% de erro)",
        "• MAE (Erro Médio Absoluto): 184,12 W (-16,9% de erro)",
        "• R² Score (Acurácia Global): 0.900 (90,0%)",
        "• Tempo de Execução: ~117,8 ms",
        "• Perfil: Captura não-linearidades complexas entre clima, solar e consumo.",
    ]:
        p_i = tf_f.add_paragraph()
        p_i.text = line
        p_i.font.size = Pt(12.5)
        p_i.font.color.rgb = DARK
        p_i.space_before = Pt(8)

    # Caixa de análise comparativa inferior
    c_cmp = s4.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.4), Inches(11.7), Inches(1.4)
    )
    c_cmp.fill.solid()
    c_cmp.fill.fore_color.rgb = RGBColor(241, 245, 249)
    c_cmp.line.color.rgb = NAVY
    c_cmp.line.width = Pt(1)
    tf_c = c_cmp.text_frame
    tf_c.word_wrap = True
    tf_c.margin_top = Inches(0.14)
    tf_c.margin_left = Inches(0.22)
    p_c0 = tf_c.paragraphs[0]
    p_c0.text = "Síntese do Trade-off Preditivo:"
    p_c0.font.bold = True
    p_c0.font.size = Pt(13)
    p_c0.font.color.rgb = NAVY
    p_c1 = tf_c.add_paragraph()
    p_c1.text = (
        "O Random Forest alcança 90,0% de poder explicativo (R² = 0.900) mantendo tempo de "
        "execução próximo de 0,1 segundo, sendo a escolha recomendada para planejamento "
        "energético horário e despacho de baterias."
    )
    p_c1.font.size = Pt(12)
    p_c1.font.color.rgb = DARK
    p_c1.space_before = Pt(4)

    # =========================================================================
    # SLIDE 5: Análise Visual (Gráfico Zenodo + Curva do Pato)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(
        s5,
        "4. Resultados Visuais: Previsão e Curva do Pato",
        "Avaliação na Semana de Teste (168 Horas) e Impacto Fotovoltaico",
    )
    notes_s5 = [
        (
            "Fidelidade Preditiva: ",
            "Random Forest acompanha picos e vales horários do consumo real com R² de 90,0%.",
        ),
        (
            "Curva do Pato: ",
            "A geração solar ao meio-dia (pico de 2.404 W) reduz drasticamente a carga líquida; "
            "no fim da tarde ocorre rampa acentuada.",
        ),
        (
            "Oportunidade BESS: ",
            "Justifica armazenamento em baterias para deslocamento de excedente solar ao horário "
            "de ponta.",
        ),
        (
            "Gestão Econômica: ",
            "Permite prever com antecedência o perfil líquido para evitar ultrapassagem.",
        ),
    ]
    hl_title_s5 = "Balanço Energético Medido no Conjunto de Teste (1.752 Horas):"
    hl_desc_s5 = (
        "• Consumo Médio Bruto do Edifício: 1.710 W (1,71 kW)  |  "
        "Demanda Líquida Média: 1.479 W (1,48 kW)\n"
        "• Geração Solar Média: 231 W (Pico máximo no teste: 2.404 W)  |  "
        "TAXA DE COBERTURA SOLAR: 13,53%"
    )
    add_chart_with_notes(
        s5,
        img_zenodo,
        notes_s5,
        "Análise Operacional",
        hl_title_s5,
        hl_desc_s5,
    )

    # =========================================================================
    # SLIDE 6: Aplicação Web Online & Funcionalidades Interativas
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(
        s6,
        "5. Plataforma Web Interativa Online (Streamlit Cloud)",
        "Sistema em Produção com Retreinamento Dinâmico e Trilha de Auditoria",
    )
    points_s6 = [
        (
            "Dashboard Interativo em Tempo Real:",
            " Gráficos Plotly com seleção dinâmica de séries (Consumo Real, Ridge Linear, "
            "Random Forest, Geração Solar e Demanda Líquida).",
        ),
        (
            "Execução Ao Vivo com Logs em Terminal:",
            " Disparo sob demanda do pipeline de IA diretamente pela interface web, com medição "
            "real de latência e bloqueio de estado durante o treinamento.",
        ),
        (
            "Ingestão em Massa & Reset de Fábrica:",
            " Upload de novos arquivos Excel (.xlsx) para retreinar os modelos em segundos, "
            "com botão dedicado de restauração para o dataset oficial Zenodo.",
        ),
        (
            "Deploy Contínuo na Nuvem:",
            " Integrado ao GitHub para atualização automática na Streamlit Community Cloud, "
            "com central de downloads para slides, dados e JSON de auditoria.",
        ),
    ]
    add_bullet_list(s6, points_s6, top_in=1.85, font_size=13.5)

    # =========================================================================
    # SLIDE 7: Conclusões & Repositório GitHub
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(
        s7,
        "6. Conclusões e Contribuições para a Pesquisa",
        "Síntese dos Resultados e Integração com a Dissertação de Mestrado",
    )
    points_s7 = [
        (
            "Eficácia de Modelos Não-Lineares com Lags:",
            " O Random Forest atingiu R² = 0.900 e RMSE = 349,45 W, comprovando que features "
            "autoregressivas (t-1, t-24) associadas à geração solar modelam o edifício.",
        ),
        (
            "Impacto Mensurável da Microgeração Solar:",
            " A cobertura solar de 13,53% altera a dinâmica da carga líquida (Curva do Pato), "
            "tornando a previsão essencial para coordenação com baterias (BESS).",
        ),
        (
            "Conexão com a Dissertação de Mestrado (HEMS):",
            " Este pipeline compõe o módulo preditivo central de um sistema de gerenciamento "
            "energético autônomo (HEMS) voltado ao Mercado Livre de Energia.",
        ),
    ]
    add_bullet_list(s7, points_s7, top_in=1.7, font_size=13)

    # Card do Repositório GitHub
    card_gh = s7.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.8),
        Inches(5.25),
        Inches(11.7),
        Inches(1.65),
    )
    card_gh.fill.solid()
    card_gh.fill.fore_color.rgb = RGBColor(241, 245, 249)
    card_gh.line.color.rgb = BLUE
    card_gh.line.width = Pt(1.5)

    tf_gh = card_gh.text_frame
    tf_gh.word_wrap = True
    tf_gh.margin_top = Inches(0.14)
    tf_gh.margin_left = Inches(0.22)
    tf_gh.margin_right = Inches(0.22)

    p_gh1 = tf_gh.paragraphs[0]
    p_gh1.text = "Repositório no GitHub (Código-Fonte, Dados, Testes e Aplicação Web):"
    p_gh1.font.bold = True
    p_gh1.font.size = Pt(12.5)
    p_gh1.font.color.rgb = NAVY

    p_gh2 = tf_gh.add_paragraph()
    run_gh_link = p_gh2.add_run()
    run_gh_link.text = "👉 https://github.com/AldairAzevedo/energy-demand-forecast"
    run_gh_link.font.bold = True
    run_gh_link.font.size = Pt(14)
    run_gh_link.font.color.rgb = BLUE
    run_gh_link.hyperlink.address = "https://github.com/AldairAzevedo/energy-demand-forecast"
    p_gh2.space_before = Pt(4)

    p_gh3 = tf_gh.add_paragraph()
    p_gh3.text = (
        "Execução local:  git clone "
        "https://github.com/AldairAzevedo/energy-demand-forecast.git  &&  "
        "python -m streamlit run streamlit_app.py"
    )
    p_gh3.font.size = Pt(10.5)
    p_gh3.font.color.rgb = DARK
    p_gh3.space_before = Pt(4)

    out_file = os.path.join(base_dir, "presentation", "slides_apresentacao.pptx")
    prs.save(out_file)
    print(f"Apresentação gerada com sucesso em: {out_file}")
    return out_file


if __name__ == "__main__":
    current = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current, ".."))
    build_presentation(project_root)
