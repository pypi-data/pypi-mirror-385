from typing import Literal, Optional, Union, overload, List


from agentle.responses.definitions.create_response import CreateResponse
from agentle.responses.definitions.include_enum import IncludeEnum
from agentle.responses.definitions.input_item import InputItem
from agentle.responses.definitions.response import Response
from agentle.responses.definitions.response_stream_event import ResponseStreamEvent
from agentle.responses.definitions.response_stream_options import ResponseStreamOptions
from agentle.responses.definitions.conversation_param import ConversationParam
from agentle.responses.definitions.metadata import Metadata
from agentle.responses.definitions.service_tier import ServiceTier
from agentle.responses.definitions.reasoning import Reasoning
from agentle.responses.definitions.text import Text
from agentle.responses.definitions.tool import Tool
from agentle.responses.definitions.tool_choice_allowed import ToolChoiceAllowed
from agentle.responses.definitions.tool_choice_custom import ToolChoiceCustom
from agentle.responses.definitions.tool_choice_function import ToolChoiceFunction
from agentle.responses.definitions.tool_choice_mcp import ToolChoiceMCP
from agentle.responses.definitions.tool_choice_options import ToolChoiceOptions
from agentle.responses.definitions.tool_choice_types import ToolChoiceTypes
from agentle.responses.definitions.prompt import Prompt
from agentle.responses.definitions.truncation import Truncation
from agentle.responses.definitions.model_ids_responses import ModelIdsResponses
import abc
from agentle.responses._streaming.async_stream import AsyncStream
from rsb.models.base_model import BaseModel


