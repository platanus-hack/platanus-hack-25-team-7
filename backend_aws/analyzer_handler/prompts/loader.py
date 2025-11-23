import os
from pathlib import Path
from typing import Dict

def _get_templates_dir() -> Path:
    """Obtiene la ruta del directorio de templates"""
    return Path(__file__).parent / "templates"

def load_template(template_name: str) -> str:
    """Carga un template desde archivo"""
    template_path = _get_templates_dir() / f"{template_name}.txt"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")

def generate_general_analyst_prompt() -> str:
    """Genera el prompt del analista general"""
    return load_template("general_analyst")

def generate_specialist_prompt(role: str, general_analysis_text: str) -> str:
    """
    Genera el prompt de un especialista con variables reemplazadas.
    
    Args:
        role: "striking", "grappling", "submission", o "movement"
        general_analysis_text: El texto del análisis general
    
    Returns:
        El prompt completo con todas las variables reemplazadas
    """
    roles = {
        "striking": {
            "name": "Striking Offense/Defense Analyst",
            "desc": "Análisis enfocado en el intercambio de golpes de pie (Boxeo y Muay Thai).",
            "emphasis": "**posicionamiento** (footwork, ángulo de ataque) y la **conexión efectiva** de golpes.",
            "actions": "Jab/Cross Conectado, Patada (al cuerpo, pierna, cabeza), Knockdown, KO/TKO, Esquive Exitoso, Uso de Finta."
        },
        "grappling": {
            "name": "Grappling Analyst",
            "desc": "Análisis enfocado en el clinch, controles contra la jaula, derribos y trabajo de piso.",
            "emphasis": "**control posicional**, **pases de guardia**, **derribos**, y **defensa de derribo**.",
            "actions": "Takedown efectivo, Defensa de takedown, Control en clinch, Pase de guardia, Ground and pound."
        },
        "submission": {
            "name": "Submission Specialist",
            "desc": "Análisis enfocado en intentos de sumisión, transiciones y defensa.",
            "emphasis": "**intentos de sumisión**, **transiciones entre posiciones**, **escapes**.",
            "actions": "Intento de estrangulación, Intento de palanca, Escape de sumisión, Defensa de sumisión."
        },
        "movement": {
            "name": "Movement Specialist",
            "desc": "Análisis enfocado en footwork, posicionamiento, manejo de distancia y ángulos.",
            "emphasis": "**footwork**, **posicionamiento**, **manejo de distancia**, **cambios de ángulo**.",
            "actions": "Cierre de distancia, Ajuste de ángulo, Footwork defensivo, Manejo de espacio, Cambio de guardia."
        }
    }
    
    role_key = role.lower()
    if role_key not in roles:
        raise ValueError(f"Rol '{role}' no soportado. Opciones: {list(roles.keys())}")
    
    # Cargar el template base
    template = load_template("specialist_base_prompt")
    
    # Obtener datos del rol
    role_data = roles[role_key]
    
    # Reemplazar todas las variables
    replacements = {
        "{role_name}": role_data["name"],
        "{role_desc}": role_data["desc"],
        "{role_emphasis}": role_data["emphasis"],
        "{role_actions}": role_data["actions"],
        "{general_analysis_text}": general_analysis_text
    }
    
    prompt = template
    for placeholder, value in replacements.items():
        prompt = prompt.replace(placeholder, value)
    
    return prompt

def generate_head_coach_aggregation_prompt(specialist_analyses: Dict[str, str]) -> str:
    """
    Genera un prompt conciso para el Head Coach que agrega todos los análisis.
    
    Args:
        specialist_analyses: Diccionario con los análisis de cada especialista
            Ejemplo: {"striking": "...", "grappling": "...", ...}
    
    Returns:
        El prompt completo con los análisis de especialistas incluidos
    """
    # Formatear los análisis de especialistas
    specialist_text = "\n\n".join([
        f"**{role.upper()}:**\n{analysis}" 
        for role, analysis in specialist_analyses.items()
    ])
    
    # Cargar el template
    template = load_template("head_coach_aggregation")
    
    # Reemplazar la variable
    prompt = template.replace("{specialist_text}", specialist_text)
    
    return prompt