import os
import time
import logging
from google import genai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
        
        # Use environment variable for model, default to gemini-2.5-pro
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        
        self.roles = {
            "striking": {
                "name": "Striking Offense/Defense Analyst",
                "desc": "Análisis enfocado en el intercambio de golpes de pie (Boxeo y Muay Thai).",
                "emphasis": "**posicionamiento** (footwork, ángulo de ataque) y la **conexión efectiva** de golpes.",
                "actions": "Jab/Cross Conectado, Patada (al cuerpo, pierna, cabeza), Knockdown, KO/TKO, Esquive Exitoso, Uso de Finta.",
                "example": """| Tiempo (MM:SS) | Peleador | Acción |
                            | :---: | :---: | :--- |
                            | 00:00 | Burns | Cross Conectado |
                            | 00:01 | Ambos | Intercambio de distancia |
                            | 00:02 | Chimaev | Jab Conectado |
                            | 00:03 | Ambos | Posicionamiento |
                            | 00:04 | Ambos | Reset a centro |
                            | 00:05 | Burns | Patada a pierna conectada |"""
            },
            "grappling": {
                "name": "Grappling Analyst",
                "desc": "Análisis enfocado en el clinch, controles contra la jaula, derribos y trabajo de piso.",
                "emphasis": "**control posicional**, **pases de guardia**, **derribos**, y **defensa de derribo**.",
                "actions": "Takedown efectivo, Defensa de takedown, Control en clinch, Pase de guardia, Ground and pound.",
                "example": """| Tiempo (MM:SS) | Peleador | Acción |
                                | :---: | :---: | :--- |
                                | 00:00 | Ambos | Clinch sin actividad |
                                | 00:01 | Chimaev | Takedown conseguido |
                                | 00:02 | Burns | Intenta defensa de takedown |
                                | 00:03 | Chimaev | Control en suelo |
                                | 00:04 | Ambos | Sin actividad relevante |
                                | 00:05 | Chimaev | Ground and pound |"""
            },
            "submission": {
                "name": "Submission Specialist",
                "desc": "Análisis enfocado en intentos de sumisión, transiciones y defensa.",
                "emphasis": "**intentos de sumisión**, **transiciones entre posiciones**, **escapes**.",
                "actions": "Intento de estrangulación, Intento de palanca, Escape de sumisión, Defensa de sumisión.",
                "example": """| Tiempo (MM:SS) | Peleador | Acción |
                                | :---: | :---: | :--- |
                                | 00:00 | Ambos | Evaluación posicional |
                                | 00:01 | Chimaev | Intento de estrangulación |
                                | 00:02 | Burns | Defensa activa de sumisión |
                                | 00:03 | Burns | Escape |
                                | 00:04 | Chimaev | Cambio a otra sumisión |
                                | 00:05 | Ambos | Sin actividad |"""
            },
            "analista_tactico": {
                "name": "Analista Táctico Integral",
                "desc": "Análisis estratégico de la pelea incluyendo toma de decisiones, estrategia, manejo del tiempo y espacio.",
                "emphasis": "**táctica general**, **patrones de comportamiento**, **ajustes de estrategia**, **lectura del oponente**.",
                "actions": "Cambio de guardia, Presión en jaula, Ajuste de distancia, Cambio de ritmo, Estrategia defensiva.",
                "example": """| Tiempo (MM:SS) | Peleador | Acción |
                                | :---: | :---: | :--- |
                                | 00:00 | Ambos | Estudio de rival |
                                | 00:01 | Burns | Ajusta distancia |
                                | 00:02 | Chimaev | Presiona en jaula |
                                | 00:03 | Ambos | Cambio de guardia |
                                | 00:04 | Ambos | Manejo del ritmo |
                                | 00:05 | Ambos | Sin actividad táctica relevante |"""
            }
        }

    def generate_coach_prompt(self, role="striking"):
        role_key = role.lower()
        if role_key == "analista":
            role_key = "analista_tactico"
        
        if role_key not in self.roles:
            raise ValueError(f"Rol '{role}' no soportado. Opciones: {list(self.roles.keys())}")

        r = self.roles[role_key]
        
        with open(os.path.join(self.prompts_dir, "coach_prompt_template.txt"), "r") as f:
            template = f.read()
            
        return template.format(
            role_name=r['name'],
            role_desc=r['desc'],
            role_emphasis=r['emphasis'],
            role_actions=r['actions'],
            role_example=r['example']
        )

    def generate_general_analyst_prompt(self):
        with open(os.path.join(self.prompts_dir, "general_analyst_prompt.txt"), "r") as f:
            return f.read()

    def upload_file(self, file_path, max_retries=3):
        """Upload file to Gemini with retry logic and timeout"""
        for attempt in range(max_retries):
            try:
                logger.info(f"[{datetime.now().isoformat()}] Uploading file (attempt {attempt + 1}/{max_retries}): {file_path}")
                myfile = self.client.files.upload(file=file_path)
                
                # Poll for processing completion with 2-minute timeout
                start_time = time.time()
                timeout = 120  # 2 minutes
                
                while myfile.state.name == "PROCESSING":
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        raise TimeoutError(f"File processing timeout after {timeout}s")
                    
                    logger.info(f"Processing video... ({int(elapsed)}s elapsed)")
                    time.sleep(5)
                    myfile = self.client.files.get(name=myfile.name)
                    
                if myfile.state.name == "FAILED":
                    raise ValueError(f"File processing failed: {myfile.state.name}")
                    
                logger.info(f"[{datetime.now().isoformat()}] File uploaded and processed: {myfile.name}")
                return myfile
                
            except Exception as e:
                logger.error(f"Upload attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e

    def analyze_chunk(self, file_path):
        """Analyze chunk with sequential LLM calls and delay between calls"""
        if not self.client:
            raise ValueError("GEMINI_API_KEY not set or client initialization failed")

        try:
            myfile = self.upload_file(file_path)
            
            results = {}
            
            # General Analyst
            logger.info(f"[{datetime.now().isoformat()}] Running General Analyst...")
            prompt_general = self.generate_general_analyst_prompt()
            response_general = self.client.models.generate_content(
                model=self.model, 
                contents=[myfile, prompt_general],
                config={"temperature": 0.0, "topP": 0.95, "seed": 42}
            )
            results["general_analyst"] = response_general.text
            logger.info(f"[{datetime.now().isoformat()}] General Analyst completed")
            
            # Delay between LLM calls to avoid rate limits
            time.sleep(5)
            
            # Specialist Roles (sequential)
            for role in ["striking", "grappling", "submission"]:
                logger.info(f"[{datetime.now().isoformat()}] Running {role} analysis...")
                prompt = self.generate_coach_prompt(role=role)
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[myfile, prompt],
                    config={"temperature": 0.0, "topP": 0.95, "seed": 42}
                )
                results[role] = response.text
                logger.info(f"[{datetime.now().isoformat()}] {role} analysis completed")
                
                # Delay between specialist analyses
                time.sleep(5)
                
            return results
            
        except Exception as e:
            logger.error(f"[{datetime.now().isoformat()}] Error in analyze_chunk: {e}")
            raise e

llm_service = LLMService()
