"""Settings and data models for LLM Provider Factory."""

from typing import List, Optional, Dict, Any, Union, BinaryIO
from pydantic import BaseModel, Field, model_validator
from enum import Enum
from pathlib import Path


class MessageRole(str, Enum):
    """Message roles in conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """Represents a single message in conversation history."""
    
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True


class GenerationRequest(BaseModel):
    """Request for text generation."""
    
    # Either prompt OR messages should be provided
    prompt: Optional[str] = Field(default=None, description="Simple prompt for generation")
    messages: Optional[List[Message]] = Field(default=None, description="Messages for conversation")
    
    # Legacy field for backward compatibility
    history: Optional[List[Message]] = Field(default=None, description="Conversation history (deprecated, use messages)")
    
    # Generation parameters
    max_tokens: Optional[int] = Field(default=None, ge=1, le=100000)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    stop_sequences: Optional[List[str]] = Field(default=None)
    stream: bool = Field(default=False, description="Whether to stream the response")
    
    class Config:
        extra = "allow"  # Allow provider-specific parameters
    
    @model_validator(mode='after')
    def validate_prompt_or_messages(self):
        """Validate that either prompt or messages is provided."""
        if not self.prompt and not self.messages:
            raise ValueError("Either 'prompt' or 'messages' must be provided")
        return self


class GenerationResponse(BaseModel):
    """Response from text generation."""
    
    content: str = Field(..., description="Generated text content")
    finish_reason: Optional[str] = Field(default=None)
    usage: Optional[Dict[str, Any]] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    provider: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)


class StreamChunk(BaseModel):
    """Chunk of streamed response."""
    
    content: str = Field(..., description="Partial content")
    is_final: bool = Field(default=False, description="Whether this is the final chunk")
    finish_reason: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class ProviderInfo(BaseModel):
    """Information about a provider."""
    
    name: str
    display_name: str
    description: str
    supported_models: List[str]
    capabilities: List[str]
    is_available: bool = True


class SpeechRequest(BaseModel):
    """Request for speech-to-text transcription."""
    
    audio_data: Union[bytes, str, Path] = Field(..., description="Audio data, file path, or file URL")
    language: Optional[str] = Field(default=None, description="Language code (e.g., 'en', 'tr')")
    model: Optional[str] = Field(default=None, description="Model to use for transcription")
    
    # Audio processing options
    format: Optional[str] = Field(default=None, description="Audio format (auto-detected if not specified)")
    sample_rate: Optional[int] = Field(default=None, description="Audio sample rate in Hz")
    
    # Transcription options
    timestamps: bool = Field(default=False, description="Include word-level timestamps")
    word_confidence: bool = Field(default=False, description="Include word confidence scores")
    speaker_labels: bool = Field(default=False, description="Enable speaker diarization")
    punctuation: bool = Field(default=True, description="Add punctuation to transcription")
    
    # Provider-specific options
    provider_options: Optional[Dict[str, Any]] = Field(default=None, description="Provider-specific parameters")
    
    class Config:
        extra = "allow"


class SpeechResponse(BaseModel):
    """Response from speech-to-text transcription."""
    
    text: str = Field(..., description="Transcribed text")
    language: Optional[str] = Field(default=None, description="Detected or specified language")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Overall confidence score")
    
    # Detailed results
    words: Optional[List[Dict[str, Any]]] = Field(default=None, description="Word-level results with timestamps")
    segments: Optional[List[Dict[str, Any]]] = Field(default=None, description="Sentence/phrase segments")
    speakers: Optional[List[Dict[str, Any]]] = Field(default=None, description="Speaker diarization results")
    
    # Metadata
    duration: Optional[float] = Field(default=None, description="Audio duration in seconds")
    provider: Optional[str] = Field(default=None, description="Provider used")
    model: Optional[str] = Field(default=None, description="Model used")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")