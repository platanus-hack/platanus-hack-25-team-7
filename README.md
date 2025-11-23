# PVHack 2025 — SkillLab

Plataforma y código fuente del proyecto desarrollado para Platanus Hack 2025 (Team 7). Este repositorio contiene la aplicación piloto "SkillLab" para análisis rápido de clips deportivos (30s) y generación de insights técnicos y tácticos.

## Descripción

Aplicación que recibe segmentos de video (30s), extrae keyframes y genera un análisis retroactivo por chunk usando modelos LLM y componentes de visión por computadora. La intención es entregar recomendaciones rápidas y accionables para entrenadores y practicantes no profesionales.

## Objetivos principales

- Extraer 3–7 keyframes por segmento de 30s.
- Identificar errores técnicos, vulnerabilidades defensivas, oportunidades ofensivas y señales de fatiga.
- Generar recomendaciones para la próxima ronda/práctica.

## Características (MVP)

- Captura continua de video en chunks de 30s.
- Extracción ligera de keyframes por chunk.
- Análisis por chunk con LLM (resumen de movimientos + keyframes).
- Agregación de insights al finalizar el video (Top 3 errores, Top 3 ajustes, 1 recomendación táctica).
- Visualización básica: frames anotados, timeline de intensidad, resumen textual.

## Stack tecnológico

- Backend: Python (FastAPI), scripts de procesamiento de video con FFmpeg
- Frontend: React (Vite) — aplicación en `sports-ai-app-frontend/`
- ML/IA: LLMs (integración en `prompts/` y `services/`), modelos de keyframe en `models/`
- Almacenamiento: persiste media en `backend/media/uploads` y `backend/media/splits`
- Infraestructura: Docker (varios Dockerfile en `backend_aws/`, `analyzer_handler/`, `splitter_handler/`)

## Instalación (rápida)

Requisitos: Node 18+, Python 3.10+, pip, ffmpeg (opcional pero recomendado para preprocesamiento).

1. Clonar repositorio

```bash
git clone <repo-url>
cd pvhack-2025
```

1. Instalar dependencias raíz (opcional si no se usa)

```bash
npm install
```

1. Backend (Python)

```bash
cd backend
python -m pip install -r requirements.txt
# luego, para ejecutar el backend en desarrollo
make run-backend
```

1. Frontend

```bash
cd ../sports-ai-app-frontend
npm install
# levantar frontend (Vite)
npm run dev
```

Nota: existen múltiples handlers y funciones para deployment en `backend_aws/` y handlers Dockerizados (ver `backend_aws/`, `analyzer_handler/`, `splitter_handler/`).

## Desarrollo

- El flujo de desarrollo habitual es ejecutar el backend (`make run-backend`) y el frontend (`npm run dev`) en paralelo.
- Los prompts y la lógica que orquesta las llamadas LLM/visión se encuentran en `prompts/`, `services/` y `backend/`.

## Estructura principal del repositorio

```text
.
├── backend/                     # Backend Python, procesamiento de video y API
├── backend_aws/                 # Plantillas y handlers para despliegue en AWS
├── models/                      # Modelos y artefactos ML (keyframe, llm proxies)
├── media/                       # Carpeta para uploads, splits y outputs locales
├── prompts/                     # Templates y loaders para prompts LLM
├── sports-ai-app-frontend/      # Frontend React + Vite
├── notebooks/                   # Notebooks exploratorios y notebooks de workflow
└── README.md                    # Este archivo
```

## Deployment

- Hay Dockerfiles y plantillas para handlers en `backend_aws/`, `analyzer_handler/` y `splitter_handler/`.
- Para despliegues rápidos revise los Dockerfile dentro de cada handler y `backend/Makefile`.

## Cómo contribuir

- Abrir issues para bugs o mejoras.
- Crear branches por feature y hacer PR a `main`.

## Licencia

Proyecto desarrollado para Platanus Hack 2025 — Team 7.

---
Pequeñas notas / supuestos:

- Asumí que el frontend principal está en `sports-ai-app-frontend/` (presente en el workspace).
- Asumí que el `backend/Makefile` expone `make run-backend` para desarrollo (ver contexto previo).

Si quieres, puedo añadir secciones adicionales: ejemplo de API, endpoints principales, o instrucciones para ejecutar los handlers Dockerizados.
