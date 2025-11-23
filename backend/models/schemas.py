from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class UploadResponse(BaseModel):
    job_id: str
    message: str
    status: str

class SplitProgress(BaseModel):
    job_id: str
    split_status: str
    total_chunks: int
    completed_chunks: int
    split_pct: float
    chunks: List[str] = []

class ChunkAnalysis(BaseModel):
    chunk_index: int
    chunk_filename: str
    status: str  # "pending", "processing", "completed", "failed", "timeout"
    general_analyst: Optional[str] = None
    striking: Optional[str] = None
    grappling: Optional[str] = None
    submission: Optional[str] = None
    head_coach: Optional[str] = None
    error: Optional[str] = None

class AnalysisProgress(BaseModel):
    job_id: str
    split_status: str
    analysis_status: str  # "pending", "processing", "completed", "partial", "failed"
    total_chunks: int
    analyzed_chunks: int
    analysis_pct: float
    chunk_analyses: List[ChunkAnalysis] = []

# Coach Response - To be Used Later

class Disciplina(str, Enum):
    STRIKING = "Striking"
    GRAPPLING = "Grappling"
    SUBMISSION = "Submission"
    MOVEMENT = "Movement"

class Impacto(str, Enum):
    MAXIMO = "MÁXIMO"
    SIGNIFICATIVO = "SIGNIFICATIVO"
    MODERADO = "MODERADO"
    BAJO = "BAJO"

class MomentoCritico(BaseModel):
    """Representa un momento crítico identificado en la pelea"""
    timestamp: str = Field(..., description="Timestamp en formato MM:SS o rango MM:SS - MM:SS")
    descripcion: str = Field(..., description="Descripción detallada del momento")
    disciplina: Disciplina = Field(..., description="Disciplina más relevante")
    impacto: Impacto = Field(..., description="Nivel de impacto del momento")

class PerfilPeleador(BaseModel):
    """Perfil de rendimiento de un peleador"""
    nombre: str = Field(..., description="Nombre del peleador")
    fortalezas: List[str] = Field(default_factory=list, description="Lista de fortalezas principales")
    debilidades: List[str] = Field(default_factory=list, description="Lista de debilidades críticas")
    patrones: List[str] = Field(default_factory=list, description="Patrones de comportamiento identificados")

class ReporteEjecutivo(BaseModel):
    """Reporte ejecutivo completo del Head Coach"""
    momentos_criticos: List[MomentoCritico] = Field(
        default_factory=list,
        description="Momentos críticos ordenados por importancia"
    )
    perfil_peleador_a: Optional[PerfilPeleador] = Field(
        None,
        description="Perfil del primer peleador"
    )
    perfil_peleador_b: Optional[PerfilPeleador] = Field(
        None,
        description="Perfil del segundo peleador"
    )
    insights_estrategicos: Optional[List[str]] = Field(
        default_factory=list,
        description="Insights estratégicos y recomendaciones"
    )

# -------------------------------------------------------------
# Modelos estructurados simples para dashboard (tres modelos)
# -------------------------------------------------------------

class MomentType(str, Enum):
    OFFENSE = "offense"
    DEFENSE = "defense"
    OPORTUNIDAD = "oportunidad"
    RIESGO = "riesgo"

class MomentHighlight(BaseModel):
    """Momento clave compacto para tarjeta de UI"""
    timestamp: str = Field(..., description="Marca MM:SS del momento")
    titulo: str = Field(..., description="Título corto (<=30c)")
    descripcion: str = Field(..., description="Descripción breve (<=90c)")
    tipo: MomentType = Field(..., description="Tipo para iconografía")
    disciplina: Disciplina = Field(..., description="Disciplina asociada")
    impacto: int = Field(..., ge=1, le=5, description="Impacto ordinal 1–5")

class SegmentSummary(BaseModel):
    """Resumen numérico y momentos de un segmento (30s)."""
    segment_index: int = Field(..., description="Índice del segmento (0-based)")
    start_s: int = Field(..., description="Segundo inicial absoluto del segmento")
    end_s: int = Field(..., description="Segundo final absoluto del segmento")
    acciones_total: int = Field(..., description="Acciones registradas en el segmento")
    acciones_min: float = Field(..., description="Ritmo (acciones por minuto)")
    intentos: int = Field(..., description="Intentos ofensivos totales")
    exitos: int = Field(..., description="Intentos con éxito")
    success_rate: float = Field(..., description="exitos / intentos (0-1)")
    striking_s: int = Field(0, description="Segundos con Striking predominante")
    grappling_s: int = Field(0, description="Segundos con Grappling predominante")
    submission_s: int = Field(0, description="Segundos con Submission activa")
    movement_s: int = Field(0, description="Segundos con Movement predominante")
    movement_ratio: float = Field(0, description="movement_s / duración segmento")
    clinch_control_s: int = Field(0, description="Segundos de control en clinch")
    submission_threat_s: int = Field(0, description="Segundos con amenaza de sumisión")
    highlights: List[MomentHighlight] = Field(default_factory=list, description="Momentos clave (máx 5)")

class TacticalCoachSummary(BaseModel):
    """Síntesis táctica global tras procesar todos los segmentos."""
    fortalezas_top3: List[str] = Field(default_factory=list, description="Fortalezas principales")
    debilidades_top3: List[str] = Field(default_factory=list, description="Debilidades principales")
    ajustes_top3: List[str] = Field(default_factory=list, description="Ajustes recomendados inmediatos")
    recomendacion_tactica: str = Field("", description="Recomendación táctica única y concreta")
    foco_disciplina: Optional[Disciplina] = Field(None, description="Disciplina de mayor relevancia competitiva")
    riesgo_principal: Optional[str] = Field(None, description="Riesgo más crítico identificado")
    oportunidad_principal: Optional[str] = Field(None, description="Mayor oportunidad explotable")