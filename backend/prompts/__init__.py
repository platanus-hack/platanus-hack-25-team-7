from .loader import (
    generate_general_analyst_prompt,
    generate_specialist_prompt,
    generate_head_coach_aggregation_prompt,
)

# -------------------------------------------------------------
# Helpers para pedir salida estructurada JSON al LLM.
# Mantienen el esquema minimalista para el dashboard.
# -------------------------------------------------------------

SEGMENT_SUMMARY_SCHEMA_EXAMPLE = {
    "segment_index": 0,
    "start_s": 0,
    "end_s": 30,
    "acciones_total": 22,
    "acciones_min": 44.0,
    "intentos": 12,
    "exitos": 7,
    "success_rate": 0.58,
    "striking_s": 9,
    "grappling_s": 6,
    "submission_s": 0,
    "movement_s": 15,
    "movement_ratio": 0.5,
    "clinch_control_s": 4,
    "submission_threat_s": 0,
    "highlights": [
        {
            "timestamp": "00:08",
            "titulo": "Jab limpio",
            "descripcion": "Peleador A conecta jab que rompe distancia.",
            "tipo": "offense",
            "disciplina": "Striking",
            "impacto": 3
        }
    ]
}

TACTICAL_COACH_SUMMARY_SCHEMA_EXAMPLE = {
    "fortalezas_top3": ["Control en clinch", "Jab consistente", "Buen manejo distancia"],
    "debilidades_top3": ["Defensa low kick", "Poca presión suelo", "Overhands telegráficos"],
    "ajustes_top3": ["Variar entradas al clinch", "Proteger pierna adelantada", "Mejorar defensa contra derribo"],
    "recomendacion_tactica": "Mantén el centro y fuerza intercambios cortos tras jab.",
    "foco_disciplina": "Striking",
    "riesgo_principal": "Acumulación de daño en pierna adelantada",
    "oportunidad_principal": "Aprovechar control en clinch para rodilla interna"
}


def generate_structured_segment_prompt(general_analyst_table: str, segment_index: int, start_s: int, end_s: int) -> str:
    """Prompt para pedir al LLM un JSON SegmentSummary + highlights.

    Ajustado para forzar salida JSON pura (sin prefijos, sin 'SegmentSummary =', sin markdown).
    """
    example = SEGMENT_SUMMARY_SCHEMA_EXAMPLE
    return f"""
Analiza este segmento de pelea de MMA (duración {end_s - start_s}s, índice {segment_index}).
Usa EXCLUSIVAMENTE la tabla proporcionada. Devuelve SOLO un objeto JSON válido que cumpla exactamente las claves y tipos mostrados en el ejemplo.

EJEMPLO (FORMATO / CLAVES / TIPOS) — NO EXPLIQUES, NO ENVUELVAS EN ``` NI TEXTO:
{example}

REGLAS:
1. Empieza la respuesta con '{{' y termina con '}}'. Nada antes ni después.
2. Máximo 5 elementos en "highlights".
3. success_rate = exitos / intentos (si intentos == 0 usar 0.0).
4. Títulos <= 30 caracteres; descripcion <= 90 caracteres.
5. "tipo" ∈ ["offense","defense","oportunidad","riesgo"].
6. timestamps MM:SS relativos al inicio del segmento.
7. Segundos por disciplina: contar segundos predominantes según la tabla (si no aparece, poner 0).
8. Si un dato no está presente: usar 0 o lista vacía; NO inventar.
9. No añadir comentarios, explicaciones, etiquetas extra ni repetir el ejemplo.
10. Asegura que todos los campos existen (aunque vacíos) exactamente con esos nombres.

TABLA DEL SEGMENTO:
{general_analyst_table}
"""


def generate_tactical_coach_structured_prompt(segment_summaries: list) -> str:
    """Prompt para síntesis táctica global en formato TacticalCoachSummary JSON."""
    return f"""
Genera la síntesis táctica global de la pelea usando estos SegmentSummary (JSON list):
{segment_summaries}

Devuelve SOLO un JSON TacticalCoachSummary con este ejemplo de referencia (no añadas explicaciones):
{TACTICAL_COACH_SUMMARY_SCHEMA_EXAMPLE}

Reglas:
- fortalezas_top3, debilidades_top3, ajustes_top3: listas de exactamente 3 ítems cortos.
- recomendacion_tactica: una frase <= 90 caracteres.
- foco_disciplina: disciplina con mayor peso competitivo (ignora Movement si domina por inactividad).
- riesgo_principal y oportunidad_principal: texto corto (<= 70c) derivado de patrones recurrentes.
- No repitas frases idénticas entre listas.
Devuelve solo JSON válido.
"""

__all__ = [
    'generate_general_analyst_prompt',
    'generate_specialist_prompt',
    'generate_head_coach_aggregation_prompt',
    'generate_structured_segment_prompt',
    'generate_tactical_coach_structured_prompt'
]