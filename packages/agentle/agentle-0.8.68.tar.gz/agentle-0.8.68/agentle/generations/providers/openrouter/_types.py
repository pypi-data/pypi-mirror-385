# Placeholder for OpenRouter types
"""
Type definitions for OpenRouter API requests and responses.

This module defines TypedDicts for all OpenRouter-specific structures,
ensuring type safety throughout the provider implementation.
"""

from typing import TypedDict, Literal, NotRequired, Sequence


class OpenRouterImageUrl(TypedDict):
    """Image URL structure for OpenRouter messages."""

    url: str
    detail: NotRequired[Literal["auto", "low", "high"]]


class OpenRouterImageUrlPart(TypedDict):
    """Image URL content part."""

    type: Literal["image_url"]
    image_url: OpenRouterImageUrl


class OpenRouterCacheControl(TypedDict):
    """Cache control for prompt caching (Anthropic-style)."""

    type: Literal["ephemeral"]


class OpenRouterTextPart(TypedDict):
    """Text content part."""

    type: Literal["text"]
    text: str
    cache_control: NotRequired[OpenRouterCacheControl]


class OpenRouterFileData(TypedDict):
    """File data structure for PDFs and other documents."""

    filename: str
    file_data: str  # URL or base64 data URL


class OpenRouterFilePart(TypedDict):
    """File content part for PDFs."""

    type: Literal["file"]
    file: OpenRouterFileData


class OpenRouterInputAudioData(TypedDict):
    """Audio data structure."""

    data: str  # base64 encoded audio
    format: Literal["wav", "mp3"]


class OpenRouterInputAudioPart(TypedDict):
    """Audio content part."""

    type: Literal["input_audio"]
    input_audio: OpenRouterInputAudioData


OpenRouterMessageContent = (
    str
    | Sequence[
        OpenRouterTextPart
        | OpenRouterImageUrlPart
        | OpenRouterFilePart
        | OpenRouterInputAudioPart
    ]
)


class OpenRouterToolCallFunction(TypedDict):
    """Function call within a tool call."""

    name: str
    arguments: str  # JSON string


class OpenRouterToolCall(TypedDict):
    """Tool call structure in assistant messages."""

    id: str
    type: Literal["function"]
    function: OpenRouterToolCallFunction


class OpenRouterSystemMessage(TypedDict):
    """System/developer message format."""

    role: Literal["system"]
    content: str


class OpenRouterUserMessage(TypedDict):
    """User message format."""

    role: Literal["user"]
    content: OpenRouterMessageContent


class OpenRouterAssistantMessage(TypedDict):
    """Assistant message format."""

    role: Literal["assistant"]
    content: str | None
    tool_calls: NotRequired[Sequence[OpenRouterToolCall]]
    reasoning: NotRequired[str]  # Reasoning from models that support it


class OpenRouterToolMessage(TypedDict):
    """Tool result message format."""

    role: Literal["tool"]
    tool_call_id: str
    content: str


OpenRouterMessage = (
    OpenRouterSystemMessage
    | OpenRouterUserMessage
    | OpenRouterAssistantMessage
    | OpenRouterToolMessage
)


class OpenRouterToolFunctionParameters(TypedDict):
    """Tool function parameter schema."""

    type: Literal["object"]
    properties: dict[str, object]
    required: NotRequired[Sequence[str]]


class OpenRouterToolFunction(TypedDict):
    """Tool function definition."""

    name: str
    description: str
    parameters: OpenRouterToolFunctionParameters


class OpenRouterTool(TypedDict):
    """Tool definition structure."""

    type: Literal["function"]
    function: OpenRouterToolFunction


class OpenRouterMaxPrice(TypedDict):
    """Maximum pricing constraints."""

    prompt: NotRequired[float]  # Price per million tokens
    completion: NotRequired[float]  # Price per million tokens
    request: NotRequired[float]  # Price per request
    image: NotRequired[float]  # Price per image


