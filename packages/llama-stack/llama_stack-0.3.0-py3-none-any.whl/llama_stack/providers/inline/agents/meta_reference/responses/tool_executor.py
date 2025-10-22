# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

import asyncio
import json
from collections.abc import AsyncIterator

from llama_stack.apis.agents.openai_responses import (
    OpenAIResponseInputToolFileSearch,
    OpenAIResponseInputToolMCP,
    OpenAIResponseObjectStreamResponseFileSearchCallCompleted,
    OpenAIResponseObjectStreamResponseFileSearchCallInProgress,
    OpenAIResponseObjectStreamResponseFileSearchCallSearching,
    OpenAIResponseObjectStreamResponseMcpCallCompleted,
    OpenAIResponseObjectStreamResponseMcpCallFailed,
    OpenAIResponseObjectStreamResponseMcpCallInProgress,
    OpenAIResponseObjectStreamResponseWebSearchCallCompleted,
    OpenAIResponseObjectStreamResponseWebSearchCallInProgress,
    OpenAIResponseObjectStreamResponseWebSearchCallSearching,
    OpenAIResponseOutputMessageFileSearchToolCall,
    OpenAIResponseOutputMessageFileSearchToolCallResults,
    OpenAIResponseOutputMessageWebSearchToolCall,
)
from llama_stack.apis.common.content_types import (
    ImageContentItem,
    TextContentItem,
)
from llama_stack.apis.inference import (
    OpenAIChatCompletionContentPartImageParam,
    OpenAIChatCompletionContentPartTextParam,
    OpenAIChatCompletionToolCall,
    OpenAIImageURL,
    OpenAIToolMessageParam,
)
from llama_stack.apis.tools import ToolGroups, ToolInvocationResult, ToolRuntime
from llama_stack.apis.vector_io import VectorIO
from llama_stack.log import get_logger
from llama_stack.providers.utils.telemetry import tracing

from .types import ChatCompletionContext, ToolExecutionResult

logger = get_logger(name=__name__, category="agents::meta_reference")


