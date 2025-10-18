from pydantic import BaseModel, Field
from typing import Literal, Optional
from ..agents import AgentUpdateFields

class AgentsCreateRequest(BaseModel):
    name: str = Field(..., description="Nome do agente")
    type: Literal["human", "ai"] = Field(..., description="Tipo do agente: 'human' para agentes humanos, 'ai' para agentes de IA")
    assistant_id: Optional[str] = Field(None, description="ID do assistente (obrigatório para agentes de IA)")
    profile_id: Optional[str] = Field(None, description="ID do perfil (obrigatório para agentes humanos)")

class AgentsUpdateRequest(BaseModel):
    fields: AgentUpdateFields = Field(..., description="Campos a serem atualizados no agente")

class AgentsSearchRequest(BaseModel):
    type: Optional[Literal["human", "ai"]] = Field(None, description="Filtrar por tipo de agente")
    assistant_id: Optional[str] = Field(None, description="Filtrar por ID do assistente")
    profile_id: Optional[str] = Field(None, description="Filtrar por ID do perfil")
    limit: Optional[int] = Field(None, description="Limite máximo de registros retornados")
    offset: Optional[int] = Field(None, description="Número de registros a pular")