class ResponderMixin(BaseModel, abc.ABC):
    @overload
    async def respond_async[TextFormatT = None](
        self,
        *,
        input: Optional[Union[str, list[InputItem[TextFormatT]]]] = None,
        model: Optional[ModelIdsResponses] = None,
        include: Optional[list[IncludeEnum]] = None,
        parallel_tool_calls: Optional[bool] = None,
        store: Optional[bool] = None,
        instructions: Optional[str] = None,
        stream: Optional[Literal[False]] = False,
        stream_options: Optional[ResponseStreamOptions] = None,
        conversation: Optional[Union[str, ConversationParam]] = None,
        text_format: type[TextFormatT] | None = None,
        # ResponseProperties parameters
        previous_response_id: Optional[str] = None,
        reasoning: Optional[Reasoning] = None,
        background: Optional[bool] = None,
        max_output_tokens: Optional[int] = None,
        max_tool_calls: Optional[int] = None,
        text: Optional[Text] = None,
        tools: Optional[List[Tool]] = None,
        tool_choice: Optional[
            Union[
                ToolChoiceOptions,
                ToolChoiceAllowed,
                ToolChoiceTypes,
                ToolChoiceFunction,
                ToolChoiceMCP,
                ToolChoiceCustom,
            ]
        ] = None,
        prompt: Optional[Prompt] = None,
        truncation: Optional[Truncation] = None,
        # ModelResponseProperties parameters
        metadata: Optional[Metadata] = None,
        top_logprobs: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        user: Optional[str] = None,
        safety_identifier: Optional[str] = None,
        prompt_cache_key: Optional[str] = None,
        service_tier: Optional[ServiceTier] = None,
    ) -> AsyncStream[ResponseStreamEvent]: ...

    @overload
    async def respond_async[TextFormatT = None](
        self,
        *,
        input: Optional[Union[str, list[InputItem[TextFormatT]]]] = None,
        model: Optional[ModelIdsResponses] = None,
        include: Optional[list[IncludeEnum]] = None,
        parallel_tool_calls: Optional[bool] = None,
        store: Optional[bool] = None,
        instructions: Optional[str] = None,
        stream: Literal[True],
        stream_options: Optional[ResponseStreamOptions] = None,
        conversation: Optional[Union[str, ConversationParam]] = None,
        text_format: type[TextFormatT] | None = None,
        # ResponseProperties parameters
        previous_response_id: Optional[str] = None,
        reasoning: Optional[Reasoning] = None,
        background: Optional[bool] = None,
        max_output_tokens: Optional[int] = None,
        max_tool_calls: Optional[int] = None,
        text: Optional[Text] = None,
        tools: Optional[List[Tool]] = None,
        tool_choice: Optional[
            Union[
                ToolChoiceOptions,
                ToolChoiceAllowed,
                ToolChoiceTypes,
                ToolChoiceFunction,
                ToolChoiceMCP,
                ToolChoiceCustom,
            ]
        ] = None,
        prompt: Optional[Prompt] = None,
        truncation: Optional[Truncation] = None,
        # ModelResponseProperties parameters
        metadata: Optional[Metadata] = None,
        top_logprobs: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        user: Optional[str] = None,
        safety_identifier: Optional[str] = None,
        prompt_cache_key: Optional[str] = None,
        service_tier: Optional[ServiceTier] = None,
    ) -> AsyncStream[ResponseStreamEvent]: ...

    @overload
    async def respond_async[TextFormatT = None](
        self,
        *,
        input: Optional[Union[str, list[InputItem[TextFormatT]]]] = None,
        model: Optional[ModelIdsResponses] = None,
        include: Optional[list[IncludeEnum]] = None,
        parallel_tool_calls: Optional[bool] = None,
        store: Optional[bool] = None,
        instructions: Optional[str] = None,
        stream: bool,
        stream_options: Optional[ResponseStreamOptions] = None,
        conversation: Optional[Union[str, ConversationParam]] = None,
        text_format: type[TextFormatT] | None = None,
        # ResponseProperties parameters
        previous_response_id: Optional[str] = None,
        reasoning: Optional[Reasoning] = None,
        background: Optional[bool] = None,
        max_output_tokens: Optional[int] = None,
        max_tool_calls: Optional[int] = None,
        text: Optional[Text] = None,
        tools: Optional[List[Tool]] = None,
        tool_choice: Optional[
            Union[
                ToolChoiceOptions,
                ToolChoiceAllowed,
                ToolChoiceTypes,
                ToolChoiceFunction,
                ToolChoiceMCP,
                ToolChoiceCustom,
            ]
        ] = None,
        prompt: Optional[Prompt] = None,
        truncation: Optional[Truncation] = None,
        # ModelResponseProperties parameters
        metadata: Optional[Metadata] = None,
        top_logprobs: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        user: Optional[str] = None,
        safety_identifier: Optional[str] = None,
        prompt_cache_key: Optional[str] = None,
        service_tier: Optional[ServiceTier] = None,
    ) -> AsyncStream[ResponseStreamEvent]: ...

    async def respond_async[TextFormatT = None](
        self,
        *,
        input: Optional[Union[str, list[InputItem[TextFormatT]]]] = None,
        model: Optional[ModelIdsResponses] = None,
        include: Optional[list[IncludeEnum]] = None,
        parallel_tool_calls: Optional[bool] = None,
        store: Optional[bool] = None,
        instructions: Optional[str] = None,
        stream: Optional[Literal[False] | Literal[True]] = None,
        stream_options: Optional[ResponseStreamOptions] = None,
        conversation: Optional[Union[str, ConversationParam]] = None,
        text_format: type[TextFormatT] | None = None,
        # ResponseProperties parameters
        previous_response_id: Optional[str] = None,
        reasoning: Optional[Reasoning] = None,
        background: Optional[bool] = None,
        max_output_tokens: Optional[int] = None,
        max_tool_calls: Optional[int] = None,
        text: Optional[Text] = None,
        tools: Optional[List[Tool]] = None,
        tool_choice: Optional[
            Union[
                ToolChoiceOptions,
                ToolChoiceAllowed,
                ToolChoiceTypes,
                ToolChoiceFunction,
                ToolChoiceMCP,
                ToolChoiceCustom,
            ]
        ] = None,
        prompt: Optional[Prompt] = None,
        truncation: Optional[Truncation] = None,
        # ModelResponseProperties parameters
        metadata: Optional[Metadata] = None,
        top_logprobs: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        user: Optional[str] = None,
        safety_identifier: Optional[str] = None,
        prompt_cache_key: Optional[str] = None,
        service_tier: Optional[ServiceTier] = None,
    ) -> Response[TextFormatT] | AsyncStream[ResponseStreamEvent]:
        return await self._respond_async(
            CreateResponse[TextFormatT](
                input=input,
                model=model,
                include=include,
                parallel_tool_calls=parallel_tool_calls,
                store=store,
                instructions=instructions,
                stream=stream,
                stream_options=stream_options,
                conversation=conversation,
                # ResponseProperties parameters
                previous_response_id=previous_response_id,
                reasoning=reasoning,
                background=background,
                max_output_tokens=max_output_tokens,
                max_tool_calls=max_tool_calls,
                text=text,
                tools=tools,
                tool_choice=tool_choice,
                prompt=prompt,
                truncation=truncation,
                # ModelResponseProperties parameters
                metadata=metadata,
                top_logprobs=top_logprobs,
                temperature=temperature,
                top_p=top_p,
                user=user,
                safety_identifier=safety_identifier,
                prompt_cache_key=prompt_cache_key,
                service_tier=service_tier,
            )
        )

    @abc.abstractmethod
    async def _respond_async[TextFormatT = None](
        self,
        create_response: CreateResponse[TextFormatT],
    ) -> Response[TextFormatT] | AsyncStream[ResponseStreamEvent]: ...
