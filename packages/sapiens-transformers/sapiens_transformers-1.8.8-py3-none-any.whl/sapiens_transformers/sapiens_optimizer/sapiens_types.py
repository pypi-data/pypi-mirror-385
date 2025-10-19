"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from typing_extensions import TypedDict, NotRequired, Literal
from typing import Any, List, Optional, Dict, Union
JsonType = Union[None, int, str, bool, List[Any], Dict[str, Any]]
class EmbeddingUsage(TypedDict):
    prompt_tokens: int
    total_tokens: int
class Embedding(TypedDict):
    index: int
    object: str
    embedding: Union[List[float], List[List[float]]]
class CreateEmbeddingResponse(TypedDict):
    object: Literal["list"]
    model: str
    data: List[Embedding]
    usage: EmbeddingUsage
class CompletionLogprobs(TypedDict):
    text_offset: List[int]
    token_logprobs: List[Optional[float]]
    tokens: List[str]
    top_logprobs: List[Optional[Dict[str, float]]]
class CompletionChoice(TypedDict):
    text: str
    index: int
    logprobs: Optional[CompletionLogprobs]
    finish_reason: Optional[Literal["stop", "length"]]
class CompletionUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
class CreateCompletionResponse(TypedDict):
    id: str
    object: Literal["text_completion"]
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: NotRequired[CompletionUsage]
class ChatCompletionResponseFunctionCall(TypedDict):
    name: str
    arguments: str
class ChatCompletionResponseMessage(TypedDict):
    content: Optional[str]
    tool_calls: NotRequired["ChatCompletionMessageToolCalls"]
    role: Literal["assistant", "function"]
    function_call: NotRequired[ChatCompletionResponseFunctionCall]
class ChatCompletionFunction(TypedDict):
    name: str
    description: NotRequired[str]
    parameters: Dict[str, JsonType]
class ChatCompletionTopLogprobToken(TypedDict):
    token: str
    logprob: float
    bytes: Optional[List[int]]
class ChatCompletionLogprobToken(ChatCompletionTopLogprobToken):
    token: str
    logprob: float
    bytes: Optional[List[int]]
    top_logprobs: List[ChatCompletionTopLogprobToken]
class ChatCompletionLogprobs(TypedDict):
    content: Optional[List[ChatCompletionLogprobToken]]
    refusal: Optional[List[ChatCompletionLogprobToken]]
class ChatCompletionResponseChoice(TypedDict):
    index: int
    message: "ChatCompletionResponseMessage"
    logprobs: Optional[ChatCompletionLogprobs]
    finish_reason: Optional[str]
class CreateChatCompletionResponse(TypedDict):
    id: str
    object: Literal["chat.completion"]
    created: int
    model: str
    choices: List["ChatCompletionResponseChoice"]
    usage: CompletionUsage
class ChatCompletionMessageToolCallChunkFunction(TypedDict):
    name: Optional[str]
    arguments: str
class ChatCompletionMessageToolCallChunk(TypedDict):
    index: int
    id: NotRequired[str]
    type: Literal["function"]
    function: ChatCompletionMessageToolCallChunkFunction
class ChatCompletionStreamResponseDeltaEmpty(TypedDict): pass
class ChatCompletionStreamResponseDeltaFunctionCall(TypedDict):
    name: str
    arguments: str
class ChatCompletionStreamResponseDelta(TypedDict):
    content: NotRequired[Optional[str]]
    function_call: NotRequired[Optional[ChatCompletionStreamResponseDeltaFunctionCall]]
    tool_calls: NotRequired[Optional[List[ChatCompletionMessageToolCallChunk]]]
    role: NotRequired[Optional[Literal["system", "user", "assistant", "tool"]]]
class ChatCompletionStreamResponseChoice(TypedDict):
    index: int
    delta: Union[ChatCompletionStreamResponseDelta, ChatCompletionStreamResponseDeltaEmpty]
    finish_reason: Optional[Literal["stop", "length", "tool_calls", "function_call"]]
    logprobs: NotRequired[Optional[ChatCompletionLogprobs]]
class CreateChatCompletionStreamResponse(TypedDict):
    id: str
    model: str
    object: Literal["chat.completion.chunk"]
    created: int
    choices: List[ChatCompletionStreamResponseChoice]
