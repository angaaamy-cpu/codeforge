"""
CodeForge Model Provider - Agent OS
===================================
إدارة مزودي LLM
"""

from src.model_provider.base import BaseProvider, ProviderConfig
from src.model_provider.registry import ProviderRegistry, provider_registry, has_llm_provider, generate, set_provider
from src.model_provider.capability_requirements import (
    CapabilityRequirement,
    CapabilityRequirementsRegistry,
    capability_requirements,
)
from src.model_provider.mock_provider import MockProvider, mock_provider

__all__ = [
    # Base
    "BaseProvider",
    "ProviderConfig",
    # Registry
    "ProviderRegistry",
    "provider_registry",
    "has_llm_provider",
    "generate",
    "set_provider",
    # Requirements
    "CapabilityRequirement",
    "CapabilityRequirementsRegistry",
    "capability_requirements",
    # Mock
    "MockProvider",
    "mock_provider",
]
