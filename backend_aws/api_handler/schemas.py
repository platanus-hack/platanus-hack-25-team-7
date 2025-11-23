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