class ToolExecutor:
    def __init__(
        self,
        tool_groups_api: ToolGroups,
        tool_runtime_api: ToolRuntime,
        vector_io_api: VectorIO,
    ):
        self.tool_groups_api = tool_groups_api
        self.tool_runtime_api = tool_runtime_api
        self.vector_io_api = vector_io_api

    async def execute_tool_call(
        self,
        tool_call: OpenAIChatCompletionToolCall,
        ctx: ChatCompletionContext,
        sequence_number: int,
        output_index: int,
        item_id: str,
        mcp_tool_to_server: dict[str, OpenAIResponseInputToolMCP] | None = None,
    ) -> AsyncIterator[ToolExecutionResult]:
        tool_call_id = tool_call.id
        function = tool_call.function
        tool_kwargs = json.loads(function.arguments) if function.arguments else {}

        if not function or not tool_call_id or not function.name:
            yield ToolExecutionResult(sequence_number=sequence_number)
            return

        # Emit progress events for tool execution start
        async for event_result in self._emit_progress_events(
            function.name, ctx, sequence_number, output_index, item_id, mcp_tool_to_server
        ):
            sequence_number = event_result.sequence_number
            yield event_result

        # Execute the actual tool call
        error_exc, result = await self._execute_tool(function.name, tool_kwargs, ctx, mcp_tool_to_server)

        # Emit completion events for tool execution
        has_error = error_exc or (result and ((result.error_code and result.error_code > 0) or result.error_message))
        async for event_result in self._emit_completion_events(
            function.name, ctx, sequence_number, output_index, item_id, has_error, mcp_tool_to_server
        ):
            sequence_number = event_result.sequence_number
            yield event_result

        # Build result messages from tool execution
        output_message, input_message = await self._build_result_messages(
            function, tool_call_id, item_id, tool_kwargs, ctx, error_exc, result, has_error, mcp_tool_to_server
        )

        # Yield the final result
        yield ToolExecutionResult(
            sequence_number=sequence_number,
            final_output_message=output_message,
            final_input_message=input_message,
            citation_files=result.metadata.get("citation_files") if result and result.metadata else None,
        )

    async def _execute_knowledge_search_via_vector_store(
        self,
        query: str,
        response_file_search_tool: OpenAIResponseInputToolFileSearch,
    ) -> ToolInvocationResult:
        """Execute knowledge search using vector_stores.search API with filters support."""
        search_results = []

        # Create search tasks for all vector stores
        async def search_single_store(vector_store_id):
            try:
                search_response = await self.vector_io_api.openai_search_vector_store(
                    vector_store_id=vector_store_id,
                    query=query,
                    filters=response_file_search_tool.filters,
                    max_num_results=response_file_search_tool.max_num_results,
                    ranking_options=response_file_search_tool.ranking_options,
                    rewrite_query=False,
                )
                return search_response.data
            except Exception as e:
                logger.warning(f"Failed to search vector store {vector_store_id}: {e}")
                return []

        # Run all searches in parallel using gather
        search_tasks = [search_single_store(vid) for vid in response_file_search_tool.vector_store_ids]
        all_results = await asyncio.gather(*search_tasks)

        # Flatten results
        for results in all_results:
            search_results.extend(results)

        content_items = []
        content_items.append(
            TextContentItem(
                text=f"knowledge_search tool found {len(search_results)} chunks:\nBEGIN of knowledge_search tool results.\n"
            )
        )

        unique_files = set()
        for i, result_item in enumerate(search_results):
            chunk_text = result_item.content[0].text if result_item.content else ""
            # Get file_id from attributes if result_item.file_id is empty
            file_id = result_item.file_id or (
                result_item.attributes.get("document_id") if result_item.attributes else None
            )
            metadata_text = f"document_id: {file_id}, score: {result_item.score}"
            if result_item.attributes:
                metadata_text += f", attributes: {result_item.attributes}"

            text_content = f"[{i + 1}] {metadata_text} (cite as <|{file_id}|>)\n{chunk_text}\n"
            content_items.append(TextContentItem(text=text_content))
            unique_files.add(file_id)

        content_items.append(TextContentItem(text="END of knowledge_search tool results.\n"))

        citation_instruction = ""
        if unique_files:
            citation_instruction = (
                " Cite sources immediately at the end of sentences before punctuation, using `<|file-id|>` format (e.g., 'This is a fact <|file-Cn3MSNn72ENTiiq11Qda4A|>.'). "
                "Do not add extra punctuation. Use only the file IDs provided (do not invent new ones)."
            )

        content_items.append(
            TextContentItem(
                text=f'The above results were retrieved to help answer the user\'s query: "{query}". Use them as supporting information only in answering this query.{citation_instruction}\n',
            )
        )

        # handling missing attributes for old versions
        citation_files = {}
        for result in search_results:
            file_id = result.file_id
            if not file_id and result.attributes:
                file_id = result.attributes.get("document_id")

            filename = result.filename
            if not filename and result.attributes:
                filename = result.attributes.get("filename")
            if not filename:
                filename = "unknown"

            citation_files[file_id] = filename

        return ToolInvocationResult(
            content=content_items,
            metadata={
                "document_ids": [r.file_id for r in search_results],
                "chunks": [r.content[0].text if r.content else "" for r in search_results],
                "scores": [r.score for r in search_results],
                "citation_files": citation_files,
            },
        )

    async def _emit_progress_events(
        self,
        function_name: str,
        ctx: ChatCompletionContext,
        sequence_number: int,
        output_index: int,
        item_id: str,
        mcp_tool_to_server: dict[str, OpenAIResponseInputToolMCP] | None = None,
    ) -> AsyncIterator[ToolExecutionResult]:
        """Emit progress events for tool execution start."""
        # Emit in_progress event based on tool type (only for tools with specific streaming events)
        progress_event = None
        if mcp_tool_to_server and function_name in mcp_tool_to_server:
            sequence_number += 1
            progress_event = OpenAIResponseObjectStreamResponseMcpCallInProgress(
                item_id=item_id,
                output_index=output_index,
                sequence_number=sequence_number,
            )
        elif function_name == "web_search":
            sequence_number += 1
            progress_event = OpenAIResponseObjectStreamResponseWebSearchCallInProgress(
                item_id=item_id,
                output_index=output_index,
                sequence_number=sequence_number,
            )
        elif function_name == "knowledge_search":
            sequence_number += 1
            progress_event = OpenAIResponseObjectStreamResponseFileSearchCallInProgress(
                item_id=item_id,
                output_index=output_index,
                sequence_number=sequence_number,
            )

        if progress_event:
            yield ToolExecutionResult(stream_event=progress_event, sequence_number=sequence_number)

        # For web search, emit searching event
        if function_name == "web_search":
            sequence_number += 1
            searching_event = OpenAIResponseObjectStreamResponseWebSearchCallSearching(
                item_id=item_id,
                output_index=output_index,
                sequence_number=sequence_number,
            )
            yield ToolExecutionResult(stream_event=searching_event, sequence_number=sequence_number)

        # For file search, emit searching event
        if function_name == "knowledge_search":
            sequence_number += 1
            searching_event = OpenAIResponseObjectStreamResponseFileSearchCallSearching(
                item_id=item_id,
                output_index=output_index,
                sequence_number=sequence_number,
            )
            yield ToolExecutionResult(stream_event=searching_event, sequence_number=sequence_number)

    async def _execute_tool(
        self,
        function_name: str,
        tool_kwargs: dict,
        ctx: ChatCompletionContext,
        mcp_tool_to_server: dict[str, OpenAIResponseInputToolMCP] | None = None,
    ) -> tuple[Exception | None, any]:
        """Execute the tool and return error exception and result."""
        error_exc = None
        result = None

        try:
            if mcp_tool_to_server and function_name in mcp_tool_to_server:
                from llama_stack.providers.utils.tools.mcp import invoke_mcp_tool

                mcp_tool = mcp_tool_to_server[function_name]
                attributes = {
                    "server_label": mcp_tool.server_label,
                    "server_url": mcp_tool.server_url,
                    "tool_name": function_name,
                }
                async with tracing.span("invoke_mcp_tool", attributes):
                    result = await invoke_mcp_tool(
                        endpoint=mcp_tool.server_url,
                        headers=mcp_tool.headers or {},
                        tool_name=function_name,
                        kwargs=tool_kwargs,
                    )
            elif function_name == "knowledge_search":
                response_file_search_tool = next(
                    (t for t in ctx.response_tools if isinstance(t, OpenAIResponseInputToolFileSearch)),
                    None,
                )
                if response_file_search_tool:
                    # Use vector_stores.search API instead of knowledge_search tool
                    # to support filters and ranking_options
                    query = tool_kwargs.get("query", "")
                    async with tracing.span("knowledge_search", {}):
                        result = await self._execute_knowledge_search_via_vector_store(
                            query=query,
                            response_file_search_tool=response_file_search_tool,
                        )
            else:
                attributes = {
                    "tool_name": function_name,
                }
                async with tracing.span("invoke_tool", attributes):
                    result = await self.tool_runtime_api.invoke_tool(
                        tool_name=function_name,
                        kwargs=tool_kwargs,
                    )
        except Exception as e:
            error_exc = e

        return error_exc, result

    async def _emit_completion_events(
        self,
        function_name: str,
        ctx: ChatCompletionContext,
        sequence_number: int,
        output_index: int,
        item_id: str,
        has_error: bool,
        mcp_tool_to_server: dict[str, OpenAIResponseInputToolMCP] | None = None,
    ) -> AsyncIterator[ToolExecutionResult]:
        """Emit completion or failure events for tool execution."""
        completion_event = None

        if mcp_tool_to_server and function_name in mcp_tool_to_server:
            sequence_number += 1
            if has_error:
                completion_event = OpenAIResponseObjectStreamResponseMcpCallFailed(
                    sequence_number=sequence_number,
                )
            else:
                completion_event = OpenAIResponseObjectStreamResponseMcpCallCompleted(
                    sequence_number=sequence_number,
                )
        elif function_name == "web_search":
            sequence_number += 1
            completion_event = OpenAIResponseObjectStreamResponseWebSearchCallCompleted(
                item_id=item_id,
                output_index=output_index,
                sequence_number=sequence_number,
            )
        elif function_name == "knowledge_search":
            sequence_number += 1
            completion_event = OpenAIResponseObjectStreamResponseFileSearchCallCompleted(
                item_id=item_id,
                output_index=output_index,
                sequence_number=sequence_number,
            )

        if completion_event:
            yield ToolExecutionResult(stream_event=completion_event, sequence_number=sequence_number)

    async def _build_result_messages(
        self,
        function,
        tool_call_id: str,
        item_id: str,
        tool_kwargs: dict,
        ctx: ChatCompletionContext,
        error_exc: Exception | None,
        result: any,
        has_error: bool,
        mcp_tool_to_server: dict[str, OpenAIResponseInputToolMCP] | None = None,
    ) -> tuple[any, any]:
        """Build output and input messages from tool execution results."""
        from llama_stack.providers.utils.inference.prompt_adapter import (
            interleaved_content_as_str,
        )

        # Build output message
        if mcp_tool_to_server and function.name in mcp_tool_to_server:
            from llama_stack.apis.agents.openai_responses import (
                OpenAIResponseOutputMessageMCPCall,
            )

            message = OpenAIResponseOutputMessageMCPCall(
                id=item_id,
                arguments=function.arguments,
                name=function.name,
                server_label=mcp_tool_to_server[function.name].server_label,
            )
            if error_exc:
                message.error = str(error_exc)
            elif (result and result.error_code and result.error_code > 0) or (result and result.error_message):
                message.error = f"Error (code {result.error_code}): {result.error_message}"
            elif result and result.content:
                message.output = interleaved_content_as_str(result.content)
        else:
            if function.name == "web_search":
                message = OpenAIResponseOutputMessageWebSearchToolCall(
                    id=item_id,
                    status="completed",
                )
                if has_error:
                    message.status = "failed"
            elif function.name == "knowledge_search":
                message = OpenAIResponseOutputMessageFileSearchToolCall(
                    id=item_id,
                    queries=[tool_kwargs.get("query", "")],
                    status="completed",
                )
                if result and "document_ids" in result.metadata:
                    message.results = []
                    for i, doc_id in enumerate(result.metadata["document_ids"]):
                        text = result.metadata["chunks"][i] if "chunks" in result.metadata else None
                        score = result.metadata["scores"][i] if "scores" in result.metadata else None
                        message.results.append(
                            OpenAIResponseOutputMessageFileSearchToolCallResults(
                                file_id=doc_id,
                                filename=doc_id,
                                text=text,
                                score=score,
                                attributes={},
                            )
                        )
                if has_error:
                    message.status = "failed"
            else:
                raise ValueError(f"Unknown tool {function.name} called")

        # Build input message
        input_message = None
        if result and result.content:
            if isinstance(result.content, str):
                content = result.content
            elif isinstance(result.content, list):
                content = []
                for item in result.content:
                    if isinstance(item, TextContentItem):
                        part = OpenAIChatCompletionContentPartTextParam(text=item.text)
                    elif isinstance(item, ImageContentItem):
                        if item.image.data:
                            url = f"data:image;base64,{item.image.data}"
                        else:
                            url = item.image.url
                        part = OpenAIChatCompletionContentPartImageParam(image_url=OpenAIImageURL(url=url))
                    else:
                        raise ValueError(f"Unknown result content type: {type(item)}")
                    content.append(part)
            else:
                raise ValueError(f"Unknown result content type: {type(result.content)}")
            input_message = OpenAIToolMessageParam(content=content, tool_call_id=tool_call_id)
        else:
            text = str(error_exc) if error_exc else "Tool execution failed"
            input_message = OpenAIToolMessageParam(content=text, tool_call_id=tool_call_id)

        return message, input_message
