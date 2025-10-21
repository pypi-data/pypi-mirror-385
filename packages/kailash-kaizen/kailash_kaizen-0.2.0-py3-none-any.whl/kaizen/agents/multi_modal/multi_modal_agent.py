"""
Multi-Modal Agent - Unified agent for vision, audio, and text processing.

Combines:
- Vision processing (Ollama llava, OpenAI GPT-4V)
- Audio processing (Local Whisper, OpenAI Whisper)
- Text processing (existing LLM providers)

Extends BaseAgent with multi-modal capabilities.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from kaizen.core.base_agent import BaseAgent, BaseAgentConfig
from kaizen.cost.tracker import CostTracker
from kaizen.memory.shared_memory import SharedMemoryPool
from kaizen.providers.multi_modal_adapter import (
    MultiModalAdapter,
    get_multi_modal_adapter,
)
from kaizen.signatures.multi_modal import AudioField, ImageField, MultiModalSignature

from kailash.nodes.base import NodeMetadata, register_node


@dataclass
class MultiModalConfig(BaseAgentConfig):
    """Configuration for MultiModalAgent."""

    # Provider settings
    prefer_local: bool = True  # Prefer Ollama over OpenAI
    auto_download_models: bool = True  # Auto-download Ollama models

    # Cost tracking
    enable_cost_tracking: bool = True
    warn_on_openai_usage: bool = True
    budget_limit: Optional[float] = None

    # Multi-modal specific
    vision_model: Optional[str] = None  # e.g., "llava:13b"
    audio_model: Optional[str] = None  # e.g., "base" for Whisper


@register_node()
class MultiModalAgent(BaseAgent):
    """
    Multi-modal agent combining vision, audio, and text processing.

    Extends BaseAgent to support:
    - ImageField inputs (auto-processed)
    - AudioField inputs (auto-processed)
    - Mixed modality workflows
    - Cost tracking
    - Provider abstraction (Ollama/OpenAI)
    """

    # Node metadata for Studio discovery
    metadata = NodeMetadata(
        name="MultiModalAgent",
        description="Unified multi-modal agent for vision, audio, and text processing with cost tracking",
        version="1.0.0",
        tags={
            "ai",
            "kaizen",
            "multi-modal",
            "vision",
            "audio",
            "unified",
            "cost-tracking",
        },
    )

    def __init__(
        self,
        config: MultiModalConfig,
        signature: MultiModalSignature,
        adapter: Optional[MultiModalAdapter] = None,
        cost_tracker: Optional[CostTracker] = None,
        shared_memory: Optional[SharedMemoryPool] = None,
        agent_id: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize multi-modal agent.

        Args:
            config: MultiModalConfig
            signature: MultiModalSignature defining inputs/outputs
            adapter: Optional MultiModalAdapter (auto-selected if None)
            cost_tracker: Optional CostTracker
            shared_memory: Optional SharedMemoryPool
            agent_id: Optional agent ID
        """
        # Initialize base agent
        super().__init__(
            config=config,
            signature=signature,
            shared_memory=shared_memory,
            agent_id=agent_id,
            **kwargs,
        )

        self.config: MultiModalConfig = config

        # Get or create adapter
        if adapter is None:
            try:
                self.adapter = get_multi_modal_adapter(
                    prefer_local=config.prefer_local,
                    model=config.vision_model or "llava:13b",
                    whisper_model=config.audio_model or "base",
                    auto_download=config.auto_download_models,
                )
            except ValueError as e:
                raise ValueError(f"No multi-modal adapter available: {e}")
        else:
            self.adapter = adapter

        # Verify adapter supports required modalities
        self._verify_adapter_compatibility()

        # Cost tracking
        self.cost_tracker = cost_tracker
        if self.cost_tracker is None and config.enable_cost_tracking:
            self.cost_tracker = CostTracker(
                budget_limit=config.budget_limit,
                warn_on_openai_usage=config.warn_on_openai_usage,
            )

    def _verify_adapter_compatibility(self):
        """Verify adapter supports signature's modalities."""
        # Check which modalities are in signature
        has_image = any(
            isinstance(getattr(self.signature, field, None), ImageField)
            for field in dir(self.signature)
        )
        has_audio = any(
            isinstance(getattr(self.signature, field, None), AudioField)
            for field in dir(self.signature)
        )

        # Verify support
        if has_image and not self.adapter.supports_vision():
            raise ValueError("Adapter does not support vision processing")

        if has_audio and not self.adapter.supports_audio():
            raise ValueError("Adapter does not support audio processing")

    def analyze(self, store_in_memory: bool = False, **inputs) -> Dict[str, Any]:
        """
        Analyze multi-modal inputs.

        Args:
            store_in_memory: Store in shared memory
            **inputs: Multi-modal inputs matching signature

        Returns:
            Dict with analysis results
        """
        # Extract modalities from inputs
        image_input = None
        audio_input = None
        text_input = None
        prompt = None

        for key, value in inputs.items():
            if isinstance(value, (ImageField, Path)) or (
                isinstance(value, str)
                and any(
                    value.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp"]
                )
            ):
                image_input = value
            elif isinstance(value, (AudioField, Path)) or (
                isinstance(value, str)
                and any(value.endswith(ext) for ext in [".wav", ".mp3", ".m4a", ".ogg"])
            ):
                audio_input = value
            elif isinstance(value, str):
                # Could be text or prompt
                if key in ["prompt", "query", "question"]:
                    prompt = value
                else:
                    text_input = value

        # Estimate cost if tracking enabled
        if self.cost_tracker:
            provider = "ollama" if self.config.prefer_local else "openai"
            modality = (
                "mixed"
                if (image_input and audio_input)
                else ("vision" if image_input else "audio" if audio_input else "text")
            )
            estimated_cost = self.cost_tracker.estimate_cost(
                provider=provider, modality=modality
            )
            self.cost_tracker.check_before_call(provider, estimated_cost)

        # Process with adapter
        result = self.adapter.process_multi_modal(
            image=image_input, audio=audio_input, text=text_input, prompt=prompt
        )

        # Record usage
        if self.cost_tracker:
            provider = "ollama" if self.config.prefer_local else "openai"
            self.cost_tracker.record_usage(
                provider=provider,
                modality=modality,
                model=self.config.model,
                cost=estimated_cost if provider == "openai" else 0.0,
            )

        # Store in memory if requested
        if store_in_memory and self.shared_memory:
            self.write_to_memory(
                content={
                    "inputs": {k: str(v) for k, v in inputs.items()},
                    "result": result,
                },
                tags=["multi_modal", modality],
                importance=0.8,
            )

        return result

    def batch_analyze(
        self,
        images: Optional[List[Union[str, Path, ImageField]]] = None,
        audios: Optional[List[Union[str, Path, AudioField]]] = None,
        texts: Optional[List[str]] = None,
        questions: Optional[List[str]] = None,
        store_in_memory: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Batch process multiple inputs.

        Args:
            images: List of images
            audios: List of audio files
            texts: List of text inputs
            questions: List of questions/prompts
            store_in_memory: Store results in memory

        Returns:
            List of results
        """
        results = []

        # Determine batch size
        batch_size = max(
            len(images) if images else 0,
            len(audios) if audios else 0,
            len(texts) if texts else 0,
            len(questions) if questions else 0,
        )

        for i in range(batch_size):
            inputs = {}

            if images and i < len(images):
                inputs["image"] = images[i]
            if audios and i < len(audios):
                inputs["audio"] = audios[i]
            if texts and i < len(texts):
                inputs["text"] = texts[i]
            if questions and i < len(questions):
                inputs["question"] = questions[i]

            result = self.analyze(store_in_memory=store_in_memory, **inputs)
            results.append(result)

        return results

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary."""
        if not self.cost_tracker:
            return {"enabled": False}

        return {
            "enabled": True,
            "stats": self.cost_tracker.get_usage_stats(),
            "by_provider": self.cost_tracker.get_usage_by_provider(),
            "by_modality": self.cost_tracker.get_usage_by_modality(),
            "budget": {
                "limit": self.cost_tracker.budget_limit,
                "used": self.cost_tracker.get_total_cost(),
                "remaining": self.cost_tracker.get_budget_remaining(),
                "percentage": self.cost_tracker.get_budget_percentage(),
            },
            "savings": {
                "actual_cost": self.cost_tracker.get_total_cost(),
                "openai_equivalent": self.cost_tracker.estimate_openai_equivalent_cost(),
                "saved": self.cost_tracker.estimate_openai_equivalent_cost()
                - self.cost_tracker.get_total_cost(),
            },
        }
