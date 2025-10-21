import asyncio
import concurrent.futures
import functools
import json
import time
from collections import deque
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

# Using Pydantic BaseModel
from pydantic import BaseModel

from argentic.core.graph.state import AgentState
from argentic.core.llm.providers.base import ModelProvider
from argentic.core.logger import LogLevel, get_logger, parse_log_level
from argentic.core.messager.messager import Messager

# Add our new entities
from argentic.core.protocol.chat_message import AssistantMessage as ChatAssistantMessage
from argentic.core.protocol.chat_message import (
    ChatMessage,
    LLMChatResponse,
)
from argentic.core.protocol.chat_message import SystemMessage as ChatSystemMessage
from argentic.core.protocol.chat_message import ToolMessage as ChatToolMessage
from argentic.core.protocol.chat_message import UserMessage as ChatUserMessage
from argentic.core.protocol.enums import LLMRole, MessageSource
from argentic.core.protocol.message import (
    AgentLLMRequestMessage,
    AgentLLMResponseMessage,
    AgentSystemMessage,
    AgentTaskMessage,
    AgentTaskResultMessage,
    AnswerMessage,
    AskQuestionMessage,
    BaseMessage,
    MinimalToolCallRequest,
)
from argentic.core.protocol.task import (
    TaskErrorMessage,
    TaskResultMessage,
    TaskStatus,
)
from argentic.core.protocol.tool import ToolCallRequest
from argentic.core.tools.tool_manager import ToolManager


# Pydantic Models for LLM JSON Response Parsing
class LLMResponseToolCall(BaseModel):
    type: Literal["tool_call"]
    tool_calls: List[ToolCallRequest]


class LLMResponseDirect(BaseModel):
    type: Literal["direct"]
    content: str


class LLMResponseToolResult(BaseModel):
    type: Literal["tool_result"]
    tool_id: str
    result: str


# Union type for all possible LLM responses
class LLMResponse(BaseModel):
    """Union model that can handle any of the three response types"""

    type: Literal["tool_call", "direct", "tool_result"]
    # Optional fields for different response types
    tool_calls: Optional[List[ToolCallRequest]] = None
    content: Optional[str] = None
    tool_id: Optional[str] = None
    result: Optional[str] = None


class AgentStateMode(str, Enum):
    STATEFUL = "stateful"
    STATELESS = "stateless"


