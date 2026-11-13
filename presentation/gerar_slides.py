"""Gerador de slides executivos (PPTX) estritamente focado no desafio Zenodo 2025."""

import json
import os
from typing import Any, Dict, List, Tuple

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

NAVY = RGBColor(15, 23, 42)
BLUE = RGBColor(37, 99, 235)
DARK = RGBColor(51, 65, 85)
GREEN = RGBColor(5, 150, 105)
WHITE = RGBColor(255, 255, 255)
LIGHT_BG = RGBColor(241, 245, 249)


def _add_header(slide: Any, title_text: str, subtitle_text: str) -> None:
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(1.15))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title_text
    p1.font.size = Pt(25)
    p1.font.bold = True
    p1.font.color.rgb = NAVY

    p2 = tf.add_paragraph()
    p2.text = subtitle_text
    p2.font.size = Pt(13)
    p2.font.color.rgb = BLUE
    p2.space_before = Pt(4)


def _add_bullets(slide: Any, points: List[Tuple[str, str]], top_in: float = 1.8) -> None:
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(top_in), Inches(11.7), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    for idx, (title, desc) in enumerate(points):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        r1 = p.add_run()
        r1.text = title
        r1.font.bold = True
        r1.font.size = Pt(14)
        r1.font.color.rgb = NAVY

        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(13.5)
        r2.font.color.rgb = DARK
        p.space_before = Pt(12 if idx > 0 else 0)


def _build_cover(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5)
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = NAVY
    bg.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "PGENE585 • PPGEE / UFAM • TRANSIÇÃO ENERGÉTICA SUSTENTÁVEL E MERCADOS DE ENERGIA"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(96, 165, 250)

    p1 = tf.add_paragraph()
    p1.text = "Previsão de Consumo Elétrico em Smart Buildings"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_before = Pt(14)

    p2 = tf.add_paragraph()
    p2.text = (
        "Competição Zenodo 2025: Electric Energy Consumption Forecast "
        "Adopting Multi-criteria Performance Metrics"
    )
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_before = Pt(12)

    p3 = tf.add_paragraph()
    p3.text = "Aluno: Aldair da Silva Azevedo   |   Prof. Dr.: Kenny Vinente"
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(148, 163, 184)
    p3.space_before = Pt(32)


def _build_problem_slide(prs: Presentation, data: Dict[str, Any]) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_header(
        slide,
        "1. O Desafio Oficial (Zenodo 2025 — GECAD / ISEP)",
        "Objetivo único: prever o consumo elétrico do edifício (power em Watts)",
    )
    _add_bullets(
        slide,
        [
            (
                "Variável Alvo (Target): ",
                "Potência ativa total consumida pelo edifício — power (W).",
            ),
            (
                "Base de Telemetria (v1.0): ",
                f"{data['total_5min_samples']} leituras válidas em intervalos de 5 min "
                f"(agregadas em {data['total_hourly_samples']} horas).",
            ),
            (
                "Canais de Entrada Disponíveis: ",
                "Time, Voltage (V), Amperage (A), Generation Power (W) e Temperature (°C).",
            ),
            (
                "Critérios Oficiais de Avaliação: ",
                "1) Acurácia (RMSE e MAE); 2) Desempenho computacional (tempo de treino e "
                "inferência); 3) Eficiência energética computacional.",
            ),
        ],
    )


def _build_features_slide(prs: Presentation, data: Dict[str, Any]) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_header(
        slide,
        "2. Engenharia de Atributos Causais para Máxima Acurácia",
        "Todos os atributos usam apenas informação disponível até o instante t (sem data leakage)",
    )
    _add_bullets(
        slide,
        [
            (
                "Sazonalidade Diária (Time): ",
                "Codificação cíclica da hora do dia (sin/cos de 24h) para capturar picos de carga.",
            ),
            (
                "Variáveis Exógenas do Dataset: ",
                "Temperatura externa (°C) e geração FV local (W) agregadas em média horária.",
            ),
            (
                "Lags Autoregressivos de Consumo: ",
                "power(t-1, t-2, t-3, t-24, t-48, t-168) para inércia horária, diária e semanal.",
            ),
            (
                "Estatísticas Móveis & Lags Elétricos: ",
                "Média móvel (6h, 24h), desvio padrão (24h) de power e lags (t-1) de tensão.",
            ),
            (
                "Divisão Temporal Estrita: ",
                f"Treino ({data['train_samples']}h — 80%) e Teste ({data['test_samples']}h — 20%).",
            ),
        ],
    )


