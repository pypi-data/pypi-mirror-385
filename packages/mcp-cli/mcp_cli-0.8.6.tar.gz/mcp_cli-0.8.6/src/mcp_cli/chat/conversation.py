# mcp_cli/chat/conversation.py - FIXED VERSION
"""
FIXED: Updated to work with the new OpenAI client universal tool compatibility system.
"""

import time
import asyncio
import logging
from typing import Optional
from chuk_term.ui import output

# mcp cli imports
from mcp_cli.chat.tool_processor import ToolProcessor

log = logging.getLogger(__name__)


class ConversationProcessor:
    """
    Class to handle LLM conversation processing with streaming support.

    Updated to work with universal tool compatibility system.
    """

    def __init__(self, context, ui_manager):
        self.context = context
        self.ui_manager = ui_manager
        self.tool_processor = ToolProcessor(context, ui_manager)

    async def process_conversation(self, max_turns: int = 10):
        """Process the conversation loop, handling tool calls and responses with streaming.

        Args:
            max_turns: Maximum number of conversation turns before forcing exit (default: 10)
        """
        turn_count = 0
        last_tool_signature = None  # Track last tool call to detect duplicates
        tools_for_completion = None  # Will be set based on context
        try:
            while turn_count < max_turns:
                try:
                    turn_count += 1
                    start_time = time.time()

                    # Skip slash commands (already handled by UI)
                    last_msg = (
                        self.context.conversation_history[-1]
                        if self.context.conversation_history
                        else {}
                    )
                    content = last_msg.get("content", "")
                    if last_msg.get("role") == "user" and content.startswith("/"):
                        return

                    # Ensure OpenAI tools are loaded for function calling
                    if not getattr(self.context, "openai_tools", None):
                        await self._load_tools()

                    # REMOVED: Sanitization logic - now handled by universal tool compatibility
                    # The OpenAI client automatically handles tool name sanitization and restoration

                    # Always pass tools - let the model decide what to do
                    tools_for_completion = self.context.openai_tools
                    log.debug(
                        f"Passing {len(tools_for_completion) if tools_for_completion else 0} tools to completion"
                    )

                    # Check if client supports streaming
                    client = self.context.client

                    # For chuk-llm, check if create_completion accepts stream parameter
                    supports_streaming = hasattr(client, "create_completion")

                    if supports_streaming:
                        # Check if create_completion accepts stream parameter
                        import inspect

                        try:
                            sig = inspect.signature(client.create_completion)
                            has_stream_param = "stream" in sig.parameters
                            supports_streaming = has_stream_param
                        except Exception as e:
                            log.debug(f"Could not inspect signature: {e}")
                            supports_streaming = False

                    completion = None

                    if supports_streaming:
                        # Use streaming response handler
                        try:
                            completion = await self._handle_streaming_completion(
                                tools=tools_for_completion
                            )
                        except Exception as e:
                            log.warning(
                                f"Streaming failed, falling back to regular completion: {e}"
                            )
                            output.warning(
                                f"Streaming failed, falling back to regular completion: {e}"
                            )
                            completion = await self._handle_regular_completion(
                                tools=tools_for_completion
                            )
                    else:
                        # Regular completion
                        completion = await self._handle_regular_completion(
                            tools=tools_for_completion
                        )

                    response_content = completion.get("response", "No response")
                    tool_calls = completion.get("tool_calls", [])

                    # If model requested tool calls, execute them
                    if tool_calls and len(tool_calls) > 0:
                        log.debug(f"Processing {len(tool_calls)} tool calls from LLM")

                        # Check if we're at max turns
                        if turn_count >= max_turns:
                            output.warning(
                                f"Maximum conversation turns ({max_turns}) reached. Stopping to prevent infinite loop."
                            )
                            self.context.conversation_history.append(
                                {
                                    "role": "assistant",
                                    "content": "I've reached the maximum number of conversation turns. The tool results have been provided above.",
                                }
                            )
                            break

                        # Create signature to detect duplicate tool calls
                        import json

                        current_signature = []
                        for tc in tool_calls:
                            if hasattr(tc, "function"):
                                name = getattr(tc.function, "name", "")
                                args = getattr(tc.function, "arguments", "")
                            elif isinstance(tc, dict) and "function" in tc:
                                name = tc["function"].get("name", "")
                                args = tc["function"].get("arguments", "")
                            else:
                                continue
                            if isinstance(args, dict):
                                args = json.dumps(args, sort_keys=True)
                            current_signature.append(f"{name}:{args}")

                        current_sig_str = "|".join(sorted(current_signature))

                        # If this is a duplicate, stop looping and return control to user
                        if (
                            last_tool_signature
                            and current_sig_str == last_tool_signature  # type: ignore[unreachable]
                        ):
                            log.warning(  # type: ignore[unreachable]
                                f"Duplicate tool call detected: {current_sig_str}"
                            )
                            output.info(
                                "Tool has already been executed. Results are shown above."
                            )
                            break

                        last_tool_signature = current_sig_str

                        # Log the tool calls for debugging
                        for i, tc in enumerate(tool_calls):
                            log.debug(f"Tool call {i}: {tc}")

                        # FIXED: Get name mapping from universal tool compatibility system
                        name_mapping = getattr(self.context, "tool_name_mapping", {})
                        log.debug(f"Using name mapping: {name_mapping}")

                        # Process tool calls - this will handle streaming display
                        await self.tool_processor.process_tool_calls(
                            tool_calls, name_mapping
                        )
                        continue

                    # Reset duplicate tracking on text response
                    last_tool_signature = None

                    # Display assistant response (if not already displayed by streaming)
                    elapsed = completion.get("elapsed_time", time.time() - start_time)

                    if not completion.get("streaming", False):
                        # Non-streaming response, display normally
                        self.ui_manager.print_assistant_response(
                            response_content, elapsed
                        )
                    else:
                        # Streaming response - final display already handled by finish_streaming()
                        # Just mark streaming as stopped and clean up
                        self.ui_manager.stop_streaming_response()
                        # Clear streaming handler reference
                        if hasattr(self.ui_manager, "streaming_handler"):
                            self.ui_manager.streaming_handler = None

                    # Add to conversation history
                    self.context.conversation_history.append(
                        {"role": "assistant", "content": response_content}
                    )
                    break

                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    output.error(f"Error during conversation processing: {exc}")
                    import traceback

                    traceback.print_exc()
                    self.context.conversation_history.append(
                        {
                            "role": "assistant",
                            "content": f"I encountered an error: {exc}",
                        }
                    )
                    break
        except asyncio.CancelledError:
            raise

    async def _handle_streaming_completion(self, tools: Optional[list] = None) -> dict:
        """Handle streaming completion with UI integration.

        Args:
            tools: Tool definitions to pass to the LLM, or None to disable tools
        """
        from mcp_cli.chat.streaming_handler import StreamingResponseHandler

        # Signal UI that streaming is starting
        self.ui_manager.start_streaming_response()

        # Set the streaming handler reference in UI manager for interruption support
        streaming_handler = StreamingResponseHandler(
            console=self.ui_manager.console, chat_display=self.ui_manager.display
        )
        self.ui_manager.streaming_handler = streaming_handler

        try:
            completion = await streaming_handler.stream_response(
                client=self.context.client,
                messages=self.context.conversation_history,
                tools=tools,
            )

            # Enhanced tool call validation and logging
            if completion.get("tool_calls"):
                log.debug(
                    f"Streaming completion returned {len(completion['tool_calls'])} tool calls"
                )
                for i, tc in enumerate(completion["tool_calls"]):
                    log.debug(f"Streamed tool call {i}: {tc}")

                    # Validate tool call structure
                    if not self._validate_streaming_tool_call(tc):
                        log.warning(f"Invalid tool call structure from streaming: {tc}")
                        # Try to fix common issues
                        fixed_tc = self._fix_tool_call_structure(tc)
                        if fixed_tc:
                            completion["tool_calls"][i] = fixed_tc
                            log.debug(f"Fixed tool call {i}: {fixed_tc}")
                        else:
                            log.error(
                                f"Could not fix tool call {i}, removing from list"
                            )
                            completion["tool_calls"].pop(i)

            return completion

        finally:
            # Keep streaming handler reference for finalization
            # Will be cleared after finalization in main conversation loop
            pass

    async def _handle_regular_completion(self, tools: Optional[list] = None) -> dict:
        """Handle regular (non-streaming) completion.

        Args:
            tools: Tool definitions to pass to the LLM, or None to disable tools
        """
        start_time = time.time()

        try:
            completion = await self.context.client.create_completion(
                messages=self.context.conversation_history,
                tools=tools,
            )
        except Exception as e:
            # If tools spec invalid, retry without tools
            err = str(e)
            if "Invalid 'tools" in err:
                log.error(f"Tool definition error: {err}")
                output.warning(
                    "Tool definitions rejected by model, retrying without tools..."
                )
                completion = await self.context.client.create_completion(
                    messages=self.context.conversation_history
                )
            else:
                raise

        elapsed = time.time() - start_time
        completion["elapsed_time"] = elapsed
        completion["streaming"] = False

        result: dict = completion
        return result

    def _validate_streaming_tool_call(self, tool_call: dict) -> bool:
        """Validate that a tool call from streaming has the required structure."""
        try:
            if not isinstance(tool_call, dict):
                return False  # type: ignore[unreachable]

            # Check for required fields
            if "function" not in tool_call:
                return False

            function = tool_call["function"]
            if not isinstance(function, dict):
                return False

            # Check function has name
            if "name" not in function or not function["name"]:
                return False

            # Validate arguments if present
            if "arguments" in function:
                args = function["arguments"]
                if isinstance(args, str):
                    # Try to parse as JSON
                    try:
                        if args.strip():  # Don't try to parse empty strings
                            import json

                            json.loads(args)
                    except json.JSONDecodeError:
                        log.warning(f"Invalid JSON arguments in tool call: {args}")
                        return False
                elif not isinstance(args, dict):
                    # Arguments should be string or dict
                    return False

            return True

        except Exception as e:
            log.error(f"Error validating streaming tool call: {e}")
            return False

    def _fix_tool_call_structure(self, tool_call: dict) -> Optional[dict]:
        """Try to fix common issues with tool call structure from streaming."""
        try:
            fixed = dict(tool_call)  # Make a copy

            # Ensure we have required fields
            if "id" not in fixed:
                fixed["id"] = f"call_{hash(str(tool_call)) % 10000}"

            if "type" not in fixed:
                fixed["type"] = "function"

            if "function" not in fixed:
                return None  # Can't fix this

            function = fixed["function"]

            # Fix empty name
            if not function.get("name"):
                return None  # Can't fix missing name

            # Fix arguments
            if "arguments" not in function:
                function["arguments"] = "{}"
            elif function["arguments"] is None:
                function["arguments"] = "{}"
            elif isinstance(function["arguments"], dict):
                # Convert dict to JSON string
                import json

                function["arguments"] = json.dumps(function["arguments"])
            elif not isinstance(function["arguments"], str):
                # Convert to string
                function["arguments"] = str(function["arguments"])

            # Validate the fixed version
            if self._validate_streaming_tool_call(fixed):
                return fixed
            else:
                return None

        except Exception as e:
            log.error(f"Error fixing tool call structure: {e}")
            return None

    async def _load_tools(self):
        """
        Load and adapt tools for the current provider.

        FIXED: Updated to use universal tool compatibility system.
        """
        try:
            if hasattr(self.context.tool_manager, "get_adapted_tools_for_llm"):
                # EXPLICITLY specify provider for proper adaptation
                provider = getattr(self.context, "provider", "openai")
                tools_and_mapping = (
                    await self.context.tool_manager.get_adapted_tools_for_llm(provider)
                )
                self.context.openai_tools = tools_and_mapping[0]
                self.context.tool_name_mapping = tools_and_mapping[1]
                log.debug(
                    f"Loaded {len(self.context.openai_tools)} adapted tools for {provider}"
                )

                # FIXED: No longer validate tool names here since universal compatibility handles it
                log.debug(f"Universal tool compatibility enabled for {provider}")

        except Exception as exc:
            log.error(f"Error loading tools: {exc}")
            self.context.openai_tools = []
            self.context.tool_name_mapping = {}