class OpenRouterProviderPreferences(TypedDict):
    """Provider routing preferences."""

    allow_fallbacks: NotRequired[bool]
    require_parameters: NotRequired[bool]
    data_collection: NotRequired[Literal["allow", "deny"]]
    zdr: NotRequired[bool]  # Zero Data Retention enforcement
    order: NotRequired[Sequence[str]]
    only: NotRequired[Sequence[str]]  # Only allow these providers
    ignore: NotRequired[Sequence[str]]  # Ignore these providers
    quantizations: NotRequired[Sequence[str]]
    sort: NotRequired[Literal["price", "throughput", "latency"]]
    max_price: NotRequired[OpenRouterMaxPrice]


class OpenRouterJsonSchema(TypedDict):
    """JSON Schema for structured outputs."""

    name: str
    strict: NotRequired[bool]
    schema: dict[str, object]


class OpenRouterResponseFormat(TypedDict):
    """Response format specification for structured outputs."""

    type: Literal["json_schema"]
    json_schema: OpenRouterJsonSchema


class OpenRouterPdfPluginConfig(TypedDict):
    """PDF parsing plugin configuration."""

    engine: NotRequired[Literal["pdf-text", "mistral-ocr", "native"]]


class OpenRouterFileParserPlugin(TypedDict):
    """File parser plugin configuration."""

    id: Literal["file-parser"]
    pdf: NotRequired[OpenRouterPdfPluginConfig]


class OpenRouterWebSearchPlugin(TypedDict):
    """Web search plugin configuration."""

    id: Literal["web"]
    engine: NotRequired[Literal["native", "exa"]]  # Search engine to use
    max_results: NotRequired[int]  # Max number of search results (default 5)
    search_prompt: NotRequired[str]  # Custom prompt for search results


OpenRouterPlugin = OpenRouterFileParserPlugin | OpenRouterWebSearchPlugin


class OpenRouterUsage(TypedDict):
    """Token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OpenRouterResponseMessage(TypedDict):
    """Response message from OpenRouter."""

    role: Literal["assistant"]
    content: str | None
    tool_calls: NotRequired[Sequence[OpenRouterToolCall]]
    reasoning: NotRequired[str]  # Reasoning from models that support it


class OpenRouterChoice(TypedDict):
    """Choice in the response."""

    index: int
    message: OpenRouterResponseMessage
    finish_reason: str


class OpenRouterResponse(TypedDict):
    """Complete response from OpenRouter API."""

    id: str
    provider: NotRequired[str]
    model: str
    object: Literal["chat.completion"]
    created: int
    choices: Sequence[OpenRouterChoice]
    usage: OpenRouterUsage


# Streaming response types


class OpenRouterStreamDelta(TypedDict):
    """Delta content in streaming response."""

    role: NotRequired[Literal["assistant"]]
    content: NotRequired[str]
    tool_calls: NotRequired[Sequence[OpenRouterToolCall]]
    reasoning: NotRequired[str]


class OpenRouterStreamChoice(TypedDict):
    """Choice in streaming response."""

    index: int
    delta: OpenRouterStreamDelta
    finish_reason: NotRequired[str | None]


class OpenRouterStreamResponse(TypedDict):
    """Streaming response chunk from OpenRouter API."""

    id: str
    provider: NotRequired[str]
    model: str
    object: Literal["chat.completion.chunk"]
    created: int
    choices: Sequence[OpenRouterStreamChoice]


class OpenRouterRequest(TypedDict):
    """Complete request structure for OpenRouter API."""

    model: str | Sequence[str]
    messages: Sequence[OpenRouterMessage]
    temperature: NotRequired[float]
    max_tokens: NotRequired[int]
    top_p: NotRequired[float]
    frequency_penalty: NotRequired[float]
    presence_penalty: NotRequired[float]
    stream: NotRequired[bool]
    tools: NotRequired[Sequence[OpenRouterTool]]
    tool_choice: NotRequired[Literal["auto", "none"] | dict[str, object]]
    response_format: NotRequired[OpenRouterResponseFormat]
    provider: NotRequired[OpenRouterProviderPreferences]
    plugins: NotRequired[Sequence[OpenRouterPlugin]]
    transforms: NotRequired[Sequence[Literal["middle-out"]]]  # Context compression
