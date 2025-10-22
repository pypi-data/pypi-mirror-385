"""
Config validation con Pydantic per enterprise-grade validation
"""
from typing import Optional, Any, Dict
from pydantic import BaseModel, HttpUrl, Field, field_validator, model_validator
from pathlib import Path


class CrawlConfigSchema(BaseModel):
    """Schema validazione configurazione crawling con Pydantic"""

    # URL e basics
    url: HttpUrl = Field(..., description="URL base da scansionare")
    max_urls: int = Field(default=500, gt=0, le=1000000, description="Numero massimo URL da scansionare")

    # Performance
    concurrency: int = Field(default=20, ge=1, le=100, description="Numero worker concorrenti")
    delay: int = Field(default=0, ge=0, le=10000, description="Delay tra richieste in ms")
    timeout: int = Field(default=15, ge=1, le=300, description="Timeout richieste HTTP in secondi")

    # Auth
    auth_user: Optional[str] = Field(default=None, description="Username HTTP Basic Auth")
    auth_pass: Optional[str] = Field(default=None, description="Password HTTP Basic Auth")

    # Features
    prestashop_mode: bool = Field(default=True, description="Abilita regole specifiche PrestaShop")
    include_subdomains: bool = Field(default=False, description="Include sottodomini nella scansione")
    respect_robots: bool = Field(default=True, description="Rispetta robots.txt")
    resume: bool = Field(default=False, description="Riprendi scansione interrotta")

    # Paths
    project: Optional[str] = Field(default=None, description="Nome progetto")
    output_dir: Optional[Path] = Field(default=None, description="Directory output report")

    # User agent
    user_agent: Optional[str] = Field(
        default=None,
        description="Custom User-Agent string"
    )

    @field_validator('auth_pass')
    @classmethod
    def validate_auth(cls, v: Optional[str], info) -> Optional[str]:
        """Valida che se c'è password ci sia anche username"""
        if v and not info.data.get('auth_user'):
            raise ValueError("auth_pass richiede auth_user")
        return v

    @field_validator('delay')
    @classmethod
    def validate_delay_with_concurrency(cls, v: int, info) -> int:
        """Valida delay in base a concorrenza"""
        concurrency = info.data.get('concurrency', 20)
        if concurrency > 50 and v < 100:
            raise ValueError(
                f"Concurrency alta ({concurrency}) richiede delay >= 100ms per evitare sovraccarico server. "
                f"Delay attuale: {v}ms"
            )
        return v

    @field_validator('timeout')
    @classmethod
    def validate_timeout_reasonable(cls, v: int) -> int:
        """Valida che timeout sia ragionevole"""
        if v < 5:
            raise ValueError("Timeout < 5s troppo basso, può causare molti timeout falsi")
        if v > 60:
            raise ValueError("Timeout > 60s troppo alto, rallenta eccessivamente il crawling")
        return v

    @field_validator('max_urls')
    @classmethod
    def validate_max_urls_reasonable(cls, v: int, info) -> int:
        """Valida max_urls in base a concorrenza"""
        concurrency = info.data.get('concurrency', 20)
        if v > 100000 and concurrency < 10:
            raise ValueError(
                f"Per scansionare {v} URL con concurrency {concurrency} serviranno molte ore. "
                f"Aumentare concurrency o ridurre max_urls"
            )
        return v

    @field_validator('user_agent')
    @classmethod
    def validate_user_agent(cls, v: Optional[str]) -> Optional[str]:
        """Valida user agent"""
        if v and len(v) > 500:
            raise ValueError("User-Agent troppo lungo (max 500 caratteri)")
        return v

    @model_validator(mode='after')
    def validate_memory_requirements(self) -> 'CrawlConfigSchema':
        """Valida che la configurazione non richieda troppa memoria"""
        max_urls = self.max_urls
        concurrency = self.concurrency

        # Stima memoria: ~50KB per URL in coda + ~100KB per worker
        estimated_memory_mb = (max_urls * 0.05) + (concurrency * 0.1)

        if estimated_memory_mb > 1000:  # > 1GB
            raise ValueError(
                f"Configurazione richiede ~{estimated_memory_mb:.0f}MB memoria. "
                f"Ridurre max_urls o concurrency per evitare MemoryError"
            )

        return self

    class Config:
        """Configurazione Pydantic"""
        arbitrary_types_allowed = True
        validate_assignment = True


def validate_crawl_config(config_dict: dict) -> CrawlConfigSchema:
    """
    Valida configurazione crawl con Pydantic

    Args:
        config_dict: Dictionary con configurazione

    Returns:
        CrawlConfigSchema validato

    Raises:
        pydantic.ValidationError: Se validazione fallisce
    """
    return CrawlConfigSchema(**config_dict)


# Export per backward compatibility
__all__ = ['CrawlConfigSchema', 'validate_crawl_config']