def _build_benchmark_slide(prs: Presentation, data: Dict[str, Any]) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_header(
        slide,
        "3. Benchmarking Multi-Critério dos Modelos Preditivos",
        f"Campeão em acurácia: {data['best_model_name']}",
    )

    bench = data["models_benchmarking"]
    rows = [["Modelo", "RMSE (W)", "MAE (W)", "R²", "Treino (ms)", "Inferência (ms)"]]
    for _, info in bench.items():
        m = info["metrics"]
        rows.append(
            [
                info["name"],
                f"{m['rmse']:.2f}",
                f"{m['mae']:.2f}",
                f"{m['r2']:.4f}",
                f"{m['train_time_ms']:.2f}",
                f"{m['inference_time_ms']:.2f}",
            ]
        )

    table_shape = slide.shapes.add_table(
        len(rows), 6, Inches(0.8), Inches(1.85), Inches(11.7), Inches(2.6)
    )
    table = table_shape.table
    widths = [3.6, 1.5, 1.5, 1.3, 1.9, 1.9]
    for idx, w in enumerate(widths):
        table.columns[idx].width = Inches(w)

    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(13)
            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = NAVY
                p.font.color.rgb = WHITE
                p.font.bold = True
            else:
                p.font.color.rgb = DARK

    _add_bullets(
        slide,
        [
            (
                "Trade-off Acurácia vs. Tempo: ",
                "HistGradientBoosting atingiu o menor erro (RMSE/MAE) com inferência < 10 ms; "
                "Ridge Linear oferece o menor custo computacional.",
            ),
        ],
        top_in=4.9,
    )


def _build_chart_slide(prs: Presentation, img_path: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_header(
        slide,
        "4. Comparação Visual: Consumo Real vs. Previsões (168h)",
        "Aderência horária dos modelos na amostra de teste da competição Zenodo 2025",
    )
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(0.8), Inches(1.65), width=Inches(11.7))


def _build_conclusion_slide(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _add_header(
        slide,
        "5. Conclusões & Ecossistema do Projeto",
        "Repositório limpo, auditável e alinhado 100% ao objetivo da competição Zenodo 2025",
    )
    _add_bullets(
        slide,
        [
            (
                "Foco Estrito na Competição: ",
                "Remoção de métricas fora do escopo, mantendo somente previsão de power (W) e "
                "avaliação multi-critério (RMSE, MAE, Treino e Inferência).",
            ),
            (
                "Qualidade & Reprodutibilidade: ",
                "Código validado com isort, black, flake8 (0 warnings) e suíte pytest.",
            ),
            (
                "Plataforma Online: ",
                "https://energy-demand-forecast-ufam.streamlit.app/",
            ),
            (
                "Repositório GitHub: ",
                "https://github.com/AldairAzevedo/energy-demand-forecast",
            ),
        ],
    )


def build_presentation(base_dir: str) -> str:
    """Constrói a apresentação PPTX com foco estrito no desafio Zenodo 2025."""
    json_path = os.path.join(base_dir, "data", "cycles", "zenodo_forecast_results.json")
    with open(json_path, "r", encoding="utf-8") as file:
        data: Dict[str, Any] = json.load(file)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    _build_cover(prs)
    _build_problem_slide(prs, data)
    _build_features_slide(prs, data)
    _build_benchmark_slide(prs, data)
    _build_chart_slide(prs, os.path.join(base_dir, "results", "zenodo_forecast.png"))
    _build_conclusion_slide(prs)

    out_path = os.path.join(base_dir, "presentation", "slides_apresentacao.pptx")
    prs.save(out_path)
    return out_path


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Apresentação atualizada: {build_presentation(root)}")
