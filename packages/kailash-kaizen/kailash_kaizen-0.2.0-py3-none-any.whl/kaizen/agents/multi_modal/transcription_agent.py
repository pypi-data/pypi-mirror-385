"""Audio transcription agent for Kaizen."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from kaizen.audio.whisper_processor import WhisperConfig, WhisperProcessor
from kaizen.core.base_agent import BaseAgent
from kaizen.signatures import InputField, OutputField, Signature
from kaizen.signatures.multi_modal import AudioField

from kailash.nodes.base import NodeMetadata, register_node


class TranscriptionSignature(Signature):
    """Signature for audio transcription."""

    audio: AudioField = InputField(description="Audio file to transcribe")
    language: str = InputField(description="Language hint (optional)", default=None)
    text: str = OutputField(description="Transcribed text")
    confidence: float = OutputField(
        description="Transcription confidence (0-1)", default=0.0
    )


@dataclass
class TranscriptionAgentConfig:
    """Configuration for TranscriptionAgent."""

    model_size: str = "base"  # Whisper model size
    device: str = "cpu"
    compute_type: str = "int8"
    language: Optional[str] = None
    word_timestamps: bool = True


@register_node()
class TranscriptionAgent(BaseAgent):
    """
    Audio transcription agent using local Whisper.

    Capabilities:
    - Speech-to-text transcription
    - Multi-language support (99+ languages)
    - Word-level timestamps
    - Language detection
    - Translation to English
    - Batch processing

    Uses faster-whisper for efficient transcription.

    Example:
        config = TranscriptionAgentConfig(model_size="base")
        agent = TranscriptionAgent(config)

        result = agent.transcribe("meeting.mp3")
        print(result["text"])
    """

    # Node metadata for Studio discovery
    metadata = NodeMetadata(
        name="TranscriptionAgent",
        description="Multi-modal audio transcription agent with multi-language support using Whisper",
        version="1.0.0",
        tags={
            "ai",
            "kaizen",
            "audio",
            "transcription",
            "whisper",
            "speech-to-text",
            "multi-modal",
        },
    )

    def __init__(self, config: TranscriptionAgentConfig, **kwargs):
        """Initialize transcription agent."""
        # Convert to BaseAgentConfig
        base_config = type(
            "BaseAgentConfig",
            (),
            {"llm_provider": "whisper", "model": config.model_size, "temperature": 0.0},
        )()

        # Initialize with transcription signature
        super().__init__(
            config=base_config, signature=TranscriptionSignature(), **kwargs
        )

        # Create Whisper processor
        self.processor = WhisperProcessor(
            config=WhisperConfig(
                model_size=config.model_size,
                device=config.device,
                compute_type=config.compute_type,
                language=config.language,
            )
        )

        self.config = config

    def transcribe(
        self,
        audio: Union[AudioField, str, Path],
        language: Optional[str] = None,
        store_in_memory: bool = True,
    ) -> Dict[str, Any]:
        """
        Transcribe audio file.

        Args:
            audio: Audio file to transcribe
            language: Language hint (optional)
            store_in_memory: Store result in agent memory

        Returns:
            Dict with 'text', 'segments', 'language', 'duration'
        """
        # Convert to path if AudioField
        if isinstance(audio, AudioField):
            # Would need to save audio data to temp file
            audio_path = "/tmp/temp_audio.mp3"  # Simplified
        else:
            audio_path = audio

        # Transcribe using Whisper
        result = self.processor.transcribe(
            audio_path,
            language=language or self.config.language,
            word_timestamps=self.config.word_timestamps,
        )

        # Calculate confidence from segments
        if result.get("segments"):
            confidences = [s.get("confidence", 0.0) for s in result["segments"]]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        else:
            avg_confidence = 0.0

        output = {
            "text": result["text"],
            "language": result["language"],
            "language_probability": result["language_probability"],
            "duration": result["duration"],
            "segments": result["segments"],
            "confidence": abs(avg_confidence),  # Convert log prob to 0-1
            "model": result["model"],
        }

        # Store in memory if requested
        if store_in_memory and hasattr(self, "write_to_memory"):
            self.write_to_memory(
                content={
                    "text": output["text"],
                    "language": output["language"],
                    "duration": output["duration"],
                },
                tags=["transcription", "audio"],
                importance=0.7,
            )

        return output

    def transcribe_batch(
        self,
        audio_files: List[Union[AudioField, str, Path]],
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Transcribe multiple audio files.

        Args:
            audio_files: List of audio files
            language: Language hint for all files

        Returns:
            List of transcription results
        """
        results = []

        for audio in audio_files:
            result = self.transcribe(audio, language, store_in_memory=False)
            results.append(result)

        return results

    def detect_language(self, audio: Union[AudioField, str, Path]) -> Dict[str, Any]:
        """
        Detect language of audio file.

        Args:
            audio: Audio file

        Returns:
            Dict with 'language', 'confidence'
        """
        audio_path = audio if isinstance(audio, (str, Path)) else "/tmp/temp_audio.mp3"
        return self.processor.detect_language(audio_path)
