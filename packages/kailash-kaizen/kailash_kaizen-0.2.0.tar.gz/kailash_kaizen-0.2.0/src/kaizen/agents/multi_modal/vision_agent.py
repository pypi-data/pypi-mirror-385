"""Vision processing agent for Kaizen."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

from kaizen.core.base_agent import BaseAgent
from kaizen.providers.ollama_vision_provider import (
    OllamaVisionConfig,
    OllamaVisionProvider,
)
from kaizen.signatures import InputField, OutputField, Signature
from kaizen.signatures.multi_modal import ImageField, MultiModalSignature

from kailash.nodes.base import NodeMetadata, register_node


class VisionQASignature(MultiModalSignature, Signature):
    """Signature for visual question answering."""

    image: ImageField = InputField(description="Image to analyze")
    question: str = InputField(description="Question about the image")
    answer: str = OutputField(description="Answer based on image analysis")
    confidence: float = OutputField(description="Confidence score (0-1)", default=0.0)


class ImageDescriptionSignature(MultiModalSignature, Signature):
    """Signature for image description generation."""

    image: ImageField = InputField(description="Image to describe")
    description: str = OutputField(description="Detailed image description")


@dataclass
class VisionAgentConfig:
    """Configuration for VisionAgent."""

    llm_provider: str = "ollama"
    model: str = "llava:13b"
    temperature: float = 0.7
    max_images: int = 5
    auto_resize: bool = True


@register_node()
class VisionAgent(BaseAgent):
    """
    Vision processing agent using Ollama vision models.

    Capabilities:
    - Image classification and description
    - Visual question answering
    - Object detection and counting
    - Text extraction (OCR)
    - Multi-image analysis

    Uses llava:13b or bakllava via Ollama.

    Example:
        config = VisionAgentConfig()
        agent = VisionAgent(config)

        result = agent.analyze(
            image="photo.jpg",
            question="What objects are in this image?"
        )
        print(result["answer"])
    """

    # Node metadata for Studio discovery
    metadata = NodeMetadata(
        name="VisionAgent",
        description="Multi-modal vision agent for image analysis, OCR, and visual Q&A",
        version="1.0.0",
        tags={"ai", "kaizen", "vision", "multi-modal", "image", "ocr"},
    )

    def __init__(self, config: VisionAgentConfig, **kwargs):
        """Initialize vision agent."""
        # Convert to BaseAgentConfig
        base_config = type(
            "BaseAgentConfig",
            (),
            {
                "llm_provider": config.llm_provider,
                "model": config.model,
                "temperature": config.temperature,
            },
        )()

        # Initialize with vision signature
        super().__init__(config=base_config, signature=VisionQASignature(), **kwargs)

        # Create vision provider
        self.vision_provider = OllamaVisionProvider(
            config=OllamaVisionConfig(
                model=config.model,
                temperature=config.temperature,
                max_images=config.max_images,
            )
        )

        self.config = config

    def analyze(
        self,
        image: Union[ImageField, str, Path],
        question: str,
        store_in_memory: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze image and answer question.

        Args:
            image: Image to analyze
            question: Question about the image
            store_in_memory: Store result in agent memory

        Returns:
            Dict with 'answer' and 'confidence' keys
        """
        # Use vision provider
        response = self.vision_provider.answer_visual_question(
            image=image, question=question
        )

        result = {
            "answer": response,
            "confidence": 0.85,  # Would need actual confidence from model
            "model": self.config.model,
            "question": question,
        }

        # Store in memory if requested
        if store_in_memory and hasattr(self, "write_to_memory"):
            self.write_to_memory(
                content=result, tags=["vision", "analysis"], importance=0.8
            )

        return result

    def describe(
        self, image: Union[ImageField, str, Path], detail: str = "auto"
    ) -> str:
        """
        Generate description of image.

        Args:
            image: Image to describe
            detail: Detail level (brief, detailed, auto)

        Returns:
            Image description
        """
        return self.vision_provider.describe_image(image=image, detail=detail)

    def extract_text(self, image: Union[ImageField, str, Path]) -> str:
        """
        Extract text from image (OCR).

        Args:
            image: Image containing text

        Returns:
            Extracted text
        """
        return self.vision_provider.extract_text(image)

    def batch_analyze(
        self, images: List[Union[ImageField, str, Path]], question: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple images with same question.

        Args:
            images: List of images to analyze
            question: Question to ask about each image

        Returns:
            List of analysis results
        """
        results = []

        for image in images:
            result = self.analyze(image, question, store_in_memory=False)
            results.append(result)

        return results