class ChatCompletionFunctions(TypedDict):
    name: str
    description: NotRequired[str]
    parameters: Dict[str, JsonType]
class ChatCompletionFunctionCallOption(TypedDict):
    name: str
class ChatCompletionRequestResponseFormat(TypedDict):
    type: Literal["text", "json_object"]
    schema: NotRequired[JsonType]
class ChatCompletionRequestMessageContentPartText(TypedDict):
    type: Literal["text"]
    text: str
class ChatCompletionRequestMessageContentPartImageImageUrl(TypedDict):
    url: str
    detail: NotRequired[Literal["auto", "low", "high"]]
class ChatCompletionRequestMessageContentPartImage(TypedDict):
    type: Literal["image_url"]
    image_url: Union[str, ChatCompletionRequestMessageContentPartImageImageUrl]
ChatCompletionRequestMessageContentPart = Union[ChatCompletionRequestMessageContentPartText, ChatCompletionRequestMessageContentPartImage]
class ChatCompletionRequestSystemMessage(TypedDict):
    role: Literal["system"]
    content: Optional[str]
class ChatCompletionRequestUserMessage(TypedDict):
    role: Literal["user"]
    content: Optional[Union[str, List[ChatCompletionRequestMessageContentPart]]]
class ChatCompletionMessageToolCallFunction(TypedDict):
    name: str
    arguments: str
class ChatCompletionMessageToolCall(TypedDict):
    id: str
    type: Literal["function"]
    function: ChatCompletionMessageToolCallFunction
ChatCompletionMessageToolCalls = List[ChatCompletionMessageToolCall]
class ChatCompletionRequestAssistantMessageFunctionCall(TypedDict):
    name: str
    arguments: str
class ChatCompletionRequestAssistantMessage(TypedDict):
    role: Literal["assistant"]
    content: NotRequired[str]
    tool_calls: NotRequired[ChatCompletionMessageToolCalls]
    function_call: NotRequired[ChatCompletionRequestAssistantMessageFunctionCall]
class ChatCompletionRequestToolMessage(TypedDict):
    role: Literal["tool"]
    content: Optional[str]
    tool_call_id: str
class ChatCompletionRequestFunctionMessage(TypedDict):
    role: Literal["function"]
    content: Optional[str]
    name: str
ChatCompletionRequestMessage = Union[ChatCompletionRequestSystemMessage, ChatCompletionRequestUserMessage, ChatCompletionRequestAssistantMessage,
ChatCompletionRequestUserMessage, ChatCompletionRequestToolMessage, ChatCompletionRequestFunctionMessage]
class ChatCompletionRequestFunctionCallOption(TypedDict):
    name: str
ChatCompletionRequestFunctionCall = Union[Literal["none", "auto"], ChatCompletionRequestFunctionCallOption]
ChatCompletionFunctionParameters = Dict[str, JsonType]
class ChatCompletionToolFunction(TypedDict):
    name: str
    description: NotRequired[str]
    parameters: ChatCompletionFunctionParameters
class ChatCompletionTool(TypedDict):
    type: Literal["function"]
    function: ChatCompletionToolFunction
class ChatCompletionNamedToolChoiceFunction(TypedDict):
    name: str
class ChatCompletionNamedToolChoice(TypedDict):
    type: Literal["function"]
    function: ChatCompletionNamedToolChoiceFunction
ChatCompletionToolChoiceOption = Union[Literal["none", "auto", "required"], ChatCompletionNamedToolChoice]
EmbeddingData = Embedding
CompletionChunk = CreateCompletionResponse
Completion = CreateCompletionResponse
CreateCompletionStreamResponse = CreateCompletionResponse
ChatCompletionMessage = ChatCompletionResponseMessage
ChatCompletionChoice = ChatCompletionResponseChoice
ChatCompletion = CreateChatCompletionResponse
ChatCompletionChunkDeltaEmpty = ChatCompletionStreamResponseDeltaEmpty
ChatCompletionChunkChoice = ChatCompletionStreamResponseChoice
ChatCompletionChunkDelta = ChatCompletionStreamResponseDelta
ChatCompletionChunk = CreateChatCompletionStreamResponse
ChatCompletionStreamResponse = CreateChatCompletionStreamResponse
ChatCompletionResponseFunction = ChatCompletionFunction
ChatCompletionFunctionCall = ChatCompletionResponseFunctionCall
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