class Agent:
    """Manages interaction with LLM and ToolManager (Async Version)."""

    def __init__(
        self,
        llm: ModelProvider,
        messager: Messager,
        tool_manager: Optional[ToolManager] = None,
        log_level: Union[str, LogLevel] = LogLevel.INFO,
        register_topic: str = "agent/tools/register",
        tool_call_topic_base: str = "agent/tools/call",
        tool_response_topic_base: str = "agent/tools/response",
        status_topic: str = "agent/status/info",
        answer_topic: str = "agent/response/answer",
        llm_response_topic: Optional[str] = None,
        tool_result_topic: Optional[str] = None,
        system_prompt: Optional[str] = None,
        override_default_prompts: bool = False,  # Flag to override default rules
        role: str = "agent",
        description: str = "General AI agent capable of processing tasks and providing responses",  # Add description
        graph_id: Optional[str] = None,
        expected_output_format: Literal["json", "text", "code"] = "json",  # New parameter
        llm_config: Optional[Dict[str, Any]] = None,  # Add llm_config parameter
        task_handling: Literal["direct", "llm"] = "llm",  # New parameter
        enable_dialogue_logging: bool = False,  # New parameter for dialogue logging
        max_dialogue_history_items: int = 100,  # Context management
        max_query_history_items: int = 20,  # History per query
        adaptive_max_iterations: bool = True,  # Adaptive iteration limits
        # Tool loop detection parameters
        max_consecutive_tool_calls: int = 3,  # Max same tool calls in a row
        tool_call_window_size: int = 5,  # Window for detecting tool call patterns
        enable_completion_analysis: bool = True,  # Analyze if tasks are complete
        # Messaging control parameters
        publish_to_supervisor: bool = True,  # Publish results to supervisor
        publish_to_agent_topic: bool = True,  # Publish to agent-specific topic
        enable_tool_result_publishing: bool = False,  # Publish individual tool results
        state_mode: AgentStateMode = AgentStateMode.STATEFUL,  # Stateful vs Stateless LLM calls
    ):
        self.llm = llm
        self.messager = messager
        self.answer_topic = answer_topic
        self.llm_response_topic = llm_response_topic
        self.tool_result_topic = tool_result_topic
        self.raw_template: Optional[str] = None
        self.system_prompt = system_prompt
        self.override_default_prompts = override_default_prompts
        self.role = role
        self.description = description  # Store agent description
        self.graph_id = graph_id
        self.expected_output_format = expected_output_format  # Store new parameter
        self.llm_config = llm_config if llm_config is not None else {}  # Store llm_config
        self.task_handling = task_handling  # Store task_handling parameter
        self.state_mode = state_mode

        if isinstance(log_level, str):
            self.log_level = parse_log_level(log_level)
        else:
            self.log_level = log_level

        self.logger = get_logger("agent", self.log_level)

        # Dialogue logging
        self.enable_dialogue_logging = enable_dialogue_logging
        # placeholder, will init after setting history size
        self.dialogue_history: deque[Dict[str, Any]]
        self.max_dialogue_history_items = max_dialogue_history_items
        # Now initialise deque with correct maxlen
        self.dialogue_history = deque(maxlen=self.max_dialogue_history_items)

        # Context management for endless cycles
        self.max_query_history_items = max_query_history_items
        self.adaptive_max_iterations = adaptive_max_iterations
        self._queries_processed = 0

        # Tool loop detection for endless cycles
        self.max_consecutive_tool_calls = max_consecutive_tool_calls
        self.tool_call_window_size = tool_call_window_size
        self.enable_completion_analysis = enable_completion_analysis
        # Track recent tool calls – deque auto-discards old entries, avoiding manual trimming
        self._tool_call_history: deque[Dict[str, Any]] = deque(maxlen=self.tool_call_window_size)
        self._consecutive_tool_calls = 0  # Counter for consecutive tool calls

        # Messaging control for endless cycles
        self.publish_to_supervisor = publish_to_supervisor
        self.publish_to_agent_topic = publish_to_agent_topic
        self.enable_tool_result_publishing = enable_tool_result_publishing

        # Use provided tool manager or create a new one
        if tool_manager is not None:
            self._tool_manager = tool_manager
            self.logger.info(f"Agent '{self.role}': Using provided tool manager")
        else:
            # Initialize the async ToolManager (private)
            self._tool_manager = ToolManager(
                messager,
                log_level=self.log_level,
                register_topic=register_topic,
                tool_call_topic_base=tool_call_topic_base,
                tool_response_topic_base=tool_response_topic_base,
                status_topic=status_topic,
            )
            self.logger.info(f"Agent '{self.role}': Created new tool manager")

        # Initialize output parsers
        # These are no longer needed as we are using Pydantic directly
        # self.response_parser = PydanticOutputParser(pydantic_object=LLMResponse)
        # self.tool_call_parser = PydanticOutputParser(pydantic_object=LLMResponseToolCall)
        # self.direct_parser = PydanticOutputParser(pydantic_object=LLMResponseDirect)
        # self.tool_result_parser = PydanticOutputParser(pydantic_object=LLMResponseToolResult)

        # self.prompt_template = self._build_prompt_template() # This line is removed
        self.raw_template = self._build_prompt_template()  # Ensure it's set
        if not self.raw_template:
            raise ValueError(
                "Agent raw_template was not set during _build_prompt_template initialization."
            )
        self.max_tool_iterations = 10

        # Create a dedicated thread pool for heavy LLM operations
        # This prevents blocking the default thread pool and allows better parallelism
        self._llm_thread_pool_size = 8  # Configurable in future
        self._llm_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self._llm_thread_pool_size, thread_name_prefix=f"agent-{self.role}-llm"
        )

        # Update history - using Union type to support both ChatMessage and protocol messages
        self.history: List[Union[ChatMessage, BaseMessage]] = []
        self.logger.info(
            "Agent initialized with consistent message pattern: direct fields + data=None."
        )

    async def invoke(self, state: AgentState) -> dict[str, list[ChatMessage]]:
        """
        Invokes the agent as part of a graph. This represents one turn of the agent.
        """
        self.logger.info(f"Agent '{self.role}' invoked with {len(state['messages'])} messages.")

        # Convert chat messages from state to our internal protocol messages
        protocol_messages = self._convert_chat_to_protocol_messages(state["messages"])

        # Build LLM input respecting state mode
        llm_input_messages = []
        if self.system_prompt:
            llm_input_messages.append({"role": LLMRole.SYSTEM.value, "content": self.system_prompt})

        if self.state_mode == AgentStateMode.STATEFUL:
            llm_input_messages.extend(
                self._convert_protocol_history_to_llm_format(protocol_messages)
            )
        else:
            # Stateless: include only the most recent relevant message
            relevant_protocol_message = None
            for msg in reversed(protocol_messages):
                if isinstance(msg, AskQuestionMessage):
                    relevant_protocol_message = msg
                    break
            if relevant_protocol_message is None and protocol_messages:
                relevant_protocol_message = protocol_messages[-1]

            if relevant_protocol_message is not None:
                llm_input_messages.extend(
                    self._convert_protocol_history_to_llm_format([relevant_protocol_message])
                )

        # The Supervisor will have agent_tools, a regular agent will not.
        tools = getattr(self, "agent_tools", None)
        # Only pass tools if there are actually tools available
        if tools and len(tools) > 0:
            llm_response: LLMChatResponse = await self._call_llm(
                llm_input_messages, tools=tools, llm_config=self.llm_config
            )  # Call LLM with tools
        else:
            llm_response: LLMChatResponse = await self._call_llm(
                llm_input_messages, llm_config=self.llm_config
            )  # Call LLM without tools

        # Get raw content string for logging and AgentLLMResponseMessage
        # This should capture either the direct text content or a string representation of tool calls
        llm_response_raw_text = ""
        if isinstance(llm_response, LLMChatResponse) and llm_response.message.tool_calls:
            # Serialize tool calls to a JSON string for raw_content
            llm_response_raw_text = json.dumps(llm_response.message.tool_calls)
        elif llm_response.message.content is not None:
            # Handle cases where content might not be a simple string (e.g., list of parts for multimodal)
            if isinstance(llm_response.message.content, str):
                llm_response_raw_text = llm_response.message.content
            else:
                llm_response_raw_text = str(llm_response.message.content)

        self.logger.debug(f"LLM raw response for '{self.role}': {llm_response_raw_text[:300]}...")

        llm_response_msg = AgentLLMResponseMessage(
            raw_content=llm_response_raw_text, source=MessageSource.LLM, data=None  # type: ignore
        )

        # Parse the response
        validated_response = await self._parse_llm_response(llm_response)  # Pass BaseMessage

        output_messages: List[BaseMessage] = []
        if isinstance(validated_response, LLMResponseToolCall):
            self.logger.info(f"Agent '{self.role}' is calling tools.")
            tool_call_requests = [
                ToolCallRequest(tool_id=tc.tool_id, arguments=tc.arguments)
                for tc in validated_response.tool_calls
            ]
            tool_outcome_messages, _ = await self._execute_tool_calls(tool_call_requests)
            output_messages = [llm_response_msg] + tool_outcome_messages

        elif validated_response:
            self.logger.info(f"Agent '{self.role}' is providing a direct answer or tool result.")
            # If validated_response is LLMResponseDirect or LLMResponseToolResult
            if isinstance(validated_response, LLMResponseDirect):
                llm_response_msg.parsed_type = validated_response.type
                llm_response_msg.parsed_direct_content = validated_response.content
                llm_response_msg.parsed_tool_result_content = None  # Ensure it's explicitly None
            elif isinstance(validated_response, LLMResponseToolResult):
                llm_response_msg.parsed_type = validated_response.type
                llm_response_msg.parsed_direct_content = None  # Ensure it's explicitly None
                llm_response_msg.parsed_tool_result_content = validated_response.result
            else:
                # This case should ideally not be reached if validated_response is always one of the expected types
                self.logger.warning(
                    f"Unexpected validated_response type in invoke: {type(validated_response)}"
                )
                llm_response_msg.parsed_type = "error_validation"
                llm_response_msg.error_details = (
                    f"Unexpected response type: {type(validated_response)}"
                )
            output_messages = [llm_response_msg]

        else:
            self.logger.error(f"Could not parse LLM response for agent '{self.role}'")
            error_msg = AgentSystemMessage(
                content="Error: Could not parse LLM response. Please check the format.",
                source=MessageSource.SYSTEM,
            )
            output_messages = [error_msg]

        # Convert our protocol messages back to message classes used in state
        chat_output_messages = self._convert_protocol_to_chat_messages(output_messages)

        # Preserve existing conversation history by appending the new messages
        combined_messages = state["messages"] + chat_output_messages

        return {"messages": combined_messages}

    def _convert_chat_to_protocol_messages(self, messages: List[ChatMessage]) -> List[BaseMessage]:
        protocol_msgs = []
        for msg in messages:
            # Accept both our ChatMessage and duck-typed message classes by checking for attributes
            msg_type_name = type(msg).__name__
            # Check for user/human messages by type name or isinstance
            if isinstance(msg, ChatUserMessage) or msg_type_name in (
                "HumanMessage",
                "LcHumanMessage",
            ):
                protocol_msgs.append(
                    AskQuestionMessage(question=msg.content, source=MessageSource.USER)
                )
            # Check for assistant/AI messages
            elif isinstance(msg, ChatAssistantMessage) or msg_type_name in (
                "AIMessage",
                "LcAIMessage",
            ):
                # Handle assistant messages
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    raw_content = json.dumps(msg.tool_calls)
                else:
                    raw_content = msg.content
                protocol_msgs.append(
                    AgentLLMResponseMessage(raw_content=raw_content, source=MessageSource.LLM)
                )
            # Check for system messages
            elif isinstance(msg, ChatSystemMessage) or msg_type_name in (
                "SystemMessage",
                "LcSystemMessage",
            ):
                protocol_msgs.append(
                    AgentSystemMessage(content=msg.content, source=MessageSource.SYSTEM)
                )
            # Check for tool messages
            elif isinstance(msg, ChatToolMessage) or msg_type_name in (
                "ToolMessage",
                "LcToolMessage",
            ):
                tool_call_id = getattr(msg, "tool_call_id", None) or "unknown_id"
                protocol_msgs.append(
                    TaskResultMessage(
                        tool_id=tool_call_id,
                        tool_name=tool_call_id,
                        status=TaskStatus.SUCCESS,
                        result=msg.content,
                    )
                )
        return protocol_msgs

    def _convert_protocol_to_chat_messages(
        self, messages: List[BaseMessage]
    ) -> List[Union[ChatMessage, Any]]:
        chat_msgs = []
        for msg in messages:
            if isinstance(msg, (AskQuestionMessage, AgentLLMRequestMessage)):
                # Return message compatible with tests
                try:
                    # Using compatibility shim for tests
                    from argentic.core.llm.providers.mock import LcHumanMessage

                    chat_msgs.append(
                        LcHumanMessage(
                            content=(
                                msg.question if isinstance(msg, AskQuestionMessage) else msg.prompt
                            )
                        )
                    )
                except Exception:
                    chat_msgs.append(
                        ChatUserMessage(
                            role="user",
                            content=(
                                msg.question if isinstance(msg, AskQuestionMessage) else msg.prompt
                            ),
                        )
                    )
            elif isinstance(msg, AgentLLMResponseMessage):
                try:
                    parsed_raw = json.loads(msg.raw_content)
                    if isinstance(parsed_raw, list) and all("name" in tc for tc in parsed_raw):
                        lc_tool_calls = []
                        for tc_dict in parsed_raw:
                            if (
                                isinstance(tc_dict, dict)
                                and "name" in tc_dict
                                and "args" in tc_dict
                            ):
                                lc_tool_calls.append(
                                    {
                                        "name": tc_dict["name"],
                                        "args": tc_dict["args"],
                                        "id": tc_dict.get("id"),
                                    }
                                )
                            else:
                                self.logger.warning(
                                    f"Malformed tool call dict in raw_content: {tc_dict}"
                                )
                        chat_msgs.append(
                            ChatAssistantMessage(
                                role="assistant", content="", tool_calls=lc_tool_calls
                            )
                        )
                    else:
                        try:
                            from argentic.core.llm.providers.mock import LcAIMessage

                            chat_msgs.append(LcAIMessage(content=msg.raw_content))
                        except Exception:
                            chat_msgs.append(
                                ChatAssistantMessage(role="assistant", content=msg.raw_content)
                            )
                except json.JSONDecodeError:
                    try:
                        from argentic.core.llm.providers.mock import LcAIMessage

                        chat_msgs.append(LcAIMessage(content=msg.raw_content))
                    except Exception:
                        chat_msgs.append(
                            ChatAssistantMessage(role="assistant", content=msg.raw_content)
                        )

            elif isinstance(msg, AgentSystemMessage):
                try:
                    from argentic.core.llm.providers.mock import LcSystemMessage

                    chat_msgs.append(LcSystemMessage(content=str(msg.content)))
                except Exception:
                    chat_msgs.append(ChatSystemMessage(role="system", content=str(msg.content)))
            elif isinstance(msg, TaskResultMessage):
                try:
                    from argentic.core.llm.providers.mock import LcToolMessage

                    chat_msgs.append(
                        LcToolMessage(
                            content=str(msg.result),
                            tool_call_id=msg.tool_name or "unknown_tool",
                        )
                    )
                except Exception:
                    chat_msgs.append(
                        ChatToolMessage(
                            role="tool",
                            content=str(msg.result),
                            tool_call_id=msg.tool_name or "unknown_tool",
                        )
                    )
            elif isinstance(msg, TaskErrorMessage):
                chat_msgs.append(
                    ChatToolMessage(
                        role="tool",
                        content=str(msg.error),
                        tool_call_id=msg.tool_name or "unknown_tool",
                    )
                )

        return chat_msgs

    async def async_init(self):
        """
        Async initialization for Agent, including tool manager subscriptions.
        """
        # Initialize tool manager if not already done
        try:
            # Try to call async_init - it's safe to call multiple times
            await self._tool_manager.async_init()
            self.logger.info("Agent: ToolManager initialized via async_init")
        except Exception as e:
            self.logger.warning(
                f"Agent: ToolManager async_init error (may be already initialized): {e}"
            )

        # Subscribe to task topic for direct task handling
        task_topic = f"agent/{self.role}/tasks"
        try:
            await self.messager.subscribe(task_topic, self.handle_task, AgentTaskMessage)
            self.logger.info(f"Agent '{self.role}': Subscribed to task topic '{task_topic}'")
        except Exception as e:
            self.logger.warning(f"Agent '{self.role}': Failed to subscribe to task topic: {e}")

        # Build tool wrappers from the agent's own tool manager so the LLM
        # can perform function-calling without requiring the supervisor to inject them.
        try:
            agent_tools_list = []
            for t_id, t_info in self._tool_manager.tools_by_id.items():
                t_name: str = t_info["name"]
                description: str = t_info["description"]
                parameters_str: str = t_info["parameters"]

                try:
                    parameters: Dict[str, Any] = json.loads(parameters_str)
                except (json.JSONDecodeError, TypeError):
                    self.logger.error(
                        f"Agent '{self.role}': Could not parse parameters for tool '{t_name}'."
                    )
                    continue

                def _create_callable(name: str, tool_id: str):
                    async def _async_tool(**kwargs: Any):
                        self.logger.info(
                            f"Agent '{self.role}' invoking own tool '{name}' (ID: {tool_id}) args={kwargs}"
                        )
                        res = await self._tool_manager.execute_tool(tool_id, kwargs)
                        if isinstance(res, TaskResultMessage):
                            return res.result
                        elif isinstance(res, TaskErrorMessage):
                            return f"Error from tool '{name}': {res.error}"
                        return str(res)

                    # Create a simple args model for the tool
                    class ToolArgsModel(BaseModel):
                        class Config:
                            extra = "allow"

                        def __init__(self, **data):
                            # Allow any arguments
                            super().__init__(**data)

                    return ToolCallRequest(
                        name=name,
                        tool_id=tool_id,
                        arguments=parameters,  # Use parameters from tool_manager
                    )

                agent_tools_list.append(_create_callable(t_name, t_id))

            if agent_tools_list:
                self.agent_tools = agent_tools_list  # type: ignore
                self.logger.info(
                    f"Agent '{self.role}': Prepared {len(agent_tools_list)} local tools for LLM."
                )
        except Exception as e:
            self.logger.error(f"Agent '{self.role}': Failed to build local tools list: {e}")

    async def stop(self) -> None:
        """Stop the agent and clean up resources."""
        self.logger.info(f"Stopping agent '{self.role}'...")

        # Shutdown the dedicated LLM thread pool
        self._llm_executor.shutdown(wait=True)
        self.logger.debug("LLM thread pool executor shut down.")

        # Gracefully disconnect from messaging broker if we own the messager instance
        try:
            if hasattr(self.messager, "disconnect") and callable(
                getattr(self.messager, "disconnect")
            ):
                if self.messager.is_connected():
                    try:
                        loop = asyncio.get_running_loop()
                        # If we're inside an event loop, run disconnect asynchronously
                        awaitable = self.messager.disconnect()
                        if loop.is_running():
                            awaitable  # type: ignore[func-returns-value]
                        else:
                            loop.run_until_complete(awaitable)
                    except RuntimeError:
                        # Not inside loop – create one
                        asyncio.run(self.messager.disconnect())
        except Exception as e:
            self.logger.debug(f"Messager disconnect raised: {e}")

        # Stop tool manager (cancel pending tasks etc.) – best-effort
        try:
            if hasattr(self._tool_manager, "stop"):
                self._tool_manager.stop()
        except Exception as e:
            self.logger.debug(f"ToolManager stop raised: {e}")

        self.logger.info(f"Agent '{self.role}' stopped.")

    def _cleanup_dialogue_history(self) -> None:
        """Clean up dialogue history to prevent unlimited growth."""
        # With deque(maxlen) growth is self-managed; nothing to do.
        pass

    def _get_adaptive_max_iterations(self, question: str) -> int:
        """Calculate adaptive max iterations based on task complexity."""
        if not self.adaptive_max_iterations:
            return self.max_tool_iterations

        # Simple heuristics for task complexity
        base_iterations = self.max_tool_iterations

        # Complex indicators
        complexity_indicators = [
            "multi-step",
            "workflow",
            "then",
            "after",
            "sequence",
            "multiple",
            "several",
            "various",
            "analyze",
            "comprehensive",
        ]

        complexity_score = sum(
            1 for indicator in complexity_indicators if indicator.lower() in question.lower()
        )

        # Adjust iterations based on complexity
        if complexity_score >= 3:
            return min(base_iterations * 2, 20)  # Max 20 for very complex tasks
        elif complexity_score >= 1:
            return min(base_iterations + 5, 15)  # Moderate increase
        else:
            return base_iterations  # Simple tasks use default

    def _detect_tool_call_loop(self, new_tool_calls: List[ToolCallRequest]) -> bool:
        """Detect if we're in a tool calling loop."""
        if not new_tool_calls:
            return False

        # Track the new tool calls
        current_call_signatures = []
        for tc in new_tool_calls:
            signature = {
                "tool_id": tc.tool_id,
                "arguments": tc.arguments,
                "timestamp": time.time(),
            }
            current_call_signatures.append(signature)

        # Add to history
        self._tool_call_history.extend(current_call_signatures)

        # deque maxlen already truncates history – no manual slicing required

        # Check for consecutive identical tool calls
        if len(self._tool_call_history) >= 2:
            last_calls = list(self._tool_call_history)[-2:]

            if (
                len(last_calls) == 2
                and last_calls[0]["tool_id"] == last_calls[1]["tool_id"]
                and last_calls[0]["arguments"] == last_calls[1]["arguments"]
            ):
                self._consecutive_tool_calls += 1
            else:
                self._consecutive_tool_calls = 0

            # Trigger loop detection if too many consecutive identical calls
            if self._consecutive_tool_calls >= self.max_consecutive_tool_calls:
                self.logger.warning(
                    f"Agent '{self.role}': Detected tool call loop - {self._consecutive_tool_calls} consecutive calls to {last_calls[0]['tool_id']}"
                )
                return True

        # Check for pattern repetition within the window
        if len(self._tool_call_history) >= 4:
            # Look for AB-AB patterns
            recent_calls = list(self._tool_call_history)[-4:]
            if (
                recent_calls[0]["tool_id"] == recent_calls[2]["tool_id"]
                and recent_calls[1]["tool_id"] == recent_calls[3]["tool_id"]
                and recent_calls[0]["arguments"] == recent_calls[2]["arguments"]
                and recent_calls[1]["arguments"] == recent_calls[3]["arguments"]
            ):
                self.logger.warning(
                    f"Agent '{self.role}': Detected tool call pattern loop: {recent_calls[0]['tool_id']}-{recent_calls[1]['tool_id']}"
                )
                return True

        return False

    def _analyze_task_completion(
        self, original_question: str, tool_results: List[BaseMessage]
    ) -> bool:
        """Analyze if the task appears to be completed based on tool results."""
        if not self.enable_completion_analysis or not tool_results:
            return False

        # Simple heuristics for task completion
        successful_results = [
            msg for msg in tool_results if isinstance(msg, TaskResultMessage) and msg.result
        ]

        if not successful_results:
            return False

        # Look for completion indicators in the results
        completion_indicators = [
            "successfully",
            "completed",
            "finished",
            "done",
            "created",
            "saved",
            "sent",
            "executed",
            "✅",
            "Success",
        ]

        result_text = " ".join(
            [str(msg.result) for msg in successful_results if msg.result is not None]
        ).lower()

        completion_score = sum(
            1 for indicator in completion_indicators if indicator.lower() in result_text
        )

        # If we have multiple successful tool executions with completion indicators,
        # the task is likely complete
        if len(successful_results) >= 2 and completion_score >= 2:
            self.logger.info(
                f"Agent '{self.role}': Task completion detected - {len(successful_results)} successful results with completion indicators"
            )
            return True

        # Special case: if the question involves saving/creating/sending and we see those keywords
        task_keywords = ["save", "create", "send", "email", "write", "generate"]
        task_has_action = any(keyword in original_question.lower() for keyword in task_keywords)

        if task_has_action and completion_score >= 1:
            self.logger.info(
                f"Agent '{self.role}': Action task completion detected - task involved {task_keywords} and results show completion"
            )
            return True

        return False

    def _reset_tool_call_tracking(self) -> None:
        """Reset tool call tracking for a new query."""
        self._tool_call_history.clear()
        self._consecutive_tool_calls = 0

    def _truncate_history_for_context(self, history: List[BaseMessage]) -> List[BaseMessage]:
        """Truncate history to keep context manageable while preserving essential information."""
        if len(history) <= self.max_query_history_items:
            return history

        # Always keep system message (first) and recent messages
        if history and isinstance(history[0], AgentSystemMessage):
            system_msg = [history[0]]
            recent_msgs = history[-(self.max_query_history_items - 1) :]

            # Add truncation marker if we removed messages
            if len(history) > len(system_msg) + len(recent_msgs):
                truncation_marker = AgentSystemMessage(
                    content=f"[CONTEXT TRUNCATED: {len(history) - len(system_msg) - len(recent_msgs)} messages omitted for efficiency]",
                    source=MessageSource.SYSTEM,
                    data=None,
                )
                return system_msg + [truncation_marker] + recent_msgs
            else:
                return system_msg + recent_msgs
        else:
            # No system message, just keep recent items
            return history[-self.max_query_history_items :]

    def _log_dialogue(
        self,
        role: str,
        content: str,
        message_type: str = "message",
        tool_info: Optional[Dict] = None,
    ) -> None:
        """Log a dialogue entry with role, content preview, and metadata."""
        if not self.enable_dialogue_logging:
            return

        # Create content preview (limit to 200 chars)
        preview = self._get_content_preview(content)

        dialogue_entry = {
            "timestamp": time.time(),
            "role": role,
            "message_type": message_type,
            "content_preview": preview,
            "tool_info": tool_info,
            "agent": self.role,
        }

        self.dialogue_history.append(dialogue_entry)

        # Cleanup dialogue history immediately if it exceeds the limit
        self._cleanup_dialogue_history()

        # Print dialogue entry in real-time
        self._print_dialogue_entry(dialogue_entry)

    def _get_content_preview(self, content: str, max_length: int = 200) -> str:
        """Get a preview of content limited to max_length characters."""
        if not content:
            return "[Empty]"

        # Clean up the content
        clean_content = str(content).strip()

        # If it's JSON, try to summarize it
        if clean_content.startswith("{") and '"type"' in clean_content:
            try:
                parsed = json.loads(clean_content)
                if parsed.get("type") == "tool_call" and "tool_calls" in parsed:
                    tool_calls = parsed["tool_calls"]
                    tool_names = [tc.get("tool_id", "unknown")[:8] + "..." for tc in tool_calls]
                    return f"🛠️ Tool calls: {', '.join(tool_names)}"
                elif parsed.get("type") == "direct":
                    return parsed.get("content", "Direct response")[:max_length]
            except:
                pass

        # Regular text content
        if len(clean_content) > max_length:
            return clean_content[:max_length] + "..."
        return clean_content

    def _print_dialogue_entry(self, entry: Dict[str, Any]) -> None:
        """Print a single dialogue entry in a formatted way."""
        role = entry["role"]
        preview = entry["content_preview"]
        message_type = entry["message_type"]
        agent = entry["agent"]

        # Role icons
        role_icons = {
            "user": "👤",
            "assistant": "🤖",
            "system": "⚙️",
            "tool": "🛠️",
            "supervisor": "👨‍💼",
            "researcher": "🔬",
            "secretary": "📝",
        }

        icon = role_icons.get(role, "💬")

        # Format the output
        if message_type == "tool_call":
            print(f"  {icon} {role.upper()} [{agent}]: {preview}")
        elif message_type == "tool_result":
            tool_info = entry.get("tool_info", {})
            tool_name = tool_info.get("name", "unknown")
            success = tool_info.get("success", True)
            status_icon = "✅" if success else "❌"
            print(f"  🛠️ TOOL [{tool_name}]: {status_icon} {preview}")
        else:
            print(f"  {icon} {role.upper()} [{agent}]: {preview}")

    def get_dialogue_history(self) -> List[Dict[str, Any]]:
        """Get the complete dialogue history for this agent."""
        return list(self.dialogue_history)

    def print_dialogue_summary(self) -> None:
        """Print a summary of the dialogue history."""
        if not self.dialogue_history:
            print(f"📋 No dialogue history for agent '{self.role}'")
            return

        print(f"\n📋 DIALOGUE SUMMARY - Agent '{self.role}' ({len(self.dialogue_history)} entries)")
        print("=" * 60)

        for entry in list(self.dialogue_history):
            self._print_dialogue_entry(entry)

        print("=" * 60)

    def _build_prompt_template(self) -> str:
        # Build system prompt based on override settings
        if self.override_default_prompts and self.system_prompt is not None:
            # Use only custom prompt, no default rules
            system_prompt = self.system_prompt
        elif self.system_prompt is not None:
            # Combine default rules with custom prompt
            default_rules = self._get_default_utility_rules()
            system_prompt = f"{default_rules}\n\n{self.system_prompt}"
        else:
            # Use full default system prompt
            system_prompt = self._get_default_system_prompt()

        if self.expected_output_format == "json":
            template = f"""{system_prompt}

Available Tools:
{{tool_descriptions}}

QUESTION: {{question}}

YOUR RESPONSE MUST BE A SINGLE JSON OBJECT. DO NOT INCLUDE ANY OTHER TEXT, COMMENTS, OR MARKDOWN OUTSIDE THE JSON BLOCK. ONLY THE JSON BLOCK IS ACCEPTABLE.
Respond with a JSON object like: {{"type": "direct|tool_call|tool_result", "content": "..."}}"""
        else:
            # Simplified template for text/code output
            template = f"""{system_prompt}

{{question}}"""

        self.raw_template = template
        # Maintain backwards-compatibility attribute used in tests
        self.prompt_template = template
        return template  # Return the string template

    def set_log_level(self, level: Union[str, LogLevel]) -> None:
        """
        Set the logger level

        Args:
            level: New log level (string or LogLevel enum)
        """
        if isinstance(level, str):
            self.log_level = parse_log_level(level)
        else:
            self.log_level = level

        self.logger.setLevel(self.log_level.value)
        self.logger.info(f"Agent log level changed to {self.log_level.name}")

        # Update handlers
        for handler in self.logger.handlers:
            handler.setLevel(self.log_level.value)

        # Update tool manager log level
        self._tool_manager.set_log_level(self.log_level)

    def set_system_prompt(
        self, system_prompt: str, override_default_prompts: Optional[bool] = None
    ) -> None:
        """
        Update the system prompt and rebuild the prompt template.

        Args:
            system_prompt: New system prompt to use
            override_default_prompts: Whether to override default utility rules (if None, keeps current setting)
        """
        self.system_prompt = system_prompt
        if override_default_prompts is not None:
            self.override_default_prompts = override_default_prompts
        # self.prompt_template = self._build_prompt_template() # This line is removed
        self.logger.info("System prompt updated and prompt template rebuilt")

    def get_system_prompt(self) -> str:
        """
        Get the current system prompt (either custom or default).

        Returns:
            The current system prompt being used
        """
        if self.override_default_prompts and self.system_prompt is not None:
            return self.system_prompt
        elif self.system_prompt is not None:
            default_rules = self._get_default_utility_rules()
            return f"{default_rules}\n\n{self.system_prompt}"
        else:
            return self._get_default_system_prompt()

    def _get_default_utility_rules(self) -> str:
        """
        Returns utilitarian default rules for tool interaction, agent interaction, and task completion.
        These rules are designed to be prepended to custom system prompts unless override_default_prompts is True.
        """
        return """CORE OPERATIONAL RULES:

TOOL INTERACTION RULES:
1. NEVER call the same tool with identical arguments repeatedly
2. After tool execution, analyze the results before deciding on next actions
3. If tools report success (✅, "successfully", "completed", "created", "saved", "sent"), the task is likely done
4. Multiple successful tool executions usually indicate task completion
5. Always check tool results for completion indicators before continuing

TASK COMPLETION RULES:
1. Tasks involving "save", "create", "send", "email", "write" are complete when tools confirm success
2. If you've successfully executed the required actions, provide a final summary instead of repeating
3. Look for these completion signals: ✅, "successfully", "completed", "finished", "created", "saved", "sent"
4. When tools confirm success, use "tool_result" format to provide final answer
5. Avoid endless cycles - if the work is done, conclude the task

AGENT INTERACTION RULES:
1. Be direct and efficient in communication
2. Focus on task completion rather than endless analysis
3. Provide clear status updates when tools are executed
4. If encountering loops or repetition, break the cycle with a direct answer
5. Prioritize completing requested actions over extended discussion

RESPONSE EFFICIENCY:
1. Keep responses focused and actionable
2. Avoid redundant tool calls when success is already confirmed
3. Recognize when objectives have been met and conclude appropriately
4. Use context from conversation history to avoid repeating successful actions"""

    def _get_default_system_prompt(self) -> str:
        """
        Returns the default system prompt.

        Returns:
            The default system prompt string
        """
        if self.expected_output_format == "json":
            return """You are a highly capable AI assistant that MUST follow these strict response format rules.

YOUR RESPONSE MUST BE A SINGLE JSON OBJECT. DO NOT INCLUDE ANY OTHER TEXT, COMMENTS, OR MARKDOWN OUTSIDE THE JSON BLOCK. ONLY THE JSON BLOCK IS ACCEPTABLE.

RESPONSE FORMATS:
1. Tool Call Format (use when you need to use a tool):
```json
{{
    "type": "tool_call",
    "tool_calls": [
        {{
            "tool_id": "<exact_tool_id_from_list>",
            "arguments": {{
                "<param1>": "<value1>",
                "<param2>": "<value2>"
            }}
        }}
    ]
}}
```

2. Direct Answer Format (use when you can answer directly without tools):
```json
{{
    "type": "direct",
    "content": "<your_answer_here>"
}}
```

3. Tool Result Format (use ONLY after receiving results from a tool call to provide the final answer):
```json
{{
    "type": "tool_result",
    "tool_id": "<tool_id_of_the_executed_tool>",
    "result": "<final_answer_incorporating_tool_results_if_relevant>"
}}
```

CRITICAL TOOL USAGE RULES:
1. ALWAYS use the EXACT "tool_id" from the Available Tools list below - do NOT generate new UUIDs
2. The "tool_id" field must match exactly one of the "tool_id" values from the tools list
3. Check the Available Tools section for the correct tool_id to use
4. Multiple tools can be called in a single "tool_call" response if needed

WHEN TO USE EACH FORMAT:
1. Use "tool_call" when:
   - You need external information or actions via a tool to answer the question.
2. Use "direct" when:
   - You can answer the question directly using your general knowledge without needing tools.
   - You need to explain a tool execution error.
3. Use "tool_result" ONLY when:
   - You have just received results from a tool call (role: tool messages in history).
   - You are providing the final answer to the original question.
   - Incorporate the tool results into your answer *if they are relevant and helpful*. If the tool results are not helpful or empty, state that briefly and answer using your general knowledge.

STRICT RULES:
1. ALWAYS wrap your response in a markdown code block (```json ... ```).
2. ALWAYS use one of the three formats above.
3. NEVER use any other "type" value.
4. NEVER include text outside the JSON structure. THIS IS CRITICAL. ONLY THE JSON BLOCK IS ALLOWED.
5. NEVER use markdown formatting inside the content/result fields.
6. ALWAYS use the exact tool_id from the available tools list for "tool_call".
7. ALWAYS provide complete, well-formatted JSON.
8. ALWAYS keep responses concise but complete.

HANDLING TOOL RESULTS:
- If a tool call fails (you receive an error message in the tool role), respond with a "direct" answer explaining the error.
- If you receive successful tool results (role: tool):
    - Analyze the results.
    - If the results help answer the original question, incorporate them into your final answer and use the "tool_result" format.
    - If the results are empty or not relevant to the original question, briefly state that the tool didn't provide useful information, then answer the original question using your general knowledge, still using the "tool_result" format but explaining the situation in the 'result' field.
- You're unsure after getting tool results, use the "tool_result" format and explain your reasoning in the 'result' field.
- Never make another tool call immediately after receiving tool results unless absolutely necessary and clearly justified.
"""
        elif self.expected_output_format == "text":
            return "You are an AI assistant that provides direct, concise textual answers. Do not use any special formatting or JSON."
        elif self.expected_output_format == "code":
            return "You are an AI assistant that generates code. Provide only the code, without any extra text or formatting unless specifically requested."
        else:
            raise ValueError(f"Unknown expected_output_format: {self.expected_output_format}")

    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Any]] = None,
        llm_config: Optional[Dict[str, Any]] = None,  # Add llm_config parameter
        **kwargs,
    ) -> LLMChatResponse:
        """
        Calls the appropriate LLM method using the ModelProvider interface.
        ModelProvider methods (achat, chat) are expected to return a BaseMessage.
        """
        self.logger.info(f"Agent '{self.role}': Starting LLM call...")

        if llm_config is None:
            llm_config = {}

        # Prefer async chat method if available
        if hasattr(self.llm, "achat"):
            self.logger.debug(f"Using async chat method from provider: {type(self.llm).__name__}")
            # For achat, we expect tools to be passed directly for binding
            result = await self.llm.achat(messages, tools=tools, **kwargs)
        elif hasattr(self.llm, "chat"):
            self.logger.debug(
                f"Using sync chat method in executor from provider: {type(self.llm).__name__}"
            )
            loop = asyncio.get_running_loop()
            # For chat, functools.partial is needed to bind tools for sync call in executor
            chat_with_tools = functools.partial(self.llm.chat, messages, tools=tools, **kwargs)
            # Use dedicated LLM thread pool to prevent blocking the default executor
            result = await loop.run_in_executor(self._llm_executor, chat_with_tools)
        elif hasattr(self.llm, "ainvoke"):
            self.logger.warning(
                f"Provider {type(self.llm).__name__} does not have 'achat'. "
                "Falling back to 'ainvoke'. Chat history might not be optimally handled."
            )
            # If tools are provided, ainvoke might not handle them directly. This path is less optimal.
            prompt = self.llm._format_chat_messages_to_prompt(messages)
            result = await self.llm.ainvoke(prompt, **kwargs)
        elif hasattr(self.llm, "invoke"):
            self.logger.warning(
                f"Provider {type(self.llm).__name__} does not have 'chat' methods. "
                "Falling back to 'invoke' in executor. Chat history might not be optimally handled."
            )
            # If tools are provided, invoke might not handle them directly. This path is less optimal.
            loop = asyncio.get_running_loop()
            prompt = self.llm._format_chat_messages_to_prompt(messages)
            # Use dedicated LLM thread pool to prevent blocking the default executor
            invoke_with_args = functools.partial(self.llm.invoke, prompt, **kwargs)
            result = await loop.run_in_executor(self._llm_executor, invoke_with_args)
        else:
            self.logger.error(
                f"LLM provider {type(self.llm).__name__} has no recognized "
                "callable method (achat, chat, ainvoke, invoke)."
            )
            raise TypeError(
                f"LLM provider {type(self.llm).__name__} has no recognized callable method."
            )

        self.logger.info(f"Agent '{self.role}': LLM call completed")
        return result  # Now returns LLMChatResponse from providers

    async def _execute_tool_calls(
        self, tool_call_requests: List[ToolCallRequest]
    ) -> Tuple[List[BaseMessage], bool]:
        """
        Executes tool calls parsed from LLM output.
        tool_calls_dicts: List of dictionaries, each representing a tool call,
                          e.g., {'tool_id': 'some_tool', 'arguments': {...}}
        Returns a list of history-formatted messages and a boolean indicating errors.
        """
        if not tool_call_requests:
            return [], False

        # execution_outcomes is List[Union[TaskResultMessage, TaskErrorMessage]]
        execution_outcomes, any_errors_from_manager = await self._tool_manager.get_tool_results(
            tool_call_requests
        )

        processed_outcomes: List[BaseMessage] = []
        for outcome in execution_outcomes:
            if isinstance(outcome, (TaskResultMessage, TaskErrorMessage)):
                processed_outcomes.append(outcome)
                if self.tool_result_topic and self.enable_tool_result_publishing:
                    await self.messager.publish(self.tool_result_topic, outcome)
            else:
                self.logger.error(f"Unexpected outcome type from ToolManager: {type(outcome)}")
                # Create a generic error message with direct fields + data=None
                error_msg = TaskErrorMessage(
                    tool_id=getattr(outcome, "tool_id", "unknown_id"),
                    tool_name=getattr(outcome, "tool_name", "unknown_name"),
                    task_id=getattr(outcome, "task_id", "unknown_task_id"),
                    error=f"Unexpected outcome type from ToolManager: {type(outcome)}",
                    source=MessageSource.AGENT,
                    data=None,
                )
                processed_outcomes.append(error_msg)
                if self.tool_result_topic and self.enable_tool_result_publishing:
                    await self.messager.publish(self.tool_result_topic, error_msg)

        return processed_outcomes, any_errors_from_manager

    async def query(
        self, question: str, user_id: Optional[str] = None, max_iterations: Optional[int] = None
    ) -> str:
        """
        Processes a question through the LLM and tool interaction loop.
        """
        # Use adaptive max iterations if not specified
        if max_iterations is None:
            max_iterations = self._get_adaptive_max_iterations(question)

        self.history = []
        self._queries_processed += 1

        # Reset tool call tracking for new query
        self._reset_tool_call_tracking()

        # Periodic dialogue cleanup
        if self._queries_processed % 10 == 0:
            self._cleanup_dialogue_history()

        if not self.raw_template:
            self.raw_template = self._build_prompt_template()

        # 1. Add System Prompt to history
        system_prompt_content = (self.raw_template or "").split("QUESTION:")[0].strip()
        if system_prompt_content:
            self.history.append(
                AgentSystemMessage(content=system_prompt_content, source=MessageSource.SYSTEM)
            )

        # 2. Add original user question to history
        self.history.append(AskQuestionMessage(question=question, source=MessageSource.USER))

        # Log the initial user question
        self._log_dialogue("user", question, "message")

        current_question_for_llm_turn = question

        for i in range(max_iterations):
            self.logger.info(
                f"Query Iteration: {i+1}/{max_iterations} for user '{user_id or 'Unknown'}'... Current prompt: {current_question_for_llm_turn[:100]}..."
            )

            tools_description_str = self._tool_manager.get_tools_description()

            # Format the user prompt for THIS specific turn, including tools and current question
            # Use simple string replacement to avoid format key conflicts with JSON in template
            template = self.raw_template or ""
            current_turn_formatted_prompt = template.replace(
                "{tool_descriptions}", tools_description_str
            ).replace("{question}", current_question_for_llm_turn)

            # Truncate or drop history depending on state mode
            if self.state_mode == AgentStateMode.STATEFUL:
                # Filter to BaseMessage for truncation function
                base_messages = [msg for msg in self.history if isinstance(msg, BaseMessage)]
                truncated_history = self._truncate_history_for_context(base_messages)
            else:
                truncated_history = []

            # Prepare messages in provider-native dict format from protocol history
            llm_input_messages = []
            for h in truncated_history:
                if isinstance(h, (AgentSystemMessage, ChatSystemMessage)):
                    llm_input_messages.append({"role": "system", "content": h.content})
                elif isinstance(h, (AskQuestionMessage, AgentLLMRequestMessage, ChatUserMessage)):
                    content = (
                        h.question
                        if isinstance(h, AskQuestionMessage)
                        else (h.prompt if isinstance(h, AgentLLMRequestMessage) else h.content)
                    )
                    llm_input_messages.append({"role": "user", "content": content})
                elif isinstance(h, (AgentLLMResponseMessage, ChatAssistantMessage)):
                    content = h.raw_content if isinstance(h, AgentLLMResponseMessage) else h.content
                    llm_input_messages.append({"role": "assistant", "content": content})
            # Append the specifically formatted user message for the current turn
            llm_input_messages.append(
                {"role": LLMRole.USER.value, "content": current_turn_formatted_prompt}
            )

            llm_response: LLMChatResponse = await self._call_llm(
                llm_input_messages
            )  # Call LLM directly returning BaseMessage

            # Get raw content string for logging and AgentLLMResponseMessage
            # This should capture either the direct text content or a string representation of tool calls
            llm_response_raw_text = ""
            if isinstance(llm_response, LLMChatResponse) and llm_response.message.tool_calls:
                # Serialize tool calls to a JSON string for raw_content
                llm_response_raw_text = json.dumps(llm_response.message.tool_calls)
            elif llm_response.message.content is not None:
                # Handle cases where content might not be a simple string (e.g., list of parts for multimodal)
                if isinstance(llm_response.message.content, str):
                    llm_response_raw_text = llm_response.message.content
                else:
                    llm_response_raw_text = str(llm_response.message.content)

            self.logger.debug(f"LLM raw response (Iter {i+1}): {llm_response_raw_text[:300]}...")

            # Instantiate AgentLLMResponseMessage with direct fields + data=None
            llm_response_msg = AgentLLMResponseMessage(
                raw_content=llm_response_raw_text, source=MessageSource.LLM, data=None
            )
            if self.llm_response_topic:
                await self.messager.publish(self.llm_response_topic, llm_response_msg)

            # Parse the response using our unified structure
            validated_response = await self._parse_llm_response(llm_response)

            if validated_response is None:
                self.logger.error(f"Could not parse LLM response: {llm_response_raw_text}")
                # Assign to direct fields of the message object
                llm_response_msg.parsed_type = "error_parsing"
                llm_response_msg.error_details = "Could not parse LLM response."
                self.history.append(llm_response_msg)
                current_question_for_llm_turn = f"Previous response could not be parsed. Please resubmit in proper JSON format. Original question: {question}"
                continue

            # Handle the different response types
            if isinstance(validated_response, LLMResponseDirect):
                llm_response_msg.parsed_type = "direct"
                llm_response_msg.parsed_direct_content = validated_response.content
                self.history.append(llm_response_msg)
                self.logger.debug(f"LLM direct response: {validated_response.content[:100]}...")

                # Log the assistant's direct response
                self._log_dialogue("assistant", validated_response.content, "message")

                return validated_response.content

            elif isinstance(validated_response, LLMResponseToolResult):
                llm_response_msg.parsed_type = "tool_result"
                llm_response_msg.parsed_tool_result_content = validated_response.result
                self.history.append(llm_response_msg)
                self.logger.debug(f"LLM tool_result response: {validated_response.result[:100]}...")

                # Log the assistant's tool result response
                self._log_dialogue("assistant", validated_response.result, "message")

                return validated_response.result

            elif isinstance(validated_response, LLMResponseToolCall):
                llm_response_msg.parsed_type = "tool_call"
                # Convert ToolCallRequest to MinimalToolCallRequest for storage
                llm_response_msg.parsed_tool_calls = [
                    MinimalToolCallRequest(tool_name=tc.tool_id, arguments=tc.arguments)
                    for tc in validated_response.tool_calls
                ]
                self.history.append(llm_response_msg)

                # Log the assistant's tool call
                tool_call_summary = (
                    f"Calling {len(validated_response.tool_calls)} tool(s): "
                    + ", ".join([tc.tool_id[:12] + "..." for tc in validated_response.tool_calls])
                )
                self._log_dialogue("assistant", tool_call_summary, "tool_call")

                if not llm_response_msg.parsed_tool_calls:
                    self.logger.warning(
                        "'tool_call' type with no tool_calls. Asking LLM to clarify."
                    )
                    current_question_for_llm_turn = f"Indicated 'tool_call' but provided no tools. Please clarify or answer directly for: {question}"
                    continue

                # Convert back to ToolCallRequest for execution
                tool_call_requests = [
                    ToolCallRequest(tool_id=tc.tool_name, arguments=tc.arguments)
                    for tc in llm_response_msg.parsed_tool_calls
                ]

                # Check for tool call loops before execution
                if self._detect_tool_call_loop(tool_call_requests):
                    self.logger.warning(
                        f"Agent '{self.role}': Tool call loop detected, breaking cycle"
                    )
                    self._log_dialogue(
                        "system", "Tool call loop detected - preventing infinite cycle", "warning"
                    )

                    # Provide a completion-focused prompt to break the loop
                    loop_break_prompt = (
                        f"LOOP DETECTED: You've been calling the same tools repeatedly. "
                        f"Based on the tool results in the conversation history, "
                        f"please provide a final answer to the original question: '{question}'. "
                        f"If the tools have successfully completed their tasks (check for success messages), "
                        f"then summarize what was accomplished. Use 'direct' format to end this cycle."
                    )
                    current_question_for_llm_turn = loop_break_prompt
                    continue

                tool_outcome_messages, had_error = await self._execute_tool_calls(
                    tool_call_requests
                )
                for outcome_msg in tool_outcome_messages:
                    self.history.append(outcome_msg)

                    # Log tool execution results
                    if isinstance(outcome_msg, TaskResultMessage):
                        tool_info = {"name": outcome_msg.tool_name, "success": True}
                        result_content = (
                            str(outcome_msg.result)
                            if outcome_msg.result is not None
                            else "Tool completed successfully"
                        )
                        self._log_dialogue("tool", result_content, "tool_result", tool_info)
                    elif isinstance(outcome_msg, TaskErrorMessage):
                        tool_info = {"name": outcome_msg.tool_name, "success": False}
                        error_content = (
                            str(outcome_msg.error)
                            if outcome_msg.error is not None
                            else "Tool execution failed"
                        )
                        self._log_dialogue("tool", error_content, "tool_result", tool_info)

                if had_error:
                    self.logger.warning(
                        "Tool execution had errors. Asking LLM to summarize for user."
                    )
                    current_question_for_llm_turn = f"Errors occurred during tool execution (see history). Explain this to the user and answer the original question: '{question}' if possible. Use 'direct' format."
                else:
                    self.logger.info("Tool execution successful. Checking for task completion.")

                    # Analyze if the task appears to be completed
                    task_appears_complete = self._analyze_task_completion(
                        question, tool_outcome_messages
                    )

                    if task_appears_complete:
                        self.logger.info(
                            f"Agent '{self.role}': Task completion analysis suggests work is done"
                        )
                        self._log_dialogue(
                            "system", "Task completion detected based on tool results", "info"
                        )

                        # Use completion-focused prompt
                        current_question_for_llm_turn = (
                            f"TASK COMPLETION DETECTED: Based on the successful tool executions and their results, "
                            f"it appears the task has been completed successfully. "
                            f"Please provide a final summary of what was accomplished for the original question: '{question}'. "
                            f"Focus on confirming what was done rather than planning additional actions. "
                            f"Use 'tool_result' format to provide the final answer."
                        )
                    else:
                        # Default continuation prompt
                        current_question_for_llm_turn = f"Tool execution finished (see history). Analyze results and answer the original question: '{question}'. Use 'tool_result' format."
                continue
            else:
                self.logger.error(f"Unknown validated response type: {type(validated_response)}")
                llm_response_msg.parsed_type = "error_validation"
                llm_response_msg.error_details = (
                    f"Unknown response type: {type(validated_response)}"
                )
                self.history.append(llm_response_msg)
                current_question_for_llm_turn = f"Unknown response format received. Please resubmit. Original question: {question}"
                continue

        self.logger.warning(f"Max iterations ({max_iterations}) reached for: {question}")
        if self.history:
            last_msg = self.history[-1]
            if isinstance(last_msg, AgentLLMResponseMessage):
                if last_msg.parsed_type == "direct" and last_msg.parsed_direct_content:
                    return last_msg.parsed_direct_content
                elif last_msg.parsed_type == "tool_result" and last_msg.parsed_tool_result_content:
                    return last_msg.parsed_tool_result_content
        return "Max iterations reached. Unable to provide a conclusive answer."

    async def handle_ask_question(self, message: AskQuestionMessage):
        """
        MQTT handler for incoming questions.
        - message: the parsed AskQuestionMessage or dict
        """
        try:
            # Access fields directly from the message object
            question: str = message.question
            user_id: Optional[str] = message.user_id

            self.logger.info(
                f"Received question from user '{user_id or 'Unknown'} via {message.source}': {question}"
            )

            answer_text = await self.query(question, user_id=user_id)

            # Create user-specific answer topic
            if user_id:
                user_answer_topic = f"{self.answer_topic}/{user_id}"
            else:
                # Fallback to global topic for clients without user_id
                user_answer_topic = self.answer_topic

            # Create AnswerMessage with direct fields + data=None
            answer_msg = AnswerMessage(
                question=question,
                answer=answer_text,
                user_id=user_id,
                source=MessageSource.AGENT,
                data=None,
            )
            await self.messager.publish(user_answer_topic, answer_msg)
            self.logger.info(
                f"Published answer to {user_answer_topic} for user '{user_id or 'Unknown'}'"
            )

        except Exception as e:
            self.logger.error(f"Error handling ask_question: {e}", exc_info=True)
            try:
                # Also use user-specific topic for error messages
                user_id = getattr(message, "user_id", None)
                if user_id:
                    error_topic = f"{self.answer_topic}/{user_id}"
                else:
                    error_topic = self.answer_topic

                error_msg = AnswerMessage(
                    question=getattr(message, "question", "Unknown question"),
                    error=f"Agent error: {str(e)}",
                    user_id=user_id,
                    source=MessageSource.AGENT,
                    data=None,
                )
                await self.messager.publish(error_topic, error_msg)
            except Exception as pub_e:
                self.logger.error(f"Failed to publish error answer: {pub_e}")

    async def handle_task(self, message: BaseMessage):
        """
        Handler for incoming task messages.
        Processes tasks directly using the agent's query method.
        """
        try:
            # Cast to AgentTaskMessage for type safety
            if not isinstance(message, AgentTaskMessage):
                self.logger.error(f"Expected AgentTaskMessage, got {type(message)}")
                return

            task: str = message.task
            task_id: str = message.task_id
            sender_id: Optional[str] = message.sender_id

            self.logger.info(
                f"Agent '{self.role}': Received task from '{sender_id or 'Unknown'}': {task[:100]}..."
            )

            # Log the incoming task
            self._log_dialogue("user", f"Task from {sender_id or 'system'}: {task}", "message")

            # Process task using existing query method
            result_text = await self.query(task)

            # Create result topic
            result_topic = f"agent/{self.role}/results"

            # Create result message
            result_msg = AgentTaskResultMessage(
                task_id=task_id,
                result=result_text,
                success=True,
                agent_id=self.role,
                source=MessageSource.AGENT,
                data=None,
            )

            # Publish to agent-specific topic if enabled
            if self.publish_to_agent_topic:
                await self.messager.publish(result_topic, result_msg)
                self.logger.info(f"Agent '{self.role}': Published task result to '{result_topic}'")

            # Note: Task response already logged in query() method, no need to log again

            # Publish to supervisor for multi-agent coordination if enabled
            if self.publish_to_supervisor:
                supervisor_result_topic = "supervisor/results"
                try:
                    await self.messager.publish(supervisor_result_topic, result_msg)
                    self.logger.info(f"Agent '{self.role}': Published task result to supervisor")
                except Exception as pub_e:
                    self.logger.warning(
                        f"Agent '{self.role}': Failed to publish to supervisor: {pub_e}"
                    )

        except Exception as e:
            self.logger.error(f"Agent '{self.role}': Error handling task: {e}", exc_info=True)
            try:
                # Create error result message
                error_msg = AgentTaskResultMessage(
                    task_id=getattr(message, "task_id", "unknown"),
                    result="",
                    success=False,
                    error=str(e),
                    agent_id=self.role,
                    source=MessageSource.AGENT,
                    data=None,
                )

                # Publish error result to agent topic if enabled
                if self.publish_to_agent_topic:
                    result_topic = f"agent/{self.role}/results"
                    await self.messager.publish(result_topic, error_msg)

                # Publish error to supervisor if enabled
                if self.publish_to_supervisor:
                    supervisor_result_topic = "supervisor/results"
                    await self.messager.publish(supervisor_result_topic, error_msg)

            except Exception as pub_e:
                self.logger.error(f"Agent '{self.role}': Failed to publish error result: {pub_e}")

    async def _publish_answer(
        self, question: str, response_content: str, user_id: Optional[str] = None
    ) -> None:
        """
        DEPRECATED or REPURPOSED: This method's original purpose of extracting content
        is now handled by ModelProviders. It might be removed or adapted if there's
        a different specific need for publishing answers outside handle_ask_question.
        For now, it's kept but likely unused by the main flow.
        """
        try:
            # Use user-specific topic if user_id is provided
            if user_id:
                publish_topic = f"{self.answer_topic}/{user_id}"
            else:
                publish_topic = self.answer_topic

            answer = AnswerMessage(
                question=question,
                answer=response_content,
                user_id=user_id,
                source=MessageSource.AGENT,
                data=None,
            )
            await self.messager.publish(publish_topic, answer)
            self.logger.info(f"Published answer (via _publish_answer) to {publish_topic}")
        except Exception as e:
            self.logger.error(f"Error in _publish_answer: {e}", exc_info=True)

    def _convert_protocol_history_to_llm_format(
        self, history_messages: List[BaseMessage]
    ) -> List[Dict[str, str]]:
        llm_formatted_messages: List[Dict[str, str]] = []
        for msg in history_messages:
            if isinstance(msg, AgentSystemMessage):
                llm_formatted_messages.append(
                    {"role": LLMRole.SYSTEM.value, "content": msg.content}
                )
            elif isinstance(msg, AskQuestionMessage):
                llm_formatted_messages.append({"role": LLMRole.USER.value, "content": msg.question})
            elif isinstance(msg, AgentLLMRequestMessage):
                llm_formatted_messages.append({"role": LLMRole.USER.value, "content": msg.prompt})
            elif isinstance(msg, AgentLLMResponseMessage):
                llm_formatted_messages.append(
                    {"role": LLMRole.ASSISTANT.value, "content": msg.raw_content}
                )
            elif isinstance(msg, TaskResultMessage):
                content = ""
                if msg.result is not None:
                    if isinstance(msg.result, (str, int, float, bool)):
                        content = str(msg.result)
                    elif isinstance(msg.result, (dict, list)):
                        try:
                            content = json.dumps(msg.result)
                        except TypeError:
                            content = f"Tool returned complex object: {str(msg.result)[:100]}..."
                    else:
                        content = f"Tool returned unhandled type: {type(msg.result)}"
                else:
                    content = "Tool executed successfully but returned no content."

                llm_formatted_messages.append(
                    {
                        "role": LLMRole.TOOL.value,
                        "tool_call_id": msg.task_id or msg.tool_id or "unknown_tool_call_id",
                        "name": msg.tool_name or "unknown_tool",
                        "content": content,
                    }
                )
            elif isinstance(msg, TaskErrorMessage):
                error_content = f"Error executing tool {msg.tool_name or 'unknown'}: {msg.error}"
                llm_formatted_messages.append(
                    {
                        "role": LLMRole.TOOL.value,
                        "tool_call_id": msg.task_id or msg.tool_id or "unknown_tool_call_id",
                        "name": msg.tool_name or "unknown_tool",
                        "content": error_content,
                    }
                )
            else:
                self.logger.warning(
                    f"Unrecognized message type in history for LLM conversion: {type(msg)}"
                )
        return llm_formatted_messages

    async def _parse_llm_response(
        self, llm_response: LLMChatResponse
    ) -> Optional[Union[LLMResponseToolCall, LLMResponseDirect, LLMResponseToolResult]]:
        # Extract from LLMChatResponse
        if llm_response.message.tool_calls:
            tool_calls_for_response = []
            for tc in llm_response.message.tool_calls:
                tool_id = tc.get("name") or tc.get("id")
                arguments = tc.get("args", tc.get("arguments", {}))
                if tool_id:
                    tool_calls_for_response.append(
                        ToolCallRequest(tool_id=tool_id, arguments=arguments)
                    )
            if tool_calls_for_response:
                return LLMResponseToolCall(type="tool_call", tool_calls=tool_calls_for_response)

        # For direct or JSON-encoded response, use content
        content = llm_response.message.content or ""
        if content:
            # Try to parse JSON-encoded schema {"type": ..., ...}
            # Handle both raw JSON and markdown-wrapped JSON
            json_content = content.strip()

            # Extract JSON from markdown code block if present
            if json_content.startswith("```json") and json_content.endswith("```"):
                json_content = json_content[7:-3].strip()  # Remove ```json and ```
            elif json_content.startswith("```") and json_content.endswith("```"):
                # Handle generic code block
                json_content = json_content[3:-3].strip()

            try:
                parsed = json.loads(json_content)
                if isinstance(parsed, dict) and "type" in parsed:
                    resp_type = str(parsed.get("type", "direct")).lower()
                    if resp_type == "direct":
                        parsed_content = str(parsed.get("content", ""))
                        return LLMResponseDirect(type="direct", content=parsed_content)
                    if resp_type == "tool_result":
                        return LLMResponseToolResult(
                            type="tool_result",
                            tool_id=str(parsed.get("tool_id", "")),
                            result=str(parsed.get("result", "")),
                        )
                    if resp_type == "tool_call":
                        tool_calls_data = parsed.get("tool_calls") or []
                        tool_calls_for_response: List[ToolCallRequest] = []
                        for tc in tool_calls_data:
                            if isinstance(tc, dict):
                                tool_id = tc.get("tool_id") or tc.get("name") or tc.get("id")
                                arguments = tc.get("arguments") or tc.get("args") or {}
                                if tool_id:
                                    tool_calls_for_response.append(
                                        ToolCallRequest(tool_id=str(tool_id), arguments=arguments)
                                    )
                        if tool_calls_for_response:
                            return LLMResponseToolCall(
                                type="tool_call", tool_calls=tool_calls_for_response
                            )
            except Exception:
                pass
            # Default to treating content as a direct string
            return LLMResponseDirect(type="direct", content=content)
        return None  # or handle empty

    async def _parse_llm_response_fallback(
        self, response_text: str
    ) -> Optional[Union[LLMResponseToolCall, LLMResponseDirect, LLMResponseToolResult]]:
        # This method is now effectively deprecated and will return None.
        # All parsing logic is consolidated in _parse_llm_response
        self.logger.debug(
            f"_parse_llm_response_fallback called (should be deprecated): {response_text[:100]}..."
        )
        return None
