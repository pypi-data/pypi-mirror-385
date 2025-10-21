from pydantic import model_validator, field_validator, ConfigDict
from typing import Any, List, Union, Dict, Optional, Literal
from typing import Literal
from pydantic import Field
from typing_extensions import Annotated, TypedDict
from datetime import datetime
from .base_types import KeywordsAIBaseModel


class CacheControl(KeywordsAIBaseModel):
    type: str  # ephemeral


class OpenAIMessage(TypedDict):
    role: str
    content: str
    tool_calls: Optional[List[dict]] = None


class OpenAIStyledInput(TypedDict):
    messages: List[OpenAIMessage] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    n: Optional[int] = None
    timeout: Optional[float] = None
    stream: Optional[bool] = None
    logprobs: Optional[bool] = None
    echo: Optional[bool] = None
    stop: Optional[Union[List[str], str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[str, float]] = None
    tools: Optional[List[dict]] = None
    parallel_tool_calls: Optional[bool] = None
    tool_choice: Optional[Union[Literal["auto", "none", "required"], dict]] = None


class FilterObject(KeywordsAIBaseModel):
    id: str = None
    metric: Union[str, List[str]]
    value: List[Any]
    operator: str = ""
    display_name: Optional[str] = ""
    value_field_type: Optional[str] = None
    from_url: Optional[str] = False

    def model_dump(self, exclude_none: bool = True, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = exclude_none
        return super().model_dump(args, kwargs)


class ImageURL(KeywordsAIBaseModel):
    url: str
    detail: Optional[str] = "auto"

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(args, kwargs)


class ImageContent(KeywordsAIBaseModel):
    type: Literal["image_url"] = "image_url"
    # text: Optional[str] = None
    image_url: Union[ImageURL, str]

    model_config = ConfigDict(extra="allow")


class FileContent(KeywordsAIBaseModel):
    type: Literal["file"] = "file"
    file_id: str
    file_name: str
    file_type: str
    file_size: int


class TextContent(KeywordsAIBaseModel):
    type: Literal["text"] = "text"
    text: str
    cache_control: Optional[CacheControl] = None


class InputTextContent(KeywordsAIBaseModel):
    type: Literal["input_text"] = "input_text"
    text: str
    cache_control: Optional[CacheControl] = None


class OutputTextContent(KeywordsAIBaseModel):
    type: Literal["output_text"] = "output_text"
    text: str
    cache_control: Optional[CacheControl] = None


class FileContent(KeywordsAIBaseModel):
    type: Literal["file"] = "file"
    file: Dict[str, Any] = {}


class InputFileContent(KeywordsAIBaseModel):
    type: Literal["input_file"] = "input_file"
    file: str
    providerData: Optional[dict] = None


class InputImageContent(KeywordsAIBaseModel):
    type: Literal["input_image"] = "input_image"
    image: str
    providerData: Optional[dict] = None


class OutputTextContent(KeywordsAIBaseModel):
    type: Literal["output_text"] = "output_text"
    text: str
    annotations: Optional[List[Union[Dict, str]]] = None
    cache_control: Optional[CacheControl] = None


class ToolUseContent(KeywordsAIBaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str = ""
    name: str = ""
    input: dict = {}


class ToolCallFunction(KeywordsAIBaseModel):
    name: str
    arguments: str


class ToolCall(KeywordsAIBaseModel):
    id: str = None
    type: str = "function"
    function: ToolCallFunction


MessageContentType = Annotated[
    Union[
        ImageContent,
        TextContent,
        InputTextContent,
        OutputTextContent,
        FileContent,
        InputFileContent,
        InputImageContent,
        ToolUseContent,
        "AnthropicImageContent",
        "AnthropicToolResultContent",
    ],
    Field(discriminator="type"),
]


class TextModelResponseFormat(KeywordsAIBaseModel):
    type: str
    response_schema: Optional[dict] = None
    json_schema: Optional[dict] = None

    model_config = ConfigDict(extra="allow")

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class Message(KeywordsAIBaseModel):
    role: Literal["user", "assistant", "system", "tool", "none", "developer"]
    content: Union[str, List[Union[MessageContentType, str]], None] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Union[ToolCall, dict]]] = None
    reasoning_content: Optional[str] = None
    thinking_blocks: Optional[List[dict]] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    model_config = ConfigDict(from_attributes=True)


class FunctionParameters(KeywordsAIBaseModel):
    type: Union[str, list[str]] = "object"
    properties: Dict[str, dict] = None  # Only need when you type is object
    required: List[str] = None

    model_config = ConfigDict(extra="allow")


class Function(KeywordsAIBaseModel):
    name: Optional[str] = None
    description: Optional[str] = None  # Optional description
    parameters: Optional[dict] = {}  # Optional parameters
    strict: Optional[bool] = None  # Optional strict mode

    def model_dump(self, exclude_none: bool = True, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = exclude_none
        return super().model_dump(*args, **kwargs)


class FunctionTool(KeywordsAIBaseModel):
    type: str = "function"
    function: Function = None

    model_config = ConfigDict(extra="allow")


class CodeInterpreterTool(KeywordsAIBaseModel):
    type: Literal["code_interpreter"] = "code_interpreter"


class FileSearchTool(KeywordsAIBaseModel):
    type: Literal["file_search"] = "file_search"

    class FileSearch(KeywordsAIBaseModel):
        max_num_results: Optional[int] = None

    file_search: FileSearch


class ToolChoiceFunction(KeywordsAIBaseModel):
    name: str

    model_config = ConfigDict(extra="allow")


class ToolChoice(KeywordsAIBaseModel):
    type: str
    function: Optional[ToolChoiceFunction] = None
    model_config = ConfigDict(extra="allow")


class BasicLLMParams(KeywordsAIBaseModel):
    echo: Optional[bool] = None
    frequency_penalty: Optional[float] = None
    logprobs: Optional[bool] = None
    logit_bias: Optional[Dict[str, float]] = None
    messages: List[Message] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    n: Optional[int] = None
    parallel_tool_calls: Optional[bool] = None
    presence_penalty: Optional[float] = None
    stop: Optional[Union[List[str], str]] = None
    stream: Optional[bool] = None
    stream_options: Optional[dict] = None
    temperature: Optional[float] = None
    timeout: Optional[float] = None
    tools: Optional[List[dict]] = None
    response_format: Optional[Dict] = None
    reasoning_effort: Optional[Union[str, None]] = None
    tool_choice: Optional[Union[Literal["auto", "none", "required"], ToolChoice]] = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None
    verbosity: Optional[str] = None
    extra_headers: Optional[Dict[str, str]] = None

    def model_dump(self, exclude_none: bool = True, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = exclude_none
        return super().model_dump(*args, **kwargs)

    model_config = ConfigDict(protected_namespaces=())


class LiteLLMCompletionParams(BasicLLMParams):
    thinking: Optional[dict] = None


class Usage(KeywordsAIBaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cache_creation_input_tokens: Optional[int] = (
        0  # Internal field, name directly from Anthropic. Will be populated from cache_creation_prompt_tokens
    )
    cache_creation_prompt_tokens: Optional[int] = (
        0  # User facing, renamed for naming consistency, equivalent to cache_creation_input_tokens
    )
    cache_read_input_tokens: Optional[int] = 0
    completion_tokens_details: Optional[dict] = None
    prompt_tokens_details: Optional[dict] = None

    @model_validator(mode="before")
    def _preprocess_data(data):
        if isinstance(data, dict):
            pass
        elif hasattr(data, "__dict__"):
            data = data.__dict__
        else:
            raise ValueError(
                "KeywordsAIParams can only be initialized with a dict or an object with a __dict__ attribute"
            )
        if data.get("cache_creation_prompt_tokens"):
            data["cache_creation_input_tokens"] = data["cache_creation_prompt_tokens"]
        return data


class BasicTextToSpeechParams(KeywordsAIBaseModel):
    model: str
    input: str
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    speed: Optional[float] = 1
    response_format: Optional[str] = "mp3"

    model_config = ConfigDict(protected_namespaces=())


class BasicEmbeddingParams(KeywordsAIBaseModel):
    input: Optional[Union[str, List[str]]] = None
    model: Optional[str] = None
    encoding_format: Optional[str] = "float"
    dimensions: Optional[int] = None
    # user: Optional[str] = None # Comment out as it is conflicting with the user field in KeywordsAIParams

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(*args, **kwargs)


# Assistant Params
class CodeInterpreterResource(KeywordsAIBaseModel):
    type: Literal["code_interpreter"] = "code_interpreter"
    code: str


class TextResponseChoice(KeywordsAIBaseModel):
    message: Message


class BasicAssistantParams(KeywordsAIBaseModel):
    model: str
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[dict]] = None
    tool_resources: Optional[dict] = None  # To complete
    metadata: Optional[dict] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    response_format: Optional[Union[str, dict]] = None  # To complete

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class ThreadMessage(Message):
    attachments: Optional[List[dict]] = None
    metadata: Optional[dict] = None


class BasicThreadParams(KeywordsAIBaseModel):
    messages: Optional[List[ThreadMessage]] = None
    tool_resources: Optional[dict] = None
    metadata: Optional[dict] = None


class TruncationStrategy(KeywordsAIBaseModel):
    type: str
    last_messages: Optional[int] = None


class BasicRunParams(KeywordsAIBaseModel):
    assistant_id: str
    model: Optional[str] = None
    instructions: Optional[str] = None
    additional_instructions: Optional[str] = None
    additional_messages: Optional[List[ThreadMessage]] = None
    tools: Optional[List[dict]] = None
    metadata: Optional[dict] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    stream: Optional[bool] = None
    max_prompt_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None
    truncation_strategy: Optional[TruncationStrategy] = None
    tool_choice: Optional[ToolChoice] = None
    parallel_tool_calls: Optional[bool] = None
    response_format: Optional[Union[str, dict]] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


# End of Assistant Params


import io


class BasicTranscriptionParams(KeywordsAIBaseModel):
    file: io.BytesIO
    model: str
    language: Optional[str] = None
    prompt: Optional[str] = None
    response_format: Optional[Literal["json", "text", "srt", "verbose_json", "vtt"]] = (
        "json"
    )
    temperature: Optional[float] = 0
    timestamp_granularities: Optional[List[Literal["word", "segment"]]] = None
    user: Optional[str] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)

    model_config = ConfigDict(arbitrary_types_allowed="allow")


class EnvEnabled(KeywordsAIBaseModel):
    test: Optional[bool] = False
    staging: Optional[bool] = False
    prod: Optional[bool] = False


class AlertSettings(KeywordsAIBaseModel):
    system: Optional[Dict[str, bool]] = None
    api: Optional[Dict[str, EnvEnabled]] = None
    webhook: Optional[Dict[str, EnvEnabled]] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


# ===============anthropic==================


class AnthropicAutoToolChoice(KeywordsAIBaseModel):
    type: Literal["auto"] = "auto"


class AnthropicAnyToolChoice(KeywordsAIBaseModel):
    type: Literal["any"] = "any"


class AnthropicToolChoice(KeywordsAIBaseModel):
    type: Literal["tool"] = "tool"
    name: str


class AnthropicInputSchemaProperty(KeywordsAIBaseModel):
    type: str
    description: str = None

    model_config = ConfigDict(extra="allow")

    def model_dump(self, exclude_none=True, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = exclude_none
        return super().model_dump(*args, **kwargs)


class AnthropicInputSchema(KeywordsAIBaseModel):
    type: Literal["object"] = "object"
    properties: Dict[str, AnthropicInputSchemaProperty] = (
        None  # Only need when you type is object
    )
    required: List[str] = None

    model_config = ConfigDict(extra="allow")


class AnthropicToolUse(KeywordsAIBaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict


class AnthropicTool(KeywordsAIBaseModel):
    type: str = "computer_20241022"
    name: str
    description: Optional[Union[str, None]] = None
    input_schema: dict = None
    # We will make all these optional and let anthropic handle the rest of the type check. Default None.
    display_height_px: Optional[int] = None
    display_width_px: Optional[int] = None
    display_number: Optional[Union[int, None]] = None


class AnthropicToolResultContent(KeywordsAIBaseModel):
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: str


class AnthropicImageContentSrc(KeywordsAIBaseModel):
    type: str
    media_type: str
    data: str


class AnthropicImageContent(KeywordsAIBaseModel):
    type: Literal["image"] = "image"
    source: AnthropicImageContentSrc


class AnthropicTextContent(KeywordsAIBaseModel):
    type: Literal["text"] = "text"
    text: str
    cache_control: Optional[CacheControl] = None


AnthropicContentTypes = Annotated[
    Union[
        AnthropicImageContent,
        AnthropicTextContent,
        AnthropicToolUse,
        AnthropicToolResultContent,
    ],
    Field(discriminator="type"),
]


class AnthropicMessage(KeywordsAIBaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: Union[List[AnthropicContentTypes], str, None] = None
    cache_control: Optional[CacheControl] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class AnthropicSystemMessage(KeywordsAIBaseModel):
    cache_control: Optional[CacheControl] = None
    type: str  # text
    text: str


class AnthropicParams(KeywordsAIBaseModel):
    model: str
    messages: List[AnthropicMessage]
    max_tokens: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    stop_sequence: Optional[List[str]] = None
    stream: Optional[bool] = None
    system: Optional[Union[str, List[AnthropicSystemMessage]]] = None
    temperature: Optional[float] = None
    tool_choice: Optional[
        Union[AnthropicAutoToolChoice, AnthropicAnyToolChoice, AnthropicToolChoice]
    ] = None
    tools: Optional[List[AnthropicTool]] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None


class AnthropicTextResponseContent(KeywordsAIBaseModel):
    type: Literal["text"] = "text"
    text: str


class AnthropicToolResponseContent(KeywordsAIBaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict


class AnthropicUsage(KeywordsAIBaseModel):
    input_tokens: Optional[int] = 0
    output_tokens: Optional[int] = 1
    cache_creation_input_tokens: Optional[int] = 0
    cache_read_input_tokens: Optional[int] = 0


class AnthropicResponse(KeywordsAIBaseModel):
    id: str
    type: Literal["message", "tool_use", "tool_result"]
    content: List[Union[AnthropicTextResponseContent, AnthropicToolResponseContent]] = (
        []
    )
    model: str
    stop_reason: Literal["end_turn ", "max_tokens", "stop_sequence", "tool_use"] = (
        "end_turn"
    )
    stop_sequence: Union[str, None] = None
    usage: AnthropicUsage


"""
event: message_start
data: {"type": "message_start", "message": {"id": "msg_id", "type": "message", "role": "assistant", "content": [], "model": "claude-3-opus-20240229", "stop_reason": null, "stop_sequence": null, "usage": {"input_tokens": 25, "output_tokens": 1}}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}

event: ping
data: {"type": "ping"}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "!"}}

event: content_block_stop
data: {"type": "content_block_stop", "index": 0}

event: message_delta
data: {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence":null}, "usage": {"output_tokens": 15}}

event: message_stop
data: {"type": "message_stop"}
"""


class AnthropicStreamDelta(KeywordsAIBaseModel):
    type: Literal["text_delta", "input_json_delta"] = "text_delta"
    text: Union[str, None] = None
    partial_json: Union[str, None] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.partial_json:
            self.type = "input_json_delta"
        elif self.text:
            self.type = "text_delta"
        else:
            self.type = "text_delta"
            self.text = ""

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)


class AnthropicStreamContentBlock(KeywordsAIBaseModel):
    type: Literal["text"] = "text"
    text: str = ""  # Initialize with an empty string


class AnthropicStreamChunk(KeywordsAIBaseModel):
    """Example chunk:
    {
    "type": "content_block_delta",
    "index": 1,
    "delta": {
        "type": "input_json_delta",
        "partial_json": "{\"location\": \"San Fra"
    }
    }
    """

    type: Literal[
        "message_start",
        "content_block_start",
        "content_block_delta",
        "content_block_stop",
        "message_delta",
        "message_stop",
        "ping",
    ]
    index: Union[int, None] = None
    delta: Union[AnthropicStreamDelta, None] = None
    content_block: Union[AnthropicStreamContentBlock, None] = None
    message: Union[AnthropicResponse, None] = None

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        kwargs["exclude_none"] = True
        return super().model_dump(*args, **kwargs)
