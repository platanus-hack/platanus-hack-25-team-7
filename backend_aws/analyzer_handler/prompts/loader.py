import os
import boto3
import logging
from botocore.exceptions import ClientError
from typing import Dict

logger = logging.getLogger(__name__)

# Cache for templates to avoid repeated S3 calls
_TEMPLATE_CACHE = {}

def _get_bucket_name() -> str:
    """Get the bucket name from environment variables"""
    bucket = os.getenv("BUCKET_NAME")
    if not bucket:
        raise ValueError("BUCKET_NAME environment variable is not set")
    return bucket

def load_template(template_name: str) -> str:
    """
    Load a template from S3.
    
    Args:
        template_name: Name of the template (without extension)
        
    Returns:
        The content of the template
    """
    if template_name in _TEMPLATE_CACHE:
        return _TEMPLATE_CACHE[template_name]

    bucket_name = _get_bucket_name()
    key = f"prompts/{template_name}.txt"
    
    s3 = boto3.client("s3")
    
    try:
        logger.info(f"Loading template from s3://{bucket_name}/{key}")
        response = s3.get_object(Bucket=bucket_name, Key=key)
        content = response["Body"].read().decode("utf-8")
        _TEMPLATE_CACHE[template_name] = content
        return content
    except ClientError as e:
        logger.error(f"Error loading template {template_name} from s3://{bucket_name}/{key}: {e}")
        raise FileNotFoundError(f"Template {template_name} not found in S3") from e

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