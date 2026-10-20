import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "ResolveAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Gemma API (supports Gemini / Gemma endpoints)
    GEMMA_API_KEY: str = os.getenv("GEMMA_API_KEY", "")
    USE_MOCK_GEMMA_IF_NO_KEY: bool = True
    
    # n8n Webhook Target
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "")
    SIMULATE_N8N_IF_OFFLINE: bool = True
    
    # Hybrid Duplicate Thresholds
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.50
    HYBRID_DUPLICATE_THRESHOLD: float = 0.58

settings = Settings()
