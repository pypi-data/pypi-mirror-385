"""
Memory system interfaces and providers.

This module provides memory management capabilities for AI workflows,
including persistent storage, caching, and context management.

Conversation Memory (Week 2 Phase 1):
- KaizenMemory: Abstract base for conversation memory
- BufferMemory: Full conversation history storage
- SummaryMemory: LLM-generated summaries with recent verbatim
- VectorMemory: Semantic search over conversation
- KnowledgeGraphMemory: Entity extraction and relationships

Shared Memory (Week 3 Phase 2):
- SharedMemoryPool: Shared insight storage for multi-agent collaboration
"""

from .buffer import BufferMemory

# Conversation memory (Week 2 Phase 1)
from .conversation_base import KaizenMemory
from .enterprise import EnterpriseMemorySystem, MemoryMonitor, MemorySystemConfig
from .knowledge_graph import KnowledgeGraphMemory
from .persistent_tiers import ColdMemoryTier, WarmMemoryTier

# Shared memory (Week 3 Phase 2)
from .shared_memory import SharedMemoryPool
from .summary import SummaryMemory
from .tiers import HotMemoryTier, MemoryTier, TierManager
from .vector import VectorMemory

__all__ = [
    # Tiered memory (existing)
    "MemoryTier",
    "HotMemoryTier",
    "WarmMemoryTier",
    "ColdMemoryTier",
    "TierManager",
    "EnterpriseMemorySystem",
    "MemorySystemConfig",
    "MemoryMonitor",
    # Individual conversation memory (Phase 1)
    "KaizenMemory",
    "BufferMemory",
    "SummaryMemory",
    "VectorMemory",
    "KnowledgeGraphMemory",
    # Shared memory (Phase 2)
    "SharedMemoryPool",
]
